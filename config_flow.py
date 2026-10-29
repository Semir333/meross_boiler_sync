"""Konfigurációs folyamat a Meross Boiler Sync integrációhoz."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

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


def _build_schema(values: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_BOILER, description={"suggested_value": values.get(CONF_BOILER)}
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate")
            ),
            vol.Required(
                CONF_VALVES, description={"suggested_value": values.get(CONF_VALVES)}
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="climate", multiple=True)
            ),
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
        }
    )


def _validate(user_input: dict[str, Any]) -> dict[str, str]:
    valves = user_input.get(CONF_VALVES) or []
    if not valves:
        return {"base": "no_valves"}
    if user_input.get(CONF_BOILER) in valves:
        return {"base": "boiler_in_valves"}
    return {}


class MerossBoilerSyncConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                await self.async_set_unique_id(user_input[CONF_BOILER])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Meross Boiler Sync", data=user_input
                )
        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input or {}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return MerossBoilerSyncOptionsFlow()


class MerossBoilerSyncOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}
        if user_input is not None:
            errors = _validate(user_input)
            if not errors:
                return self.async_create_entry(title="", data=user_input)
        values = user_input or {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init", data_schema=_build_schema(values), errors=errors
        )
