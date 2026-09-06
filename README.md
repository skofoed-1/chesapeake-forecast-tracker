# Chesapeake Forecast Reliability Tracker

**Question:** How accurate are NOAA marine forecasts for the Chesapeake Bay, and does accuracy degrade meaningfully as lead time increases?

Sailors plan around multi-day marine forecasts, but forecast providers rarely publish their own accuracy track record by lead time. This project builds one from scratch for a single, well-instrumented stretch of the Bay: it daily-snapshots the official NWS forecast alongside the buoy observations that later reveal what actually happened, so the gap between predicted and actual conditions can be measured directly instead of taken on faith.

## Method

- **Forecast:** NWS Coastal Waters Forecast (CWF) product, issued by the Baltimore/Washington office (LWX), for marine zone **ANZ532**: Chesapeake Bay, Sandy Point to North Beach (the Annapolis stretch).
- **Actuals:** NDBC buoy **TPLM2** (Thomas Point Light), which sits inside that same zone.
- **Cadence:** a scheduled job pulls both sources once daily and commits the raw snapshots to this repo (see `.github/workflows/collect.yml`).
- **Why build forward instead of backfilling:** NOAA/NWS archives past buoy *observations* but not past *forecasts*. There's no public record of "what the forecast said on day X for day X+3," so forecast accuracy here can only be tracked starting from when this pipeline went live, accumulating a real accuracy history week over week.

## Status

Early / data-accumulation phase. The collection pipeline is live; the accuracy analysis (forecast vs. actual, broken out by lead time) will be added once enough history has built up to be meaningful.

## Data

Raw daily snapshots live in `data/`: `forecasts/raw/` (full CWF product text), `forecasts/parsed/` (per-pull JSON with the ANZ532 segment extracted), and `actuals/raw/` (NDBC observation text). Collector scripts are in `scripts/`.

## Stack

Python (stdlib only — no dependencies), GitHub Actions for scheduling, both public NOAA/NWS data sources (no API keys required, descriptive User-Agent only).
