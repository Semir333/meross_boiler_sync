"""Diagnosztikai szenzorok: szobánkénti hőigény és nyári mód."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_ROOM_ID, CONF_ROOM_NAME, DOMAIN
from .controller import BoilerController


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    controller: BoilerController = hass.data[DOMAIN][entry.entry_id]

    entities: list[_BaseSensor] = [SummerModeSensor(controller, entry)]
    entities += [
        RoomDemandSensor(controller, entry, room[CONF_ROOM_ID], room[CONF_ROOM_NAME])
        for room in controller.rooms
    ]

    # törölt szobák entitásainak eltávolítása
    valid = {entity.unique_id for entity in entities}
    registry = er.async_get(hass)
    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.unique_id not in valid:
            registry.async_remove(reg_entry.entity_id)

    async_add_entities(entities)


class _BaseSensor(BinarySensorEntity):
    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(
        self, controller: BoilerController, entry: ConfigEntry, key: str
    ) -> None:
        # a név a translations/<nyelv>.json "entity" szekciójából jön (translation_key)
        self._controller = controller
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Meross Boiler Sync",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            self._controller.async_add_listener(self.async_write_ha_state)
        )


class RoomDemandSensor(_BaseSensor):
    """Be: a szoba hőt kér a kazántól."""

    _attr_icon = "mdi:radiator"
    _attr_translation_key = "room_demand"

    def __init__(
        self, controller: BoilerController, entry: ConfigEntry, room_id: str, name: str
    ) -> None:
        super().__init__(controller, entry, f"room_{room_id}")
        self._room_id = room_id
        # a fordított név "{room} ..." helyőrzőjébe kerül a szoba neve
        self._attr_translation_placeholders = {"room": name}

    @property
    def is_on(self) -> bool:
        return self._controller.status[self._room_id].boiler_demand

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        st = self._controller.status[self._room_id]
        return {
            "room_name": st.name,
            "valves": st.valves,
            "valve_active": st.active,
            "current_temperature": None if st.current is None else round(st.current, 1),
            "temperature_source": st.source,
            "target_temperature": st.target,
            "effective_target": st.effective_target,
            "humidity": st.humidity,
            "humidity_boost": st.humidity_boost,
            "room_below_target": st.calling,
            "deviation": st.deviation,
            "valve_demand_link": st.valve_demand_link,
            "valve_open_estimate": st.valve_open if st.valve_demand_link else None,
            "boost_threshold": st.boost_threshold,
            "boost_delay_minutes": round(st.boost_delay_s / 60, 1),
            "release_margin": st.release_margin,
            "valve_control": st.valve_control,
            "temperature_sensor_stale": st.sensor_stale,
            "window_open": st.window_open,
            "window_open_pending": st.window_open_since is not None and not st.window_open,
            "valve_boost_resting": st.rest_until is not None,
            "valve_boost_waiting": st.cold_since is not None and not st.boost_wanted,
            "valve_boosted": st.boosted,
            "valve_dry_run": self._controller.valve_dry_run,
        }


class SummerModeSensor(_BaseSensor):
    """Be: nyári mód aktív, a kazán nem kap hőigényt."""

    _attr_icon = "mdi:weather-sunny"
    _attr_translation_key = "summer_mode"

    def __init__(self, controller: BoilerController, entry: ConfigEntry) -> None:
        super().__init__(controller, entry, "summer_mode")

    @property
    def is_on(self) -> bool:
        return self._controller.summer_active

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        c = self._controller
        return {
            "boiler_entity": c.boiler,
            "outdoor_sensor": c.outdoor_sensor,
            "outdoor_temperature": c.outdoor_now,
            "outdoor_sensor_stale": c.outdoor_stale,
            "outdoor_average_24h": c.outdoor_avg,
            "threshold": c.summer_temp,
            "in_summer_period": c.in_summer_period,
            "period_start": "{:02d}-{:02d}".format(*c.summer_start),
            "period_end": "{:02d}-{:02d}".format(*c.summer_end),
        }
