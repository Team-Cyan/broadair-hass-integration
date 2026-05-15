"""Sensor platform for BROAD AIR."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
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


class BroadAirSensorDescription(SensorEntityDescription, frozen_or_thawed=True):
    """Description for a BROAD AIR sensor."""

    value_fn: Callable[[Any], Any] = _float_value


SENSORS: tuple[BroadAirSensorDescription, ...] = (
    BroadAirSensorDescription(
        key="TEMP_INDOOR1",
        translation_key="indoor_temperature",
        name="Indoor temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="TEMP_INDOOR2",
        translation_key="indoor_temperature_2",
        name="Secondary indoor temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="TEMP_OUTDOOR",
        translation_key="outdoor_temperature",
        name="Outdoor temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="TEMP_FAIR",
        translation_key="fresh_air_temperature",
        name="Fresh air temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="TEMP_EXHAUST",
        translation_key="exhaust_temperature",
        name="Exhaust temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="SUPPLY_AIR_TEMP",
        translation_key="supply_air_temperature",
        name="Supply air temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="INDOOR_HUMIDITY",
        translation_key="indoor_humidity",
        name="Indoor humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="SUPPLY_AIR_HUMIDITY",
        translation_key="supply_air_humidity",
        name="Supply air humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="CO2_CONCENTRATION",
        translation_key="co2",
        name="CO2",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="OUT_PM2.5",
        translation_key="outdoor_pm25",
        name="Outdoor PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="PATICLE_CCT_2_5",
        translation_key="indoor_pm25",
        name="Indoor PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="RT_VOLUME",
        translation_key="realtime_air_volume",
        name="Realtime air volume",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="FREQUENCY_RUN",
        translation_key="running_frequency",
        name="Running frequency",
        native_unit_of_measurement="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="FREQUENCY_SET",
        translation_key="set_frequency",
        name="Set frequency",
        native_unit_of_measurement="Hz",
        device_class=SensorDeviceClass.FREQUENCY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="POWER_USED_RT",
        translation_key="realtime_power",
        name="Realtime power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    BroadAirSensorDescription(
        key="RT_HOT_RECOVERY",
        translation_key="realtime_heat_recovery",
        name="Realtime heat recovery",
        native_unit_of_measurement="W",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
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
