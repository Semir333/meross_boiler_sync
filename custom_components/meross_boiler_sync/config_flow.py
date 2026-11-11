"""Konfigurációs folyamat: kazán kiválasztása, majd szobák és nyári mód az opciókban."""
from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .offset import room_trv_offset, room_valve_offsets
from .const import (
    CONF_BOILER,
    CONF_BOILER_MIN_OFF,
    CONF_BOILER_MIN_ON,
    CONF_BOILER_ON_TEMP,
    CONF_CALIBRATION_DRY_RUN,
    CONF_CALIBRATION_ENABLED,
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
    CONF_GAS_ESTIMATE,
    CONF_GAS_M3_PER_HOUR,
    CONF_RESIDUAL_ALLOW,
    CONF_RESIDUAL_COMP,
    CONF_PREHEAT_DEFAULT_RATE,
    CONF_PREHEAT_ENABLED,
    CONF_PREHEAT_HOLD_MINUTES,
    CONF_PREHEAT_MAX_MINUTES,
    CONF_OUTDOOR_SENSOR,
    CONF_ROOM_CALIBRATE,
    CONF_ROOM_TRV_OFFSET_SIGNED,
    CONF_ROOM_VALVE_OFFSETS,
    CONF_ROOM_HUM,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_PREHEAT,
    CONF_ROOM_TEMP,
    CONF_ROOM_VALVE_CONTROL,
    CONF_REGISTER_CARD,
    CONF_ROOM_VALVE_LINK,
    CONF_ROOM_VALVES,
    CONF_ROOM_WINDOWS,
    CONF_ROOMS,
    CONF_SUMMER_END,
    CONF_SUMMER_START,
    CONF_MAX_BOOST_ENABLED,
    CONF_MAX_BOOST_HOURS,
    CONF_MAX_BOOST_REST,
    CONF_STALE_ENABLED,
    CONF_STALE_HOURS,
    CONF_SUMMER_TEMP,
    CONF_TRV_LOG,
    CONF_VALVE_BOOST_DELAY,
    CONF_VALVE_BOOST_THRESHOLD,
    CONF_VALVE_DRY_RUN,
    CONF_VALVE_RELEASE_MARGIN,
    CONF_WINDOW_DELAY,
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
    DEFAULT_GAS_ESTIMATE,
    DEFAULT_GAS_M3_PER_HOUR,
    DEFAULT_RESIDUAL_ALLOW,
    DEFAULT_RESIDUAL_COMP,
    DEFAULT_PREHEAT_RATE,
    DEFAULT_SUMMER_END,
    DEFAULT_SUMMER_START,
    DEFAULT_MAX_BOOST_ENABLED,
    DEFAULT_MAX_BOOST_HOURS,
    DEFAULT_MAX_BOOST_REST,
    DEFAULT_REGISTER_CARD,
    DEFAULT_ROOM_CALIBRATE,
    DEFAULT_TRV_OFFSET,
    DEFAULT_STALE_ENABLED,
    DEFAULT_STALE_HOURS,
    DEFAULT_SUMMER_TEMP,
    DEFAULT_TRV_LOG,
    DEFAULT_VALVE_BOOST_DELAY,
    DEFAULT_VALVE_BOOST_THRESHOLD,
    DEFAULT_VALVE_DRY_RUN,
    DEFAULT_VALVE_RELEASE_MARGIN,
    DEFAULT_WINDOW_DELAY,
    DOMAIN,
    MAX_VALVE_OFFSET_FIELDS,
    RESIDUAL_ALLOW_MAX,
    TRV_OFFSET_MAX,
    TRV_OFFSET_MIN_ACTIVE,
    parse_month_day,
)

CONF_PICK_ROOM = "room"
CONF_REMOVE_ROOMS = "rooms_to_remove"


# ------------------------------------------------------------------ selectorok
def _entity(domain: str, device_class: str | None = None, multiple: bool = False):
    cfg: dict[str, Any] = {"domain": domain, "multiple": multiple}
    if device_class:
        cfg["device_class"] = device_class
    return selector.EntitySelector(selector.EntitySelectorConfig(**cfg))


def _number(minimum: float, maximum: float, step: float, unit: str):
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum,
            max=maximum,
            step=step,
            mode=selector.NumberSelectorMode.BOX,
            unit_of_measurement=unit,
        )
    )


def _suggest(values: dict[str, Any], key: str) -> dict[str, Any]:
    return {"suggested_value": values.get(key)}


# ------------------------------------------------------------------ sémák
def _trv_offset_default(values: dict[str, Any]) -> float:
    """Az űrlapon felajánlott TRV eltolás (előjeles): a szoba mentett értéke, ennek hiányában az alapérték. A 2.16 és régebbi
    verziókban mentett (ellentétes előjelű) érték átszámolva jelenik meg, ugyanúgy, ahogy a vezérlő használja."""
    return room_trv_offset(values)


def _room_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_ROOM_NAME, description=_suggest(values, CONF_ROOM_NAME)
            ): selector.TextSelector(),
            vol.Required(
                CONF_ROOM_VALVES, description=_suggest(values, CONF_ROOM_VALVES)
            ): _entity("climate", multiple=True),
            vol.Optional(
                CONF_ROOM_TEMP, description=_suggest(values, CONF_ROOM_TEMP)
            ): _entity("sensor", "temperature"),
            vol.Optional(
                CONF_ROOM_VALVE_CONTROL,
                default=bool(values.get(CONF_ROOM_VALVE_CONTROL, False)),
            ): selector.BooleanSelector(),
            vol.Optional(
                CONF_VALVE_BOOST_THRESHOLD,
                description=_suggest(values, CONF_VALVE_BOOST_THRESHOLD),
            ): _number(0.1, 3, 0.1, "°C"),
            vol.Optional(
                CONF_VALVE_BOOST_DELAY,
                description=_suggest(values, CONF_VALVE_BOOST_DELAY),
            ): _number(0, 60, 1, "min"),
            vol.Optional(
                CONF_VALVE_RELEASE_MARGIN,
                description=_suggest(values, CONF_VALVE_RELEASE_MARGIN),
            ): _number(0, 2, 0.1, "°C"),
            vol.Optional(
                CONF_ROOM_VALVE_LINK,
                default=bool(values.get(CONF_ROOM_VALVE_LINK, False)),
            ): selector.BooleanSelector(),
            vol.Optional(
                CONF_ROOM_HUM, description=_suggest(values, CONF_ROOM_HUM)
            ): _entity("sensor", "humidity"),
            vol.Optional(
                CONF_ROOM_WINDOWS, description=_suggest(values, CONF_ROOM_WINDOWS)
            ): _entity("binary_sensor", ["window", "door", "opening"], multiple=True),
            vol.Optional(
                CONF_WINDOW_DELAY, description=_suggest(values, CONF_WINDOW_DELAY)
            ): _number(0, 120, 1, "min"),
            vol.Optional(
                CONF_ROOM_CALIBRATE,
                default=bool(values.get(CONF_ROOM_CALIBRATE, DEFAULT_ROOM_CALIBRATE)),
            ): selector.BooleanSelector(),
            vol.Optional(
                CONF_ROOM_TRV_OFFSET_SIGNED,
                default=_trv_offset_default(values),
            ): _number(-TRV_OFFSET_MAX, TRV_OFFSET_MAX, 0.5, "°C"),
        }
    )


def _valve_field(index: int) -> str:
    """2.18: a szelepenkénti eltolás mezőjének kulcsa (1-től): `valve_offset_1`, `valve_offset_2`, ... A kulcs szám szerinti,
    hogy a mezők címkéje a többi mezőhöz hasonlóan statikus fordítás lehessen; hogy melyik szám melyik szelep, azt az űrlap
    leírása sorolja fel (a szelep neve és entitás-azonosítója)."""
    return f"valve_offset_{index}"


def _valve_offsets_schema(count: int, values: dict[str, Any]) -> vol.Schema:
    """2.18: egy mező szelepenként (`count` darab), mind elhagyható: az üres mező azt jelenti, hogy a szelep a szoba eltolását
    használja. A javasolt érték a szelep mentett egyedi eltolása (a `values` a mező kulcsa szerint adja)."""
    return vol.Schema(
        {
            vol.Optional(
                _valve_field(index), description=_suggest(values, _valve_field(index))
            ): _number(-TRV_OFFSET_MAX, TRV_OFFSET_MAX, 0.5, "°C")
            for index in range(1, count + 1)
        }
    )


def _offset_invalid(offset: Any) -> bool:
    """Az eltolás megadott értéke nem érvényes: abszolút értéke nagyobb a megengedettnél, vagy nem nulla, de kisebb a
    legkisebb aktív értéknél (a szelep kalibrációjának legkisebb lépése 0,5 °C)."""
    return abs(float(offset)) > TRV_OFFSET_MAX or 0 < abs(float(offset)) < TRV_OFFSET_MIN_ACTIVE


def _validate_valve_offsets(user_input: dict[str, Any], count: int) -> dict[str, str]:
    """2.18: a szelepenkénti eltolások ellenőrzése; a hibás mező mellett jelenik meg a hiba."""
    errors: dict[str, str] = {}
    for index in range(1, count + 1):
        value = user_input.get(_valve_field(index))
        if value is not None and _offset_invalid(value):
            errors[_valve_field(index)] = "trv_offset_range"
    return errors


def _offset_text(value: float) -> str:
    """Az eltolás a leírásban: előjellel, egy tizedessel ("-1.0", "+1.5"), a nulla előjel nélkül."""
    return "0" if value == 0 else f"{value:+.1f}"


def _markdown_safe(text: str) -> str:
    """A leírásba kerülő név: sortörés és kód-jelölő nélkül, hogy ne törje szét a felsorolást."""
    return " ".join(str(text).replace("`", "'").split())


def _settings_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_HYSTERESIS,
                default=values.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS),
            ): _number(0, 3, 0.1, "°C"),
            vol.Required(
                CONF_MIN_SWITCH_TIME,
                default=values.get(CONF_MIN_SWITCH_TIME, DEFAULT_MIN_SWITCH_TIME),
            ): _number(0, 60, 1, "min"),
            vol.Required(
                CONF_BOILER_ON_TEMP,
                default=values.get(CONF_BOILER_ON_TEMP, DEFAULT_BOILER_ON_TEMP),
            ): _number(0, 35, 1, "°C"),
            vol.Required(
                CONF_HUMIDITY_MAX_BOOST,
                default=values.get(CONF_HUMIDITY_MAX_BOOST, DEFAULT_HUMIDITY_MAX_BOOST),
            ): _number(0, 2, 0.1, "°C"),
            vol.Required(
                CONF_VALVE_BOOST_THRESHOLD,
                default=values.get(
                    CONF_VALVE_BOOST_THRESHOLD, DEFAULT_VALVE_BOOST_THRESHOLD
                ),
            ): _number(0.1, 3, 0.1, "°C"),
            vol.Required(
                CONF_VALVE_BOOST_DELAY,
                default=values.get(CONF_VALVE_BOOST_DELAY, DEFAULT_VALVE_BOOST_DELAY),
            ): _number(0, 60, 1, "min"),
            vol.Required(
                CONF_VALVE_RELEASE_MARGIN,
                default=values.get(
                    CONF_VALVE_RELEASE_MARGIN, DEFAULT_VALVE_RELEASE_MARGIN
                ),
            ): _number(0, 2, 0.1, "°C"),
            vol.Required(
                CONF_STALE_ENABLED,
                default=bool(values.get(CONF_STALE_ENABLED, DEFAULT_STALE_ENABLED)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_STALE_HOURS,
                default=values.get(CONF_STALE_HOURS, DEFAULT_STALE_HOURS),
            ): _number(1, 72, 1, "h"),
            vol.Required(
                CONF_MAX_BOOST_ENABLED,
                default=bool(
                    values.get(CONF_MAX_BOOST_ENABLED, DEFAULT_MAX_BOOST_ENABLED)
                ),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_MAX_BOOST_HOURS,
                default=values.get(CONF_MAX_BOOST_HOURS, DEFAULT_MAX_BOOST_HOURS),
            ): _number(0.5, 24, 0.5, "h"),
            vol.Required(
                CONF_MAX_BOOST_REST,
                default=values.get(CONF_MAX_BOOST_REST, DEFAULT_MAX_BOOST_REST),
            ): _number(0, 480, 5, "min"),
            vol.Required(
                CONF_WINDOW_DELAY,
                default=values.get(CONF_WINDOW_DELAY, DEFAULT_WINDOW_DELAY),
            ): _number(0, 120, 1, "min"),
            vol.Required(
                CONF_VALVE_DRY_RUN,
                default=bool(values.get(CONF_VALVE_DRY_RUN, DEFAULT_VALVE_DRY_RUN)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_REGISTER_CARD,
                default=bool(values.get(CONF_REGISTER_CARD, DEFAULT_REGISTER_CARD)),
            ): selector.BooleanSelector(),
        }
    )


def _features_schema(values: dict[str, Any]) -> vol.Schema:
    """Események, kazán-ciklusok figyelése és az opcionális kazán védelem (mind kapcsolható)."""
    return vol.Schema(
        {
            vol.Required(
                CONF_EVENTS_ENABLED,
                default=bool(values.get(CONF_EVENTS_ENABLED, DEFAULT_EVENTS_ENABLED)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_TRV_LOG,
                default=bool(values.get(CONF_TRV_LOG, DEFAULT_TRV_LOG)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_CYCLE_MONITOR,
                default=bool(values.get(CONF_CYCLE_MONITOR, DEFAULT_CYCLE_MONITOR)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_CYCLE_MAX_STARTS,
                default=values.get(CONF_CYCLE_MAX_STARTS, DEFAULT_CYCLE_MAX_STARTS),
            ): _number(1, 30, 1, "×/h"),
            vol.Required(
                CONF_CYCLE_MIN_AVG_ON,
                default=values.get(CONF_CYCLE_MIN_AVG_ON, DEFAULT_CYCLE_MIN_AVG_ON),
            ): _number(0, 30, 1, "min"),
            vol.Required(
                CONF_CYCLE_PROTECTION,
                default=bool(values.get(CONF_CYCLE_PROTECTION, DEFAULT_CYCLE_PROTECTION)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_BOILER_MIN_ON,
                default=values.get(CONF_BOILER_MIN_ON, DEFAULT_BOILER_MIN_ON),
            ): _number(0, 60, 1, "min"),
            vol.Required(
                CONF_BOILER_MIN_OFF,
                default=values.get(CONF_BOILER_MIN_OFF, DEFAULT_BOILER_MIN_OFF),
            ): _number(0, 60, 1, "min"),
            vol.Required(
                CONF_MANUAL_BOOST_ENABLED,
                default=bool(values.get(CONF_MANUAL_BOOST_ENABLED, DEFAULT_MANUAL_BOOST_ENABLED)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_MANUAL_BOOST_MINUTES,
                default=values.get(CONF_MANUAL_BOOST_MINUTES, DEFAULT_MANUAL_BOOST_MINUTES),
            ): _number(5, 480, 5, "min"),
            vol.Required(
                CONF_MANUAL_BOOST_OFFSET,
                default=values.get(CONF_MANUAL_BOOST_OFFSET, DEFAULT_MANUAL_BOOST_OFFSET),
            ): _number(0.5, 5, 0.5, "°C"),
            vol.Required(
                CONF_MANUAL_BOOST_END_ON_TARGET,
                default=bool(
                    values.get(CONF_MANUAL_BOOST_END_ON_TARGET, DEFAULT_MANUAL_BOOST_END_ON_TARGET)
                ),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_PREHEAT_ENABLED,
                default=bool(values.get(CONF_PREHEAT_ENABLED, DEFAULT_PREHEAT_ENABLED)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_PREHEAT_MAX_MINUTES,
                default=values.get(CONF_PREHEAT_MAX_MINUTES, DEFAULT_PREHEAT_MAX_MINUTES),
            ): _number(30, 480, 15, "min"),
            vol.Required(
                CONF_PREHEAT_HOLD_MINUTES,
                default=values.get(CONF_PREHEAT_HOLD_MINUTES, DEFAULT_PREHEAT_HOLD_MINUTES),
            ): _number(0, 180, 5, "min"),
            vol.Required(
                CONF_PREHEAT_DEFAULT_RATE,
                default=values.get(CONF_PREHEAT_DEFAULT_RATE, DEFAULT_PREHEAT_RATE),
            ): _number(0.2, 4, 0.1, "°C/h"),
            vol.Required(
                CONF_GAS_ESTIMATE,
                default=bool(values.get(CONF_GAS_ESTIMATE, DEFAULT_GAS_ESTIMATE)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_GAS_M3_PER_HOUR,
                default=values.get(CONF_GAS_M3_PER_HOUR, DEFAULT_GAS_M3_PER_HOUR),
            ): _number(0.1, 20, 0.1, "m³/h"),
            vol.Required(
                CONF_CALIBRATION_ENABLED,
                default=bool(values.get(CONF_CALIBRATION_ENABLED, DEFAULT_CALIBRATION_ENABLED)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_CALIBRATION_DRY_RUN,
                default=bool(values.get(CONF_CALIBRATION_DRY_RUN, DEFAULT_CALIBRATION_DRY_RUN)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_RESIDUAL_COMP,
                default=bool(values.get(CONF_RESIDUAL_COMP, DEFAULT_RESIDUAL_COMP)),
            ): selector.BooleanSelector(),
            vol.Required(
                CONF_RESIDUAL_ALLOW,
                default=values.get(CONF_RESIDUAL_ALLOW, DEFAULT_RESIDUAL_ALLOW),
            ): _number(0, RESIDUAL_ALLOW_MAX, 0.1, "°C"),
        }
    )


# ------------------------------------------------------------------ előfűtés menetrend
CONF_PICK_ENTRIES = "entries_to_remove"
ATTR_DAYS = "days"
ATTR_TIME = "time"
ATTR_TEMPERATURE = "temperature"
_DAYS_HU = ["H", "K", "Sze", "Cs", "P", "Szo", "V"]
_DAYS_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def schedule_text(entry: dict[str, Any], hu: bool) -> str:
    """Egy menetrendi sor olvasható szövege, pl. "H, K, Sze, Cs, P 06:30 → 22 °C"."""
    names = _DAYS_HU if hu else _DAYS_EN
    days = sorted({int(d) for d in entry.get(ATTR_DAYS, []) if 0 <= int(d) <= 6})
    if days == list(range(7)):
        label = "minden nap" if hu else "every day"
    elif days == [0, 1, 2, 3, 4]:
        label = "H–P" if hu else "Mon–Fri"
    elif days == [5, 6]:
        label = "Szo–V" if hu else "Sat–Sun"
    else:
        label = ", ".join(names[d] for d in days)
    temp = float(entry.get(ATTR_TEMPERATURE, 0))
    return f"{label} {entry.get(ATTR_TIME, '')} → {temp:g} °C"


def _schedule_add_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                ATTR_DAYS, default=values.get(ATTR_DAYS, ["0", "1", "2", "3", "4"])
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[str(d) for d in range(7)],
                    multiple=True,
                    mode=selector.SelectSelectorMode.LIST,
                    translation_key="preheat_days",
                )
            ),
            vol.Required(
                ATTR_TIME, default=values.get(ATTR_TIME, "06:30:00")
            ): selector.TimeSelector(),
            vol.Required(
                ATTR_TEMPERATURE, default=values.get(ATTR_TEMPERATURE, 21.0)
            ): _number(5, 30, 0.5, "°C"),
        }
    )


def _summer_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_OUTDOOR_SENSOR, description=_suggest(values, CONF_OUTDOOR_SENSOR)
            ): _entity("sensor", "temperature"),
            vol.Required(
                CONF_SUMMER_TEMP,
                default=values.get(CONF_SUMMER_TEMP, DEFAULT_SUMMER_TEMP),
            ): _number(0, 35, 0.5, "°C"),
            vol.Required(
                CONF_SUMMER_START,
                default=values.get(CONF_SUMMER_START, DEFAULT_SUMMER_START),
            ): selector.TextSelector(),
            vol.Required(
                CONF_SUMMER_END,
                default=values.get(CONF_SUMMER_END, DEFAULT_SUMMER_END),
            ): selector.TextSelector(),
        }
    )


def _validate_settings(user_input: dict[str, Any]) -> dict[str, str]:
    if float(user_input[CONF_VALVE_RELEASE_MARGIN]) >= float(
        user_input[CONF_VALVE_BOOST_THRESHOLD]
    ):
        return {CONF_VALVE_RELEASE_MARGIN: "release_ge_threshold"}
    return {}


def _validate_summer(user_input: dict[str, Any]) -> dict[str, str]:
    errors: dict[str, str] = {}
    if parse_month_day(user_input.get(CONF_SUMMER_START)) is None:
        errors[CONF_SUMMER_START] = "invalid_date"
    if parse_month_day(user_input.get(CONF_SUMMER_END)) is None:
        errors[CONF_SUMMER_END] = "invalid_date"
    return errors


# ------------------------------------------------------------------ config flow
class MerossBoilerSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_BOILER])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Meross Boiler Sync",
                data={CONF_BOILER: user_input[CONF_BOILER]},
                options={
                    CONF_HYSTERESIS: DEFAULT_HYSTERESIS,
                    CONF_MIN_SWITCH_TIME: DEFAULT_MIN_SWITCH_TIME,
                    CONF_BOILER_ON_TEMP: DEFAULT_BOILER_ON_TEMP,
                    CONF_HUMIDITY_MAX_BOOST: DEFAULT_HUMIDITY_MAX_BOOST,
                    CONF_VALVE_DRY_RUN: DEFAULT_VALVE_DRY_RUN,
                    CONF_WINDOW_DELAY: DEFAULT_WINDOW_DELAY,
                    CONF_REGISTER_CARD: DEFAULT_REGISTER_CARD,
                    CONF_STALE_ENABLED: DEFAULT_STALE_ENABLED,
                    CONF_STALE_HOURS: DEFAULT_STALE_HOURS,
                    CONF_MAX_BOOST_ENABLED: DEFAULT_MAX_BOOST_ENABLED,
                    CONF_MAX_BOOST_HOURS: DEFAULT_MAX_BOOST_HOURS,
                    CONF_MAX_BOOST_REST: DEFAULT_MAX_BOOST_REST,
                    CONF_VALVE_BOOST_THRESHOLD: DEFAULT_VALVE_BOOST_THRESHOLD,
                    CONF_VALVE_BOOST_DELAY: DEFAULT_VALVE_BOOST_DELAY,
                    CONF_VALVE_RELEASE_MARGIN: DEFAULT_VALVE_RELEASE_MARGIN,
                    CONF_SUMMER_TEMP: DEFAULT_SUMMER_TEMP,
                    CONF_SUMMER_START: DEFAULT_SUMMER_START,
                    CONF_SUMMER_END: DEFAULT_SUMMER_END,
                    CONF_EVENTS_ENABLED: DEFAULT_EVENTS_ENABLED,
                    CONF_TRV_LOG: DEFAULT_TRV_LOG,
                    CONF_CYCLE_MONITOR: DEFAULT_CYCLE_MONITOR,
                    CONF_CYCLE_MAX_STARTS: DEFAULT_CYCLE_MAX_STARTS,
                    CONF_CYCLE_MIN_AVG_ON: DEFAULT_CYCLE_MIN_AVG_ON,
                    CONF_CYCLE_PROTECTION: DEFAULT_CYCLE_PROTECTION,
                    CONF_BOILER_MIN_ON: DEFAULT_BOILER_MIN_ON,
                    CONF_BOILER_MIN_OFF: DEFAULT_BOILER_MIN_OFF,
                    CONF_MANUAL_BOOST_ENABLED: DEFAULT_MANUAL_BOOST_ENABLED,
                    CONF_MANUAL_BOOST_MINUTES: DEFAULT_MANUAL_BOOST_MINUTES,
                    CONF_MANUAL_BOOST_OFFSET: DEFAULT_MANUAL_BOOST_OFFSET,
                    CONF_MANUAL_BOOST_END_ON_TARGET: DEFAULT_MANUAL_BOOST_END_ON_TARGET,
                    CONF_PREHEAT_ENABLED: DEFAULT_PREHEAT_ENABLED,
                    CONF_PREHEAT_MAX_MINUTES: DEFAULT_PREHEAT_MAX_MINUTES,
                    CONF_PREHEAT_HOLD_MINUTES: DEFAULT_PREHEAT_HOLD_MINUTES,
                    CONF_PREHEAT_DEFAULT_RATE: DEFAULT_PREHEAT_RATE,
                    CONF_GAS_ESTIMATE: DEFAULT_GAS_ESTIMATE,
                    CONF_GAS_M3_PER_HOUR: DEFAULT_GAS_M3_PER_HOUR,
                    CONF_CALIBRATION_ENABLED: DEFAULT_CALIBRATION_ENABLED,
                    CONF_CALIBRATION_DRY_RUN: DEFAULT_CALIBRATION_DRY_RUN,
                    CONF_RESIDUAL_COMP: DEFAULT_RESIDUAL_COMP,
                    CONF_RESIDUAL_ALLOW: DEFAULT_RESIDUAL_ALLOW,
                    CONF_ROOMS: [],
                },
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_BOILER): _entity("climate")}
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return MerossBoilerSyncOptionsFlow()


# ------------------------------------------------------------------ options flow
class MerossBoilerSyncOptionsFlow(config_entries.OptionsFlow):
    """Menü: szoba hozzáadás/szerkesztés/törlés, alapbeállítások, nyári mód, mentés."""

    def __init__(self) -> None:
        self._opts: dict[str, Any] | None = None
        self._edit_id: str | None = None
        self._offsets_id: str | None = None  # 2.18: az a szoba, amelynek a szelepenkénti eltolását szerkesztjük

    def _load(self) -> dict[str, Any]:
        if self._opts is None:
            opts = dict(self.config_entry.options)
            opts[CONF_ROOMS] = [dict(room) for room in opts.get(CONF_ROOMS, [])]
            self._opts = opts
        return self._opts

    def _room_options(self) -> list[dict[str, str]]:
        return [
            {"value": room[CONF_ROOM_ID], "label": room[CONF_ROOM_NAME]}
            for room in self._load()[CONF_ROOMS]
        ]

    def _validate_room(
        self, user_input: dict[str, Any], editing_id: str | None
    ) -> dict[str, str]:
        rooms = self._load()[CONF_ROOMS]
        name = (user_input.get(CONF_ROOM_NAME) or "").strip()
        if not name:
            return {CONF_ROOM_NAME: "no_name"}
        others = [room for room in rooms if room[CONF_ROOM_ID] != editing_id]
        if any(room[CONF_ROOM_NAME].lower() == name.lower() for room in others):
            return {CONF_ROOM_NAME: "duplicate_name"}
        valves = set(user_input.get(CONF_ROOM_VALVES) or [])
        if not valves:
            return {CONF_ROOM_VALVES: "no_valves"}
        if self.config_entry.data[CONF_BOILER] in valves:
            return {CONF_ROOM_VALVES: "boiler_in_valves"}
        if any(valves & set(room[CONF_ROOM_VALVES]) for room in others):
            return {CONF_ROOM_VALVES: "valve_in_use"}
        defaults = self._load()
        threshold = user_input.get(CONF_VALVE_BOOST_THRESHOLD)
        if threshold is None:
            threshold = defaults.get(CONF_VALVE_BOOST_THRESHOLD, DEFAULT_VALVE_BOOST_THRESHOLD)
        release = user_input.get(CONF_VALVE_RELEASE_MARGIN)
        if release is None:
            release = defaults.get(CONF_VALVE_RELEASE_MARGIN, DEFAULT_VALVE_RELEASE_MARGIN)
        if float(release) >= float(threshold):
            return {CONF_VALVE_RELEASE_MARGIN: "release_ge_threshold"}
        if user_input.get(CONF_ROOM_VALVE_CONTROL) and not user_input.get(CONF_ROOM_TEMP):
            return {CONF_ROOM_VALVE_CONTROL: "control_needs_sensor"}
        offset = user_input.get(CONF_ROOM_TRV_OFFSET_SIGNED)
        if offset is not None and _offset_invalid(offset):
            return {CONF_ROOM_TRV_OFFSET_SIGNED: "trv_offset_range"}
        return {}

    @staticmethod
    def _room_from_input(user_input: dict[str, Any], room_id: str) -> dict[str, Any]:
        room: dict[str, Any] = {
            CONF_ROOM_ID: room_id,
            CONF_ROOM_NAME: user_input[CONF_ROOM_NAME].strip(),
            CONF_ROOM_VALVES: list(user_input[CONF_ROOM_VALVES]),
        }
        for key in (CONF_ROOM_TEMP, CONF_ROOM_HUM):
            if user_input.get(key):
                room[key] = user_input[key]
        for key in (
            CONF_VALVE_BOOST_THRESHOLD,
            CONF_VALVE_BOOST_DELAY,
            CONF_VALVE_RELEASE_MARGIN,
            CONF_WINDOW_DELAY,
        ):
            if user_input.get(key) is not None:  # a 0 is érvényes érték
                room[key] = float(user_input[key])
        room[CONF_ROOM_VALVE_LINK] = bool(user_input.get(CONF_ROOM_VALVE_LINK))
        room[CONF_ROOM_CALIBRATE] = bool(user_input.get(CONF_ROOM_CALIBRATE, DEFAULT_ROOM_CALIBRATE))
        offset = user_input.get(CONF_ROOM_TRV_OFFSET_SIGNED)
        room[CONF_ROOM_TRV_OFFSET_SIGNED] = DEFAULT_TRV_OFFSET if offset is None else float(offset) + 0.0  # a 0 is érvényes
        windows = [w for w in (user_input.get(CONF_ROOM_WINDOWS) or []) if w]
        if windows:
            room[CONF_ROOM_WINDOWS] = windows
        room[CONF_ROOM_VALVE_CONTROL] = bool(
            user_input.get(CONF_ROOM_VALVE_CONTROL) and user_input.get(CONF_ROOM_TEMP)
        )
        return room

    # --- főmenü
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        menu = ["add_room"]
        if opts[CONF_ROOMS]:
            menu += ["edit_room", "remove_room", "preheat"]
        menu += ["settings", "features", "summer", "done"]
        names = ", ".join(room[CONF_ROOM_NAME] for room in opts[CONF_ROOMS]) or "–"
        return self.async_show_menu(
            step_id="init",
            menu_options=menu,
            description_placeholders={"rooms": names},
        )

    # --- szoba hozzáadása
    async def async_step_add_room(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = self._validate_room(user_input, None)
            if not errors:
                room_id = uuid.uuid4().hex[:8]
                opts[CONF_ROOMS].append(self._room_from_input(user_input, room_id))
                return await self._async_after_room(room_id)
        return self.async_show_form(
            step_id="add_room",
            data_schema=_room_schema(user_input or {}),
            errors=errors,
        )

    # --- szoba szerkesztése
    async def async_step_edit_room(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._edit_id = user_input[CONF_PICK_ROOM]
            return await self.async_step_edit_room_form()
        return self.async_show_form(
            step_id="edit_room",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PICK_ROOM): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._room_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_edit_room_form(
        self, user_input: dict[str, Any] | None = None
    ):
        opts = self._load()
        errors: dict[str, str] = {}
        room = next(
            (r for r in opts[CONF_ROOMS] if r[CONF_ROOM_ID] == self._edit_id), None
        )
        if room is None:
            return await self.async_step_init()
        if user_input is not None:
            errors = self._validate_room(user_input, self._edit_id)
            if not errors:
                index = opts[CONF_ROOMS].index(room)
                updated = self._room_from_input(user_input, self._edit_id)
                if room.get(CONF_ROOM_PREHEAT):  # a menetrendet ez az űrlap nem szerkeszti
                    updated[CONF_ROOM_PREHEAT] = room[CONF_ROOM_PREHEAT]
                # 2.18: a szelepek egyedi eltolását sem ez az űrlap szerkeszti: megmarad azoknál a szelepeknél, amelyek a
                # szobában maradtak. Ha a szobában egynél több szelep nem marad, a szobaszintű mező az egyetlen beállítás
                # (különben egy láthatatlan egyedi érték felülírná azt, amit az űrlap mutat)
                kept = {
                    valve_id: value
                    for valve_id, value in room_valve_offsets(room).items()
                    if valve_id in updated[CONF_ROOM_VALVES]
                }
                if kept and len(updated[CONF_ROOM_VALVES]) >= 2:
                    updated[CONF_ROOM_VALVE_OFFSETS] = kept
                opts[CONF_ROOMS][index] = updated
                return await self._async_after_room(self._edit_id)
        return self.async_show_form(
            step_id="edit_room_form",
            data_schema=_room_schema(user_input or room),
            errors=errors,
        )

    # --- 2.18: szelepenkénti TRV eltolás (több szelepes szoba)
    async def _async_after_room(self, room_id: str | None):
        """A szoba mentése után: több szelepes szobánál a szelepenkénti eltolás lépése, különben a főmenü."""
        room = next((r for r in self._load()[CONF_ROOMS] if r[CONF_ROOM_ID] == room_id), None)
        if room is not None and len(room[CONF_ROOM_VALVES]) >= 2:
            self._offsets_id = room_id
            return await self.async_step_valve_offsets()
        return await self.async_step_init()

    def _valve_title(self, valve_id: str) -> str:
        """A szelep a leírásban: "**név** (`entitás`)"; ha nincs (más) neve, csak az entitás-azonosító."""
        name = None
        try:
            state = self.hass.states.get(valve_id)
            name = state.attributes.get("friendly_name") if state is not None else None
        except Exception:  # noqa: BLE001 - a név csak szépítés: hiányában az azonosító is elég
            name = None
        name = _markdown_safe(name) if name else ""
        if name and name != valve_id:
            return f"**{name}** (`{valve_id}`)"
        return f"`{valve_id}`"

    async def async_step_valve_offsets(self, user_input: dict[str, Any] | None = None):
        """2.18: a több szelepes szoba szelepeinek külön TRV eltolása. A mezők a szelepek sorrendjében követik egymást, a leírás
        felsorolja, melyik szám melyik szelep (név és entitás-azonosító). Az üres mező: a szelep a szoba eltolását használja."""
        opts = self._load()
        room = next((r for r in opts[CONF_ROOMS] if r[CONF_ROOM_ID] == self._offsets_id), None)
        if room is None or len(room[CONF_ROOM_VALVES]) < 2:
            return await self.async_step_init()
        shown = list(room[CONF_ROOM_VALVES])[:MAX_VALVE_OFFSET_FIELDS]
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_valve_offsets(user_input, len(shown))
            if not errors:
                # a nem szerkeszthető (a mezők számát meghaladó) szelepek értéke változatlan marad
                offsets = {
                    valve_id: value for valve_id, value in room_valve_offsets(room).items() if valve_id not in shown
                }
                for index, valve_id in enumerate(shown, start=1):
                    value = user_input.get(_valve_field(index))
                    if value is not None:  # a 0 is érvényes: az a szelep a szoba hőmérőjét követi
                        offsets[valve_id] = float(value) + 0.0
                if offsets:
                    room[CONF_ROOM_VALVE_OFFSETS] = offsets
                else:
                    room.pop(CONF_ROOM_VALVE_OFFSETS, None)
                self._offsets_id = None  # a lépés kész: a főmenüből nem nyitható meg újra
                return await self.async_step_init()
            values: dict[str, Any] = user_input
        else:
            current = room_valve_offsets(room)
            values = {_valve_field(index): current.get(valve_id) for index, valve_id in enumerate(shown, start=1)}
        return self.async_show_form(
            step_id="valve_offsets",
            data_schema=_valve_offsets_schema(len(shown), values),
            errors=errors,
            description_placeholders={
                "room": room[CONF_ROOM_NAME],
                "room_offset": _offset_text(room_trv_offset(room)),
                "valves": "\n".join(
                    f"{index}. {self._valve_title(valve_id)}" for index, valve_id in enumerate(shown, start=1)
                ),
            },
        )

    # --- szoba törlése
    async def async_step_remove_room(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        if user_input is not None:
            remove = set(user_input.get(CONF_REMOVE_ROOMS) or [])
            opts[CONF_ROOMS] = [
                room for room in opts[CONF_ROOMS] if room[CONF_ROOM_ID] not in remove
            ]
            return await self.async_step_init()
        return self.async_show_form(
            step_id="remove_room",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REMOVE_ROOMS): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._room_options(),
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    # --- alapbeállítások
    async def async_step_settings(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_settings(user_input)
            if not errors:
                opts.update(user_input)
                return await self.async_step_init()
        return self.async_show_form(
            step_id="settings",
            data_schema=_settings_schema(user_input or opts),
            errors=errors,
        )

    # --- előfűtés: szobánkénti heti menetrend
    def _hu(self) -> bool:
        return str(self.hass.config.language or "").lower().startswith("hu")

    def _preheat_room(self) -> dict[str, Any] | None:
        return next(
            (r for r in self._load()[CONF_ROOMS] if r[CONF_ROOM_ID] == self._edit_id), None
        )

    async def async_step_preheat(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._edit_id = user_input[CONF_PICK_ROOM]
            return await self.async_step_preheat_menu()
        return self.async_show_form(
            step_id="preheat",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PICK_ROOM): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=self._room_options(),
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_preheat_menu(self, user_input: dict[str, Any] | None = None):
        room = self._preheat_room()
        if room is None:
            return await self.async_step_init()
        entries = room.get(CONF_ROOM_PREHEAT) or []
        menu = ["preheat_add"] + (["preheat_remove"] if entries else []) + ["init"]
        text = "\n".join(f"- {schedule_text(e, self._hu())}" for e in entries) or "–"
        return self.async_show_menu(
            step_id="preheat_menu",
            menu_options=menu,
            description_placeholders={"room": room[CONF_ROOM_NAME], "entries": text},
        )

    async def async_step_preheat_add(self, user_input: dict[str, Any] | None = None):
        room = self._preheat_room()
        if room is None:
            return await self.async_step_init()
        errors: dict[str, str] = {}
        if user_input is not None:
            days = sorted({int(d) for d in user_input.get(ATTR_DAYS) or []})
            if not days:
                errors[ATTR_DAYS] = "no_days"
            else:
                room.setdefault(CONF_ROOM_PREHEAT, []).append(
                    {
                        ATTR_DAYS: days,
                        ATTR_TIME: str(user_input[ATTR_TIME])[:5],
                        ATTR_TEMPERATURE: float(user_input[ATTR_TEMPERATURE]),
                    }
                )
                return await self.async_step_preheat_menu()
        return self.async_show_form(
            step_id="preheat_add",
            data_schema=_schedule_add_schema(user_input or {}),
            errors=errors,
            description_placeholders={"room": room[CONF_ROOM_NAME]},
        )

    async def async_step_preheat_remove(self, user_input: dict[str, Any] | None = None):
        room = self._preheat_room()
        if room is None:
            return await self.async_step_init()
        entries = room.get(CONF_ROOM_PREHEAT) or []
        if user_input is not None:
            drop = {int(i) for i in user_input.get(CONF_PICK_ENTRIES) or []}
            kept = [e for i, e in enumerate(entries) if i not in drop]
            if kept:
                room[CONF_ROOM_PREHEAT] = kept
            else:
                room.pop(CONF_ROOM_PREHEAT, None)
            return await self.async_step_preheat_menu()
        return self.async_show_form(
            step_id="preheat_remove",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PICK_ENTRIES): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": str(i), "label": schedule_text(e, self._hu())}
                                for i, e in enumerate(entries)
                            ],
                            multiple=True,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            description_placeholders={"room": room[CONF_ROOM_NAME]},
        )

    # --- funkciók: események, ciklusok, védelem
    async def async_step_features(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        if user_input is not None:
            opts.update(user_input)
            return await self.async_step_init()
        return self.async_show_form(
            step_id="features",
            data_schema=_features_schema(opts),
        )

    # --- nyári mód
    async def async_step_summer(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate_summer(user_input)
            if not errors:
                opts.pop(CONF_OUTDOOR_SENSOR, None)  # ha kitörölte a szenzort
                opts.update(user_input)
                return await self.async_step_init()
        return self.async_show_form(
            step_id="summer",
            data_schema=_summer_schema(user_input or opts),
            errors=errors,
        )

    # --- mentés
    async def async_step_done(self, user_input: dict[str, Any] | None = None):
        return self.async_create_entry(title="", data=self._load())
