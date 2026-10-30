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


v.0.0.3 version


Automatic valve control switch (with test mode for only logging)
Operation when the switch is turned on

When the room thermometer indicates that it is cold, the valve's target temperature temporarily jumps to its maximum setting. This causes the valve to open fully, preventing it from closing due to the heat radiating from the radiator.
Once the room reaches the target temperature, the valve reverts to its original target temperature.
Throughout this process, the room's target temperature remains at its original value, not 35°C. The valve retains its original setting even after a restart.
If you—or a Meross app schedule—change the valve's target temperature during this time, the plugin will not override that change. If you turn the valve off, the plugin will not interfere.
The original value is also restored if "summer mode" is activated, the thermometer becomes unavailable, the switch is turned off, or the integration is deleted.
The original preset (e.g., "auto") is also restored if the `set_temperature` call had switched the valve to manual mode.


v.0.0.4 version


New Settings (Configuration → Basic Settings)

Setting	Default Value	Function
Valve opening threshold	0.8 °C	- The valve only opens further if the room is colder than the target temperature by at least this amount. For smaller deviations, the valve decides on its own; the residual heat from the radiator is usually sufficient.
Valve opening delay	10 minutes	- The deviation must persist continuously for this duration before the valve opens further. If the room warms up on its own during this time, the timer resets.
Valve adjustment before target	- 0.3 °C	The valve reverts to its original target setting when the room temperature is this close to the target, as a fully open radiator will continue to heat the room even after the adjustment. This helps prevent overshooting the target temperature.

There is no delay in the event of a large deviation. If the deviation exceeds the threshold by 1 °C (i.e., 1.8 °C by default), the valve opens immediately. This ensures that if you increase the target temperature, you do not have to wait 10 minutes for a response.

Example with a target of 21 °C, using default values:

At 20.5 °C (a deviation of 0.5 °C), the valve remains unchanged.
At 20.0 °C (a deviation of 1.0 °C), it waits for 10 minutes and only opens further if the room has not warmed up during that time.
At 19.0 °C (a deviation of 2.0 °C), it opens immediately. During the boost phase, the valve is eased back (partially closed) at 20.7 °C; the residual heat from the radiator then brings the temperature the rest of the way up.

Fine-tuning

If the room temperature overshoots the target, increase the "ease-back" value (e.g., to 0.5 °C).
If the room heats up too slowly, decrease the threshold or the wait time. A setting of 0 minutes means the boost is applied immediately.
The "ease-back" value must be smaller than the threshold; the configuration interface enforces this.
The new settings apply globally to all rooms. If you need different values ​​for individual rooms (e.g., to account for large vs. small radiators), let me know, and I can set that up.

Two new attributes on the room's binary sensor can assist with fine-tuning: `deviation` (how much colder the room is compared to the target) and `valve_boost_waiting` (indicating whether the system is currently in the wait phase).

One thing that remains unchanged: the boiler's heat demand is still triggered based on the hysteresis (0.3 °C), regardless of the valve boost status. Consequently, in cases of minor temperature deviations, the boiler might run even while the valve is closed.


v.0.0.5 version


Two new features: the three valve settings can be overridden on a room-by-room basis (if left blank, the general default value applies), and there will be a per-room switch that links the boiler's heat demand to the state of the valve.


v.0.0.6,v.0.0.7 

Versions only contains repository fixes for HACS.


v.0.0.8

Language fixes, and hints


Installation:

1.Download "Meross_LAN" plugin from HACS.
2.Install and setup as the plugin said.
3.Unzip the main base file to  HA /config folder, makke sure the path is this: /config/custom_components/meross_boiler_sync/
4.Restart Home Assistant
5.Go to Settings → Devices → Integration add menu, search for: Meross Boiler Sync.
6.Choose the termostat,valves and do the settings and save.


Thank you for @krahabb for the main controller plugin Meross_Lan.
https://github.com/krahabb/meross_lan
