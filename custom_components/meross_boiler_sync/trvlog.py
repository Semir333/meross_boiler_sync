"""2.14: TRV-napló – az automatika szelep- és kalibráció-döntéseinek külön naplócsatornája.

A Beállítások › Rendszer › Naplók oldal szolgáltató-listája (Home Assistant Core, Supervisor, Host, ...)
rögzített, egyedi integráció nem tud új elemet hozzáadni. Ezért a napló a "Home Assistant Core" naplójában
jelenik meg, külön logger néven (`custom_components.meross_boiler_sync.trv_log`) és "TRV-napló ▸" előtaggal:
az oldal "Integrációk" szűrőjével vagy a keresővel külön is nézhető.

A HA naplószintje alapból figyelmeztetés, ezért a sima INFO sor nem látszana. A napló logger szintjét az
integráció INFO-ra állítja, amíg legalább egy bejegyzésnél be van kapcsolva (a szülő logger szintjétől
függetlenül), kikapcsoláskor visszaállítja. Kikapcsolva a döntés-sorok csak hibakereső (DEBUG) szinten
kerülnek a naplóba. A figyelmeztetések és hibák ettől függetlenül mindig a szokásos módon naplózódnak.

2.15: A Naplók oldal alapnézete csak a figyelmeztetéseket és hibákat mutatja ("Nem található hiba"); az INFO sorok
a "Teljes naplók" nézetben vannak. Ezért minden sor a Home Assistant Naplókönyvébe (Logbook) is bekerül
(`logbook_entry` esemény), ami külön beállítás nélkül, időrendben, az újraindítás után is látszik.
"""
from __future__ import annotations

import logging
from typing import Any

from .const import (
    CAL_GLOBAL_SPACING,
    CAL_MAX_PER_DAY,
    CAL_MIN_INTERVAL,
    CAL_QUIET_SECONDS,
    CAL_SETTLE_SECONDS,
    CAL_THRESHOLD,
    DOMAIN,
)

PREFIX = "TRV-napló ▸"
LOGBOOK_EVENT = "logbook_entry"  # a Naplókönyv eseménye (a HA magjában: homeassistant.const.EVENT_LOGBOOK_ENTRY)
LOGBOOK_NAME = "TRV-napló"
FEED_NAME = f"custom_components.{DOMAIN}.trv_log"

_FEED = logging.getLogger(FEED_NAME)
_LOGGER = logging.getLogger(__name__)

# azok a bejegyzések (config entry azonosítók), amelyeknél a napló be van kapcsolva
_ENABLED: set[str] = set()


def set_enabled(entry_id: str, enabled: bool) -> None:
    """Egy bejegyzés naplója be- / kikapcsolva. A csatorna szintje INFO, amíg bármelyik be van kapcsolva.

    Több bejegyzés (több kazán) is lehet: a szint csak akkor áll vissza, ha az utolsó is kikapcsolt.
    A HA `logger` integrációja csak azt a loggert védi, amelynek pontos neve a felhasználó
    `logs:` beállításában szerepel; ilyenkor a szintállítás hatástalan, és az a beállítás érvényes.
    """
    if enabled:
        _ENABLED.add(entry_id)
    else:
        _ENABLED.discard(entry_id)
    _FEED.setLevel(logging.INFO if _ENABLED else logging.NOTSET)


def info(enabled: bool, msg: str, *args: Any) -> None:
    """Egy döntés-sor. Bekapcsolt naplónál a csatornára kerül (INFO), kikapcsoltnál csak DEBUG szintre.

    A sor sosem ismétlődik: vagy az egyik, vagy a másik helyre megy. A naplózás hibája (rossz argumentum)
    a logging modulban marad, a vezérlést nem érinti.
    """
    if enabled:
        _FEED.info(PREFIX + " " + msg, *args)
    else:
        _LOGGER.debug(msg, *args)


def render(msg: str, args: tuple[Any, ...]) -> str:
    """A naplósor kész szövege (a Naplókönyvhöz); hibás formátum esetén maga az üzenet, kivétel nélkül."""
    try:
        return msg % args if args else msg
    except Exception:  # noqa: BLE001 - a napló hibája nem állíthatja le a vezérlést
        return msg


def num(value: Any) -> str:
    """Szám a naplóba (rövid alak, legfeljebb két tizedes), hibatűrően: hiányzó vagy értelmetlen érték helyett "?"."""
    try:
        return f"{round(float(value), 2):g}"
    except (TypeError, ValueError, OverflowError):
        return "?"


# a szelep-emelés végének oka (a `_boost_end_reason` kódjai)
BOOST_END_TEXT = {
    "max_time": "elérte a maximális emelési időt",
    "window": "nyitott ablak",
    "summer": "nyári mód",
    "target_reached": "a szoba elérte a célt",
    "sensor": "nincs használható szoba hőmérő",
    "other": "egyéb ok",
}


# ------------------------------------------------------------------ a kalibráció állapotának szövege
def _minutes(seconds: float) -> str:
    return f"{seconds / 60:g} perc"


_STATE_TEXT: dict[tuple[str, str | None], str] = {
    ("off", None): "ebben a szobában ki van kapcsolva",
    ("error", None): "váratlan hiba (a részletek a naplóban)",
    ("unavailable", None): "a szelep nem elérhető",
    ("unavailable", "number"): "a kalibráció szám-entitása nem elérhető",
    ("no_entity", None): "a szelephez nincs használható kalibráció szám-entitás",
    ("no_entity", "not_found"): "a szelephez nem található kalibráció szám-entitás",
    ("no_entity", "no_device"): "a szelep nem tartozik eszközhöz, ezért nincs kalibráció szám-entitása",
    ("no_entity", "disabled"): "a kalibráció szám-entitása le van tiltva a Home Assistantban",
    ("no_entity", "error"): "az entitások keresése nem sikerült",
    ("no_entity", "range"): "a kalibráció szám-entitásának tartománya értelmetlen",
    ("tracker", None): "a Meross LAN külső hőmérőt követ (maga állítja a kalibrációt), nem nyúlok hozzá",
    ("waiting", "hold"): "a Home Assistant éppen indul vagy leáll, még nem módosítok",
    ("waiting", "dry_run"): "próbaüzem: egy korábbi módosítás ellenőrzése még függőben van, ezt próbaüzemben nem folytatom",
    ("waiting", "unsent"): "az előző módosítás parancsa nem ment el (leállás közben), új mérés indul",
    ("waiting", "external"): "közben kézzel átállították a kalibrációt, új mérés indul",
    ("waiting", "interval"): f"két módosítás között legalább {CAL_MIN_INTERVAL // 3600} óra telik el",
    ("waiting", "daily_limit"): f"elérte a napi {CAL_MAX_PER_DAY} módosítást, holnapig vár",
    ("waiting", "spacing"): f"a másik szelep módosítása után {_minutes(CAL_GLOBAL_SPACING)} szünetet tart",
    ("waiting", "backoff"): "az előző parancs sikertelen volt, később próbálom újra",
    ("waiting", "reverted"): "a hatástalan módosítást visszaállítottam",
    ("waiting", "reverting"): "visszaállítás folyamatban",
    ("waiting", "no_reference"): "nincs használható szoba hőmérő",
    ("waiting", "stale"): "a szoba hőmérő adata elavult",
    ("waiting", "unreliable"): "a szoba hőmérő nem megbízható (képtelen vagy ugráló érték)",
    ("waiting", "window"): "nyitott ablak",
    ("waiting", "no_reading"): "a szelep nem ad használható hőmérséklet-értéket",
    ("waiting", "boost"): "a szelep éppen emelt célhőmérsékleten fűt",
    ("waiting", "trend"): "a szoba hőmérséklete gyorsan változik",
    ("waiting", "not_quiet"): f"a radiátor még nem hűlt ki (a kazán vagy a szelep legalább {_minutes(CAL_QUIET_SECONDS)}e nem fűt)",
    ("waiting", "settling"): f"a módosítás után {_minutes(CAL_SETTLE_SECONDS)} türelmi idő, hogy a szelep mérése beálljon",
    ("sampling", "samples"): "mintavétel folyamatban",
    ("sampling", "unstable"): "a minták szórnak, még nem döntök",
    ("verifying", "confirm"): "a módosítás megerősítésére vár",
    ("verifying", "settling"): f"a módosítás hatását ellenőrzi ({_minutes(CAL_SETTLE_SECONDS)} türelmi idő)",
    ("verifying", "samples"): "a módosítás hatását ellenőrzi (mintavétel)",
    ("verifying", "unstable"): "a módosítás hatását ellenőrzi (a minták szórnak)",
    ("waiting", None): "vár",
    ("sampling", None): "mintavétel",
    ("verifying", None): "a módosítás hatását ellenőrzi",
    ("failed", None): "a módosítás nem sikerült",
    ("suspended", None): "felfüggesztve (hatástalan módosítások miatt)",
    ("failed", "rejected"): "a szelep nem fogadta el a módosítást",
    ("failed", "command"): "a módosítás parancsa nem sikerült",
    ("ok", None): f"rendben (±{num(CAL_THRESHOLD)} °C tűrésen belül)",
    ("ok", "recheck"): "rendben, a következő mérés később",
    ("implausible", None): "a szelep mérése képtelenül távol van a céltól, nem módosítok",
    ("limit", None): "a kalibráció a határán áll, nincs mit módosítani",
    ("proposed", None): "próbaüzem: módosítást javasol",
}


def state_text(status: str | None, reason: str | None) -> str:
    """A kalibráció állapotának magyar szövege; ismeretlen kód esetén maga a kód."""
    text = _STATE_TEXT.get((status or "", reason)) or _STATE_TEXT.get((status or "", None))
    if text is not None:
        return text
    return f"{status}" + (f" ({reason})" if reason else "")
