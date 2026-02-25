"""LeakDefense Home Assistant integration."""
""" Unofficial Leak Defense Integration """
""" Provided "as-is" under the MIT License. Use at your own risk."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_DEVICE_ID, DOMAIN
from .coordinator import LeakDefenseCoordinator

PLATFORMS = ["sensor", "binary_sensor", "switch", "number"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = LeakDefenseCoordinator(
        hass,
        token=entry.data["token"],
        device_id=entry.data[CONF_DEVICE_ID],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
