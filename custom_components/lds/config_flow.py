"""Config flow for LeakDefense integration."""
from __future__ import annotations

import logging
import uuid

import aiohttp
import voluptuous as vol

from homeassistant import config_entries

from .const import BASE_URL, CONF_DEVICE_ID, DOMAIN, USER_AGENT

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


async def _login(username: str, password: str) -> tuple[str, str, str, list[dict]]:
    """Log in and return (token, device_hash, uid, panels)."""
    device_id = str(uuid.uuid4())
    headers = {
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BASE_URL}/account/token2",
            headers=headers,
            json={"username": username, "password": password, "deviceid": device_id},
        ) as resp:
            resp.raise_for_status()
            auth = await resp.json()

        token = auth["token"]
        device_hash = auth["deviceHash"]
        uid = auth["uid"]

        async with session.get(
            f"{BASE_URL}/customer/getv3",
            headers={
                "token": token,
                "deviceid": device_hash,
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
                "Accept": "*/*",
            },
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            panels = data["customer"]["Panels"]
            if not panels:
                raise ValueError("no_panels")

    return token, device_hash, uid, panels


class LeakDefenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the LeakDefense config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                token, device_hash, uid, panels = await _login(
                    user_input["username"], user_input["password"]
                )
                panel = panels[0]
                address = panel.get("Address1", "Leak Defense")
                city = panel.get("City", "")
                title = f"{address}, {city}" if city else address

                await self.async_set_unique_id(uid)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data={
                        "token": token,
                        CONF_DEVICE_ID: device_hash,
                    },
                )

            except aiohttp.ClientResponseError as err:
                _LOGGER.warning("Auth error: %s", err)
                errors["base"] = "invalid_auth"
            except aiohttp.ClientError as err:
                _LOGGER.warning("Connection error: %s", err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.exception("Unexpected error: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
