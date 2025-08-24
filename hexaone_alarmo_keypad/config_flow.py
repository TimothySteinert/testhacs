import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.selector import selector
from .const import DOMAIN, CONF_ALARMO_ENTITY

class HexaOneKeypadConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="HexaOne Alarm State", data=user_input)

        schema = vol.Schema({
            vol.Required(CONF_ALARMO_ENTITY): selector({
                "entity": {"domain": "alarm_control_panel"}
            })
        })
        return self.async_show_form(step_id="user", data_schema=schema)
