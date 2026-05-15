"""Number platform for BROAD AIR."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfFrequency
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BroadAirCoordinator
from .entity import BroadAirEntity


def _float_value(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BROAD AIR numbers."""

    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BroadAirFrequencyNumber(coordinator, device.guid)
        for device in coordinator.devices
    )


class BroadAirFrequencyNumber(BroadAirEntity, NumberEntity):
    """Target frequency control."""

    _attr_translation_key = "target_frequency"
    _attr_name = "Target frequency"
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfFrequency.HERTZ
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator: BroadAirCoordinator, device_guid: str) -> None:
        super().__init__(coordinator, device_guid)
        self._attr_unique_id = f"{device_guid}_target_frequency"

    @property
    def native_value(self) -> float | None:
        """Return the current target frequency."""

        state = self.device_state
        if state is None:
            return None
        return _float_value(state.status.get("FREQUENCY_SET"))

    @property
    def native_min_value(self) -> float:
        """Return the minimum target frequency for this device."""

        return float(self.coordinator.frequency_range(self._device_guid).minimum)

    @property
    def native_max_value(self) -> float:
        """Return the maximum target frequency for this device."""

        return float(self.coordinator.frequency_range(self._device_guid).maximum)

    async def async_set_native_value(self, value: float) -> None:
        """Set the target frequency."""

        await self.coordinator.async_set_frequency(round(value), self._device_guid)
