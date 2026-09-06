# Chesapeake Forecast Reliability Tracker

Portfolio project (part of a 4-project set — see `~/Projects/contract-jobs/docs/PROJECTS.md` for the tracker across all of them). Compares NWS marine forecasts against NDBC buoy actuals for a Chesapeake Bay zone, to score forecast accuracy by lead time.

**See README.md for the project pitch and findings (written for a portfolio audience).**

## Data Sources (both free, no auth beyond a descriptive User-Agent)

| Source | What | Status |
|---|---|---|
| `api.weather.gov` — CWF product, LWX office | Coastal Waters Forecast text, zone ANZ532 (Sandy Point to North Beach / Annapolis) | **WORKING** |
| `ndbc.noaa.gov/data/realtime2/TPLM2.txt` | Buoy actuals, Thomas Point Light | **WORKING** |

Note: the `/zones/{type}/{zoneId}/forecast` structured JSON endpoint does **not** support marine zones (404 "Marine Forecast Not Supported" — confirmed live 2026-09-06). The only path is the raw CWF text product, parsed per-zone in `scripts/collect_forecast.py`.

## Project Structure

```
scripts/
  collect_forecast.py   # pulls latest CWF product, saves raw text + parsed ANZ532 segment
  collect_actuals.py    # pulls NDBC TPLM2 realtime observations
data/
  forecasts/raw/        # full CWF product text, one file per pull
  forecasts/parsed/     # {pulled_at, issuance_time, zone, zone_text} JSON per pull
  actuals/raw/          # NDBC realtime2 snapshot, one file per pull
.github/workflows/collect.yml   # daily cron (12:00 UTC), commits new data back to the repo
```

Both scripts are stdlib-only (no pip install step in CI, nothing to break).

## Status

- 2026-09-06: repo scaffolded, collectors seeded with one manual pull each, cron live via GitHub Actions.
- No accuracy analysis yet — needs weeks/months of accumulated data first. There's no historical forecast archive to backtest against, so this can only be scored forward from when the pipeline started.

## Next steps (when enough data has accumulated)

- Write a scoring script: match each forecast period (e.g. "TODAY", "TONIGHT") against the actuals timestamp range it covers, compare predicted vs. observed wind speed/direction and wave height.
- Decide accuracy metric(s) — e.g. mean absolute error on wind speed, categorical hit rate on Small Craft Advisory calls.
- Build the presentation layer (static site via GitHub Pages, per the portfolio's hosting convention) once there's something worth showing.
