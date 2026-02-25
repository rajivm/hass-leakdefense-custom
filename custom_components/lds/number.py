"""Number entities for LeakDefense: trip rate and time to alarm."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
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
        entities.append(LeakDefenseTripRateNumber(coordinator, panel_id, name))
        entities.append(LeakDefenseTimeToAlarmNumber(coordinator, panel_id, name))

    async_add_entities(entities)


class LeakDefenseTripRateNumber(LeakDefensePanelEntity, NumberEntity):
    """Configures the flow rate percentage that triggers the countdown."""

    _attr_icon = "mdi:gauge"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_trip_rate"
        self._attr_name = f"LeakDefense {panel_name} Trip Rate"

    @property
    def native_value(self) -> float | None:
        return self._panel.get("TripValue")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_trip_rate(self._panel_id, int(value))


class LeakDefenseTimeToAlarmNumber(LeakDefensePanelEntity, NumberEntity):
    """Configures how long flow must exceed the trip rate before the alarm triggers."""

    _attr_icon = "mdi:timer-outline"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 1
    _attr_native_max_value = 60
    _attr_native_step = 1
    _attr_device_class = "duration"
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_time_to_alarm"
        self._attr_name = f"LeakDefense {panel_name} Time to Alarm"

    @property
    def native_value(self) -> float | None:
        return self._panel.get("TimerCountdownMinutes")

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_time_to_alarm(self._panel_id, int(value))
