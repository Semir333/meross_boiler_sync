"""A kazán vezérlés logikája: szobák hőigénye + nyári mód."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from homeassistant.components.climate import HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.exceptions import HomeAssistantError
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
    CONF_BOILER_ON_TEMP,
    CONF_HUMIDITY_MAX_BOOST,
    CONF_HYSTERESIS,
    CONF_MIN_SWITCH_TIME,
    CONF_OUTDOOR_SENSOR,
    CONF_ROOM_HUM,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_TEMP,
    CONF_ROOM_VALVE_CONTROL,
    CONF_ROOM_VALVE_LINK,
    CONF_ROOM_VALVES,
    CONF_ROOMS,
    CONF_SUMMER_END,
    CONF_SUMMER_START,
    CONF_SUMMER_TEMP,
    CONF_VALVE_BOOST_DELAY,
    CONF_VALVE_BOOST_THRESHOLD,
    CONF_VALVE_DRY_RUN,
    CONF_VALVE_RELEASE_MARGIN,
    DEFAULT_BOILER_ON_TEMP,
    DEFAULT_HUMIDITY_MAX_BOOST,
    DEFAULT_HYSTERESIS,
    DEFAULT_MIN_SWITCH_TIME,
    DEFAULT_SUMMER_END,
    DEFAULT_SUMMER_START,
    DEFAULT_SUMMER_TEMP,
    DEFAULT_VALVE_BOOST_DELAY,
    DEFAULT_VALVE_BOOST_THRESHOLD,
    DEFAULT_VALVE_DRY_RUN,
    DEFAULT_VALVE_MAX_TEMP,
    DEFAULT_VALVE_RELEASE_MARGIN,
    DOMAIN,
    HUMIDITY_FULL,
    HUMIDITY_START,
    MAX_EFFECTIVE_TARGET,
    MIN_BOOST_GAIN,
    RESTORE_RETRY_SECONDS,
    SAMPLE_INTERVAL_SECONDS,
    STORAGE_VERSION,
    SUMMER_HYSTERESIS,
    parse_month_day,
)

_LOGGER = logging.getLogger(__name__)

TICK = timedelta(seconds=60)


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
            valve_control=bool(room.get(CONF_ROOM_VALVE_CONTROL))
            and bool(room.get(CONF_ROOM_TEMP)),
            boost_threshold=threshold,
            boost_delay_s=delay_min * 60,
            release_margin=release,
            valve_demand_link=bool(room.get(CONF_ROOM_VALVE_LINK)),
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
        # újraindítás előtt még emelt szobák: ne engedjük el és emeljük újra feleslegesen
        for st in self.status.values():
            if any(
                v in self._boosts and not self._boosts[v]["restoring"] for v in st.valves
            ):
                st.boost_wanted = True

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

    # ------------------------------------------------------------------ segédek
    def _read_float(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return None
        try:
            return float(state.state)
        except (TypeError, ValueError):
            return None

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
        value = self._read_float(self.outdoor_sensor)
        self.outdoor_now = value

        if value is not None and (
            not self._samples
            or now_ts - self._samples[-1][0] >= SAMPLE_INTERVAL_SECONDS
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

        if self.outdoor_avg is None or not self.in_summer_period:
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
        st.current = st.source = st.target = st.effective_target = None
        st.deviation = None
        st.humidity = None
        st.humidity_boost = 0.0

        if not targets:
            st.calling = False
            st.valve_open = False
            return st

        # a szoba célhőmérséklete a szelep(ek)en beállított érték (a legmagasabb)
        st.target = max(targets)

        # aktuális hőmérséklet: szoba szenzor, ennek hiányában a szelepek átlaga
        current = self._read_float(room.get(CONF_ROOM_TEMP))
        if current is not None:
            st.source = "sensor"
        elif valve_temps:
            current = sum(valve_temps) / len(valve_temps)
            st.source = "valve"
        st.current = current

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
        st.effective_target = round(
            min(st.target + st.humidity_boost, max(MAX_EFFECTIVE_TARGET, st.target)),
            2,
        )

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

        st.valve_open = (
            self._valve_open(st.valve_open, pairs) if st.valve_demand_link else False
        )
        return st

    # ------------------------------------------------------------------ kiértékelés
    async def async_evaluate(self) -> None:
        async with self._lock:
            try:
                await self._async_evaluate()
            finally:
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

        if not statuses or not any(st.reachable for st in statuses):
            # nincs szoba, vagy egyik szelep sem elérhető: nem nyúlunk a kazánhoz
            return

        demand = any(st.boiler_demand for st in statuses)

        boiler = self.hass.states.get(self.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            return
        boiler_on = boiler.state != HVACMode.OFF

        if demand != boiler_on and self._last_switch is not None:
            remaining = self._last_switch + self.min_switch - dt_util.utcnow()
            if remaining > timedelta(0):
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
            boost = self._room_wants_boost(st, now_ts)
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

    def _room_wants_boost(self, st: RoomStatus, now_ts: float) -> bool:
        """Mikor kell a szelepet ténylegesen kinyitni a szoba hőmérője alapján.

        - indul: ha a szoba legalább `küszöb`-bel hidegebb a célnál ÉS ez
          `várakozás` ideje folyamatosan fennáll (nagy eltérésnél nincs várakozás)
        - megáll: ha a szoba a célhoz `visszaengedés`-nyire megközelített
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
            return False

        dev = st.deviation
        if st.boost_wanted:
            if dev <= st.release_margin:
                st.boost_wanted = False
                st.cold_since = None
            return st.boost_wanted

        if dev >= st.boost_threshold:
            if st.cold_since is None:
                st.cold_since = now_ts
            big = dev >= st.boost_threshold + BOOST_IMMEDIATE_EXTRA
            if big or now_ts - st.cold_since >= st.boost_delay_s:
                st.boost_wanted = True
        else:
            st.cold_since = None
        return st.boost_wanted

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
                if not at_boost:
                    await self._async_drop_boost(valve_id)  # visszaállt
                elif now_ts - rec["ts"] > RESTORE_RETRY_SECONDS:
                    await self._async_restore(valve_id, state, rec)
                return
            if not at_boost:
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
