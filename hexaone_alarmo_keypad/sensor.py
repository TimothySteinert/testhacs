from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, CONF_ALARMO_ENTITY

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([HexaOneAlarmStateSensor(hass, entry)])

class HexaOneAlarmStateSensor(SensorEntity):
    _attr_name = "HexaOne Alarm State"
    _attr_unique_id = "hexaone_alarm_state"

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._alarmo = entry.data[CONF_ALARMO_ENTITY]

    @property
    def state(self):
        data = self.hass.data[DOMAIN][self._entry_id]
        override = data["override_state"]
        if override:
            return override

        alarm_state = self.hass.states.get(self._alarmo)
        if not alarm_state:
            return "unknown"

        s = alarm_state.state
        mode = alarm_state.attributes.get("arm_mode", "")
        next_state = alarm_state.attributes.get("next_state", "")
        bypassed = alarm_state.attributes.get("bypassed_sensors")

        if s == "disarmed": return "disarmed"
        if s == "triggered": return "triggered"
        if s == "arming": return "arming_home" if mode == "armed_home" else "arming_away"
        if s == "pending": return "pending_home" if (mode == "armed_home" or next_state == "armed_home") else "pending_away"
        if s == "armed_home": return "armed_home_bypass" if bypassed else "armed_home"
        if s == "armed_away": return "armed_away_bypass" if bypassed else "armed_away"
        return "disarmed"
