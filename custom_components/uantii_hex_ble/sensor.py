"""Show the last Basic effect position selected from Home Assistant."""

from homeassistant.components.sensor import RestoreSensor
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UanTiiHexConfigEntry
from .const import BASIC_MODES
from .controller import UanTiiHexController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UanTiiHexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Add the mode number display to the lamp device."""
    async_add_entities([UanTiiModeNumber(entry.runtime_data)])


class UanTiiModeNumber(RestoreSensor):
    """Display the last commanded mode number and name."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_assumed_state = True
    _attr_translation_key = "mode_number"
    _attr_icon = "mdi:format-list-numbered"

    def __init__(self, controller: UanTiiHexController) -> None:
        self._controller = controller
        self._attr_unique_id = f"{controller.unique_id}_mode_number"
        self._attr_device_info = controller.device_info

    @property
    def native_value(self) -> int | None:
        """Return a position from 1 to 47 after a selection has been made."""
        return self._controller.mode_number

    @property
    def extra_state_attributes(self) -> dict[str, str] | None:
        """Give the displayed position its app label."""
        number = self.native_value
        if number is None:
            return None
        return {"mode_name": BASIC_MODES[number - 1][0]}

    async def async_added_to_hass(self) -> None:
        """Restore the last position and subscribe to local changes."""
        await super().async_added_to_hass()
        last = await self.async_get_last_sensor_data()
        if last is not None and type(last.native_value) is int:
            self._controller.async_restore_mode_number(last.native_value)
        self.async_on_remove(
            async_dispatcher_connect(self.hass, self._controller.mode_signal, self._mode_changed)
        )

    @callback
    def _mode_changed(self) -> None:
        self.async_write_ha_state()
