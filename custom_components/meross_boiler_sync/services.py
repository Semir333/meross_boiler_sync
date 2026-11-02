"""Szolgáltatások: "Fűts most" és előfűtés (2.9)."""
from __future__ import annotations

from datetime import datetime, timedelta

import voluptuous as vol

from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    MANUAL_BOOST_MAX_MINUTES,
    MANUAL_BOOST_MAX_OFFSET,
    MANUAL_BOOST_MIN_MINUTES,
    MANUAL_BOOST_MIN_OFFSET,
    MAX_RAISED_TARGET,
)
from .controller import BoilerController, BoostError, RoomStatus

SERVICE_BOOST_NOW = "boost_now"
SERVICE_CANCEL_BOOST_NOW = "cancel_boost_now"
SERVICE_PREHEAT = "preheat"
SERVICE_CANCEL_PREHEAT = "cancel_preheat"

ATTR_MINUTES = "minutes"
ATTR_OFFSET = "offset"
ATTR_READY_BY = "ready_by"
ATTR_TARGET = "target_temperature"
ATTR_HOLD = "hold_minutes"

_ENTITIES = vol.Schema({vol.Required(ATTR_ENTITY_ID): cv.entity_ids}, extra=vol.ALLOW_EXTRA)

_BOOST_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(ATTR_MINUTES): vol.All(
            vol.Coerce(float), vol.Range(min=MANUAL_BOOST_MIN_MINUTES, max=MANUAL_BOOST_MAX_MINUTES)
        ),
        vol.Optional(ATTR_OFFSET): vol.All(
            vol.Coerce(float), vol.Range(min=MANUAL_BOOST_MIN_OFFSET, max=MANUAL_BOOST_MAX_OFFSET)
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

_PREHEAT_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_READY_BY): vol.Any(cv.datetime, cv.time),
        vol.Required(ATTR_TARGET): vol.All(vol.Coerce(float), vol.Range(min=5, max=MAX_RAISED_TARGET)),
        vol.Optional(ATTR_HOLD): vol.All(vol.Coerce(float), vol.Range(min=0, max=480)),
    },
    extra=vol.ALLOW_EXTRA,
)


def _error(err: BoostError) -> ServiceValidationError:
    return ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key=err.code,
        translation_placeholders={k: str(v) for k, v in err.placeholders.items()},
    )


def _rooms(hass: HomeAssistant, entity_ids: list[str]) -> list[tuple[BoilerController, RoomStatus]]:
    controllers = [c for c in hass.data.get(DOMAIN, {}).values() if isinstance(c, BoilerController)]
    found: list[tuple[BoilerController, RoomStatus]] = []
    for entity_id in entity_ids:
        match = next(
            ((c, st) for c in controllers if (st := c.room_by_entity(entity_id)) is not None),
            None,
        )
        if match is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="not_a_room",
                translation_placeholders={"entity_id": entity_id},
            )
        found.append(match)
    return found


def _ready_ts(value: datetime | object) -> float:
    """A "kész" időpont epoch-ban: dátum+idő, vagy csak idő (a következő ilyen időpont)."""
    now = dt_util.now()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=now.tzinfo)
        return value.timestamp()
    ready = datetime(now.year, now.month, now.day, value.hour, value.minute, tzinfo=now.tzinfo)  # type: ignore[attr-defined]
    if ready <= now:
        ready += timedelta(days=1)
    return ready.timestamp()


async def async_setup_services(hass: HomeAssistant) -> None:
    """A szolgáltatások regisztrálása (az első bejegyzésnél; többszöri hívás ártalmatlan)."""
    if hass.services.has_service(DOMAIN, SERVICE_BOOST_NOW):
        return

    async def boost_now(call: ServiceCall) -> None:
        targets = _rooms(hass, call.data[ATTR_ENTITY_ID])
        try:
            for ctrl, st in targets:  # előbb mindent ellenőriz, hogy ne maradjon félig végrehajtva
                ctrl.check_boost_allowed(st)
            for ctrl, st in targets:
                await ctrl.async_boost_now(st.room_id, call.data.get(ATTR_MINUTES), call.data.get(ATTR_OFFSET))
        except BoostError as err:
            raise _error(err) from err

    async def cancel_boost_now(call: ServiceCall) -> None:
        for ctrl, st in _rooms(hass, call.data[ATTR_ENTITY_ID]):
            await ctrl.async_cancel_boost_now(st.room_id)

    async def preheat(call: ServiceCall) -> None:
        targets = _rooms(hass, call.data[ATTR_ENTITY_ID])
        ready = _ready_ts(call.data[ATTR_READY_BY])
        try:
            for ctrl, st in targets:
                ctrl.check_preheat_allowed(st)
            for ctrl, st in targets:
                await ctrl.async_preheat(st.room_id, ready, call.data[ATTR_TARGET], call.data.get(ATTR_HOLD))
        except BoostError as err:
            raise _error(err) from err

    async def cancel_preheat(call: ServiceCall) -> None:
        for ctrl, st in _rooms(hass, call.data[ATTR_ENTITY_ID]):
            await ctrl.async_cancel_preheat(st.room_id)

    hass.services.async_register(DOMAIN, SERVICE_BOOST_NOW, boost_now, schema=_BOOST_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CANCEL_BOOST_NOW, cancel_boost_now, schema=_ENTITIES)
    hass.services.async_register(DOMAIN, SERVICE_PREHEAT, preheat, schema=_PREHEAT_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_CANCEL_PREHEAT, cancel_preheat, schema=_ENTITIES)


def async_unload_services(hass: HomeAssistant) -> None:
    for name in (SERVICE_BOOST_NOW, SERVICE_CANCEL_BOOST_NOW, SERVICE_PREHEAT, SERVICE_CANCEL_PREHEAT):
        hass.services.async_remove(DOMAIN, name)
