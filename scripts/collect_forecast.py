#!/usr/bin/env python3
"""Daily pull of the NWS Coastal Waters Forecast (CWF) product for LWX
(Baltimore/Washington office), which covers the Maryland portion of the
Chesapeake Bay. Saves the full raw product text plus a parsed record for
the tracked zone (ANZ532: Chesapeake Bay from Sandy Point to North Beach,
the Annapolis stretch).
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "chesapeake-forecast-tracker (contact: kapoc1@gmail.com)"
PRODUCT_URL = "https://api.weather.gov/products/types/CWF/locations/LWX/latest"
TARGET_ZONE = "ANZ532"

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "forecasts" / "raw"
PARSED_DIR = ROOT / "data" / "forecasts" / "parsed"


def fetch_product() -> dict:
    req = urllib.request.Request(PRODUCT_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def extract_zone_segment(product_text: str, zone: str):
    pattern = rf"{zone}-\d+-\n(.*?)\n\$\$"
    match = re.search(pattern, product_text, re.DOTALL)
    return match.group(1).strip() if match else None


def main() -> None:
    product = fetch_product()
    text = product["productText"]
    product_id = product["id"]

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    pulled_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    raw_path = RAW_DIR / f"{pulled_at}_{product_id}.txt"
    raw_path.write_text(text)

    zone_text = extract_zone_segment(text, TARGET_ZONE)
    if zone_text is None:
        print(f"WARNING: zone {TARGET_ZONE} not found in product {product_id}", file=sys.stderr)

    parsed = {
        "pulled_at": pulled_at,
        "product_id": product_id,
        "issuance_time": product["issuanceTime"],
        "zone": TARGET_ZONE,
        "zone_text": zone_text,
        "raw_file": raw_path.name,
    }
    parsed_path = PARSED_DIR / f"{pulled_at}_{TARGET_ZONE}.json"
    parsed_path.write_text(json.dumps(parsed, indent=2))

    print(f"Saved forecast: {raw_path.relative_to(ROOT)} and {parsed_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
