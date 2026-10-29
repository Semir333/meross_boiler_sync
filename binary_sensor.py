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
        self, controller: BoilerController, entry: ConfigEntry, key: str, name: str
    ) -> None:
        self._controller = controller
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
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

    def __init__(
        self, controller: BoilerController, entry: ConfigEntry, room_id: str, name: str
    ) -> None:
        super().__init__(controller, entry, f"room_{room_id}", f"{name} fűtési igény")
        self._room_id = room_id

    @property
    def is_on(self) -> bool:
        return self._controller.status[self._room_id].calling

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        st = self._controller.status[self._room_id]
        return {
            "valves": st.valves,
            "valve_active": st.active,
            "current_temperature": None if st.current is None else round(st.current, 1),
            "temperature_source": st.source,
            "target_temperature": st.target,
            "effective_target": st.effective_target,
            "humidity": st.humidity,
            "humidity_boost": st.humidity_boost,
        }


class SummerModeSensor(_BaseSensor):
    """Be: nyári mód aktív, a kazán nem kap hőigényt."""

    _attr_icon = "mdi:weather-sunny"

    def __init__(self, controller: BoilerController, entry: ConfigEntry) -> None:
        super().__init__(controller, entry, "summer_mode", "Nyári mód")

    @property
    def is_on(self) -> bool:
        return self._controller.summer_active

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        c = self._controller
        return {
            "outdoor_sensor": c.outdoor_sensor,
            "outdoor_temperature": c.outdoor_now,
            "outdoor_average_24h": c.outdoor_avg,
            "threshold": c.summer_temp,
            "in_summer_period": c.in_summer_period,
            "period_start": "{:02d}-{:02d}".format(*c.summer_start),
            "period_end": "{:02d}-{:02d}".format(*c.summer_end),
        }
