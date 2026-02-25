"""Sensors for LeakDefense: flow rate and temperature."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature, UnitOfTime
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
        entities.append(LeakDefenseFlowSensor(coordinator, panel_id, name))
        entities.append(LeakDefenseCountdownSensor(coordinator, panel_id, name))
        if panel.get("LDS1Metrics", {}) and panel["LDS1Metrics"].get("Temperature") is not None:
            entities.append(LeakDefenseTemperatureSensor(coordinator, panel_id, name))

    async_add_entities(entities)


class LeakDefenseFlowSensor(LeakDefensePanelEntity, SensorEntity):
    """Current flow rate as a percentage of the trip threshold."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water-percent"

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_flow_rate"
        self._attr_name = f"LeakDefense {panel_name} Flow Rate"

    @property
    def native_value(self) -> float | None:
        return self._panel.get("FlowValue")

    @property
    def extra_state_attributes(self) -> dict:
        panel = self._panel
        return {
            "trip_value_pct": panel.get("TripValue"),
            "in_alarm": panel.get("InAlarm"),
            "scene": panel.get("Scene"),
        }


class LeakDefenseCountdownSensor(LeakDefensePanelEntity, SensorEntity):
    """Remaining minutes until the alarm triggers.

    Only meaningful while FlowTrip is True (flow is exceeding the trip rate).
    Returns None when the system is not actively counting down.
    """

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:timer-alert-outline"

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_countdown"
        self._attr_name = f"LeakDefense {panel_name} Alarm Countdown"

    @property
    def native_value(self) -> float | None:
        panel = self._panel
        if not panel.get("FlowTrip"):
            return None
        return panel.get("CountdownTimer")


class LeakDefenseTemperatureSensor(LeakDefensePanelEntity, SensorEntity):
    """Pipe temperature reported by the LDS sensor."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_temperature"
        self._attr_name = f"LeakDefense {panel_name} Temperature"

    @property
    def native_value(self) -> float | None:
        metrics = self._panel.get("LDS1Metrics") or {}
        return metrics.get("Temperature")
