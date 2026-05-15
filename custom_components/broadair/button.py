"""Button platform for BROAD AIR."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BroadAirCoordinator
from .entity import BroadAirEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BROAD AIR buttons."""

    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BroadAirRefreshButton(coordinator, device.guid)
        for device in coordinator.devices
    )


class BroadAirRefreshButton(BroadAirEntity, ButtonEntity):
    """Button that requests realtime data from the device."""

    _attr_translation_key = "refresh_realtime"
    _attr_name = "Refresh realtime data"

    def __init__(self, coordinator: BroadAirCoordinator, device_guid: str) -> None:
        super().__init__(coordinator, device_guid)
        self._attr_unique_id = f"{device_guid}_refresh_realtime"

    async def async_press(self) -> None:
        """Request realtime data and refresh coordinator state."""

        await self.coordinator.async_refresh_realtime(self._device_guid)
