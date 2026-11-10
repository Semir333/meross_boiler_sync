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

TRV eltolás (2.12): a szelep saját szabályzása arányos, ezért kis eltérésnél csak részben nyit, és a
szoba lassan vagy sehogy sem melegszik fel. Szobánként megadható eltolás (`trv_offset`, °C) esetén a
kalibráció nem a szoba hőmérőjére, hanem annál ennyivel hidegebb értékre állítja a szelep mérését. A
szelep így a cél alatti szobában mindig teljesen nyit, a célhőmérséklet (a szelepen beállított érték)
pedig változatlan marad. Ez ugyanaz, mintha a szelep célját az eltolással megemelnénk, de nem kell
célhőmérsékletet írni, és ha a HA leáll, a szelepen tartósan csak az eltolásnyi eltérés marad.
Következménye: ha a kazán más szobáknak fűt, ez a szoba a céljánál legfeljebb az eltolásnyival
melegebb lehet. Az eltolás 0 (ki), vagy legalább 1 °C: a kalibráció tűrése (`CAL_THRESHOLD`) miatt
kisebb érték nem érvényesülne.

Az eltolás megváltoztatása (2.14): a kalibráció additív, ezért ha a szelep az előző eltoláshoz volt beállítva
(a plugin ezt tartósan megjegyzi), az új eltoláshoz a kalibrációt pontosan az eltolások különbségével kell
elmozdítani, mérés és kihűlt radiátor nélkül. Így a 0,5 °C-os váltás is, és a fűtés közbeni váltás is percek
alatt érvényesül; a pontos beállítást a következő csendes mérés igazolja.

Az eltolás megváltoztatása (2.16): a szám kézi átállítása (Meross alkalmazás, másik automatika) nem akadály: a
kalibráció additív, ezért a szelep mostani igazítása a rögzítettből kiszámolható, és az új eltolás ehhez képest azonnal
érvényesül. Ha a szelep igazítása nem ismert (új szelep, a rögzítés elveszett), és a radiátor nem hűlt ki (fűtési
időben ez órákig, akár soha nem következik be), a plugin nem vár a mérésre: a mostani értékből, illetve a plugin által
mozgatott eredeti értékből becsül, azonnal módosít, a következő csendes mérés pedig szűk tűréssel ellenőrzi és
szükség esetén javítja. Csendes radiátornál, próbaüzemben és hibapont után a mérés-alapú út dönt. Az eltolás-váltás
(a felhasználó kérése) napi keretét nem a mérésből számolt módosítások 4-es korlátja szabja meg (`CAL_MAX_PER_DAY_USER`).
Ha a szám az utolsó módosítás után (a 60 másodperces megerősítés után is) a régi értékre áll vissza, a hub nem fogadta
el az új értéket (vagy kézzel visszaállították): ezt figyelmeztetés jelzi a naplóban.

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

from . import trvlog
from .const import (
    CAL_BIAS_MIN_SHIFT,
    CAL_CONFIRM_SECONDS,
    CAL_DISCOVERY_RETRY,
    CAL_FIRST_THRESHOLD,
    CAL_GLOBAL_SPACING,
    CAL_GUESS_MAX,
    CAL_IDLE_KEEP_SECONDS,
    CAL_JUDGE_MIN,
    CAL_LATE_REVERT_SECONDS,
    CAL_LATE_REVERTS_MAX,
    CAL_MAX_DIFF,
    CAL_MAX_PER_DAY,
    CAL_MAX_PER_DAY_USER,
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
    CAL_TARGET_LIMIT,
    CAL_THRESHOLD,
    TRV_LOG_STATE_MIN_INTERVAL,
    TRV_OFFSET_MAX,
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
# a naplósor jelzése, ha a szelep korábbi igazítása nem mért, hanem becsült érték (2.15)
_GUESS_NOTE = " (a kiinduló érték becsült, a következő csendes mérés pontosítja)"


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
    """Az új kalibrációs érték a hátralévő korrekcióból; None, ha nincs mit módosítani.

    `diff` = a szelep mérésének kívánt és tényleges értéke közti különbség. Eltolás nélkül a kívánt
    mérés a szoba hőmérője, vagyis `diff` = szoba hőmérő - szelep mérése; eltolásnál a kívánt mérés a
    szoba hőmérője mínusz az eltolás. A cél: offset + diff, az eredeti értéktől legfeljebb
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
    # 2.14: mire volt beállítva a szelep utoljára: az eltolás (a szoba célja) és a kalibráció értéke ekkor.
    # Ebből tudja, hogy az eltolás megváltoztatásakor mennyivel kell a kalibrációt azonnal elmozdítani.
    target: float | None = None
    target_offset: float | None = None
    # 2.15: igazolta-e már egy mérés, hogy a szelep a rögzített eltoláson áll (szűk tűrés, amíg nem)
    aligned: bool = False
    # 2.15: a 2.14 előtti állományból betöltve: a szelep igazítása nincs rögzítve, egyszer becsülhető
    legacy: bool = False
    # 2.16: a késői visszaállások (a szám a megerősítés után a régi értékre állt vissza) ideje az utolsó 24 órában. Nem
    # törli a rendben lévő mérés: egy mérés a visszaállás előtt készült, tehát nem bizonyítja, hogy az eszköz megtartja az értéket.
    late_reverts: list[float] = field(default_factory=list)

    # --- nem tartós (újraindítás után újraépül)
    guessed: bool = False  # a rögzített igazítás becslésből jön (a naplósorban jelezzük)
    samples: list[tuple[float, float, float, float]] = field(default_factory=list)  # (idő, eltérés, kalibráció, szoba)
    next_sample: float = 0.0
    settle_until: float = 0.0
    recheck_until: float = 0.0
    idle_since: float | None = None
    dry_logged: tuple[float, float, float] | None = None  # a próbaüzemben utoljára jelzett eltolás-váltás
    traced: tuple[str, str | None] | None = None  # a TRV-naplóba utoljára írt (állapot, ok)
    traced_ts: float = 0.0
    status: str = "waiting"
    reason: str | None = None
    offset: float | None = None
    proposed: float | None = None
    err_logged: float = 0.0
    last_from: float | None = None  # a szám értéke az utolsó elküldött módosítás előtt (a késői visszaállás észleléséhez)
    revert_logged: float = 0.0
    wait_until: float = 0.0  # a sebesség-korlát (időköz / napi darabszám / szünet) várhatóan eddig tart

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
            "target": self.target,
            "target_offset": self.target_offset,
            "aligned": self.aligned,
            "legacy": self.legacy,
            "late_reverts": list(self.late_reverts),
        }

    def forget_target(self) -> None:
        """A szelep igazítása már nem ismert (a módosítás nem érvényesült, vagy közben átállították a számot)."""
        self.target = self.target_offset = None
        self.aligned = self.guessed = False

    def has_state(self) -> bool:
        """Érdemes-e menteni (volt-e már módosítás, függő művelet vagy felfüggesztés)."""
        return bool(
            self.orig is not None
            or self.pending
            or self.revert
            or self.strikes
            or self.suspended_until
            or self.writes
            or self.late_reverts
            or self.target is not None
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
        reverts = raw.get("late_reverts")
        if isinstance(reverts, list):
            cal.late_reverts = sorted(
                t for t in (_num(x) for x in reverts) if t is not None and now_ts - 86400 < t <= now_ts + 60
            )[-CAL_LATE_REVERTS_MAX:]
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
                bias = _num(pending.get("bias"))
                cal.pending = {
                    "from": frm,
                    "to": to,
                    "ts": ts,
                    "diff": diff_before,
                    "sent": bool(pending.get("sent")),
                    "done": bool(pending.get("done")),
                    "judge": pending.get("judge") is not False,  # az eltolás-váltás hatását nem ítéljük meg
                    "bias": bias if bias is not None and 0 <= bias <= TRV_OFFSET_MAX else None,
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
        target, target_offset = _num(raw.get("target")), _num(raw.get("target_offset"))
        # 2.16: a rögzített igazítás negatív is lehet (a szelep melegebbet mutat a szoba hőmérőjénél), és a szám kézi
        # átállítása után a számolt érték a 0..3 °C-os eltolás-tartományon kívülre is eshet
        if target is not None and target_offset is not None and abs(target) <= CAL_TARGET_LIMIT and abs(target_offset) <= 10:
            cal.target, cal.target_offset = target, target_offset
            cal.aligned = raw.get("aligned") is True
        # a "legacy" kulcs hiánya a 2.14 vagy régebbi állományt jelzi: ott a rögzített igazítás még ismeretlen
        legacy = raw.get("legacy")
        cal.legacy = (legacy is None or legacy is True) and cal.orig is not None and cal.target is None
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
    if "temp" in text and "adjust" in text:
        return 2  # a Meross LAN 5.x neve: "Adjust temperature" (az entitás-azonosító a frissítés után is megmarad)
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

    def idle_to_dict(self, now_ts: float) -> dict[str, Any]:
        """A "kihűlt a radiátor" számlálók. Egy beállítás mentése újratölti az integrációt; ha ilyenkor a
        számlálók nulláról indulnának, minden mentés után újra kellene várni a 90 percet."""
        return {
            "saved": now_ts,
            "boiler": self._boiler_idle_since,
            "valves": {vid: cal.idle_since for vid, cal in self.cal.items() if cal.idle_since is not None},
        }

    def load_idle(self, raw: Any, valves: set[str], now_ts: float) -> None:
        """A csendes idő számlálóinak visszatöltése. Csak rövid leállás (újratöltés) után hihető: a HA
        hosszabb kiesése alatt a radiátor felmelegedhetett, ezért akkor a számlálók újraindulnak. Ha a
        szelep vagy a kazán most fűt, a következő kör úgyis törli őket."""
        if not isinstance(raw, dict):
            return
        saved = _num(raw.get("saved"))
        if saved is None or not 0 <= now_ts - saved <= CAL_IDLE_KEEP_SECONDS:
            return
        boiler = _num(raw.get("boiler"))
        if boiler is not None and 0 < boiler <= now_ts:
            self._boiler_idle_since = boiler
        entries = raw.get("valves")
        for valve_id, since in (entries.items() if isinstance(entries, dict) else ()):
            value = _num(since)
            if valve_id in valves and value is not None and 0 < value <= now_ts:
                self.cal.setdefault(valve_id, ValveCal()).idle_since = value

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
                    st.calibration.append(self._summary(valve_id, cal, now_ts, st.trv_offset))
                    self._trace(st, valve_id, cal, now_ts)
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

    def describe_valve(self, valve_id: str, now_ts: float) -> str:
        """Rövid leírás az induló naplósorhoz: melyik szám-entitást használja a szelephez (és mi az értéke), mihez
        volt a szelep utoljára igazítva. Ebből látszik, ha a plugin nem talál használható entitást."""
        info = self._entities(valve_id, now_ts)
        number = info["number"]
        if number is None:
            return trvlog.state_text("no_entity", info["reason"])
        state = self.ctl.hass.states.get(number)
        value = None if state is None else _num(state.state)
        cal = self.cal.get(valve_id)
        parts = [f"kalibráció-szám: {number} (most " + ("?" if value is None else f"{value:+g}") + " °C"
                 + (f", eredeti {cal.orig:+g} °C" if cal is not None and cal.orig is not None else "") + ")"]
        if cal is not None and cal.target is not None:
            parts.append(
                f"utoljára {trvlog.num(cal.target)} °C eltoláshoz volt igazítva"
                + ("" if cal.aligned else " (még nem igazolta mérés)")
            )
        elif cal is not None and cal.legacy:
            parts.append("a korábbi igazítás nincs rögzítve, az első eltolás-váltásnál becsüli")
        else:
            parts.append("a szelep igazítása még nem ismert (az első módosítás becslés, a csendes mérés pontosítja)")
        if cal is not None and cal.suspended_until > now_ts:
            parts.append(
                f"FELFÜGGESZTVE még {trvlog.num((cal.suspended_until - now_ts) / 86400)} napig "
                "(hatástalan módosítások miatt; a Javítások között is látszik)"
            )
        return "; ".join(parts)

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

    def _summary(self, valve_id: str, cal: ValveCal, now_ts: float, bias: float = 0.0) -> dict[str, Any]:
        return {
            "valve": valve_id,
            "status": cal.status,
            "reason": cal.reason,
            "offset": cal.offset,
            "original_offset": cal.orig,
            # szoba hőmérő - szelep mérése, és a kívánt érték (a szoba eltolása)
            "difference": None if cal.last_diff is None else round(cal.last_diff, 1),
            "target_difference": bias,
            "samples": len(cal.samples),
            "last_adjusted": _iso(cal.last_adjusted),
            "proposed_offset": cal.proposed,
            "suspended_until": _iso(cal.suspended_until) if cal.suspended_until > now_ts else None,
            # 2.15: az eltolás, amihez a szelepet utoljára igazította, és hogy mérés igazolta-e
            "aligned_to": cal.target,
            "verified": cal.aligned,
        }

    # az eredmény-jellegű állapotok azonnal kerülnek a naplóba; a "vár / mintavétel" jellegűek ritkábban
    _TRACE_NOW = frozenset({"ok", "proposed", "failed", "suspended", "limit", "implausible"})

    def _trace(self, st: "RoomStatus", valve_id: str, cal: ValveCal, now_ts: float) -> None:
        """A szelep kalibrációs állapotának változása a TRV-naplóba: miért vár, mit mért, mit tervez.

        Csak változáskor ír. Az eredmény-jellegű állapotok (rendben, hiba, javaslat, felfüggesztés, határ)
        azonnal; a többi (vár, mintavétel, ellenőrzés) szelepenként legfeljebb `TRV_LOG_STATE_MIN_INTERVAL`
        másodpercenként, hogy a villogó állapotok ne árasszák el a naplót. A hiba itt sosem szökhet ki.
        """
        try:
            key = (cal.status, cal.reason)
            if key == cal.traced:
                return
            if (
                cal.status not in self._TRACE_NOW
                and cal.traced is not None
                and now_ts - cal.traced_ts < TRV_LOG_STATE_MIN_INTERVAL
            ):
                return
            cal.traced, cal.traced_ts = key, now_ts
            self.ctl._tlog(
                "%s: kalibráció: %s%s",
                self.ctl._valve_label(valve_id),
                trvlog.state_text(cal.status, cal.reason),
                self._trace_context(st, cal, now_ts),
            )
        except Exception as err:  # noqa: BLE001 - a napló hibája nem állíthatja le a kalibrációt
            _LOGGER.debug("%s: a TRV-napló sora nem készült el: %s", valve_id, err)

    def _trace_context(self, st: "RoomStatus", cal: ValveCal, now_ts: float) -> str:
        """A naplósor kiegészítése: eredménynél a mért eltérés; egyébként a kívánt eltolás és amihez a szelep eddig
        igazítva volt (ebből látszik, hogy az eltolás átállítása még nem érvényesült), kihűlésnél a hátralévő idő."""
        parts: list[str] = []
        if cal.status == "ok":
            if cal.last_diff is not None:
                parts.append(f"a szelep mérése {self._diff_text(cal.last_diff, st.trv_offset)}")
        elif cal.status in ("waiting", "sampling", "verifying", "proposed", "limit", "implausible", "suspended", "failed"):
            parts.append(f"kívánt TRV eltolás: {trvlog.num(st.trv_offset)} °C")
            if cal.target is not None and abs(cal.target - st.trv_offset) >= CAL_BIAS_MIN_SHIFT:
                parts.append(
                    f"a szelep eddig {trvlog.num(cal.target)} °C-hoz volt igazítva" + (" (becsült)" if cal.guessed else "")
                )
            elif cal.target is None and cal.status == "waiting" and cal.reason == "not_quiet":
                parts.append("még nem ismert, mihez volt igazítva a szelep, ezért az első igazítás kihűlt radiátort vár")
        if cal.status == "proposed" and cal.proposed is not None:
            parts.append(f"javasolt kalibráció: {cal.proposed:+g} °C")
        if cal.status == "waiting" and cal.reason in ("interval", "daily_limit", "spacing") and cal.wait_until > now_ts:
            parts.append(f"kb. {trvlog.duration(cal.wait_until - now_ts)} múlva próbálja újra")
        if cal.status == "waiting" and cal.reason == "not_quiet":
            ages = [
                now_ts - since
                for since in (self._boiler_idle_since, cal.idle_since)
                if since is not None
            ]
            if ages:
                parts.append(f"még kb. {max(CAL_QUIET_SECONDS - max(ages), 0) / 60:.0f} perc")
        return " – " + "; ".join(parts) if parts else ""

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

        # 3a) 2.14 előtti állomány: a rögzített igazítás ismeretlen, egyszer becsüljük
        self._adopt_legacy(cal, offset)

        # 3b) a szoba eltolását közben megváltoztatták: a különbséget mérés nélkül, azonnal alkalmazzuk
        if await self._async_retarget(st, valve_id, cal, number, offset, (low, high, step), now_ts):
            return

        # 4) mérhetünk-e most?
        reason, ref, reading = self._gate(st, valve_id, state, cal, now_ts)
        if reason is not None:
            if reason == "recheck":
                # a lezárt mérés eredménye (ok / implausible / limit) látszik az újramérésig
                if cal.status in ("ok", "implausible", "limit"):
                    cal.samples.clear()
                    return
                return self._stop(cal, "ok", reason)
            if reason == "not_quiet" and await self._async_blind(st, valve_id, cal, number, offset, (low, high, step), now_ts):
                return
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
            if pend.get("judge", True):
                # Hatásos, ha a kért változtatásnak legalább a fele megjelent a mérésben. Egy 1 °C-nál
                # kisebb változtatás (tartomány- vagy összhatár miatt levágott módosítás) a mérési
                # zajtól nem különböztethető meg, azt nem ítéljük meg.
                applied = pend["to"] - pend["from"]
                improved = abs(applied) < CAL_JUDGE_MIN or (pend["diff"] - med) / applied >= 0.5
                if not improved:
                    return await self._async_ineffective(st, valve_id, cal, number, pend, med, now_ts)
                cal.strikes = 0
            # Az eltolás-váltásnak nincs "előtte" mérése (a felhasználó kérte, nem a szabályozás): nem
            # ítéljük meg, nem számít hibapontnak. Ha a szelep nem követi, az alábbi döntés újra módosít,
            # és az már megítélt módosítás.
            cal.pending = None
            self._save_later()

        # 6) döntés: a szelep mérése a szoba hőmérője mínusz az eltolás legyen (eltolás nélkül: a szoba hőmérője)
        bias = st.trv_offset
        res = med - bias  # a hátralévő korrekció: pozitív, ha a szelep mérését emelni kell
        # Az igazolt szelepnél széles a tűrés (nem ír feleslegesen); amíg egy mérés nem igazolta az igazítást (első
        # beállítás, módosítás, becslés után), szűk, hogy a 0,5 °C-os eltolás ne vesszen el a tűrésben.
        tolerance = CAL_THRESHOLD if cal.aligned and cal.target is not None else CAL_FIRST_THRESHOLD
        if abs(res) < tolerance:
            cal.strikes = 0
            self._remember_target(cal, bias, offset, verified=True)
            return self._done(cal, "ok", None, now_ts, healthy=True)
        if abs(res) > CAL_MAX_DIFF:
            return self._done(cal, "implausible", None, now_ts)
        new = plan_offset(res, offset, cal.orig, low, high, step)
        if new is None:
            return self._done(cal, "limit", None, now_ts)
        wait = self._rate_wait(cal, now_ts)
        if wait is not None:
            return self._set(cal, "waiting", wait)
        if ctl._cmd_blocked(number):
            return self._set(cal, "waiting", "backoff")
        if ctl.cal_dry_run:
            return self._propose(st, valve_id, cal, offset, new, med, now_ts)
        await self._async_write(valve_id, cal, number, offset, new, med, now_ts, bias)

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

    def _rate_wait(self, cal: ValveCal, now_ts: float, *, ignore_interval: bool = False) -> str | None:
        """None, ha most módosíthatunk; különben az ok kódja (és `cal.wait_until`: mikorra enyhül a korlát).

        Az eltolás szándékos megváltoztatása (ignore_interval) nem várja meg a két módosítás közti időközt: az nem
        szabályozási kör, hanem a felhasználó kérése. Neki a napi keret is nagyobb (`CAL_MAX_PER_DAY_USER`): a
        tesztelés közben gyorsan egymás után kért váltások ne fogyasszák el a keretet. A szelepek közti szünet
        mindkettőre érvényes."""
        cal.wait_until = 0.0
        if not ignore_interval and now_ts - cal.last_write < CAL_MIN_INTERVAL:
            cal.wait_until = cal.last_write + CAL_MIN_INTERVAL
            return "interval"
        limit = CAL_MAX_PER_DAY_USER if ignore_interval else CAL_MAX_PER_DAY
        recent = sorted(t for t in cal.writes if now_ts - t < 86400)
        if len(recent) >= limit:
            cal.wait_until = recent[len(recent) - limit] + 86400  # amikor a legrégebbi még számító módosítás kiesik
            return "daily_limit"
        if now_ts - self._last_global < CAL_GLOBAL_SPACING:
            cal.wait_until = self._last_global + CAL_GLOBAL_SPACING
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
                if not pend.get("sent"):
                    # a parancs eljutott az eszközig, de a leállás miatt a vezérlő nem rögzíthette, mihez igazít: a
                    # lemezen a módosítás előtti állapot van, arra építeni (a szám kézi átállítását követő újraszámolás)
                    # a módosítást visszafordítaná
                    pend["sent"] = True
                    if pend.get("bias") is None:
                        cal.forget_target()
                    else:
                        self._remember_target(cal, pend["bias"], pend["to"])
                    cal.guessed = False
                    self._save_later()
                if not pend.get("done"):
                    pend["done"] = True
                    if pend.get("judge", True):
                        self._announce(st, valve_id, pend["from"], pend["to"], pend["diff"], "auto")
                    else:
                        self._announce(st, valve_id, pend["from"], pend["to"], None, "retarget")
                    self._save_later()
                return "confirmed"
            cal.pending = None
            cal.samples.clear()
            cal.forget_target()  # a szelep nem a rögzített értéken van
            self._save_later()
            if not pend.get("sent"):
                return "lost"
            self.ctl._cmd_result(number, False)  # a parancs elment, de nem érvényesült
            return "failed"
        cal.pending = None
        cal.samples.clear()
        cal.forget_target()  # a felhasználó közben máshova állította
        self._save_later()
        return "external"

    def _remember_target(self, cal: ValveCal, bias: float, offset: float, *, verified: bool = False) -> None:
        """Rögzíti, hogy a szelep ezzel az eltolással és ezzel a kalibrációval van beállítva (tartós).

        `verified`: mérés igazolta (rendben állapot); módosítás után még nem igazolt, a következő mérés szűk
        tűréssel ellenőrzi."""
        if verified:
            cal.guessed = False
        if cal.target != bias or cal.target_offset != offset or cal.aligned != verified:
            cal.target, cal.target_offset, cal.aligned = bias, offset, verified
            self._save_later()

    def _adopt_legacy(self, cal: ValveCal, offset: float) -> None:
        """A 2.14 előtti állományban nincs rögzítve, mihez volt igazítva a szelep, ezért az eltolás első
        megváltoztatása kihűlt radiátorra (órákig) várna. Egyszer, a frissítés után becsüljük: a plugin a szelep
        eredeti kalibrációját (`orig`) mozgatta, és a kalibráció additív, tehát az eredeti és a mostani érték
        különbsége az eddig alkalmazott eltolás. A becslés hibája legfeljebb a szelep és a szoba hőmérőjének
        saját eltérése; a becslésre épülő igazítás nincs igazolva, ezért a következő csendes mérés szűk
        tűréssel ellenőrzi és szükség esetén javítja."""
        if not cal.legacy:
            return
        cal.legacy = False
        self._save_later()
        if cal.target is not None or cal.orig is None:
            return
        anchor = cal.orig - offset
        if not -CAL_BIAS_MIN_SHIFT <= anchor <= CAL_GUESS_MAX:
            return  # nem hihető eltolás (pl. kézzel átállított kalibráció): marad a mérés
        cal.target = min(max(anchor, 0.0), TRV_OFFSET_MAX)
        cal.target_offset = offset
        cal.aligned = False
        cal.guessed = True

    async def _async_blind(
        self,
        st: "RoomStatus",
        valve_id: str,
        cal: ValveCal,
        number: str,
        offset: float,
        limits: tuple[float, float, float],
        now_ts: float,
    ) -> bool:
        """2.16: nem ismert, mihez van igazítva a szelep, és a radiátor nem hűlt ki (a mérés most nem indulhat):
        becsléssel azonnal teljesíti az eltolást, a pontosítást a következő csendes mérésre bízza.

        Fűtési időben a szelep sokat nyitva van, és a "kihűlt a radiátor" feltétel órákig, néha soha nem teljesül; a
        mérésre várva az eltolás átállítása nem csinál semmit. A becslés kiindulópontja: a plugin a szelep eredeti
        kalibrációját (`orig`) mozgatta, és a kalibráció additív, tehát az eredeti és a mostani érték különbsége az
        eddig alkalmazott eltolás; ha a plugin még nem módosította a szelepet, a mostani értéket tekintjük a szoba
        hőmérőjéhez igazítottnak. A becslés hibája legfeljebb a szelep és a szoba hőmérőjének saját eltérése. A becsült
        igazítás nincs igazolva, ezért a következő csendes mérés szűk tűréssel ellenőrzi és szükség esetén javítja.
        Csendes radiátornál nem fut: ott a mérés pontosabb, és percek alatt elindul; próbaüzemben sem (ott a mérés-alapú
        javaslat az érdekes). A hibás eszközt nem terheli: a becsült módosítás sem marad el a figyelemből, az elutasított
        vagy visszaálló módosítás hibapontot ad, és a hibapontok felfüggesztéshez vezetnek.

        A becslés csak akkor marad meg, ha módosítás lett belőle; ha nincs mit módosítani, semmi nem változik.
        Igaz, ha ebben a körben ez volt a teendő (a kör véget ér)."""
        if self.ctl.cal_dry_run or cal.target is not None or cal.pending is not None or cal.revert is not None:
            return False
        anchor = 0.0 if cal.orig is None else cal.orig - offset
        if not -CAL_BIAS_MIN_SHIFT <= anchor <= CAL_GUESS_MAX:
            return False  # nem hihető kiindulás (például kézzel messzire állított kalibráció): marad a mérés
        anchor = min(max(anchor, 0.0), TRV_OFFSET_MAX)
        if abs(st.trv_offset - anchor) < CAL_BIAS_MIN_SHIFT:
            return False  # a becslés szerint a szelep már jó helyen van: nincs mit módosítani
        cal.target, cal.target_offset, cal.aligned, cal.guessed = anchor, offset, False, True
        if await self._async_retarget(st, valve_id, cal, number, offset, limits, now_ts):
            self._save_later()
            return True
        cal.forget_target()  # nem lett belőle módosítás: a becslés nem marad meg
        return False

    def _note_late_revert(
        self, st: "RoomStatus", valve_id: str, cal: ValveCal, offset: float, now_ts: float
    ) -> str | None:
        """Az utolsó módosítás után a szám a módosítás előtti értékre állt vissza (a 60 másodperces megerősítés után).

        A Meross LAN a számot az új értékre állítja be (optimista), és a hub következő jelentése írja felül: ha az
        eszköz nem fogadta el a módosítást, a régi érték percekkel később jön vissza. Ez ugyanaz, mint a megerősítési
        időn belüli elutasítás, ezért hibapont (két ilyen után a szelep felfüggesztődik: egy olyan eszközre, ami nem
        tartja meg a kalibrációt, nem írunk újra és újra), és a felhasználónak is jelezni kell, a figyelmeztetések
        között (a Naplók oldal alapnézetében látszik).

        Ha 24 órán belül másodszor áll vissza a szám, a szelep azonnal felfüggesztődik, akkor is, ha közben egy mérés
        rendben lévőnek találta (a mérés a visszaállás előtt készült, nem bizonyítja, hogy az eszköz megtartja az
        értéket): különben a "módosít, mérés rendben, visszaáll" kör naponta akár tucatszor megismétlődne.

        None, ha nem késői visszaállásról van szó; "reverted", ha igen; "suspended", ha a szelep emiatt felfüggesztődött."""
        before, written = cal.last_from, cal.target_offset
        if before is None or written is None or not _near(offset, before) or _near(before, written):
            return None
        minutes = (now_ts - cal.last_adjusted) / 60 if cal.last_adjusted else -1
        if not 0 <= minutes <= CAL_LATE_REVERT_SECONDS / 60:
            return None
        cal.last_from = None
        cal.late_reverts = [t for t in cal.late_reverts if now_ts - 86400 < t <= now_ts] + [now_ts]
        del cal.late_reverts[:-CAL_LATE_REVERTS_MAX]
        if len(cal.late_reverts) >= CAL_LATE_REVERTS_MAX:
            cal.strikes = max(cal.strikes, CAL_MAX_STRIKES - 1)  # ismétlődő visszaállás: a közbeeső rendes mérés nem számít
        self.ctl._tlog(
            "%s: a kalibráció-szám a módosítás (%+g -> %+g °C) után %d perccel visszaállt %+g °C-ra (az eszköz nem "
            "tartotta meg, vagy kézzel visszaállították)",
            self.ctl._valve_label(valve_id),
            before,
            written,
            round(minutes),
            offset,
        )
        if now_ts - cal.revert_logged > 1800:
            cal.revert_logged = now_ts
            _LOGGER.warning(
                "%s: a kalibráció-szám a módosítás (%+g -> %+g °C) után %d perccel visszaállt %+g °C-ra. Vagy az eszköz "
                "nem fogadta el az új értéket (a Meross LAN a számot az eszköz jelentése szerint frissíti), vagy kézzel "
                "visszaállították. Ha nem te voltál, a szelep nem tartja meg a kalibrációt: nézd meg a Meross LAN naplóját.",
                valve_id,
                before,
                written,
                round(minutes),
                offset,
            )
        if self._add_strike(st, valve_id, cal, now_ts, "reverted"):
            cal.forget_target()
            return "suspended"
        return "reverted"

    async def _async_retarget(
        self,
        st: "RoomStatus",
        valve_id: str,
        cal: ValveCal,
        number: str,
        offset: float,
        limits: tuple[float, float, float],
        now_ts: float,
    ) -> bool:
        """A szoba eltolását megváltoztatták: a szelep kalibrációját azonnal elmozdítja a különbséggel.

        Mérés nélkül is pontos, mert a kalibráció additív: ha a szelep az előző eltoláshoz volt
        beállítva (`cal.target`), és azóta senki nem nyúlt a számhoz (`cal.target_offset`), akkor az új
        eltoláshoz a kalibrációt pontosan az eltolások különbségével kell elmozdítani, a radiátor
        hőmérsékletétől függetlenül. Enélkül a váltás a kihűlt radiátorra várna (órákig), és a
        kalibráció tűrése (`CAL_THRESHOLD`) a 0,5 °C-os váltásokat el is nyelné. Ami így nem pontos
        (kerekítés, zaj), azt a következő csendes mérés a tűrésen belülre hozza.

        2.16: ha a számot közben átállították (kézzel, az alkalmazásból, másik automatika), az sem akadály: a
        kalibráció additív, ezért a szelep mostani igazítása a rögzítettből kiszámolható (ennyivel hidegebbet mutat
        a szelep, amennyivel a szám a rögzített érték alá ment). Korábban ilyenkor a plugin "idegen módosításnak"
        vette, és kihűlt radiátorra várt: fűtési időben ez órákig, akár soha nem jött el, vagyis az eltolás átállítása
        nem csinált semmit.

        Igaz, ha ebben a körben ez volt a teendő (a kör véget ér); hamis, ha nincs mit módosítani, vagy
        nem tudjuk, mire volt beállítva a szelep: akkor a szokásos, mérés-alapú döntés következik.
        """
        ctl = self.ctl
        if cal.target is None or cal.target_offset is None:
            return False
        if not _near(offset, cal.target_offset):
            moved = cal.target + (cal.target_offset - offset)
            if abs(moved) > CAL_TARGET_LIMIT:
                return False  # nem hihető igazítás: a mérés dönt
            late = self._note_late_revert(st, valve_id, cal, offset, now_ts)
            if late == "suspended":
                self._set(cal, "suspended")
                return True
            if late is None:
                ctl._tlog(
                    "%s: a kalibráció-számot közben átállították (%+g -> %+g °C); a szelep igazítása ennek megfelelően "
                    "%s °C-ról %s °C-ra módosult",
                    ctl._valve_label(valve_id),
                    cal.target_offset,
                    offset,
                    trvlog.num(cal.target),
                    trvlog.num(moved),
                )
            cal.target, cal.target_offset, cal.aligned = moved, offset, False
            self._save_later()
        shift = st.trv_offset - cal.target  # pozitív: a szelepnek még hidegebbet kell mutatnia
        if abs(shift) < CAL_BIAS_MIN_SHIFT:
            return False
        low, high, step = limits
        new = plan_offset(-shift, offset, cal.orig, low, high, step)
        if new is None:
            return False  # határ vagy lépésköz miatt nincs mit módosítani: a csendes mérés dönt
        if ctl.cal_dry_run:
            self._propose(st, valve_id, cal, offset, new, None, now_ts, retarget_from=cal.target)
            return True
        wait = self._rate_wait(cal, now_ts, ignore_interval=True)
        if wait is not None:
            self._set(cal, "waiting", wait)
            return True
        if ctl._cmd_blocked(number):
            self._set(cal, "waiting", "backoff")
            return True
        await self._async_write(
            valve_id, cal, number, offset, new, cal.last_diff or 0.0, now_ts, st.trv_offset, retarget_from=cal.target
        )
        return True

    def _announce(
        self, st: "RoomStatus", valve_id: str, frm: float, to: float, diff: float | None, reason: str
    ) -> None:
        """A megerősített módosítás naplózása és eseménye."""
        if reason == "auto" and diff is not None:
            why = f" (a szelep mérése {self._diff_text(diff, st.trv_offset)})"
        elif reason == "retarget":
            cal = self.cal.get(valve_id)
            note = "; a kiinduló érték becsült" if cal is not None and cal.guessed else ""
            why = f" (az új eltoláshoz igazítva: {trvlog.num(st.trv_offset)} °C{note})"
        elif reason == "revert":
            why = " (visszaállítva: az előző módosítás nem hozta közelebb a szelepet a szoba hőmérőjéhez)"
        else:
            why = ""
        self.ctl._tlog(
            "%s: a szelep kalibrációja %+g -> %+g °C%s",
            self.ctl._valve_label(valve_id),
            frm,
            to,
            why,
        )
        self.ctl._emit(
            "valve_calibrated",
            st,
            valve=valve_id,
            from_offset=frm,
            to_offset=to,
            difference=None if diff is None else round(diff, 2),
            target_difference=st.trv_offset,
            dry_run=False,
            reason=reason,
        )

    @staticmethod
    def _diff_text(diff: float, bias: float = 0.0) -> str:
        if abs(diff) < 0.05:
            text = "megegyezik a szoba hőmérőjével"
        else:
            text = "%.1f °C-kal %s a szoba hőmérőjénél" % (abs(diff), "alacsonyabb" if diff > 0 else "magasabb")
        if bias > 0:
            text += ", a cél %.1f °C-kal alacsonyabb" % bias
        return text

    def _propose(
        self,
        st: "RoomStatus",
        valve_id: str,
        cal: ValveCal,
        offset: float,
        new: float,
        med: float | None,
        now_ts: float,
        *,
        retarget_from: float | None = None,
    ) -> None:
        """Próbaüzem: csak jelzi, mit módosítana. Az eltolás megváltoztatása miatti javaslat (`retarget_from`
        az előző eltolás) nem mérésből jön, és azonnal jelzi magát, ha a javaslat megváltozott."""
        cal.proposed = new
        self._set(cal, "proposed")
        if retarget_from is not None:
            key = (offset, new, st.trv_offset)
            if cal.dry_logged == key and now_ts - cal.last_dry < CAL_MIN_INTERVAL:
                return
            cal.dry_logged = key
        elif now_ts - cal.last_dry < CAL_MIN_INTERVAL:
            return
        cal.last_dry = now_ts
        if retarget_from is None and med is not None:
            self.ctl._tlog(
                "[PRÓBAÜZEM] %s: a kalibrációt %+g -> %+g °C-ra állítanám (a szelep mérése %s)",
                self.ctl._valve_label(valve_id),
                offset,
                new,
                self._diff_text(med, st.trv_offset),
            )
        else:
            self.ctl._tlog(
                "[PRÓBAÜZEM] %s: az eltolás %g -> %g °C, a kalibrációt %+g -> %+g °C-ra állítanám%s",
                self.ctl._valve_label(valve_id),
                retarget_from,
                st.trv_offset,
                offset,
                new,
                _GUESS_NOTE if cal.guessed else "",
            )
        self.ctl._emit(
            "valve_calibrated",
            st,
            valve=valve_id,
            from_offset=offset,
            to_offset=new,
            difference=None if med is None or retarget_from is not None else round(med, 2),
            target_difference=st.trv_offset,
            dry_run=True,
            reason="auto" if retarget_from is None else "retarget",
        )
        self._save_later()

    async def _async_write(
        self,
        valve_id: str,
        cal: ValveCal,
        number: str,
        offset: float,
        new: float,
        med: float,
        now_ts: float,
        bias: float = 0.0,
        *,
        retarget_from: float | None = None,
    ) -> None:
        """A kalibráció módosítása. `retarget_from` megadva az eltolás megváltoztatása miatti módosításról
        van szó (az előző eltolás értéke): annak nincs mérése, és hatását nem ítéljük meg."""
        ctl = self.ctl
        if cal.orig is None:
            cal.orig = offset
        # Előre írt rekord: a módosítás előtt a lemezre kerül, mit készülünk csinálni. Újraindítás után
        # a plugin a szám-entitás állapotából látja, megtörtént-e, és az időközök sem nullázódnak.
        cal.pending = {
            "from": offset,
            "to": new,
            "ts": now_ts,
            "diff": med,
            "sent": False,
            "done": False,
            "judge": retarget_from is None,
            "bias": bias,  # az eltolás, amihez a módosítás igazít (leállás után a rögzített igazítás pótlásához)
        }
        before = (cal.last_write, list(cal.writes), self._last_global)
        cal.last_write = now_ts
        cal.writes = [t for t in cal.writes if now_ts - t < 86400] + [now_ts]
        self._last_global = now_ts
        await ctl._async_save()
        ok = await ctl._entity_call(
            "number", number, "set_value", value=new, _warn=number not in ctl._cmd_fail
        )
        if not ctl._cmd_result(number, ok):
            cal.pending = None
            if retarget_from is not None:
                # A felhasználó kérte, és a parancs biztosan nem ment el: ne merítse a napi keretet, a
                # következő próbálkozást csak a parancs-hibák egyre ritkuló újrapróbálása korlátozza.
                cal.last_write, cal.writes, self._last_global = before
            self._stop(cal, "failed", "command")
            await ctl._async_save()
            return
        cal.pending["sent"] = True
        cal.last_adjusted = now_ts
        cal.last_from = offset
        cal.samples.clear()
        cal.settle_until = now_ts + CAL_SETTLE_SECONDS
        self._remember_target(cal, bias, new)  # a szelep mostantól erre az eltolásra van beállítva
        if retarget_from is None:
            cal.guessed = False  # mérésből számolt módosítás: a kiinduló érték már nem becsült
        self._set(cal, "verifying", "confirm")
        if retarget_from is None:
            self.ctl._tlog(
                "%s: kalibráció-módosítás elküldve: %+g -> %+g °C (a szelep mérése %s); a hatását a következő "
                "csendes mérés igazolja",
                self.ctl._valve_label(valve_id),
                offset,
                new,
                self._diff_text(med, bias),
            )
        else:
            self.ctl._tlog(
                "%s: az eltolás %g -> %g °C, a kalibráció módosítása elküldve: %+g -> %+g °C; a pontos "
                "beállítást a következő csendes mérés igazolja%s",
                self.ctl._valve_label(valve_id),
                retarget_from,
                bias,
                offset,
                new,
                _GUESS_NOTE if cal.guessed else "",
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
        cal.forget_target()  # a visszaállítás után a szelep nem a rögzített értéken áll
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
            cal.forget_target()
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
