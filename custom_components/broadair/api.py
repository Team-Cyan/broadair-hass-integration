"""Async client for the official BROAD AIR cloud API."""

from __future__ import annotations

import hashlib
import json
import random
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import aiohttp

APP_TOKEN = "8q7l82AxXB8Qo99vesUUvy1ED5tIuPT31NoIL6ZE5THH7clkfN"
FRESH_AIR_EQ_TYPE = "02"


class BroadAirError(Exception):
    """Base exception for BROAD AIR API failures."""


class BroadAirAuthError(BroadAirError):
    """Raised when authentication fails."""


class BroadAirApiError(BroadAirError):
    """Raised when the API returns an error response."""


class BroadAirConnectionError(BroadAirError):
    """Raised when the API cannot be reached."""


class BroadAirDataError(BroadAirError):
    """Raised when the API returns malformed data."""


@dataclass(slots=True, frozen=True)
class BroadAirDevice:
    """Fresh air device returned by the cloud."""

    guid: str
    name: str
    model: str | None
    product_name: str | None
    online: bool | None
    raw: Mapping[str, Any]


def build_login_signature(
    *,
    app_token: str = APP_TOKEN,
    nonce: str,
    timestamp: str,
) -> str:
    """Build the login signature used by the official app."""

    return hashlib.md5(f"{app_token}{nonce}{timestamp}".encode()).hexdigest()


def parse_wrapped_json(value: Any) -> Any:
    """Parse API fields that wrap JSON as a string."""

    if value in (None, ""):
        return None
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as err:
        raise BroadAirDataError("API returned invalid JSON in Body.Data") from err


def _as_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "online"}:
        return True
    if text in {"0", "false", "no", "offline"}:
        return False
    return None


class BroadAirApiClient:
    """Small async wrapper around BROAD AIR cloud endpoints."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        username: str,
        password: str,
        base_url: str,
        verify_ssl: bool,
    ) -> None:
        self._session = session
        self._username = username
        self._password = password
        self._base_url = base_url.rstrip("/")
        self._verify_ssl = verify_ssl
        self._token: str | None = None

    @property
    def token(self) -> str | None:
        """Return the current session token."""

        return self._token

    async def login(self) -> None:
        """Authenticate and cache the returned session token."""

        timestamp = str(int(time.time()))
        nonce = f"{random.randint(0, 999999):06d}"
        payload = {
            "user_id": self._username,
            "pass_word": self._password,
            "token": APP_TOKEN,
            "nonce": nonce,
            "timestamp": timestamp,
            "sign": build_login_signature(nonce=nonce, timestamp=timestamp),
        }
        data = await self._request("Account/Login", payload, include_token=False)
        token = data.get("token") if isinstance(data, dict) else None
        if not token:
            raise BroadAirAuthError("Login succeeded without a session token")
        self._token = str(token)

    async def get_fresh_air_devices(self) -> list[BroadAirDevice]:
        """Return fresh air devices bound to the current account."""

        data = await self._request(
            "Equipment/GetEquipmentsList",
            {
                "user_id": self._username,
                "eqType": FRESH_AIR_EQ_TYPE,
                "pageIndex": "1",
                "pageSize": "100",
            },
        )
        parsed = parse_wrapped_json(data)
        if not isinstance(parsed, list):
            raise BroadAirDataError("Device list is not a list")
        devices: list[BroadAirDevice] = []
        for item in parsed:
            if not isinstance(item, dict) or not item.get("eq_guid"):
                continue
            devices.append(
                BroadAirDevice(
                    guid=str(item["eq_guid"]),
                    name=str(
                        item.get("eq_name") or item.get("product_name") or "Fresh Air"
                    ),
                    model=str(item["product_model"])
                    if item.get("product_model")
                    else None,
                    product_name=str(item["product_name"])
                    if item.get("product_name")
                    else None,
                    online=_as_bool(item.get("online")),
                    raw=item,
                )
            )
        return devices

    async def get_fresh_air_status(self, device_guid: str) -> dict[str, Any]:
        """Return realtime status for one fresh air device."""

        data = await self._request(
            "Equipment/GetFreshAirStatus",
            {
                "user_id": self._username,
                "eq_guid": device_guid,
                "eq_name": "",
                "city": "",
                "pageIndex": "1",
                "pageSize": "10",
                "codeinfo": "",
                "time": str(int(time.time() * 1000)),
            },
        )
        parsed = parse_wrapped_json(data)
        if not isinstance(parsed, dict):
            raise BroadAirDataError("Fresh air status is not an object")
        return parsed

    async def _request(
        self,
        path: str,
        payload: Mapping[str, Any],
        *,
        include_token: bool = True,
    ) -> Any:
        headers = {"Content-Type": "application/json"}
        if include_token:
            if not self._token:
                await self.login()
            headers["token"] = self._token or ""
        url = f"{self._base_url}/api/{path}"
        try:
            async with self._session.post(
                url,
                json=dict(payload),
                headers=headers,
                ssl=self._verify_ssl,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                response.raise_for_status()
                envelope = await response.json(content_type=None)
        except TimeoutError as err:
            raise BroadAirConnectionError(
                "Timed out connecting to BROAD AIR API"
            ) from err
        except aiohttp.ClientError as err:
            raise BroadAirConnectionError("Could not connect to BROAD AIR API") from err

        if not isinstance(envelope, dict):
            raise BroadAirDataError("API response is not an object")
        head = envelope.get("Head")
        if not isinstance(head, dict):
            raise BroadAirDataError("API response is missing Head")
        code = head.get("Code")
        if code != 200:
            message = str(head.get("Msg") or "BROAD AIR API error")
            if code in {500, 600, 700, 800}:
                raise BroadAirAuthError(message)
            raise BroadAirApiError(message)
        body = envelope.get("Body")
        if not isinstance(body, dict):
            raise BroadAirDataError("API response is missing Body")
        return body.get("Data")
