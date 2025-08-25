"""Config flow for the HexaOne Alarm State Tracker integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import (
    DOMAIN,
    CONF_ALARM_PROVIDER,
    CONF_ALARM_PROVIDER_ENTITY,
    CONF_FAILED_TIMEOUT,
    CONF_PIN_TIMEOUT,
)
from .options_flow import HexaOneOptionsFlowHandler


class HexaOneKeypadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for HexaOne Alarm State Tracker."""

    async def async_step_user(self, user_input: dict | None = None):
        """Prompt the user for configuration."""
        if user_input is not None:
            return self.async_create_entry(
                title="HexaOne Alarm State Tracker",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_ALARM_PROVIDER, default="Alarmo"): selector(
                    {
                        "select": {
                            "options": ["Alarmo"],  # TODO: extend with Manual, Konnected.io
                            "mode": "dropdown",
                        }
                    }
                ),
                vol.Required(CONF_ALARM_PROVIDER_ENTITY): selector(
                    {
                        "entity": {
                            "domain": "alarm_control_panel"
                        }
                    }
                ),
                vol.Optional(
                    CONF_FAILED_TIMEOUT, default=2
                ): selector(
                    {
                        "number": {
                            "min": 1,
                            "max": 60,
                            "mode": "box",
                            "unit_of_measurement": "s",
                        }
                    }
                ),
                vol.Optional(
                    CONF_PIN_TIMEOUT, default=2
                ): selector(
                    {
                        "number": {
                            "min": 1,
                            "max": 60,
                            "mode": "box",
                            "unit_of_measurement": "s",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow handler so users can edit settings later."""
        return HexaOneOptionsFlowHandler(config_entry)
