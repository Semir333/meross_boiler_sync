"""Meross Boiler Sync: szobánkénti hőigény alapján vezérli a kazán termosztátot."""
from __future__ import annotations

import logging
import uuid
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.loader import async_get_integration

from .const import (
    CONF_BOILER,
    CONF_REGISTER_CARD,
    CONF_ROOM_ID,
    CONF_ROOM_NAME,
    CONF_ROOM_VALVES,
    CONF_ROOMS,
    CONF_VALVES,
    DEFAULT_REGISTER_CARD,
    DOMAIN,
    STORAGE_VERSION,
)
from .controller import BoilerController, async_restore_on_remove

PLATFORMS = [Platform.BINARY_SENSOR]

_LOGGER = logging.getLogger(__name__)

CARD_FILE = "meross-boiler-sync-card.js"
CARD_URL = f"/{DOMAIN}_static/{CARD_FILE}"


async def _async_register_card(hass: HomeAssistant, load_in_frontend: bool = True) -> None:
    """A Lovelace kártya JS-ének kiszolgálása és (opcionálisan) betöltése.

    - A fájl elérési útja mindig regisztrálódik, így kézzel is felvehető erőforrásként.
    - Betöltve a kártya megjelenik a "Kártya hozzáadása" listában.
    Dashboardra SEMMILYEN kártyát nem tesz fel.
    """
    try:
        if not hass.data.get(f"{DOMAIN}_card_path"):
            hass.data[f"{DOMAIN}_card_path"] = True
            path = Path(__file__).parent / "frontend" / CARD_FILE
            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_URL, str(path), False)]
            )
        if load_in_frontend and not hass.data.get(f"{DOMAIN}_card_js"):
            hass.data[f"{DOMAIN}_card_js"] = True
            integration = await async_get_integration(hass, DOMAIN)
            add_extra_js_url(hass, f"{CARD_URL}?v={integration.version}")
    except Exception as err:  # noqa: BLE001 - a kártya hiánya nem akaszthatja meg az integrációt
        _LOGGER.warning("A Lovelace kártya betöltése nem sikerült: %s", err)


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
    await _async_register_card(
        hass, bool({**entry.data, **entry.options}.get(CONF_REGISTER_CARD, DEFAULT_REGISTER_CARD))
    )
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
    await async_restore_on_remove(hass, entry.entry_id)
    await Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}").async_remove()


async def _async_reload(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
