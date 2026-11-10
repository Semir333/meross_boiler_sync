"""A kazán be/ki váltásainak naplója: indítások száma, átlagos be- és kikapcsolt idő.

Csak a kazán megfigyelt állapotából dolgozik (nem függ a Home Assistant-tól),
ezért önállóan tesztelhető. A napló újraindítás után is megmarad (a vezérlő menti).

Újraindításkor a napló nem látja, mi történt a kazánnal a leállás alatt. Ezt két jelzés
mutatja: a ciklus kezdete nem ismert (`known` = 0), illetve a vége nem ismert
(`end_known` = 0, ha a kazán a plugin leállása alatt kapcsolt ki). Az ilyen ciklus nem
számít bele az átlagokba, így egy újraindítás nem torzítja a statisztikát.
"""
from __future__ import annotations

import math
from typing import Any

from .const import (
    CYCLE_AVG_WINDOW_SECONDS,
    CYCLE_HISTORY_SECONDS,
    CYCLE_LIST_SECONDS,
    CYCLE_MIN_SAMPLES,
)

# egy elem: [bekapcsolás ideje, kikapcsolás ideje vagy None,
#            a kezdet pontosan ismert-e (1/0), a vége pontosan ismert-e (1/0)]
_ON, _OFF, _KNOWN, _END_KNOWN = 0, 1, 2, 3


class CycleLog:
    """Kazán ciklusok: megfigyelés (observe) és statisztika (stats)."""

    def __init__(self) -> None:
        self._items: list[list[Any]] = []
        self._prev_on: bool | None = None

    # ------------------------------------------------------------------ mentés / betöltés
    def to_list(self) -> list[list[Any]]:
        # a negyedik elem csak akkor kerül a fájlba, ha a vég nem ismert (régebbi verzióval kompatibilis)
        return [list(item) if not item[_END_KNOWN] else list(item[:3]) for item in self._items]

    def load(self, raw: Any) -> None:
        self._items = []
        self._prev_on = None
        if not isinstance(raw, list):
            return
        for item in raw:
            try:
                on = float(item[_ON])
                off = None if item[_OFF] is None else float(item[_OFF])
                known = 1 if len(item) <= 2 else (1 if int(item[_KNOWN]) else 0)
                end_known = 1 if len(item) <= 3 else (1 if int(item[_END_KNOWN]) else 0)
            except (TypeError, ValueError, IndexError):
                continue
            if not math.isfinite(on) or (off is not None and not math.isfinite(off)):
                continue  # hibás (nem szám) idő
            if off is not None and off < on:
                continue  # értelmetlen ciklus: a vége a kezdete előtt van
            self._items.append([on, off, known, end_known])
        self._items.sort(key=lambda it: it[_ON])
        # csak az utolsó elem lehet még nyitott; a többi nyitott elem hibás, az adatot nem torzítjuk
        for item in self._items[:-1]:
            if item[_OFF] is None:
                item[_OFF] = item[_ON]
                item[_END_KNOWN] = 0

    # ------------------------------------------------------------------ megfigyelés
    def observe(self, is_on: bool, now: float) -> str | None:
        """A kazán mostani állapota. "started" / "stopped" ha váltás történt, különben None."""
        change: str | None = None
        open_item = self._items[-1] if self._items and self._items[-1][_OFF] is None else None
        if is_on and open_item is None:
            # ha ez az első megfigyelés (újraindítás után), a pontos kezdet nem ismert,
            # ezért nem számít indításnak
            known = 0 if self._prev_on is None else 1
            self._items.append([now, None, known, 1])
            change = "started" if known else None
        elif not is_on and open_item is not None:
            open_item[_OFF] = max(now, open_item[_ON])
            if self._prev_on is None:
                # a kazán a plugin leállása alatt kapcsolt ki: a kikapcsolás ideje nem ismert,
                # a mostani megfigyelés csak a legkésőbbi lehetséges időpont
                open_item[_END_KNOWN] = 0
            change = "stopped"
        self._prev_on = is_on
        self._prune(now)
        return change

    def _prune(self, now: float) -> None:
        cutoff = now - CYCLE_HISTORY_SECONDS
        self._items = [
            it for it in self._items if (it[_OFF] if it[_OFF] is not None else now) >= cutoff
        ]

    # ------------------------------------------------------------------ lekérdezések
    def last_change(self) -> float | None:
        """A legutolsó be- vagy kikapcsolás ideje (a védelemhez)."""
        if not self._items:
            return None
        item = self._items[-1]
        return item[_OFF] if item[_OFF] is not None else item[_ON]

    def last_known_change(self) -> float | None:
        """A legutolsó biztosan megfigyelt váltás ideje (újraindítás utáni első látás nem számít)."""
        if not self._items:
            return None
        item = self._items[-1]
        if item[_OFF] is not None:
            return item[_OFF] if item[_END_KNOWN] else None
        return item[_ON] if item[_KNOWN] else None

    def stats(self, now: float) -> dict[str, Any]:
        known = [it for it in self._items if it[_KNOWN]]
        starts_24h = sum(1 for it in known if it[_ON] >= now - CYCLE_HISTORY_SECONDS)
        starts_hour = sum(1 for it in known if it[_ON] >= now - 3600)
        window = now - CYCLE_AVG_WINDOW_SECONDS
        # átlagos bekapcsolt idő: csak olyan ciklusból, aminek a kezdete és a vége is ismert
        done = [
            it
            for it in known
            if it[_OFF] is not None and it[_END_KNOWN] and it[_ON] >= window
        ]
        on_minutes = [(it[_OFF] - it[_ON]) / 60 for it in done]
        # átlagos kikapcsolt idő: két egymás utáni ciklus között, ha mindkét határ ismert
        recent = [it for it in self._items if it[_ON] >= window]
        gaps = [
            (b[_ON] - a[_OFF]) / 60
            for a, b in zip(recent, recent[1:])
            if a[_OFF] is not None and a[_END_KNOWN] and b[_KNOWN]
        ]
        last_start = next((it[_ON] for it in reversed(known)), None)
        last_stop = next(
            (it[_OFF] for it in reversed(self._items) if it[_OFF] is not None and it[_END_KNOWN]),
            None,
        )
        return {
            "starts_24h": starts_24h,
            "starts_last_hour": starts_hour,
            "samples": len(on_minutes),
            "avg_on_minutes": round(sum(on_minutes) / len(on_minutes), 1) if on_minutes else None,
            "avg_off_minutes": round(sum(gaps) / len(gaps), 1) if gaps else None,
            "last_start": last_start,
            "last_stop": last_stop,
        }

    def is_short_cycling(self, stats: dict[str, Any], max_starts: float, min_avg_on: float) -> bool:
        if max_starts > 0 and stats["starts_last_hour"] >= max_starts:
            return True
        avg_on = stats["avg_on_minutes"]
        return bool(
            min_avg_on > 0
            and avg_on is not None
            and stats["samples"] >= CYCLE_MIN_SAMPLES
            and avg_on < min_avg_on
        )

    def recent_list(self, now: float) -> list[list[int | None]]:
        """A szenzor attribútumához: az utolsó órák ciklusai [be, ki|None] egész másodpercekben.

        A nem ismert végű ciklus kimarad: a kikapcsolás ideje nem ismert, ezért nem rajzolunk neki sávot.
        """
        cutoff = now - CYCLE_LIST_SECONDS
        out: list[list[int | None]] = []
        for it in self._items:
            if (it[_OFF] if it[_OFF] is not None else now) < cutoff:
                continue
            if it[_OFF] is not None and not it[_END_KNOWN]:
                continue
            out.append([int(it[_ON]), None if it[_OFF] is None else int(it[_OFF])])
        return out
