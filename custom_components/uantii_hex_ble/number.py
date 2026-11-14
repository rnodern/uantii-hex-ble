"""Adjust the lamp's animation speed without changing its mode."""

import asyncio

from homeassistant.components.number import NumberMode, RestoreNumber
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UanTiiHexConfigEntry
from .controller import UanTiiHexController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UanTiiHexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the effect speed slider."""
    async_add_entities([UanTiiEffectSpeed(entry.runtime_data)])


class UanTiiEffectSpeed(RestoreNumber):
    """Store the last animation speed Home Assistant sent."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_assumed_state = True
    _attr_translation_key = "effect_speed"
    _attr_mode = NumberMode.SLIDER
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:speedometer"

    def __init__(self, controller: UanTiiHexController) -> None:
        self._controller = controller
        self._command_lock = asyncio.Lock()
        self._attr_unique_id = f"{controller.unique_id}_effect_speed"
        self._attr_device_info = controller.device_info

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if last := await self.async_get_last_number_data():
            self._attr_native_value = last.native_value

    async def async_set_native_value(self, value: float) -> None:
        """Send and remember the selected speed."""
        async with self._command_lock:
            percent = round(value)
            await self._controller.async_set_effect_speed(percent)
            self._attr_native_value = percent
            self.async_write_ha_state()
