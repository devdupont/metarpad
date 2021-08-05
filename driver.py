"""
METARPad Driver for the Adafruit MacroPad

Uses AVWX to fetch METAR reports and flight rules.
Updates CIRCUITPY drive data to force a soft reset.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
import avwx


##-- Config --##

# Update this list with your airport ICAO IDs
# Sorted alphabetically by the MacroPad code
# Max 12 will display
STATIONS = ["KMCO", "KISM", "KORL", "KSFB"]

UPDATE_INTERVAL = 15 * 60  # 15 minutes


##-- Find CIRCUITPY drive --##

SOURCES = (
    "/Volumes/CIRCUITPY",  # Mac
)


def find_drive() -> Path:
    """Returns the path of a connected CIRCUITPY drive"""
    for source in SOURCES:
        path = Path(source)
        if path.exists():
            return path
    raise Exception("Could not find a CIRCUITPY drive on your machine")


PATH = find_drive() / "metars.json"


##-- Main Loop --##

def main():
    """Fetch reports and save to CIRCUITPY drive"""
    data = {"stations": {}}
    for icao in STATIONS:
        metar = avwx.Metar(icao)
        metar.update()
        data["stations"][icao] = {
            "report": metar.data.sanitized,
            "rules": metar.data.flight_rules,
        }
    data["updated"] = datetime.now(tz=timezone.utc).isoformat()
    json.dump(data, PATH.open("w"))
    print("Updated", data["updated"])


if __name__ == "__main__":
    while True:
        main()
        sleep(UPDATE_INTERVAL)
