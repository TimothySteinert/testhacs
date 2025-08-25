"""ESPHome-facing raw state sensor for HexaOne Alarmo Keypad."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .const import CONF_ALARMO_ENTITY, DOMAIN


class HexaOneKeypadEspHomeState(SensorEntity):
    """Raw hidden state for ESPHome to consume."""

    _attr_name = "HexaOne Keypad ESPHome State"
    _attr_unique_id = "hexaone_keypad_esphome_state"
    _attr_entity_registry_enabled_default = False  # hidden from UI

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the raw state sensor."""
        self.hass = hass
        self._entry_id = entry.entry_id
        self._alarmo = entry.data[CONF_ALARMO_ENTITY]
        self._override: str | None = None
        self._reset_task: asyncio.Task | None = None
        self._attr_native_value = "disarmed"

    async def async_added_to_hass(self) -> None:
        """Sync immediately, listen to Alarmo state, and set periodic refresh."""
        # Refresh right away
        self.update_from_alarmo()

        @callback
        def _alarmo_changed(event) -> None:
            """Handle state changes from Alarmo."""
            self.update_from_alarmo()

        self.async_on_remove(
            async_track_state_change_event(self.hass, [self._alarmo], _alarmo_changed)
        )
        self.async_on_remove(
            async_track_time_interval(
                self.hass, lambda now: self.update_from_alarmo(), timedelta(seconds=30)
            )
        )

    def set_override(self, state: str) -> None:
        """Apply override and reset after 2s."""
        self._override = state
        self._attr_native_value = state
        self.async_write_ha_state()

        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()
        self._reset_task = self.hass.loop.create_task(self._reset_override())

    async def _reset_override(self) -> None:
        try:
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            return
        self._override = None
        self.update_from_alarmo()

    def update_from_alarmo(self) -> None:
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

        if s == "arming":
            val = "arming_home" if mode == "armed_home" else "arming_away"
        elif s == "pending":
            home_mode = mode == "armed_home" or next_state == "armed_home"
            val = "pending_home" if home_mode else "pending_away"
        else:
            mapping = {
                "disarmed": "disarmed",
                "triggered": "triggered",
                "armed_home": "armed_home_bypass" if bypassed else "armed_home",
                "armed_away": "armed_away_bypass" if bypassed else "armed_away",
            }
            val = mapping.get(s, "disarmed")

        self._attr_native_value = val
        self.async_write_ha_state()

    @property
    def native_value(self) -> str:
        """Return the current raw value."""
        return self._attr_native_value
