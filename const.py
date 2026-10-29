"""Konstansok a Meross Boiler Sync integrációhoz."""

DOMAIN = "meross_boiler_sync"

CONF_BOILER = "boiler"
CONF_VALVES = "valves"
CONF_HYSTERESIS = "hysteresis"
CONF_MIN_SWITCH_TIME = "min_switch_time"
CONF_BOILER_ON_TEMP = "boiler_on_temp"

DEFAULT_HYSTERESIS = 0.3  # °C
DEFAULT_MIN_SWITCH_TIME = 3  # perc
DEFAULT_BOILER_ON_TEMP = 35  # °C, 0 = nem módosítjuk a kazán célhőmérsékletét
