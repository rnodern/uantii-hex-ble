"""Find and verify a supported lamp using Home Assistant's Bluetooth adapter."""

import re
from typing import Any

import probatio

from homeassistant.components.bluetooth import async_discovered_service_info
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_IDENTIFIER, DOMAIN, LAMP_NAME
from .controller import UanTiiHexController

_MODEL_NAME = re.compile(r"MELK-OA21(?: +[0-9A-F]{2})?", re.IGNORECASE)


class UanTiiHexBleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Choose a nearby MELK-OA21 lamp."""

    VERSION = 1

    def __init__(self) -> None:
        self._candidates: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Choose a lamp and verify the control characteristic without changing it."""
        errors: dict[str, str] = {}
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            try:
                identifier = await UanTiiHexController(
                    self.hass, address
                ).async_read_identifier()
            except HomeAssistantError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=LAMP_NAME,
                    data={CONF_ADDRESS: address, CONF_IDENTIFIER: identifier},
                )

        if not self._candidates:
            configured = self._async_current_ids()
            self._candidates = {
                info.address: f"{info.name} ({info.address})"
                for info in async_discovered_service_info(self.hass, connectable=True)
                if info.address not in configured and _MODEL_NAME.fullmatch(info.name)
            }
        if not self._candidates:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(
                {probatio.Required(CONF_ADDRESS): probatio.In(self._candidates)}
            ),
            errors=errors,
        )
