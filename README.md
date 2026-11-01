# Meross Boiler Sync  
Meross Boiler Sync is a custom Home Assistant integration designed to bridge the gap between Meross smart radiator valves and independent room thermometers/hygrometers.  

In the native Meross ecosystem, heating demand and temperature regulation are controlled exclusively by the built-in sensors located directly inside the valves right next to the hot radiator. This often causes valves to shut off prematurely because radiant heat tricks the sensor while the rest of the room is still cold. This integration solves that problem by delegating heating demand calculations to external room thermometers while keeping your normal valve schedules intact.`The plugin also work together with the boiler termostat what is a huge missing in the normal ecosystem. This plugin fill this gap!`

Multi-language support translations for `en, de, nl, fr, it, es, ru, pl, uk, ko, ja, zh, nb, sv, lv, and hu.`

<img width="1103" height="847" alt="image" src="https://github.com/user-attachments/assets/23d4b470-b65c-4914-ac61-abb163aafdea" />
<img width="1213" height="861" alt="image" src="https://github.com/user-attachments/assets/edda4fe3-fb63-473a-b204-4da64492bd2f" />
<img width="689" height="1229" alt="image" src="https://github.com/user-attachments/assets/4549fd19-3b29-44e2-a5e4-8a5c968f6155" />
<img width="1370" height="549" alt="image" src="https://github.com/user-attachments/assets/fd188f98-f2fb-463a-a3ba-9030e9ff6138" />

## 🛠️ Key Features & Capabilities

### Intelligent Room-Based Heating Control:  
Group one or more valves, an external thermometer, and an optional hygrometer into a single room. The system calculates heat demand based on the room's thermometer rather than individual valve sensors. If a thermometer ever becomes unreachable, the system automatically and seamlessly falls back to the valves' own readings.  
### Preservation of Native Schedules:  
Target temperatures configured on the valves and schedules set within the Meross app continue to function completely uninterrupted.  
### Automatic Valve Boost:  
When a room is cold, the integration temporarily raises the valve's target temperature to maximum in the background to force the valve fully open (overcoming localized radiator heat bias). Once the room reaches the target, the valve reverts to its original setting.  
### Humidity Compensation:  
If room humidity exceeds 60% (such as in a bathroom or a room with a running clothes dryer), the system automatically increases the target temperature—reaching a maximum adjustment of +1 °C at 80% humidity—to help dry the air and reduce mold risk. This feature automatically disables if the target is below 17 °C or in "away" mode.  
### Intelligent Summer Mode:  
Automatically disables the boiler thermostat when the current date falls within a defined summer period (default: May 15 to September 15) and the 24-hour outdoor temperature average exceeds a specified threshold (default: 17 °C), preventing unnecessary heating during warm spells.  
### Advanced Fine-Tuning Settings:  
Customize valve opening thresholds, delay timers (to prevent unnecessary valve jitter), and pre-target ease-back offsets (to prevent temperature overshooting).  
### Flexible Overrides:  
Settings can be adjusted globally or overridden on a per-room basis. You can also link a room's boiler heat demand directly to the valve's state via a dedicated per-room switch.  
### Extensive Multi-Language Support:  
Fully localized in over 15 languages (including English, Hungarian, German, French, Spanish, and more) for a native Home Assistant experience.  

## 📋 Version History

### Version 1.1
Window Sensor
You can assign one or more window/door sensors to each room. If multiple sensors are used, the opening of any one of them is sufficient to trigger the response.  
Delay: If a window remains open longer than the specified duration, the room will no longer request heat, and the valve will stop opening. Once the window is closed, heating resumes. Brief periods of ventilation (shorter than the delay) have no effect.  
Settings: The default is 5 minutes (0 = immediate); this can be adjusted in the General Settings and overridden on a per-room basis.  
An unreachable (offline) window sensor is treated as "closed," meaning it does not block heating.  
The window sensor does not physically close the valve; it merely pauses the heat demand. If you also need the valve to close, let me know—that would require a separate, minor adjustment.  

Introducin lovelace card:  

<img width="1944" height="811" alt="image" src="https://github.com/user-attachments/assets/9ddc66ff-d9fa-4011-bb89-c6e51f911562" />

Visual editor with four sections:  
General: design, title, selection of rooms (with custom order), and number of columns.  
Content to display: boiler status, number of rooms requesting heat, summer mode, current temperature, target temperature, humidity, deviation, status label—individual indicators can be toggled on or off.  
Values ​​and appearance: gauge scale, decimal precision, corner radius, and background transparency/blur.  
Colors: color picker for each state, plus a button to reset to default colors.  
Four design styles: glass gauge (closest to your current dashboard), minimalist rows, gradient tiles, and a list view with a status bar. Colors and background automatically adapt to your Home Assistant theme.  


### Version 0.1.0  
Monitoring for Stale Sensors (enabled by default, 6-hour threshold)  

If a thermometer has not reported data within the specified timeframe, the plugin treats it as unavailable. The room switches to using the valves' own internal temperature readings, automatic valve control is suspended, and the valve reverts to its original target setting.
A notification—displaying the room name and the sensor ID—will appear under Settings → Fixes. Once the sensor reports data again, this notification will automatically disappear.
This also applies to the outdoor sensor: if it becomes stale, "Summer Mode" is disabled, and heating remains enabled. No new data points from a stale sensor are added to the 24-hour average.
A stale humidity sensor is simply ignored, meaning no adjustments based on humidity levels will be applied. No notification is sent in this case.
Adjust the 6-hour threshold to match your sensor's typical reporting frequency. If a sensor reports infrequently, you may receive false alarms; in such cases, increase the threshold to at least twice the sensor's usual reporting interval.

Limiting the Duration of Valve Adjustments (enabled by default; 3-hour limit, followed by a 60-minute cooldown)

If an adjustment has been active for 3 hours and the room has still not reached its target temperature (e.g., due to an open window, a poorly placed sensor, or a "stuck" reading), the valve will revert to its original target and will not be adjusted again for 60 minutes.
If the room reaches its target temperature, the cooldown period is reset. After a restart, the time is calculated from the original start point; it does not reset.
This also applies during test mode, where entries are simply written to the log.

The new sensor attributes are: `temperature_sensor_stale` and `valve_boost_resting` on the room sensor, and `outdoor_sensor_stale` on the summer mode sensor.

### Version 0.0.9  
Expanded Multi-language Support: Added translations for `en, de, nl, fr, it, es, ru, pl, uk, ko, ja, zh, nb, sv, lv, and hu.`

### Version 0.0.8  
Language refinements, translation fixes, and added UI configuration hints.

### Versions 0.0.6 & 0.0.7  
Repository and structure fixes required for HACS integration compliance.

### Version 0.0.5  
Per-Room Settings Overrides: The three valve configuration thresholds can now be overridden on a per-room basis (falls back to global defaults if left blank).  
Valve Link Switch: Introduced a per-room switch option to directly link boiler heat demand to individual valve open states.

### Version 0.0.4  
Advanced Control Settings (Configuration → Basic Settings):  
  -Valve opening threshold (Default: 0.8 °C): Minimum temperature deficit before forcing the valve fully open. Minor fluctuations rely on valve internal logic and radiator residual heat.  
  -Valve opening delay (Default: 10 minutes): Temperature deviation must persist continuously for this duration before triggering a valve boost.  
  -Valve adjustment before target (Default: 0.3 °C): Offset near target temperature where the boost eases back (partially closes) to prevent overshoot.  
Immediate Response: Deviations exceeding the threshold by $1.0\text{ }^\circ\text{C}$ or more (e.g., total deviation $\ge 1.8\text{ }^\circ\text{C}$ with default settings) bypass the delay timer and open the valve immediately.  
Diagnostics: Added deviation and valve_boost_waiting attributes to room binary sensors.  

### Version 0.0.3  
Automatic Valve Control Switch: Includes a logging-only test mode.  
Temporarily sets target temperature to maximum when a room is cold, ensuring full valve opening despite radiator proximity heat.  
Reverts valve to original target temperature once room ambient target is met.  
Preserves user manual overrides, Meross app schedules, and turned-off states without forcing unwanted changes.  
Restores original settings safely across restarts, switch toggles, missing sensors, or Summer Mode activation.  

### Version 0.0.2  
UI for configuration
Room Management: Group valves, external thermometers, and optional hygrometers per room. Prioritizes room thermometer data with automatic fallback to internal valve sensors if the thermometer goes offline.  
Schedule Compatibility: Native Meross app schedules remain fully functional.  
Humidity Compensation: Automatically adjusts room target temperature (+1 °C max at 80% RH) when humidity exceeds 60% to help dry room air. Automatically disabled when setpoint is below 17 °C or in Away mode.  
Summer Mode: Disables boiler thermostat based on configurable date range (default: May 15 – Sep 15) and 24-hour outdoor average temperature (default threshold: $> 17\text{ }^\circ\text{C}$).  
Binary Sensors: Dedicated demand sensors with diagnostic attributes for each room and Summer Mode state.  

### Version 0.0.1  
Initial core release.  
Device mapping logic for valves and boiler controller.  
Maximum temperature setpoint feature for high ambient heat rooms (e.g., rooms with running tumble dryers).  


## 🙏 Acknowledgments
Special thanks to @krahabb for creating and maintaining the foundational Meross_LAN integration (https://github.com/krahabb/meross_lan).


## 🚀 Installation  
1.Download and install the Meross_LAN plugin via HACS.  
2.Set up and configure Meross_LAN according to its instructions.  
3.Download or unzip the repository files into your Home Assistant /config folder, ensuring the directory path matches: `/config/custom_components/meross_boiler_sync/`  
4.Restart Home Assistant.  
5.Navigate to Settings → Devices & Services → Add Integration, and search for Meross Boiler Sync.  
6.Select your thermostat, valves, configure your preferences, and save.  


