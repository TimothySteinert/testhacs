"""Setup for the HexaOne Keypad integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import EventType

from .const import DOMAIN, CONF_ALARM_PROVIDER_ENTITY


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HexaOne Keypad from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "entities": [],
        "provider_tracker": None,
        "ready_tracker": None,
    }

    alarm_entity = entry.data.get(CONF_ALARM_PROVIDER_ENTITY)
    remove_listeners: list[callable] = []

    @callback
    def handle_failed(event: EventType) -> None:
        """Relay Alarmo failure events to the provider tracker."""
        if event.data.get("entity_id") != alarm_entity:
            return

        reason = event.data.get("reason")
        provider_tracker = hass.data[DOMAIN][entry.entry_id].get("provider_tracker")
        if not provider_tracker:
            return

        if reason == "invalid_code":
            provider_tracker.set_override("incorrect_pin", reason="invalid_code")
        else:
            provider_tracker.set_override("failed_to_arm", reason=reason)

    # Listen only for Alarmo failed_to_arm events on this entity
    remove_listeners.append(
        hass.bus.async_listen("alarmo_failed_to_arm", handle_failed)
    )

    # Store cleanup handles for unload
    hass.data[DOMAIN][entry.entry_id]["remove_listeners"] = remove_listeners

    # Forward setup to the sensor platform (HexaOneAlarmTracker + ReadyToArmSensor)
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a HexaOne Keypad config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        # Clean up event listeners
        remove_listeners: list[callable] = hass.data[DOMAIN][entry.entry_id].get(
            "remove_listeners", []
        )
        for remove in remove_listeners:
            remove()

        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
