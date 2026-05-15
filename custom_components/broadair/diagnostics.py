"""Diagnostics support for BROAD AIR."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "password",
    "pass_word",
    "token",
    "user_id",
    "username",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""

    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    devices = []
    if coordinator is not None:
        for device in coordinator.devices:
            state = coordinator.data.get(device.guid) if coordinator.data else None
            devices.append(
                {
                    "guid": device.guid,
                    "name": device.name,
                    "model": device.model,
                    "product_name": device.product_name,
                    "online": device.online,
                    "status_keys": sorted(state.status) if state else [],
                }
            )

    return {
        "entry": async_redact_data(
            {
                "title": entry.title,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            TO_REDACT,
        ),
        "devices": async_redact_data(devices, TO_REDACT),
    }
