"""Kazán ciklus szenzor: indítások száma az elmúlt 24 órában."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .controller import BoilerController


def _iso(ts: float | None) -> str | None:
    if ts is None:
        return None
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    controller: BoilerController = hass.data[DOMAIN][entry.entry_id]
    entities: list[BoilerStartsSensor] = []
    if controller.cycle_monitor:
        entities.append(BoilerStartsSensor(controller, entry))

    # kikapcsolt figyelésnél az entitás eltűnik (csak a saját "sensor" entitásaink)
    valid = {entity.unique_id for entity in entities}
    registry = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.domain == "sensor" and reg_entry.unique_id not in valid:
            registry.async_remove(reg_entry.entity_id)

    async_add_entities(entities)


class BoilerStartsSensor(SensorEntity):
    """A kazán indításainak száma az elmúlt 24 órában (a ciklus-naplóból)."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_icon = "mdi:fire-circle"
    _attr_translation_key = "boiler_starts"
    _attr_state_class = SensorStateClass.MEASUREMENT
    # a kártyák ciklus-sávjához kell, de az előzményekbe nem érdemes menteni
    _unrecorded_attributes = frozenset({"cycles", "last_start", "last_stop"})

    def __init__(self, controller: BoilerController, entry: ConfigEntry) -> None:
        self._controller = controller
        self._attr_unique_id = f"{entry.entry_id}_boiler_starts"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Meross Boiler Sync",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._controller.async_add_listener(self.async_write_ha_state)
        )

    @property
    def native_value(self) -> int:
        return self._controller.cycle_info["starts_24h"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        info = self._controller.cycle_info
        now_ts = dt_util.utcnow().timestamp()
        return {
            "starts_last_hour": info["starts_last_hour"],
            "avg_on_minutes": info["avg_on_minutes"],
            "avg_off_minutes": info["avg_off_minutes"],
            "last_start": _iso(info["last_start"]),
            "last_stop": _iso(info["last_stop"]),
            "cycles": self._controller.cycles.recent_list(now_ts),
        }
