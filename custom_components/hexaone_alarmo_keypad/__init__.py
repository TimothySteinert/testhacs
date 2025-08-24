from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN, CONF_ALARMO_ENTITY
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry):
    alarmo_entity = entry.data[CONF_ALARMO_ENTITY]

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        CONF_ALARMO_ENTITY: alarmo_entity,
        "override_state": None,  # can be "failed_to_arm" or "incorrect_pin"
    }

    # Listen for failed-to-arm events
    @callback
    def handle_failed(event):
        reason = event.data.get("reason")
        if reason == "invalid_code":
            hass.data[DOMAIN][entry.entry_id]["override_state"] = "incorrect_pin"
        else:
            hass.data[DOMAIN][entry.entry_id]["override_state"] = "failed_to_arm"

    hass.bus.async_listen("alarmo_failed_to_arm", handle_failed)

    hass.async_create_task(hass.config_entries.async_forward_entry_setups(entry, ["sensor"]))
    return True
