"""A kazán vezérlés logikája: szobák hőigénye + nyári mód."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Any

from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
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
    BOOST_GRACE_SECONDS,
    BOOST_IMMEDIATE_EXTRA,
    BOOST_TOLERANCE,
    COMFORT_MIN_TARGET,
    CONF_BOILER,
    CONF_BOILER_MIN_OFF,
    CONF_BOILER_MIN_ON,
    CONF_BOILER_ON_TEMP,
    CONF_CYCLE_MAX_STARTS,
    CONF_CYCLE_MIN_AVG_ON,
    CONF_CYCLE_MONITOR,
    CONF_CYCLE_PROTECTION,
    CONF_EVENTS_ENABLED,
    CONF_HUMIDITY_MAX_BOOST,
    CONF_HYSTERESIS,
    CONF_MANUAL_BOOST_ENABLED,
    CONF_MANUAL_BOOST_END_ON_TARGET,
    CONF_MANUAL_BOOST_MINUTES,
    CONF_MANUAL_BOOST_OFFSET,
    CONF_MIN_SWITCH_TIME,
    CONF_PREHEAT_DEFAULT_RATE,
    CONF_PREHEAT_ENABLED,
    CONF_PREHEAT_HOLD_MINUTES,
    CONF_PREHEAT_MAX_MINUTES,
    CONF_OUTDOOR_SENSOR,
    CONF_ROOM_HUM,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_PREHEAT,
    CONF_ROOM_TEMP,
    CONF_ROOM_VALVE_CONTROL,
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
    CONF_WINDOW_DELAY,
    CONF_VALVE_BOOST_DELAY,
    CONF_VALVE_BOOST_THRESHOLD,
    CONF_VALVE_DRY_RUN,
    CONF_VALVE_RELEASE_MARGIN,
    DEFAULT_BOILER_MIN_OFF,
    DEFAULT_BOILER_MIN_ON,
    DEFAULT_BOILER_ON_TEMP,
    DEFAULT_CYCLE_MAX_STARTS,
    DEFAULT_CYCLE_MIN_AVG_ON,
    DEFAULT_CYCLE_MONITOR,
    DEFAULT_CYCLE_PROTECTION,
    DEFAULT_EVENTS_ENABLED,
    DEFAULT_HUMIDITY_MAX_BOOST,
    DEFAULT_HYSTERESIS,
    DEFAULT_MANUAL_BOOST_ENABLED,
    DEFAULT_MANUAL_BOOST_END_ON_TARGET,
    DEFAULT_MANUAL_BOOST_MINUTES,
    DEFAULT_MANUAL_BOOST_OFFSET,
    DEFAULT_MIN_SWITCH_TIME,
    DEFAULT_PREHEAT_ENABLED,
    DEFAULT_PREHEAT_HOLD_MINUTES,
    DEFAULT_PREHEAT_MAX_MINUTES,
    DEFAULT_PREHEAT_RATE,
    DEFAULT_SUMMER_END,
    DEFAULT_SUMMER_START,
    DEFAULT_MAX_BOOST_ENABLED,
    DEFAULT_MAX_BOOST_HOURS,
    DEFAULT_MAX_BOOST_REST,
    DEFAULT_STALE_ENABLED,
    DEFAULT_STALE_HOURS,
    DEFAULT_SUMMER_TEMP,
    DEFAULT_WINDOW_DELAY,
    DEFAULT_VALVE_BOOST_DELAY,
    DEFAULT_VALVE_BOOST_THRESHOLD,
    DEFAULT_VALVE_DRY_RUN,
    DEFAULT_VALVE_MAX_TEMP,
    DEFAULT_VALVE_RELEASE_MARGIN,
    DOMAIN,
    EVENT_TYPE,
    HEATING_RATE_MAX,
    HEATING_RATE_MIN,
    HEATING_RATE_MIN_SAMPLES,
    HEATING_RATE_MIN_TREND,
    HEATING_RATE_WINDOW,
    HUMIDITY_FULL,
    HUMIDITY_START,
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
    RESTORE_RETRY_SECONDS,
    SAMPLE_INTERVAL_SECONDS,
    STORAGE_VERSION,
    SUMMER_HYSTERESIS,
    TREND_HYSTERESIS,
    TREND_MIN_SPAN_SECONDS,
    TREND_SAMPLE_SECONDS,
    TREND_WINDOW_SECONDS,
    parse_month_day,
)

from .cycles import CycleLog

_LOGGER = logging.getLogger(__name__)

TICK = timedelta(seconds=60)
PREHEAT_LOOKAHEAD_SECONDS = 24 * 3600  # ennyire előre mutatjuk a következő előfűtést
RATE_SAMPLE_SECONDS = 55  # a felfűtési sebességet legfeljebb percenként mintázzuk


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


async def _climate_call(
    hass: HomeAssistant, entity_id: str, service: str, **data: Any
) -> bool:
    try:
        await hass.services.async_call(
            "climate",
            service,
            {"entity_id": entity_id, **data},
            blocking=True,
        )
    except HomeAssistantError as err:
        _LOGGER.warning("climate.%s hiba a(z) %s-en: %s", service, entity_id, err)
        return False
    return True


async def _async_restore_valve(
    hass: HomeAssistant, valve_id: str, state: State, rec: dict[str, Any]
) -> bool:
    """Visszaállítja a szelep eredeti célját (vagy az eredeti presetet, ha az változott)."""
    preset = state.attributes.get("preset_mode")
    presets = state.attributes.get("preset_modes") or []
    original_preset = rec.get("preset")
    if original_preset and preset != original_preset and original_preset in presets:
        return await _climate_call(
            hass, valve_id, "set_preset_mode", preset_mode=original_preset
        )
    return await _climate_call(
        hass, valve_id, "set_temperature", temperature=rec["original"]
    )


async def async_restore_on_remove(hass: HomeAssistant, entry_id: str) -> None:
    """Az integráció törlésekor visszaállítja az összes még emelt szelepet."""
    store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry_id}")
    data = await store.async_load()
    boosts = data.get("boosts") if isinstance(data, dict) else None
    for valve_id, rec in (boosts or {}).items():
        state = hass.states.get(valve_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            continue
        try:
            raw = float(state.attributes["temperature"])
            if abs(raw - float(rec["boost"])) > BOOST_TOLERANCE:
                continue  # időközben máshol módosították
            await _async_restore_valve(
                hass,
                valve_id,
                state,
                {"original": float(rec["original"]), "preset": rec.get("preset")},
            )
        except (KeyError, TypeError, ValueError):
            continue


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
    boost_started: float | None = None
    rest_until: float | None = None
    # ablakérzékelők
    window_sensors: list[str] = field(default_factory=list)
    window_delay_s: float = DEFAULT_WINDOW_DELAY * 60
    window_open_since: float | None = None
    window_open: bool = False  # a késleltetés letelt: a szoba szünetel
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
    # tanult felfűtési sebesség (°C/óra)
    heating_rate: float | None = None
    heating_samples: int = 0
    rate_ts: float = 0.0


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
        self.outdoor_stale = False
        self._issue_state: dict[str, bool] = {}

        # 2.8: események, kazán-ciklusok, védelem (mind külön kapcsolható)
        self.events_enabled = bool(cfg.get(CONF_EVENTS_ENABLED, DEFAULT_EVENTS_ENABLED))
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

        self._last_switch = None
        self._prev_summer = False
        # szelep emelések: valve_id -> {original, boost, preset, ts, restoring}
        self._boosts: dict[str, dict[str, Any]] = {}
        self._dry: set[str] = set()
        self._unsubs: list[Callable[[], None]] = []
        self._retry_unsub: Callable[[], None] | None = None
        self._listeners: list[Callable[[], None]] = []
        self._lock = asyncio.Lock()

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
        )

    # ------------------------------------------------------------------ életciklus
    async def async_load(self) -> None:
        """A kinti hőmérséklet-minták visszatöltése újraindítás után."""
        data = await self._store.async_load()
        if not isinstance(data, dict):
            return
        for item in data.get("samples", []):
            try:
                self._samples.append((float(item[0]), float(item[1])))
            except (TypeError, ValueError, IndexError):
                continue
        self.cycles.load(data.get("cycles"))
        for valve_id, rec in (data.get("boosts") or {}).items():
            try:
                self._boosts[valve_id] = {
                    "original": float(rec["original"]),
                    "boost": float(rec["boost"]),
                    "preset": rec.get("preset"),
                    "ts": float(rec.get("ts", 0)),
                    "restoring": bool(rec.get("restoring", False)),
                }
            except (KeyError, TypeError, ValueError):
                continue
        self._load_2_9(data)
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
        for room_id, rec in (data.get("rates") or {}).items():
            st = self.status.get(room_id)
            try:
                rate, count = float(rec["rate"]), int(rec["n"])
            except (KeyError, TypeError, ValueError):
                continue
            if st is not None and HEATING_RATE_MIN <= rate <= HEATING_RATE_MAX and count > 0:
                st.heating_rate, st.heating_samples = rate, count
        if self.manual_boost_enabled:
            for room_id, rec in (data.get("manual") or {}).items():
                st = self.status.get(room_id)
                try:
                    until, offset = float(rec["until"]), float(rec["offset"])
                    started = float(rec.get("started") or now_ts)
                except (KeyError, TypeError, ValueError):
                    continue
                if st is not None and until > now_ts:
                    st.manual_until, st.manual_offset, st.manual_started = until, offset, started
        if self.preheat_enabled:
            for room_id, rec in (data.get("preheat") or {}).items():
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
        return clean if clean["ready"] + clean["hold"] > now_ts else None

    async def async_start(self) -> None:
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
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
        if self._retry_unsub:
            self._retry_unsub()
            self._retry_unsub = None
        for issue_id, active in list(self._issue_state.items()):
            if active:
                ir.async_delete_issue(self.hass, DOMAIN, issue_id)
        self._issue_state.clear()

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
        self.hass.async_create_task(self.async_evaluate())

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
        elif st.sensor_stale:
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
        self._store.async_delay_save(self._data_to_save, 30)

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
        _LOGGER.info("%s: Fűts most (+%s °C, %s percre)", st.name, f"{offset:g}", f"{minutes:g}")
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
        """Amíg a kazán fűt és a szoba melegszik, a mért trendből tanulja a felfűtési sebességet."""
        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN, HVACMode.OFF):
            return
        now_ts = dt_util.utcnow().timestamp()
        for st in statuses:
            if not (
                st.boiler_demand
                and st.source == "sensor"
                and not st.sensor_stale
                and not st.window_open
                and st.trend is not None
                and st.trend >= HEATING_RATE_MIN_TREND
                and now_ts - st.rate_ts >= RATE_SAMPLE_SECONDS
            ):
                continue
            sample = _clamp(st.trend, HEATING_RATE_MIN, HEATING_RATE_MAX)
            st.rate_ts = now_ts
            if st.heating_rate is None:
                st.heating_rate = sample
            else:
                st.heating_rate += (sample - st.heating_rate) / min(
                    st.heating_samples + 1, HEATING_RATE_WINDOW
                )
            st.heating_samples += 1
            if st.heating_samples % 10 == 0:
                self._store.async_delay_save(self._data_to_save, 600)

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
            or st.sensor_stale
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
                self._store.async_delay_save(self._data_to_save, 30)
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
        _LOGGER.info(
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
    ) -> None:
        """Javítások (Repairs) értesítés létrehozása / törlése, csak változáskor."""
        if self._issue_state.get(issue_id) == active:
            return
        self._issue_state[issue_id] = active
        if active:
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
        return {
            "samples": [[ts, val] for ts, val in self._samples],
            "boosts": self._boosts,
            "cycles": self.cycles.to_list(),
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
            "rates": {
                st.room_id: {"rate": round(st.heating_rate, 3), "n": st.heating_samples}
                for st in self.status.values()
                if st.heating_rate is not None
            },
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
            self._store.async_delay_save(self._data_to_save, 600)

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

        targets: list[float] = []
        valve_temps: list[float] = []
        pairs: list[tuple[float, float]] = []
        reachable = 0
        for valve_id in room[CONF_ROOM_VALVES]:
            state = self.hass.states.get(valve_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            reachable += 1
            if state.state == HVACMode.OFF:
                continue
            raw = self._valve_target(state)
            user_target = self._user_target(valve_id, raw) if raw is not None else None
            if user_target is not None:
                targets.append(user_target)
            try:
                valve_current = float(state.attributes["current_temperature"])
            except (KeyError, TypeError, ValueError):
                valve_current = None
            if valve_current is not None:
                valve_temps.append(valve_current)
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
        now_ts = dt_util.utcnow().timestamp()
        self._check_manual(st, now_ts)

        st.current = st.source = st.target = st.effective_target = None
        st.deviation = None
        st.humidity = None
        st.humidity_boost = 0.0

        if not targets:
            st.calling = False
            st.valve_open = False
            self._reset_preheat_view(st)
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

        # páratartalom miatti célhőmérséklet-emelés
        humidity = self._read_float(room.get(CONF_ROOM_HUM))
        st.humidity = humidity
        if (
            humidity is not None
            and self.humidity_max_boost > 0
            and st.target >= COMFORT_MIN_TARGET
        ):
            frac = (humidity - HUMIDITY_START) / (HUMIDITY_FULL - HUMIDITY_START)
            st.humidity_boost = round(
                self.humidity_max_boost * min(max(frac, 0.0), 1.0), 2
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

        # hőigény hiszterézissel: indul, ha a cél alatt van, megy a cél eléréséig
        if current is None:
            st.calling = False
        elif st.calling:
            if current >= st.effective_target:
                st.calling = False
        elif current < st.effective_target - self.hysteresis:
            st.calling = True

        if st.window_open:
            st.calling = False  # nyitott ablak: a szoba nem kér hőt, a szelep emelés leáll

        st.valve_open = (
            self._valve_open(st.valve_open, pairs) if st.valve_demand_link else False
        )
        return st

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
            try:
                await self._async_evaluate()
            finally:
                self._events_armed = True  # az első kiértékelés után már küldhetünk eseményt
                self._notify()

    async def _async_evaluate(self) -> None:
        self._update_outdoor()
        statuses = [self._update_room(room) for room in self.rooms]

        if self.summer_active:
            for st in statuses:
                st.calling = False
        if self.summer_active != self._prev_summer:
            _LOGGER.info(
                "Nyári mód %s (kinti 24 órás átlag: %s °C)",
                "BEKAPCSOLVA" if self.summer_active else "KIKAPCSOLVA",
                self.outdoor_avg,
            )
            self._prev_summer = self.summer_active

        await self._async_control_valves(statuses)
        for st in statuses:
            st.boiler_demand = self._room_boiler_demand(st)
        self._observe_boiler()
        self._learn_rates(statuses)

        if not statuses or not any(st.reachable for st in statuses):
            # nincs szoba, vagy egyik szelep sem elérhető: nem nyúlunk a kazánhoz
            return

        demand = any(st.boiler_demand for st in statuses)

        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        boiler_on = boiler.state != HVACMode.OFF

        if demand != boiler_on:
            remaining = self._switch_wait_remaining(demand)
            if remaining is not None and remaining > timedelta(0):
                self._schedule_retry(remaining)
                return

        if demand:
            await self._async_ensure_on(boiler)
        elif boiler_on:
            await self._call("set_hvac_mode", hvac_mode=HVACMode.OFF)

        if demand != boiler_on:
            self._last_switch = dt_util.utcnow()
            _LOGGER.info(
                "Kazán %s (%s)",
                "BE" if demand else "KI",
                (
                    "hőt kérő szobák: "
                    + ", ".join(st.name for st in statuses if st.boiler_demand)
                    if demand
                    else "nyári mód" if self.summer_active else "nincs hőigény"
                ),
            )

    def _switch_wait_remaining(self, turning_on: bool) -> timedelta | None:
        """Mennyi ideig kell még várni a kazán következő kapcsolásáig (None: nincs korlát).

        Alapból a "minimális kapcsolási idő" számít az utolsó kapcsolástól. Ha a ciklus-védelem
        be van kapcsolva, a kazán minimális be- / kikapcsolt ideje is (a megfigyelt váltásoktól,
        így újraindítás után és külső kapcsolásnál is).
        """
        refs: list[datetime] = []
        if self._last_switch is not None:
            refs.append(self._last_switch + self.min_switch)
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

    def _observe_boiler(self) -> None:
        """A kazán be/ki váltásainak naplózása; gyakori kapcsolgatás figyelése."""
        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        now_ts = dt_util.utcnow().timestamp()
        # a váltás valódi ideje (az állapot utolsó változása), hogy a késve észlelt váltás se csússzon el
        changed = getattr(boiler, "last_changed", None)
        event_ts = changed.timestamp() if changed is not None else now_ts
        event_ts = min(max(event_ts, self.cycles.last_change() or 0.0), now_ts)
        if self.cycles.observe(boiler.state != HVACMode.OFF, event_ts):
            self._store.async_delay_save(self._data_to_save, 600)
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
        return raw

    async def _async_save(self) -> None:
        await self._store.async_save(self._data_to_save())

    async def _async_drop_boost(self, valve_id: str) -> None:
        self._boosts.pop(valve_id, None)
        await self._async_save()

    async def _async_control_valves(self, statuses: list[RoomStatus]) -> None:
        """A szoba hőmérője alapján teljesen kinyitja / visszaállítja a szelepeket."""
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
            if self.valve_dry_run:
                if valve_id in self._boosts:
                    await self._async_control_valve(valve_id, False)
                self._dry_run_valve(valve_id, wanted)
            else:
                await self._async_control_valve(valve_id, wanted)

        for st in statuses:
            if self.valve_dry_run:
                st.boosted = any(v in self._dry for v in st.valves)
            else:
                st.boosted = any(
                    v in self._boosts and not self._boosts[v]["restoring"]
                    for v in st.valves
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
        if started_now:
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
            if not st.calling:
                st.rest_until = None  # a szoba elérte a célt: új kör kezdődhet
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
                _LOGGER.info("%s: az ablak bezárva, a fűtés újra engedélyezett", st.name)
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
            _LOGGER.info(
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
        if not st.valve_demand_link:
            return True
        forced_open = st.boost_wanted and not self.valve_dry_run
        return forced_open or st.valve_open

    def _dry_run_valve(self, valve_id: str, wanted: bool) -> None:
        was = valve_id in self._dry
        if wanted and not was:
            self._dry.add(valve_id)
            _LOGGER.info(
                "[PRÓBAÜZEM] %s: kinyitnám (célhőmérséklet emelés), mert a szoba "
                "hőmérője szerint hideg van",
                valve_id,
            )
        elif not wanted and was:
            self._dry.discard(valve_id)
            _LOGGER.info(
                "[PRÓBAÜZEM] %s: visszaállítanám az eredeti célhőmérsékletet", valve_id
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
                _LOGGER.info(
                    "%s: a célhőmérsékletet közben máshol módosították (%s °C), "
                    "nem állítom vissza",
                    valve_id,
                    raw,
                )
                await self._async_drop_boost(valve_id)
                rec = None

        if wanted and rec is None:
            await self._async_start_boost(valve_id, state, raw)
        elif not wanted and rec is not None:
            await self._async_restore(valve_id, state, rec)

    async def _async_start_boost(self, valve_id: str, state: State, raw: float) -> None:
        try:
            boost = float(state.attributes.get("max_temp", DEFAULT_VALVE_MAX_TEMP))
        except (TypeError, ValueError):
            boost = DEFAULT_VALVE_MAX_TEMP
        if boost - raw < MIN_BOOST_GAIN:
            return  # a szelep már eleve (majdnem) maximumon van
        # az eredeti presetet a hívás ELŐTT jegyezzük meg (a hívás átválthatja kézire)
        original_preset = state.attributes.get("preset_mode")
        if not await _climate_call(
            self.hass, valve_id, "set_temperature", temperature=boost
        ):
            return
        self._boosts[valve_id] = {
            "original": raw,
            "boost": boost,
            "preset": original_preset,
            "ts": dt_util.utcnow().timestamp(),
            "restoring": False,
        }
        await self._async_save()
        _LOGGER.info(
            "%s: célhőmérséklet %s -> %s °C (szoba hőmérője szerint hideg van)",
            valve_id,
            raw,
            boost,
        )

    async def _async_restore(
        self, valve_id: str, state: State, rec: dict[str, Any]
    ) -> None:
        if await _async_restore_valve(self.hass, valve_id, state, rec):
            rec["restoring"] = True
            rec["ts"] = dt_util.utcnow().timestamp()
            await self._async_save()
            _LOGGER.info(
                "%s: eredeti célhőmérséklet visszaállítva (%s °C)",
                valve_id,
                rec["original"],
            )

    # ------------------------------------------------------------------ kazán
    async def _async_ensure_on(self, boiler: State) -> None:
        attrs = boiler.attributes
        if boiler.state == HVACMode.OFF:
            modes = attrs.get("hvac_modes") or []
            if HVACMode.HEAT in modes or not modes:
                mode = HVACMode.HEAT
            elif HVACMode.AUTO in modes:
                mode = HVACMode.AUTO
            else:
                _LOGGER.warning("A(z) %s nem támogat heat/auto módot", self.boiler)
                return
            await self._call("set_hvac_mode", hvac_mode=mode)

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
                await self._call("set_temperature", temperature=target)

    async def _call(self, service: str, **data) -> bool:
        return await _climate_call(self.hass, self.boiler, service, **data)
