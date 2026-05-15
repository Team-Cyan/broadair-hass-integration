"""BROAD AIR integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import (
    ATTR_DEVICE_GUID,
    ATTR_FREQUENCY,
    DOMAIN,
    PLATFORMS,
    SERVICE_REFRESH_REALTIME,
    SERVICE_SET_FREQUENCY,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from .coordinator import BroadAirCoordinator, coordinator_from_config_entry

CONTROL_SERVICE_SCHEMA = vol.Schema({vol.Optional(ATTR_DEVICE_GUID): str})
SET_FREQUENCY_SERVICE_SCHEMA = CONTROL_SERVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_FREQUENCY): vol.All(
            vol.Coerce(int),
            vol.Range(min=0, max=100),
        )
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BROAD AIR from a config entry."""

    coordinator = coordinator_from_config_entry(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _async_register_services(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
        if not hass.data[DOMAIN]:
            _async_remove_services(hass)
    return unload_ok


def _get_coordinator(
    hass: HomeAssistant,
    device_guid: str | None = None,
) -> BroadAirCoordinator:
    coordinators = list(hass.data.get(DOMAIN, {}).values())
    if device_guid:
        for coordinator in coordinators:
            if any(device.guid == device_guid for device in coordinator.devices):
                return coordinator
        raise HomeAssistantError(f"Unknown BROAD AIR device: {device_guid}")
    if len(coordinators) == 1:
        return coordinators[0]

    raise HomeAssistantError(
        "device_guid is required when multiple BROAD AIR config entries exist"
    )


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_TURN_ON):
        return

    async def async_turn_on(call: ServiceCall) -> None:
        device_guid = call.data.get(ATTR_DEVICE_GUID)
        await _get_coordinator(hass, device_guid).async_turn_on(device_guid)

    async def async_turn_off(call: ServiceCall) -> None:
        device_guid = call.data.get(ATTR_DEVICE_GUID)
        await _get_coordinator(hass, device_guid).async_turn_off(device_guid)

    async def async_refresh_realtime(call: ServiceCall) -> None:
        device_guid = call.data.get(ATTR_DEVICE_GUID)
        await _get_coordinator(hass, device_guid).async_refresh_realtime(device_guid)

    async def async_set_frequency(call: ServiceCall) -> None:
        device_guid = call.data.get(ATTR_DEVICE_GUID)
        await _get_coordinator(hass, device_guid).async_set_frequency(
            call.data[ATTR_FREQUENCY],
            device_guid,
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_TURN_ON,
        async_turn_on,
        schema=CONTROL_SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_TURN_OFF,
        async_turn_off,
        schema=CONTROL_SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_REALTIME,
        async_refresh_realtime,
        schema=CONTROL_SERVICE_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FREQUENCY,
        async_set_frequency,
        schema=SET_FREQUENCY_SERVICE_SCHEMA,
    )


def _async_remove_services(hass: HomeAssistant) -> None:
    for service in (
        SERVICE_TURN_ON,
        SERVICE_TURN_OFF,
        SERVICE_REFRESH_REALTIME,
        SERVICE_SET_FREQUENCY,
    ):
        hass.services.async_remove(DOMAIN, service)
