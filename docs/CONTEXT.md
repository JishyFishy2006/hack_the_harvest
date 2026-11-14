# Hack the Harvest: project context

Handoff notes so a new Claude Code session (e.g. in Keeboh) can pick up where planning left off. The deeper research is in `docs/lit-review.md`.

## The challenge
- **Event:** Hack the Harvest (UC Davis / USDA, Sacramento, Nov 14–15 2026). Build window: Sat 10:30 → Sun 9:00 (22.5 h). Submissions through Keeboh. Need ≥5 team members checked in both days to be eligible for the $5k prize.
- **Question (USDA):** using only public satellite/geospatial data, tell whether a cornfield was harvested for **silage** (whole green plant chopped for cattle feed, late summer) or **grain** (kernels combined after dry-down, fall).
- **Why it matters:** USDA estimates production with slow, costly surveys. Silage acres produce no grain, so getting the split wrong distorts grain estimates. The split shifts most in drought years, exactly when timely numbers matter.
- **Judging (25 pts):** presentation 40% (5 min, no Q&A), technical 20%, innovation 20%, feasibility/USDA fit 20%. Ties go to the better presentation.
- **NVIDIA Nemotron side prize:** they want multi-step agentic workflows ("over chatbot"). Plan: an agent that investigates **low-confidence fields** (checks curve → fetches radar if cloud gap → checks residue → compares county stats → relabels or flags, with reasoning). Nemotron never does the core classification. One person owns it; it's off the critical path.

## Compute and data we have
- **Keeboh:** shared Jupyter workspace with a terminal and a **B200 GPU**. The heavy pixel work still happens server-side in Google Earth Engine (GEE); export per-field time series (CSV/Parquet), not raw imagery. Brev credits ($60 / ~12 GPU-h) are a backup.
- **USDA field boundaries + which fields are corn** (from organizers).
- **BARC labeled fields**: Keeboh starter data with field-level **Grain/Silage** reference labels by year (chart "BARC labeled fields by year and harvest type"). Probably USDA Beltsville, Maryland; **not yet inspected**: need counts per year/class, columns, stable field ID, location.
- **NASS Quick Stats** via `/workspace/02_QuickStats/download_corn_acres.py` → `/workspace/corn_grain_silage_acres.csv`. **County-level only in census years 2012, 2017, 2022**; state-level every year. Has `cv_percent` (USDA's own uncertainty). `(D)` = withheld.

## Decisions made
- **Target year: 2022** (county truth; modern imagery: Sentinel-2 A+B, Landsat 8/9, Sentinel-1). 2012 lacks Sentinel-2/Landsat 8 (only striped Landsat 7 + 250 m MODIS), so avoid it except possibly a drought-year story.
- **Region:** build in **Wisconsin** (~22% silage, good class balance, ~66 counties with real 2022 numbers). **California Central Valley** = transfer test (88% silage, double-cropping). Texas = "next steps". If BARC labels are in Maryland, build there first and use WI/CA as transfer.
- **Model:** XGBoost/LightGBM on per-field features. Model choice matters little; spend time on features, labels, the QC filter. Skip deep learning / Prithvi.
- **Accuracy:** county-level silage share vs NASS, plus field-level vs BARC labels (to be added). Hard share is the headline; soft share is reported beside it.
- **Experiment log:** a Google Sheet; `eval.score` prints a TSV row to paste.

## Signal and preprocessing plan
- **Clouds:** Sentinel-2 + **Cloud Score+** (`GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED`, use `cs_cdf` ≥ 0.6, *not* `cs`, which can mask real harvest changes). Per-field **median** over pixels; keep a date only if ≥ ~60% of the field is clear. Add Landsat/HLS for revisit. Gap-fill linearly (no heavy smoothing, which erases the harvest cliff). Sentinel-1 VH drop/coherence jump as a cloud-proof harvest timer. Record "harvest date ± N days" as a confidence feature.
- **Field geometry:** buffer polygons inward ~15 m (`buffer(-15)`); drop fields < ~1 ha after the buffer. `reduceRegions` per image; batch exports by county.
- **Climate/season variation:** never use calendar dates. Split each field's year into growth cycles; pick the **summer** (corn) cycle (handles CA double-crop: winter forage chopped in spring, then corn). Features are relative to the field's own cycle:
  - **NDVI just before the harvest drop** (anchor: silage high, grain low)
  - slope over the 2–4 weeks before harvest (cliff vs gradual)
  - days from peak to harvest
  - post-harvest residue (NDTI, B11/B12) within 2–3 weeks, unless the field regreens
  - optional growing-degree-days to harvest (gridMET `IDAHO_EPSCOR/GRIDMET`) as an "innovation" feature
- **Indices:** NDVI (+ EVI, GNDVI, highly correlated; ablate), NDMI (canopy water; silage is chopped at 65–70% moisture), NDTI (residue). **CAI needs narrow SWIR bands Sentinel-2/Landsat don't have**, so drop it unless another source exists. RGB is for slides only.
- **Distance to dairies** (state CAFO permit lists): strong prior. Run with and without it; "without" is the more convincing story.
- **Pitfalls:** snaplage/earlage looks like grain; fall tillage makes grain fields bare; drought speeds dry-down; random CV splits inflate results, so hold out by county/region (and by year/field ID for BARC).

## Eval harness (built, working on Keeboh)
Code: `eval/score.py`, `eval/from_keeboh.py`, `eval/fetch_nass.py`; tests in `tests/`. Branch `keeboh-truth` (not merged to `main` yet).
- Convert NASS: `python -m eval.from_keeboh /workspace/corn_grain_silage_acres.csv` → `data/truth/nass_{county,state}_{year}.csv`. It filters exact `CORN, GRAIN|SILAGE - ACRES HARVESTED`, `domain=TOTAL`, county=CENSUS only, state prefers SURVEY, drops "OTHER STATES"/county 998, and maps `(D)` to empty.
- Score: `python -m eval.score --run /workspace/runs/<name>-<what> --split /workspace/splits/wi_test.txt [--level state] [--max-cv 30]`.
- Run folder contract: `predictions.csv` (`field_id, county_fips(5-char str), state, year, acres, pred_label(silage|grain), p_silage, passed_qc`, **one year per run**) + `meta.json` (`who, region, train_years, train_counties (FIPS/state codes/"none"), indices, quality_filter, dairy_dist, model, notes`).
- Baseline = the most recent earlier truth year (2022 → **2017**). The leakage guard blocks a test county (or its state) in train_counties for the same year. Units with < 20 QC fields or withheld NASS are skipped and reported.
- **Smoke test result (random predictions, WI 2022):** hard MAE 31.1 pp vs **persistence baseline MAE 4.5 pp (r = 0.86)**. County shares barely changed 2017→2022, so beating persistence is a stretch goal. **Pitch:** timeliness (annual, right after harvest, vs a census every 5 years), catching counties that *changed*, field-level maps.

## Keeboh environment quirks
- **No git, no nano.** Update the repo by downloading the zip (use short lines, because long pasted lines wrap and get indented, causing a Python IndentationError):
  ```
  cd /workspace/J-Evaluation && rm -rf hack_the_harvest
  U=https://github.com/JishyFishy2006/hack_the_harvest
  U=$U/archive/refs/heads/keeboh-truth.zip
  python3 -c "import urllib.request as r,sys; r.urlretrieve(sys.argv[1],'h.zip')" $U
  python3 -m zipfile -e h.zip . && mv hack_the_harvest-keeboh-truth hack_the_harvest && rm h.zip
  python -m eval.from_keeboh /workspace/corn_grain_silage_acres.csv   # re-create truth files
  ```
  Re-downloading **wipes everything inside `hack_the_harvest/`**, so runs and splits live in `/workspace/runs` and `/workspace/splits`. Code changes made in Keeboh are lost on re-download; make lasting changes on GitHub.
- **Terminal vs notebook:** `%cd` and `!cmd` only work in notebook cells.
- **Secrets:** `/workspace/.env` (`NASS_API_KEY=...`), auto-loaded in terminals via `~/.bashrc` (`set -a; source /workspace/.env; set +a`). It's a **shared workspace**: teammates can read `.env` and use a logged-in Claude Code session. Never print keys or paste them in notebook cells.

## Open items / next steps
1. Inspect BARC labels (`field_counts`, columns, 3 rows, location, stable field ID) → add a **field-level mode** to the harness (balanced accuracy, silage F1, confusion matrix; split by year/spatial block, same field never on both sides).
2. Choose the **real WI test split** (≈⅓ of counties, spatially grouped). The current `wi_test.txt` is a smoke-test placeholder (every other county).
3. Add a "changed counties" metric (counties whose share moved > ~5 pp since the baseline year).
4. Check CA county coverage: `grep -c ',CA,' data/truth/nass_county_2022.csv`.
5. Merge `keeboh-truth` → `main`; create the experiment-log Sheet.
6. Rewrite `CLAUDE.md`'s Project section for the Python/notebook stack (logic in `.py`, notebooks thin).
7. Experiment order: WI NDVI rule → XGBoost → +NDMI/NDTI → +dairy distance → +EVI/GNDVI → CA transfer. Cut off new experiments around 3 a.m.; slides start right after planning (presentation = 40%).
