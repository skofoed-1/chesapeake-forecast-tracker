#!/usr/bin/env python3
"""Daily pull of the NWS Coastal Waters Forecast (CWF) product for LWX
(Baltimore/Washington office), which covers the Maryland portion of the
Chesapeake Bay. LWX issues the CWF several times a day (6-17 times/day seen
so far), and the API only keeps about a week of them, so every issuance not
already on file is saved: the full raw product text plus a parsed record for
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
LIST_URL = "https://api.weather.gov/products/types/CWF/locations/LWX"
TARGET_ZONE = "ANZ532"

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "forecasts" / "raw"
PARSED_DIR = ROOT / "data" / "forecasts" / "parsed"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def extract_zone_segment(product_text: str, zone: str):
    pattern = rf"{zone}-\d+-\n(.*?)\n\$\$"
    match = re.search(pattern, product_text, re.DOTALL)
    return match.group(1).strip() if match else None


def saved_product_ids() -> set:
    return {json.loads(p.read_text())["product_id"] for p in PARSED_DIR.glob("*.json")}


def save_product(product: dict, pulled_at: str) -> Path:
    text = product["productText"]
    product_id = product["id"]
    issued = datetime.fromisoformat(product["issuanceTime"]).astimezone(timezone.utc)
    issued_stamp = issued.strftime("%Y%m%dT%H%M%SZ")

    raw_path = RAW_DIR / f"{issued_stamp}_{product_id}.txt"
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
    parsed_path = PARSED_DIR / f"{issued_stamp}_{TARGET_ZONE}.json"
    parsed_path.write_text(json.dumps(parsed, indent=2))
    return parsed_path


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    pulled_at = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    have = saved_product_ids()
    listing = fetch_json(LIST_URL)["@graph"]  # newest first
    new = [entry for entry in reversed(listing) if entry["id"] not in have]

    # One bad product fetch shouldn't cost us the rest of the batch.
    failed = []
    for entry in new:
        try:
            parsed_path = save_product(fetch_json(entry["@id"]), pulled_at)
        except Exception as exc:
            print(f"ERROR: product {entry['id']}: {exc}", file=sys.stderr)
            failed.append(entry["id"])
            continue
        print(f"Saved forecast: {parsed_path.relative_to(ROOT)}")

    print(f"{len(new) - len(failed)} new issuance(s) saved, {len(listing) - len(new)} already on file")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
