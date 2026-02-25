"""Base entity for LeakDefense panels."""
from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import LeakDefenseCoordinator


class LeakDefensePanelEntity(CoordinatorEntity[LeakDefenseCoordinator]):
    """Common base for all LeakDefense panel entities."""

    def __init__(
        self,
        coordinator: LeakDefenseCoordinator,
        panel_id: int,
        panel_name: str,
    ) -> None:
        super().__init__(coordinator)
        self._panel_id = panel_id
        self._panel_name = panel_name

    @property
    def _panel(self) -> dict:
        for panel in self.coordinator.data:
            if panel["Id"] == self._panel_id:
                return panel
        return {}

    @property
    def device_info(self) -> dict:
        panel = self._panel
        return {
            "identifiers": {("leakdefense", str(self._panel_id))},
            "name": f"LeakDefense {self._panel_name}",
            "manufacturer": "LeakDefense",
            "model": "LDS Panel",
            "sw_version": panel.get("Version"),
        }
