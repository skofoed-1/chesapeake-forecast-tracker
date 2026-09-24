#!/usr/bin/env python3
"""Daily pull of NDBC real-time observations for the stations inside the
Annapolis-area Chesapeake Bay marine zone (ANZ532) this project tracks
forecasts for:

- TPLM2: Thomas Point Light (C-MAN). Wind, pressure, temps; no wave sensor.
- 44063: Annapolis CBIBS buoy. Wind and wave height.
"""
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "chesapeake-forecast-tracker (contact: kapoc1@gmail.com)"
STATIONS = ["TPLM2", "44063"]
URL_TEMPLATE = "https://www.ndbc.noaa.gov/data/realtime2/{station}.txt"

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "actuals" / "raw"


def collect(station: str, pulled_at: str) -> Path:
    url = URL_TEMPLATE.format(station=station)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8")

    raw_path = RAW_DIR / f"{pulled_at}_{station}.txt"
    raw_path.write_text(text)
    return raw_path


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pulled_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # One station being down shouldn't cost us the other's data.
    failed = []
    for station in STATIONS:
        try:
            raw_path = collect(station, pulled_at)
        except Exception as exc:
            print(f"ERROR: {station}: {exc}", file=sys.stderr)
            failed.append(station)
            continue
        print(f"Saved actuals: {raw_path.relative_to(ROOT)}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
