"""Main sensor platform for HexaOne Keypad."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_ALARM_PROVIDER
from .sensor_alarmo_tracker import HexaOneAlarmoTracker


class HexaOneAlarmTracker(SensorEntity):
    """Published HexaOne Alarm state sensor."""

    _attr_name = "HexaOne Alarm Tracker"
    _attr_unique_id = "hexaone_alarm_tracker"
    _attr_translation_key = "hexaone_alarm_state_tracker"
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the published tracker sensor."""
        self.hass = hass
        self._entry = entry
        self._provider = entry.data[CONF_ALARM_PROVIDER]
        self._attr_native_value = "disarmed"
        self._provider_tracker = None

        # State update callback
        def _update_state(new_value: str) -> None:
            """Receive state updates from provider tracker (including overrides)."""
            self._attr_native_value = new_value
            self.schedule_update_ha_state()

        # Pick the correct provider tracker
        if self._provider.lower() == "alarmo":
            self._provider_tracker = HexaOneAlarmoTracker(
                hass, entry, state_callback=_update_state
            )

        # Store reference so __init__.py can reach it for events
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id]["provider_tracker"] = self._provider_tracker

    @property
    def native_value(self) -> str:
        """Return the current state."""
        return self._attr_native_value


class HexaOneReadyToArmSensor(SensorEntity):
    """Published HexaOne Ready To Arm sensor."""

    _attr_name = "HexaOne Ready To Arm"
    _attr_unique_id = "hexaone_ready_to_arm"
    _attr_translation_key = "hexaone_ready_to_arm"
    _attr_has_entity_name = True

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the published ready-to-arm sensor."""
        self.hass = hass
        self._entry = entry
        self._provider = entry.data[CONF_ALARM_PROVIDER]
        self._attr_native_value = "unknown"
        self._provider_tracker = None

        # Ready-to-arm callback
        def _update_ready(new_value: str) -> None:
            """Receive ready-to-arm updates from provider tracker."""
            self._attr_native_value = new_value
            self.schedule_update_ha_state()

        # Pick the correct provider tracker
        if self._provider.lower() == "alarmo":
            self._provider_tracker = HexaOneAlarmoTracker(
                hass, entry, state_callback=None, ready_callback=_update_ready
            )

        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id]["ready_tracker"] = self._provider_tracker

    @property
    def native_value(self) -> str:
        """Return the current ready-to-arm state."""
        return self._attr_native_value


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the HexaOne Alarm sensors."""
    state_sensor = HexaOneAlarmTracker(hass, entry)
    ready_sensor = HexaOneReadyToArmSensor(hass, entry)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id]["entities"] = [state_sensor, ready_sensor]

    async_add_entities([state_sensor, ready_sensor])
