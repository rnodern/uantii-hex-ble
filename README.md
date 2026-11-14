# MELK-OA21 Bluetooth lights for Home Assistant

Control compatible `MELK-OA21` RGB lights locally using Home Assistant Bluetooth. This integration was developed and tested on the six-panel UanTii hex light using Magic Lantern.

## Compatibility

The `MELK-OA21` Bluetooth name also appears on other products, including RGB strips. Setup looks for `MELK-OA21` with an optional two-digit hex suffix, then checks for the readable and writable `FFF3` characteristic and a controller identifier.

The [DuoCo StripX integration](https://github.com/tgmstudios/duoco-stripx-ha#protocol-9-byte-frames-characteristic-0000fff3-0000-1000-8000-00805f9b34fb) documents the same command formats for RGB, brightness, effects, speed and power off on a different `MELK-OA21` unit. Its power-on command differs (`01` where the UanTii capture uses `F0`). Whether both commands work on both units is untested. Full compatibility with other `MELK-OA21` products is unverified.

## Install

1. Copy the `custom_components/uantii_hex_ble` directory from this repo into the `custom_components` directory in your Home Assistant configuration.
2. Restart Home Assistant.
3. Leave the panels powered and close Magic Lantern so the controller can accept a new Bluetooth connection.
4. Open **Settings → Devices & services → Add integration**, search for **UanTii Hex Lamp BLE**, and select the lamp. Setup reads the Bluetooth controller identifier before adding the device.

## Controls

- The **light** has on/off, brightness, an RGB picker, a White preset and an effects menu. White uses equal RGB channels. The app's tested CCT tap is available as RGB `[255, 251, 9]` in an action.
- **Mode +** and **Mode −** turn the lamp on and cycle the 47 Basic effects shown in Magic Lantern. They wrap in both directions.
- **Mode number** displays the last effect Home Assistant selected from 1 to 47. The effect name is available as the `mode_name` attribute.
- **Effect speed** adjusts animation playback from 0 to 100.

Home Assistant remembers the last settings it sent across restarts. Magic Lantern and the physical remote can change the lamp independently. The controller can be busy while Magic Lantern is connected.

## Verification

On the six-panel lamp, direct Bluetooth commands for power, RGB, dimming, Auto Play and Magic Forward were visibly confirmed. The application sent effect speed values of 25 and 50, and the brightness and colour controls have been exercised through Home Assistant in an isolated test with simulated Bluetooth. The remaining effect IDs come from the [MELK-OA21 Basic list](https://gist.github.com/clienthax/5b3cc5fa68f7c4c943f2252eaa21d804) and were checked against the integration's command output.
