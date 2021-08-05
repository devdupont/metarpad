"""
METARPad for the Adafruit MacroPad.

Reads driver data and colors keys to match current flight rules.
Press the airport's key to display the report string.
"""

import json
from time import sleep
from adafruit_display_text import wrap_text_to_lines
from adafruit_macropad import MacroPad

macropad = MacroPad()
text_lines = macropad.display_text()


##-- Load Global Data --##

DATA = json.load(open("metars.json"))
UPDATED = DATA["updated"]
UPDATED = UPDATED.replace("T", " ")[:UPDATED.find(".")]
DATA = DATA["stations"]
STATIONS = sorted(list(DATA.keys()))

RULES = {
    None: (0, 0, 0),
    "VFR": (0, 255, 0),
    "MVFR": (0, 0, 255),
    "IFR": (255, 0, 0),
    "LIFR": (255, 0, 255),
}


##-- Display Writing Functions --##


def chunks(items: list, n: int) -> list:
    """Yield list chunks of size n"""
    for i in range(0, len(items), n):
        yield items[i : i + n]


def fill_extra(index: int):
    """Clear remaining lines starting at the given index"""
    while index < 5:
        text_lines[index].text = ""
        index += 1


def show_station_list():
    """Write station home screen to display"""
    index = 0
    for group in chunks(STATIONS, 3):
        text_lines[index].text = "    ".join(group)
        index += 1
    fill_extra(index)
    text_lines[4].text = UPDATED
    text_lines.show()


def show_report(report: str):
    """Write text-wrapped report string to display"""
    index = 0
    for line in wrap_text_to_lines(report, 21):
        text_lines[index].text = line
        index += 1
    fill_extra(index)
    text_lines.show()


##-- Board Setup --##

show_station_list()
for i, station in enumerate(STATIONS):
    macropad.pixels[i] = RULES[DATA[station]["rules"]]


##-- Main Loop --##

while True:
    key_event = macropad.keys.events.get()

    # On key press/release
    if key_event:
        key_number = key_event.key_number

        # Ignore unassigned key
        if key_number >= len(STATIONS):
            continue

        if key_event.pressed:
            macropad.pixels[key_number] = (100, 100, 100)
            station = STATIONS[key_number]
            report = DATA[station]["report"] or f"{station} No report"
            show_report(report)

        else:
            macropad.pixels[key_number] = RULES[DATA[station]["rules"]]
            show_station_list()

    sleep(0.01)
