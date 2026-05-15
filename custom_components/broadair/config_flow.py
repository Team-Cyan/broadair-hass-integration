"""Config flow for BROAD AIR."""

from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    BroadAirApiClient,
    BroadAirAuthError,
    BroadAirConnectionError,
    BroadAirError,
)
from .const import (
    CONF_BASE_URL,
    CONF_FREQUENCY_MAX,
    CONF_FREQUENCY_MIN,
    CONF_SCAN_INTERVAL,
    CONF_VERIFY_SSL,
    DEFAULT_BASE_URL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
)


class BroadAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a BROAD AIR config flow."""

    VERSION = 1
    _reauth_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            username = user_input[CONF_USERNAME]
            await self.async_set_unique_id(username)
            self._abort_if_unique_id_configured()
            try:
                await _validate_input(self.hass, user_input)
            except BroadAirAuthError:
                errors["base"] = "invalid_auth"
            except (BroadAirConnectionError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
            except BroadAirError:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=username,
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Optional(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                    vol.Optional(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                    vol.Optional(CONF_SCAN_INTERVAL, default=60): vol.All(
                        vol.Coerce(int), vol.Range(min=30, max=3600)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Create the options flow."""

        return BroadAirOptionsFlow(config_entry)

    async def async_step_reauth(
        self,
        entry_data: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """Handle reauthentication."""

        self._reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Confirm BROAD AIR reauthentication."""

        if self._reauth_entry is None:
            return self.async_abort(reason="reauth_entry_missing")

        errors: dict[str, str] = {}
        if user_input is not None:
            data = {**self._reauth_entry.data, **user_input}
            try:
                await _validate_input(self.hass, data)
            except BroadAirAuthError:
                errors["base"] = "invalid_auth"
            except (BroadAirConnectionError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
            except BroadAirError:
                errors["base"] = "unknown"
            else:
                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=data,
                )
                await self.hass.config_entries.async_reload(
                    self._reauth_entry.entry_id
                )
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=self._reauth_entry.data.get(CONF_USERNAME, ""),
                    ): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class BroadAirOptionsFlow(config_entries.OptionsFlow):
    """Handle BROAD AIR options."""

    def __init__(self, config_entry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_BASE_URL,
                        default=self._config_entry.options.get(
                            CONF_BASE_URL,
                            self._config_entry.data.get(
                                CONF_BASE_URL, DEFAULT_BASE_URL
                            ),
                        ),
                    ): str,
                    vol.Optional(
                        CONF_VERIFY_SSL,
                        default=self._config_entry.options.get(
                            CONF_VERIFY_SSL,
                            self._config_entry.data.get(
                                CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL
                            ),
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self._config_entry.data.get(CONF_SCAN_INTERVAL, 60),
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=3600)),
                    vol.Optional(
                        CONF_FREQUENCY_MIN,
                        default=self._config_entry.options.get(CONF_FREQUENCY_MIN, 0),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=200)),
                    vol.Optional(
                        CONF_FREQUENCY_MAX,
                        default=self._config_entry.options.get(CONF_FREQUENCY_MAX, 0),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=200)),
                }
            ),
        )


async def _validate_input(hass, data: dict[str, Any]) -> None:
    session = async_get_clientsession(
        hass,
        verify_ssl=data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
    )
    client = BroadAirApiClient(
        session,
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        base_url=data.get(CONF_BASE_URL, DEFAULT_BASE_URL),
        verify_ssl=data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
    )
    await client.login()
    await client.get_fresh_air_devices()
