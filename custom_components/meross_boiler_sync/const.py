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
# 2.9: "Fűts most" (megemelt cél) és előfűtés (mind külön ki/be kapcsolható)
CONF_MANUAL_BOOST_ENABLED = "manual_boost_enabled"
CONF_MANUAL_BOOST_MINUTES = "manual_boost_minutes"
CONF_MANUAL_BOOST_OFFSET = "manual_boost_offset"
CONF_MANUAL_BOOST_END_ON_TARGET = "manual_boost_end_on_target"
CONF_PREHEAT_ENABLED = "preheat_enabled"
CONF_PREHEAT_MAX_MINUTES = "preheat_max_minutes"
CONF_PREHEAT_HOLD_MINUTES = "preheat_hold_minutes"
CONF_PREHEAT_DEFAULT_RATE = "preheat_default_rate"
# 2.10: becsült gázfogyasztás az Energia fülhöz (külön kapcsolható)
CONF_GAS_ESTIMATE = "gas_estimate_enabled"
CONF_GAS_M3_PER_HOUR = "gas_m3_per_hour"
# 2.11: a radiátor szelepek hőmérőjének automata kalibrációja (külön kapcsolható, alapból ki)
CONF_CALIBRATION_ENABLED = "calibration_enabled"
CONF_CALIBRATION_DRY_RUN = "calibration_dry_run"
# 2.13: a maradékhő (a hőigény megszűnése utáni további melegedés) szobánkénti tanulása és kompenzálása
CONF_RESIDUAL_COMP = "residual_comp"
CONF_RESIDUAL_ALLOW = "residual_allow"

# --- szoba kulcsok
CONF_ROOM_ID = "id"
CONF_ROOM_NAME = "name"
CONF_ROOM_VALVES = "valves"
CONF_ROOM_TEMP = "temperature_sensor"
CONF_ROOM_HUM = "humidity_sensor"
CONF_ROOM_VALVE_CONTROL = "valve_control"
CONF_ROOM_VALVE_LINK = "valve_demand_link"
CONF_ROOM_WINDOWS = "window_sensors"
CONF_ROOM_PREHEAT = "preheat_schedule"  # [{"days": [0..6], "time": "HH:MM", "temperature": 22.0}]
CONF_ROOM_CALIBRATE = "calibrate_valves"  # a szoba szelepeinek kalibrálása (a globális kapcsoló mellett)
CONF_ROOM_TRV_OFFSET = "trv_offset"  # 2.12: a kalibrált szelep ennyivel mutasson hidegebbet a szoba hőmérőjénél

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
DEFAULT_MANUAL_BOOST_ENABLED = True
DEFAULT_MANUAL_BOOST_MINUTES = 60  # perc: a "Fűts most" alap időtartama
DEFAULT_MANUAL_BOOST_OFFSET = 2.0  # °C: ennyivel emeli meg a szoba célját
DEFAULT_MANUAL_BOOST_END_ON_TARGET = False  # véget ér-e a Fűts most, amint a szoba eléri a megemelt célt
DEFAULT_PREHEAT_ENABLED = False  # az előfűtés magától indul, ezért alapból ki van kapcsolva
DEFAULT_PREHEAT_MAX_MINUTES = 240  # perc: ennél korábban nem kezd előfűteni (4 óra)
DEFAULT_PREHEAT_HOLD_MINUTES = 30  # perc: a "kész" időpont után ennyi ideig tartja a célt
DEFAULT_PREHEAT_RATE = 1.0  # °C/óra: ennyivel számol, amíg nem tanulta meg a szoba felfűtési sebességét
DEFAULT_GAS_ESTIMATE = False  # a becslés új szenzort hoz létre, ezért alapból ki van kapcsolva
DEFAULT_GAS_M3_PER_HOUR = 1.6  # m³/óra: a kazán gázfogyasztása bekapcsolt állapotban (a kártyán is ez az alap)
DEFAULT_CALIBRATION_ENABLED = False  # a kalibráció tartós beállítást ír a szelepbe, ezért alapból ki van kapcsolva
DEFAULT_CALIBRATION_DRY_RUN = False
DEFAULT_ROOM_CALIBRATE = True  # a globális kapcsoló bekapcsolása után minden hőmérős szoba részt vesz
# 2.12: A szelep saját szabályzása arányos: kis eltérésnél csak részben nyit. Ha a kalibráció a szelep
# mérését szándékosan ennyivel hidegebbre állítja a szoba hőmérőjénél, a szelep a cél alatti szobában
# mindig teljesen nyit. 0 = a szelep mérése a szoba hőmérőjét követi (a 2.11 viselkedése).
DEFAULT_TRV_OFFSET = 1.0  # °C
TRV_OFFSET_MAX = 3.0  # °C
TRV_OFFSET_MIN_ACTIVE = 1.0  # °C: kisebb (de nem nulla) eltolás nem érvényesülne a kalibráció tűrése miatt
# 2.13: Leállás után a radiátor maradékhője még tovább melegíti a szobát. A plugin ezt szobánként méri, és
# ha a szoba ennél többel melegedne a cél fölé, a hőigényt ennyivel előbb szünteti meg.
DEFAULT_RESIDUAL_COMP = True  # a kompenzáció korlátos és csak a megengedett túllövés fölötti részt érinti
DEFAULT_RESIDUAL_ALLOW = 0.3  # °C: ennyi túllövést megengedünk (ennyit nem kompenzálunk)
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

# --- "Fűts most" és előfűtés (2.9)
MANUAL_BOOST_MIN_MINUTES = 5
MANUAL_BOOST_MAX_MINUTES = 480
MANUAL_BOOST_MIN_OFFSET = 0.5
MANUAL_BOOST_MAX_OFFSET = 5.0
MAX_RAISED_TARGET = 30.0  # °C: a megemelt (kézi / előfűtési) cél felső határa
HEATING_RATE_MIN = 0.1  # °C/óra: ennél lassabb / gyorsabb mintát nem tanul meg
HEATING_RATE_MAX = 5.0
HEATING_RATE_MIN_SAMPLES = 20  # ennyi percnyi fűtés után használja a tanult sebességet

# --- becsült gázfogyasztás (2.10)
GAS_M3_PER_HOUR_MIN = 0.1
GAS_M3_PER_HOUR_MAX = 20.0
GAS_MAX_GAP_SECONDS = 600  # ennél hosszabb kihagyás (újraindítás, elérhetetlen kazán) alatt nem számolunk fogyasztást
GAS_SAVE_SECONDS = 300  # a számlálót legfeljebb ilyen gyakran mentjük
HEATING_RATE_WINDOW = 240  # a tanulás ennyi minta után "állandó ablakú" átlag
HEATING_RATE_MIN_TREND = 0.15  # °C/óra: ennél kisebb melegedés nem számít mintának
PREHEAT_SAFETY = 1.15  # a becsült felfűtési időt ennyivel szorozza
PREHEAT_GRACE_SECONDS = 300  # ennyivel később érhető el a cél, ez még nem "nem éri el"
PREHEAT_DONE_TOLERANCE = 0.2  # °C: ennyire a céltól már "kész"

# --- szelep szabályzás (kísérleti)
DEFAULT_VALVE_MAX_TEMP = 30.0  # °C, ha a szelep nem jelent max_temp-et
BOOST_IMMEDIATE_EXTRA = 1.0  # °C: küszöb + ennyi eltérésnél nincs várakozás
MIN_BOOST_GAIN = 1.0  # °C: ennél kisebb emelésnek nincs értelme
BOOST_TOLERANCE = 0.5  # °C: ennyi eltérésen belül a szelep célja = a mi emelésünk
BOOST_GRACE_SECONDS = 120  # írás után ennyi ideig várjuk meg a szelep visszajelzését
RESTORE_RETRY_SECONDS = 300  # visszaállítás ismétlése, ha a szelep nem reagál
# 2.10.2: a szelepnek küldött célhőmérséklet kemény határai (a Meross vezérlő a határon kívüli
# értéket elutasítja, a folyamatos újrapróbálás pedig lefagyaszthatja)
VALVE_TARGET_MIN = 6.0  # °C: ennél kisebb célt soha nem küldünk a szelepnek
VALVE_TARGET_MAX = 34.0  # °C: ennél nagyobbat sem
# sikertelen parancs után egyre ritkábban próbálkozunk újra (másodperc)
VALVE_RETRY_STEPS = (120, 300, 900, 1800, 3600)

# --- szelep hőmérő automata kalibráció (2.11)
# A szelep a radiátor mellett méri a hőmérsékletet, ezért fűtés közben melegebbnek látja a szobát.
# Mérni csak akkor érdemes, ha a radiátor már kihűlt, ezért a kalibráció csak csendes időben dolgozik.
CAL_QUIET_SECONDS = 90 * 60  # ennyi ideje nem fűt a kazán / nem nyitott a szelep, mielőtt mér
CAL_SAMPLE_SECONDS = 150  # két minta között legalább ennyi idő (a hub kb. 3 percenként jelent)
CAL_MIN_SAMPLES = 6  # ennyi egymás utáni, stabil minta kell a döntéshez (kb. 12 perc)
CAL_MAX_SAMPLES = 12
CAL_SAMPLE_MAX_AGE = 40 * 60  # ennél régebbi minta nem számít
CAL_MAX_SPREAD = 0.8  # °C: a minták eltérései ennyin belül legyenek (stabil mérés)
CAL_MAX_ROOM_SPREAD = 0.6  # °C: a szoba hőmérője a mintavétel alatt ennyinél jobban nem ingadozhat
CAL_MAX_TREND = 0.6  # °C/óra: a szoba hőmérője ennél gyorsabban nem változhat mérés közben
CAL_THRESHOLD = 0.8  # °C: ennél kisebb eltérést nem korrigál
CAL_JUDGE_MIN = 1.0  # °C: ennél kisebb módosítás hatását nem ítéli meg (a mérési zajtól nem különböztethető meg)
CAL_MAX_DIFF = 3.0  # °C: ennél nagyobb eltérés rossz hőmérő-elhelyezésre utal, ahhoz nem nyúl
CAL_MAX_TOTAL = 4.0  # °C: az eredeti kalibrációtól legfeljebb ennyit mozdul el
CAL_MIN_INTERVAL = 2 * 3600  # két módosítás között legalább ennyi idő telik el szelepenként
CAL_MAX_PER_DAY = 4  # szelepenként legfeljebb ennyi módosítás 24 óra alatt
CAL_GLOBAL_SPACING = 300  # másodperc két szelep módosítása között (a Meross hub kímélése)
CAL_SETTLE_SECONDS = 600  # módosítás után ennyit vár az új mérésre (a hub ritkán jelent)
CAL_CONFIRM_SECONDS = 60  # ennyi idő után nézi meg, hogy a szám-entitás megtartotta-e az új értéket
CAL_REVERT_TRIES = 3  # a visszaállítást ennyiszer próbálja, mielőtt feladja és felfüggeszt
CAL_MAX_RANGE = 30.0  # °C: ennél nagyobb tartományú szám-entitás nem kalibráció (nem nyúl hozzá)
CAL_MAX_STRIKES = 2  # ennyi egymás utáni hatástalan módosítás után felfüggeszti a szelepet
CAL_SUSPEND_SECONDS = 7 * 24 * 3600  # a felfüggesztés ideje
CAL_RECHECK_SECONDS = 6 * 3600  # rendben lévő szelepet ennyi időnként mér újra
CAL_DISCOVERY_RETRY = 600  # hiányzó kalibráció-entitást ennyi időnként keres újra
CAL_READING_MIN = 5.0  # °C: ezen kívüli szelepmérést nem használ
CAL_READING_MAX = 40.0

# --- maradékhő tanulása (2.13)
# A hőigény megszűnése után addig figyeli a szoba hőmérőjét, amíg a csúcs el nem múlik (legfeljebb
# `RESIDUAL_WINDOW_SECONDS`). Csak tiszta mérést fogad el: a kazán leáll és nem indul újra, nincs ablaknyitás,
# a szoba hőmérője megbízható, a szelepek célja nem változik, nincs "Fűts most" / előfűtés.
RESIDUAL_ALLOW_MAX = 1.0  # °C: a megengedett túllövés felső határa
RESIDUAL_MIN_ON_SECONDS = 180  # ennél rövidebb hőigény után nem mérünk (indulási zaj)
RESIDUAL_WINDOW_SECONDS = 60 * 60  # ennyi ideig figyeli a csúcsot a leállás után
RESIDUAL_MIN_WINDOW_SECONDS = 10 * 60  # a csúcs elmúltát legkorábban ennyi idő után fogadja el
RESIDUAL_FALL = 0.2  # °C: a csúcshoz képest ennyi esés = a csúcs elmúlt
RESIDUAL_BOILER_GRACE_SECONDS = 15 * 60  # a leállás után ennyi ideig járhat még a kazán (kapcsolási késleltetés)
RESIDUAL_TARGET_TOLERANCE = 0.05  # °C: a szelepek célja ennyinél jobban nem változhat a mérés alatt
RESIDUAL_SAMPLE_MAX = 1.5  # °C: ennél nagyobb emelkedés nem hihető maradékhőnek (napsütés, kézi fűtés), erre vágjuk
RESIDUAL_KEEP = 9  # az utolsó ennyi mérés mediánját használja
RESIDUAL_MIN_SAMPLES = 4  # ennyi mérés kell, mielőtt a tanult érték számít
RESIDUAL_LEAD_MAX = 0.8  # °C: ennél többel soha nem állítja le előbb a hőigényt
RESIDUAL_LEAD_MIN = 0.1  # °C: ennél kisebb korrekciót nem alkalmaz (a hőmérő felbontásán belül van)
RESIDUAL_LEAD_STEP = 0.05  # °C: a korrekció ilyen lépésekre kerekített (ne ugráljon)

# --- újraindítás-biztonság (2.11)
STARTUP_SETTLE_SECONDS = 90 # a HA indulása után ennyi ideig a vezérlő csak olvas (az entitások még töltődnek)
RESUME_WINDOW_SECONDS = 600  # indulás után ennyi ideig folytatja a fűtés hiszterézisét a kazán állapotából
SAMPLE_TEMP_MIN = -60.0  # °C: a tárolt kinti minták ésszerű tartománya
SAMPLE_TEMP_MAX = 60.0

# --- szenzor hihetőségi ellenőrzés (2.11.1)
# Egy hibás szenzor (kimerülő elem, hibaérték, ugráló mérés) hideget vagy meleget hazudna, és a kazánt
# feleslegesen járatná vagy leállítaná. A képtelen vagy ugráló értékre a plugin nem épít.
SENSOR_TEMP_MIN = 1.0  # °C: ennél hidegebb / melegebb szobamérés nem hihető (pl. 0, -127 vagy 85 °C hibaérték)
SENSOR_TEMP_MAX = 45.0
SENSOR_PATH_WINDOW = 20 * 60  # másodperc: ennyi idő alatt vizsgáljuk a mérés ingadozását
SENSOR_PATH_MAX = 6.0  # °C: ennyinél többet ennyi idő alatt (fel-le) ugráló szenzor nem megbízható
SENSOR_STEP_MIN = 1.0  # °C: ennél kisebb lépés mérési zajnak számít, az ingadozásba nem számít bele
SENSOR_HOLD_SECONDS = 30 * 60  # gyanús érték után ennyi ideig nem bízunk a szenzorban
HUMIDITY_MIN = 0.0  # %: a páramérő hihető tartománya
HUMIDITY_MAX = 100.0


def parse_month_day(value: str | None) -> tuple[int, int] | None:
    """'MM-DD' szöveg (hónap, nap) párrá alakítása; érvénytelen esetén None."""
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.strptime(f"2000-{value.strip()}", "%Y-%m-%d")
    except ValueError:
        return None
    return (parsed.month, parsed.day)
