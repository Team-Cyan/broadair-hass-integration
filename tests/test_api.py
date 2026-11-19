from __future__ import annotations

import asyncio
import sys
from collections.abc import Mapping
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any

import pytest

SPEC = spec_from_file_location(
    "broadair_api",
    Path(__file__).parents[1] / "custom_components" / "broadair" / "api.py",
)
assert SPEC is not None
assert SPEC.loader is not None
api = module_from_spec(SPEC)
sys.modules[SPEC.name] = api
SPEC.loader.exec_module(api)


def test_build_login_signature() -> None:
    assert (
        api.build_login_signature(
            app_token="abc",
            nonce="123456",
            timestamp="1778680000",
        )
        == "30a3fb244e8834b68b9334f5738b4da8"
    )


def test_parse_wrapped_json_object() -> None:
    assert api.parse_wrapped_json('{"TEMP_INDOOR1":"27.4"}') == {"TEMP_INDOOR1": "27.4"}


def test_parse_wrapped_json_list() -> None:
    assert api.parse_wrapped_json('[{"eq_guid":"abc"}]') == [{"eq_guid": "abc"}]


def test_parse_wrapped_json_rejects_bad_json() -> None:
    with pytest.raises(api.BroadAirDataError):
        api.parse_wrapped_json("{bad")


def test_control_operation_constants() -> None:
    assert api.OPERATION_REFRESH_REALTIME == "1"
    assert api.OPERATION_TURN_OFF == "2"
    assert api.OPERATION_TURN_ON == "3"
    assert api.OPERATION_SET_FREQUENCY == "4"


class FakeResponse:
    def __init__(self, payload: Mapping[str, Any]) -> None:
        self._payload = payload
        self.status = 200
        self.headers = {"Date": "Fri, 15 May 2026 05:47:34 GMT"}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    async def json(self, content_type: str | None = None) -> Mapping[str, Any]:
        return self._payload


class FakeSession:
    def __init__(self) -> None:
        self.posts: list[dict[str, Any]] = []

    def head(self, *args: object, **kwargs: object) -> FakeResponse:
        return FakeResponse({})

    def post(self, *args: object, **kwargs: object) -> FakeResponse:
        self.posts.append(dict(kwargs))
        if len(self.posts) == 1:
            return FakeResponse({"Head": {"Code": 700, "Msg": "token expired"}})
        if len(self.posts) == 2:
            return FakeResponse(
                {"Head": {"Code": 200}, "Body": {"Data": {"token": "new-token"}}}
            )
        return FakeResponse({"Head": {"Code": 200}, "Body": {"Data": "ok"}})


def test_request_reauthenticates_once_when_session_token_expires() -> None:
    asyncio.run(_assert_request_reauthenticates_once_when_session_token_expires())


async def _assert_request_reauthenticates_once_when_session_token_expires() -> None:
    session = FakeSession()
    client = api.BroadAirApiClient(
        session,
        username="user",
        password="password",
        base_url="https://example.test",
        verify_ssl=False,
    )
    client._token = "expired-token"

    assert (
        await client._request("Equipment/GetFreshAirStatus", {"eq_guid": "abc"})
        == "ok"
    )
    assert [post["headers"].get("token") for post in session.posts] == [
        "expired-token",
        None,
        "new-token",
    ]


@pytest.mark.parametrize(
    ("path", "failure", "retries", "stage"),
    [
        (
            "Equipment/GetFreshAirStatus",
            TimeoutError,
            True,
            "request_or_response_headers",
        ),
        ("Equipment/SetFreshAir", TimeoutError, False, "request_or_response_headers"),
        ("Equipment/SetFreshAir", api.aiohttp.ConnectionTimeoutError, True, "connect"),
        (
            "Equipment/SetFreshAir",
            api.aiohttp.SocketTimeoutError,
            False,
            "response_body",
        ),
    ],
)
def test_transport_retry_boundaries(path, failure, retries, stage, monkeypatch, caplog):
    monkeypatch.setattr(api, "_RETRY_DELAY_SECONDS", 0)
    caplog.set_level("DEBUG", logger=api.__name__)

    class FailingResponse(FakeResponse):
        async def __aenter__(self):
            if stage != "response_body":
                raise failure()
            return self

        async def json(self, content_type=None):
            raise failure()

    class Session(FakeSession):
        def post(self, *args, **kwargs):
            self.posts.append(kwargs)
            return FailingResponse({})

    session = Session()
    client = api.BroadAirApiClient(
        session,
        username="private-user",
        password="private-password",
        base_url="https://private-host.test",
        verify_ssl=True,
    )
    client._token = "private-token"
    with pytest.raises(api.BroadAirConnectionError, match=stage):
        asyncio.run(client._request(path, {"sjx": "4", "eq_guid": "private-guid"}))

    assert len(session.posts) == (2 if retries else 1)
    assert f"stage={stage}" in caplog.text
    assert "retry=False" in caplog.text
    assert "private-" not in caplog.text
