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
CONF_TRV_LOG = "trv_log"  # 2.14: TRV-napló (az automatika döntései a Rendszer › Naplók oldalon)
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
# 2.19: fagyvédelem: ez alatt a szoba a szelep állapotától függetlenül hőt kér (0 = kikapcsolva)
CONF_FROST_TEMP = "frost_temp"

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
# 2.12-2.16: a kalibrált szelep ennyivel mutasson HIDEGEBBET a szoba hőmérőjénél (0..3 °C). 2.17-től csak a régi, mentett beállítás
# olvasására szolgál (előjelet vált: lásd `room_trv_offset`); az űrlap és a mentés az előjeles kulcsot használja.
CONF_ROOM_TRV_OFFSET = "trv_offset"
# 2.17: a szelep mérése a szoba hőmérőjéhez képest, előjelesen, a Meross LAN kalibráció számával azonos előjellel: a plusz
# érték melegebbet, a mínusz hidegebbet mutat a szelep a szoba hőmérőjénél (-3..+3 °C). Külön kulcs, hogy a régi, ellentétes
# előjelű értékek ne keveredhessenek az újakkal (nincs szükség verzióváltásra és átalakításra, ami kétszer lefuthatna).
CONF_ROOM_TRV_OFFSET_SIGNED = "trv_offset_signed"
# 2.18: szelepenkénti (egyedi) TRV eltolás, a több szelepes szobákhoz: {szelep entitás-azonosító: előjeles eltolás}, ugyanabban az
# alakban, mint a szoba eltolása. Csak a megadott szelepeknek van bejegyzése; amelyiknek nincs, az a szoba eltolását használja.
CONF_ROOM_VALVE_OFFSETS = "valve_trv_offsets"
# 2.19: szelep-zárás túlfűtés ellen (szobánként kapcsolható): ha a szoba a célja fölött van, nem kér hőt, és a kazán más szobának
# fűt, a plugin a szelep célját ideiglenesen lejjebb állítja (a szelep-emelés tükörképe); nyitott ablaknál is
CONF_ROOM_VALVE_CUT = "valve_cut"
# Az űrlap legfeljebb ennyi szelep eltolását teszi szerkeszthetővé (a mezők kulcsa és fordítása szám szerinti: `valve_offset_1`, ...)
MAX_VALVE_OFFSET_FIELDS = 8

# --- alapértékek
DEFAULT_HYSTERESIS = 0.3  # °C
DEFAULT_MIN_SWITCH_TIME = 5  # perc (2.19: 3 helyett 5; a rövid ciklus a gázkazánnak árt)
DEFAULT_BOILER_ON_TEMP = 35  # °C, 0 = nem módosítjuk a kazán célhőmérsékletét
DEFAULT_HUMIDITY_MAX_BOOST = 0.5  # °C, 0 = kikapcsolva (2.19: 1,0 helyett 0,5; szobánként felülírható)
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
DEFAULT_TRV_LOG = True
DEFAULT_CYCLE_MONITOR = True
DEFAULT_CYCLE_MAX_STARTS = 5  # indítás / óra: ennyitől számít gyakori kapcsolgatásnak
DEFAULT_CYCLE_MIN_AVG_ON = 4  # perc: ennél rövidebb átlagos bekapcsolt idő gyakori kapcsolgatás
DEFAULT_CYCLE_PROTECTION = True  # 2.19: alapból bekapcsolva (a kazán minimális be- és kikapcsolt ideje)
DEFAULT_BOILER_MIN_ON = 10  # perc: a védelem bekapcsolva ennyi ideig nem kapcsolja ki a kazánt (2.19: 5 helyett 10)
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
# mérését szándékosan hidegebbre állítja a szoba hőmérőjénél, a szelep a cél alatti szobában
# mindig teljesen nyit. 0 = a szelep mérése a szoba hőmérőjét követi (a 2.11 viselkedése).
# 2.17: az eltolás előjeles (szelep mérése - szoba hőmérője): a mínusz hidegebbet, a plusz melegebbet mutat a szelep. Az
# alapérték ugyanaz, mint korábban (1 °C-kal hidegebb), csak az előjele változott.
DEFAULT_TRV_OFFSET = -1.0  # °C
# 2.19: az ÚJ szoba űrlapján felajánlott eltolás 0: a kalibráció így mérés nélkül semmit nem ír a szelepbe (a negatív eltolás
# a cél fölé fűtheti a szobát, ha a kazán más szobának megy). A már mentett szobák értéke nem változik, és a mentett érték
# nélküli (2.12 előtti) szobáknál a fenti alapérték marad érvényes, hogy a frissítés ne állítsa át a szelepeket.
DEFAULT_NEW_ROOM_TRV_OFFSET = 0.0  # °C
TRV_OFFSET_MAX = 3.0  # °C: az eltolás abszolút értéke legfeljebb ennyi (mindkét előjellel)
# 2.15: 0,5 °C is lehet. A nulla és a 0,5 megkülönböztetéséhez a még nem igazolt igazítás szűkebb tűréssel
# dolgozik (`CAL_FIRST_THRESHOLD`); az igazolt szelepnél marad a széles tűrés (`CAL_THRESHOLD`).
TRV_OFFSET_MIN_ACTIVE = 0.5  # °C: ennél kisebb abszolút értékű (de nem nulla) eltolás nem lehet (a kalibráció lépésköze 0,5 °C)
# 2.13: Leállás után a radiátor maradékhője még tovább melegíti a szobát. A plugin ezt szobánként méri, és
# ha a szoba ennél többel melegedne a cél fölé, a hőigényt ennyivel előbb szünteti meg.
DEFAULT_RESIDUAL_COMP = True  # a kompenzáció korlátos és csak a megengedett túllövés fölötti részt érinti
DEFAULT_RESIDUAL_ALLOW = 0.3  # °C: ennyi túllövést megengedünk (ennyit nem kompenzálunk)
DEFAULT_FROST_TEMP = 7.0  # °C: fagyvédelem (2.19); 0 = kikapcsolva
FROST_TEMP_MAX = 12.0  # °C: a fagyvédelem küszöbe legfeljebb ennyi lehet
DEFAULT_ROOM_VALVE_CUT = False  # a szelep-zárás a szelep célját írja, ezért szobánként külön kell bekapcsolni
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
# 2.19: a sebességet fűtési alkalmanként egy minta adja (a hőigény alatti emelkedés osztva az idővel), az utolsó
# `HEATING_RATE_KEEP` alkalom mediánja a tanult érték. A korábbi, percenkénti 30 perces trend átlaga késett (a fűtés elején még a
# hűlést látta), és a gyorsan melegedő szobára kisebb számot tanult.
HEATING_RATE_MIN_SAMPLES = 3  # ennyi fűtési alkalom után használja a tanult sebességet
HEATING_RATE_KEEP = 10  # az utolsó ennyi alkalom mediánja
HEATING_SESSION_MIN_SECONDS = 20 * 60  # ennél rövidebb fűtési alkalom nem minta (a radiátor felfűtése dominál)
HEATING_SESSION_MIN_RISE = 0.2  # °C: ennél kisebb emelkedés nem minta (a hőmérő felbontása)
# 2.19.1: a hőleadás ennél rövidebb szünete nem szakítja meg a fűtési alkalmat: a szelep elzárása (a szelep állapotához kötött
# hőigénynél ilyenkor a kazán is leáll), a kazán ciklusvédelmi szünete, egy kimaradt mérés vagy egy újraindítás. Ha a szünet
# tovább tart, az alkalom a szünet kezdetéig mért adattal zárul (minta, ha elég hosszú).
HEATING_SESSION_PAUSE_MAX = 15 * 60
HEATING_SESSION_SAVE_SECONDS = 600  # a futó alkalom legfeljebb ennyi késéssel kerül a lemezre (újraindítás után folytatható)
HEATING_DROP_LOG_SECONDS = 3600  # ugyanazt az elvetési okot szobánként legfeljebb óránként egyszer írja a TRV-naplóba

# --- becsült gázfogyasztás (2.10)
GAS_M3_PER_HOUR_MIN = 0.1
GAS_M3_PER_HOUR_MAX = 20.0
GAS_MAX_GAP_SECONDS = 600  # ennél hosszabb kihagyás (újraindítás, elérhetetlen kazán) alatt nem számolunk fogyasztást
GAS_SAVE_SECONDS = 300  # a számlálót legfeljebb ilyen gyakran mentjük
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
# 2.13.1: egy szelep váratlan (nem parancs-) hibáját legfeljebb ilyen gyakran naplózzuk részletesen (másodperc)
VALVE_ERROR_LOG_SECONDS = 1800
# 2.13.1: a "a kazán nem támogat fűtő módot" figyelmeztetés ismétlése (másodperc)
BOILER_MODE_WARN_SECONDS = 1800

# --- szelep hőmérő automata kalibráció (2.11)
# A szelep a radiátor mellett méri a hőmérsékletet, ezért fűtés közben melegebbnek látja a szobát.
# Mérni csak akkor érdemes, ha a radiátor már kihűlt, ezért a kalibráció csak csendes időben dolgozik.
# 2.16.2: 90 helyett 45 perc. Fűtési időben a szoba egy óra alatt is kihűl, és a fűtés újraindul, így a rögzített 90 perc
# szinte soha nem telt le. A "kihűlt-e a radiátor" kérdést mostantól a szelep mérésének csúszása (`CAL_MAX_DRIFT`) dönti el:
# a gyorsan hűlő radiátornál hamarabb mér, a lassúnál tovább vár. A 45 perc alsó határ (a kazán / a szelep ennyi ideje nem fűt).
CAL_QUIET_SECONDS = 45 * 60  # ennyi ideje nem fűt a kazán / nem nyitott a szelep, mielőtt mér
CAL_SAMPLE_SECONDS = 150  # két minta között legalább ennyi idő (a hub kb. 3 percenként jelent)
CAL_MIN_SAMPLES = 6  # ennyi egymás utáni, stabil minta kell a döntéshez (kb. 12 perc)
CAL_MAX_SAMPLES = 12
CAL_SAMPLE_MAX_AGE = 40 * 60  # ennél régebbi minta nem számít
CAL_MAX_SPREAD = 0.8  # °C: a minták eltérései ennyin belül legyenek (stabil mérés)
# 2.16.2: a hűlő radiátor a szelep mérését lassan, de egyirányba húzza (a szelep egyre hidegebbet mutat). A mintákra illesztett
# egyenes meredeksége (a szoba hőmérője mínusz a szelep mérése, °C/óra) ennél nagyobb: a radiátor még hűl, a mérés vár.
# A maradék hiba kb. a meredekség és a radiátor hűlési időállandójának szorzata (0,6 °C/óra és 25 perc: ~0,25 °C).
# Szimulált, zajos (0,05 °C) lapos szelepnél a hat mintás ablakok ~90%-a átmegy ezen; a 0,4-es határ már a felét elutasítaná.
CAL_MAX_DRIFT = 0.6  # °C/óra
CAL_MAX_ROOM_SPREAD = 0.6  # °C: a szoba hőmérője a mintavétel alatt ennyinél jobban nem ingadozhat
CAL_MAX_TREND = 0.6  # °C/óra: a szoba hőmérője ennél gyorsabban nem változhat mérés közben
CAL_THRESHOLD = 0.8  # °C: az igazolt (már rendben mért) szelepnél ennél kisebb eltérést nem korrigál
# 2.15: A még nem igazolt igazításnál (első beállítás, módosítás vagy becslés után) szűkebb a tűrés, különben a 0,5 °C-os
# eltolás "rendben"-ként elveszne. A kalibráció lépésköze 0,5 °C, így az igazítás után a maradék legfeljebb 0,25 °C;
# a 0,4 °C ehhez még ~0,15 °C mérési zajt enged anélkül, hogy felesleges módosítás indulna.
# 2.19: a szűk tűrés nem változott (0,5-re emelve a 0,5 °C-os eltolás mérési zaj mellett "rendben"-ként elveszne). A még nem
# igazolt szelep oda-vissza lépkedését (a ±0,5 °C-os mérési bizonytalanság miatt) külön szabály szünteti meg: egy lépésnyi
# finomítás után a következő mérés már a széles tűréssel (`CAL_THRESHOLD`) dönt (`ValveCal.fine_done`).
CAL_FIRST_THRESHOLD = 0.4  # °C
CAL_JUDGE_MIN = 1.0  # °C: ennél kisebb módosítás hatását nem ítéli meg (a mérési zajtól nem különböztethető meg)
CAL_MAX_DIFF = 3.0  # °C: ennél nagyobb eltérés rossz hőmérő-elhelyezésre utal, ahhoz nem nyúl
CAL_MAX_TOTAL = 4.0  # °C: az eredeti kalibrációtól legfeljebb ennyit mozdul el
CAL_MIN_INTERVAL = 2 * 3600  # két módosítás között legalább ennyi idő telik el szelepenként
CAL_MAX_PER_DAY = 4  # szelepenként legfeljebb ennyi automatikus (mérésből számolt) módosítás 24 óra alatt
# 2.16: az eltolás megváltoztatása (a felhasználó kérése) nem szabályozási kör: több kell neki, mert tesztelés közben
# egymás után többször is átállíthatják; a napi 4 módosítás elfogyása után a kérés órákig, akár másnapig sem teljesülne
CAL_MAX_PER_DAY_USER = 12
CAL_GLOBAL_SPACING = 300  # másodperc két szelep módosítása között (a Meross hub kímélése)
# 2.16.1: az eltolás-váltás (a felhasználó kérése) nem várhat a mérésből számolt módosítások 5 perces szünetére: 6 szelepnél az
# utolsó 25 percig sem kapta volna meg a számot, és a felhasználó egyetlen szelepet figyelve semmit nem látott változni. A hub
# parancsonként kevés terhelést kap, 15 másodperc bőven elég a sorbaállításhoz.
CAL_USER_SPACING = 15
CAL_SETTLE_SECONDS = 600  # módosítás után ennyit vár az új mérésre (a hub ritkán jelent)
CAL_CONFIRM_SECONDS = 60  # ennyi idő után nézi meg, hogy a szám-entitás megtartotta-e az új értéket
CAL_REVERT_TRIES = 3  # a visszaállítást ennyiszer próbálja, mielőtt feladja és felfüggeszt
CAL_MAX_RANGE = 30.0  # °C: ennél nagyobb tartományú szám-entitás nem kalibráció (nem nyúl hozzá)
CAL_MAX_STRIKES = 2  # ennyi egymás utáni hatástalan módosítás után felfüggeszti a szelepet
# 2.19: fokozatos felfüggesztés: az első 1 nap, a második 3 nap, a további 7 nap. A fokozat akkor áll vissza, ha egy módosítás
# igazoltan hatásos volt, ha a felhasználó átállítja a szelep TRV eltolását, vagy a `reset_calibration` szolgáltatás hívásakor.
CAL_SUSPEND_STEPS = (1 * 24 * 3600, 3 * 24 * 3600, 7 * 24 * 3600)
CAL_SUSPEND_SECONDS = CAL_SUSPEND_STEPS[-1]  # a felfüggesztés leghosszabb ideje
# 2.19: a hatástalannak mért módosítást nem állítja vissza azonnal: a két mérés más hőállapotban készül, és a szelep és a szoba
# természetes különbségének elmozdulása (hidegebb éjszaka, hideg fal) egy jó módosítást is hatástalannak mutathat. Az első
# sikertelen ellenőrzés után legalább ennyi idő múlva újra mér, és csak a második sikertelen ellenőrzés számít hibapontnak.
CAL_RETEST_SECONDS = 2 * 3600
CAL_RECHECK_SECONDS = 6 * 3600  # rendben lévő szelepet ennyi időnként mér újra
CAL_DISCOVERY_RETRY = 600  # hiányzó kalibráció-entitást ennyi időnként keres újra
CAL_READING_MIN = 5.0  # °C: ezen kívüli szelepmérést nem használ
CAL_READING_MAX = 40.0
# 2.14: Az eltolás megváltoztatásakor a különbség mérés nélkül alkalmazható (a kalibráció additív): ha a szelep az
# előző eltoláshoz volt beállítva, az új beállításhoz pontosan az eltolások különbségével kell elmozdítani.
CAL_BIAS_MIN_SHIFT = 0.25  # °C: ekkora (vagy nagyobb) eltolás-váltást alkalmaz azonnal; a kisebb mérési zaj
# 2.15: A 2.14 előtti állományban nincs rögzítve, mihez volt igazítva a szelep. Ilyenkor (csak egyszer, a frissítés után)
# a szelep eredeti és mostani kalibrációjának különbségéből becsüljük (az igazítás additív), ha az hihető eltolás.
CAL_GUESS_MAX = TRV_OFFSET_MAX + 0.25  # °C: ennél nagyobb (abszolút értékű) becsült igazítás nem hihető (nincs becslés)
# 2.16: Ha a kalibráció-számot kézzel (vagy az alkalmazásból) átállították, a szelep igazítása a rögzítettből kiszámolható
# (a kalibráció additív), és a normál 0..3 °C-os eltolás-tartományon kívülre is eshet. Ennél nagyobb érték nem hihető.
CAL_TARGET_LIMIT = 15.0  # °C
# 2.16: A Meross LAN a számot az új értékre állítja (optimista), és a hub következő jelentése írja felül. Ha az eszköz nem fogadta
# el a módosítást, a régi érték a 60 másodperces megerősítés után, percekkel később is visszajöhet: ezt ennyi időn belül észleli.
CAL_LATE_REVERT_SECONDS = 3 * 3600
# Ennyi késői visszaállás után 24 órán belül a szelep felfüggesztődik (akkor is, ha közben egy mérés rendben lévőnek találta:
# a mérés a visszaállás előtt készült). Különben a módosít - rendben - visszaáll kör naponta többször megismétlődne.
CAL_LATE_REVERTS_MAX = 2
CAL_IDLE_KEEP_SECONDS = 120  # a "kihűlt a radiátor" számláló ennyi leállás után még hihető (újratöltés); hosszabb kiesés után nem
# 2.14: a TRV-naplóba ugyanazon szelep "vár / mintavétel" jellegű állapotváltásai ilyen ritkán kerülnek (másodperc);
# az eredmény-jellegű állapotok (rendben, hiba, javaslat, felfüggesztés, határ) azonnal.
TRV_LOG_STATE_MIN_INTERVAL = 900

# --- maradékhő tanulása (2.13)
# A hőigény megszűnése után addig figyeli a szoba hőmérőjét, amíg a csúcs el nem múlik (legfeljebb
# `RESIDUAL_WINDOW_SECONDS`). Csak tiszta mérést fogad el: a kazán leáll és nem indul újra, nincs ablaknyitás,
# a szoba hőmérője megbízható, a szelepek célja nem változik, nincs "Fűts most" / előfűtés.
RESIDUAL_ALLOW_MAX = 1.0  # °C: a megengedett túllövés felső határa
RESIDUAL_MIN_ON_SECONDS = 180  # ennél rövidebb hőigény után nem mérünk (indulási zaj)
RESIDUAL_WINDOW_SECONDS = 60 * 60  # ennyi ideig figyeli a csúcsot a leállás után
RESIDUAL_MIN_WINDOW_SECONDS = 10 * 60  # a csúcs elmúltát legkorábban ennyi idő után fogadja el
RESIDUAL_FALL = 0.2  # °C: a csúcshoz képest ennyi esés = a csúcs elmúlt
# 2.19: a leállás után a kazán a kapcsolási késleltetés miatt járhat még (minimális kapcsolási idő, illetve a ciklusvédelem
# minimális bekapcsolt ideje) + `RESIDUAL_BOILER_GRACE_EXTRA`, de legfeljebb `RESIDUAL_BOILER_GRACE_SECONDS` ideig. Korábban
# rögzített 15 perc volt: ennyi idő alatt egy másik szoba miatt járó kazán a nyitott szelepen át rendes fűtést adott a méréshez.
RESIDUAL_BOILER_GRACE_SECONDS = 15 * 60  # a türelmi idő felső határa
RESIDUAL_BOILER_GRACE_EXTRA = 2 * 60
# 2.19: ha a csúcs után nincs visszaesés (60 perc telt el), a mérés csak akkor érvényes, ha a legmagasabb értéket az első
# ennyi időben érte el a szoba, vagyis az ablak utolsó negyedórájában már nem melegedett tovább. A lassú (nagy tömegű)
# radiátor maradékhője is átadódik ennyi idő alatt; ami az ablak végén is melegíti a szobát, az más hőforrás (napsütés, főzés).
RESIDUAL_PEAK_MAX_SECONDS = 45 * 60
RESIDUAL_SAMPLE_MAX_AGE = 30 * 24 * 3600  # ennél régebbi mérés nem számít (évszakváltás)
RESIDUAL_TARGET_TOLERANCE = 0.05  # °C: a szelepek célja ennyinél jobban nem változhat a mérés alatt
RESIDUAL_SAMPLE_MAX = 1.5  # °C: ennél nagyobb emelkedés nem hihető maradékhőnek (napsütés, kézi fűtés), erre vágjuk
RESIDUAL_KEEP = 9  # az utolsó ennyi mérés mediánját használja
RESIDUAL_MIN_SAMPLES = 4  # ennyi mérés kell, mielőtt a tanult érték számít
RESIDUAL_LEAD_MAX = 0.5  # °C: ennél többel soha nem állítja le előbb a hőigényt (2.19: 0,8 helyett 0,5: a bekapcsolási küszöb is ennyivel csúszik)
RESIDUAL_LEAD_MIN = 0.1  # °C: ennél kisebb korrekciót nem alkalmaz (a hőmérő felbontásán belül van)
RESIDUAL_LEAD_STEP = 0.05  # °C: a korrekció ilyen lépésekre kerekített (ne ugráljon)

# --- újraindítás-biztonság (2.11)
STARTUP_SETTLE_SECONDS = 90 # a HA indulása után ennyi ideig a vezérlő csak olvas (az entitások még töltődnek)
RESUME_WINDOW_SECONDS = 600  # indulás után ennyi ideig folytatja a fűtés hiszterézisét a kazán állapotából
SAMPLE_TEMP_MIN = -60.0  # °C: a tárolt kinti minták ésszerű tartománya
SAMPLE_TEMP_MAX = 60.0

# --- 2.19: kiesés-kezelés, fagyvédelem, kazánparancs, elakadt hőmérő, szelep-zárás
EVENT_DEBOUNCE_SECONDS = 0.5  # az egyszerre érkező állapotváltozásokat ennyi idő alatt egy kiértékelésbe vonja össze
# Ha a szoba egyik szelepe sem érhető el (hub, Wi-Fi, Meross LAN hiba), a szelep a saját céljával tovább szabályoz, csak a HA nem
# látja. Ennyi idő után a szoba a hőmérője és az utolsó ismert célja alapján kér tovább hőt (rövid újracsatlakozás nem számít).
VALVE_LOST_GRACE_SECONDS = 10 * 60
# Ha egyetlen szoba sem értékelhető (nincs elérhető szelep, és hőmérő + utolsó ismert cél sincs), ennyi idő után a kazán kikapcsol.
BLIND_OFF_SECONDS = 30 * 60
# A tartalék vezérlés (elérhetetlen szelepek) csak akkor kérhet tartósan hőt, ha a szoba melegszik is: ha a szelep zárva maradt
# (például lemerült az eleme), a szoba a végtelenségig járatná a kazánt. Ha a szoba járó kazán mellett ennyi idő alatt sem
# melegszik legalább `FALLBACK_MIN_RISE` fokot, a hőigénye `FALLBACK_REST_SECONDS` időre szünetel, utána újra próbálja.
FALLBACK_STALL_SECONDS = 2 * 3600
FALLBACK_MIN_RISE = 0.3  # °C
FALLBACK_REST_SECONDS = 6 * 3600
LAST_TARGET_MIN = 5.0  # °C: a mentett utolsó cél hihető tartománya
LAST_TARGET_MAX = 35.0
FROST_HYSTERESIS = 1.0  # °C: a fagyvédelem ennyivel a küszöb fölött enged el (és ez a fagyvédelmi cél is)
FROST_CONFIRM_SECONDS = 5 * 60  # ennyi ideig kell a küszöb alatt lennie (egyetlen hibás mérés ne indítson fűtést)
FROST_READING_MIN = -30.0  # °C: ennél hidegebb mérés már nem hihető fagynak sem (hibaérték)
# a kazán termosztátjának küldött parancs
BOILER_RETRY_SECONDS = 60  # sikertelen (vagy nem követett) parancs után leghamarabb ennyi idő múlva próbálja újra
BOILER_FAIL_ISSUE_AFTER = 3  # ennyi egymás utáni sikertelen / nem követett parancs után jelez a Javítások között
# Elakadt szoba hőmérő: a szoba hőt kér, a kazán ennyi ideje megy, és a hőmérő közben egyszer sem jelentett. A fűtött szobában
# a hőmérsékletnek változnia kell; ha ugyanazon az eszközön a páratartalom-mérő jelent, az eszköz él (a hőmérséklet tényleg áll).
SENSOR_STUCK_SECONDS = 45 * 60
# szelep-zárás (a szelep-emelés tükörképe)
CUT_START_MARGIN = 0.3  # °C: ennyivel a (tényleges) cél fölött indul
CUT_RELEASE_MARGIN = 0.1  # °C: eddig tart (hiszterézis)
CUT_DROP = 3.0  # °C: ennyivel állítja lejjebb a szelep célját (a legnagyobb TRV eltolás mellett is zár)
CUT_MAX_SECONDS = 30 * 60  # legfeljebb ennyi ideig tartja egyben: utána visszaállít, hogy a szelep saját menetrendje érvényesülhessen
CUT_PAUSE_SECONDS = 5 * 60  # visszaállítás után ennyi ideig nem zár újra (a szelep jelentse a valódi célját)
CUT_SETTLE_SECONDS = 120  # a preset visszaállítása után ennyi idő múlva fogadja el a szelep célját akkor is, ha az egyezik a zárás értékével

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
