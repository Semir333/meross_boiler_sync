"""A radiátor szelepek hőmérőjének automata kalibrációja (2.11).

Miért kell: a szelep a radiátor mellett méri a hőmérsékletet, ezért a szoba valódi hőmérsékletétől
eltérhet. A szelep a saját mérése alapján nyit és zár, így téves méréssel a szoba túl hideg vagy túl
meleg marad. A plugin ismeri a szoba hőmérőjét: ezt veszi referenciának, és a szelep kalibrációs
értékét (a Meross LAN "Calibration" szám-entitása) úgy állítja, hogy a szelep mérése a szoba
hőmérőjét kövesse. A fő kazán termosztátot nem érinti.

Mikor mér: csak akkor, ha a radiátor már kihűlt. Fűtés közben a forró radiátor a szelepet melegebbnek
mutatja, és egy ilyenkor végzett "korrekció" a kihűlt radiátornál rossz irányba tolná a szelepet.
Csendes időnek az számít, ha a kazán (vagy a szelep) legalább `CAL_QUIET_SECONDS` ideje nem fűt.
Mérés közben a szoba hőmérőjének is stabilnak kell lennie, nem lehet nyitott ablak, szelepemelés vagy
külső követés (Meross LAN "Tracked sensor").

Hogyan dönt: több mérés mediánjából számolja az eltérést (szoba hőmérő - szelep). Csak stabil
mérésből, a küszöbnél nagyobb és a hihetőségi határon belüli eltérést korrigál, a szám-entitás
lépésközére kerekítve, az eredeti kalibrációtól legfeljebb `CAL_MAX_TOTAL` fokra.

Mi védi a beállítást:
- Minden módosítás előtt "előre írt" rekord kerül a lemezre; újraindítás után a plugin a szám-entitás
  állapotából tudja, megtörtént-e a módosítás, és a korlátozások (időköz, napi darabszám) tovább élnek.
- A módosítás után új, stabil mérést vár (a hub ritkán jelent), és csak akkor korrigál újra, ha az
  előző módosítás igazoltan közelebb vitte a szelepet a szoba hőmérőjéhez. Ha nem (a szelep nem veszi
  figyelembe, vagy éppen rossz irányba hat), visszaállítja az előző értéket; két egymás utáni
  hatástalan módosítás után a szelepet egy hétre felfüggeszti és Javítások (Repairs) üzenetet küld.
- Próbaüzem: csak naplóz és eseményt küld, a szelepet nem módosítja (függő visszaállítást sem hajt végre).

A szelep állapotkódjai (`status`): off (a szobában ki van kapcsolva), waiting, sampling, verifying,
ok, proposed (próbaüzem), suspended, failed, tracker, no_entity, unavailable, implausible, limit, error.
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers import entity_registry as er

from .const import (
    CAL_CONFIRM_SECONDS,
    CAL_DISCOVERY_RETRY,
    CAL_GLOBAL_SPACING,
    CAL_JUDGE_MIN,
    CAL_MAX_DIFF,
    CAL_MAX_PER_DAY,
    CAL_MAX_RANGE,
    CAL_MAX_ROOM_SPREAD,
    CAL_MAX_SAMPLES,
    CAL_MAX_SPREAD,
    CAL_MAX_STRIKES,
    CAL_MAX_TOTAL,
    CAL_MAX_TREND,
    CAL_MIN_INTERVAL,
    CAL_MIN_SAMPLES,
    CAL_QUIET_SECONDS,
    CAL_READING_MAX,
    CAL_READING_MIN,
    CAL_RECHECK_SECONDS,
    CAL_REVERT_TRIES,
    CAL_SAMPLE_MAX_AGE,
    CAL_SAMPLE_SECONDS,
    CAL_SETTLE_SECONDS,
    CAL_SUSPEND_SECONDS,
    CAL_THRESHOLD,
)

if TYPE_CHECKING:
    from .controller import BoilerController, RoomStatus

_LOGGER = logging.getLogger(__name__)

# a szám-entitás tartománya, ha az állapota nem adja meg (Meross MTS100 / MTS150)
DEFAULT_NUMBER_MIN = -5.0
DEFAULT_NUMBER_MAX = 5.0
DEFAULT_NUMBER_STEP = 0.5
_SAME = 0.05  # °C: ennyin belül két kalibrációs érték azonosnak számít
_NOT_TRACKING = ("off", "none", "unknown", "unavailable", "")


def _num(value: Any) -> float | None:
    """Véges szám vagy None."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _iso(ts: float | None) -> str | None:
    if not ts:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _near(a: float, b: float) -> bool:
    return abs(a - b) < _SAME


def median(values: list[float]) -> float:
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def round_to_step(value: float, step: float) -> float:
    """A lépésköz legközelebbi többszörösére kerekít (a fél lépés nulltól távolodva)."""
    if step <= 0:
        return value
    steps = math.floor(abs(value) / step + 0.5)
    return round(math.copysign(steps * step, value), 4) + 0.0


def plan_offset(
    diff: float,
    offset: float,
    orig: float | None,
    low: float,
    high: float,
    step: float,
) -> float | None:
    """Az új kalibrációs érték a mért eltérésből; None, ha nincs mit módosítani.

    `diff` = szoba hőmérő - szelep mérése. A cél: offset + diff, az eredeti értéktől legfeljebb
    `CAL_MAX_TOTAL` fokra, a szám-entitás határain belül, a lépésközre kerekítve.
    """
    base = offset if orig is None else orig
    target = offset + diff
    target = min(max(target, base - CAL_MAX_TOTAL), base + CAL_MAX_TOTAL)
    new = round_to_step(min(max(target, low), high), step)
    new = min(max(new, low), high)
    if abs(new - offset) < step / 2:
        return None
    return new


@dataclass
class ValveCal:
    """Egy szelep kalibrációs állapota. Az első blokk tartós (újraindítás után is megmarad)."""

    orig: float | None = None  # a kalibráció a plugin első módosítása előtt
    last_write: float = 0.0
    last_dry: float = 0.0
    writes: list[float] = field(default_factory=list)  # a módosítások ideje az utolsó 24 órában
    # módosítás, aminek a hatását még nem ellenőriztük: from, to, ts, diff, sent, done
    pending: dict[str, Any] | None = None
    # visszaállítás folyamatban: from (a rossz érték), to (az előző), n (próbálkozások), ts (utolsó)
    revert: dict[str, Any] | None = None
    strikes: int = 0
    suspended_until: float = 0.0
    last_ok: float | None = None
    last_diff: float | None = None
    last_adjusted: float | None = None

    # --- nem tartós (újraindítás után újraépül)
    samples: list[tuple[float, float, float, float]] = field(default_factory=list)  # (idő, eltérés, kalibráció, szoba)
    next_sample: float = 0.0
    settle_until: float = 0.0
    recheck_until: float = 0.0
    idle_since: float | None = None
    status: str = "waiting"
    reason: str | None = None
    offset: float | None = None
    proposed: float | None = None
    err_logged: float = 0.0

    # ------------------------------------------------------------------ mentés / betöltés
    def to_dict(self) -> dict[str, Any]:
        return {
            "orig": self.orig,
            "last_write": self.last_write,
            "last_dry": self.last_dry,
            "writes": list(self.writes),
            "pending": dict(self.pending) if self.pending else None,
            "revert": dict(self.revert) if self.revert else None,
            "strikes": self.strikes,
            "suspended_until": self.suspended_until,
            "last_ok": self.last_ok,
            "last_diff": self.last_diff,
            "last_adjusted": self.last_adjusted,
        }

    def has_state(self) -> bool:
        """Érdemes-e menteni (volt-e már módosítás, függő művelet vagy felfüggesztés)."""
        return bool(
            self.orig is not None
            or self.pending
            or self.revert
            or self.strikes
            or self.suspended_until
            or self.writes
        )

    @classmethod
    def from_dict(cls, raw: Any, now_ts: float) -> "ValveCal | None":
        """Ellenőrzött betöltés: a hibás vagy értelmetlen érték kimarad."""
        if not isinstance(raw, dict):
            return None
        cal = cls()
        orig = _num(raw.get("orig"))
        if orig is not None and abs(orig) <= 10:
            cal.orig = orig
        for key in ("last_write", "last_dry"):
            value = _num(raw.get(key))
            if value is not None and 0 < value <= now_ts + 60:
                setattr(cal, key, value)
        for key in ("last_ok", "last_adjusted"):
            value = _num(raw.get(key))
            if value is not None and 0 < value <= now_ts + 60:
                setattr(cal, key, value)
        diff = _num(raw.get("last_diff"))
        if diff is not None and abs(diff) <= 50:
            cal.last_diff = diff
        writes = raw.get("writes")
        if isinstance(writes, list):
            cal.writes = sorted(
                t for t in (_num(x) for x in writes) if t is not None and now_ts - 86400 < t <= now_ts + 60
            )
        pending = raw.get("pending")
        if isinstance(pending, dict):
            frm, to = _num(pending.get("from")), _num(pending.get("to"))
            ts, diff_before = _num(pending.get("ts")), _num(pending.get("diff"))
            if (
                None not in (frm, to, ts, diff_before)
                and abs(frm) <= 10
                and abs(to) <= 10
                and 0 < ts <= now_ts + 60
                and abs(diff_before) <= 50
            ):
                cal.pending = {
                    "from": frm,
                    "to": to,
                    "ts": ts,
                    "diff": diff_before,
                    "sent": bool(pending.get("sent")),
                    "done": bool(pending.get("done")),
                }
        revert = raw.get("revert")
        if isinstance(revert, dict):
            frm, to = _num(revert.get("from")), _num(revert.get("to"))
            if None not in (frm, to) and abs(frm) <= 10 and abs(to) <= 10:
                tries = _num(revert.get("n"))
                last = _num(revert.get("ts"))
                cal.revert = {
                    "from": frm,
                    "to": to,
                    "n": min(max(int(tries), 0), CAL_REVERT_TRIES) if tries is not None else 0,
                    "ts": last if last is not None and 0 < last <= now_ts + 60 else 0.0,
                }
        strikes = _num(raw.get("strikes"))
        cal.strikes = min(max(int(strikes), 0), CAL_MAX_STRIKES) if strikes is not None else 0
        until = _num(raw.get("suspended_until"))
        if until is not None and now_ts < until <= now_ts + CAL_SUSPEND_SECONDS + 60:
            cal.suspended_until = until
        return cal


def _number_score(entry: Any) -> int:
    """Mennyire valószínű, hogy a regisztrált szám-entitás a szelep hőmérséklet-kalibrációja."""
    key = (getattr(entry, "translation_key", None) or "").lower()
    if key == "calibration_temperature":
        return 3  # Meross LAN
    name = getattr(entry, "original_name", None) or getattr(entry, "name", None) or ""
    text = f"{entry.entity_id} {name}".lower()
    if "humid" in text:
        return 0
    if "temp" in text and ("calibrat" in text or "offset" in text):
        return 1  # más integrációk szelepei (pl. Zigbee2MQTT local_temperature_calibration)
    return 0


def _is_tracker(entry: Any) -> bool:
    """A Meross LAN "Tracked sensor" választója (külső hőmérő követése)."""
    key = (getattr(entry, "translation_key", None) or "").lower()
    uid = (getattr(entry, "unique_id", None) or "").lower()
    return key == "tracked_sensor" or "tracked_sensor" in uid or "tracked_sensor" in entry.entity_id.lower()


class Calibrator:
    """A vezérlőhöz tartozó kalibrációs logika: mintavétel, döntés, módosítás, ellenőrzés."""

    def __init__(self, ctl: "BoilerController") -> None:
        self.ctl = ctl
        self.cal: dict[str, ValveCal] = {}
        self._ent: dict[str, dict[str, Any]] = {}
        self._last_global = 0.0
        self._boiler_idle_since: float | None = None
        self._issue_rooms: dict[str, str] = {}

    # ------------------------------------------------------------------ mentés / betöltés
    def load(self, raw: Any, valves: set[str], now_ts: float) -> None:
        self.cal = {}
        if isinstance(raw, dict):
            for valve_id, rec in raw.items():
                if valve_id not in valves:
                    continue  # már nem beállított szelep
                cal = ValveCal.from_dict(rec, now_ts)
                if cal is not None:
                    self.cal[valve_id] = cal
        # a két szelep közti időköz újraindítás után sem nullázódik
        self._last_global = max((c.last_write for c in self.cal.values()), default=0.0)

    def to_dict(self) -> dict[str, Any]:
        return {vid: cal.to_dict() for vid, cal in self.cal.items() if cal.has_state()}

    def _save_later(self) -> None:
        self.ctl._store.async_delay_save(self.ctl._data_to_save, 60)

    # ------------------------------------------------------------------ belépési pont
    async def async_run(self, statuses: "list[RoomStatus]", allow: bool, now_ts: float) -> None:
        """Egy kiértékelési kör: csendes idő követése, majd szelepenként a kalibráció."""
        for st in statuses:
            st.calibration = []
        try:
            self._track_boiler(now_ts)
            if not self.ctl.cal_enabled:
                for valve_id, room in list(self._issue_rooms.items()):
                    self._sync_issue(valve_id, room, False)
                return
            for st in statuses:
                for valve_id in st.valves:
                    cal = self.cal.setdefault(valve_id, ValveCal())
                    try:
                        if not st.calibrate:
                            self._stop(cal, "off")
                            self._sync_issue(valve_id, st.name, False)
                        else:
                            await self._async_valve(st, valve_id, cal, allow, now_ts)
                    except Exception as err:  # noqa: BLE001 - a kalibráció hibája nem állíthatja le a fűtést
                        self._stop(cal, "error")
                        if now_ts - cal.err_logged > 1800:
                            cal.err_logged = now_ts
                            _LOGGER.exception("%s: váratlan hiba a szelep kalibrációjában: %s", valve_id, err)
                    st.calibration.append(self._summary(valve_id, cal, now_ts))
        except Exception as err:  # noqa: BLE001
            _LOGGER.exception("Váratlan hiba a kalibrációban: %s", err)

    # ------------------------------------------------------------------ csendes idő
    def _track_boiler(self, now_ts: float) -> None:
        """Mióta nem fűt a kazán (kikapcsolt, vagy bekapcsolt, de tétlen)."""
        boiler = self.ctl.hass.states.get(self.ctl.boiler)
        if boiler is None or boiler.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
            self._boiler_idle_since = None
            return
        action = boiler.attributes.get("hvac_action")
        idle = boiler.state == "off" or action in ("idle", "off")
        if not idle:
            self._boiler_idle_since = None
        elif self._boiler_idle_since is None:
            self._boiler_idle_since = now_ts

    @staticmethod
    def _track_idle(cal: ValveCal, state: Any, now_ts: float) -> None:
        """Mióta nem nyitott a szelep (kikapcsolt, vagy a saját jelentése szerint tétlen)."""
        quiet = state is not None and (
            state.state == "off" or state.attributes.get("hvac_action") in ("idle", "off")
        )
        if not quiet:
            cal.idle_since = None
        elif cal.idle_since is None:
            cal.idle_since = now_ts

    def _quiet(self, cal: ValveCal, now_ts: float) -> bool:
        """A radiátor kihűlt: a kazán vagy a szelep elég régóta nem fűt."""
        if self._boiler_idle_since is not None and now_ts - self._boiler_idle_since >= CAL_QUIET_SECONDS:
            return True
        return cal.idle_since is not None and now_ts - cal.idle_since >= CAL_QUIET_SECONDS

    # ------------------------------------------------------------------ entitások
    def _entities(self, valve_id: str, now_ts: float) -> dict[str, Any]:
        """A szelep kalibráció szám-entitása és (ha van) a külső követés választója."""
        info = self._ent.get(valve_id)
        if info is not None:
            retry = CAL_DISCOVERY_RETRY if info["number"] is None else 3600
            if now_ts - info["ts"] < retry:
                return info
        info = {"number": None, "tracker": None, "reason": "not_found", "ts": now_ts}
        try:
            registry = er.async_get(self.ctl.hass)
            entry = registry.async_get(valve_id)
            device_id = getattr(entry, "device_id", None) if entry is not None else None
            if not device_id:
                info["reason"] = "no_device"
            else:
                best, best_score, disabled_only = None, 0, False
                for item in er.async_entries_for_device(registry, device_id, include_disabled_entities=True):
                    disabled = bool(getattr(item, "disabled", False))
                    if item.domain == "number":
                        score = _number_score(item)
                        if not score:
                            continue
                        if disabled:
                            disabled_only = True
                        elif score > best_score:
                            best, best_score = item.entity_id, score
                    elif item.domain == "select" and not disabled and _is_tracker(item):
                        info["tracker"] = item.entity_id
                if best is not None:
                    info["number"], info["reason"] = best, None
                elif disabled_only:
                    info["reason"] = "disabled"
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("%s: a kalibráció-entitás keresése nem sikerült: %s", valve_id, err)
            info["reason"] = "error"
        self._ent[valve_id] = info
        return info

    def _tracker_active(self, info: dict[str, Any]) -> bool:
        """A Meross LAN külső hőmérőt követ (maga állítja a kalibrációt): ahhoz nem nyúlunk."""
        tracker = info.get("tracker")
        if not tracker:
            return False
        state = self.ctl.hass.states.get(tracker)
        if state is None:
            return False
        return str(state.state).lower() not in _NOT_TRACKING

    @staticmethod
    def _limits(state: Any) -> tuple[float, float, float] | None:
        """(min, max, lépésköz) a szám-entitás állapotából; None, ha nem hihető kalibráció-tartomány."""
        low = _num(state.attributes.get("min"))
        high = _num(state.attributes.get("max"))
        step = _num(state.attributes.get("step"))
        if low is None or high is None or high <= low:
            low, high = DEFAULT_NUMBER_MIN, DEFAULT_NUMBER_MAX
        if step is None or step <= 0:
            step = DEFAULT_NUMBER_STEP
        if high - low > CAL_MAX_RANGE:
            return None
        return low, high, step

    # ------------------------------------------------------------------ állapot / összegzés
    @staticmethod
    def _set(cal: ValveCal, status: str, reason: str | None = None) -> None:
        cal.status, cal.reason = status, reason

    def _stop(self, cal: ValveCal, status: str, reason: str | None = None, *, clear: bool = True) -> None:
        """A kör véget ér ezzel az állapottal; a gyűjtött minták (alapból) eldobódnak."""
        if clear:
            cal.samples.clear()
        self._set(cal, status, reason)

    def _summary(self, valve_id: str, cal: ValveCal, now_ts: float) -> dict[str, Any]:
        return {
            "valve": valve_id,
            "status": cal.status,
            "reason": cal.reason,
            "offset": cal.offset,
            "original_offset": cal.orig,
            "difference": None if cal.last_diff is None else round(cal.last_diff, 1),
            "samples": len(cal.samples),
            "last_adjusted": _iso(cal.last_adjusted),
            "proposed_offset": cal.proposed,
            "suspended_until": _iso(cal.suspended_until) if cal.suspended_until > now_ts else None,
        }

    def _sync_issue(self, valve_id: str, room: str, active: bool) -> None:
        self.ctl._sync_issue(
            f"calibration_suspended_{self.ctl.entry_id}_{valve_id}",
            active,
            "calibration_suspended",
            {"room": room, "valve": valve_id, "days": f"{CAL_SUSPEND_SECONDS // 86400}"},
            message=f"A szelep kalibrációja felfüggesztve: {valve_id} ({room})",
        )
        if active:
            self._issue_rooms[valve_id] = room
        else:
            self._issue_rooms.pop(valve_id, None)

    # ------------------------------------------------------------------ egy szelep
    async def _async_valve(
        self, st: "RoomStatus", valve_id: str, cal: ValveCal, allow: bool, now_ts: float
    ) -> None:
        ctl = self.ctl
        state = ctl.hass.states.get(valve_id)
        valid = state is not None and state.state not in (STATE_UNAVAILABLE, STATE_UNKNOWN)
        self._track_idle(cal, state if valid else None, now_ts)
        self._sync_issue(valve_id, st.name, cal.suspended_until > now_ts)
        cal.proposed = None
        if not valid:
            return self._stop(cal, "unavailable")

        info = self._entities(valve_id, now_ts)
        number = info["number"]
        if number is None:
            return self._stop(cal, "no_entity", info["reason"])
        num_state = ctl.hass.states.get(number)
        offset = (
            None
            if num_state is None or num_state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN)
            else _num(num_state.state)
        )
        if offset is None:
            return self._stop(cal, "unavailable", "number")
        cal.offset = offset
        limits = self._limits(num_state)
        if limits is None:
            return self._stop(cal, "no_entity", "range")
        low, high, step = limits

        if self._tracker_active(info):
            return self._stop(cal, "tracker")
        if not allow:
            return self._stop(cal, "waiting", "hold")  # indulás / leállás: még / már nem írunk
        if ctl.cal_dry_run and (cal.pending is not None or cal.revert is not None):
            return self._stop(cal, "waiting", "dry_run")  # próbaüzemben semmit nem módosítunk

        # 1) félbehagyott visszaállítás folytatása (a módosítás hatástalan volt)
        if cal.revert is not None and await self._async_continue_revert(st, valve_id, cal, number, offset, now_ts):
            return

        # 2) felfüggesztés
        if cal.suspended_until:
            if now_ts < cal.suspended_until:
                return self._stop(cal, "suspended")
            cal.suspended_until = 0.0
            cal.strikes = max(CAL_MAX_STRIKES - 1, 0)  # a próba után egyetlen újabb hiba is felfüggeszt
            self._sync_issue(valve_id, st.name, False)
            self._save_later()

        # 3) a függő módosítás egyeztetése a szám-entitás tényleges állapotával
        verdict = self._reconcile(st, valve_id, cal, number, offset, now_ts)
        if verdict == "wait":
            return self._stop(cal, "verifying", "confirm", clear=False)
        if verdict == "lost":
            return self._stop(cal, "waiting", "unsent")  # a parancs el sem ment (leállás): nem az eszköz hibája
        if verdict == "failed":
            suspended = self._add_strike(st, valve_id, cal, now_ts, "rejected")
            return self._stop(cal, "suspended" if suspended else "failed", None if suspended else "rejected")
        if verdict == "external":
            return self._stop(cal, "waiting", "external")

        # 4) mérhetünk-e most?
        reason, ref, reading = self._gate(st, valve_id, state, cal, now_ts)
        if reason is not None:
            if reason == "recheck":
                # a lezárt mérés eredménye (ok / implausible / limit) látszik az újramérésig
                if cal.status in ("ok", "implausible", "limit"):
                    cal.samples.clear()
                    return
                return self._stop(cal, "ok", reason)
            return self._stop(cal, "verifying" if cal.pending and reason == "settling" else "waiting", reason)

        self._sample(cal, ref, reading, offset, now_ts)
        if len(cal.samples) < CAL_MIN_SAMPLES:
            return self._set(cal, "verifying" if cal.pending else "sampling", "samples")
        recent = cal.samples[-CAL_MIN_SAMPLES:]
        diffs = [s[1] for s in recent]
        rooms = [s[3] for s in recent]
        if max(diffs) - min(diffs) > CAL_MAX_SPREAD or max(rooms) - min(rooms) > CAL_MAX_ROOM_SPREAD:
            return self._set(cal, "verifying" if cal.pending else "sampling", "unstable")
        med = median(diffs)
        cal.last_diff = round(med, 2)

        # 5) a legutóbbi módosítás hatásának ellenőrzése
        pend = cal.pending
        if pend is not None:
            # Hatásos, ha a kért változtatásnak legalább a fele megjelent a mérésben. Egy 1 °C-nál
            # kisebb változtatás (tartomány- vagy összhatár miatt levágott módosítás) a mérési
            # zajtól nem különböztethető meg, azt nem ítéljük meg.
            applied = pend["to"] - pend["from"]
            improved = abs(applied) < CAL_JUDGE_MIN or (pend["diff"] - med) / applied >= 0.5
            if not improved:
                return await self._async_ineffective(st, valve_id, cal, number, pend, med, now_ts)
            cal.strikes = 0
            cal.pending = None
            self._save_later()

        # 6) döntés
        if abs(med) < CAL_THRESHOLD:
            cal.strikes = 0
            return self._done(cal, "ok", None, now_ts, healthy=True)
        if abs(med) > CAL_MAX_DIFF:
            return self._done(cal, "implausible", None, now_ts)
        new = plan_offset(med, offset, cal.orig, low, high, step)
        if new is None:
            return self._done(cal, "limit", None, now_ts)
        wait = self._rate_wait(cal, now_ts)
        if wait is not None:
            return self._set(cal, "waiting", wait)
        if ctl._cmd_blocked(number):
            return self._set(cal, "waiting", "backoff")
        if ctl.cal_dry_run:
            return self._propose(st, valve_id, cal, offset, new, med, now_ts)
        await self._async_write(valve_id, cal, number, offset, new, med, now_ts)

    def _done(self, cal: ValveCal, status: str, reason: str | None, now_ts: float, *, healthy: bool = False) -> None:
        """A mérés lezárult; egy ideig nem mér újra."""
        if healthy:
            cal.last_ok = now_ts
        cal.recheck_until = now_ts + CAL_RECHECK_SECONDS
        self._stop(cal, status, reason)

    # ------------------------------------------------------------------ kapuk és mintavétel
    def _gate(
        self, st: "RoomStatus", valve_id: str, state: Any, cal: ValveCal, now_ts: float
    ) -> tuple[str | None, float, float]:
        """(ok, szoba hőmérő, szelep mérése): az ok None, ha most mérhetünk, különben a kapu kódja."""
        if now_ts < cal.recheck_until and cal.pending is None:
            return "recheck", 0.0, 0.0
        if not st.temp_sensor:
            return "no_reference", 0.0, 0.0
        if st.sensor_bad:
            return "unreliable", 0.0, 0.0  # képtelen / ugráló szoba hőmérő: nem lehet referencia
        ref, stale = self.ctl._read_sensor(st.temp_sensor)
        if ref is None:
            return ("stale" if stale else "no_reference"), 0.0, 0.0
        if not CAL_READING_MIN <= ref <= CAL_READING_MAX:
            return "no_reference", 0.0, 0.0
        if st.window_open or st.window_open_since is not None:
            return "window", 0.0, 0.0
        reading = self._reading(state)
        if reading is None:
            return "no_reading", 0.0, 0.0
        if valve_id in self.ctl._boosts:
            return "boost", 0.0, 0.0
        if st.trend is not None and abs(st.trend) > CAL_MAX_TREND:
            return "trend", 0.0, 0.0
        if not self._quiet(cal, now_ts):
            return "not_quiet", 0.0, 0.0
        if now_ts < cal.settle_until:
            return "settling", 0.0, 0.0
        return None, ref, reading

    @staticmethod
    def _reading(state: Any) -> float | None:
        value = _num(state.attributes.get("current_temperature"))
        if value is None or not CAL_READING_MIN <= value <= CAL_READING_MAX:
            return None
        return value

    @staticmethod
    def _sample(cal: ValveCal, ref: float, reading: float, offset: float, now_ts: float) -> None:
        if cal.samples and abs(cal.samples[-1][2] - offset) > _SAME:
            cal.samples.clear()  # közben megváltozott a kalibráció: a régi minták nem érvényesek
        cal.samples = [s for s in cal.samples if now_ts - s[0] <= CAL_SAMPLE_MAX_AGE]
        if now_ts >= cal.next_sample:
            cal.samples.append((now_ts, ref - reading, offset, ref))
            cal.samples = cal.samples[-CAL_MAX_SAMPLES:]
            cal.next_sample = now_ts + CAL_SAMPLE_SECONDS

    def _rate_wait(self, cal: ValveCal, now_ts: float) -> str | None:
        """None, ha most módosíthatunk; különben az ok kódja."""
        if now_ts - cal.last_write < CAL_MIN_INTERVAL:
            return "interval"
        if len([t for t in cal.writes if now_ts - t < 86400]) >= CAL_MAX_PER_DAY:
            return "daily_limit"
        if now_ts - self._last_global < CAL_GLOBAL_SPACING:
            return "spacing"
        return None

    # ------------------------------------------------------------------ módosítás
    def _reconcile(
        self, st: "RoomStatus", valve_id: str, cal: ValveCal, number: str, offset: float, now_ts: float
    ) -> str:
        """A függő módosítás egyeztetése a szám-entitás tényleges értékével.

        none: nincs függő módosítás; confirmed: a szám megtartotta az új értéket (az ellenőrzés mehet);
        wait: még nem telt le a megerősítési idő; failed: a parancs elment, de a szám a régi értéken
        van (az eszköz elutasította); lost: a parancs el sem ment (a HA közben leállt); external: a
        felhasználó közben más értékre állította.
        """
        pend = cal.pending
        if pend is None:
            return "none"
        if _near(offset, pend["to"]) or _near(offset, pend["from"]):
            if now_ts - pend["ts"] < CAL_CONFIRM_SECONDS:
                return "wait"  # a szám optimista: az elutasítás csak később látszik
            if _near(offset, pend["to"]):
                # az új mérésre a hubnak is időt kell hagyni (újraindítás után is a módosítás idejétől számít)
                cal.settle_until = max(cal.settle_until, pend["ts"] + CAL_SETTLE_SECONDS)
                if not pend.get("done"):
                    pend["done"] = True
                    self._announce(st, valve_id, pend["from"], pend["to"], pend["diff"], "auto")
                    self._save_later()
                return "confirmed"
            cal.pending = None
            cal.samples.clear()
            self._save_later()
            if not pend.get("sent"):
                return "lost"
            self.ctl._cmd_result(number, False)  # a parancs elment, de nem érvényesült
            return "failed"
        cal.pending = None
        cal.samples.clear()
        self._save_later()
        return "external"

    def _announce(
        self, st: "RoomStatus", valve_id: str, frm: float, to: float, diff: float | None, reason: str
    ) -> None:
        """A megerősített módosítás naplózása és eseménye."""
        _LOGGER.info(
            "%s: a szelep kalibrációja %+g -> %+g °C%s",
            valve_id,
            frm,
            to,
            "" if reason != "auto" or diff is None else f" (a szelep mérése {self._diff_text(diff)})",
        )
        self.ctl._emit(
            "valve_calibrated",
            st,
            valve=valve_id,
            from_offset=frm,
            to_offset=to,
            difference=None if diff is None else round(diff, 2),
            dry_run=False,
            reason=reason,
        )

    @staticmethod
    def _diff_text(diff: float) -> str:
        return "%.1f °C-kal %s a szoba hőmérőjénél" % (abs(diff), "alacsonyabb" if diff > 0 else "magasabb")

    def _propose(
        self, st: "RoomStatus", valve_id: str, cal: ValveCal, offset: float, new: float, med: float, now_ts: float
    ) -> None:
        """Próbaüzem: csak jelzi, mit módosítana."""
        cal.proposed = new
        self._set(cal, "proposed")
        if now_ts - cal.last_dry < CAL_MIN_INTERVAL:
            return
        cal.last_dry = now_ts
        _LOGGER.info(
            "[PRÓBAÜZEM] %s: a kalibrációt %+g -> %+g °C-ra állítanám (a szelep mérése %s)",
            valve_id,
            offset,
            new,
            self._diff_text(med),
        )
        self.ctl._emit(
            "valve_calibrated",
            st,
            valve=valve_id,
            from_offset=offset,
            to_offset=new,
            difference=round(med, 2),
            dry_run=True,
            reason="auto",
        )
        self._save_later()

    async def _async_write(
        self, valve_id: str, cal: ValveCal, number: str, offset: float, new: float, med: float, now_ts: float
    ) -> None:
        ctl = self.ctl
        if cal.orig is None:
            cal.orig = offset
        # Előre írt rekord: a módosítás előtt a lemezre kerül, mit készülünk csinálni. Újraindítás után
        # a plugin a szám-entitás állapotából látja, megtörtént-e, és az időközök sem nullázódnak.
        cal.pending = {"from": offset, "to": new, "ts": now_ts, "diff": med, "sent": False, "done": False}
        cal.last_write = now_ts
        cal.writes = [t for t in cal.writes if now_ts - t < 86400] + [now_ts]
        self._last_global = now_ts
        await ctl._async_save()
        ok = await ctl._entity_call(
            "number", number, "set_value", value=new, _warn=number not in ctl._cmd_fail
        )
        if not ctl._cmd_result(number, ok):
            cal.pending = None
            self._stop(cal, "failed", "command")
            await ctl._async_save()
            return
        cal.pending["sent"] = True
        cal.last_adjusted = now_ts
        cal.samples.clear()
        cal.settle_until = now_ts + CAL_SETTLE_SECONDS
        self._set(cal, "verifying", "confirm")
        _LOGGER.info(
            "%s: kalibráció-módosítás elküldve: %+g -> %+g °C (a szelep mérése %s); a hatását a következő "
            "csendes mérés igazolja",
            valve_id,
            offset,
            new,
            self._diff_text(med),
        )
        self._save_later()

    def _add_strike(self, st: "RoomStatus", valve_id: str, cal: ValveCal, now_ts: float, why: str) -> bool:
        """Hatástalan módosítás nyilvántartása; igaz, ha emiatt a szelep felfüggesztődött."""
        cal.strikes += 1
        self._save_later()
        if cal.strikes < CAL_MAX_STRIKES:
            return False
        self._suspend(st, valve_id, cal, now_ts, why)
        return True

    def _suspend(self, st: "RoomStatus", valve_id: str, cal: ValveCal, now_ts: float, why: str) -> None:
        cal.suspended_until = now_ts + CAL_SUSPEND_SECONDS
        self._sync_issue(valve_id, st.name, True)
        _LOGGER.warning(
            "%s: a kalibráció %d napra felfüggesztve (ok: %s)", valve_id, CAL_SUSPEND_SECONDS // 86400, why
        )
        self.ctl._emit(
            "valve_calibration_suspended", st, valve=valve_id, days=CAL_SUSPEND_SECONDS // 86400, reason=why
        )
        self._save_later()

    async def _async_ineffective(
        self,
        st: "RoomStatus",
        valve_id: str,
        cal: ValveCal,
        number: str,
        pend: dict[str, Any],
        med: float,
        now_ts: float,
    ) -> None:
        """A módosítás nem vitte közelebb a szelepet a szoba hőmérőjéhez: visszaállítja, és számolja."""
        _LOGGER.warning(
            "%s: a kalibráció módosítása (%+g -> %+g °C) nem hozta közelebb a szelep mérését a szoba "
            "hőmérőjéhez (előtte %.1f, utána %.1f °C eltérés); visszaállítom az előző értéket",
            valve_id,
            pend["from"],
            pend["to"],
            pend["diff"],
            med,
        )
        cal.pending = None
        cal.samples.clear()
        cal.settle_until = now_ts + CAL_SETTLE_SECONDS
        suspended = self._add_strike(st, valve_id, cal, now_ts, "ineffective")
        cal.revert = {"from": pend["to"], "to": pend["from"], "n": 0, "ts": 0.0}
        await self.ctl._async_save()  # a visszaállítási szándék a lemezen van, mielőtt a parancs elmegy
        await self._async_continue_revert(st, valve_id, cal, number, pend["to"], now_ts)
        if suspended:
            self._set(cal, "suspended")
        else:
            self._set(cal, "waiting", "reverted")

    async def _async_continue_revert(
        self, st: "RoomStatus", valve_id: str, cal: ValveCal, number: str, offset: float, now_ts: float
    ) -> bool:
        """A visszaállítás küldése / követése. Igaz, ha ebben a körben ez volt a teendő."""
        ctl = self.ctl
        rev = cal.revert
        if rev is None:
            return False
        if _near(offset, rev["to"]):
            # megvan: az előző érték visszakerült
            cal.revert = None
            self._announce(st, valve_id, rev["from"], rev["to"], cal.last_diff, "revert")
            self._save_later()
            return False
        if not _near(offset, rev["from"]):
            cal.revert = None  # a felhasználó közben máshova állította: nem írjuk felül
            self._save_later()
            return False
        if now_ts - rev["ts"] < CAL_CONFIRM_SECONDS:
            self._set(cal, "waiting", "reverting")
            return True
        if rev["n"] >= CAL_REVERT_TRIES:
            cal.revert = None
            _LOGGER.warning(
                "%s: a kalibrációt nem sikerült visszaállítani (%s: %+g °C). Állítsd vissza kézzel a(z) %s "
                "entitáson %+g °C-ra",
                valve_id,
                number,
                rev["from"],
                number,
                rev["to"],
            )
            if not cal.suspended_until:
                self._suspend(st, valve_id, cal, now_ts, "revert_failed")
            self._save_later()
            return False
        if ctl._cmd_blocked(number):
            self._set(cal, "waiting", "backoff")
            return True
        rev["n"] += 1
        rev["ts"] = now_ts
        cal.last_write = now_ts
        cal.writes = [t for t in cal.writes if now_ts - t < 86400] + [now_ts]
        self._last_global = now_ts
        ok = await ctl._entity_call(
            "number", number, "set_value", value=rev["to"], _warn=number not in ctl._cmd_fail
        )
        ctl._cmd_result(number, ok)
        self._save_later()
        self._set(cal, "waiting", "reverting")
        return True
