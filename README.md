v.0.0.1 version

Create methoad
Insert logic
Feature for add valves and main device
Feature for max. temperature set if heating needed. (For those rooms where could go above the temperature as comfy)
  Example: Your device's internal sensor, is in a room where you have dryer machine. In this case, in the room the temperature could go above as normal, so you need maximize the setted temperature to always on fire the boiler as needed.

v.0.0.2 version

Operation

Room: A room consists of one or more valves, a thermometer, and an optional hygrometer. Heat demand is calculated based on the room's thermometer rather than the individual valve's own sensor. Consequently, if a valve registers an excessively high temperature due to proximity to a hot radiator—while the room itself remains cold—the system will still request heat. If the thermometer becomes unreachable, the system temporarily reverts to using the valves' own temperature readings.
Target Temperature: This remains the value set on the valve (or valves). As a result, the schedules configured within the Meross app continue to function as intended.
Humidity: If the room's humidity exceeds 60%, the target temperature is increased, reaching a maximum adjustment (default: +1 °C) at 80% humidity. This helps dry the air slightly and reduces the risk of mold. If the target temperature is below 17 °C, or if the system is in an "away" state, no temperature increase is applied. Setting this value to 0 in the Basic Settings disables the feature.
Summer Mode: This mode activates when the current date falls within the defined summer period (default: between May 15 and September 15) and the 24-hour average of the outdoor temperature exceeds a specific threshold (default: 17 °C). When active, the boiler thermostat is switched off. The 24-hour average is used to prevent the mode from triggering due to a single warm afternoon or a cool night. Summer mode is disabled if no external sensor is available. Sensors: A binary sensor is created for each room—as well as for summer mode—indicating whether the room is currently requesting heat. The attributes display the measured temperature and its source (room thermometer or valve), the target temperature, the adjustment based on humidity, and the average value for summer mode.


Installation:

1.Unzip the main base file to  HA /config folder, makke sure the path is this: /config/custom_components/meross_boiler_sync/
2.Restart Home Assistant
3.Go to Settings → Devices → Integration add menu, search for: Meross Boiler Sync.
4. Choose the termostat,valves and do the settings and save.
