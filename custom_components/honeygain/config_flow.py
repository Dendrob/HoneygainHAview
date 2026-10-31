"""Config flow for Honeygain."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import selector
from requests.exceptions import RequestException

from .api import HoneygainApi, HoneygainApiError
from .const import DOMAIN


class HoneygainConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Honeygain."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial setup form."""
        errors: dict[str, str] = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL].strip()
            await self.async_set_unique_id(email.casefold())
            self._abort_if_unique_id_configured()
            try:
                await self.hass.async_add_executor_job(
                    HoneygainApi, email, user_input[CONF_PASSWORD]
                )
            except RequestException:
                errors["base"] = "cannot_connect"
            except (HoneygainApiError, KeyError, ValueError):
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(
                    title="HoneygainHAview",
                    data={
                        CONF_EMAIL: email,
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_EMAIL): str,
                vol.Required(CONF_PASSWORD): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
