"""Config flow for the HexaOne Alarmo Keypad integration."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector

from .const import CONF_ALARMO_ENTITY, DOMAIN


class HexaOneKeypadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the configuration flow for HexaOne Alarmo Keypad."""

    async def async_step_user(self, user_input: dict | None = None):
        """Prompt the user for the Alarmo entity ID."""
        if user_input is not None:
            return self.async_create_entry(title="HexaOne Alarm State", data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_ALARMO_ENTITY): selector(
                    {"entity": {"domain": "alarm_control_panel"}}
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
