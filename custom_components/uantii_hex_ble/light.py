"""Expose power, RGB, brightness, white and effects as a Home Assistant light."""

import asyncio
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ATTR_WHITE,
    EFFECT_OFF,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.const import STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity, RestoredExtraData

from . import UanTiiHexConfigEntry
from .const import BASIC_MODES, RGB_WHITE
from .controller import UanTiiHexController

_EFFECTS = [name for name, _ in BASIC_MODES]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UanTiiHexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the hex lamp."""
    async_add_entities([UanTiiHexLight(entry.runtime_data)])


class UanTiiHexLight(LightEntity, RestoreEntity):
    """Show the lamp settings last commanded by Home Assistant."""

    _attr_name = None
    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_assumed_state = True
    _attr_supported_color_modes = {ColorMode.RGB, ColorMode.WHITE}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = [EFFECT_OFF, *_EFFECTS]
    _attr_is_on: bool | None = None
    _solid_mode = ColorMode.RGB

    def __init__(self, controller: UanTiiHexController) -> None:
        self._controller = controller
        self._command_lock = asyncio.Lock()
        self._attr_unique_id = controller.unique_id
        self._attr_device_info = controller.device_info

    @property
    def effect(self) -> str | None:
        """Report the last effect Home Assistant selected."""
        return self._controller.active_effect

    @property
    def color_mode(self) -> ColorMode:
        """Keep brightness available during an effect."""
        if self.effect and self.effect != EFFECT_OFF:
            return ColorMode.BRIGHTNESS
        return self._solid_mode

    @property
    def extra_restore_state_data(self) -> RestoredExtraData:
        """Keep the last static settings even when the lamp is off."""
        return RestoredExtraData(
            {
                "rgb": self._attr_rgb_color,
                "brightness": self._attr_brightness,
                "solid_mode": self._solid_mode,
                "effect": self.effect,
            }
        )

    async def async_added_to_hass(self) -> None:
        """Restore the last recorded command without touching the lamp."""
        await super().async_added_to_hass()
        last = await self.async_get_last_state()
        if last and last.state in (STATE_ON, STATE_OFF):
            self._attr_is_on = last.state == STATE_ON
        if extra := await self.async_get_last_extra_data():
            data = extra.as_dict()
            rgb = data.get("rgb")
            if (
                isinstance(rgb, (list, tuple))
                and len(rgb) == 3
                and all(type(value) is int and 0 <= value <= 255 for value in rgb)
            ):
                self._attr_rgb_color = (rgb[0], rgb[1], rgb[2])
            brightness = data.get("brightness")
            if type(brightness) is int and 1 <= brightness <= 255:
                self._attr_brightness = brightness
            if data.get("solid_mode") == ColorMode.WHITE:
                self._solid_mode = ColorMode.WHITE
            if self._controller.active_effect is None and data.get("effect") in self._attr_effect_list:
                self._controller.active_effect = data["effect"]
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._controller.mode_signal, self._mode_changed
            )
        )

    @callback
    def _mode_changed(self) -> None:
        """A mode command also turns on the lamp."""
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        async with self._command_lock:
            white = kwargs.get(ATTR_WHITE)
            rgb = kwargs.get(ATTR_RGB_COLOR)
            brightness = kwargs.get(ATTR_BRIGHTNESS)
            effect = kwargs.get(ATTR_EFFECT)
            solid_mode = self._solid_mode
            if white is not None:
                rgb, brightness, solid_mode = RGB_WHITE, white, ColorMode.WHITE
            elif rgb is not None:
                solid_mode = ColorMode.RGB
            elif effect == EFFECT_OFF:
                rgb = self._attr_rgb_color or RGB_WHITE

            if brightness == 0:
                await self._async_turn_off()
                return
            try:
                await self._controller.async_turn_on(rgb, brightness, effect)
            except HomeAssistantError:
                self._attr_is_on = None
                self.async_write_ha_state()
                raise
            self._attr_is_on = True
            if rgb is not None and effect in (None, EFFECT_OFF):
                self._attr_rgb_color = tuple(rgb)
                self._solid_mode = solid_mode
            if brightness is not None:
                self._attr_brightness = brightness
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        async with self._command_lock:
            await self._async_turn_off()

    async def _async_turn_off(self) -> None:
        try:
            await self._controller.async_set_power(False)
        except HomeAssistantError:
            self._attr_is_on = None
            self.async_write_ha_state()
            raise
        self._attr_is_on = False
        self.async_write_ha_state()
