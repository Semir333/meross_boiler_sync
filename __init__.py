"""Meross Boiler Sync: szobánkénti hőigény alapján vezérli a kazán termosztátot."""
from __future__ import annotations

import uuid

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import (
    CONF_BOILER,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_VALVES,
    CONF_ROOMS,
    CONF_VALVES,
    DOMAIN,
    STORAGE_VERSION,
)
from .controller import BoilerController

PLATFORMS = [Platform.BINARY_SENSOR]


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """1.x -> 2.x: minden korábbi szelepből egy-egy (hőmérő nélküli) szoba lesz."""
    if entry.version < 2:
        merged = {**entry.data, **entry.options}
        boiler = merged.pop(CONF_BOILER, None)
        valves = merged.pop(CONF_VALVES, [])
        rooms = []
        for valve in valves:
            state = hass.states.get(valve)
            name = state.attributes.get("friendly_name", valve) if state else valve
            rooms.append(
                {
                    CONF_ROOM_ID: uuid.uuid4().hex[:8],
                    CONF_ROOM_NAME: name,
                    CONF_ROOM_VALVES: [valve],
                }
            )
        merged[CONF_ROOMS] = rooms
        hass.config_entries.async_update_entry(
            entry, data={CONF_BOILER: boiler}, options=merged, version=2
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = BoilerController(hass, entry)
    await controller.async_load()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await controller.async_start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        controller: BoilerController = hass.data[DOMAIN].pop(entry.entry_id)
        controller.async_stop()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
