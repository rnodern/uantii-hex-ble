"""Send lamp commands over short-lived Bluetooth connections."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging
import re

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.components.light import EFFECT_OFF
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    BASIC_MODES,
    CONTROL_UUID,
    DOMAIN,
    LAMP_NAME,
    POWER_OFF,
    POWER_ON,
)

_LOGGER = logging.getLogger(__name__)
_DEVICE_IDENTIFIER = re.compile(rb"[A-Z0-9]{8,32}")


class UanTiiHexController:
    """Verify the lamp identity before writing to its control characteristic."""

    def __init__(
        self, hass: HomeAssistant, address: str, identifier: str | None = None
    ) -> None:
        self._hass = hass
        self._address = address
        self._identifier = identifier
        self._command_lock = asyncio.Lock()
        self.unique_id = address.replace(":", "").lower()
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            manufacturer="UanTii",
            model="MELK-OA21",
            name=LAMP_NAME,
        )
        self.mode_signal = f"{DOMAIN}_{self.unique_id}_mode"
        self.mode_number: int | None = None
        self.active_effect: str | None = None

    def _ble_device(self):
        return bluetooth.async_ble_device_from_address(self._hass, self._address, True)

    async def async_set_power(self, is_on: bool) -> None:
        """Send the same on or off command the phone app sends."""
        async with self._command_lock:
            await self._async_write(POWER_ON if is_on else POWER_OFF)

    async def async_turn_on(
        self,
        rgb: tuple[int, int, int] | None,
        brightness: int | None,
        effect: str | None,
    ) -> None:
        """Apply power, colour or effect and brightness in one Bluetooth session."""
        commands = [POWER_ON]
        index = None
        if effect is not None and effect != EFFECT_OFF:
            index = next(
                (i for i, (name, _) in enumerate(BASIC_MODES) if name == effect), None
            )
            if index is None:
                raise HomeAssistantError(f"Unknown lamp effect: {effect}")
            commands.append(self._mode_command(index))
        elif rgb is not None:
            commands.append(bytes((0x7E, 0x07, 0x05, 0x03, *rgb, 0x10, 0xEF)))
        if brightness is not None:
            percent = max(1, round(brightness * 100 / 255))
            commands.append(bytes((0x7E, 0x04, 0x01, percent, 0xFF, 0xFF, 0xFF, 0, 0xEF)))

        async with self._command_lock:
            await self._async_write(*commands)
            if index is not None:
                self._set_mode(index)
            elif rgb is not None:
                self.active_effect = EFFECT_OFF

    async def async_step_mode(self, step: int) -> None:
        """Select the adjacent Basic effect and remember its position."""
        async with self._command_lock:
            if self.mode_number is None:
                index = 0 if step > 0 else len(BASIC_MODES) - 1
            else:
                index = (self.mode_number - 1 + step) % len(BASIC_MODES)

            await self._async_write(POWER_ON, self._mode_command(index))
            self._set_mode(index)

    async def async_set_effect_speed(self, percent: int) -> None:
        """Send the animation speed independently of the selected effect."""
        command = bytes((0x7E, 0x04, 0x02, percent, 0xFF, 0xFF, 0xFF, 0, 0xEF))
        async with self._command_lock:
            await self._async_write(command)

    @staticmethod
    def _mode_command(index: int) -> bytes:
        mode_id = BASIC_MODES[index][1]
        return bytes((0x7E, 0x05, 0x03, mode_id, 0x06, 0xFF, 0xFF, 0, 0xEF))

    @callback
    def _set_mode(self, index: int) -> None:
        self.mode_number = index + 1
        self.active_effect = BASIC_MODES[index][0]
        async_dispatcher_send(self._hass, self.mode_signal)

    @callback
    def async_restore_mode_number(self, number: int) -> None:
        """Recover the previous selection without writing to the lamp."""
        if self.mode_number is None and 1 <= number <= len(BASIC_MODES):
            self.mode_number = number

    async def async_read_identifier(self) -> str:
        """Verify the lamp endpoint during setup without changing the light."""
        async with self._connection() as (_, _, identifier):
            return identifier

    async def _async_write(self, *commands: bytes) -> None:
        """Write a short batch without keeping the lamp connected."""
        async with self._connection() as (client, control, _):
            for command in commands:
                await client.write_gatt_char(control, command, response=False)
                await asyncio.sleep(0.2)
            await asyncio.sleep(0.5)

    @asynccontextmanager
    async def _connection(
        self,
    ) -> AsyncIterator[tuple[BleakClientWithServiceCache, BleakGATTCharacteristic, str]]:
        """Check the GATT characteristic and controller identity before use."""
        device = self._ble_device()
        if device is None:
            raise HomeAssistantError(f"{LAMP_NAME} is out of Bluetooth reach")

        client = None
        try:
            async with asyncio.timeout(20):
                client = await establish_connection(
                    BleakClientWithServiceCache,
                    device,
                    device.name or LAMP_NAME,
                    max_attempts=3,
                    ble_device_callback=lambda: self._ble_device() or device,
                )
                control = client.services.get_characteristic(CONTROL_UUID)
                if control is None or not {"read", "write-without-response"}.issubset(
                    control.properties
                ):
                    raise HomeAssistantError(f"{LAMP_NAME} control characteristic is unavailable")

                raw = (await client.read_gatt_char(control, use_cached=False)).rstrip(b"\x00")
                if not _DEVICE_IDENTIFIER.fullmatch(raw):
                    raise HomeAssistantError("Unrecognised lamp identifier")
                identifier = raw.decode("ascii")
                if self._identifier is not None and self._identifier != identifier:
                    raise HomeAssistantError("The Bluetooth device identity does not match the lamp")
                yield client, control, identifier
                self._identifier = identifier
        except (BleakError, TimeoutError, OSError) as err:
            raise HomeAssistantError(f"{LAMP_NAME} command failed: {err}") from err
        finally:
            if client is not None:
                try:
                    async with asyncio.timeout(5):
                        await client.disconnect()
                except (BleakError, TimeoutError, OSError) as err:
                    _LOGGER.warning("Could not close the lamp Bluetooth connection: %s", err)
