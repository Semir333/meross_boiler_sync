"""Meross Boiler Sync: a radiátor szelepek hőigénye alapján vezérli a kazán termosztátot."""
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta

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
from homeassistant.util import dt as dt_util

from .const import (
    CONF_BOILER,
    CONF_BOILER_ON_TEMP,
    CONF_HYSTERESIS,
    CONF_MIN_SWITCH_TIME,
    CONF_VALVES,
    DEFAULT_BOILER_ON_TEMP,
    DEFAULT_HYSTERESIS,
    DEFAULT_MIN_SWITCH_TIME,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

TICK = timedelta(seconds=60)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = BoilerController(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await controller.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller: BoilerController = hass.data[DOMAIN].pop(entry.entry_id)
    controller.async_stop()
    return True


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


class BoilerController:
    """Összeköti a szelepeket és a kazán termosztátot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        cfg = {**entry.data, **entry.options}
        self.hass = hass
        self.boiler: str = cfg[CONF_BOILER]
        self.valves: list[str] = list(cfg[CONF_VALVES])
        self.hysteresis = float(cfg.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))
        self.min_switch = timedelta(
            minutes=float(cfg.get(CONF_MIN_SWITCH_TIME, DEFAULT_MIN_SWITCH_TIME))
        )
        self.on_temp = float(cfg.get(CONF_BOILER_ON_TEMP, DEFAULT_BOILER_ON_TEMP))

        self._calling: set[str] = set()
        self._last_switch = None
        self._unsubs: list = []
        self._retry_unsub = None
        self._lock = asyncio.Lock()

    # ------------------------------------------------------------------ életciklus
    async def async_start(self) -> None:
        self._unsubs.append(
            async_track_state_change_event(
                self.hass, [self.boiler, *self.valves], self._handle_event
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

    # ------------------------------------------------------------------ logika
    def _update_calling(self) -> bool | None:
        """Frissíti, mely szelepek kérnek hőt. None, ha egyik szelep sem elérhető."""
        reachable = 0
        for entity_id in self.valves:
            state = self.hass.states.get(entity_id)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                self._calling.discard(entity_id)
                continue
            reachable += 1
            if state.state == HVACMode.OFF:
                self._calling.discard(entity_id)
                continue
            try:
                current = float(state.attributes["current_temperature"])
                target = float(state.attributes["temperature"])
            except (KeyError, TypeError, ValueError):
                self._calling.discard(entity_id)
                continue

            if entity_id in self._calling:
                # addig kér hőt, amíg el nem éri a célt
                if current >= target:
                    self._calling.discard(entity_id)
            elif current < target - self.hysteresis:
                self._calling.add(entity_id)

        if reachable == 0:
            return None
        return bool(self._calling)

    async def async_evaluate(self) -> None:
        async with self._lock:
            demand = self._update_calling()
            if demand is None:
                # egyetlen szelep sem elérhető: nem nyúlunk a kazánhoz
                return

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
                    "Kazán %s (hőt kérő szelepek: %s)",
                    "BE" if demand else "KI",
                    ", ".join(sorted(self._calling)) or "-",
                )

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
