from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN


class HexaOneKeypadState(SensorEntity):
    """User-facing sensor with pretty names, derived from raw ESPHome state."""

    _attr_name = "HexaOne Keypad State"
    _attr_unique_id = "hexaone_keypad_state"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        # We derive from the raw state sensor entity
        self._esp_sensor_id = "sensor.hexaone_keypad_esphome_state"
        self._attr_native_value = "Disarmed"

    def update_from_espsensor(self):
        """Pull state from raw ESPHome sensor and map to pretty value."""
        raw = self.hass.states.get(self._esp_sensor_id)
        if not raw:
            self._attr_native_value = "Unknown"
        else:
            state = raw.state
            mapping = {
                "armed_away": "Armed Away",
                "armed_home": "Armed Home",
                "armed_home_bypass": "Armed Home (Bypass)",
                "armed_away_bypass": "Armed Away (Bypass)",
                "arming_home": "Arming Home",
                "arming_away": "Arming Away",
                "pending_home": "Pending Home",
                "pending_away": "Pending Away",
                "disarmed": "Disarmed",
                "triggered": "Triggered",
                "failed_to_arm": "Failed to Arm",
                "incorrect_pin": "Incorrect PIN",
                "unknown": "Unknown",
            }
            self._attr_native_value = mapping.get(state, state)

        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Sync immediately and subscribe to raw state updates."""
        self.update_from_espsensor()
        self.async_on_remove(
            self.hass.bus.async_listen("state_changed", self._handle_state_change)
        )

    async def _handle_state_change(self, event):
        """Refresh when the raw ESPHome state changes."""
        if event.data.get("entity_id") == self._esp_sensor_id:
            self.update_from_espsensor()

    @property
    def native_value(self):
        """Return the current pretty state."""
        return self._attr_native_value
