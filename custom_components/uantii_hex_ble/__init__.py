"""Control the UanTii hex lamp through Home Assistant Bluetooth."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant

from .const import CONF_IDENTIFIER, PLATFORMS
from .controller import UanTiiHexController

type UanTiiHexConfigEntry = ConfigEntry[UanTiiHexController]


async def async_setup_entry(hass: HomeAssistant, entry: UanTiiHexConfigEntry) -> bool:
    """Set up the lamp and its mode controls."""
    entry.runtime_data = UanTiiHexController(
        hass, entry.data[CONF_ADDRESS], entry.data.get(CONF_IDENTIFIER)
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: UanTiiHexConfigEntry) -> bool:
    """Unload the lamp and its mode controls."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
