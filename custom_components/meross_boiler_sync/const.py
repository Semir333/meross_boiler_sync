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
CONF_VALVE_DRY_RUN = "valve_dry_run"
CONF_WINDOW_DELAY = "window_open_delay"  # globális alapérték és szobai felülírás is
CONF_REGISTER_CARD = "register_card"
CONF_STALE_ENABLED = "stale_check_enabled"
CONF_STALE_HOURS = "stale_hours"
CONF_MAX_BOOST_ENABLED = "max_boost_enabled"
CONF_MAX_BOOST_HOURS = "max_boost_hours"
CONF_MAX_BOOST_REST = "max_boost_rest_minutes"
CONF_VALVE_BOOST_THRESHOLD = "valve_boost_threshold"
CONF_VALVE_BOOST_DELAY = "valve_boost_delay"
CONF_VALVE_RELEASE_MARGIN = "valve_release_margin"
CONF_SUMMER_TEMP = "summer_temp"
CONF_SUMMER_START = "summer_start"
CONF_SUMMER_END = "summer_end"
# 2.8: események, kazán-ciklusok, védelem (mind külön ki/be kapcsolható)
CONF_EVENTS_ENABLED = "events_enabled"
CONF_CYCLE_MONITOR = "cycle_monitor_enabled"
CONF_CYCLE_MAX_STARTS = "cycle_max_starts_per_hour"
CONF_CYCLE_MIN_AVG_ON = "cycle_min_avg_on_minutes"
CONF_CYCLE_PROTECTION = "cycle_protection_enabled"
CONF_BOILER_MIN_ON = "boiler_min_on_minutes"
CONF_BOILER_MIN_OFF = "boiler_min_off_minutes"

# --- szoba kulcsok
CONF_ROOM_ID = "id"
CONF_ROOM_NAME = "name"
CONF_ROOM_VALVES = "valves"
CONF_ROOM_TEMP = "temperature_sensor"
CONF_ROOM_HUM = "humidity_sensor"
CONF_ROOM_VALVE_CONTROL = "valve_control"
CONF_ROOM_VALVE_LINK = "valve_demand_link"
CONF_ROOM_WINDOWS = "window_sensors"

# --- alapértékek
DEFAULT_HYSTERESIS = 0.3  # °C
DEFAULT_MIN_SWITCH_TIME = 3  # perc
DEFAULT_BOILER_ON_TEMP = 35  # °C, 0 = nem módosítjuk a kazán célhőmérsékletét
DEFAULT_HUMIDITY_MAX_BOOST = 1.0  # °C, 0 = kikapcsolva
DEFAULT_SUMMER_TEMP = 17.0  # °C (24 órás átlag)
DEFAULT_VALVE_DRY_RUN = False
DEFAULT_WINDOW_DELAY = 5  # perc: ennyi ideig kell nyitva lennie az ablaknak
DEFAULT_REGISTER_CARD = True
DEFAULT_STALE_ENABLED = True
DEFAULT_STALE_HOURS = 6  # óra: ennyi ideje nem jelentő szenzor elavultnak számít
DEFAULT_MAX_BOOST_ENABLED = True
DEFAULT_MAX_BOOST_HOURS = 3  # óra: a szelep emelés maximális időtartama
DEFAULT_MAX_BOOST_REST = 60  # perc: pihenő a maximális idő után
DEFAULT_VALVE_BOOST_THRESHOLD = 0.8  # °C: ennyivel hidegebb legyen a szoba, hogy a szelep emeljen
DEFAULT_VALVE_BOOST_DELAY = 10  # perc: ennyi ideig álljon fenn az eltérés az emelés előtt
DEFAULT_VALVE_RELEASE_MARGIN = 0.3  # °C: a cél előtt ennyivel visszaengedi a szelepet
DEFAULT_EVENTS_ENABLED = True
DEFAULT_CYCLE_MONITOR = True
DEFAULT_CYCLE_MAX_STARTS = 5  # indítás / óra: ennyitől számít gyakori kapcsolgatásnak
DEFAULT_CYCLE_MIN_AVG_ON = 4  # perc: ennél rövidebb átlagos bekapcsolt idő gyakori kapcsolgatás
DEFAULT_CYCLE_PROTECTION = False  # a védelem beavatkozik, ezért alapból ki van kapcsolva
DEFAULT_BOILER_MIN_ON = 5  # perc: a védelem bekapcsolva ennyi ideig nem kapcsolja ki a kazánt
DEFAULT_BOILER_MIN_OFF = 5  # perc: a védelem bekapcsolva ennyi ideig nem kapcsolja be újra
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
# a szoba hőmérsékletének trendje (°C/óra): az utolsó ~30 percből, percenkénti mintákból
TREND_WINDOW_SECONDS = 30 * 60
TREND_SAMPLE_SECONDS = 60
TREND_MIN_SPAN_SECONDS = 10 * 60  # ennél rövidebb mintavételből még nem számolunk trendet
TREND_HYSTERESIS = 0.2  # °C/óra: ennél kisebb változásnál a kiadott érték nem frissül (kíméli az adatbázist)
STORAGE_VERSION = 1

# --- események és kazán-ciklusok (2.8)
EVENT_TYPE = "meross_boiler_sync_event"
CYCLE_HISTORY_SECONDS = 24 * 3600  # ennyit őrzünk meg a kazán be/ki váltásaiból
CYCLE_AVG_WINDOW_SECONDS = 2 * 3600  # az átlagos be/ki időt ennyi időre visszamenőleg számoljuk
CYCLE_MIN_SAMPLES = 3  # ennyi lezárt ciklus kell, hogy az átlag alapján jelezzünk
CYCLE_LIST_SECONDS = 12 * 3600  # a szenzor attribútumában ennyi időnyi ciklus látszik

# --- szelep szabályzás (kísérleti)
DEFAULT_VALVE_MAX_TEMP = 30.0  # °C, ha a szelep nem jelent max_temp-et
BOOST_IMMEDIATE_EXTRA = 1.0  # °C: küszöb + ennyi eltérésnél nincs várakozás
MIN_BOOST_GAIN = 1.0  # °C: ennél kisebb emelésnek nincs értelme
BOOST_TOLERANCE = 0.5  # °C: ennyi eltérésen belül a szelep célja = a mi emelésünk
BOOST_GRACE_SECONDS = 120  # írás után ennyi ideig várjuk meg a szelep visszajelzését
RESTORE_RETRY_SECONDS = 300  # visszaállítás ismétlése, ha a szelep nem reagál


def parse_month_day(value: str | None) -> tuple[int, int] | None:
    """'MM-DD' szöveg (hónap, nap) párrá alakítása; érvénytelen esetén None."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(f"2000-{value.strip()}", "%Y-%m-%d")
    except ValueError:
        return None
    return (parsed.month, parsed.day)
