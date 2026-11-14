# UanTii Hex Lamp BLE for Home Assistant

Control the Magic Lantern UanTii hex panels locally using Home Assistant Bluetooth. The commands were captured from a six-panel lamp advertising as `MELK-OA21`. Other controller variants may use a different protocol.

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
