"""Lamp identity, captured commands and Basic effect order."""

from homeassistant.const import Platform

DOMAIN = "uantii_hex_ble"
PLATFORMS = (Platform.LIGHT, Platform.BUTTON, Platform.SENSOR, Platform.NUMBER)
LAMP_NAME = "UanTii Hex Lamp"
CONF_IDENTIFIER = "identifier"

CONTROL_UUID = "0000fff3-0000-1000-8000-00805f9b34fb"
POWER_ON = bytes.fromhex("7e0404f00001ff00ef")
POWER_OFF = bytes.fromhex("7e0404000000ff00ef")
RGB_WHITE = (255, 255, 255)

# Magic Lantern's Basic list order. The position and on-wire ID are independent.
# https://gist.github.com/clienthax/5b3cc5fa68f7c4c943f2252eaa21d804
# Auto Play's ID of 0 is from the capture of this lamp.
BASIC_MODES = (
    ("Auto Play", 0),
    ("Magic Forward", 1),
    ("Magic Back", 2),
    ("7-Color Energy", 212),
    ("7-Color Jump", 193),
    ("R-G-B Jump", 194),
    ("Y-C-P Jump", 195),
    ("7-Color Strobe", 196),
    ("R-G-B Strobe", 197),
    ("Y-C-P Strobe", 198),
    ("7-Color Gradual", 199),
    ("R-Y Gradual", 200),
    ("R-P Gradual", 201),
    ("G-C Gradual", 202),
    ("G-Y Gradual", 203),
    ("B-P Gradual", 204),
    ("Red Marquee", 205),
    ("Green Marquee", 206),
    ("Blue Marquee", 207),
    ("Yellow Marquee", 208),
    ("Cyan Marquee", 209),
    ("Purple Marquee", 210),
    ("White Marquee", 211),
    ("7-Color Race", 77),
    ("7-Color Race Back", 78),
    ("R-G-B Race", 79),
    ("R-G-B Race Back", 80),
    ("Y-C-P Race", 81),
    ("Y-C-P Race Back", 82),
    ("7-Color Wave", 83),
    ("7-Color Wave Back", 84),
    ("R-G-B Wave", 85),
    ("R-G-B Wave Back", 86),
    ("Y-C-P Wave", 87),
    ("Y-C-P Wave Back", 88),
    ("7-Color Flush", 181),
    ("7-Color Flush Back", 182),
    ("R-G-B Flush", 183),
    ("R-G-B Flush Back", 184),
    ("Y-C-P Flush", 185),
    ("Y-C-P Flush Back", 186),
    ("7-Color Flush Close", 187),
    ("7-Color Flush Open", 188),
    ("R-G-B Flush Close", 189),
    ("R-G-B Flush Open", 190),
    ("Y-C-P Flush Close", 191),
    ("Y-C-P Flush Open", 192),
)
