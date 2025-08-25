HexaOne Alarm – Home Assistant Integration

A custom Home Assistant integration that provides a Keypad State Proxy for Alarmo
.
This integration exposes two sensor entities that track Alarmo’s state and present it both in a machine-friendly form (for ESPHome keypads) and a user-friendly form (for the Home Assistant UI).

✨ Features

✅ Tracks Alarmo’s state in real-time (disarmed, armed away, armed home, pending, arming, triggered, etc).

✅ Adds override states (failed_to_arm, incorrect_pin) when Alarmo emits failure events.

✅ Automatically clears override states after 2 seconds.

✅ Provides two sensors:

HexaOne Keypad ESPHome State → raw, lowercase identifiers (safe for parsing in ESPHome automations).

HexaOne Keypad State → human-friendly names (for Lovelace UI).

✅ Periodic refresh + instant updates on Alarmo state changes → no de-sync after HA restart.

📦 Installation
HACS (recommended)

Go to HACS → Integrations.

Click the ⋮ menu → Custom repositories.

Add this repo URL as an Integration.

Find HexaOne Alarm in HACS and install.

Restart Home Assistant.

Manual

Copy the custom_components/hexaone_alarm/ folder into your Home Assistant config/custom_components/.

Restart Home Assistant.

⚙️ Configuration

In Home Assistant, go to Settings → Devices & services → Add Integration.

Search for HexaOne Alarm.

Enter the entity_id of your Alarmo control panel (usually alarm_control_panel.alarmo).

Done! Two new sensors will be created:

sensor.hexaone_keypad_esphome_state (internal/raw – use in ESPHome).

sensor.hexaone_keypad_state (pretty/visual – use in UI cards).

🔧 Example ESPHome usage

You can bind your keypad display logic to the raw state:

text_sensor:
  - platform: homeassistant
    id: alarmo_keypad_state
    entity_id: sensor.hexaone_keypad_esphome_state
    on_value:
      then:
        - logger.log: "Keypad state changed to: ${x}"


This way your ESP32 keypad sees clean identifiers like:

armed_away

arming_home

incorrect_pin

🚨 Supported States

Raw identifiers (for ESPHome):

disarmed
armed_home
armed_home_bypass
armed_away
armed_away_bypass
arming_home
arming_away
pending_home
pending_away
triggered
failed_to_arm
incorrect_pin


UI names (for Lovelace):

Disarmed
Armed Home
Armed Home (Bypass)
Armed Away
Armed Away (Bypass)
Arming Home
Arming Away
Pending Home
Pending Away
Triggered
Failed to Arm
Incorrect PIN

## What's New

### 0.1.1
- Added unloading support and internal refactoring for reliability.
- Improved documentation and metadata for HACS.

## Compatibility

| Integration Version | Minimum HA Version |
| ------------------- | ------------------ |
| 0.1.1               | 2024.12.0          |

## Upgrade Instructions

1. In **HACS**, open **Settings → Updates** and install the latest version.
2. **Restart Home Assistant** to load the update.
3. Clear your browser cache if the new version doesn't appear.

## Backup Reminder

Back up your `config/` folder before upgrading.

🛠 Development

This integration uses:

sensor_esphome.py → manages raw state sensor.

sensor_ui.py → derives pretty state from the raw one.

__init__.py → wires them together and listens for Alarmo events.

config_flow.py → asks user for the Alarmo entity ID during setup.

*Consider adding unit tests and a GitHub Actions workflow for linting and tests.*

📜 License

MIT License – free to use and modify.
