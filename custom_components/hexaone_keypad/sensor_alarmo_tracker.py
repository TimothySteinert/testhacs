"""Internal Alarmo tracker for HexaOne Keypad (not published to HA directly)."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_interval,
)

from .const import (
    CONF_ALARM_PROVIDER_ENTITY,
    CONF_FAILED_TIMEOUT,
    CONF_PIN_TIMEOUT,
)


class HexaOneAlarmoTracker:
    """Internal tracker that monitors Alarmo state and reports updates via callback(s)."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        state_callback=None,
        ready_callback=None,
    ) -> None:
        """Initialize the Alarmo tracker."""
        self.hass = hass
        self._entry = entry

        self._alarm_entity = entry.data[CONF_ALARM_PROVIDER_ENTITY]
        self._failed_timeout = entry.options.get(
            CONF_FAILED_TIMEOUT, entry.data.get(CONF_FAILED_TIMEOUT, 2)
        )
        self._pin_timeout = entry.options.get(
            CONF_PIN_TIMEOUT, entry.data.get(CONF_PIN_TIMEOUT, 2)
        )

        self._state_callback = state_callback
        self._ready_callback = ready_callback

        self._override: str | None = None
        self._reset_task: asyncio.Task | None = None
        self._last_value: str = "disarmed"
        self._last_ready: str = "unknown"

        # Set up listeners
        self._setup_listeners()

    def _setup_listeners(self) -> None:
        """Attach state and periodic listeners."""

        # Initial sync for both sensors
        self.update_from_alarm(force=True)
        self._update_ready_from_alarm(force=True)

        @callback
        def _alarm_changed(event) -> None:
            """Handle Alarmo state changes."""
            self.update_from_alarm()

        async_track_state_change_event(self.hass, [self._alarm_entity], _alarm_changed)

        # Periodic refresh every 30s as a safety net
        async_track_time_interval(
            self.hass, lambda now: self.update_from_alarm(), timedelta(seconds=30)
        )
        async_track_time_interval(
            self.hass, lambda now: self._update_ready_from_alarm(), timedelta(seconds=30)
        )

        # Ready-to-arm listener (event-driven updates)
        if self._ready_callback:
            @callback
            def _ready_to_arm(event) -> None:
                """Handle Alarmo ready-to-arm events."""
                if event.data.get("entity_id") != self._alarm_entity:
                    return
                self._update_ready_from_alarm(force=True, event_data=event.data)

            self.hass.bus.async_listen(
                "alarmo_ready_to_arm_modes_updated", _ready_to_arm
            )

    def set_override(self, state: str, reason: str | None = None) -> None:
        """Apply an override state and schedule reset."""
        self._override = state
        self._publish(state, force=True)

        if self._reset_task and not self._reset_task.done():
            self._reset_task.cancel()
        self._reset_task = self.hass.loop.create_task(self._reset_override(reason))

    async def _reset_override(self, reason: str | None) -> None:
        """Reset override after timeout."""
        failed_timeout = self._entry.options.get(
            CONF_FAILED_TIMEOUT, self._entry.data.get(CONF_FAILED_TIMEOUT, 2)
        )
        pin_timeout = self._entry.options.get(
            CONF_PIN_TIMEOUT, self._entry.data.get(CONF_PIN_TIMEOUT, 2)
        )

        try:
            if reason == "invalid_code":
                await asyncio.sleep(pin_timeout)
            else:
                await asyncio.sleep(failed_timeout)
        except asyncio.CancelledError:
            return

        self._override = None
        self.update_from_alarm(force=True)

    def update_from_alarm(self, force: bool = False) -> None:
        """Recalculate Alarmo state if no override active."""
        if self._override:
            return

        alarm_state = self.hass.states.get(self._alarm_entity)
        if not alarm_state:
            self._publish("unknown", force=force)
            return

        s = alarm_state.state
        mode = alarm_state.attributes.get("arm_mode", "")
        next_state = alarm_state.attributes.get("next_state", "")
        bypassed = alarm_state.attributes.get("bypassed_sensors")

        if s == "unavailable":
            val = "unavailable"
        elif s == "arming":
            if mode == "armed_home":
                val = "arming_home"
            elif mode == "armed_away":
                val = "arming_away"
            elif mode == "armed_night":
                val = "arming_night"
            elif mode == "armed_vacation":
                val = "arming_vacation"
            elif mode == "armed_custom_bypass":
                val = "arming_custom_bypass"
            else:
                val = "arming"
        elif s == "pending":
            if mode == "armed_home" or next_state == "armed_home":
                val = "pending_home"
            elif mode == "armed_away" or next_state == "armed_away":
                val = "pending_away"
            elif mode == "armed_night" or next_state == "armed_night":
                val = "pending_night"
            elif mode == "armed_vacation" or next_state == "armed_vacation":
                val = "pending_vacation"
            elif mode == "armed_custom_bypass" or next_state == "armed_custom_bypass":
                val = "pending_custom_bypass"
            else:
                val = "pending"
        else:
            mapping = {
                "disarmed": "disarmed",
                "triggered": "triggered",
                "armed_home": "armed_home_bypass" if bypassed else "armed_home",
                "armed_away": "armed_away_bypass" if bypassed else "armed_away",
                "armed_night": "armed_night_bypass" if bypassed else "armed_night",
                "armed_vacation": "armed_vacation_bypass" if bypassed else "armed_vacation",
                "armed_custom_bypass": "armed_custom_bypass",
            }
            val = mapping.get(s, "unknown")

        self._publish(val, force=force)

    def _update_ready_from_alarm(
        self, force: bool = False, event_data: dict | None = None
    ) -> None:
        """Recalculate ready-to-arm state."""
        if not self._ready_callback:
            return

        if event_data is None:
            alarm_state = self.hass.states.get(self._alarm_entity)
            if not alarm_state:
                new_val = "unknown"
            else:
                # Default heuristic: ready if no bypassed sensors
                bypassed = alarm_state.attributes.get("bypassed_sensors")
                new_val = "ready" if not bypassed else "not_ready"
        else:
            # Event provides specific ready flags
            armed_away = event_data.get("armed_away", False)
            new_val = "ready" if armed_away else "not_ready"

        if force or new_val != self._last_ready:
            self._last_ready = new_val
            self._ready_callback(new_val)

    def _publish(self, value: str, force: bool = False) -> None:
        """Send state to main sensor (force overrides and reset)."""
        if force or value != self._last_value:
            self._last_value = value
            if self._state_callback:
                self._state_callback(value)
