"""Config flow for AirGradient integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN

SETUP_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_PORT, default=8088): int
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AirGradient."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Configure an AirGradient HTTP listener."""
        if user_input is not None:
            await self.async_set_unique_id(str(user_input[CONF_PORT]))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="AirGradient", data=user_input)

        return self.async_show_form(step_id="user", data_schema=SETUP_SCHEMA)
