#!/usr/bin/env python3
"""Daily pull of NDBC real-time observations for Thomas Point Light (TPLM2),
the buoy nearest the Annapolis-area Chesapeake Bay marine zone (ANZ532) this
project tracks forecasts for.
"""
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "chesapeake-forecast-tracker (contact: kapoc1@gmail.com)"
STATION = "TPLM2"
URL = f"https://www.ndbc.noaa.gov/data/realtime2/{STATION}.txt"

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "actuals" / "raw"


def main() -> None:
    req = urllib.request.Request(URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    pulled_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_path = RAW_DIR / f"{pulled_at}_{STATION}.txt"
    raw_path.write_text(text)

    print(f"Saved actuals: {raw_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
