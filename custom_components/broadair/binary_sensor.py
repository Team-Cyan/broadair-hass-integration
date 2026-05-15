"""Binary sensor platform for BROAD AIR."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import BroadAirCoordinator
from .entity import BroadAirEntity


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class BroadAirBinarySensorDescription(
    BinarySensorEntityDescription, frozen_or_thawed=True
):
    """Description for a BROAD AIR binary sensor."""

    value_fn: Callable[[Any], bool]


BINARY_SENSORS: tuple[BroadAirBinarySensorDescription, ...] = (
    BroadAirBinarySensorDescription(
        key="online",
        translation_key="online",
        name="Online",
        value_fn=_truthy,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BroadAirBinarySensorDescription(
        key="FREQUENCY_RUN",
        translation_key="running",
        name="Running",
        value_fn=lambda value: float(value or 0) > 0,
        device_class=BinarySensorDeviceClass.RUNNING,
    ),
    BroadAirBinarySensorDescription(
        key="FAULT",
        translation_key="fault",
        name="Fault",
        value_fn=lambda value: bool(str(value or "").strip()),
        device_class=BinarySensorDeviceClass.PROBLEM,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BROAD AIR binary sensors."""

    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BroadAirBinarySensor(coordinator, device.guid, description)
        for device in coordinator.devices
        for description in BINARY_SENSORS
    ]
    async_add_entities(entities)


class BroadAirBinarySensor(BroadAirEntity, BinarySensorEntity):
    """BROAD AIR binary sensor."""

    entity_description: BroadAirBinarySensorDescription

    def __init__(
        self,
        coordinator: BroadAirCoordinator,
        device_guid: str,
        description: BroadAirBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator, device_guid)
        self.entity_description = description
        self._attr_unique_id = (
            f"{device_guid}_{description.key.lower().replace('.', '_')}"
        )
        self._attr_translation_key = description.translation_key
        self._attr_name = description.name
        self._attr_device_class = description.device_class

    @property
    def is_on(self) -> bool | None:
        """Return binary sensor state."""

        state = self.device_state
        if state is None:
            return None
        if self.entity_description.key == "online":
            return True
        return self.entity_description.value_fn(
            state.status.get(self.entity_description.key)
        )
