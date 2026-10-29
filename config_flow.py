"""Konfigurációs folyamat: kazán kiválasztása, majd szobák és nyári mód az opciókban."""
from __future__ import annotations

import uuid
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
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
    DEFAULT_VALVE_RELEASE_MARGIN,
    DOMAIN,
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
        }
    )


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
                CONF_VALVE_DRY_RUN,
                default=bool(values.get(CONF_VALVE_DRY_RUN, DEFAULT_VALVE_DRY_RUN)),
            ): selector.BooleanSelector(),
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
                    CONF_VALVE_BOOST_THRESHOLD: DEFAULT_VALVE_BOOST_THRESHOLD,
                    CONF_VALVE_BOOST_DELAY: DEFAULT_VALVE_BOOST_DELAY,
                    CONF_VALVE_RELEASE_MARGIN: DEFAULT_VALVE_RELEASE_MARGIN,
                    CONF_SUMMER_TEMP: DEFAULT_SUMMER_TEMP,
                    CONF_SUMMER_START: DEFAULT_SUMMER_START,
                    CONF_SUMMER_END: DEFAULT_SUMMER_END,
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
        ):
            if user_input.get(key) is not None:  # a 0 is érvényes érték
                room[key] = float(user_input[key])
        room[CONF_ROOM_VALVE_LINK] = bool(user_input.get(CONF_ROOM_VALVE_LINK))
        room[CONF_ROOM_VALVE_CONTROL] = bool(
            user_input.get(CONF_ROOM_VALVE_CONTROL) and user_input.get(CONF_ROOM_TEMP)
        )
        return room

    # --- főmenü
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        opts = self._load()
        menu = ["add_room"]
        if opts[CONF_ROOMS]:
            menu += ["edit_room", "remove_room"]
        menu += ["settings", "summer", "done"]
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
                opts[CONF_ROOMS].append(
                    self._room_from_input(user_input, uuid.uuid4().hex[:8])
                )
                return await self.async_step_init()
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
                opts[CONF_ROOMS][index] = self._room_from_input(
                    user_input, self._edit_id
                )
                return await self.async_step_init()
        return self.async_show_form(
            step_id="edit_room_form",
            data_schema=_room_schema(user_input or room),
            errors=errors,
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
