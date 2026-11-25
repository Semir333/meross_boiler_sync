"""A kazán vezérlés logikája: szobák hőigénye + nyári mód."""
from __future__ import annotations

import asyncio
import copy
import logging
import math
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import (
    AVG_WINDOW_SECONDS,
    BLIND_OFF_SECONDS,
    BOILER_FAIL_ISSUE_AFTER,
    BOILER_MODE_WARN_SECONDS,
    BOILER_RETRY_SECONDS,
    BOOST_GRACE_SECONDS,
    BOOST_IMMEDIATE_EXTRA,
    BOOST_TOLERANCE,
    COMFORT_MIN_TARGET,
    CONF_BOILER,
    CONF_CALIBRATION_DRY_RUN,
    CONF_CALIBRATION_ENABLED,
    CONF_BOILER_MIN_OFF,
    CONF_BOILER_MIN_ON,
    CONF_BOILER_ON_TEMP,
    CONF_CYCLE_MAX_STARTS,
    CONF_CYCLE_MIN_AVG_ON,
    CONF_CYCLE_MONITOR,
    CONF_CYCLE_PROTECTION,
    CONF_EVENTS_ENABLED,
    CONF_FROST_TEMP,
    CONF_HUMIDITY_MAX_BOOST,
    CONF_HYSTERESIS,
    CONF_MANUAL_BOOST_ENABLED,
    CONF_MANUAL_BOOST_END_ON_TARGET,
    CONF_MANUAL_BOOST_MINUTES,
    CONF_MANUAL_BOOST_OFFSET,
    CONF_MIN_SWITCH_TIME,
    CONF_GAS_ESTIMATE,
    CONF_GAS_M3_PER_HOUR,
    CONF_PREHEAT_DEFAULT_RATE,
    CONF_PREHEAT_ENABLED,
    CONF_PREHEAT_HOLD_MINUTES,
    CONF_PREHEAT_MAX_MINUTES,
    CONF_OUTDOOR_SENSOR,
    CONF_RESIDUAL_ALLOW,
    CONF_RESIDUAL_COMP,
    CONF_ROOM_CALIBRATE,
    CONF_ROOM_HUM,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_PREHEAT,
    CONF_ROOM_TEMP,
    CONF_ROOM_VALVE_CONTROL,
    CONF_ROOM_VALVE_CUT,
    CONF_ROOM_VALVE_LINK,
    CONF_ROOM_VALVES,
    CONF_ROOMS,
    CONF_SUMMER_END,
    CONF_SUMMER_START,
    CONF_MAX_BOOST_ENABLED,
    CONF_MAX_BOOST_HOURS,
    CONF_MAX_BOOST_REST,
    CONF_STALE_ENABLED,
    CONF_STALE_HOURS,
    CONF_ROOM_WINDOWS,
    CONF_SUMMER_TEMP,
    CONF_TRV_LOG,
    CONF_WINDOW_DELAY,
    CONF_VALVE_BOOST_DELAY,
    CONF_VALVE_BOOST_THRESHOLD,
    CONF_VALVE_DRY_RUN,
    CONF_VALVE_RELEASE_MARGIN,
    DEFAULT_BOILER_MIN_OFF,
    DEFAULT_BOILER_MIN_ON,
    DEFAULT_BOILER_ON_TEMP,
    DEFAULT_CALIBRATION_DRY_RUN,
    DEFAULT_CALIBRATION_ENABLED,
    DEFAULT_CYCLE_MAX_STARTS,
    DEFAULT_CYCLE_MIN_AVG_ON,
    DEFAULT_CYCLE_MONITOR,
    DEFAULT_CYCLE_PROTECTION,
    DEFAULT_EVENTS_ENABLED,
    DEFAULT_FROST_TEMP,
    DEFAULT_HUMIDITY_MAX_BOOST,
    DEFAULT_HYSTERESIS,
    DEFAULT_MANUAL_BOOST_ENABLED,
    DEFAULT_MANUAL_BOOST_END_ON_TARGET,
    DEFAULT_MANUAL_BOOST_MINUTES,
    DEFAULT_MANUAL_BOOST_OFFSET,
    DEFAULT_MIN_SWITCH_TIME,
    DEFAULT_PREHEAT_ENABLED,
    DEFAULT_ROOM_CALIBRATE,
    DEFAULT_ROOM_VALVE_CUT,
    DEFAULT_PREHEAT_HOLD_MINUTES,
    DEFAULT_PREHEAT_MAX_MINUTES,
    DEFAULT_GAS_ESTIMATE,
    DEFAULT_GAS_M3_PER_HOUR,
    DEFAULT_PREHEAT_RATE,
    DEFAULT_RESIDUAL_ALLOW,
    DEFAULT_RESIDUAL_COMP,
    DEFAULT_SUMMER_END,
    DEFAULT_SUMMER_START,
    DEFAULT_MAX_BOOST_ENABLED,
    DEFAULT_MAX_BOOST_HOURS,
    DEFAULT_MAX_BOOST_REST,
    DEFAULT_STALE_ENABLED,
    DEFAULT_STALE_HOURS,
    DEFAULT_SUMMER_TEMP,
    DEFAULT_TRV_LOG,
    DEFAULT_WINDOW_DELAY,
    DEFAULT_VALVE_BOOST_DELAY,
    DEFAULT_VALVE_BOOST_THRESHOLD,
    DEFAULT_VALVE_DRY_RUN,
    DEFAULT_VALVE_MAX_TEMP,
    DEFAULT_VALVE_RELEASE_MARGIN,
    DOMAIN,
    CUT_DROP,
    CUT_MAX_SECONDS,
    CUT_PAUSE_SECONDS,
    CUT_RELEASE_MARGIN,
    CUT_SETTLE_SECONDS,
    CUT_START_MARGIN,
    EVENT_DEBOUNCE_SECONDS,
    EVENT_TYPE,
    FALLBACK_MIN_RISE,
    FALLBACK_REST_SECONDS,
    FALLBACK_STALL_SECONDS,
    FROST_CONFIRM_SECONDS,
    FROST_HYSTERESIS,
    FROST_READING_MIN,
    FROST_TEMP_MAX,
    HEATING_RATE_MAX,
    GAS_M3_PER_HOUR_MAX,
    GAS_M3_PER_HOUR_MIN,
    GAS_MAX_GAP_SECONDS,
    GAS_SAVE_SECONDS,
    HEATING_RATE_KEEP,
    HEATING_RATE_MIN,
    HEATING_RATE_MIN_SAMPLES,
    HEATING_SESSION_MIN_RISE,
    HEATING_SESSION_MIN_SECONDS,
    HEATING_DROP_LOG_SECONDS,
    HEATING_SESSION_PAUSE_MAX,
    HEATING_SESSION_SAVE_SECONDS,
    HUMIDITY_FULL,
    HUMIDITY_MAX,
    HUMIDITY_MIN,
    HUMIDITY_START,
    LAST_TARGET_MAX,
    LAST_TARGET_MIN,
    MANUAL_BOOST_MAX_MINUTES,
    MANUAL_BOOST_MAX_OFFSET,
    MANUAL_BOOST_MIN_MINUTES,
    MANUAL_BOOST_MIN_OFFSET,
    MAX_EFFECTIVE_TARGET,
    MAX_RAISED_TARGET,
    MIN_BOOST_GAIN,
    PREHEAT_DONE_TOLERANCE,
    PREHEAT_GRACE_SECONDS,
    PREHEAT_SAFETY,
    RESIDUAL_ALLOW_MAX,
    RESIDUAL_BOILER_GRACE_EXTRA,
    RESIDUAL_BOILER_GRACE_SECONDS,
    RESIDUAL_FALL,
    RESIDUAL_KEEP,
    RESIDUAL_LEAD_MAX,
    RESIDUAL_LEAD_MIN,
    RESIDUAL_LEAD_STEP,
    RESIDUAL_MIN_ON_SECONDS,
    RESIDUAL_MIN_SAMPLES,
    RESIDUAL_MIN_WINDOW_SECONDS,
    RESIDUAL_PEAK_MAX_SECONDS,
    RESIDUAL_SAMPLE_MAX,
    RESIDUAL_SAMPLE_MAX_AGE,
    RESIDUAL_TARGET_TOLERANCE,
    RESIDUAL_WINDOW_SECONDS,
    RESTORE_RETRY_SECONDS,
    RESUME_WINDOW_SECONDS,
    SAMPLE_INTERVAL_SECONDS,
    SAMPLE_TEMP_MAX,
    SAMPLE_TEMP_MIN,
    SENSOR_HOLD_SECONDS,
    SENSOR_PATH_MAX,
    SENSOR_PATH_WINDOW,
    SENSOR_STEP_MIN,
    SENSOR_STUCK_SECONDS,
    SENSOR_TEMP_MAX,
    SENSOR_TEMP_MIN,
    STARTUP_SETTLE_SECONDS,
    STORAGE_VERSION,
    SUMMER_HYSTERESIS,
    TRV_OFFSET_MAX,
    VALVE_ERROR_LOG_SECONDS,
    VALVE_LOST_GRACE_SECONDS,
    VALVE_RETRY_STEPS,
    VALVE_TARGET_MAX,
    VALVE_TARGET_MIN,
    TREND_HYSTERESIS,
    TREND_MIN_SPAN_SECONDS,
    TREND_SAMPLE_SECONDS,
    TREND_WINDOW_SECONDS,
    parse_month_day,
)

from . import trvlog
from .calibration import Calibrator
from .offset import room_trv_offset, room_valve_offsets, trv_offset_from  # noqa: F401 - a trv_offset_from a külső használatra (tesztek) is elérhető
from .cycles import CycleLog

_LOGGER = logging.getLogger(__name__)

TICK = timedelta(seconds=60)
PREHEAT_LOOKAHEAD_SECONDS = 24 * 3600  # ennyire előre mutatjuk a következő előfűtést


class BoostError(Exception):
    """A "Fűts most" / előfűtés kérés nem teljesíthető; a `code` a fordítás kulcsa."""

    def __init__(self, code: str, **placeholders: Any) -> None:
        super().__init__(code)
        self.code = code
        self.placeholders = placeholders


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _parse_hhmm(value: Any) -> tuple[int, int] | None:
    """'HH:MM' (vagy 'HH:MM:SS') -> (óra, perc); érvénytelen esetén None."""
    if not isinstance(value, str):
        return None
    parts = value.strip().split(":")
    try:
        hour, minute = int(parts[0]), int(parts[1])
    except (IndexError, ValueError):
        return None
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return hour, minute


def clamp_valve_target(value: float, state: State | None = None) -> float:
    """A szelepnek küldhető célhőmérséklet: 6-34 °C, és a szelep saját min/max értékén belül."""
    lo, hi = VALVE_TARGET_MIN, VALVE_TARGET_MAX
    if state is not None:
        try:
            lo = max(lo, float(state.attributes["min_temp"]))
        except (KeyError, TypeError, ValueError):
            pass
        try:
            hi = min(hi, float(state.attributes["max_temp"]))
        except (KeyError, TypeError, ValueError):
            pass
    if hi < lo:  # értelmetlen szelep-határok: a kemény határokra esünk vissza
        lo, hi = VALVE_TARGET_MIN, VALVE_TARGET_MAX
    return min(max(float(value), lo), hi)


async def _service_call(
    hass: HomeAssistant,
    domain: str,
    entity_id: str,
    service: str,
    *,
    _warn: bool = True,
    **data: Any,
) -> bool:
    """Szolgáltatáshívás egy entitásra; a hibát (és az időtúllépést) jelzi, nem dobja tovább.

    Bármilyen hibát elfog, nem csak a HomeAssistantError-t: a Meross LAN 6.x a sikertelen parancsot
    saját kivétellel (MerossTransportError, az Exception leszármazottja) adja tovább - az 5.x még
    csendben figyelmen kívül hagyta -, a HA pedig blocking hívásnál a szolgáltatás kivételét
    változatlanul visszadobja. Ha ez kiszökne, a szelepek feldolgozása (ami a kazán kapcsolása ELŐTT
    van) megszakadna, és a kazán nem kapcsolna be vagy ki. A megszakítás (CancelledError) nem
    `Exception`, az továbbmegy, így a leállítás közben sem akad el semmi.
    """
    try:
        await hass.services.async_call(
            domain,
            service,
            {"entity_id": entity_id, **data},
            blocking=True,
        )
    except Exception as err:  # noqa: BLE001 - lásd fent: a parancs hibája nem állíthatja le a vezérlést
        # a hiba fajtáját is kiírjuk: a Meross LAN kivételeinek gyakran üres a szövege
        detail = f"{type(err).__name__}: {err}" if str(err) else type(err).__name__
        if _warn:
            _LOGGER.warning("%s.%s hiba a(z) %s-en: %s", domain, service, entity_id, detail)
        else:
            _LOGGER.debug("%s.%s hiba a(z) %s-en: %s", domain, service, entity_id, detail)
        return False
    return True


async def _climate_call(
    hass: HomeAssistant,
    entity_id: str,
    service: str,
    *,
    _warn: bool = True,
    **data: Any,
) -> bool:
    return await _service_call(hass, "climate", entity_id, service, _warn=_warn, **data)


def _as_dict(value: Any) -> dict[str, Any]:
    """A tárolt adat dict-je; bármi más (sérült fájl) esetén üres."""
    return value if isinstance(value, dict) else {}


def _finite(value: Any) -> float | None:
    """Szám (véges) vagy None; a tárolt adatok ellenőrzéséhez."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _median(values: list[float]) -> float:
    """Medián (páros darabszámnál a két középső átlaga); az outlierekre érzéketlen."""
    ordered = sorted(values)
    mid = len(ordered) // 2
    return ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2


# 2.19.1: a fűtési alkalom vége és az elvetés oka (a TRV-naplóhoz; az attribútumokban a kódok szerepelnek)
_RATE_ENDED_HU = {
    "target": "a szoba elérte a célját",
    "pause": f"a hőleadás {HEATING_SESSION_PAUSE_MAX // 60} percnél tovább szünetelt (a szelep elzárt, a kazán állt vagy nem jött mérés), "
    "a mérés a szünet kezdetéig tart",
    "restart": "az újraindítás előtti utolsó fűtésig mérve",
    "interrupted": "megszakadt",
}
_RATE_DROP_HU = {
    "short": f"{HEATING_SESSION_MIN_SECONDS // 60} percnél rövidebb fűtés",
    "small_rise": f"{HEATING_SESSION_MIN_RISE:g} °C-nál kisebb emelkedés".replace(".", ","),
    "window": "kinyílt az ablak",
    "sensor": "a szoba hőmérő megbízhatatlan vagy elakadt",
    "valves_unreachable": "a szelepek nem elérhetők",
    "frost": "fagyvédelem",
}


def _load_rate_last(raw: Any, now_ts: float) -> dict[str, Any] | None:
    """A mentett utolsó minta ellenőrzése (2.19.1); hibás vagy hiányos rekordnál None."""
    if not isinstance(raw, dict) or raw.get("ended") not in _RATE_ENDED_HU:
        return None
    ts, rate, minutes, rise = (_finite(raw.get(k)) for k in ("ts", "rate", "minutes", "rise"))
    if ts is None or rate is None or minutes is None or rise is None:
        return None
    if not (0 < ts <= now_ts + 60 and HEATING_RATE_MIN <= rate <= HEATING_RATE_MAX and 0 <= minutes <= 7 * 24 * 60):
        return None
    pauses = _finite(raw.get("pauses"))
    return {
        "ts": ts,
        "rate": round(rate, 3),
        "minutes": int(minutes),
        "rise": round(rise, 2),
        "ended": raw["ended"],
        "pauses": int(pauses) if pauses is not None and 0 <= pauses <= 1000 else 0,
    }


def _load_rate_drop(raw: Any, now_ts: float) -> dict[str, Any] | None:
    """A mentett utolsó elvetett alkalom ellenőrzése (2.19.1); hibás vagy hiányos rekordnál None."""
    if not isinstance(raw, dict) or raw.get("reason") not in _RATE_DROP_HU or raw.get("ended") not in _RATE_ENDED_HU:
        return None
    ts, minutes, rise = (_finite(raw.get(k)) for k in ("ts", "minutes", "rise"))
    if ts is None or minutes is None or rise is None or not (0 < ts <= now_ts + 60 and 0 <= minutes <= 7 * 24 * 60):
        return None
    return {"ts": ts, "reason": raw["reason"], "ended": raw["ended"], "minutes": int(minutes), "rise": round(rise, 2)}


def _load_rate_run(raw: Any, now_ts: float) -> dict[str, Any] | None:
    """A mentett futó alkalom ellenőrzése (2.19.1); hibás, jövőbeli vagy egy napnál régebbi rekordnál None."""
    if not isinstance(raw, dict):
        return None
    t0, temp0, t_heat, temp_heat = (_finite(raw.get(k)) for k in ("t0", "temp0", "t_heat", "temp_heat"))
    if t0 is None or temp0 is None or t_heat is None or temp_heat is None:
        return None
    if not (now_ts - 86400 <= t0 <= t_heat <= now_ts + 60):
        return None
    if not (SENSOR_TEMP_MIN <= temp0 <= SENSOR_TEMP_MAX and SENSOR_TEMP_MIN <= temp_heat <= SENSOR_TEMP_MAX):
        return None
    pauses = _finite(raw.get("pauses"))
    return {
        "t0": t0,
        "temp0": temp0,
        "t_heat": t_heat,
        "temp_heat": temp_heat,
        "pauses": int(pauses) if pauses is not None and 0 <= pauses <= 1000 else 0,
    }


async def _async_restore_valve(
    hass: HomeAssistant,
    valve_id: str,
    state: State,
    rec: dict[str, Any],
    _warn: bool = True,
) -> bool:
    """Visszaállítja a szelep eredeti célját (vagy az eredeti presetet, ha az változott)."""
    preset = state.attributes.get("preset_mode")
    presets = state.attributes.get("preset_modes") or []
    original_preset = rec.get("preset")
    if original_preset and preset != original_preset and original_preset in presets:
        return await _climate_call(
            hass,
            valve_id,
            "set_preset_mode",
            preset_mode=original_preset,
            _warn=_warn,
        )
    return await _climate_call(
        hass,
        valve_id,
        "set_temperature",
        temperature=clamp_valve_target(rec["original"], state),
        _warn=_warn,
    )


async def async_restore_on_remove(hass: HomeAssistant, entry_id: str) -> None:
    """Az integráció törlésekor visszaállítja az összes még emelt szelepet."""
    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry_id}")
    data = await store.async_load()
    # 2.19: a szelep-zárások (lejjebb állított célok) ugyanígy visszaállnak
    for key, value_key in (("boosts", "boost"), ("cuts", "cut")):
        records = data.get(key) if isinstance(data, dict) else None
        for valve_id, rec in (records if isinstance(records, dict) else {}).items():
            state = hass.states.get(valve_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            try:
                raw = float(state.attributes["temperature"])
                if abs(raw - float(rec[value_key])) > BOOST_TOLERANCE:
                    continue  # időközben máshol módosították
                await _async_restore_valve(
                    hass,
                    valve_id,
                    state,
                    {"original": float(rec["original"]), "preset": rec.get("preset")},
                )
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
    # 2.19: a kalibráció-számok is visszakapják az eredeti értéküket (különben a plugin eltolása a szelepben maradna)
    try:
        from .calibration import async_restore_numbers_on_remove  # noqa: PLC0415

        await async_restore_numbers_on_remove(hass, data.get("calibration") if isinstance(data, dict) else None)
    except Exception as err:  # noqa: BLE001 - a törlés nem akadhat el ezen
        _LOGGER.warning("A szelepek kalibrációjának visszaállítása nem sikerült: %s", err)


@dataclass
class RoomStatus:
    """Egy szoba aktuális állapota (a szenzorok ezt mutatják)."""

    room_id: str
    name: str
    valves: list[str]
    reachable: bool = False
    active: bool = False
    calling: bool = False
    current: float | None = None
    source: str | None = None
    target: float | None = None
    effective_target: float | None = None
    humidity: float | None = None
    humidity_boost: float = 0.0
    valve_control: bool = False
    boosted: bool = False
    deviation: float | None = None  # cél - aktuális (pozitív: hideg van)
    boost_wanted: bool = False
    cold_since: float | None = None
    # szobánkénti (vagy az általánosból örökölt) szelep paraméterek
    boost_threshold: float = DEFAULT_VALVE_BOOST_THRESHOLD
    boost_delay_s: float = DEFAULT_VALVE_BOOST_DELAY * 60
    release_margin: float = DEFAULT_VALVE_RELEASE_MARGIN
    # kazán hőigény a szelep állapotához kötve
    valve_demand_link: bool = False
    valve_open: bool = False
    boiler_demand: bool = False
    # biztonsági funkciók
    sensor_stale: bool = False
    temp_sensor: str | None = None
    # 2.11.1: a szoba hőmérő hihetősége (képtelen vagy ugráló érték nem vezérel)
    sensor_bad: str | None = None  # None (rendben) | "range" | "jump"
    sv_hist: list[tuple[float, float]] = field(default_factory=list)  # (jelentés ideje, érték) az utolsó percekből
    sv_seen: float = 0.0  # az utoljára vizsgált jelentés ideje
    sv_until: float = 0.0  # eddig nem bízunk a szenzorban
    sv_reason: str | None = None
    boost_started: float | None = None
    rest_until: float | None = None
    # ablakérzékelők
    window_sensors: list[str] = field(default_factory=list)
    window_delay_s: float = DEFAULT_WINDOW_DELAY * 60
    window_open_since: float | None = None
    window_open: bool = False  # a késleltetés letelt: a szoba szünetel
    # 2.11: a szelepek hőmérőjének automata kalibrációja
    calibrate: bool = True  # a szoba részt vesz-e (a globális kapcsoló mellett)
    # 2.12: a kalibrált szelep mérése a szoba hőmérőjéhez képest (0 = ne legyen eltolás). 2.17: előjeles, a Meross LAN
    # kalibráció számával azonos előjellel: a plusz melegebbet, a mínusz hidegebbet mutat a szelep (alapérték: -1 °C)
    trv_offset: float = 0.0
    # 2.18: a szelepek egyedi eltolása (előjeles, mint a `trv_offset`); csak a megadott szelepek szerepelnek benne, a többi a
    # szoba eltolását használja (`offset_for`)
    valve_offsets: dict[str, float] = field(default_factory=dict)
    calibration: list[dict[str, Any]] = field(default_factory=list)  # szelepenkénti állapot
    # hőmérséklet trend (°C/óra), csak a kártyák kijelzéséhez
    trend: float | None = None
    trend_source: str | None = None
    trend_samples: deque[tuple[float, float]] = field(default_factory=deque)
    # 2.9: "Fűts most" (megemelt cél)
    manual_until: float | None = None
    manual_offset: float = 0.0
    manual_started: float | None = None
    # 2.9: előfűtés
    preheat_status: str | None = None  # scheduled | heating | ready | unreachable
    preheat_active: bool = False
    preheat_start_at: float | None = None
    preheat_ready_by: float | None = None
    preheat_target: float | None = None
    preheat_source: str | None = None  # schedule | service
    preheat_req: dict[str, Any] | None = None  # egyszeri (szolgáltatás) kérés
    preheat_latch: dict[str, Any] | None = None  # az éppen futó terv
    preheat_skip: float | None = None  # az eddig kihagyott menetrendi időpontok (epoch)
    # tanult felfűtési sebesség (°C/óra). 2.19: fűtési alkalmanként egy minta, a tanult érték az utolsó alkalmak mediánja;
    # a `heating_samples` az alkalmak száma (korábban percenkénti minták száma volt)
    heating_rate: float | None = None
    heating_samples: int = 0
    rate_samples: list[float] = field(default_factory=list)
    # a futó fűtési alkalom (2.19.1: kezdete, az utolsó hőleadás közbeni mérés, a szünetek száma; újraindítás után folytatható)
    rate_run: dict[str, Any] | None = None
    rate_last: dict[str, Any] | None = None  # 2.19.1: az utolsó minta (idő, sebesség, perc, emelkedés, hogyan ért véget)
    rate_drop: dict[str, Any] | None = None  # 2.19.1: az utolsó, mintának nem számító alkalom (idő, ok, vége, perc, emelkedés)
    rate_drop_logged: dict[str, float] = field(default_factory=dict)  # elvetési ok -> mikor került utoljára a TRV-naplóba
    # 2.13: tanult maradékhő (a hőigény megszűnése utáni további melegedés, °C)
    resid_samples: list[float] = field(default_factory=list)  # az utolsó érvényes mérések
    resid_times: list[float] = field(default_factory=list)  # 2.19: a mérések ideje (epoch), a `resid_samples` párja (elévülés)
    resid_run: dict[str, Any] | None = None  # a futó megfigyelés (a leállás utáni csúcs keresése)
    call_since: float | None = None  # a mostani hőigény kezdete (epoch)
    call_target: float | None = None  # a szelepek célja a hőigény kezdetekor
    call_clean: bool = False  # a hőigény alatt nem volt zavaró körülmény (ablak, kézi fűtés, ...)
    stop_lead: float = 0.0  # ennyivel előbb áll le a hőigény a tanult maradékhő miatt (°C)
    # 2.19: kiesés-kezelés (a szoba szelepei nem elérhetők) és fagyvédelem
    last_target: float | None = None  # a szelepeken utoljára látott cél (mentve): elérhetetlen szelepnél ezzel megy tovább
    lost_since: float | None = None  # mióta nem érhető el a szoba egyik szelepe sem
    fallback: bool = False  # a hőigény most a szoba hőmérőjéből és az utolsó ismert célból jön
    fb_since: float | None = None  # a tartalék vezérlés megfigyelési ablakának kezdete (melegszik-e a szoba?)
    fb_temp: float | None = None  # a szoba hőmérséklete az ablak kezdetén
    fb_rest_until: float = 0.0  # eddig szünetel a tartalék vezérlés hőigénye (a szoba nem melegedett)
    fallback_paused: bool = False  # a tartalék vezérlés hőigénye most szünetel
    frost: bool = False  # fagyvédelem: a szoba a szelep állapotától függetlenül hőt kér
    frost_since: float | None = None  # mióta van a mérés a fagyküszöb alatt (megerősítés)
    # 2.19: elakadt szoba hőmérő (fűtés közben nem jelent): a szelepek mérésére váltunk, amíg újra nem jelent
    sensor_stuck: bool = False
    stuck_ref: float = 0.0  # a hőmérő utolsó jelentésének ideje, amikor elakadtnak találtuk
    # 2.19: szobánkénti páratartalom-emelés (a szobában megadott érték, ennek hiányában az általános)
    humidity_max_boost: float = DEFAULT_HUMIDITY_MAX_BOOST
    # 2.19: szelep-zárás túlfűtés ellen (a szelep-emelés tükörképe), szobánként kapcsolható
    valve_cut: bool = False
    cut_since: float | None = None  # a mostani zárás kezdete
    cut_pause_until: float = 0.0  # eddig nem zár újra (visszaállítás után a szelep jelentse a valódi célját)
    cut_reason: str | None = None  # over (a cél fölött) | window (nyitott ablak)
    cut_active: bool = False  # legalább egy szelep célja most le van engedve

    @property
    def trv_bias(self) -> float:
        """2.17: a szoba eltolásának belső alakja: ennyivel mutasson HIDEGEBBET a szelep a szoba hőmérőjénél (szoba hőmérője -
        szelep mérése). A felhasználónak látszó `trv_offset` ellentettje (a plusz eltolás melegebbet jelent). 2.18-tól a
        kalibráció szelepenként számol (`bias_for`); ez a szoba alapértéke."""
        return 0.0 - self.trv_offset

    def offset_for(self, valve_id: str) -> float:
        """2.18: a szelep TRV eltolása (°C, előjeles): az egyedi érték, ennek hiányában a szoba eltolása. Egy szelepes
        szobában, vagy ha nincs egyedi érték, megegyezik a `trv_offset` értékével."""
        value = self.valve_offsets.get(valve_id)
        return self.trv_offset if value is None else value

    def bias_for(self, valve_id: str) -> float:
        """2.18: a szelep eltolásának belső alakja (a `trv_bias` szelepenkénti megfelelője): a kalibráció ezzel számol."""
        return 0.0 - self.offset_for(valve_id)

    @property
    def sensor_unusable(self) -> bool:
        """A szoba hőmérője most nem használható: elavult, elakadt, vagy képtelen / ugráló értéket ad."""
        return self.sensor_stale or self.sensor_stuck or self.sensor_bad is not None

    @property
    def residual(self) -> float | None:
        """A tanult maradékhő (°C): az utolsó mérések mediánja, elég mérés esetén."""
        if len(self.resid_samples) < RESIDUAL_MIN_SAMPLES:
            return None
        return round(_median(self.resid_samples), 2)


def _slope_per_hour(samples: deque[tuple[float, float]]) -> float | None:
    """Legkisebb négyzetes egyenes meredeksége °C/órában; kevés / rövid mintából None."""
    if len(samples) < 3:
        return None
    t0 = samples[0][0]
    if samples[-1][0] - t0 < TREND_MIN_SPAN_SECONDS:
        return None
    xs = [ts - t0 for ts, _ in samples]
    ys = [val for _, val in samples]
    n = len(samples)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    den = sum((x - mean_x) ** 2 for x in xs)
    if den <= 0:
        return None
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    return round(num / den * 3600, 2) + 0.0  # + 0.0: a "-0.0" ne jelenjen meg


def _stable_trend(prev: float | None, raw: float | None) -> float | None:
    """A kiadott trend: 0,1-re kerekítve, és csak ≥ 0,2 °C/óra változásnál frissül.

    Így az attribútum nem változik minden percben, és nem terheli feleslegesen
    az állapot-előzményeket.
    """
    if raw is None:
        return None
    val = round(raw, 1) + 0.0
    if prev is None or abs(val - prev) >= TREND_HYSTERESIS - 1e-9:
        return val
    return prev


class BoilerController:
    """Összeköti a szobákat és a kazán termosztátot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        cfg: dict[str, Any] = {**entry.data, **entry.options}
        self.hass = hass
        self.entry_id = entry.entry_id
        self.boiler: str = cfg[CONF_BOILER]
        self.rooms: list[dict[str, Any]] = list(cfg.get(CONF_ROOMS, []))

        self.hysteresis = float(cfg.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))
        self.min_switch = timedelta(
            minutes=float(cfg.get(CONF_MIN_SWITCH_TIME, DEFAULT_MIN_SWITCH_TIME))
        )
        self.on_temp = float(cfg.get(CONF_BOILER_ON_TEMP, DEFAULT_BOILER_ON_TEMP))
        self.humidity_max_boost = float(
            cfg.get(CONF_HUMIDITY_MAX_BOOST, DEFAULT_HUMIDITY_MAX_BOOST)
        )

        self.valve_dry_run = bool(cfg.get(CONF_VALVE_DRY_RUN, DEFAULT_VALVE_DRY_RUN))
        self.valve_boost_threshold = float(
            cfg.get(CONF_VALVE_BOOST_THRESHOLD, DEFAULT_VALVE_BOOST_THRESHOLD)
        )
        self.valve_boost_delay = (
            float(cfg.get(CONF_VALVE_BOOST_DELAY, DEFAULT_VALVE_BOOST_DELAY)) * 60
        )
        release = float(cfg.get(CONF_VALVE_RELEASE_MARGIN, DEFAULT_VALVE_RELEASE_MARGIN))
        self._release_raw = release
        if release >= self.valve_boost_threshold:  # különben azonnal újraindulna
            release = round(max(self.valve_boost_threshold - 0.1, 0.0), 2)
        self.valve_release_margin = release

        # biztonsági funkciók (ki/be és értékek állíthatók)
        stale_hours = float(cfg.get(CONF_STALE_HOURS, DEFAULT_STALE_HOURS))
        self.stale_enabled = (
            bool(cfg.get(CONF_STALE_ENABLED, DEFAULT_STALE_ENABLED)) and stale_hours > 0
        )
        self.stale_seconds = stale_hours * 3600
        self.max_boost_enabled = bool(
            cfg.get(CONF_MAX_BOOST_ENABLED, DEFAULT_MAX_BOOST_ENABLED)
        )
        self.max_boost_seconds = (
            float(cfg.get(CONF_MAX_BOOST_HOURS, DEFAULT_MAX_BOOST_HOURS)) * 3600
        )
        self.max_boost_rest_seconds = (
            float(cfg.get(CONF_MAX_BOOST_REST, DEFAULT_MAX_BOOST_REST)) * 60
        )
        self.window_delay_s = float(cfg.get(CONF_WINDOW_DELAY, DEFAULT_WINDOW_DELAY)) * 60
        # 2.19: fagyvédelem (0 = kikapcsolva)
        self.frost_temp = _clamp(float(cfg.get(CONF_FROST_TEMP, DEFAULT_FROST_TEMP)), 0.0, FROST_TEMP_MAX)
        self.outdoor_stale = False
        self._outdoor_warned = 0.0  # a képtelen kinti érték utolsó naplózása (óránként egyszer)
        self._issue_state: dict[str, bool] = {}

        # 2.8: események, kazán-ciklusok, védelem (mind külön kapcsolható)
        self.events_enabled = bool(cfg.get(CONF_EVENTS_ENABLED, DEFAULT_EVENTS_ENABLED))
        # 2.14: TRV-napló: az automatika döntései külön naplócsatornán (kikapcsolva csak DEBUG szinten)
        self.trv_log = bool(cfg.get(CONF_TRV_LOG, DEFAULT_TRV_LOG))
        self.cycle_monitor = bool(cfg.get(CONF_CYCLE_MONITOR, DEFAULT_CYCLE_MONITOR))
        self.cycle_max_starts = float(cfg.get(CONF_CYCLE_MAX_STARTS, DEFAULT_CYCLE_MAX_STARTS))
        self.cycle_min_avg_on = float(cfg.get(CONF_CYCLE_MIN_AVG_ON, DEFAULT_CYCLE_MIN_AVG_ON))
        self.cycle_protection = bool(cfg.get(CONF_CYCLE_PROTECTION, DEFAULT_CYCLE_PROTECTION))
        self.boiler_min_on = timedelta(
            minutes=float(cfg.get(CONF_BOILER_MIN_ON, DEFAULT_BOILER_MIN_ON))
        )
        self.boiler_min_off = timedelta(
            minutes=float(cfg.get(CONF_BOILER_MIN_OFF, DEFAULT_BOILER_MIN_OFF))
        )
        # 2.9: "Fűts most" és előfűtés (külön kapcsolhatók)
        self.manual_boost_enabled = bool(
            cfg.get(CONF_MANUAL_BOOST_ENABLED, DEFAULT_MANUAL_BOOST_ENABLED)
        )
        self.manual_boost_minutes = _clamp(
            float(cfg.get(CONF_MANUAL_BOOST_MINUTES, DEFAULT_MANUAL_BOOST_MINUTES)),
            MANUAL_BOOST_MIN_MINUTES,
            MANUAL_BOOST_MAX_MINUTES,
        )
        self.manual_boost_end_on_target = bool(
            cfg.get(CONF_MANUAL_BOOST_END_ON_TARGET, DEFAULT_MANUAL_BOOST_END_ON_TARGET)
        )
        self.manual_boost_offset = _clamp(
            float(cfg.get(CONF_MANUAL_BOOST_OFFSET, DEFAULT_MANUAL_BOOST_OFFSET)),
            MANUAL_BOOST_MIN_OFFSET,
            MANUAL_BOOST_MAX_OFFSET,
        )
        self.preheat_enabled = bool(cfg.get(CONF_PREHEAT_ENABLED, DEFAULT_PREHEAT_ENABLED))
        self.preheat_max_s = (
            float(cfg.get(CONF_PREHEAT_MAX_MINUTES, DEFAULT_PREHEAT_MAX_MINUTES)) * 60
        )
        self.preheat_hold_s = (
            float(cfg.get(CONF_PREHEAT_HOLD_MINUTES, DEFAULT_PREHEAT_HOLD_MINUTES)) * 60
        )
        self.preheat_default_rate = max(
            float(cfg.get(CONF_PREHEAT_DEFAULT_RATE, DEFAULT_PREHEAT_RATE)), HEATING_RATE_MIN
        )
        # 2.10: becsült gázfogyasztás (a kazán bekapcsolt ideje × m³/óra), az Energia fülhöz
        self.gas_enabled = bool(cfg.get(CONF_GAS_ESTIMATE, DEFAULT_GAS_ESTIMATE))
        self.gas_m3_per_hour = _clamp(
            float(cfg.get(CONF_GAS_M3_PER_HOUR, DEFAULT_GAS_M3_PER_HOUR)),
            GAS_M3_PER_HOUR_MIN,
            GAS_M3_PER_HOUR_MAX,
        )
        self.gas_m3 = 0.0  # a kezdet óta halmozott becsült fogyasztás (m³), újraindítás után is megmarad
        self._gas_last_ts: float | None = None  # az utolsó elszámolás ideje
        self._gas_last_on: bool | None = None  # a kazán állapota az utolsó elszámoláskor
        self._gas_saved_ts = 0.0
        # 2.11: a szelepek hőmérőjének automata kalibrációja (alapból kikapcsolt; a kazán termosztátot nem érinti)
        self.cal_enabled = bool(cfg.get(CONF_CALIBRATION_ENABLED, DEFAULT_CALIBRATION_ENABLED))
        self.cal_dry_run = bool(cfg.get(CONF_CALIBRATION_DRY_RUN, DEFAULT_CALIBRATION_DRY_RUN))
        # 2.13: maradékhő: a tanulás mindig fut, a kompenzáció (korábbi leállítás) kapcsolható
        self.residual_comp = bool(cfg.get(CONF_RESIDUAL_COMP, DEFAULT_RESIDUAL_COMP))
        self.residual_allow = _clamp(
            float(cfg.get(CONF_RESIDUAL_ALLOW, DEFAULT_RESIDUAL_ALLOW)), 0.0, RESIDUAL_ALLOW_MAX
        )
        self.cycles = CycleLog()
        self.cycle_info: dict[str, Any] = self.cycles.stats(0)
        self.short_cycling = False
        self._events_armed = False  # az első kiértékelés alatt nem küldünk eseményt
        self._entity_ids: dict[str, str | None] = {}

        self.outdoor_sensor: str | None = cfg.get(CONF_OUTDOOR_SENSOR) or None
        self.summer_temp = float(cfg.get(CONF_SUMMER_TEMP, DEFAULT_SUMMER_TEMP))
        self.summer_start = parse_month_day(
            cfg.get(CONF_SUMMER_START, DEFAULT_SUMMER_START)
        ) or parse_month_day(DEFAULT_SUMMER_START)
        self.summer_end = parse_month_day(
            cfg.get(CONF_SUMMER_END, DEFAULT_SUMMER_END)
        ) or parse_month_day(DEFAULT_SUMMER_END)

        # nyári mód állapot
        self.summer_active = False
        self.in_summer_period = False
        self.outdoor_now: float | None = None
        self.outdoor_avg: float | None = None
        self._samples: deque[tuple[float, float]] = deque()
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")

        self.status: dict[str, RoomStatus] = {
            room[CONF_ROOM_ID]: self._build_status(room) for room in self.rooms
        }
        self.calibrator = Calibrator(self)

        self._last_switch = None
        self._prev_summer = False
        # 2.19: a kazánnak küldött parancsok követése: egymás utáni sikertelen / nem követett parancsok száma, az utolsó
        # (sikeresen elküldött, de még nem igazolt) kapcsolás iránya és ideje, és meddig nem küldünk újabb parancsot
        self._boiler_fail = 0
        self._boiler_try: tuple[bool, float] | None = None
        self._boiler_block_until = 0.0
        # 2.19: mióta nem értékelhető egyetlen szoba sem (nincs elérhető szelep, és hőmérő + utolsó ismert cél sincs)
        self._blind_since: float | None = None
        # 2.19: a szoba hőmérő eszközének többi entitása (az "eszköz él" jelzéshez, lásd `_companion_alive`), hőmérőnként egyszer
        self._companion: dict[str, list[str]] = {}
        # szelep emelések: valve_id -> {original, boost, preset, ts, restoring}
        self._boosts: dict[str, dict[str, Any]] = {}
        # 2.19: szelep-zárások: valve_id -> {original, cut, preset, ts, restoring, via, reason}
        self._cuts: dict[str, dict[str, Any]] = {}
        self._dry_cut: set[str] = set()
        # szelep -> {"n": egymás utáni hibák, "until": eddig nem próbálkozunk újra (epoch)}
        self._cmd_fail: dict[str, dict[str, float]] = {}
        # szelepenként: mikor naplóztunk utoljára váratlan hibát (hogy ne ismétlődjön percenként)
        self._valve_err_logged: dict[str, float] = {}
        # mikor figyelmeztettünk utoljára, hogy a kazán termosztátja nem fűtő módban van
        self._mode_warned: float = 0.0
        self._dry: set[str] = set()
        self._unsubs: list[Callable[[], None]] = []
        self._retry_unsub: Callable[[], None] | None = None
        self._listeners: list[Callable[[], None]] = []
        self._lock = asyncio.Lock()
        # 2.19: a legkorábbi függő késleltetett mentés határideje (egyenletes órán), lásd `_delay_save`
        self._save_due: float | None = None
        # 2.19: az állapotváltozások összevont kiértékelése: a függő időzítő, és hogy vár-e már kör a zárra
        self._eval_unsub: Callable[[], None] | None = None
        self._eval_queued = False

        # --- újraindítás-biztonság (2.11)
        # Leállított vezérlő már nem értékel és nem ír (újratöltéskor a régi példány ne zavarjon).
        self._stopped = False
        # Ha a HA még indul, a vezérlő addig csak olvas, utána rövid ideig még várja, hogy az
        # entitások (Meross LAN, szenzorok) feltöltődjenek. Újratöltésnél (futó HA) nincs várakozás.
        self._boot_hold = not getattr(hass, "is_running", True)
        self._ready_since: float | None = None
        self._start_ts = dt_util.utcnow().timestamp()
        # azok a szobák, amelyek hiszterézis-állapotát már a kazán állapotából vettük fel
        self._seeded: set[str] = set()

    def _build_status(self, room: dict[str, Any]) -> RoomStatus:
        """Szoba státusz; a szelep paraméterek a szobából, ennek hiányában az általánosból."""

        def opt(key: str, default: float) -> float:
            value = room.get(key)
            return default if value is None else float(value)

        threshold = opt(CONF_VALVE_BOOST_THRESHOLD, self.valve_boost_threshold)
        delay_min = opt(CONF_VALVE_BOOST_DELAY, self.valve_boost_delay / 60)
        release = opt(CONF_VALVE_RELEASE_MARGIN, self._release_raw)
        if release >= threshold:  # különben azonnal újraindulna
            release = round(max(threshold - 0.1, 0.0), 2)
        return RoomStatus(
            room_id=room[CONF_ROOM_ID],
            name=room[CONF_ROOM_NAME],
            valves=list(room[CONF_ROOM_VALVES]),
            temp_sensor=room.get(CONF_ROOM_TEMP) or None,
            valve_control=bool(room.get(CONF_ROOM_VALVE_CONTROL))
            and bool(room.get(CONF_ROOM_TEMP)),
            boost_threshold=threshold,
            boost_delay_s=delay_min * 60,
            release_margin=release,
            valve_demand_link=bool(room.get(CONF_ROOM_VALVE_LINK)),
            window_sensors=list(room.get(CONF_ROOM_WINDOWS) or []),
            window_delay_s=opt(CONF_WINDOW_DELAY, self.window_delay_s / 60) * 60,
            calibrate=bool(room.get(CONF_ROOM_CALIBRATE, DEFAULT_ROOM_CALIBRATE)),
            trv_offset=room_trv_offset(room),
            valve_offsets=room_valve_offsets(room),
            humidity_max_boost=_clamp(opt(CONF_HUMIDITY_MAX_BOOST, self.humidity_max_boost), 0.0, 5.0),
            valve_cut=bool(room.get(CONF_ROOM_VALVE_CUT, DEFAULT_ROOM_VALVE_CUT)),
        )

    # ------------------------------------------------------------------ életciklus
    async def async_load(self) -> None:
        """A mentett állapot visszatöltése újraindítás / újratöltés után.

        Minden értéket ellenőrzünk: a hibás, tartományon kívüli vagy a jövőbe mutató adat kimarad,
        így egy sérült vagy régi fájl nem állíthatja el a vezérlést.
        """
        data = await self._store.async_load()
        if not isinstance(data, dict):
            return
        now_ts = dt_util.utcnow().timestamp()

        samples: list[tuple[float, float]] = []
        raw_samples = data.get("samples")
        for item in raw_samples if isinstance(raw_samples, list) else []:
            try:
                ts, value = _finite(item[0]), _finite(item[1])
            except (TypeError, IndexError, KeyError):
                continue
            if ts is None or value is None:
                continue
            if ts > now_ts + 300 or not SAMPLE_TEMP_MIN <= value <= SAMPLE_TEMP_MAX:
                continue  # a jövőből jövő vagy értelmetlen minta
            samples.append((ts, value))
        samples.sort()
        self._samples = deque(samples)

        self.cycles.load(data.get("cycles"))
        gas = data.get("gas")
        m3 = _finite(gas.get("m3")) if isinstance(gas, dict) else None
        self.gas_m3 = max(0.0, m3) if m3 is not None else 0.0

        raw_boosts = data.get("boosts")
        for valve_id, rec in raw_boosts.items() if isinstance(raw_boosts, dict) else ():
            if not isinstance(rec, dict):
                continue
            original, boost = _finite(rec.get("original")), _finite(rec.get("boost"))
            if original is None or boost is None:
                continue
            if not (0.0 <= original <= 45.0 and 0.0 <= boost <= 45.0):
                continue  # értelmetlen célhőmérséklet: nem állítjuk vissza
            ts = _finite(rec.get("ts")) or 0.0
            self._boosts[valve_id] = {
                "original": original,
                "boost": boost,
                "preset": rec.get("preset") if isinstance(rec.get("preset"), str) else None,
                "ts": min(ts, now_ts),
                "restoring": bool(rec.get("restoring", False)),
            }
        raw_cuts = data.get("cuts")
        for valve_id, rec in raw_cuts.items() if isinstance(raw_cuts, dict) else ():
            if not isinstance(rec, dict):
                continue
            original, cut = _finite(rec.get("original")), _finite(rec.get("cut"))
            if original is None or cut is None:
                continue
            if not (0.0 <= original <= 45.0 and 0.0 <= cut <= 45.0):
                continue  # értelmetlen célhőmérséklet: nem állítjuk vissza
            ts = _finite(rec.get("ts")) or 0.0
            self._cuts[valve_id] = {
                "original": original,
                "cut": cut,
                "preset": rec.get("preset") if isinstance(rec.get("preset"), str) else None,
                "ts": min(ts, now_ts),
                "restoring": bool(rec.get("restoring", False)),
                "via": rec.get("via") if rec.get("via") in ("preset", "temp") else None,
                "reason": rec.get("reason") if rec.get("reason") in ("over", "window") else "over",
            }
        # 2.19: a szobák utolsó ismert célja (ha a szelepek indulás után sem érhetők el, ezzel megy tovább a fűtés)
        for room_id, value in _as_dict(data.get("targets")).items():
            st = self.status.get(room_id)
            target = _finite(value)
            if st is not None and target is not None and LAST_TARGET_MIN <= target <= LAST_TARGET_MAX:
                st.last_target = target
        self._load_2_9(data)
        self._load_residual(data)
        cal_valves = {valve for st in self.status.values() for valve in st.valves}
        self.calibrator.load(data.get("calibration"), cal_valves, now_ts)
        # a "kihűlt a radiátor" számlálók csak rövid leállást (újratöltést) élnek túl
        self.calibrator.load_idle(data.get("cal_idle"), cal_valves, now_ts)

        # nyári mód: a hiszterézis állapota megmarad (különben az átlag a két küszöb között
        # újraindítás után fűtési üzemre váltana)
        summer = data.get("summer")
        if self.outdoor_sensor and isinstance(summer, dict) and summer.get("active") is True:
            self.summer_active = True
        self._prev_summer = self.summer_active

        # a maximális emelés utáni pihenő nem szűnhet meg egy újraindítástól
        rest = data.get("rest")
        for room_id, until in rest.items() if isinstance(rest, dict) else ():
            st = self.status.get(room_id)
            value = _finite(until)
            if st is not None and value is not None and value > now_ts:
                st.rest_until = min(value, now_ts + self.max_boost_rest_seconds + 60)

        # újraindítás előtt még emelt szobák: ne engedjük el és emeljük újra feleslegesen
        for st in self.status.values():
            live = [
                self._boosts[v]["ts"]
                for v in st.valves
                if v in self._boosts and not self._boosts[v]["restoring"]
            ]
            if live:
                st.boost_wanted = True
                st.boost_started = min(live)  # a maximális idő az eredeti kezdettől számít

    def _load_2_9(self, data: dict[str, Any]) -> None:
        """A "Fűts most", az előfűtés és a tanult felfűtési sebesség visszatöltése."""
        now_ts = dt_util.utcnow().timestamp()
        for room_id, rec in _as_dict(data.get("rates")).items():
            st = self.status.get(room_id)
            if st is None or not isinstance(rec, dict):
                continue
            # 2.19: csak a fűtési alkalmankénti minták ("s") számítanak. A korábbi verziók egyetlen száma (a 30 perces trend
            # mozgóátlaga) torzított volt (a gyorsan melegedő szobára kisebb értéket adott), ezért nem vesszük át.
            raw = rec.get("s")
            samples = [
                round(value, 3)
                for value in (_finite(item) for item in (raw if isinstance(raw, list) else []))
                if value is not None and HEATING_RATE_MIN <= value <= HEATING_RATE_MAX
            ][-HEATING_RATE_KEEP:]
            if samples:
                st.rate_samples = samples
                st.heating_rate = round(_median(samples), 3)
                st.heating_samples = len(samples)
            # 2.19.1: az utolsó minta és az utolsó elvetett alkalom (a szenzor attribútumaihoz), és a futó alkalom: rövid
            # újraindítás után folytatódik, hosszabb után a `_learn_rates` az újraindítás előtti adatokkal lezárja
            st.rate_last = _load_rate_last(rec.get("last"), now_ts)
            st.rate_drop = _load_rate_drop(rec.get("drop"), now_ts)
            run = _load_rate_run(rec.get("run"), now_ts)
            if run is not None:
                run["heating"] = False  # az újraindítás szünetnek számít
                run["restored"] = True
                st.rate_run = run
        if self.manual_boost_enabled:
            for room_id, rec in _as_dict(data.get("manual")).items():
                st = self.status.get(room_id)
                try:
                    until, offset = float(rec["until"]), float(rec["offset"])
                    started = float(rec.get("started") or now_ts)
                except (KeyError, TypeError, ValueError, AttributeError):
                    continue
                if not (math.isfinite(until) and math.isfinite(offset) and math.isfinite(started)):
                    continue
                if st is not None and now_ts < until <= now_ts + MANUAL_BOOST_MAX_MINUTES * 60 + 60:
                    st.manual_until = until
                    st.manual_offset = _clamp(offset, MANUAL_BOOST_MIN_OFFSET, MANUAL_BOOST_MAX_OFFSET)
                    st.manual_started = min(started, now_ts)
        if self.preheat_enabled:
            for room_id, rec in _as_dict(data.get("preheat")).items():
                st = self.status.get(room_id)
                if st is None or not isinstance(rec, dict):
                    continue
                st.preheat_req = self._clean_plan(rec.get("req"), now_ts)
                st.preheat_latch = self._clean_plan(rec.get("latch"), now_ts)
                if st.preheat_latch is not None:
                    st.preheat_latch["started"] = float(rec["latch"].get("started") or now_ts)
                    st.preheat_latch["warned"] = bool(rec["latch"].get("warned"))
                try:
                    st.preheat_skip = float(rec["skip"]) if rec.get("skip") else None
                except (TypeError, ValueError):
                    st.preheat_skip = None

    def _load_residual(self, data: dict[str, Any]) -> None:
        """A tanult maradékhő mérései. Csak az a szoba kapja vissza, amelynek hőmérője ugyanaz maradt:
        más szenzor más helyen más dinamikát mér. Minden értéket ellenőrzünk."""
        for room_id, rec in _as_dict(data.get("residual")).items():
            st = self.status.get(room_id)
            if st is None or not isinstance(rec, dict) or not st.temp_sensor:
                continue
            if rec.get("sensor") != st.temp_sensor:
                continue
            raw = rec.get("s")
            raw_times = rec.get("t")
            # 2.19: a mérések ideje ("t") a mintákkal párhuzamos lista. A régebbi állományban nincs: ott a betöltés ideje
            # számít, vagyis a korábbi minták a frissítéstől számított 30 nap múlva évülnek el.
            times = raw_times if isinstance(raw_times, list) and isinstance(raw, list) and len(raw_times) == len(raw) else None
            now_ts = dt_util.utcnow().timestamp()
            pairs: list[tuple[float, float]] = []
            for index, item in enumerate(raw if isinstance(raw, list) else []):
                value = _finite(item)
                if value is None or not 0.0 <= value <= RESIDUAL_SAMPLE_MAX:
                    continue
                ts = _finite(times[index]) if times is not None else None
                if ts is None or not 0 < ts <= now_ts + 300:
                    ts = now_ts
                if now_ts - ts > RESIDUAL_SAMPLE_MAX_AGE:
                    continue  # elévült (évszakváltás)
                pairs.append((ts, round(value, 2)))
            pairs = pairs[-RESIDUAL_KEEP:]
            st.resid_times = [ts for ts, _ in pairs]
            st.resid_samples = [value for _, value in pairs]

    @staticmethod
    def _clean_plan(plan: Any, now_ts: float) -> dict[str, Any] | None:
        """Mentett előfűtési terv ellenőrzése; lejárt vagy hibás esetén None."""
        if not isinstance(plan, dict):
            return None
        try:
            clean = {
                "ready": float(plan["ready"]),
                "target": float(plan["target"]),
                "hold": float(plan["hold"]),
                "source": "schedule" if plan.get("source") == "schedule" else "service",
            }
        except (KeyError, TypeError, ValueError):
            return None
        if not all(math.isfinite(clean[key]) for key in ("ready", "target", "hold")):
            return None
        if not 5 <= clean["target"] <= MAX_RAISED_TARGET or not 0 <= clean["hold"] <= 8 * 3600:
            return None  # értelmetlen terv: nem hajtjuk végre
        return clean if clean["ready"] + clean["hold"] > now_ts else None

    async def async_start(self) -> None:
        trvlog.set_enabled(self.entry_id, self.trv_log)
        self._log_startup(await self._async_version())
        if not self.rooms:
            _LOGGER.warning(
                "Nincs szoba beállítva, a kazánt nem vezérlem. "
                "Add hozzá az első szobát az integráció Konfigurálás menüjében."
            )

        tracked: set[str] = {self.boiler}
        if self.outdoor_sensor:
            tracked.add(self.outdoor_sensor)
        for room in self.rooms:
            tracked.update(room[CONF_ROOM_VALVES])
            tracked.update(room.get(CONF_ROOM_WINDOWS) or [])
            for key in (CONF_ROOM_TEMP, CONF_ROOM_HUM):
                if room.get(key):
                    tracked.add(room[key])

        self._unsubs.append(
            async_track_state_change_event(
                self.hass, sorted(tracked), self._handle_event
            )
        )
        self._unsubs.append(
            async_track_time_interval(self.hass, self._handle_tick, TICK)
        )
        self.hass.async_create_task(self.async_evaluate())

    @callback
    def async_stop(self) -> None:
        self._stopped = True  # a függőben lévő kiértékelések már nem futnak le
        trvlog.set_enabled(self.entry_id, False)
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        if self._eval_unsub:
            self._eval_unsub()
            self._eval_unsub = None
        if self.calibrator is not None:
            self.calibrator.async_stop()
        for issue_id, active in list(self._issue_state.items()):
            if active:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)
        self._issue_state.clear()

    async def async_shutdown(self) -> None:
        """Leállítás: megvárja a futó kiértékelést, majd az állapotot azonnal menti.

        Újratöltéskor (beállítás módosítása) és eltávolításkor is ez fut. A régi példány
        késleltetett mentése így nem írhatja felül az újat egy elavult állapottal, és a következő
        indítás pontosan onnan folytatja, ahol ez abbahagyta.
        """
        self.async_stop()
        async with self._lock:
            await self._async_save()

    # ------------------------------------------------------------------ TRV-napló
    def _tlog(self, msg: str, *args: Any) -> None:
        """Az automatika egy döntése a TRV-naplóba (kikapcsolva csak DEBUG szintre), bekapcsolva a Naplókönyvbe is."""
        trvlog.info(self.trv_log, msg, *args)
        if self.trv_log:
            try:
                self.hass.bus.async_fire(
                    trvlog.LOGBOOK_EVENT,
                    {"name": trvlog.LOGBOOK_NAME, "message": trvlog.render(msg, args), "domain": DOMAIN},
                )
            except Exception as err:  # noqa: BLE001 - a napló hibája nem állíthatja le a vezérlést
                _LOGGER.debug("a TRV-napló sora nem került a Naplókönyvbe: %s", err)

    async def _async_version(self) -> str | None:
        """Az integráció verziója a manifestből (az induló naplósorhoz); hiba esetén None."""
        try:
            from homeassistant.loader import async_get_integration  # noqa: PLC0415

            integration = await async_get_integration(self.hass, DOMAIN)
            return str(integration.version) if integration.version else None
        except Exception:  # noqa: BLE001
            return None

    def _valve_label(self, valve_id: str) -> str:
        """"Szoba / szelep" a naplósorokhoz; ismeretlen szelepnél maga az azonosító."""
        for room in self.rooms:
            if valve_id in room.get(CONF_ROOM_VALVES, ()):
                return f"{room.get(CONF_ROOM_NAME, '?')} / {valve_id}"
        return valve_id

    def _describe_valve(self, valve_id: str, now_ts: float) -> str:
        """A szelep kalibráció-számának leírása az induló sorhoz; a hibája nem viheti el a többi szobát."""
        try:
            return self.calibrator.describe_valve(valve_id, now_ts)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("%s: a kalibráció-szám leírása nem sikerült: %s", valve_id, err)
            return "a kalibráció-szám keresése nem sikerült"

    def _log_startup(self, version: str | None = None) -> None:
        """Induláskor (és minden újratöltéskor, vagyis beállítás-mentés után) egy összefoglaló szobánként:
        ebből látszik, mit töltött be az integráció (eltolás, kalibráció, szelep-vezérlés), és hogy a napló működik."""
        if not self.trv_log:
            return
        try:
            self._tlog(
                "%sa napló be van kapcsolva; az automatika szelep- és kalibráció-döntései itt és a Naplókönyvben "
                "követhetők (kikapcsolható: Beállítások › Funkciók)",
                f"Meross Boiler Sync {version}: " if version else "",
            )
            now_ts = dt_util.utcnow().timestamp()
            for room in self.rooms:
                st = self.status.get(room.get(CONF_ROOM_ID))
                if st is None:
                    continue
                if not self.cal_enabled:
                    cal_text = "ki (a Funkciók között nincs bekapcsolva)"
                elif not st.calibrate:
                    cal_text = "ki (ebben a szobában)"
                elif not st.temp_sensor:
                    cal_text = "be, de nincs szoba hőmérő, ezért nem mér"
                else:
                    cal_text = "próbaüzem (csak naplóz)" if self.cal_dry_run else "be"
                    for v in st.valves:
                        cal_text += "; " + (f"{v}: " if len(st.valves) > 1 else "") + self._describe_valve(v, now_ts)
                offset_text = f"{trvlog.signed(st.trv_offset)} °C"
                if st.valve_offsets:  # 2.18: a szelepek egyedi eltolása is látszik (melyik szelep melyik értéket használja)
                    offset_text += " (szoba alapérték; egyedi: " + ", ".join(
                        f"{valve_id} {trvlog.signed(value)} °C" for valve_id, value in st.valve_offsets.items()
                    ) + ")"
                self._tlog(
                    "%s: betöltve – szelepek: %s; szoba hőmérő: %s; szelep-vezérlés: %s; szelep-zárás: %s; TRV eltolás: %s; "
                    "kalibráció: %s",
                    st.name,
                    ", ".join(st.valves) or "nincs",
                    st.temp_sensor or "nincs",
                    "próbaüzem" if st.valve_control and self.valve_dry_run else "be" if st.valve_control else "ki",
                    "próbaüzem" if st.valve_cut and self.valve_dry_run else "be" if st.valve_cut else "ki",
                    offset_text,
                    cal_text,
                )
        except Exception as err:  # noqa: BLE001 - a napló hibája nem állíthatja le az indulást
            _LOGGER.debug("a TRV-napló induló sora nem készült el: %s", err)

    async def async_release_all(self) -> None:
        """Letiltott integráció: az emelt szelepek visszakapják az eredeti célhőmérsékletüket.

        Letiltás után senki nem állítaná vissza őket, és a szelep a maximumon maradna (törléskor ezt az
        `async_restore_on_remove` végzi). Beállítás-módosításnál (újratöltés) nem fut: ott az új példány
        folytatja az emelést. Ha egy szelep éppen nem érhető el, a rekordja megmarad, és a következő
        indulás visszaállítja.
        """
        if getattr(self.hass, "is_stopping", False):
            return
        async with self._lock:
            for valve_id, rec in list(self._boosts.items()):
                state = self.hass.states.get(valve_id)
                if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    continue
                try:
                    raw = float(state.attributes["temperature"])
                except (KeyError, TypeError, ValueError):
                    continue
                if abs(raw - rec["boost"]) > BOOST_TOLERANCE:
                    self._boosts.pop(valve_id, None)  # időközben máshol módosították
                    continue
                if await _async_restore_valve(self.hass, valve_id, state, rec):
                    self._boosts.pop(valve_id, None)
                    self._tlog(
                        "%s: az integráció le van tiltva, az eredeti célhőmérséklet visszaállítva (%s -> %s °C)",
                        self._valve_label(valve_id),
                        rec["boost"],
                        rec["original"],
                    )
            # 2.19: a szelep-zárások (lejjebb állított célok) is visszaállnak
            for valve_id, rec in list(self._cuts.items()):
                state = self.hass.states.get(valve_id)
                if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                    continue
                try:
                    raw = float(state.attributes["temperature"])
                except (KeyError, TypeError, ValueError):
                    continue
                if abs(raw - rec["cut"]) > BOOST_TOLERANCE:
                    self._cuts.pop(valve_id, None)  # időközben máshol módosították
                    continue
                if await _async_restore_valve(self.hass, valve_id, state, rec):
                    self._cuts.pop(valve_id, None)
                    self._tlog(
                        "%s: az integráció le van tiltva, az eredeti célhőmérséklet visszaállítva (%s -> %s °C)",
                        self._valve_label(valve_id),
                        rec["cut"],
                        rec["original"],
                    )
            await self._async_save()

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(listener)

        @callback
        def _remove() -> None:
            if listener in self._listeners:
                self._listeners.remove(listener)

        return _remove

    @callback
    def _notify(self) -> None:
        for listener in list(self._listeners):
            listener()

    @callback
    def _handle_event(self, _event) -> None:
        """Egy figyelt entitás megváltozott: kiértékelés, de az egyszerre érkező változásokat egy körbe vonja össze (2.19).

        Korábban minden állapotváltozás külön, teljes kiértékelést indított, amelyek a zár mögött sorban álltak: a Meross LAN
        újracsatlakozásakor ez több tucat egymás utáni kör volt, közte blokkoló szolgáltatáshívásokkal. Most legfeljebb egy
        kör vár (rövid időzítővel vagy a zárra): az úgyis a friss állapotot olvassa, a közben érkező változás nem vész el.
        """
        if self._stopped or self._eval_unsub is not None or self._eval_queued:
            return
        self._eval_unsub = async_call_later(self.hass, EVENT_DEBOUNCE_SECONDS, self._handle_debounced)

    async def _handle_debounced(self, _now) -> None:
        self._eval_unsub = None
        if self._eval_queued:
            return
        self._eval_queued = True
        try:
            await self.async_evaluate()
        finally:
            self._eval_queued = False

    async def _handle_tick(self, _now) -> None:
        await self.async_evaluate()

    async def _handle_retry(self, _now) -> None:
        self._retry_unsub = None
        await self.async_evaluate()

    def _schedule_retry(self, delay: timedelta) -> None:
        if self._retry_unsub:
            self._retry_unsub()
        self._retry_unsub = async_call_later(
            self.hass, delay + timedelta(seconds=1), self._handle_retry
        )

    # ------------------------------------------------------------------ "Fűts most"
    def _check_manual(self, st: RoomStatus, now_ts: float) -> None:
        """A "Fűts most" lejárata, illetve leállítása (ablak, nyári mód, elavult szenzor)."""
        if st.manual_until is None:
            return
        if now_ts >= st.manual_until:
            self._end_manual(st, "expired", now_ts)
        elif st.window_open:
            self._end_manual(st, "window", now_ts)
        elif self.summer_active:
            self._end_manual(st, "summer", now_ts)
        elif st.sensor_unusable:
            self._end_manual(st, "sensor", now_ts)

    def _end_manual(self, st: RoomStatus, reason: str, now_ts: float) -> None:
        if st.manual_until is None:
            return
        started = st.manual_started
        st.manual_until = None
        st.manual_offset = 0.0
        st.manual_started = None
        extra: dict[str, Any] = {"reason": reason}
        if started is not None:
            extra["duration_minutes"] = round((now_ts - started) / 60)
        self._emit("manual_boost_ended", st, **extra)
        self._delay_save(30)

    def room_by_entity(self, entity_id: str) -> RoomStatus | None:
        """A szoba hőigény szenzorának entity_id-jából a szoba állapota."""
        for st in self.status.values():
            if self._room_entity_id(st.room_id) == entity_id:
                return st
        return None

    def check_boost_allowed(self, st: RoomStatus) -> None:
        """BoostError, ha a szobában most nem indítható a "Fűts most"."""
        if not self.manual_boost_enabled:
            raise BoostError("boost_disabled")
        if self.summer_active:
            raise BoostError("boost_summer", room=st.name)
        if st.window_open:
            raise BoostError("boost_window", room=st.name)
        if st.sensor_stale:
            raise BoostError("boost_stale", room=st.name)
        if st.sensor_bad is not None:
            raise BoostError("boost_unreliable", room=st.name)
        if not st.active:
            raise BoostError("boost_inactive", room=st.name)

    def check_preheat_allowed(self, st: RoomStatus) -> None:
        if not self.preheat_enabled:
            raise BoostError("preheat_disabled")

    async def async_boost_now(
        self, room_id: str, minutes: float | None = None, offset: float | None = None
    ) -> None:
        """"Fűts most": a szoba célját ideiglenesen megemeli (alap +2,0 °C, 60 percre)."""
        st = self.status[room_id]
        self.check_boost_allowed(st)
        now_ts = dt_util.utcnow().timestamp()
        minutes = _clamp(
            float(minutes if minutes is not None else self.manual_boost_minutes),
            MANUAL_BOOST_MIN_MINUTES,
            MANUAL_BOOST_MAX_MINUTES,
        )
        offset = _clamp(
            float(offset if offset is not None else self.manual_boost_offset),
            MANUAL_BOOST_MIN_OFFSET,
            MANUAL_BOOST_MAX_OFFSET,
        )
        if st.manual_until is None:
            st.manual_started = now_ts
        st.manual_until = now_ts + minutes * 60
        st.manual_offset = offset
        self._tlog("%s: Fűts most (+%s °C, %s percre)", st.name, f"{offset:g}", f"{minutes:g}")
        self._emit("manual_boost_started", st, minutes=minutes, offset=offset)
        await self._async_save()
        await self.async_evaluate()

    async def async_cancel_boost_now(self, room_id: str) -> bool:
        st = self.status[room_id]
        if st.manual_until is None:
            return False
        self._end_manual(st, "cancelled", dt_util.utcnow().timestamp())
        await self._async_save()
        await self.async_evaluate()
        return True

    async def async_reset_calibration(self, room_id: str) -> list[str]:
        """2.19: a szoba szelepeinek kalibrációs hibaállapotát törli (hibapontok, felfüggesztés, függő ellenőrzés és
        visszaállítás). A szelep eredeti kalibrációja, ismert igazítása és a módosítások napi kerete megmarad.
        Visszaadja az érintett szelepeket."""
        st = self.status[room_id]
        async with self._lock:
            done = self.calibrator.reset(list(st.valves))
            for valve_id in done:
                self.calibrator._sync_issue(valve_id, st.name, False)
            if done:
                self._tlog(
                    "%s: a kalibráció alaphelyzetbe állítva (%s): hibapontok, felfüggesztés és függő ellenőrzés törölve",
                    st.name,
                    ", ".join(done),
                )
            await self._async_save()
        await self.async_evaluate()
        return done

    # ------------------------------------------------------------------ előfűtés
    def _reset_preheat_view(self, st: RoomStatus) -> None:
        st.preheat_active = False
        st.preheat_status = None
        st.preheat_start_at = st.preheat_ready_by = None
        st.preheat_target = st.preheat_source = None

    def _rate_for(self, st: RoomStatus) -> float:
        """A szoba felfűtési sebessége (°C/óra): a tanult érték, amíg nincs elég minta, az alapérték."""
        if st.heating_rate is not None and st.heating_samples >= HEATING_RATE_MIN_SAMPLES:
            return max(st.heating_rate, HEATING_RATE_MIN)
        return self.preheat_default_rate

    def _learn_rates(self, statuses: list[RoomStatus]) -> None:
        """A felfűtési sebesség tanulása fűtési alkalmanként (2.19; 2.19.1: a rövid szünetek nem szakítják meg).

        Egy alkalom akkor indul, amikor a hőt kérő szoba hőt kap (a szoba hőt kér a kazántól, és a kazán megy), a szoba
        hőmérője megbízható, és nincs nyitott ablak, tartalék vezérlés vagy fagyvédelem. A hőleadás legfeljebb
        `HEATING_SESSION_PAUSE_MAX` hosszú szünete nem szakítja meg: a szelep elzárása (a szelep állapotához kötött
        hőigénynél ilyenkor a kazán is leáll; a Meross szelep a radiátor melletti mérése miatt gyakran a szoba céljának
        elérése előtt zár), a kazán ciklusvédelmi szünete, egy kimaradt mérés vagy egy újraindítás.

        A minta az emelkedés osztva az idővel, a rövid szünetekkel és a radiátor felfűtésével együtt:
        - ha a szoba már nem kér hőt (elérte a célját): az alkalom kezdetétől mostanáig;
        - ha a hőleadás ennél tovább szünetel (vagy a HA ennél tovább nem futott): a kezdettől a szünet kezdetéig, vagyis az
          utolsó hőleadás közbeni mérésig (a szelep elzárása előtti fűtés is érvényes mérés);
        legalább 20 perc és 0,2 °C emelkedés kell hozzá. A nyitott ablak, a szoba hőmérő hibája, a tartalék vezérlés és a
        fagyvédelem az alkalmat elveti. A nem számító alkalom okát a TRV-napló és a szoba szenzorának
        `heating_rate_last_drop` attribútuma mutatja (a célját gyorsan elérő rövid rátöltés rendszeres, ezért az csak az
        attribútumban és a hibakereső naplóban látszik).
        """
        boiler_on = self._boiler_is_on()
        now_ts = dt_util.utcnow().timestamp()
        for st in statuses:
            reading = st.current is not None and st.source == "sensor" and not st.sensor_unusable
            heating = reading and st.boiler_demand and boiler_on is True
            run = st.rate_run
            if run is None:
                if heating and st.calling and self._rate_spoiler(st) is None:
                    st.rate_run = {
                        "t0": now_ts,
                        "temp0": st.current,
                        "t_heat": now_ts,
                        "temp_heat": st.current,
                        "pauses": 0,
                        "heating": True,
                    }
                    self._delay_save(HEATING_SESSION_SAVE_SECONDS)
                continue
            if now_ts - run["t_heat"] > HEATING_SESSION_PAUSE_MAX:
                # a hőleadás (vagy a mérés) régóta szünetel, vagy a HA ennél tovább nem futott: a szünet kezdetéig mért adat
                # érvényes, azzal zárjuk (az újraindítás előtti, azóta nem folytatott alkalomnál "restart")
                self._finish_rate_run(
                    st, run["t_heat"], run["temp_heat"], "restart" if run.get("restored") else "pause", now_ts
                )
                continue
            spoiler = self._rate_spoiler(st)
            if spoiler is not None:
                st.rate_run = None
                self._note_rate_drop(
                    st, spoiler, "interrupted", max(run["t_heat"] - run["t0"], 0.0), run["temp_heat"] - run["temp0"], now_ts
                )
                continue
            if not st.calling and reading:
                self._finish_rate_run(st, now_ts, st.current, "target", now_ts)
                continue
            if heating:
                if not run.get("heating"):
                    run["pauses"] = int(run.get("pauses", 0)) + 1  # szünet után újra kap hőt
                run.update(t_heat=now_ts, temp_heat=st.current, heating=True)
                run.pop("restored", None)
            else:
                run["heating"] = False  # rövid szünet: a szelep elzárt, a kazán áll, vagy most nincs mérés
            self._delay_save(HEATING_SESSION_SAVE_SECONDS)

    @staticmethod
    def _rate_spoiler(st: RoomStatus) -> str | None:
        """Ami mellett a mérés nem a szoba szokásos felfűtését mutatja: az alkalom elvetésének oka (2.19.1), vagy None."""
        if st.window_open:
            return "window"
        if st.sensor_bad is not None or st.sensor_stuck:
            return "sensor"
        if st.fallback:
            return "valves_unreachable"
        if st.frost:
            return "frost"
        return None

    def _finish_rate_run(self, st: RoomStatus, end_ts: float, end_temp: float, ended: str, now_ts: float) -> None:
        """A futó alkalom lezárása: minta, ha legalább 20 perc és 0,2 °C; különben elvetett alkalom (az okával)."""
        run = st.rate_run or {}
        st.rate_run = None
        seconds = max(end_ts - run.get("t0", end_ts), 0.0)
        rise = end_temp - run.get("temp0", end_temp)
        if seconds < HEATING_SESSION_MIN_SECONDS:
            self._note_rate_drop(st, "short", ended, seconds, rise, now_ts)
            return
        if rise < HEATING_SESSION_MIN_RISE - 1e-9:
            self._note_rate_drop(st, "small_rise", ended, seconds, rise, now_ts)
            return
        pauses = int(run.get("pauses", 0))
        sample = round(_clamp(rise / (seconds / 3600), HEATING_RATE_MIN, HEATING_RATE_MAX), 3)
        st.rate_samples.append(sample)
        del st.rate_samples[:-HEATING_RATE_KEEP]
        st.heating_rate = round(_median(st.rate_samples), 3)
        st.heating_samples = len(st.rate_samples)
        st.rate_last = {
            "ts": end_ts,
            "rate": sample,
            "minutes": round(seconds / 60),
            "rise": round(rise, 2),
            "ended": ended,
            "pauses": pauses,
        }
        self._tlog(
            "%s: felfűtési minta: +%.1f °C %d perc alatt (%.2f °C/óra; %s%s); tanult sebesség: %.2f °C/óra (%d alkalomból)",
            st.name,
            rise,
            round(seconds / 60),
            sample,
            _RATE_ENDED_HU[ended],
            f", {pauses} rövid szünettel" if pauses else "",
            st.heating_rate,
            st.heating_samples,
        )
        self._delay_save(60)

    def _note_rate_drop(
        self, st: RoomStatus, reason: str, ended: str, seconds: float, rise: float, now_ts: float
    ) -> None:
        """Egy mintának nem számító alkalom rögzítése (attribútum, mentés) és naplózása az okával."""
        st.rate_drop = {
            "ts": now_ts,
            "reason": reason,
            "ended": ended,
            "minutes": round(seconds / 60),
            "rise": round(rise, 2),
        }
        self._delay_save(60)
        args = (st.name, _RATE_DROP_HU[reason], round(seconds / 60), rise, _RATE_ENDED_HU[ended])
        key = f"{reason}/{ended}"
        routine = ended == "target" and reason in ("short", "small_rise")  # a célját gyorsan elérő rövid rátöltés
        if routine or now_ts - st.rate_drop_logged.get(key, -1e12) < HEATING_DROP_LOG_SECONDS:
            _LOGGER.debug("%s: a felfűtési alkalom nem számít mintának: %s (%d perc, %+.1f °C; %s)", *args)
            return
        st.rate_drop_logged[key] = now_ts
        self._tlog("%s: a felfűtési alkalom nem számít mintának: %s (%d perc, %+.1f °C; %s)", *args)

    def _preheat_plans(
        self, st: RoomStatus, room: dict[str, Any], now_ts: float
    ) -> list[dict[str, Any]]:
        """Az egyszeri kérés és a heti menetrend következő időpontjai (ready szerint rendezve)."""
        plans: list[dict[str, Any]] = []
        if st.preheat_req:
            plans.append({**st.preheat_req, "source": "service"})
        local_now = dt_util.now()
        tz = local_now.tzinfo
        for entry in room.get(CONF_ROOM_PREHEAT) or []:
            clock = _parse_hhmm(entry.get("time"))
            try:
                days = {int(d) for d in entry.get("days") or []}
                target = float(entry["temperature"])
            except (KeyError, TypeError, ValueError):
                continue
            if clock is None or not days:
                continue
            for add in range(-1, 8):  # tegnap is: a tartás átnyúlhat éjfélen
                day = local_now.date() + timedelta(days=add)
                if day.weekday() not in days:
                    continue
                ready = datetime(day.year, day.month, day.day, clock[0], clock[1], tzinfo=tz).timestamp()
                if ready + self.preheat_hold_s <= now_ts:
                    continue
                if st.preheat_skip is not None and ready <= st.preheat_skip:
                    continue
                plans.append(
                    {"ready": ready, "target": target, "hold": self.preheat_hold_s, "source": "schedule"}
                )
                break
        plans.sort(key=lambda p: p["ready"])
        return plans

    @staticmethod
    def _same_plan(a: dict[str, Any] | None, b: dict[str, Any]) -> bool:
        return (
            a is not None
            and abs(a["ready"] - b["ready"]) < 1
            and abs(a["target"] - b["target"]) < 0.05
        )

    def _local_hhmm(self, ts: float) -> str:
        tz = dt_util.now().tzinfo
        return datetime.fromtimestamp(ts, tz=tz).strftime("%H:%M")

    def _update_preheat(
        self, st: RoomStatus, room: dict[str, Any], current: float | None, now_ts: float
    ) -> None:
        """Előfűtés: a "kész" időpont elé időzítve megemeli a szoba célját.

        Az indulást a tanult (vagy alap) felfűtési sebességből számolja: a hiányzó fokokat
        elosztja a sebességgel, megszorozza a biztonsági tényezővel, de legfeljebb a beállított
        maximumot (alap 4 óra) kezdi korábban. Ha elindult, a "kész" időpont + tartás végéig
        fut, akkor is, ha közben a szoba már felmelegedett.
        """
        self._reset_preheat_view(st)
        if not self.preheat_enabled:
            st.preheat_latch = None
            st.preheat_req = None
            return
        plans = self._preheat_plans(st, room, now_ts)
        # lejárt egyszeri kérés / futó terv törlése
        if st.preheat_req and st.preheat_req["ready"] + st.preheat_req["hold"] <= now_ts:
            st.preheat_req = None
        if st.preheat_latch and st.preheat_latch["ready"] + st.preheat_latch["hold"] <= now_ts:
            st.preheat_latch = None
        if (
            current is None
            or self.summer_active
            or st.window_open
            or st.sensor_unusable
        ):
            return  # nem fűtünk előre, a terv megmarad (a latch is)

        rate = self._rate_for(st)
        best: tuple[dict[str, Any], float, float] | None = None  # (terv, indulás, szükséges idő)
        upcoming: tuple[dict[str, Any], float] | None = None
        for plan in plans:
            ready, target = plan["ready"], plan["target"]
            if now_ts >= ready + plan["hold"]:
                continue
            gap = target - current
            need = gap / rate * 3600 * PREHEAT_SAFETY if gap > PREHEAT_DONE_TOLERANCE else 0.0
            start_at = ready - min(need, self.preheat_max_s)
            latched = self._same_plan(st.preheat_latch, plan)
            # indulhat: elérte az indulási időt, és a "kész" időponthoz képest nem késett le (1 tick)
            can_start = start_at <= now_ts < ready + TICK.total_seconds() * 1.5
            if latched or can_start:
                if best is None or target > best[0]["target"]:
                    best = (plan, start_at, need)
            elif upcoming is None and start_at - now_ts <= PREHEAT_LOOKAHEAD_SECONDS:
                upcoming = (plan, start_at)

        if best is not None:
            plan, start_at, need = best
            if not self._same_plan(st.preheat_latch, plan):
                st.preheat_latch = {**plan, "started": now_ts, "warned": False}
                self._emit(
                    "preheat_started",
                    st,
                    target_temperature=plan["target"],
                    ready_by=self._local_hhmm(plan["ready"]),
                    minutes_to_ready=max(0, round((plan["ready"] - now_ts) / 60)),
                    heating_rate=round(rate, 2),
                    source=plan["source"],
                )
                self._delay_save(30)
            remaining = plan["ready"] - now_ts
            late = remaining > 0 and need > remaining + PREHEAT_GRACE_SECONDS
            if late and not st.preheat_latch.get("warned"):
                st.preheat_latch["warned"] = True
                self._emit(
                    "preheat_unreachable",
                    st,
                    target_temperature=plan["target"],
                    ready_by=self._local_hhmm(plan["ready"]),
                    minutes_needed=round(need / 60),
                    minutes_available=max(0, round(remaining / 60)),
                )
            st.preheat_active = True
            st.preheat_target = plan["target"]
            st.preheat_ready_by = plan["ready"]
            st.preheat_source = plan["source"]
            st.preheat_start_at = st.preheat_latch.get("started", start_at)
            if current >= plan["target"] - PREHEAT_DONE_TOLERANCE:
                st.preheat_status = "ready"
            elif late:
                st.preheat_status = "unreachable"
            else:
                st.preheat_status = "heating"
        elif upcoming is not None:
            plan, start_at = upcoming
            st.preheat_status = "scheduled"
            st.preheat_start_at = start_at
            st.preheat_ready_by = plan["ready"]
            st.preheat_target = plan["target"]
            st.preheat_source = plan["source"]

    async def async_preheat(
        self,
        room_id: str,
        ready_ts: float,
        target: float,
        hold_minutes: float | None = None,
    ) -> None:
        """Egyszeri előfűtés: a szoba legyen `target` °C a `ready_ts` időpontra."""
        st = self.status[room_id]
        self.check_preheat_allowed(st)
        now_ts = dt_util.utcnow().timestamp()
        if ready_ts <= now_ts:
            raise BoostError("preheat_past", room=st.name)
        if not 5 <= target <= MAX_RAISED_TARGET:
            raise BoostError("preheat_target", room=st.name)
        hold = self.preheat_hold_s if hold_minutes is None else _clamp(float(hold_minutes), 0, 480) * 60
        st.preheat_req = {"ready": ready_ts, "target": float(target), "hold": hold, "source": "service"}
        if st.preheat_latch is not None and st.preheat_latch.get("source") == "service":
            st.preheat_latch = None
        self._tlog(
            "%s: előfűtés kérve: %s °C, kész: %s", st.name, f"{target:g}", self._local_hhmm(ready_ts)
        )
        await self._async_save()
        await self.async_evaluate()

    async def async_cancel_preheat(self, room_id: str) -> bool:
        """Az egyszeri kérés törlése, és a most futó / következő menetrendi előfűtés kihagyása."""
        st = self.status[room_id]
        room = next(r for r in self.rooms if r[CONF_ROOM_ID] == room_id)
        now_ts = dt_util.utcnow().timestamp()
        changed = st.preheat_req is not None or st.preheat_latch is not None
        st.preheat_req = None
        if st.preheat_latch is not None:
            if st.preheat_latch.get("source") == "schedule":
                st.preheat_skip = max(st.preheat_skip or 0.0, st.preheat_latch["ready"])
            st.preheat_latch = None
        else:
            sched = [p for p in self._preheat_plans(st, room, now_ts) if p["source"] == "schedule"]
            if sched and st.preheat_status == "scheduled":
                st.preheat_skip = max(st.preheat_skip or 0.0, sched[0]["ready"])
                changed = True
        await self._async_save()
        await self.async_evaluate()
        return changed

    # ------------------------------------------------------------------ események
    def _room_entity_id(self, room_id: str) -> str | None:
        """A szoba "fűtési igény" szenzorának entity_id-ja (az eseményekhez és a naplóhoz)."""
        if room_id not in self._entity_ids:
            try:
                self._entity_ids[room_id] = er.async_get(self.hass).async_get_entity_id(
                    "binary_sensor", DOMAIN, f"{self.entry_id}_room_{room_id}"
                )
            except Exception:  # noqa: BLE001 - az esemény miatt ne álljon le a vezérlés
                self._entity_ids[room_id] = None
        return self._entity_ids[room_id]

    def _emit(self, type_: str, st: RoomStatus | None = None, **extra: Any) -> None:
        """meross_boiler_sync_event esemény küldése (ki/be kapcsolható; indulás alatt nem küld)."""
        if not self.events_enabled or not self._events_armed:
            return
        data: dict[str, Any] = {"type": type_, **extra}
        if st is not None:
            data["room"] = st.name
            data["entity_id"] = self._room_entity_id(st.room_id)
        self.hass.bus.async_fire(EVENT_TYPE, data)

    # ------------------------------------------------------------------ segédek
    def _read_sensor(self, entity_id: str | None) -> tuple[float | None, bool]:
        """(érték, elavult-e). Elavult: a szenzor a megadott ideje nem jelentett."""
        if not entity_id:
            return None, False
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None, False
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None, False
        if self.stale_enabled:
            reported = getattr(state, "last_reported", None) or getattr(
                state, "last_updated", None
            )
            if (
                reported is not None
                and (dt_util.utcnow() - reported).total_seconds() > self.stale_seconds
            ):
                return None, True
        return value, False

    def _read_float(self, entity_id: str | None) -> float | None:
        return self._read_sensor(entity_id)[0]

    def _vet_room_temp(self, st: RoomStatus, value: float | None, now_ts: float) -> float | None:
        """A szoba hőmérő hihetőségi vizsgálata: a képtelen vagy ugráló értékre nem építünk.

        Egy hibás szenzor (kimerülő elem, zárlat, hibaérték, ugráló mérés) hideget vagy meleget hazudna,
        és a kazánt feleslegesen járatná, a szelepet feleslegesen emelné. Gyanús:
        - a tartományon kívüli érték (`SENSOR_TEMP_MIN`..`SENSOR_TEMP_MAX`; a NaN is),
        - ha a mérés az utolsó `SENSOR_PATH_WINDOW` másodpercben összesen több mint `SENSOR_PATH_MAX`
          fokot ugrál fel-le (az `SENSOR_STEP_MIN`-nél kisebb lépés mérési zaj, az nem számít).
        Gyanús érték után az utolsó gyanús lépéstől számított `SENSOR_HOLD_SECONDS` ideig nem bízunk a
        szenzorban: a szoba a szelepek saját mérésére vált (mint elérhetetlen szenzornál), a
        szelepemelés és a kalibráció megáll. A ritkán jelentő szenzort egy nagy lépés nem teszi gyanússá
        (a jelentések az ablakon kívül esnek), a tartományon kívüli érték viszont ilyenkor is az.
        Ha a szenzor közben elérhetetlenné válik, a jelzés megmarad: hihető mérés nélkül nem oldjuk fel.
        """
        if not st.temp_sensor:
            st.sensor_bad = None
            return value
        if value is None:
            return None  # nem elérhető / elavult: nincs mit vizsgálni, a korábbi jelzés változatlan marad
        rep = min(self._reported_ts(st.temp_sensor) or now_ts, now_ts)
        if not (SENSOR_TEMP_MIN <= value <= SENSOR_TEMP_MAX):
            st.sv_until, st.sv_reason = now_ts + SENSOR_HOLD_SECONDS, "range"
        elif rep > st.sv_seen + 0.5:  # új jelentés: az ingadozást csak jelentésenként vizsgáljuk
            hist = st.sv_hist
            hist.append((rep, value))
            while hist and hist[0][0] < rep - SENSOR_PATH_WINDOW:
                hist.pop(0)
            if len(hist) >= 2 and abs(hist[-1][1] - hist[-2][1]) >= SENSOR_STEP_MIN:
                # az új lépés nem zaj: ha az ablak összes nagy lépése együtt túl sok, gyanús
                path = sum(
                    abs(b[1] - a[1])
                    for a, b in zip(hist, hist[1:])
                    if abs(b[1] - a[1]) >= SENSOR_STEP_MIN
                )
                if path > SENSOR_PATH_MAX:
                    st.sv_until, st.sv_reason = now_ts + SENSOR_HOLD_SECONDS, "jump"
        st.sv_seen = max(st.sv_seen, rep)
        st.sensor_bad = st.sv_reason if now_ts < st.sv_until else None
        return None if st.sensor_bad else value

    def _note_sensor_vetting(
        self, st: RoomStatus, was_bad: str | None, raw: float | None
    ) -> None:
        """A szoba hőmérő hihetőségének változása: Javítások-üzenet, napló és esemény."""
        temp_id = st.temp_sensor or ""
        bad = st.sensor_bad
        minutes = f"{SENSOR_HOLD_SECONDS // 60}"
        if bad is not None and was_bad is None:
            what = (
                f"képtelen érték ({raw:g} °C)"
                if bad == "range" and raw is not None and math.isfinite(raw)
                else "képtelen érték" if bad == "range" else "ugráló mérés"
            )
            self._sync_issue(
                f"unreliable_room_{self.entry_id}_{st.room_id}",
                True,
                "unreliable_room_temp",
                {"room": st.name, "sensor": temp_id, "minutes": minutes},
                message=(
                    f"{st.name}: a szoba hőmérő ({temp_id}) nem megbízható: {what}; {minutes} percig "
                    "a szelepek saját mérésére váltok"
                ),
            )
            self._emit(
                "sensor_unreliable",
                st,
                sensor=temp_id,
                reason=bad,
                value=None if raw is None or not math.isfinite(raw) else round(raw, 1),
            )
        elif bad is None and was_bad is not None:
            self._sync_issue(
                f"unreliable_room_{self.entry_id}_{st.room_id}",
                False,
                "unreliable_room_temp",
                {"room": st.name, "sensor": temp_id, "minutes": minutes},
            )
            self._tlog("%s: a szoba hőmérő (%s) újra megbízhatónak látszik", st.name, temp_id)
            self._emit("sensor_reliable", st, sensor=temp_id)

    def _reported_ts(self, entity_id: str | None) -> float | None:
        """A szenzor utolsó jelentésének ideje (epoch), ha ismert."""
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None:
            return None
        reported = getattr(state, "last_reported", None) or getattr(
            state, "last_updated", None
        )
        return reported.timestamp() if reported is not None else None

    def _stale_hours_text(self) -> str:
        return f"{self.stale_seconds / 3600:g}"

    def _sync_issue(
        self,
        issue_id: str,
        active: bool,
        translation_key: str,
        placeholders: dict[str, str],
        message: str | None = None,
    ) -> None:
        """Javítások (Repairs) értesítés létrehozása / törlése, csak változáskor."""
        if self._issue_state.get(issue_id) == active:
            return
        self._issue_state[issue_id] = active
        if active:
            if message is not None:
                _LOGGER.warning("%s", message)
            else:
                _LOGGER.warning(
                    "Elavult szenzor: %s (%s óra óta nem jelentett)",
                    placeholders.get("sensor"),
                    placeholders.get("hours"),
                )
            ir.async_create_issue(
                self.hass,
                DOMAIN,
                issue_id,
                is_fixable=False,
                severity=ir.IssueSeverity.WARNING,
                translation_key=translation_key,
                translation_placeholders=placeholders,
            )
        else:
            ir.async_delete_issue(self.hass, DOMAIN, issue_id)

    def _in_summer_window(self, today: date) -> bool:
        md = (today.month, today.day)
        start, end = self.summer_start, self.summer_end
        if start <= end:
            return start <= md <= end
        return md >= start or md <= end  # évhatáron átnyúló időszak

    def _data_to_save(self) -> dict[str, Any]:
        # másolatot adunk: a mentés közben a vezérlő tovább módosíthatja a saját adatait
        return copy.deepcopy(self._raw_data_to_save())

    def _raw_data_to_save(self) -> dict[str, Any]:
        return {
            "samples": [[ts, val] for ts, val in self._samples],
            "boosts": self._boosts,
            "cuts": self._cuts,
            "targets": {
                st.room_id: st.last_target for st in self.status.values() if st.last_target is not None
            },
            "cycles": self.cycles.to_list(),
            "gas": {"m3": round(self.gas_m3, 4)},
            "summer": {"active": self.summer_active},
            "rest": {
                st.room_id: st.rest_until
                for st in self.status.values()
                if st.rest_until is not None
            },
            "manual": {
                st.room_id: {
                    "until": st.manual_until,
                    "offset": st.manual_offset,
                    "started": st.manual_started,
                }
                for st in self.status.values()
                if st.manual_until is not None
            },
            "preheat": {
                st.room_id: {"req": st.preheat_req, "latch": st.preheat_latch, "skip": st.preheat_skip}
                for st in self.status.values()
                if st.preheat_req or st.preheat_latch or st.preheat_skip
            },
            # 2.19: fűtési alkalmankénti minták ("s"); a "rate" és az "n" csak tájékoztató (a betöltés a mintákból számol)
            "rates": {
                st.room_id: {
                    "rate": st.heating_rate,
                    "n": st.heating_samples,
                    "s": list(st.rate_samples),
                    # 2.19.1: az utolsó minta, az utolsó elvetett alkalom és a futó alkalom
                    **({"last": dict(st.rate_last)} if st.rate_last else {}),
                    **({"drop": dict(st.rate_drop)} if st.rate_drop else {}),
                    **({"run": {k: v for k, v in st.rate_run.items() if k != "restored"}} if st.rate_run else {}),
                }
                for st in self.status.values()
                if st.rate_samples or st.rate_last or st.rate_drop or st.rate_run
            },
            # 2.13: a tanult maradékhő mérései (a szoba hőmérőjével együtt)
            "residual": {
                st.room_id: {
                    "sensor": st.temp_sensor,
                    "s": list(st.resid_samples),
                    # 2.19: a mérések ideje (a 30 napnál régebbiek kiesnek); csak akkor írjuk ki, ha a két lista párban áll
                    **({"t": list(st.resid_times)} if len(st.resid_times) == len(st.resid_samples) else {}),
                }
                for st in self.status.values()
                if st.resid_samples and st.temp_sensor
            },
            # kalibráció: az eredeti értékek, a függő módosítások és a korlátozások (újraindítás után is)
            "calibration": self.calibrator.to_dict(),
            "cal_idle": self.calibrator.idle_to_dict(dt_util.utcnow().timestamp()),
        }

    # ------------------------------------------------------------------ nyári mód
    def _update_outdoor(self) -> None:
        if not self.outdoor_sensor:
            self.summer_active = False
            self.in_summer_period = self._in_summer_window(dt_util.now().date())
            self.outdoor_now = None
            self.outdoor_avg = None
            return

        now_ts = dt_util.utcnow().timestamp()
        value, stale = self._read_sensor(self.outdoor_sensor)
        if value is not None and not (SAMPLE_TEMP_MIN <= value <= SAMPLE_TEMP_MAX):
            # képtelen érték (pl. 85 vagy -127 °C hibaérték): nem használjuk, nehogy tévesen nyári módot
            # (vagy fűtést) kapcsoljon; a fűtés ilyenkor engedélyezett marad
            if now_ts - self._outdoor_warned >= 3600:
                self._outdoor_warned = now_ts
                _LOGGER.warning(
                    "A kinti szenzor (%s) képtelen értéket ad (%s), nem használom", self.outdoor_sensor, value
                )
            value = None
        self.outdoor_now = value
        if stale != self.outdoor_stale:
            self._emit_stale(None, self.outdoor_sensor, stale)
        self.outdoor_stale = stale
        self._sync_issue(
            f"stale_outdoor_{self.entry_id}",
            stale,
            "stale_outdoor",
            {"sensor": self.outdoor_sensor, "hours": self._stale_hours_text()},
        )
        reported_ts = self._reported_ts(self.outdoor_sensor)

        # csak akkor mintavételezünk, ha a szenzor az előző minta óta tényleg jelentett
        if value is not None and (
            not self._samples
            or (
                now_ts - self._samples[-1][0] >= SAMPLE_INTERVAL_SECONDS
                and (reported_ts is None or reported_ts > self._samples[-1][0])
            )
        ):
            self._samples.append((now_ts, value))
            self._delay_save(600)

        cutoff = now_ts - AVG_WINDOW_SECONDS
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()

        if self._samples:
            self.outdoor_avg = round(
                sum(v for _, v in self._samples) / len(self._samples), 1
            )
        else:
            self.outdoor_avg = None

        self.in_summer_period = self._in_summer_window(dt_util.now().date())

        if self.outdoor_avg is None or not self.in_summer_period or self.outdoor_stale:
            # elavult kinti szenzornál nincs nyári mód: a fűtés engedélyezett marad
            self.summer_active = False
        elif self.summer_active:
            self.summer_active = (
                self.outdoor_avg > self.summer_temp - SUMMER_HYSTERESIS
            )
        else:
            self.summer_active = self.outdoor_avg > self.summer_temp

    # ------------------------------------------------------------------ szobák
    def _update_room(self, room: dict[str, Any]) -> RoomStatus:
        st = self.status[room[CONF_ROOM_ID]]
        now_ts = dt_util.utcnow().timestamp()

        targets: list[float] = []
        valve_temps: list[float] = []
        frost_reads: list[float] = []  # 2.19: a szelepek nyers mérései a fagyvédelemhez (a kikapcsolt szelepé is)
        pairs: list[tuple[float, float]] = []
        reachable = 0
        for valve_id in room[CONF_ROOM_VALVES]:
            state = self.hass.states.get(valve_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            reachable += 1
            try:
                valve_current = float(state.attributes["current_temperature"])
            except (KeyError, TypeError, ValueError):
                valve_current = None
            if valve_current is not None and FROST_READING_MIN <= valve_current <= SENSOR_TEMP_MAX:
                frost_reads.append(valve_current)
            if state.state == HVACMode.OFF:
                continue
            raw = self._valve_target(state)
            user_target = self._user_target(valve_id, raw) if raw is not None else None
            if user_target is not None:
                targets.append(user_target)
            if valve_current is not None and not (
                SENSOR_TEMP_MIN <= valve_current <= SENSOR_TEMP_MAX
            ):
                valve_current = None  # hibaérték (pl. 0 vagy 85 °C): nem hihető
            if valve_current is not None:
                # 2.19: ha a szoba hőmérője helyett a szelep mérése vezérel, a kalibrációval szándékosan beállított
                # eltolást visszaszámoljuk (a szelep saját szabályzását becslő `pairs` a nyers mérést kapja)
                valve_temps.append(valve_current + self._valve_shift(st, valve_id))
                if user_target is not None:
                    pairs.append((valve_current, user_target))

        st.reachable = reachable > 0
        st.active = bool(targets)

        temp_id = room.get(CONF_ROOM_TEMP)
        sensor_value, sensor_stale = self._read_sensor(temp_id)
        if temp_id and sensor_stale != st.sensor_stale:
            self._emit_stale(st, temp_id, sensor_stale)
        st.sensor_stale = sensor_stale
        self._sync_issue(
            f"stale_room_{self.entry_id}_{st.room_id}",
            sensor_stale and bool(temp_id),
            "stale_room_temp",
            {"room": st.name, "sensor": temp_id or "", "hours": self._stale_hours_text()},
        )
        self._update_window(st)
        # 2.11.1: képtelen vagy ugráló érték nem vezérli a szobát (a szelepek saját mérésére váltunk)
        raw_sensor_value, was_bad = sensor_value, st.sensor_bad
        sensor_value = self._vet_room_temp(st, sensor_value, now_ts)
        if (st.sensor_bad is None) != (was_bad is None):
            self._note_sensor_vetting(st, was_bad, raw_sensor_value)
        # 2.19: fűtés közben nem jelentő (elakadt) hőmérő sem vezérel: a szelepek mérésére váltunk, amíg újra nem jelent
        if self._check_stuck(st, room, sensor_value, now_ts):
            sensor_value = None
        self._check_manual(st, now_ts)

        # 2.19: a szoba szelepei nem elérhetők (hub, Wi-Fi, Meross LAN hiba): a szelep a saját céljával tovább szabályoz, csak
        # a HA nem látja. A türelmi idő után a hőigény a szoba hőmérőjéből és az utolsó ismert célból megy tovább.
        self._track_targets(st, targets, reachable, now_ts)
        fallback = (
            not targets
            and reachable == 0
            and st.last_target is not None
            and st.lost_since is not None
            and now_ts - st.lost_since >= VALVE_LOST_GRACE_SECONDS
            and sensor_value is not None
        )
        self._set_fallback(st, fallback)
        if fallback:
            targets = [st.last_target]
        # 2.19: fagyvédelem (a szelep állapotától, az ablaktól és a nyári módtól függetlenül)
        frost = self._update_frost(st, sensor_value, raw_sensor_value, frost_reads, now_ts)

        st.current = st.source = st.target = st.effective_target = None
        st.deviation = None
        st.humidity = None
        st.humidity_boost = 0.0

        if not targets:
            st.calling = False
            st.valve_open = False
            self._reset_preheat_view(st)
            self._reset_residual(st)
            if frost:
                # nincs cél (kikapcsolt vagy elérhetetlen szelepek), de fagyveszély van: a szoba hőt kér a kazántól
                if sensor_value is not None:
                    st.current, st.source = sensor_value, "sensor"
                elif frost_reads:
                    st.current, st.source = sum(frost_reads) / len(frost_reads), "valve"
                st.effective_target = round(self.frost_temp + FROST_HYSTERESIS, 2)
                if st.current is not None:
                    st.deviation = round(st.effective_target - st.current, 2)
                st.calling = True
            self._update_trend(st)  # nincs aktuális érték: a trend törlődik
            return st

        # a szoba célhőmérséklete a szelep(ek)en beállított érték (a legmagasabb)
        st.target = max(targets)

        # aktuális hőmérséklet: szoba szenzor, ennek hiányában a szelepek átlaga
        current = sensor_value
        if current is not None:
            st.source = "sensor"
        elif valve_temps:
            current = sum(valve_temps) / len(valve_temps)
            st.source = "valve"
        st.current = current
        self._update_trend(st)

        # páratartalom miatti célhőmérséklet-emelés (2.19: a szobában megadott érték, ennek hiányában az általános)
        humidity = self._read_float(room.get(CONF_ROOM_HUM))
        if humidity is not None and not (HUMIDITY_MIN <= humidity <= HUMIDITY_MAX):
            humidity = None  # képtelen páratartalom (hibás szenzor): nem emeli a célt
        st.humidity = humidity
        if (
            humidity is not None
            and st.humidity_max_boost > 0
            and st.target >= COMFORT_MIN_TARGET
        ):
            frac = (humidity - HUMIDITY_START) / (HUMIDITY_FULL - HUMIDITY_START)
            st.humidity_boost = round(
                st.humidity_max_boost * min(max(frac, 0.0), 1.0), 2
            )
        base = min(st.target + st.humidity_boost, max(MAX_EFFECTIVE_TARGET, st.target))
        raised = base + st.manual_offset if st.manual_until is not None else base
        self._update_preheat(st, room, current, now_ts)
        if st.preheat_active and st.preheat_target is not None:
            raised = max(raised, st.preheat_target)
        if (
            self.manual_boost_end_on_target
            and st.manual_until is not None
            and current is not None
            and current >= raised
        ):
            # a szoba elérte a megemelt célt: a Fűts most véget ér (kapcsolható viselkedés)
            self._end_manual(st, "target_reached", now_ts)
            raised = base
            if st.preheat_active and st.preheat_target is not None:
                raised = max(raised, st.preheat_target)
        if raised > base:  # "Fűts most" / előfűtés: megemelt cél, de nem a végtelenségig
            raised = min(raised, max(MAX_RAISED_TARGET, base))
        st.effective_target = round(raised, 2)

        if current is not None:
            st.deviation = round(st.effective_target - current, 2)

        # újraindítás után: a hiszterézis állapota nem veszett el, ha a kazán közben fűtött
        resume = self._seed_active(st) if current is not None else False

        # hőigény hiszterézissel: indul, ha a cél alatt van, megy a cél eléréséig. A tanult maradékhő
        # (2.13) miatt a leállás `stop_lead`-del előbb jön, és a sáv szélessége nem változik, ezért a
        # bekapcsolási küszöb is ennyivel lejjebb csúszik (így nem lesz több kazánindítás).
        was_calling = st.calling
        st.stop_lead = self._stop_lead(st)
        stop_at = st.effective_target - st.stop_lead
        if current is None:
            st.calling = False
        elif st.calling:
            if current >= stop_at:
                st.calling = False
        elif current < stop_at - self.hysteresis:
            st.calling = True
        elif resume and current < stop_at:
            st.calling = True  # a fűtés a cél eléréséig folytatódik

        if st.window_open:
            st.calling = False  # nyitott ablak: a szoba nem kér hőt, a szelep emelés leáll
        # 2.19: a tartalék vezérlés (elérhetetlen szelepek) csak akkor kérhet tartósan hőt, ha a szoba melegszik is
        st.fallback_paused = st.fallback and self._fallback_stalled(st, current, now_ts)
        if st.fallback_paused:
            st.calling = False
        if frost:
            # 2.19: fagyveszély: a szoba nyitott ablaknál és a saját (alacsonyabb) célja fölött is kér hőt
            st.calling = True
            if st.effective_target < self.frost_temp + FROST_HYSTERESIS:
                st.effective_target = round(self.frost_temp + FROST_HYSTERESIS, 2)
                if current is not None:
                    st.deviation = round(st.effective_target - current, 2)
        self._track_residual(st, was_calling, current, stop_at, now_ts)

        st.valve_open = (
            self._valve_open(st.valve_open or resume, pairs) if st.valve_demand_link else False
        )
        return st

    # ------------------------------------------------------------------ 2.19: kiesés, fagyvédelem, elakadt hőmérő
    def _valve_shift(self, st: RoomStatus, valve_id: str) -> float:
        """A kalibrált szelep mérése szándékosan el van tolva a szoba hőmérőjétől (TRV eltolás): ha a szelep mérése
        helyettesíti a szoba hőmérőjét (elavult, elakadt, megbízhatatlan hőmérő), ennyit kell hozzáadni, hogy a szoba
        hőmérsékletét becsülje. Csak akkor nem nulla, ha a kalibráció be van kapcsolva és ismert, mihez igazította a szelepet."""
        if not (self.cal_enabled and st.calibrate):
            return 0.0
        try:
            cal = self.calibrator.cal.get(valve_id)
        except AttributeError:
            return 0.0
        target = getattr(cal, "target", None)
        if target is None or not math.isfinite(target):
            return 0.0
        return _clamp(target, -TRV_OFFSET_MAX, TRV_OFFSET_MAX)

    def _clear_issue(self, issue_id: str, translation_key: str) -> bool:
        """Törli a Javítások-üzenetet, ha aktív volt (és csak akkor: a soha nem jelzett hibát nem kell törölni). Igaz, ha törölt."""
        if not self._issue_state.get(issue_id):
            return False
        self._sync_issue(issue_id, False, translation_key, {})
        return True

    def _track_targets(self, st: RoomStatus, targets: list[float], reachable: int, now_ts: float) -> None:
        """Megjegyzi a szoba utolsó ismert célját, és azt, mióta nem érhető el egyetlen szelepe sem."""
        if targets:
            target = max(targets)
            if LAST_TARGET_MIN <= target <= LAST_TARGET_MAX and (
                st.last_target is None or abs(st.last_target - target) > 0.01
            ):
                st.last_target = target
                self._delay_save(60)
            st.lost_since = None
        elif reachable == 0 and st.valves:
            if st.lost_since is None:
                st.lost_since = now_ts
        else:
            st.lost_since = None  # elérhető, de kikapcsolt szelep(ek): az a felhasználó döntése

    def _set_fallback(self, st: RoomStatus, active: bool) -> None:
        """A "szelepek nem elérhetők, a szoba hőmérője vezérel" állapot váltása: Javítások-üzenet, napló, esemény."""
        if active == st.fallback:
            return
        st.fallback = active
        st.fb_since = st.fb_temp = None
        st.fb_rest_until = 0.0
        st.fallback_paused = False
        issue_id = f"valves_unreachable_{self.entry_id}_{st.room_id}"
        if active:
            minutes = f"{VALVE_LOST_GRACE_SECONDS // 60}"
            self._sync_issue(
                issue_id,
                True,
                "valves_unreachable",
                {"room": st.name, "minutes": minutes, "target": f"{st.last_target:g}"},
                message=(
                    f"{st.name}: a szoba szelepei {minutes} perce nem elérhetők; a fűtést a szoba hőmérője és az utolsó "
                    f"ismert cél ({st.last_target:g} °C) alapján folytatom"
                ),
            )
            self._tlog(
                "%s: a szelepek nem elérhetők, a hőigény a szoba hőmérőjéből és az utolsó ismert célból (%s °C) megy tovább",
                st.name,
                f"{st.last_target:g}",
            )
            self._emit("valves_unreachable", st, target_temperature=st.last_target)
        else:
            self._clear_issue(issue_id, "valves_unreachable")
            self._tlog("%s: a szelepek újra elérhetők (vagy a tartalék vezérlés feltétele megszűnt)", st.name)
            self._emit("valves_reachable", st)

    def _fallback_stalled(self, st: RoomStatus, current: float | None, now_ts: float) -> bool:
        """Igaz, ha a tartalék vezérlés hőigénye most szünetel, mert a szoba a fűtés ellenére sem melegszik.

        Elérhetetlen szelepnél nem tudjuk, nyitva van-e. Ha a hub esett ki, a szelep a saját beállítása szerint szabályoz, a
        szoba melegszik, és minden rendben. Ha viszont a szelep zárva maradt (lemerült az eleme, elakadt), a szoba hőmérője
        a végtelenségig hőt kérne, a kazán pedig hiába járna. Ezért a hőt kérő szobának járó kazán mellett
        `FALLBACK_STALL_SECONDS` időn belül legalább `FALLBACK_MIN_RISE` fokot melegednie kell (minden emelkedés új ablakot
        nyit); különben a hőigénye `FALLBACK_REST_SECONDS` időre szünetel, utána újra próbálja. A fagyvédelem ettől
        független. Ha a kazán nem megy (például a parancsa hibázik), nincs mit megítélni."""
        if now_ts < st.fb_rest_until:
            return True
        if not st.calling or current is None:
            st.fb_since = st.fb_temp = None
            return False
        on_since = self._boiler_on_since()
        if on_since is None:
            st.fb_since = st.fb_temp = None
            return False
        if st.fb_since is None or st.fb_temp is None or current >= st.fb_temp + FALLBACK_MIN_RISE - 1e-9:
            st.fb_since, st.fb_temp = now_ts, current  # új megfigyelési ablak (az elején, vagy mert a szoba melegedett)
            return False
        if now_ts - max(st.fb_since, on_since) < FALLBACK_STALL_SECONDS:
            return False
        st.fb_rest_until = now_ts + FALLBACK_REST_SECONDS
        self._tlog(
            "%s: a szelepek nem elérhetők, és a szoba %s fűtés alatt sem melegedett (%s -> %s °C; a szelep zárva maradhatott): "
            "a szoba hőigénye %s időre szünetel, utána újra próbálom",
            st.name,
            trvlog.duration(FALLBACK_STALL_SECONDS),
            trvlog.num(st.fb_temp),
            trvlog.num(current),
            trvlog.duration(FALLBACK_REST_SECONDS),
        )
        self._emit(
            "fallback_paused",
            st,
            current_temperature=round(current, 1),
            hours=round(FALLBACK_REST_SECONDS / 3600, 1),
        )
        st.fb_since = st.fb_temp = None
        return True

    def _update_frost(
        self,
        st: RoomStatus,
        sensor_value: float | None,
        raw_sensor: float | None,
        valve_reads: list[float],
        now_ts: float,
    ) -> bool:
        """Fagyvédelem: igaz, ha a szobának a szelep állapotától függetlenül hőt kell kérnie.

        A megbízható szoba hőmérő dönt; ennek hiányában a szelepek nyers mérése és a szoba hőmérőjének nyers értéke
        együtt (az 1 °C alatti értéket a hihetőségi szűrő hibának veszi, de fagynál éppen ilyen jön): fagy csak akkor,
        ha MINDEN elérhető mérés a küszöb alatt van, így egyetlen hibaérték nem indít fűtést. A küszöb alatti állapotnak
        `FROST_CONFIRM_SECONDS` ideig fenn kell állnia; a fagyvédelem a küszöb + `FROST_HYSTERESIS` elérésekor enged el.
        Ha közben minden mérés eltűnik, a jelzés megmarad (hideg volt, és nincs bizonyíték, hogy már nincs)."""
        if self.frost_temp <= 0:
            if st.frost:
                self._set_frost(st, False, None)
            st.frost_since = None
            return False
        if sensor_value is not None:
            readings = [sensor_value]
        else:
            readings = list(valve_reads)
            if (
                raw_sensor is not None
                and math.isfinite(raw_sensor)
                and FROST_READING_MIN <= raw_sensor <= SENSOR_TEMP_MAX
            ):
                readings.append(raw_sensor)
        if not readings:
            return st.frost  # nincs mérés: a meglévő állapot marad
        warmest = max(readings)
        if st.frost:
            if warmest >= self.frost_temp + FROST_HYSTERESIS:
                self._set_frost(st, False, warmest)
                st.frost_since = None
        elif warmest < self.frost_temp:
            if st.frost_since is None:
                st.frost_since = now_ts
            if now_ts - st.frost_since >= FROST_CONFIRM_SECONDS:
                self._set_frost(st, True, warmest)
        else:
            st.frost_since = None
        return st.frost

    def _set_frost(self, st: RoomStatus, active: bool, value: float | None) -> None:
        st.frost = active
        issue_id = f"frost_{self.entry_id}_{st.room_id}"
        if active:
            self._sync_issue(
                issue_id,
                True,
                "frost_protection",
                {
                    "room": st.name,
                    "temperature": "?" if value is None else f"{value:.1f}",
                    "threshold": f"{self.frost_temp:g}",
                    "target": f"{self.frost_temp + FROST_HYSTERESIS:g}",
                },
                message=(
                    f"{st.name}: fagyvédelem: a szoba {'?' if value is None else f'{value:.1f}'} °C "
                    f"(a küszöb {self.frost_temp:g} °C); a szoba hőt kér, a szelepeit fűtésre kapcsolom"
                ),
            )
            self._tlog(
                "%s: FAGYVÉDELEM – a szoba %s °C, a küszöb %s °C; a szoba a szelep állapotától függetlenül hőt kér",
                st.name,
                "?" if value is None else f"{value:.1f}",
                f"{self.frost_temp:g}",
            )
            self._emit("frost_protection_started", st, temperature=value, threshold=self.frost_temp)
        else:
            self._clear_issue(issue_id, "frost_protection")
            self._tlog("%s: a fagyvédelem véget ért%s", st.name, "" if value is None else f" (a szoba {value:.1f} °C)")
            self._emit("frost_protection_ended", st, temperature=value)

    def _boiler_on_since(self) -> float | None:
        """Mióta megy megszakítás nélkül a kazán (epoch); None, ha nem megy vagy nem ismert."""
        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, HVACMode.OFF):
            return None
        changed = getattr(boiler, "last_changed", None)
        return changed.timestamp() if changed is not None else None

    def _companion_alive(self, room: dict[str, Any], now_ts: float) -> bool:
        """Él-e a szoba hőmérőjének eszköze: ha az eszköz bármelyik másik entitása (páratartalom, elem, jelerősség) az elmúlt
        `SENSOR_STUCK_SECONDS` időben jelentett, az eszköz működik, a hőmérséklet tényleg nem változott. A szoba űrlapján
        megadott páramérő csak akkor számít, ha ugyanazon az eszközön van (más eszköz nem bizonyítja, hogy a hőmérő él)."""
        temp_id = room.get(CONF_ROOM_TEMP)
        if not temp_id:
            return False
        siblings = self._companion.get(temp_id)
        if siblings is None:
            siblings = []
            try:
                registry = er.async_get(self.hass)
                entry = registry.async_get(temp_id)
                device = getattr(entry, "device_id", None) if entry is not None else None
                if device:
                    siblings = [
                        item.entity_id
                        for item in er.async_entries_for_device(registry, device)
                        if item.entity_id != temp_id
                    ]
            except Exception:  # noqa: BLE001 - a nyilvántartás hibája nem állíthatja le a vezérlést
                siblings = []
            self._companion[temp_id] = siblings
        for entity_id in siblings:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            reported = self._reported_ts(entity_id)
            if reported is not None and now_ts - reported < SENSOR_STUCK_SECONDS:
                return True
        return False

    def _check_stuck(
        self, st: RoomStatus, room: dict[str, Any], sensor_value: float | None, now_ts: float
    ) -> bool:
        """Elakadt-e a szoba hőmérője: a szoba hőt kér, a kazán megy, és a hőmérő `SENSOR_STUCK_SECONDS` ideje nem jelentett.

        A fűtött szobában a hőmérsékletnek változnia kell. Egy a cél alatti értéken ragadt hőmérő (lemerülő elem, hálózati
        hiba úgy, hogy az entitás nem válik elérhetetlenné) a beállított elavulási időig (alapból 6 óra) járatná a kazánt.
        Ha a hőmérő eszközének egy másik entitása (páratartalom, elem) közben jelentett, az eszköz él: a hőmérséklet tényleg
        áll (gyengén fűtő radiátor), ez nem elakadás. Az elakadt hőmérő helyett a szelepek mérése vezérel, amíg a hőmérő újra
        nem jelent. Igaz, ha a hőmérő most elakadtnak számít."""
        temp_id = st.temp_sensor
        if not temp_id or sensor_value is None:
            if st.sensor_stuck and not temp_id:
                self._set_stuck(st, False, 0.0)
            return st.sensor_stuck and bool(temp_id)
        reported = self._reported_ts(temp_id)
        if st.sensor_stuck:
            if reported is not None and reported > st.stuck_ref + 0.5:
                self._set_stuck(st, False, reported)  # új jelentés érkezett
                return False
            return True
        if reported is None or now_ts - reported < SENSOR_STUCK_SECONDS:
            return False
        if not st.calling or st.call_since is None or now_ts - st.call_since < SENSOR_STUCK_SECONDS:
            return False
        on_since = self._boiler_on_since()
        if on_since is None or now_ts - on_since < SENSOR_STUCK_SECONDS:
            return False
        if self._companion_alive(room, now_ts):
            return False
        self._set_stuck(st, True, reported)
        return True

    def _set_stuck(self, st: RoomStatus, active: bool, reported: float) -> None:
        st.sensor_stuck = active
        temp_id = st.temp_sensor or ""
        issue_id = f"stuck_room_{self.entry_id}_{st.room_id}"
        minutes = f"{SENSOR_STUCK_SECONDS // 60}"
        if active:
            st.stuck_ref = reported
            self._sync_issue(
                issue_id,
                True,
                "stuck_room_temp",
                {"room": st.name, "sensor": temp_id, "minutes": minutes},
                message=(
                    f"{st.name}: a szoba hőmérő ({temp_id}) fűtés közben {minutes} perce nem jelentett; "
                    "a szelepek saját mérésére váltok, amíg újra nem jelent"
                ),
            )
            self._emit("sensor_stuck", st, sensor=temp_id, minutes=SENSOR_STUCK_SECONDS // 60)
        else:
            self._clear_issue(issue_id, "stuck_room_temp")
            self._tlog("%s: a szoba hőmérő (%s) újra jelent", st.name, temp_id)
            self._emit("sensor_unstuck", st, sensor=temp_id)

    # ------------------------------------------------------------------ maradékhő (2.13)
    def _reset_residual(self, st: RoomStatus) -> None:
        st.resid_run = None
        st.call_since = st.call_target = None
        st.call_clean = False
        st.stop_lead = 0.0

    def _stop_lead(self, st: RoomStatus) -> float:
        """Mennyivel állítsa le előbb a szoba hőigényét a tanult maradékhő miatt (°C, 0 = nem).

        Csak a megengedett túllövés fölötti részt kompenzálja, legfeljebb `RESIDUAL_LEAD_MAX`-ot, és csak
        akkor, ha a kompenzáció be van kapcsolva, elég mérés van, a szoba hőmérője megbízható, és nincs
        "Fűts most" / előfűtés (azoknál a megemelt cél a kért viselkedés).
        """
        self._expire_residual(st)
        learned = st.residual
        if (
            not self.residual_comp
            or learned is None
            or st.source != "sensor"
            or st.sensor_unusable
            or st.manual_until is not None
            or st.preheat_active
        ):
            return 0.0
        lead = min(learned - self.residual_allow, RESIDUAL_LEAD_MAX)
        if lead < RESIDUAL_LEAD_MIN - 1e-9:  # a lebegőpontos zaj ne döntsön a határon (0,3 - 0,2 = 0,0999…)
            return 0.0
        return round(round(lead / RESIDUAL_LEAD_STEP) * RESIDUAL_LEAD_STEP, 2)

    def _expire_residual(self, st: RoomStatus) -> None:
        """2.19: a 30 napnál régebbi mérések kiesnek (az évszakkal a radiátor és a szoba viselkedése is változik)."""
        if not st.resid_samples:
            return
        if len(st.resid_times) != len(st.resid_samples):  # nem lehet eltérő hosszú (védekezés): mind mostaninak számít
            st.resid_times = [dt_util.utcnow().timestamp()] * len(st.resid_samples)
            return
        cutoff = dt_util.utcnow().timestamp() - RESIDUAL_SAMPLE_MAX_AGE
        if st.resid_times[0] >= cutoff:
            return  # a legrégebbi is elég friss (a lista időrendben van)
        keep = [index for index, ts in enumerate(st.resid_times) if ts >= cutoff]
        st.resid_samples = [st.resid_samples[index] for index in keep]
        st.resid_times = [st.resid_times[index] for index in keep]
        self._delay_save(60)

    def _residual_grace(self) -> float:
        """2.19: a hőigény megszűnése után a kazán ennyi ideig járhat még úgy, hogy a mérés érvényes marad: a kapcsolási
        késleltetés (a minimális kapcsolási idő, bekapcsolt ciklusvédelemnél a minimális bekapcsolt idő is) + 2 perc,
        legfeljebb 15 perc. Ennél tovább csak egy másik szoba miatt jár, és az a nyitott szelepen át ezt a szobát is fűti."""
        hold = self.min_switch.total_seconds()
        if self.cycle_protection:
            hold = max(hold, self.boiler_min_on.total_seconds())
        return min(hold + RESIDUAL_BOILER_GRACE_EXTRA, RESIDUAL_BOILER_GRACE_SECONDS)

    def _residual_clean(self, st: RoomStatus, current: float | None) -> bool:
        """Tiszta-e most a mérés feltétele: megbízható szoba hőmérő, nincs ablaknyitás (sem függő),
        nyári mód, "Fűts most" vagy előfűtés."""
        return (
            current is not None
            and st.source == "sensor"
            and not st.sensor_unusable
            and not st.window_open
            and st.window_open_since is None
            and not self.summer_active
            and st.manual_until is None
            and not st.preheat_active
            and not st.fallback  # 2.19: tartalék vezérlés (elérhetetlen szelepek) és fagyvédelem alatt nem mérünk
            and not st.frost
        )

    def _track_residual(
        self,
        st: RoomStatus,
        was_calling: bool,
        current: float | None,
        stop_at: float,
        now_ts: float,
    ) -> None:
        """A maradékhő mérése: mennyit melegszik még a szoba, miután a hőigénye megszűnt.

        Ha a hőigény természetes módon ért véget (a szoba elérte a leállási küszöböt, közben nem változott
        a szelepek célja, nem volt ablaknyitás, "Fűts most" vagy előfűtés), a mérés elindul: a szoba
        hőmérőjének csúcsát keresi a leállás utáni órában. Érvényes, ha a kazán közben tényleg leállt és
        nem indult újra (különben más szoba fűtése is hozzátesz), és a csúcs elmúlt. Az utolsó
        `RESIDUAL_KEEP` mérés mediánja a tanult érték.
        """
        clean = self._residual_clean(st, current)
        if st.resid_run is not None:
            self._step_residual_run(st, current, now_ts)
        if st.calling:
            if not was_calling or st.call_since is None:
                st.call_since, st.call_target, st.call_clean = now_ts, st.target, True
            if not clean or abs((st.target or 0.0) - (st.call_target or 0.0)) >= RESIDUAL_TARGET_TOLERANCE:
                st.call_clean = False
            return
        if not was_calling:
            return
        # a hőigény éppen megszűnt
        natural = (
            st.call_clean
            and clean
            and st.call_since is not None
            and now_ts - st.call_since >= RESIDUAL_MIN_ON_SECONDS
            and current >= stop_at - 1e-9
            and st.call_target is not None
            and abs(st.target - st.call_target) < RESIDUAL_TARGET_TOLERANCE
        )
        st.call_since = st.call_target = None
        st.call_clean = False
        if natural:
            st.resid_run = {
                "t0": now_ts,
                "base": current,
                "peak": current,
                "peak_ts": now_ts,  # 2.19: mikor érte el (először) a legmagasabb értéket
                "target": st.target,
                "off": False,
            }

    def _step_residual_run(self, st: RoomStatus, current: float | None, now_ts: float) -> None:
        run = st.resid_run
        if run is None:
            return
        elapsed = now_ts - run["t0"]
        if not self._residual_clean(st, current) or abs(st.target - run["target"]) >= RESIDUAL_TARGET_TOLERANCE:
            st.resid_run = None  # zavaró körülmény: a mérés nem tiszta
            return
        boiler_on = self._boiler_is_on()
        if boiler_on is None or (boiler_on and (run["off"] or elapsed > self._residual_grace())):
            st.resid_run = None  # a kazán nem állt le, vagy újra fűt (más szoba is melegít): nem tiszta
            return
        if not boiler_on:
            run["off"] = True
        if current > run["peak"] + 1e-9:
            run["peak"], run["peak_ts"] = current, now_ts
        peak_passed = elapsed >= RESIDUAL_MIN_WINDOW_SECONDS and current <= run["peak"] - RESIDUAL_FALL + 1e-9
        if not (elapsed >= RESIDUAL_WINDOW_SECONDS or peak_passed):
            if st.calling:
                st.resid_run = None  # a szoba újra fűt, mielőtt a csúcs elmúlt volna
            return
        st.resid_run = None
        if not run["off"]:
            return
        if not peak_passed and run.get("peak_ts", run["t0"]) - run["t0"] > RESIDUAL_PEAK_MAX_SECONDS:
            # 2.19: nincs visszaesés, és a szoba az ablak utolsó negyedórájában is melegedett: ez nem (csak) a radiátor
            # maradékhője (napsütés, főzés), a mérés nem tiszta
            self._tlog(
                "%s: maradékhő mérés elvetve: a szoba a leállás után %d perccel is melegedett (más hőforrás)",
                st.name,
                round((run.get("peak_ts", run["t0"]) - run["t0"]) / 60),
            )
            return
        self._add_residual_sample(st, run["peak"] - run["base"])

    def _add_residual_sample(self, st: RoomStatus, rise: float) -> None:
        sample = round(_clamp(rise, 0.0, RESIDUAL_SAMPLE_MAX), 2)
        if len(st.resid_times) != len(st.resid_samples):
            st.resid_times = [dt_util.utcnow().timestamp()] * len(st.resid_samples)
        st.resid_samples.append(sample)
        st.resid_times.append(dt_util.utcnow().timestamp())
        del st.resid_samples[:-RESIDUAL_KEEP]
        del st.resid_times[:-RESIDUAL_KEEP]
        learned = st.residual
        self._tlog(
            "%s: maradékhő mérés: +%.2f °C a hőigény megszűnése után (tanult: %s, %d mérés)",
            st.name,
            sample,
            "még nincs elég mérés" if learned is None else f"{learned:.2f} °C",
            len(st.resid_samples),
        )
        self._delay_save(60)

    def _boiler_is_on(self) -> bool | None:
        """A kazán állapota: True (be), False (ki), None (ismeretlen / nem elérhető)."""
        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        return boiler.state != HVACMode.OFF

    def _seed_active(self, st: RoomStatus) -> bool:
        """Indítás után, szobánként egyszer: igaz, ha a kazán már fűt.

        A hőigény hiszterézisének állapota (fűtünk-e még a cél eléréséig) csak a memóriában él.
        Hogy a kazán újraindítás után ne kapcsoljon ki idő előtt, a fűtő kazán mellett az első
        értékeléskor a céltól elmaradó szobát hőt kérőnek vesszük, mintha az előző körben is az
        lett volna. Csak az indítás utáni első percekben él, később nem változtat semmit.
        """
        if st.room_id in self._seeded:
            return False
        on = self._boiler_is_on()
        if on is None:
            return False  # a kazán állapota még nem ismert: később újra megpróbáljuk
        self._seeded.add(st.room_id)
        return on and dt_util.utcnow().timestamp() - self._start_ts <= RESUME_WINDOW_SECONDS

    def _emit_stale(self, st: RoomStatus | None, sensor: str | None, stale: bool) -> None:
        extra: dict[str, Any] = {"sensor": sensor}
        if stale:
            reported = self._reported_ts(sensor)
            if reported is not None:
                extra["age_minutes"] = round((dt_util.utcnow().timestamp() - reported) / 60)
        if st is None:
            extra["outdoor"] = True
        self._emit("sensor_stale" if stale else "sensor_recovered", st, **extra)

    def _update_trend(self, st: RoomStatus) -> None:
        """A szoba hőmérsékletének változási sebessége (°C/óra) az utolsó ~30 percből.

        Csak kijelzésre szolgál (kártyák), a vezérlést nem befolyásolja.
        """
        if st.current is None:
            st.trend_samples.clear()
            st.trend = None
            st.trend_source = None
            return
        now_ts = dt_util.utcnow().timestamp()
        if st.trend_source != st.source:  # más forrás: más mérés, nem keverjük össze
            st.trend_samples.clear()
            st.trend_source = st.source
        samples = st.trend_samples
        if not samples or now_ts - samples[-1][0] >= TREND_SAMPLE_SECONDS:
            samples.append((now_ts, st.current))
        cutoff = now_ts - TREND_WINDOW_SECONDS
        while samples and samples[0][0] < cutoff:
            samples.popleft()
        st.trend = _stable_trend(st.trend, _slope_per_hour(samples))

    def room_times(self, st: RoomStatus) -> dict[str, float | None]:
        """A kártyák visszaszámlálóihoz: mikor történik a következő esemény (epoch)."""
        waiting = st.cold_since is not None and not st.boost_wanted
        return {
            "boost_starts_at": st.cold_since + st.boost_delay_s if waiting else None,
            "boost_rest_until": st.rest_until,
            "boost_max_until": (
                st.boost_started + self.max_boost_seconds
                if st.boost_wanted and self.max_boost_enabled and st.boost_started is not None
                else None
            ),
            "window_pending_until": (
                st.window_open_since + st.window_delay_s
                if st.window_open_since is not None and not st.window_open
                else None
            ),
        }

    # ------------------------------------------------------------------ kiértékelés
    async def async_evaluate(self) -> None:
        async with self._lock:
            # a kör elindult: az ezután érkező állapotváltozás már új kört kér (lásd `_handle_event`)
            self._eval_queued = False
            if self._stopped:
                return  # leállított (újratöltött) vezérlő: nem értékel és nem ír
            try:
                await self._async_evaluate()
            finally:
                self._events_armed = True  # az első kiértékelés után már küldhetünk eseményt
                self._notify()

    def _writes_allowed(self, now_ts: float) -> bool:
        """Írhat-e a vezérlő (szelep, kazán)? Nem, amíg a HA indul vagy leáll.

        Indulás közben az entitások (Meross LAN, szenzorok) még töltődnek, a hiányos adatból hozott
        döntés (például egy még be nem töltött szoba) feleslegesen kikapcsolná a kazánt vagy
        átállítaná a szelepeket. Ezért a vezérlő olvas és számol, de a HA elindulása után még
        `STARTUP_SETTLE_SECONDS` másodpercig nem ír. Futó HA-ban (újratöltés) nincs várakozás.
        """
        if getattr(self.hass, "is_stopping", False):
            return False
        if not getattr(self.hass, "is_running", True):
            self._ready_since = None
            return False
        if self._boot_hold:
            if self._ready_since is None:
                self._ready_since = now_ts
            remaining = STARTUP_SETTLE_SECONDS - (now_ts - self._ready_since)
            if remaining > 0:
                # 2.16.1: a tartás végén azonnal értékel, nem a következő egyperces kört várja (indulás után a felhasználó
                # perceket vár arra, hogy a plugin megmozdítsa a szelepeket)
                self._schedule_retry(timedelta(seconds=remaining))
                return False
            self._boot_hold = False
        return True

    async def _async_evaluate(self) -> None:
        allow = self._writes_allowed(dt_util.utcnow().timestamp())
        self._update_outdoor()
        statuses = [self._update_room(room) for room in self.rooms]

        if self.summer_active:
            for st in statuses:
                if not st.frost:  # 2.19: a fagyvédelem a nyári módnál is erősebb (hibás kinti szenzor ne fagyassza le a házat)
                    st.calling = False
        if self.summer_active != self._prev_summer:
            if self.outdoor_avg is None or self.outdoor_stale:
                why = "nincs használható kinti hőmérséklet"
            else:
                why = f"kinti 24 órás átlag: {trvlog.num(self.outdoor_avg)} °C"
                if not self.in_summer_period:
                    why += ", a nyári időszakon kívül"
            self._tlog("Nyári mód %s (%s)", "BEKAPCSOLVA" if self.summer_active else "KIKAPCSOLVA", why)
            self._prev_summer = self.summer_active
            self._delay_save(30)  # újraindítás után is megmarad

        await self._async_control_valves(statuses, allow)
        await self._async_frost_valves(statuses, allow)
        for st in statuses:
            st.boiler_demand = self._room_boiler_demand(st)
        self._observe_boiler()
        self._learn_rates(statuses)

        await self._async_switch_boiler(statuses, allow)
        # A kalibráció a kazán kapcsolása UTÁN fut: egy lassú szelep-parancs nem késleltetheti a kazánt.
        await self.calibrator.async_run(statuses, allow, dt_util.utcnow().timestamp())

    async def _async_switch_boiler(self, statuses: list[RoomStatus], allow: bool) -> None:
        """A szobák hőigénye alapján be- vagy kikapcsolja a kazánt.

        2.19: (1) Ha egyetlen szoba sem értékelhető (nincs elérhető szelep, és a szoba hőmérőjéből + az utolsó ismert
        célból sem megy tartalék vezérlés), a kazánhoz `BLIND_OFF_SECONDS` ideig nem nyúl (rövid kiesés), utána
        kikapcsolja: vakon nem fűt tovább, és ezt a Javítások között jelzi. (2) A parancs eredményét ellenőrzi: a
        sikertelen parancs nem számít kapcsolásnak (nincs naplósor, nincs kapcsolási idő), percenként újra próbálja, és
        ha a kazán termosztátja többször egymás után nem fogadja el vagy nem követi a parancsot, a Javítások között jelez.
        """
        if not statuses:
            return  # nincs szoba: nem nyúlunk a kazánhoz
        now_ts = dt_util.utcnow().timestamp()
        blind_id = f"heating_blind_{self.entry_id}"
        if any(st.reachable or st.fallback or st.frost for st in statuses):
            self._blind_since = None
            if self._clear_issue(blind_id, "heating_blind"):
                self._tlog("Újra van értékelhető szoba, a kazán vezérlése folytatódik")
            demand = any(st.boiler_demand for st in statuses)
        else:
            # egyik szelep sem elérhető, és tartalék vezérlés sincs
            if self._blind_since is None:
                self._blind_since = now_ts
            if now_ts - self._blind_since < BLIND_OFF_SECONDS:
                return  # rövid kiesés: nem nyúlunk a kazánhoz
            minutes = f"{BLIND_OFF_SECONDS // 60}"
            self._sync_issue(
                blind_id,
                True,
                "heating_blind",
                {"minutes": minutes},
                message=(
                    f"Egyik szoba szelepe sem elérhető {minutes} perce, és a szobák hőmérőjéből sem megy tartalék "
                    "vezérlés (nincs hőmérő vagy utolsó ismert cél): a kazánt kikapcsolom, amíg újra nem látok szobát"
                ),
            )
            demand = False

        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        boiler_on = boiler.state != HVACMode.OFF

        if not allow:
            return  # indulás / leállás: a kazánhoz még / már nem nyúlunk

        switching = demand != boiler_on
        if not switching:
            self._boiler_try = None  # a kazán a kívánt állapotban van: az utolsó kapcsolás igazolva
        if now_ts < self._boiler_block_until and (switching or self._boiler_fail):
            # az előző parancs nemrég bukott el (vagy a kazán nem követte): nem ismételjük másodpercenként
            self._schedule_retry(timedelta(seconds=self._boiler_block_until - now_ts))
            return
        repeat = False
        if switching:
            remaining = self._switch_wait_remaining(demand)
            if remaining is not None and remaining > timedelta(0):
                self._schedule_retry(remaining)
                return
            # ugyanebbe az irányba már ment (sikeres) parancs, és a kazán azóta sem váltott át
            repeat = self._boiler_try is not None and self._boiler_try[0] == demand
            if repeat and now_ts - self._boiler_try[1] < BOILER_RETRY_SECONDS:
                self._schedule_retry(timedelta(seconds=BOILER_RETRY_SECONDS - (now_ts - self._boiler_try[1])))
                return

        if demand:
            ok = await self._async_ensure_on(boiler)
        elif boiler_on:
            ok = await self._call("set_hvac_mode", hvac_mode=HVACMode.OFF, _warn=self._boiler_fail == 0)
        else:
            ok = True  # nincs hőigény, a kazán áll: nincs teendő

        if not ok or repeat:
            self._boiler_fail += 1
        elif not switching:
            self._boiler_fail = 0  # a kazán a kívánt állapotban van, és a parancs (ha kellett) sikerült
        if not ok:
            self._boiler_block_until = now_ts + BOILER_RETRY_SECONDS
            self._schedule_retry(timedelta(seconds=BOILER_RETRY_SECONDS))
        self._sync_boiler_issue(demand)
        if not ok or not switching:
            return

        self._boiler_try = (demand, now_ts)
        self._last_switch = dt_util.utcnow()
        if repeat:
            self._tlog(
                "Kazán %s parancs megismételve (a kazán termosztátja az előző parancs után nem váltott át)",
                "BE" if demand else "KI",
            )
            return
        self._tlog(
            "Kazán %s (%s)",
            "BE" if demand else "KI",
            (
                "hőt kérő szobák: "
                + ", ".join(st.name for st in statuses if st.boiler_demand)
                if demand
                else "nyári mód" if self.summer_active
                else "nincs értékelhető szoba" if self._blind_since is not None
                else "nincs hőigény"
            ),
        )

    def _sync_boiler_issue(self, demand: bool) -> None:
        """Javítások-üzenet, ha a kazán termosztátja többször egymás után nem fogadta el vagy nem követte a parancsot."""
        issue_id = f"boiler_command_{self.entry_id}"
        if self._boiler_fail >= BOILER_FAIL_ISSUE_AFTER:
            if not self._issue_state.get(issue_id):
                self._sync_issue(
                    issue_id,
                    True,
                    "boiler_command_failed",
                    {"boiler": self.boiler, "count": f"{self._boiler_fail}"},
                    message=(
                        f"A kazán termosztátja ({self.boiler}) egymás után {self._boiler_fail} alkalommal nem fogadta el "
                        f"vagy nem követte a parancsot (a kívánt állapot: {'BE' if demand else 'KI'}); percenként újra próbálom"
                    ),
                )
                self._emit("boiler_command_failed", None, boiler=self.boiler, wanted="on" if demand else "off")
        elif self._boiler_fail == 0 and self._clear_issue(issue_id, "boiler_command_failed"):
            self._tlog("A kazán termosztátja (%s) újra követi a parancsokat", self.boiler)

    def _switch_wait_remaining(self, turning_on: bool) -> timedelta | None:
        """Mennyi ideig kell még várni a kazán következő kapcsolásáig (None: nincs korlát).

        Alapból a "minimális kapcsolási idő" számít az utolsó kapcsolástól. Ha a ciklus-védelem
        be van kapcsolva, a kazán minimális be- / kikapcsolt ideje is (a megfigyelt váltásoktól,
        így újraindítás után és külső kapcsolásnál is).
        """
        refs: list[datetime] = []
        if self._last_switch is not None:
            refs.append(self._last_switch + self.min_switch)
        else:
            # újraindítás / újratöltés után a plugin saját utolsó kapcsolását nem ismeri: a mentett
            # ciklusnaplóból tudjuk, mikor váltott utoljára a kazán (csak biztosan ismert váltás)
            known_change = self.cycles.last_known_change()
            if known_change is not None:
                refs.append(
                    datetime.fromtimestamp(known_change, tz=timezone.utc) + self.min_switch
                )
        if self.cycle_protection:
            wait = self.boiler_min_off if turning_on else self.boiler_min_on
            if self._last_switch is not None:
                refs.append(self._last_switch + wait)
            last = self.cycles.last_change()
            if last is not None:
                refs.append(datetime.fromtimestamp(last, tz=timezone.utc) + wait)
        if not refs:
            return None
        return max(refs) - dt_util.utcnow()

    def _account_gas(self, is_on: bool, event_ts: float, now_ts: float) -> None:
        """Becsült gázfogyasztás: a kazán bekapcsolt ideje × a beállított m³/óra.

        Becslés, nem mérés: a kazán működés közben modulál, ezért az érték gázóra nélkül csak
        közelítő. Újraindítás, elérhetetlen kazán vagy hosszabb kihagyás alatt nem számol (a
        kihagyott időt nem pótolja), hogy ne legyen túlbecslés.
        """
        if not self.gas_enabled:
            self._gas_last_ts = None
            self._gas_last_on = None
            return
        last_ts, last_on = self._gas_last_ts, self._gas_last_on
        on_seconds = 0.0
        if last_ts is not None and last_on is not None and 0 <= now_ts - last_ts <= GAS_MAX_GAP_SECONDS:
            if is_on == last_on:
                if is_on:
                    on_seconds = now_ts - last_ts
            else:
                # váltás az utolsó elszámolás óta: a határ a váltás valódi ideje
                boundary = min(max(event_ts, last_ts), now_ts)
                on_seconds = (boundary - last_ts) if last_on else (now_ts - boundary)
        if on_seconds > 0:
            self.gas_m3 += on_seconds / 3600 * self.gas_m3_per_hour
            if now_ts - self._gas_saved_ts >= GAS_SAVE_SECONDS:
                self._gas_saved_ts = now_ts
                self._delay_save(5)
        self._gas_last_ts, self._gas_last_on = now_ts, is_on

    @property
    def gas_boiler_on(self) -> bool | None:
        """A kazán állapota az utolsó elszámoláskor (None: még nem látott / kihagyott)."""
        return self._gas_last_on

    def _observe_boiler(self) -> None:
        """A kazán be/ki váltásainak naplózása; gyakori kapcsolgatás figyelése."""
        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self._gas_last_ts = None  # kihagyott időre nem számolunk fogyasztást
            self._gas_last_on = None
            return
        now_ts = dt_util.utcnow().timestamp()
        # a váltás valódi ideje (az állapot utolsó változása), hogy a késve észlelt váltás se csússzon el
        changed = getattr(boiler, "last_changed", None)
        event_ts = changed.timestamp() if changed is not None else now_ts
        event_ts = min(max(event_ts, self.cycles.last_change() or 0.0), now_ts)
        if self.cycles.observe(boiler.state != HVACMode.OFF, event_ts):
            self._delay_save(600)
        self._account_gas(boiler.state != HVACMode.OFF, event_ts, now_ts)
        self.cycle_info = self.cycles.stats(now_ts)
        was = self.short_cycling
        self.short_cycling = self.cycle_monitor and self.cycles.is_short_cycling(
            self.cycle_info, self.cycle_max_starts, self.cycle_min_avg_on
        )
        if self.short_cycling and not was:
            _LOGGER.warning(
                "Gyakori kazán kapcsolgatás: %s indítás az utolsó órában, átlagos bekapcsolt idő %s perc",
                self.cycle_info["starts_last_hour"],
                self.cycle_info["avg_on_minutes"],
            )
            self._emit(
                "short_cycling",
                None,
                starts_last_hour=self.cycle_info["starts_last_hour"],
                avg_on_minutes=self.cycle_info["avg_on_minutes"],
            )

    # ------------------------------------------------------------------ szelep szabályzás
    @staticmethod
    def _valve_target(state: State) -> float | None:
        try:
            return float(state.attributes["temperature"])
        except (KeyError, TypeError, ValueError):
            return None

    def _user_target(self, valve_id: str, raw: float) -> float:
        """A szelep "valódi" célja: a mi emelésünk alatt az eredeti érték."""
        rec = self._boosts.get(valve_id)
        if rec and abs(raw - rec["boost"]) <= BOOST_TOLERANCE:
            return rec["original"]
        cut = self._cuts.get(valve_id)  # 2.19: a szelep-zárás alatt is az eredeti cél a szoba célja
        if cut and abs(raw - cut["cut"]) <= BOOST_TOLERANCE:
            return cut["original"]
        return raw

    async def _async_save(self) -> None:
        self._save_due = None  # az azonnali mentés a függő késleltetett mentést is kiváltja (a HA törli az időzítőjét)
        await self._store.async_save(self._data_to_save())

    def _mono(self) -> float:
        """Egyenletesen járó óra (a HA eseményhurkáé, ugyanaz, amivel a Store időzít); nem a falióra."""
        loop = getattr(self.hass, "loop", None)
        try:
            return float(loop.time()) if loop is not None else time.monotonic()
        except Exception:  # noqa: BLE001
            return time.monotonic()

    def _delay_save(self, delay: float) -> None:
        """Késleltetett mentés kérése úgy, hogy egy későbbi kérés ne tolhassa ki a korábbit (2.19).

        A HA `Store.async_delay_save` hívásánál az utolsó hívás határideje dönt: ha egy 60 másodperces kérés után egy
        600 másodperces érkezik, az írás 600 másodperccel későbbre tolódik. A ritka, hosszú késleltetésű kérések (kinti minták
        5 percenként, ciklusnapló) így a végtelenségig kitolhatták a tanult adatok mentését, és azok áramszünetnél vagy
        lefagyásnál elvesztek (szabályos leálláskor a HA kiírja őket). Ezért a vezérlő maga tartja nyilván a legkorábbi
        határidőt, és a Store-nak csak akkor szól újra, ha az új kérés ennél korábbi; az írás mindig a friss adatot menti.
        """
        now = self._mono()
        due = now + max(float(delay), 0.0)
        pending = self._save_due
        if pending is not None and now < pending <= due:
            return  # már vár egy nem későbbi mentés
        self._save_due = due
        self._store.async_delay_save(self._delayed_data, max(due - now, 0.0))

    def _delayed_data(self) -> dict[str, Any]:
        """A késleltetett mentés adata (a Store az írás pillanatában hívja): a függő határidő ezzel teljesült."""
        self._save_due = None
        return self._data_to_save()

    async def _async_drop_boost(self, valve_id: str) -> None:
        self._boosts.pop(valve_id, None)
        await self._async_save()

    async def _async_control_valves(
        self, statuses: list[RoomStatus], allow: bool = True
    ) -> None:
        """A szoba hőmérője alapján teljesen kinyitja / visszaállítja a szelepeket.

        `allow` hamis (a HA indul vagy leáll): a döntés elkészül, de a szelepekhez nem nyúlunk.
        """
        want: dict[str, bool] = {}
        now_ts = dt_util.utcnow().timestamp()
        for room in self.rooms:
            st = self.status[room[CONF_ROOM_ID]]
            was, started = st.boost_wanted, st.boost_started
            boost = self._room_wants_boost(st, now_ts)
            if boost != was:
                self._emit_boost(st, boost, started, now_ts)
            for valve_id in room[CONF_ROOM_VALVES]:
                want[valve_id] = boost
        # kikapcsolt / törölt vezérlésű szelepek: a korábbi emelést vissza kell állítani
        for valve_id in list(self._boosts):
            want.setdefault(valve_id, False)

        for valve_id, wanted in want.items():
            try:
                if self.valve_dry_run:
                    if allow and valve_id in self._boosts:
                        await self._async_control_valve(valve_id, False)
                    self._dry_run_valve(valve_id, wanted)
                elif allow:
                    await self._async_control_valve(valve_id, wanted)
            except Exception as err:  # noqa: BLE001 - egy szelep hibája nem állíthatja le a többit és a kazánt
                self._valve_unexpected_error(valve_id, err, now_ts)

        for st in statuses:
            if self.valve_dry_run:
                st.boosted = any(v in self._dry for v in st.valves)
            else:
                st.boosted = any(
                    v in self._boosts and not self._boosts[v]["restoring"]
                    for v in st.valves
                )

        await self._async_control_cuts(statuses, allow, now_ts)

    # ------------------------------------------------------------------ 2.19: szelep-zárás túlfűtés ellen
    def _room_wants_cut(self, st: RoomStatus, now_ts: float, boiler_on: bool | None) -> str | None:
        """Kell-e most a szoba szelepeit lezárni (a céljukat ideiglenesen lejjebb állítani)? None, "over" vagy "window".

        A TRV eltolás miatt a szelep a cél fölött is nyitva maradhat, és az integráció a szelep célját eddig csak emelni
        tudta: ha a kazán egy másik szoba miatt megy, a már meleg szoba is kapta a hőt. A zárás ennek a tükörképe:
        - "over": a szoba hőmérője szerint a szoba legalább `CUT_START_MARGIN` fokkal a (tényleges) cél fölött van, nem kér
          hőt, és a kazán megy; addig tart, amíg a szoba `CUT_RELEASE_MARGIN` fölött marad (hiszterézis);
        - "window": a szoba ablaka (a késleltetés után) nyitva van, és a kazán megy.
        Csak járó kazánnál: álló kazánnál a szelep állása nem számít, és a szelep saját menetrendje addig is érvényesül.
        Egyben legfeljebb `CUT_MAX_SECONDS` ideig tart, utána `CUT_PAUSE_SECONDS` szünet jön: a zárás alatt a szelep kézi
        módban van (a Meross LAN a cél írásakor oda vált), a visszaállítás hozza vissza a menetrendjét, így egy közben
        esedékes menetrendi váltás legfeljebb ennyit késik."""
        active = st.cut_since is not None
        reason: str | None = None
        if st.valve_cut and boiler_on and not self.summer_active and not st.frost and not st.fallback:
            if st.window_open and st.window_sensors:
                reason = "window"
            elif (
                st.source == "sensor"
                and st.current is not None
                and st.effective_target is not None
                and not st.calling
                and not st.sensor_unusable
                and st.manual_until is None
                and not st.preheat_active
            ):
                over = st.current - st.effective_target
                if over >= CUT_START_MARGIN - 1e-9 or (active and over > CUT_RELEASE_MARGIN + 1e-9):
                    reason = "over"
        if reason is None:
            if active:
                st.cut_since = None
                st.cut_pause_until = now_ts + CUT_PAUSE_SECONDS
            return None
        if not active:
            if now_ts < st.cut_pause_until:
                return None
            st.cut_since = now_ts
        elif now_ts - st.cut_since >= CUT_MAX_SECONDS:
            st.cut_since = None
            st.cut_pause_until = now_ts + CUT_PAUSE_SECONDS
            return None
        return reason

    async def _async_control_cuts(self, statuses: list[RoomStatus], allow: bool, now_ts: float) -> None:
        """A szelep-zárások kezelése a szelep-emelés mintájára: előre írt rekord, visszaállítás, hibatűrés."""
        boiler_on = self._boiler_is_on()
        want: dict[str, str | None] = {}
        rooms: dict[str, RoomStatus] = {}
        for st in statuses:
            was = st.cut_reason
            reason = self._room_wants_cut(st, now_ts, boiler_on)
            if reason != was:
                self._note_cut(st, reason, was)
            st.cut_reason = reason
            for valve_id in st.valves:
                want[valve_id] = reason
                rooms[valve_id] = st
        # kikapcsolt funkciójú / törölt szobák szelepei: a korábbi zárást vissza kell állítani
        for valve_id in list(self._cuts):
            want.setdefault(valve_id, None)
        for valve_id in list(self._dry_cut):
            want.setdefault(valve_id, None)

        for valve_id, reason in want.items():
            try:
                if self.valve_dry_run:
                    if allow and valve_id in self._cuts:
                        await self._async_cut_valve(valve_id, None, rooms.get(valve_id))
                    self._dry_run_cut(valve_id, reason)
                else:
                    self._dry_cut.discard(valve_id)
                    if allow:
                        await self._async_cut_valve(valve_id, reason, rooms.get(valve_id))
            except Exception as err:  # noqa: BLE001 - egy szelep hibája nem állíthatja le a többit és a kazánt
                self._valve_unexpected_error(valve_id, err, now_ts)

        for st in statuses:
            if self.valve_dry_run:
                st.cut_active = any(v in self._dry_cut for v in st.valves)
            else:
                st.cut_active = any(v in self._cuts and not self._cuts[v]["restoring"] for v in st.valves)

    def _note_cut(self, st: RoomStatus, reason: str | None, was: str | None) -> None:
        dry = "[PRÓBAÜZEM] " if self.valve_dry_run else ""
        if reason == "over":
            self._tlog(
                "%s%s: szelep-zárás – a szoba %s °C, a cél %s °C, és a kazán más szobának fűt: a nyitott szelepeit lezárom",
                dry,
                st.name,
                trvlog.num(st.current),
                trvlog.num(st.effective_target),
            )
        elif reason == "window":
            self._tlog("%s%s: szelep-zárás – nyitott ablak, és a kazán más szobának fűt: a szelepeit lezárom", dry, st.name)
        else:
            self._tlog("%s%s: szelep-zárás vége", dry, st.name)
        if reason is not None and was is None:
            self._emit(
                "valve_cut_started",
                st,
                reason=reason,
                current_temperature=None if st.current is None else round(st.current, 1),
                target_temperature=st.effective_target,
                dry_run=self.valve_dry_run,
            )
        elif reason is None and was is not None:
            self._emit("valve_cut_ended", st, dry_run=self.valve_dry_run)

    def _dry_run_cut(self, valve_id: str, reason: str | None) -> None:
        was = valve_id in self._dry_cut
        if reason and not was:
            self._dry_cut.add(valve_id)
            self._tlog(
                "[PRÓBAÜZEM] %s: lezárnám (a célhőmérsékletet %s °C-kal lejjebb állítanám)",
                self._valve_label(valve_id),
                f"{CUT_DROP:g}",
            )
        elif not reason and was:
            self._dry_cut.discard(valve_id)
            self._tlog("[PRÓBAÜZEM] %s: visszaállítanám az eredeti célhőmérsékletet", self._valve_label(valve_id))

    async def _async_drop_cut(self, valve_id: str) -> None:
        self._cuts.pop(valve_id, None)
        await self._async_save()

    @staticmethod
    def _valve_seems_closed(state: State, raw: float) -> bool:
        """A szelep a saját jelentése szerint zárva van-e: nem fűt (`hvac_action`), vagy a saját mérése már elérte a célját.
        Ilyenkor a zárásnak nincs mit tennie (felesleges írás és szelepmozgás lenne). Adat hiányában: nem."""
        action = state.attributes.get("hvac_action")
        if action in ("idle", "off"):
            return True
        if action == "heating":
            return False
        try:
            return float(state.attributes["current_temperature"]) >= raw
        except (KeyError, TypeError, ValueError):
            return False

    async def _async_cut_valve(self, valve_id: str, reason: str | None, st: RoomStatus | None) -> None:
        state = self.hass.states.get(valve_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return  # a rekord megmarad: ha a szelep visszajön, visszaállítjuk
        rec = self._cuts.get(valve_id)
        now_ts = dt_util.utcnow().timestamp()
        if state.state == HVACMode.OFF:
            # a felhasználó kikapcsolta a szelepet: a rekord megmarad, mert bekapcsoláskor a lejjebb állított cél jönne
            # vissza; akkor (ha a cél még a zárás értéke) visszaállítjuk
            return
        raw = self._valve_target(state)
        if raw is None:
            return

        if rec is not None:
            at_cut = abs(raw - rec["cut"]) <= BOOST_TOLERANCE
            if rec["restoring"]:
                if at_cut:
                    preset_back = (
                        rec.get("via") == "preset"
                        and rec.get("preset")
                        and state.attributes.get("preset_mode") == rec["preset"]
                    )
                    if preset_back and now_ts - rec["ts"] >= CUT_SETTLE_SECONDS:
                        # az eredeti üzemmód (pl. menetrend) visszaállt, a szelep azóta sem jelentett más célt: a mostani
                        # cél a szelepé (a menetrend értéke egybeeshet a zárás értékével), a zárásnak vége
                        await self._async_drop_cut(valve_id)
                    elif not preset_back and now_ts - rec["ts"] > RESTORE_RETRY_SECONDS:
                        await self._async_restore_cut(valve_id, state, rec)
                    return
                await self._async_drop_cut(valve_id)  # a szelep visszaállt
                return  # új zárás leghamarabb a következő körben (a szoba szünete után)
            if not at_cut:
                if now_ts - rec["ts"] < BOOST_GRACE_SECONDS:
                    return  # még nem érkezett meg a szelep visszajelzése
                self._tlog(
                    "%s: a célhőmérsékletet közben máshol módosították (%s °C, a zárás %s °C volt), nem állítom vissza",
                    self._valve_label(valve_id),
                    raw,
                    rec["cut"],
                )
                await self._async_drop_cut(valve_id)
                return

        if reason and rec is None:
            if valve_id in self._boosts:
                return  # a szelep-emelés rekordja még él (visszaállítás alatt): előbb az záruljon le
            if reason == "over" and self._valve_seems_closed(state, raw):
                return  # a szelep magától is zárva van: nincs mit lezárni
            await self._async_start_cut(valve_id, state, raw, reason)
        elif not reason and rec is not None:
            await self._async_restore_cut(valve_id, state, rec)

    async def _async_start_cut(self, valve_id: str, state: State, raw: float, reason: str) -> None:
        if self._cmd_blocked(valve_id):
            return  # az előző parancs elbukott: nem ismételjük folyamatosan
        cut = clamp_valve_target(raw - CUT_DROP, state)
        if raw - cut < MIN_BOOST_GAIN:
            return  # a szelep célja már eleve (majdnem) a minimumon van
        original_preset = state.attributes.get("preset_mode")
        # Előre írt rekord (mint a szelep-emelésnél): ha a HA a parancs közben leáll, az újraindulás tudja, mi volt az
        # eredeti cél; különben a lejjebb állított érték a szelep "saját" céljának látszana, és ott maradna.
        rec = {
            "original": raw,
            "cut": cut,
            "preset": original_preset if isinstance(original_preset, str) else None,
            "ts": dt_util.utcnow().timestamp(),
            "restoring": False,
            "via": None,
            "reason": reason,
        }
        self._cuts[valve_id] = rec
        await self._async_save()
        ok = await _climate_call(
            self.hass,
            valve_id,
            "set_temperature",
            temperature=cut,
            _warn=valve_id not in self._cmd_fail,
        )
        if not self._cmd_result(valve_id, ok):
            if self._cuts.get(valve_id) is rec:
                del self._cuts[valve_id]  # a parancs nem ment át: nincs mit visszaállítani
            await self._async_save()
            return
        rec["ts"] = dt_util.utcnow().timestamp()  # a türelmi idő a parancs befejezésétől számít
        self._tlog(
            "%s: célhőmérséklet %s -> %s °C (%s)",
            self._valve_label(valve_id),
            raw,
            cut,
            "nyitott ablak miatt lezárva" if reason == "window" else "a szoba a cél fölött van, a szelep lezárva",
        )

    async def _async_restore_cut(self, valve_id: str, state: State, rec: dict[str, Any]) -> None:
        if self._cmd_blocked(valve_id):
            return
        preset = state.attributes.get("preset_mode")
        presets = state.attributes.get("preset_modes") or []
        via = "preset" if rec.get("preset") and preset != rec["preset"] and rec["preset"] in presets else "temp"
        ok = await _async_restore_valve(
            self.hass, valve_id, state, rec, _warn=valve_id not in self._cmd_fail
        )
        if self._cmd_result(valve_id, ok):
            rec["restoring"] = True
            rec["via"] = via
            rec["ts"] = dt_util.utcnow().timestamp()
            await self._async_save()
            self._tlog(
                "%s: célhőmérséklet %s -> %s °C (%s)",
                self._valve_label(valve_id),
                rec["cut"],
                rec["original"],
                "az eredeti üzemmód visszaállítva" if via == "preset" else "az eredeti érték visszaállítva",
            )

    # ------------------------------------------------------------------ 2.19: fagyvédelem a szelepeken
    async def _async_frost_valves(self, statuses: list[RoomStatus], allow: bool) -> None:
        """Fagyveszélynél a szoba szelepei fűtő módban, legalább a fagyvédelmi céllal legyenek: a kazán hiába megy, ha a
        szelep ki van kapcsolva vagy a célja a fagyküszöb alatt van. A kikapcsolt szelepet bekapcsolja, és a célját a
        fagyvédelmi értékre állítja (nem a korábbi komfort célra); a bekapcsolt szelep célját csak akkor emeli, ha az a
        fagyvédelmi érték alatt van. A szelep utána így marad, amíg a felhasználó (vagy a menetrendje) át nem állítja."""
        if not allow:
            return
        now_ts = dt_util.utcnow().timestamp()
        for st in statuses:
            if not st.frost:
                continue
            for valve_id in st.valves:
                try:
                    await self._async_frost_valve(valve_id)
                except Exception as err:  # noqa: BLE001 - egy szelep hibája nem állíthatja le a többit és a kazánt
                    self._valve_unexpected_error(valve_id, err, now_ts)

    async def _async_frost_valve(self, valve_id: str) -> None:
        state = self.hass.states.get(valve_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        if self._cmd_blocked(valve_id) or valve_id in self._boosts or valve_id in self._cuts:
            return
        goal = clamp_valve_target(self.frost_temp + FROST_HYSTERESIS, state)
        warn = valve_id not in self._cmd_fail
        if state.state == HVACMode.OFF:
            modes = state.attributes.get("hvac_modes") or []
            if HVACMode.HEAT in modes or not modes:
                mode = HVACMode.HEAT
            elif HVACMode.AUTO in modes:
                mode = HVACMode.AUTO
            else:
                return
            ok = await _climate_call(self.hass, valve_id, "set_hvac_mode", hvac_mode=mode, _warn=warn)
            if not self._cmd_result(valve_id, ok):
                return
            ok = await _climate_call(self.hass, valve_id, "set_temperature", temperature=goal, _warn=warn)
            self._cmd_result(valve_id, ok)
            self._tlog(
                "%s: fagyvédelem: a kikapcsolt szelep bekapcsolva, a célja %s °C",
                self._valve_label(valve_id),
                f"{goal:g}",
            )
            return
        raw = self._valve_target(state)
        if raw is None or raw >= goal - 0.01:
            return
        ok = await _climate_call(self.hass, valve_id, "set_temperature", temperature=goal, _warn=warn)
        if self._cmd_result(valve_id, ok):
            self._tlog(
                "%s: fagyvédelem: célhőmérséklet %s -> %s °C", self._valve_label(valve_id), raw, f"{goal:g}"
            )

    def _valve_unexpected_error(self, valve_id: str, err: Exception, now_ts: float) -> None:
        """Egy szelep feldolgozásának váratlan hibája (nem a parancs elutasítása: azt a
        `_service_call` és a `_cmd_result` kezeli). A szelepek a kazán kapcsolása ELŐTT vannak
        sorban, ezért egy ilyen hiba nem szökhet ki: a többi szelep és a kazán dolga megy tovább.
        A részletes naplóbejegyzés szelepenként legfeljebb félóránként egyszer készül."""
        if now_ts - self._valve_err_logged.get(valve_id, 0.0) > VALVE_ERROR_LOG_SECONDS:
            self._valve_err_logged[valve_id] = now_ts
            _LOGGER.error(
                "%s: váratlan hiba a szelep vezérlésében (a többi szelep és a kazán kapcsolása megy tovább): %s",
                valve_id,
                err,
                exc_info=err,
            )

    def _boost_end_reason(self, st: RoomStatus) -> str:
        """Miért ért véget a szelep emelése (az eseményhez)."""
        if st.rest_until is not None:
            return "max_time"
        if st.window_open:
            return "window"
        if self.summer_active:
            return "summer"
        if not st.calling or (st.deviation is not None and st.deviation <= st.release_margin):
            return "target_reached"
        if st.source != "sensor":
            return "sensor"
        return "other"

    def _emit_boost(
        self, st: RoomStatus, started_now: bool, started_at: float | None, now_ts: float
    ) -> None:
        dry = "[PRÓBAÜZEM] " if self.valve_dry_run else ""
        if started_now:
            self._tlog(
                "%s%s: szelep-emelés indul – a szoba %s °C, a cél %s °C (%s °C-kal hidegebb)",
                dry,
                st.name,
                trvlog.num(st.current),
                trvlog.num(st.effective_target),
                trvlog.num(st.deviation),
            )
            self._emit(
                "boost_started",
                st,
                deviation=st.deviation,
                current_temperature=None if st.current is None else round(st.current, 1),
                target_temperature=st.effective_target,
                dry_run=self.valve_dry_run,
            )
        else:
            extra: dict[str, Any] = {"reason": self._boost_end_reason(st), "dry_run": self.valve_dry_run}
            if started_at is not None:
                extra["duration_minutes"] = round((now_ts - started_at) / 60)
            self._tlog(
                "%s%s: szelep-emelés vége%s – %s",
                dry,
                st.name,
                "" if started_at is None else f" ({extra['duration_minutes']} perc után)",
                trvlog.BOOST_END_TEXT.get(extra["reason"], extra["reason"]),
            )
            self._emit("boost_ended", st, **extra)

    def _room_wants_boost(self, st: RoomStatus, now_ts: float) -> bool:
        """Mikor kell a szelepet ténylegesen kinyitni a szoba hőmérője alapján.

        - indul: ha a szoba legalább `küszöb`-bel hidegebb a célnál ÉS ez
          `várakozás` ideje folyamatosan fennáll (nagy eltérésnél nincs várakozás)
        - megáll: ha a szoba a célhoz `visszaengedés`-nyire megközelített,
          vagy ha az emelés elérte a maximális időtartamot (utána pihenő)
        Kis eltérésnél a szelep maga dönt, a radiátor maradékhője elég lehet.
        """
        if not (
            st.valve_control
            and st.source == "sensor"
            and st.calling
            and st.deviation is not None
        ):
            st.boost_wanted = False
            st.cold_since = None
            st.boost_started = None
            if not st.calling and st.current is not None:
                # a szoba elérte a célt: új kör kezdődhet. Hiányzó adatnál (szenzor / szelep
                # átmenetileg nem elérhető, újraindítás) a pihenő nem törlődik.
                st.rest_until = None
            return False

        if st.rest_until is not None:
            if now_ts < st.rest_until:
                st.cold_since = None
                return False
            st.rest_until = None

        dev = st.deviation
        if st.boost_wanted:
            if st.boost_started is None:
                st.boost_started = now_ts
            if dev <= st.release_margin:
                st.boost_wanted = False
                st.cold_since = None
                st.boost_started = None
            elif (
                self.max_boost_enabled
                and now_ts - st.boost_started >= self.max_boost_seconds
            ):
                st.boost_wanted = False
                st.cold_since = None
                st.boost_started = None
                st.rest_until = now_ts + self.max_boost_rest_seconds
                self._delay_save(30)  # újraindítás után is érvényes
                _LOGGER.warning(
                    "%s: a szelep emelése elérte a maximális időt (%s óra), "
                    "a szelep visszaáll, %s percig nem emelek újra",
                    st.name,
                    f"{self.max_boost_seconds / 3600:g}",
                    f"{self.max_boost_rest_seconds / 60:g}",
                )
            return st.boost_wanted

        if dev >= st.boost_threshold:
            if st.cold_since is None:
                st.cold_since = now_ts
            big = dev >= st.boost_threshold + BOOST_IMMEDIATE_EXTRA
            # "Fűts most" és az előfűtés nem vár: a felhasználó (vagy a menetrend) azonnal meleget kér
            urgent = st.manual_until is not None or st.preheat_active
            if big or urgent or now_ts - st.cold_since >= st.boost_delay_s:
                st.boost_wanted = True
                st.boost_started = now_ts
        else:
            st.cold_since = None
        return st.boost_wanted

    def _update_window(self, st: RoomStatus) -> None:
        """Az ablak csak a késleltetés letelte után számít nyitottnak (rövid szellőztetés nem)."""
        now_ts = dt_util.utcnow().timestamp()
        any_open = any(
            (state := self.hass.states.get(entity_id)) is not None and state.state == "on"
            for entity_id in st.window_sensors
        )
        if not any_open:
            if st.window_open:
                self._tlog("%s: az ablak bezárva, a fűtés újra engedélyezett", st.name)
                self._emit(
                    "window_resumed",
                    st,
                    open_minutes=round((now_ts - (st.window_open_since or now_ts)) / 60),
                )
            st.window_open_since = None
            st.window_open = False
            return
        if st.window_open_since is None:
            st.window_open_since = now_ts
        was_open = st.window_open
        st.window_open = now_ts - st.window_open_since >= st.window_delay_s
        if st.window_open and not was_open:
            self._emit("window_paused", st, open_minutes=round(st.window_delay_s / 60))
            self._tlog(
                "%s: az ablak %s perce nyitva, a szoba fűtése szünetel",
                st.name,
                f"{st.window_delay_s / 60:g}",
            )

    def _valve_open(self, previous: bool, pairs: list[tuple[float, float]]) -> bool:
        """Becslés: a szelep a saját szabályzása szerint nyitva van-e (hiszterézissel)."""
        if not pairs:
            return True  # nincs adat: nem blokkoljuk a fűtést
        if previous:
            return any(cur < tgt for cur, tgt in pairs)
        return any(cur < tgt - self.hysteresis for cur, tgt in pairs)

    def _room_boiler_demand(self, st: RoomStatus) -> bool:
        """A szoba kér-e hőt a kazántól (szelep állapothoz kötés esetén csak nyitott szelepnél)."""
        if not st.calling:
            return False
        if st.frost:
            return True  # 2.19: fagyvédelem: a szelep állapotától függetlenül
        if not st.valve_demand_link:
            return True
        forced_open = st.boost_wanted and not self.valve_dry_run
        return forced_open or st.valve_open

    def _dry_run_valve(self, valve_id: str, wanted: bool) -> None:
        was = valve_id in self._dry
        if wanted and not was:
            self._dry.add(valve_id)
            self._tlog(
                "[PRÓBAÜZEM] %s: kinyitnám (célhőmérséklet emelés), mert a szoba "
                "hőmérője szerint hideg van",
                self._valve_label(valve_id),
            )
        elif not wanted and was:
            self._dry.discard(valve_id)
            self._tlog(
                "[PRÓBAÜZEM] %s: visszaállítanám az eredeti célhőmérsékletet", self._valve_label(valve_id)
            )

    async def _async_control_valve(self, valve_id: str, wanted: bool) -> None:
        state = self.hass.states.get(valve_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        rec = self._boosts.get(valve_id)
        now_ts = dt_util.utcnow().timestamp()

        if state.state == HVACMode.OFF:
            if rec is not None:  # a felhasználó kikapcsolta a szelepet
                await self._async_drop_boost(valve_id)
            return

        raw = self._valve_target(state)
        if raw is None:
            return

        if rec is not None:
            at_boost = abs(raw - rec["boost"]) <= BOOST_TOLERANCE
            if rec["restoring"]:
                if at_boost:
                    if now_ts - rec["ts"] > RESTORE_RETRY_SECONDS:
                        await self._async_restore(valve_id, state, rec)
                    return
                await self._async_drop_boost(valve_id)  # a szelep visszaállt
                rec = None  # és ha kell, azonnal indulhat az új emelés
            elif not at_boost:
                if now_ts - rec["ts"] < BOOST_GRACE_SECONDS:
                    return  # még nem érkezett meg a szelep visszajelzése
                self._tlog(
                    "%s: a célhőmérsékletet közben máshol módosították (%s °C, az emelés %s °C volt), "
                    "nem állítom vissza",
                    self._valve_label(valve_id),
                    raw,
                    rec["boost"],
                )
                await self._async_drop_boost(valve_id)
                rec = None

        if wanted and rec is None:
            await self._async_start_boost(valve_id, state, raw)
        elif not wanted and rec is not None:
            await self._async_restore(valve_id, state, rec)

    # --- sikertelen szelep-parancsok: egyre ritkább újrapróbálás, egyszeri jelzés
    def _cmd_blocked(self, valve_id: str) -> bool:
        """Igaz, ha az előző parancs elbukott, és még nem telt le a várakozás."""
        rec = self._cmd_fail.get(valve_id)
        return bool(rec) and dt_util.utcnow().timestamp() < rec["until"]

    def _cmd_result(self, valve_id: str, ok: bool) -> bool:
        """A parancs eredményének nyilvántartása; a hibát csak az első alkalommal jelezzük."""
        if ok:
            self._cmd_fail.pop(valve_id, None)
            return True
        rec = self._cmd_fail.setdefault(valve_id, {"n": 0, "until": 0.0})
        rec["n"] += 1
        delay = VALVE_RETRY_STEPS[min(int(rec["n"]) - 1, len(VALVE_RETRY_STEPS) - 1)]
        rec["until"] = dt_util.utcnow().timestamp() + delay
        if rec["n"] == 1:
            _LOGGER.warning(
                "%s: a szelep nem fogadta el a parancsot; %d s múlva újra próbálom, "
                "azután egyre ritkábban (a további hibákat nem naplózom)",
                valve_id,
                delay,
            )
            self._emit("valve_command_failed", valve=valve_id)
        return False

    async def _async_start_boost(self, valve_id: str, state: State, raw: float) -> None:
        if self._cmd_blocked(valve_id):
            return  # az előző parancs elbukott: nem ismételjük folyamatosan
        try:
            boost = float(state.attributes.get("max_temp", DEFAULT_VALVE_MAX_TEMP))
        except (TypeError, ValueError):
            boost = DEFAULT_VALVE_MAX_TEMP
        boost = clamp_valve_target(boost, state)  # soha nem 34 °C fölé
        if boost - raw < MIN_BOOST_GAIN:
            return  # a szelep már eleve (majdnem) maximumon van
        # az eredeti presetet a hívás ELŐTT jegyezzük meg (a hívás átválthatja kézire)
        original_preset = state.attributes.get("preset_mode")
        # Előre írt napló: a rekord előbb kerül a lemezre, mint ahogy a parancs elmegy. Ha a HA
        # a kettő között (vagy a parancs közben) leáll, az újraindulás tudja, mi volt az eredeti
        # cél; különben a megemelt érték a szelep "saját" céljának látszana, és ott maradna.
        rec = {
            "original": raw,
            "boost": boost,
            "preset": original_preset,
            "ts": dt_util.utcnow().timestamp(),
            "restoring": False,
        }
        self._boosts[valve_id] = rec
        await self._async_save()
        ok = await _climate_call(
            self.hass,
            valve_id,
            "set_temperature",
            temperature=boost,
            _warn=valve_id not in self._cmd_fail,
        )
        if not self._cmd_result(valve_id, ok):
            if self._boosts.get(valve_id) is rec:
                del self._boosts[valve_id]  # a parancs nem ment át: nincs mit visszaállítani
            await self._async_save()
            return
        rec["ts"] = dt_util.utcnow().timestamp()  # a türelmi idő a parancs befejezésétől számít
        self._tlog(
            "%s: célhőmérséklet %s -> %s °C (a szoba hőmérője szerint hideg van)",
            self._valve_label(valve_id),
            raw,
            boost,
        )

    async def _async_restore(
        self, valve_id: str, state: State, rec: dict[str, Any]
    ) -> None:
        if self._cmd_blocked(valve_id):
            return
        ok = await _async_restore_valve(
            self.hass, valve_id, state, rec, _warn=valve_id not in self._cmd_fail
        )
        if self._cmd_result(valve_id, ok):
            rec["restoring"] = True
            rec["ts"] = dt_util.utcnow().timestamp()
            await self._async_save()
            self._tlog(
                "%s: célhőmérséklet %s -> %s °C (az eredeti érték visszaállítva)",
                self._valve_label(valve_id),
                rec["boost"],
                rec["original"],
            )

    # ------------------------------------------------------------------ kazán
    async def _async_ensure_on(self, boiler: State) -> bool:
        """A kazán termosztátja fűtő módban és a beállított célon legyen. Igaz, ha minden szükséges parancs sikerült
        (vagy nem kellett parancs); hamis, ha egy parancs elbukott, vagy a termosztát nem kínál fűtő módot (2.19)."""
        attrs = boiler.attributes
        warn = self._boiler_fail == 0  # a figyelmeztetést csak az első hibánál írjuk ki, az ismétlések csendesek
        if boiler.state == HVACMode.OFF:
            modes = attrs.get("hvac_modes") or []
            if HVACMode.HEAT in modes or not modes:
                mode = HVACMode.HEAT
            elif HVACMode.AUTO in modes:
                mode = HVACMode.AUTO
            else:
                # Meross LAN 6.x: az MTS200 "Summer mode" kapcsolója bekapcsolva csak OFF / COOL módot
                # kínál, ilyenkor a kazánt nem lehet fűtésre kapcsolni. A figyelmeztetést ritkán ismételjük.
                now_ts = dt_util.utcnow().timestamp()
                if now_ts - self._mode_warned > BOILER_MODE_WARN_SECONDS:
                    self._mode_warned = now_ts
                    _LOGGER.warning(
                        "A(z) %s nem támogat heat/auto módot (támogatott módok: %s); ha Meross MTS200, "
                        "nézd meg, hogy a \"Summer mode\" (nyári mód) kapcsolója ki van-e kapcsolva",
                        self.boiler,
                        ", ".join(str(m) for m in modes),
                    )
                return False
            if not await self._call("set_hvac_mode", hvac_mode=mode, _warn=warn):
                return False

        if self.on_temp > 0:
            try:
                target = min(self.on_temp, float(attrs.get("max_temp", self.on_temp)))
            except (TypeError, ValueError):
                target = self.on_temp
            try:
                current_target = float(attrs.get("temperature"))
            except (TypeError, ValueError):
                current_target = None
            if current_target is None or abs(current_target - target) > 0.01:
                return await self._call("set_temperature", temperature=target, _warn=warn)
        return True

    async def _call(self, service: str, *, _warn: bool = True, **data) -> bool:
        return await _climate_call(self.hass, self.boiler, service, _warn=_warn, **data)

    async def _entity_call(self, domain: str, entity_id: str, service: str, **data: Any) -> bool:
        """Szolgáltatáshívás tetszőleges entitásra (a kalibráció a szelep szám-entitását írja)."""
        return await _service_call(self.hass, domain, entity_id, service, **data)
