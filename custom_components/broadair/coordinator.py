"""Coordinator for BROAD AIR devices."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BroadAirApiClient, BroadAirDevice, BroadAirError
from .const import (
    CONF_BASE_URL,
    CONF_VERIFY_SSL,
    DEFAULT_BASE_URL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)

COMMAND_COOLDOWN_SECONDS = 2.0
COMMAND_SETTLE_REFRESH_SECONDS = 5.0


@dataclass(slots=True)
class BroadAirDeviceState:
    """Cached device and status data."""

    device: BroadAirDevice
    status: dict[str, Any]


class BroadAirCoordinator(DataUpdateCoordinator[dict[str, BroadAirDeviceState]]):
    """Fetch BROAD AIR device state."""

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        username: str,
        password: str,
        base_url: str | None,
        verify_ssl: bool | None,
        update_interval,
    ) -> None:
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = BroadAirApiClient(
            async_get_clientsession(
                hass, verify_ssl=verify_ssl if verify_ssl is not None else True
            ),
            username=username,
            password=password,
            base_url=base_url or DEFAULT_BASE_URL,
            verify_ssl=DEFAULT_VERIFY_SSL if verify_ssl is None else verify_ssl,
        )
        self.devices: list[BroadAirDevice] = []
        self._last_command_at = 0.0
        self._command_lock = asyncio.Lock()

    async def _async_update_data(self) -> dict[str, BroadAirDeviceState]:
        try:
            if not self.devices:
                self.devices = await self.client.get_fresh_air_devices()
            result: dict[str, BroadAirDeviceState] = {}
            for device in self.devices:
                status = await self.client.get_fresh_air_status(device.guid)
                result[device.guid] = BroadAirDeviceState(device=device, status=status)
            return result
        except BroadAirError as err:
            raise UpdateFailed(str(err)) from err

    def resolve_device_guid(self, device_guid: str | None) -> str:
        """Resolve an optional service device GUID."""

        if device_guid:
            if any(device.guid == device_guid for device in self.devices):
                return device_guid
            raise HomeAssistantError(f"Unknown BROAD AIR device: {device_guid}")
        if len(self.devices) == 1:
            return self.devices[0].guid
        raise HomeAssistantError("device_guid is required when multiple devices exist")

    async def async_turn_on(self, device_guid: str | None = None) -> None:
        """Turn on a fresh air unit and refresh state."""

        guid = self.resolve_device_guid(device_guid)
        await self._run_control_command(lambda: self.client.turn_on_fresh_air(guid))

    async def async_turn_off(self, device_guid: str | None = None) -> None:
        """Turn off a fresh air unit and refresh state."""

        guid = self.resolve_device_guid(device_guid)
        await self._run_control_command(lambda: self.client.turn_off_fresh_air(guid))

    async def async_set_frequency(
        self,
        frequency: int,
        device_guid: str | None = None,
    ) -> None:
        """Set fresh air unit frequency and refresh state."""

        guid = self.resolve_device_guid(device_guid)
        await self._run_control_command(
            lambda: self.client.set_fresh_air_frequency(guid, frequency)
        )

    async def async_refresh_realtime(self, device_guid: str | None = None) -> None:
        """Request realtime data and refresh state."""

        guid = self.resolve_device_guid(device_guid)
        await self._run_control_command(
            lambda: self.client.refresh_fresh_air_realtime(guid)
        )

    async def _run_control_command(self, command: Callable[[], Awaitable[Any]]) -> None:
        """Run a control command serially, then refresh state."""

        async with self._command_lock:
            now = time.monotonic()
            cooldown_remaining = COMMAND_COOLDOWN_SECONDS - (
                now - self._last_command_at
            )
            if cooldown_remaining > 0:
                await asyncio.sleep(cooldown_remaining)
            try:
                await command()
                self._last_command_at = time.monotonic()
                await self.async_request_refresh()
                self.hass.async_create_task(self._async_delayed_refresh())
            except BroadAirError as err:
                raise HomeAssistantError(str(err)) from err

    async def _async_delayed_refresh(self) -> None:
        """Refresh again after the cloud/device state has had time to settle."""

        await asyncio.sleep(COMMAND_SETTLE_REFRESH_SECONDS)
        await self.async_request_refresh()


def coordinator_from_config_entry(hass: HomeAssistant, entry) -> BroadAirCoordinator:
    """Build a coordinator from a config entry."""

    from datetime import timedelta

    scan_interval = int(
        entry.options.get("scan_interval", entry.data.get("scan_interval", 60))
    )
    return BroadAirCoordinator(
        hass,
        username=entry.data["username"],
        password=entry.data["password"],
        base_url=entry.options.get(CONF_BASE_URL, entry.data.get(CONF_BASE_URL)),
        verify_ssl=entry.options.get(CONF_VERIFY_SSL, entry.data.get(CONF_VERIFY_SSL)),
        update_interval=timedelta(seconds=scan_interval),
    )
