"""Water valve switch for LeakDefense."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import LeakDefenseCoordinator
from .entity import LeakDefensePanelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LeakDefenseCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LeakDefenseValveSwitch(
            coordinator,
            panel["Id"],
            panel.get("TextIdentifier", str(panel["Id"])),
        )
        for panel in coordinator.data
    ]
    async_add_entities(entities)


class LeakDefenseValveSwitch(LeakDefensePanelEntity, SwitchEntity):
    """Controls the main water shutoff valve.

    On  = water flowing (valve open)
    Off = water shut off (valve closed)
    """

    _attr_icon = "mdi:pipe-valve"

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_valve"
        self._attr_name = f"LeakDefense {panel_name} Water"

    @property
    def is_on(self) -> bool:
        return bool(self._panel.get("WaterOn", False))

    @property
    def available(self) -> bool:
        return not bool(self._panel.get("Offline", False))

    @property
    def extra_state_attributes(self) -> dict:
        panel = self._panel
        return {
            "scene": panel.get("Scene"),
            "can_receive_command": panel.get("CanRecieveCmd"),
            "valve_moving": panel.get("IsValveMoving"),
            "flow_value_pct": panel.get("FlowValue"),
            "trip_value_pct": panel.get("TripValue"),
            "countdown_timer_min": panel.get("CountdownTimer"),
        }

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_valve(self._panel_id, True, self._panel)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_valve(self._panel_id, False, self._panel)
