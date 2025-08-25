"""Sensor platform for the HexaOne Alarmo Keypad integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .sensor_esphome import HexaOneKeypadEspHomeState
from .sensor_ui import HexaOneKeypadState


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up both raw and pretty keypad state sensors."""
    esp_sensor = HexaOneKeypadEspHomeState(hass, entry)
    pretty_sensor = HexaOneKeypadState(hass, entry)

    # Save them so __init__.py can access
    hass.data[DOMAIN][entry.entry_id]["entities"] = [esp_sensor, pretty_sensor]

    async_add_entities([esp_sensor, pretty_sensor])
