"""Setup for the HexaOne Alarmo Keypad integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN
from .sensor_esphome import HexaOneKeypadEspHomeState


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HexaOne Alarmo Keypad from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"entities": []}

    @callback
    def handle_failed(event) -> None:
        """Relay Alarmo failure events to the raw ESPHome sensor."""
        reason = event.data.get("reason")
        entities = hass.data[DOMAIN][entry.entry_id]["entities"]
        if not entities:
            return

        # Raw ESPHome state sensor is always first
        ent = entities[0]
        if isinstance(ent, HexaOneKeypadEspHomeState):
            if reason == "invalid_code":
                ent.set_override("incorrect_pin")
            else:
                ent.set_override("failed_to_arm")

    hass.bus.async_listen("alarmo_failed_to_arm", handle_failed)

    # Load sensor.py ? this will register both sensors
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HexaOne Alarmo Keypad config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
