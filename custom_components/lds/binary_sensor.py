"""Binary sensors for LeakDefense: alarm, connectivity, valve moving."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    entities: list[LeakDefensePanelEntity] = []

    for panel in coordinator.data:
        panel_id = panel["Id"]
        name = panel.get("TextIdentifier", str(panel_id))
        entities.extend(
            [
                LeakDefenseAlarmSensor(coordinator, panel_id, name),
                LeakDefenseConnectivitySensor(coordinator, panel_id, name),
                LeakDefenseValveMovingSensor(coordinator, panel_id, name),
            ]
        )

    async_add_entities(entities)


class LeakDefenseAlarmSensor(LeakDefensePanelEntity, BinarySensorEntity):
    """True when the panel is in a leak alarm state."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_alarm"
        self._attr_name = f"LeakDefense {panel_name} Alarm"

    @property
    def is_on(self) -> bool:
        return bool(self._panel.get("InAlarm"))

    @property
    def extra_state_attributes(self) -> dict:
        panel = self._panel
        return {
            "alarm_message": panel.get("AlarmMessage") or None,
            "alarm_header": panel.get("AlarmHeader") or None,
        }


class LeakDefenseConnectivitySensor(LeakDefensePanelEntity, BinarySensorEntity):
    """True when the panel is online (inverted from Offline field)."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_connectivity"
        self._attr_name = f"LeakDefense {panel_name} Connectivity"

    @property
    def is_on(self) -> bool:
        return not bool(self._panel.get("Offline", False))


class LeakDefenseValveMovingSensor(LeakDefensePanelEntity, BinarySensorEntity):
    """True while the valve is in transit (opening or closing)."""

    _attr_icon = "mdi:valve"

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_valve_moving"
        self._attr_name = f"LeakDefense {panel_name} Valve Moving"

    @property
    def is_on(self) -> bool:
        return bool(self._panel.get("IsValveMoving", False))
