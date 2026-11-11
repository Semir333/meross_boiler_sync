"""A szoba TRV eltolásának (előjeles) beolvasása a mentett beállításból.

2.17: az eltolás előjeles, a Meross LAN kalibráció számával azonos előjellel. A szelep mérése a szoba hőmérőjéhez képest: a plusz
érték azt jelenti, hogy a szelep melegebbet mutat a szoba hőmérőjénél, a mínusz azt, hogy hidegebbet (az alapérték: -1 °C). A 2.12-2.16
verziók a `trv_offset` kulcsban az ellentettjét, a "ennyivel mutasson hidegebbet" értéket (0..3) tárolták; az 2.17 űrlapja az új
`trv_offset_signed` kulcsba ment. A régi értéket olvasáskor átszámoljuk, ezért a mentett szobák ugyanúgy működnek tovább, és nincs
szükség a beállítások átírására (az átírás kétszer lefuthatna, az olvasáskori átszámolás nem).

2.18: a több szelepes szobában az egyes szelepek eltolása külön is megadható (`valve_trv_offsets`, szelep → előjeles eltolás);
amelyik szelepnek nincs egyedi értéke, az a szoba eltolását használja (`room_valve_offsets`).

Ez a modul a vezérlőtől és az űrlaptól függetlenül, csak az állandókra épül, hogy mindkettő ugyanazt az értelmezést használja.
"""
from __future__ import annotations

import math
from typing import Any

from .const import (
    CONF_ROOM_TRV_OFFSET,
    CONF_ROOM_TRV_OFFSET_SIGNED,
    CONF_ROOM_VALVE_OFFSETS,
    CONF_ROOM_VALVES,
    DEFAULT_TRV_OFFSET,
    TRV_OFFSET_MAX,
)


def _finite(value: Any) -> float | None:
    """Szám (véges) vagy None."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def trv_offset_from(value: Any) -> float:
    """A szoba TRV eltolása (°C), előjelesen: a szelep mérése mínusz a szoba hőmérője (a plusz melegebbet, a mínusz
    hidegebbet mutat a szelep, mint a Meross LAN kalibráció száma). Hiányzó vagy hibás érték esetén az alapérték,
    különben -`TRV_OFFSET_MAX` és +`TRV_OFFSET_MAX` közé szorítva."""
    number = _finite(value)
    if number is None:
        return DEFAULT_TRV_OFFSET
    return round(min(max(number, -TRV_OFFSET_MAX), TRV_OFFSET_MAX), 2) + 0.0  # a "+ 0.0" a -0.0-t 0.0-ra cseréli


def room_trv_offset(room: dict[str, Any]) -> float:
    """A szoba mentett beállításából az előjeles TRV eltolás (°C).

    2.17-től a `trv_offset_signed` kulcs érvényes. A 2.12-2.16 verziók `trv_offset` kulcsa a szelep HIDEGEBBET mutatásának
    mértékét tárolta (0..3, nem negatív szám): az előjelet vált (a régi 1,0 az új -1,0), így a mentett szoba ugyanúgy működik
    tovább. Mindkét kulcs hiányában (vagy hibás értéknél) az alapérték érvényes. Ha mindkettő megvan, az új dönt."""
    if CONF_ROOM_TRV_OFFSET_SIGNED in room:
        return trv_offset_from(room[CONF_ROOM_TRV_OFFSET_SIGNED])
    number = _finite(room.get(CONF_ROOM_TRV_OFFSET))
    if number is None:
        return DEFAULT_TRV_OFFSET
    return 0.0 - round(min(max(number, 0.0), TRV_OFFSET_MAX), 2)  # a régi beállítás nem lehetett negatív


def room_valve_offsets(room: dict[str, Any]) -> dict[str, float]:
    """2.18: a szoba szelepeinek egyedi TRV eltolása (°C, előjelesen): {szelep: eltolás}.

    Több szelepes szobában az egyes szelepek eltolása külön is megadható (az űrlap második lépése). Csak a megadott szelepek
    szerepelnek az eredményben; amelyik nincs benne, az a szoba eltolását (`room_trv_offset`) használja. A mentett beállításból
    csak a hihető elemek számítanak: a szobában már nem szereplő szelep bejegyzése (a szelepet kivették) és a hibás vagy nem
    szám érték kimarad, és ilyenkor a szoba eltolása érvényes (nem az alapérték: egy elírás ne írja át a szoba beállítását).
    Az érték ±`TRV_OFFSET_MAX` közé szorított, a 0 érvényes (az a szelep a szoba hőmérőjét követi)."""
    raw = room.get(CONF_ROOM_VALVE_OFFSETS)
    if not isinstance(raw, dict):
        return {}
    result: dict[str, float] = {}
    for valve_id in room.get(CONF_ROOM_VALVES) or []:
        number = _finite(raw.get(valve_id))
        if number is not None:
            result[valve_id] = trv_offset_from(number)
    return result
