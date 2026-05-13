"""Base entities for BROAD AIR."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BroadAirCoordinator, BroadAirDeviceState


class BroadAirEntity(CoordinatorEntity[BroadAirCoordinator]):
    """Base BROAD AIR entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BroadAirCoordinator, device_guid: str) -> None:
        super().__init__(coordinator)
        self._device_guid = device_guid

    @property
    def device_state(self) -> BroadAirDeviceState | None:
        """Return cached state for this entity's device."""

        return (
            self.coordinator.data.get(self._device_guid)
            if self.coordinator.data
            else None
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return Home Assistant device info."""

        state = self.device_state
        name = state.device.name if state else "BROAD AIR"
        model = state.device.model if state else None
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_guid)},
            manufacturer="BROAD",
            name=name,
            model=model,
        )
