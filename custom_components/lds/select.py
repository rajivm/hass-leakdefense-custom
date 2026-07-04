"""Scene selector for LeakDefense panels (Home / Standby / Away)."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SCENE_API_TO_LABEL, SCENE_LABEL_TO_API, SCENE_LABELS
from .coordinator import LeakDefenseCoordinator
from .entity import LeakDefensePanelEntity


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LeakDefenseCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        LeakDefenseSceneSelect(
            coordinator,
            panel["Id"],
            panel.get("TextIdentifier", str(panel["Id"])),
        )
        for panel in coordinator.data
    ]
    async_add_entities(entities)


class LeakDefenseSceneSelect(LeakDefensePanelEntity, SelectEntity):
    """Switches the panel between Home, Standby and Away scenes."""

    _attr_icon = "mdi:home-switch"
    _attr_options = SCENE_LABELS

    def __init__(self, coordinator: LeakDefenseCoordinator, panel_id: int, panel_name: str) -> None:
        super().__init__(coordinator, panel_id, panel_name)
        self._attr_unique_id = f"{panel_id}_scene"
        self._attr_name = f"LeakDefense {panel_name} Scene"

    @property
    def current_option(self) -> str | None:
        scene = self._panel.get("Scene")
        if scene is None:
            return None
        # Map the raw API value to a friendly label; fall back to the raw value
        # (title-cased) if the panel reports an unrecognized scene.
        return SCENE_API_TO_LABEL.get(str(scene).upper(), str(scene).title())

    @property
    def available(self) -> bool:
        return not bool(self._panel.get("Offline", False))

    async def async_select_option(self, option: str) -> None:
        scene = SCENE_LABEL_TO_API.get(option)
        if scene is None:
            raise ValueError(f"Unknown scene: {option}")
        await self.coordinator.async_set_scene(self._panel_id, scene)
