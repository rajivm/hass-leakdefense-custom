"""DataUpdateCoordinator for LeakDefense."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN, USER_AGENT

_LOGGER = logging.getLogger(__name__)


class LeakDefenseCoordinator(DataUpdateCoordinator[list[dict]]):
    """Fetches and caches panel data from the LeakDefense cloud API."""

    def __init__(self, hass: HomeAssistant, token: str, device_id: str) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.token = token
        self.device_id = device_id
        self._session = async_get_clientsession(hass)

    def _headers(self) -> dict[str, str]:
        return {
            "token": self.token,
            "deviceid": self.device_id,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
        }

    async def _async_update_data(self) -> list[dict]:
        try:
            async with self._session.get(
                f"{BASE_URL}/customer/getv3",
                headers=self._headers(),
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["customer"]["Panels"]
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with LeakDefense API: {err}") from err

    def _panel_by_id(self, panel_id: int) -> dict:
        for panel in self.data:
            if panel["Id"] == panel_id:
                return panel
        return {}

    async def async_set_trip_rate(self, panel_id: int, trip_val: int) -> None:
        """Set the flow trip rate threshold for a panel."""
        panel = self._panel_by_id(panel_id)
        scene = panel.get("Scene", "HOME")
        payload = {
            "ApiSource": 3,
            "ReturnPanelVM": True,
            "LegacyRequest": {
                "id": None,
                "mode": None,
                "tripTime": None,
                "tripVal": None,
                "waterOff": None,
                "clearAlarm": None,
                "ApiSource": None,
            },
            "HexRequest": {
                "value": trip_val,
                "ldsNumber": 0,
                "Scene": scene,
                "deviceId": panel_id,
            },
        }
        try:
            async with self._session.post(
                f"{BASE_URL}/Command/SetTripRate",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                if not result.get("Success"):
                    raise Exception(f"SetTripRate failed: {result.get('ErrorMsg')}")
        except aiohttp.ClientError as err:
            raise Exception(f"Error setting trip rate: {err}") from err
        await self.async_request_refresh()

    async def async_set_time_to_alarm(self, panel_id: int, minutes: int) -> None:
        """Set the countdown duration before the alarm triggers."""
        panel = self._panel_by_id(panel_id)
        scene = panel.get("Scene", "HOME")
        trip_val = int(panel.get("TripValue", 10))
        water_on = bool(panel.get("WaterOn", True))
        payload = {
            "ApiSource": 3,
            "ReturnPanelVM": True,
            "LegacyRequest": {
                "id": panel_id,
                "mode": scene,
                "tripTime": minutes,
                "tripVal": trip_val,
                "waterOff": not water_on,
                "clearAlarm": False,
                "ApiSource": 3,
            },
            "HexRequest": {
                "value": minutes,
                "Scene": scene,
                "deviceId": panel_id,
            },
        }
        try:
            async with self._session.post(
                f"{BASE_URL}/Command/SetTripTime",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                if not result.get("Success"):
                    raise Exception(f"SetTripTime failed: {result.get('ErrorMsg')}")
        except aiohttp.ClientError as err:
            raise Exception(f"Error setting time to alarm: {err}") from err
        await self.async_request_refresh()

    async def async_set_scene(self, panel_id: int, scene: str) -> None:
        """Switch a panel's scene (HOME / STANDBY / AWAY).

        Sends a dedicated SetScene command carrying the target scene/mode while
        preserving the panel's current trip-time, trip-rate and valve state so
        nothing else is altered by the switch.
        """
        panel = self._panel_by_id(panel_id)
        minutes = int(panel.get("TimerCountdownMinutes", panel.get("CountdownTimer", 20)))
        trip_val = int(panel.get("TripValue", 10))
        water_on = bool(panel.get("WaterOn", True))
        payload = {
            "ApiSource": 3,
            "ReturnPanelVM": True,
            "LegacyRequest": {
                "id": panel_id,
                "mode": scene,
                "tripTime": minutes,
                "tripVal": trip_val,
                "waterOff": not water_on,
                "clearAlarm": False,
                "ApiSource": 3,
            },
            "HexRequest": {
                "Scene": scene,
                "deviceId": panel_id,
            },
        }
        try:
            async with self._session.post(
                f"{BASE_URL}/Command/SetScene",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                if not result.get("Success"):
                    raise Exception(f"SetScene failed: {result.get('ErrorMsg')}")
        except aiohttp.ClientError as err:
            raise Exception(f"Error setting scene: {err}") from err
        await self.async_request_refresh()

    async def async_set_valve(self, panel_id: int, valve_open: bool, panel: dict) -> None:
        """Send a valve open/close command, then refresh coordinator data."""
        scene = panel.get("Scene", "HOME")
        trip_time = int(panel.get("CountdownTimer", 20))
        trip_val = int(panel.get("TripValue", 10))

        payload = {
            "ApiSource": 3,
            "ReturnPanelVM": True,
            "LegacyRequest": {
                "id": panel_id,
                "mode": scene,
                "tripTime": trip_time,
                "tripVal": trip_val,
                "waterOff": not valve_open,
                "clearAlarm": False,
                "ApiSource": 3,
            },
            "HexRequest": {
                "ValveOpen": valve_open,
                "Scene": scene,
                "deviceId": panel_id,
            },
        }

        try:
            async with self._session.post(
                f"{BASE_URL}/Command/SetWaterValve",
                headers=self._headers(),
                json=payload,
            ) as resp:
                resp.raise_for_status()
                result = await resp.json()
                if not result.get("Success"):
                    raise Exception(f"Valve command failed: {result.get('ErrorMsg')}")
        except aiohttp.ClientError as err:
            raise Exception(f"Error sending valve command: {err}") from err

        await self.async_request_refresh()
