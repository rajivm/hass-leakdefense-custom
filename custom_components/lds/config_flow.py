"""Config flow for LeakDefense integration."""
from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import BASE_URL, CONF_DEVICE_ID, DOMAIN, USER_AGENT

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required("token"): str,
        vol.Required(CONF_DEVICE_ID): str,
    }
)


async def _validate_credentials(token: str, device_id: str) -> list[dict]:
    """Validate credentials by calling the API and return panels."""
    headers = {
        "token": token,
        "deviceid": device_id,
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/customer/getv3", headers=headers) as resp:
            resp.raise_for_status()
            data = await resp.json()
            panels = data["customer"]["Panels"]
            if not panels:
                raise ValueError("no_panels")
            return panels


class LeakDefenseConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the LeakDefense config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                panels = await _validate_credentials(
                    user_input["token"], user_input[CONF_DEVICE_ID]
                )
                panel = panels[0]
                address = panel.get("Address1", "LeakDefense")
                city = panel.get("City", "")
                title = f"{address}, {city}" if city else address

                await self.async_set_unique_id(user_input["token"][:16])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=title, data=user_input)

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
