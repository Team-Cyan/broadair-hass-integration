"""Switch platform for BROAD AIR."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BroadAirCoordinator
from .entity import BroadAirEntity


def _frequency_is_running(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BROAD AIR switches."""

    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BroadAirPowerSwitch(coordinator, device.guid)
        for device in coordinator.devices
    )


class BroadAirPowerSwitch(BroadAirEntity, SwitchEntity):
    """Fresh air power switch."""

    _attr_translation_key = "power"
    _attr_name = "Power"
    _attr_assumed_state = True

    def __init__(self, coordinator: BroadAirCoordinator, device_guid: str) -> None:
        super().__init__(coordinator, device_guid)
        self._attr_unique_id = f"{device_guid}_power"

    @property
    def is_on(self) -> bool | None:
        """Return whether the unit is currently running."""

        state = self.device_state
        if state is None:
            return None
        return any(
            value is True
            for value in (
                _frequency_is_running(state.status.get("FREQUENCY_RUN")),
                _frequency_is_running(state.status.get("RT_VOLUME")),
                _frequency_is_running(state.status.get("POWER_USED_RT")),
            )
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the fresh air unit."""

        await self.coordinator.async_turn_on(self._device_guid)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the fresh air unit."""

        await self.coordinator.async_turn_off(self._device_guid)
