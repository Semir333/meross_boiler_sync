"""A Lovelace kártya kiszolgálása és felvétele az irányítópult erőforrásai közé.

Miért erőforrás és nem `add_extra_js_url`?
A Home Assistant újabb frontendjében az `extra_module_url`-lel betöltött kártya versenyhelyzetbe
kerül a felület saját indulásával: néha rossz egyéni-elem nyilvántartásba regisztrálódik, és a
Lovelace "Konfigurációs hiba / Custom element doesn't exist" üzenetet mutatja. A Lovelace
erőforrásként felvett kártya a felület elindulása UTÁN fut le, ezért megbízható (a kézzel felvett
erőforrás is ezért működik).

Dashboardra SEMMILYEN kártyát nem tesz fel, csak a kártya fájlját veszi fel erőforrásként,
hogy megjelenjen a "Kártya hozzáadása" listában.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from homeassistant.loader import async_get_integration

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_FILE = "meross-boiler-sync-card.js"
CARD_URL = f"/{DOMAIN}_static/{CARD_FILE}"

RETRY_SECONDS = 15  # a Lovelace még nem állt fel: ennyi időnként próbáljuk újra
MAX_ATTEMPTS = 40  # kb. 10 perc

_KEY_PATH = f"{DOMAIN}_card_path"
_KEY_RETRY = f"{DOMAIN}_card_retry"


def _resources(hass: HomeAssistant) -> Any | None:
    """A Lovelace erőforrás-gyűjtemény (a HA verziójától függően objektum vagy szótár)."""
    data = hass.data.get("lovelace")
    if data is None:
        return None
    if isinstance(data, dict):
        return data.get("resources")
    return getattr(data, "resources", None)


def _path_of(url: Any) -> str:
    return str(url or "").split("?", 1)[0]


def _can_edit(resources: Any) -> bool:
    """Csak a tárolt (UI-ból kezelt) erőforrások módosíthatók; YAML módban nem."""
    return all(
        hasattr(resources, name)
        for name in ("async_create_item", "async_update_item", "async_delete_item")
    )


async def _async_ensure_loaded(resources: Any) -> None:
    if not getattr(resources, "loaded", True):
        await resources.async_load()
        resources.loaded = True


async def async_sync_resource(hass: HomeAssistant, version: str) -> bool:
    """Felveszi / frissíti a kártya erőforrást.

    True: kész (létrehozva, frissítve, már rendben volt, vagy YAML mód).
    False: a Lovelace még nem áll készen, később újra kell próbálni.
    """
    resources = _resources(hass)
    if resources is None:
        return False
    if not _can_edit(resources):
        _LOGGER.info(
            "A Lovelace erőforrások YAML módban vannak, ezért a kártyát kézzel kell felvenni: "
            "url: %s, type: module (lásd README)",
            CARD_URL,
        )
        return True

    await _async_ensure_loaded(resources)
    wanted = f"{CARD_URL}?v={version}"
    same = [r for r in resources.async_items() if _path_of(r.get("url")) == CARD_URL]

    if not same:
        await resources.async_create_item({"res_type": "module", "url": wanted})
        _LOGGER.info("Lovelace erőforrás felvéve: %s", wanted)
        return True

    first = same[0]
    if first.get("url") != wanted or first.get("type", first.get("res_type")) != "module":
        await resources.async_update_item(first["id"], {"res_type": "module", "url": wanted})
        _LOGGER.info("Lovelace erőforrás frissítve: %s", wanted)
    for duplicate in same[1:]:  # ugyanaz a fájl kétszer: a kártya így kétszer próbálna betöltődni
        await resources.async_delete_item(duplicate["id"])
        _LOGGER.info("Felesleges ismétlődő Lovelace erőforrás törölve: %s", duplicate.get("url"))
    return True


async def async_remove_resource(hass: HomeAssistant) -> None:
    """Az integráció végleges törlésekor eltávolítja a kártya erőforrást."""
    try:
        resources = _resources(hass)
        if resources is None or not _can_edit(resources):
            return
        await _async_ensure_loaded(resources)
        for item in [r for r in resources.async_items() if _path_of(r.get("url")) == CARD_URL]:
            await resources.async_delete_item(item["id"])
            _LOGGER.info("Lovelace erőforrás törölve: %s", item.get("url"))
    except Exception as err:  # noqa: BLE001 - a takarítás hibája nem akaszthat meg semmit
        _LOGGER.debug("A Lovelace erőforrás törlése nem sikerült: %s", err)


def async_cancel_retry(hass: HomeAssistant) -> None:
    unsub = hass.data.pop(_KEY_RETRY, None)
    if unsub:
        unsub()


async def async_register_card(hass: HomeAssistant, register_resource: bool = True) -> None:
    """A kártya fájljának kiszolgálása és (opcionálisan) felvétele erőforrásként.

    - A fájl elérési útja mindig regisztrálódik, így kézzel is felvehető erőforrásként.
    - register_resource=True: a plugin maga veszi fel / tartja frissen a Lovelace erőforrást.
    """
    try:
        if not hass.data.get(_KEY_PATH):
            path = Path(__file__).parent / "frontend" / CARD_FILE
            await hass.http.async_register_static_paths(
                [StaticPathConfig(CARD_URL, str(path), False)]
            )
            hass.data[_KEY_PATH] = True
    except Exception as err:  # noqa: BLE001 - a kártya hiánya nem akaszthatja meg az integrációt
        _LOGGER.warning("A Lovelace kártya fájljának kiszolgálása nem sikerült: %s", err)
        return

    if not register_resource:
        return

    try:
        version = str((await async_get_integration(hass, DOMAIN)).version)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Az integráció verziója nem olvasható, a kártya erőforrás nem frissül: %s", err)
        return

    async_cancel_retry(hass)
    attempts = 0

    async def _attempt(_now: Any = None) -> None:
        nonlocal attempts
        hass.data.pop(_KEY_RETRY, None)
        attempts += 1
        try:
            done = await async_sync_resource(hass, version)
        except Exception as err:  # noqa: BLE001
            _LOGGER.warning("A Lovelace kártya erőforrás felvétele nem sikerült: %s", err)
            return
        if done:
            return
        if attempts >= MAX_ATTEMPTS:
            _LOGGER.warning(
                "A Lovelace nem állt fel időben, a kártya erőforrás nem lett felvéve. "
                "Vedd fel kézzel: %s (típus: JavaScript modul)",
                CARD_URL,
            )
            return
        hass.data[_KEY_RETRY] = async_call_later(hass, RETRY_SECONDS, _attempt)

    await _attempt()
