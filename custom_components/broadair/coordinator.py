"""Coordinator for BROAD AIR devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.core import HomeAssistant
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
