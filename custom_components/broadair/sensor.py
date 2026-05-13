"""Sensor platform for BROAD AIR."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfVolumeFlowRate,
)
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


@dataclass(slots=True, frozen=True)
class BroadAirSensorDescription:
    """Description for a BROAD AIR sensor."""

    key: str
    translation_key: str
    name: str
    native_unit_of_measurement: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    value_fn: Callable[[Any], Any] = _float_value


SENSORS: tuple[BroadAirSensorDescription, ...] = (
    BroadAirSensorDescription(
        "TEMP_INDOOR1",
        "indoor_temperature",
        "Indoor temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "TEMP_INDOOR2",
        "indoor_temperature_2",
        "Secondary indoor temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "TEMP_OUTDOOR",
        "outdoor_temperature",
        "Outdoor temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "TEMP_FAIR",
        "fresh_air_temperature",
        "Fresh air temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "TEMP_EXHAUST",
        "exhaust_temperature",
        "Exhaust temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "SUPPLY_AIR_TEMP",
        "supply_air_temperature",
        "Supply air temperature",
        UnitOfTemperature.CELSIUS,
        SensorDeviceClass.TEMPERATURE,
    ),
    BroadAirSensorDescription(
        "INDOOR_HUMIDITY",
        "indoor_humidity",
        "Indoor humidity",
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
    ),
    BroadAirSensorDescription(
        "SUPPLY_AIR_HUMIDITY",
        "supply_air_humidity",
        "Supply air humidity",
        PERCENTAGE,
        SensorDeviceClass.HUMIDITY,
    ),
    BroadAirSensorDescription(
        "CO2_CONCENTRATION",
        "co2",
        "CO2",
        CONCENTRATION_PARTS_PER_MILLION,
        SensorDeviceClass.CO2,
    ),
    BroadAirSensorDescription(
        "OUT_PM2.5",
        "outdoor_pm25",
        "Outdoor PM2.5",
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorDeviceClass.PM25,
    ),
    BroadAirSensorDescription(
        "PATICLE_CCT_2_5",
        "indoor_pm25",
        "Indoor PM2.5",
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorDeviceClass.PM25,
    ),
    BroadAirSensorDescription(
        "RT_VOLUME",
        "realtime_air_volume",
        "Realtime air volume",
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    ),
    BroadAirSensorDescription(
        "FREQUENCY_RUN",
        "running_frequency",
        "Running frequency",
        "Hz",
        SensorDeviceClass.FREQUENCY,
    ),
    BroadAirSensorDescription(
        "FREQUENCY_SET",
        "set_frequency",
        "Set frequency",
        "Hz",
        SensorDeviceClass.FREQUENCY,
    ),
    BroadAirSensorDescription(
        "POWER_USED_RT",
        "realtime_power",
        "Realtime power",
        UnitOfPower.WATT,
        SensorDeviceClass.POWER,
    ),
    BroadAirSensorDescription(
        "RT_HOT_RECOVERY",
        "realtime_heat_recovery",
        "Realtime heat recovery",
        "W",
        SensorDeviceClass.POWER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BROAD AIR sensors."""

    coordinator: BroadAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        BroadAirSensor(coordinator, device.guid, description)
        for device in coordinator.devices
        for description in SENSORS
    ]
    async_add_entities(entities)


class BroadAirSensor(BroadAirEntity, SensorEntity):
    """BROAD AIR sensor."""

    entity_description: BroadAirSensorDescription

    def __init__(
        self,
        coordinator: BroadAirCoordinator,
        device_guid: str,
        description: BroadAirSensorDescription,
    ) -> None:
        super().__init__(coordinator, device_guid)
        self.entity_description = description
        self._attr_unique_id = (
            f"{device_guid}_{description.key.lower().replace('.', '_')}"
        )
        self._attr_translation_key = description.translation_key
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""

        state = self.device_state
        if state is None:
            return None
        return self.entity_description.value_fn(
            state.status.get(self.entity_description.key)
        )
