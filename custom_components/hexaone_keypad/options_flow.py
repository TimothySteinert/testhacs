"""Options flow for the HexaOne Keypad integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import DOMAIN, CONF_FAILED_TIMEOUT, CONF_PIN_TIMEOUT


class HexaOneOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle HexaOne options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self.config_entry.options or {}

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_FAILED_TIMEOUT,
                    default=options.get(CONF_FAILED_TIMEOUT, 2),
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
                    CONF_PIN_TIMEOUT,
                    default=options.get(CONF_PIN_TIMEOUT, 2),
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

        return self.async_show_form(step_id="init", data_schema=schema)
