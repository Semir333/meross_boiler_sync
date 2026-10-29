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
    CONF_ROOM_VALVES,
    CONF_ROOMS,
    CONF_SUMMER_END,
    CONF_SUMMER_START,
    CONF_SUMMER_TEMP,
    DEFAULT_BOILER_ON_TEMP,
    DEFAULT_HUMIDITY_MAX_BOOST,
    DEFAULT_HYSTERESIS,
    DEFAULT_MIN_SWITCH_TIME,
    DEFAULT_SUMMER_END,
    DEFAULT_SUMMER_START,
    DEFAULT_SUMMER_TEMP,
    DOMAIN,
    HUMIDITY_FULL,
    HUMIDITY_START,
    MAX_EFFECTIVE_TARGET,
    SAMPLE_INTERVAL_SECONDS,
    STORAGE_VERSION,
    SUMMER_HYSTERESIS,
    parse_month_day,
)

_LOGGER = logging.getLogger(__name__)

TICK = timedelta(seconds=60)


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
            room[CONF_ROOM_ID]: RoomStatus(
                room_id=room[CONF_ROOM_ID],
                name=room[CONF_ROOM_NAME],
                valves=list(room[CONF_ROOM_VALVES]),
            )
            for room in self.rooms
        }

        self._last_switch = None
        self._prev_summer = False
        self._unsubs: list[Callable[[], None]] = []
        self._retry_unsub: Callable[[], None] | None = None
        self._listeners: list[Callable[[], None]] = []
        self._lock = asyncio.Lock()

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
        return {"samples": [[ts, val] for ts, val in self._samples]}

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
        reachable = 0
        for valve_id in room[CONF_ROOM_VALVES]:
            state = self.hass.states.get(valve_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                continue
            reachable += 1
            if state.state == HVACMode.OFF:
                continue
            try:
                targets.append(float(state.attributes["temperature"]))
            except (KeyError, TypeError, ValueError):
                pass
            try:
                valve_temps.append(float(state.attributes["current_temperature"]))
            except (KeyError, TypeError, ValueError):
                pass

        st.reachable = reachable > 0
        st.active = bool(targets)
        st.current = st.source = st.target = st.effective_target = None
        st.humidity = None
        st.humidity_boost = 0.0

        if not targets:
            st.calling = False
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

        # hőigény hiszterézissel: indul, ha a cél alatt van, megy a cél eléréséig
        if current is None:
            st.calling = False
        elif st.calling:
            if current >= st.effective_target:
                st.calling = False
        elif current < st.effective_target - self.hysteresis:
            st.calling = True
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

        if not statuses or not any(st.reachable for st in statuses):
            # nincs szoba, vagy egyik szelep sem elérhető: nem nyúlunk a kazánhoz
            return

        demand = any(st.calling for st in statuses)

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
                    + ", ".join(st.name for st in statuses if st.calling)
                    if demand
                    else "nyári mód" if self.summer_active else "nincs hőigény"
                ),
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
        try:
            await self.hass.services.async_call(
                "climate",
                service,
                {"entity_id": self.boiler, **data},
                blocking=True,
            )
        except HomeAssistantError as err:
            _LOGGER.warning("climate.%s hiba a(z) %s-en: %s", service, self.boiler, err)
            return False
        return True
