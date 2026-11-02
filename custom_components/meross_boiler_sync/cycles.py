"""A kazán be/ki váltásainak naplója: indítások száma, átlagos be- és kikapcsolt idő.

Csak a kazán megfigyelt állapotából dolgozik (nem függ a Home Assistant-tól),
ezért önállóan tesztelhető. A napló újraindítás után is megmarad (a vezérlő menti).
"""
from __future__ import annotations

from typing import Any

from .const import (
    CYCLE_AVG_WINDOW_SECONDS,
    CYCLE_HISTORY_SECONDS,
    CYCLE_LIST_SECONDS,
    CYCLE_MIN_SAMPLES,
)

# egy elem: [bekapcsolás ideje, kikapcsolás ideje vagy None, a kezdet pontosan ismert-e (1/0)]
_ON, _OFF, _KNOWN = 0, 1, 2


class CycleLog:
    """Kazán ciklusok: megfigyelés (observe) és statisztika (stats)."""

    def __init__(self) -> None:
        self._items: list[list[Any]] = []
        self._prev_on: bool | None = None

    # ------------------------------------------------------------------ mentés / betöltés
    def to_list(self) -> list[list[Any]]:
        return [list(item) for item in self._items]

    def load(self, raw: Any) -> None:
        self._items = []
        if not isinstance(raw, list):
            return
        for item in raw:
            try:
                on = float(item[_ON])
                off = None if item[_OFF] is None else float(item[_OFF])
                known = int(item[_KNOWN]) if len(item) > 2 else 1
            except (TypeError, ValueError, IndexError):
                continue
            self._items.append([on, off, known])
        self._items.sort(key=lambda it: it[_ON])

    # ------------------------------------------------------------------ megfigyelés
    def observe(self, is_on: bool, now: float) -> str | None:
        """A kazán mostani állapota. "started" / "stopped" ha váltás történt, különben None."""
        change: str | None = None
        open_item = self._items[-1] if self._items and self._items[-1][_OFF] is None else None
        if is_on and open_item is None:
            # ha az előző megfigyelés is "be" volt, akkor ez újraindítás utáni első látás:
            # a pontos kezdet nem ismert, ezért nem számít indításnak
            known = 0 if self._prev_on is None else 1
            self._items.append([now, None, known])
            change = "started" if known else None
        elif not is_on and open_item is not None:
            open_item[_OFF] = now
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

    def stats(self, now: float) -> dict[str, Any]:
        known = [it for it in self._items if it[_KNOWN]]
        starts_24h = sum(1 for it in known if it[_ON] >= now - CYCLE_HISTORY_SECONDS)
        starts_hour = sum(1 for it in known if it[_ON] >= now - 3600)
        window = now - CYCLE_AVG_WINDOW_SECONDS
        done = [it for it in known if it[_OFF] is not None and it[_ON] >= window]
        on_minutes = [(it[_OFF] - it[_ON]) / 60 for it in done]
        recent = [it for it in known if it[_ON] >= window]
        gaps = [
            (b[_ON] - a[_OFF]) / 60
            for a, b in zip(recent, recent[1:])
            if a[_OFF] is not None
        ]
        last_start = next((it[_ON] for it in reversed(known)), None)
        last_stop = next((it[_OFF] for it in reversed(self._items) if it[_OFF] is not None), None)
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
        """A szenzor attribútumához: az utolsó órák ciklusai [be, ki|None] egész másodpercekben."""
        cutoff = now - CYCLE_LIST_SECONDS
        out: list[list[int | None]] = []
        for it in self._items:
            if (it[_OFF] if it[_OFF] is not None else now) < cutoff:
                continue
            out.append([int(it[_ON]), None if it[_OFF] is None else int(it[_OFF])])
        return out
