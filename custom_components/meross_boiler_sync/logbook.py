"""A meross_boiler_sync_event események megjelenítése a Home Assistant naplójában (Logbook)."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from homeassistant.core import Event, HomeAssistant, callback

from .const import DOMAIN, EVENT_TYPE

_HU_REASON = {
    "target_reached": "cél elérve",
    "expired": "az idő lejárt",
    "cancelled": "lemondva",
    "max_time": "elérte a maximális időt",
    "window": "ablak nyitva",
    "summer": "nyári mód",
    "sensor": "nincs szoba hőmérő",
    "manual": "kézi leállítás",
    "disabled": "kikapcsolva",
    "other": "egyéb ok",
}
_EN_REASON = {
    "target_reached": "target reached",
    "expired": "time ran out",
    "cancelled": "cancelled",
    "max_time": "maximum time reached",
    "window": "window open",
    "summer": "summer mode",
    "sensor": "no room sensor",
    "manual": "stopped manually",
    "disabled": "disabled",
    "other": "other reason",
}


def _offsets(data: dict[str, Any]) -> str:
    frm, to = data.get("from_offset"), data.get("to_offset")
    if isinstance(frm, (int, float)) and isinstance(to, (int, float)):
        return f"{frm:+g} → {to:+g} °C"
    return ""


def _cal_text_hu(data: dict[str, Any]) -> str:
    base = {"revert": "a szelep kalibrációja visszaállítva", "auto": "a szelep kalibrációja módosítva"}
    text = base.get(data.get("reason", "auto"), base["auto"])
    if data.get("dry_run"):
        text = "próbaüzem: a szelep kalibrációját módosítanám"
    return f"{text}: {data.get('valve')} {_offsets(data)}".rstrip()


def _cal_text_en(data: dict[str, Any]) -> str:
    base = {"revert": "valve calibration restored", "auto": "valve calibration changed"}
    text = base.get(data.get("reason", "auto"), base["auto"])
    if data.get("dry_run"):
        text = "dry run: would change the valve calibration"
    return f"{text}: {data.get('valve')} {_offsets(data)}".rstrip()


def describe(language: str, data: dict[str, Any]) -> tuple[str, str]:
    """(név, üzenet) az eseményhez; magyar vagy angol (a HA nyelve szerint)."""
    hu = (language or "").lower().startswith("hu")
    kind = data.get("type", "")
    room = data.get("room") or ("Meross Boiler Sync" if kind in ("short_cycling", "valve_command_failed") else "")
    reasons = _HU_REASON if hu else _EN_REASON
    dev = data.get("deviation")
    if hu:
        msgs = {
            "boost_started": "szelepemelés indult" + (f" ({dev:g}° a cél alatt)" if isinstance(dev, (int, float)) else ""),
            "boost_ended": "a szelepemelés véget ért: " + reasons.get(data.get("reason", ""), reasons["other"]),
            "window_paused": "ablak nyitva, a szoba szünetel",
            "window_resumed": "az ablak bezárva, a fűtés folytatódik",
            "sensor_stale": "elavult szenzor" + (f" ({data['age_minutes']} perce nem frissült)" if data.get("age_minutes") is not None else ""),
            "sensor_recovered": "a szenzor újra frissül",
            "sensor_unreliable": "a szoba hőmérő nem megbízható"
            + (f" ({data['value']:g} °C)" if isinstance(data.get("value"), (int, float)) else "")
            + ", a szelepek saját mérésére váltok",
            "sensor_reliable": "a szoba hőmérő újra megbízhatónak látszik",
            "short_cycling": f"a kazán gyakran kapcsolgat ({data.get('starts_last_hour')} indítás az elmúlt órában)",
            "manual_boost_started": "Fűts most elindult" + (f" ({data['minutes']:g} percre)" if data.get("minutes") is not None else ""),
            "manual_boost_ended": "Fűts most véget ért: " + reasons.get(data.get("reason", ""), reasons["other"]),
            "preheat_started": "előfűtés elindult" + (f" (kész: {data['ready_by']})" if data.get("ready_by") else ""),
            "preheat_unreachable": "az előfűtés nem éri el a célt időre",
            "valve_command_failed": f"a szelep nem fogadta el a parancsot ({data.get('valve')}), egyre ritkábban próbálom újra",
            "valve_calibrated": _cal_text_hu(data),
            "valve_calibration_suspended": f"a szelep kalibrációja felfüggesztve {data.get('days', 7)} napra ({data.get('valve')})",
        }
    else:
        msgs = {
            "boost_started": "valve boost started" + (f" ({dev:g}° below target)" if isinstance(dev, (int, float)) else ""),
            "boost_ended": "valve boost ended: " + reasons.get(data.get("reason", ""), reasons["other"]),
            "window_paused": "window open, room paused",
            "window_resumed": "window closed, heating resumes",
            "sensor_stale": "stale sensor" + (f" (no update for {data['age_minutes']} min)" if data.get("age_minutes") is not None else ""),
            "sensor_recovered": "sensor is updating again",
            "sensor_unreliable": "the room thermometer is not reliable"
            + (f" ({data['value']:g} °C)" if isinstance(data.get("value"), (int, float)) else "")
            + ", switching to the valves' own readings",
            "sensor_reliable": "the room thermometer looks reliable again",
            "short_cycling": f"boiler is short-cycling ({data.get('starts_last_hour')} starts in the last hour)",
            "manual_boost_started": "Heat now started" + (f" ({data['minutes']:g} min)" if data.get("minutes") is not None else ""),
            "manual_boost_ended": "Heat now ended: " + reasons.get(data.get("reason", ""), reasons["other"]),
            "preheat_started": "preheat started" + (f" (ready by {data['ready_by']})" if data.get("ready_by") else ""),
            "preheat_unreachable": "preheat cannot reach the target in time",
            "valve_command_failed": f"the valve rejected a command ({data.get('valve')}), retrying less and less often",
            "valve_calibrated": _cal_text_en(data),
            "valve_calibration_suspended": f"valve calibration suspended for {data.get('days', 7)} days ({data.get('valve')})",
        }
    return room, msgs.get(kind, kind)


@callback
def async_describe_events(
    hass: HomeAssistant,
    async_describe_event: Callable[[str, str, Callable[[Event], dict[str, Any]]], None],
) -> None:
    """Az eseményeket olvasható szöveggel jeleníti meg a naplóban."""

    @callback
    def _describe(event: Event) -> dict[str, Any]:
        name, message = describe(hass.config.language, dict(event.data))
        out: dict[str, Any] = {"name": name, "message": message}
        if event.data.get("entity_id"):
            out["entity_id"] = event.data["entity_id"]
        return out

    async_describe_event(DOMAIN, EVENT_TYPE, _describe)
