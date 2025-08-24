import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.core import callback
from .const import DOMAIN, CONF_ALARMO_ENTITY


class HexaOneKeypadEspHomeState(SensorEntity):
    """Raw hidden state for ESPHome to consume."""

    _attr_name = "HexaOne Keypad ESPHome State"
    _attr_unique_id = "hexaone_keypad_esphome_state"
    _attr_entity_registry_enabled_default = False  # hidden from UI

    def __init__(self, hass, entry):
        self.hass = hass
        self._entry_id = entry.entry_id
        self._alarmo = entry.data[CONF_ALARMO_ENTITY]
        self._override = None
        self._reset_task = None
        self._attr_native_value = "disarmed"

    async def async_added_to_hass(self):
    	"""Sync immediately, listen to Alarmo state, and set periodic refresh."""
    	# Refresh right away
    	self.update_from_alarmo()

    	@callback
    	def _alarmo_changed(event):
            self.update_from_alarmo()

    	async_track_state_change_event(self.hass, [self._alarmo], _alarmo_changed)

    	async_track_time_interval(
            self.hass, lambda now: self.update_from_alarmo(), timedelta(seconds=30)
    )

    def set_override(self, state: str):
        """Apply override and reset after 2s."""
        self._override = state
        self._attr_native_value = state
        self.async_write_ha_state()

        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()
        self._reset_task = self.hass.loop.create_task(self._reset_override())

    async def _reset_override(self):
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            return
        self._override = None
        self.update_from_alarmo()

    def update_from_alarmo(self):
        """Recalculate raw Alarmo state if no override active."""
        if self._override:
            return

        alarm_state = self.hass.states.get(self._alarmo)
        if not alarm_state:
            self._attr_native_value = "unknown"
            self.async_write_ha_state()
            return

        s = alarm_state.state
        mode = alarm_state.attributes.get("arm_mode", "")
        next_state = alarm_state.attributes.get("next_state", "")
        bypassed = alarm_state.attributes.get("bypassed_sensors")

        if s == "disarmed":
            val = "disarmed"
        elif s == "triggered":
            val = "triggered"
        elif s == "arming":
            val = "arming_home" if mode == "armed_home" else "arming_away"
        elif s == "pending":
            val = "pending_home" if (mode == "armed_home" or next_state == "armed_home") else "pending_away"
        elif s == "armed_home":
            val = "armed_home_bypass" if bypassed else "armed_home"
        elif s == "armed_away":
            val = "armed_away_bypass" if bypassed else "armed_away"
        else:
            val = "disarmed"

        self._attr_native_value = val
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._attr_native_value
