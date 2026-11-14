"""Step through the lamp's Basic effects."""

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UanTiiHexConfigEntry
from .controller import UanTiiHexController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UanTiiHexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the two buttons to the lamp device."""
    controller = entry.runtime_data
    async_add_entities(
        [
            UanTiiModeButton(controller, "mode_plus", "mdi:plus", 1),
            UanTiiModeButton(controller, "mode_minus", "mdi:minus", -1),
        ]
    )


class UanTiiModeButton(ButtonEntity):
    """Move one position in the Basic effects list."""

    _attr_has_entity_name = True

    def __init__(
        self, controller: UanTiiHexController, key: str, icon: str, step: int
    ) -> None:
        self._controller = controller
        self._step = step
        self._attr_translation_key = key
        self._attr_icon = icon
        self._attr_unique_id = f"{controller.unique_id}_{key}"
        self._attr_device_info = controller.device_info
        self.entity_id = f"button.uantii_hex_lamp_{key}"

    async def async_press(self) -> None:
        """Select the next or previous effect."""
        await self._controller.async_step_mode(self._step)
