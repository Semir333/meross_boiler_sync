"""Konstansok a Meross Boiler Sync integrációhoz."""
from __future__ import annotations

from datetime import datetime

DOMAIN = "meross_boiler_sync"

# --- config entry / options kulcsok
CONF_BOILER = "boiler"
CONF_VALVES = "valves"  # csak a régi (1.x) verzió migrálásához
CONF_ROOMS = "rooms"
CONF_HYSTERESIS = "hysteresis"
CONF_MIN_SWITCH_TIME = "min_switch_time"
CONF_BOILER_ON_TEMP = "boiler_on_temp"
CONF_HUMIDITY_MAX_BOOST = "humidity_max_boost"
CONF_OUTDOOR_SENSOR = "outdoor_sensor"
CONF_SUMMER_TEMP = "summer_temp"
CONF_SUMMER_START = "summer_start"
CONF_SUMMER_END = "summer_end"

# --- szoba kulcsok
CONF_ROOM_ID = "id"
CONF_ROOM_NAME = "name"
CONF_ROOM_VALVES = "valves"
CONF_ROOM_TEMP = "temperature_sensor"
CONF_ROOM_HUM = "humidity_sensor"

# --- alapértékek
DEFAULT_HYSTERESIS = 0.3  # °C
DEFAULT_MIN_SWITCH_TIME = 3  # perc
DEFAULT_BOILER_ON_TEMP = 35  # °C, 0 = nem módosítjuk a kazán célhőmérsékletét
DEFAULT_HUMIDITY_MAX_BOOST = 1.0  # °C, 0 = kikapcsolva
DEFAULT_SUMMER_TEMP = 17.0  # °C (24 órás átlag)
DEFAULT_SUMMER_START = "05-15"
DEFAULT_SUMMER_END = "09-15"

# --- belső paraméterek
HUMIDITY_START = 60.0  # % - ettől kezdve nő a célhőmérséklet
HUMIDITY_FULL = 80.0  # % - ennél éri el a maximális emelést
COMFORT_MIN_TARGET = 17.0  # °C alatti célnál (pl. távollét) nincs páratartalom miatti emelés
MAX_EFFECTIVE_TARGET = 26.0  # °C, a páratartalom miatt sem emelünk e fölé
SUMMER_HYSTERESIS = 1.0  # °C
AVG_WINDOW_SECONDS = 24 * 3600
SAMPLE_INTERVAL_SECONDS = 300
STORAGE_VERSION = 1


def parse_month_day(value: str | None) -> tuple[int, int] | None:
    """'MM-DD' szöveg (hónap, nap) párrá alakítása; érvénytelen esetén None."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(f"2000-{value.strip()}", "%Y-%m-%d")
    except ValueError:
        return None
    return (parsed.month, parsed.day)
