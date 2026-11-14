# Evaluation harness

Scores silage-vs-grain predictions against USDA NASS county (or state) silage share
(`silage_acres / (silage_acres + grain_acres)`, corn area harvested). One run = one year.

## Schemas
`runs/<run_id>/predictions.csv` (one row per field):
`field_id:str, county_fips:str(5), state:str(2), year:int, acres:float, pred_label:"silage"|"grain", p_silage:float[0,1], passed_qc:bool`

`runs/<run_id>/meta.json`: `who, region, train_years[], train_counties[] ("none" or 5-char FIPS / 2-letter states), indices[], quality_filter, dairy_dist, model, notes`

`splits/<name>.txt`: one unit per line (county FIPS, or state codes for `--level state`); blank lines and `#` ignored.

## Commands
```
pip install -r requirements.txt            # NASS_API_KEY in .env or environment
python -m eval.fetch_nass --years 2019-2025 --level county   # also: --level state
python -m eval.score --run runs/<run_id> --split splits/<name>.txt [--level county|state] [--truth-dir data/truth]
```
Needs truth for the run's year and year-1. Writes `runs/<run_id>/per_unit.csv` and prints a TSV row for the sheet.
Units with < 20 QC fields or withheld NASS values are skipped and counted. Same-year + overlapping train county/state exits non-zero.

## Example output row
```
run_id	who	time	region	train_years	train_counties	test_split	indices	quality_filter	dairy_dist	model	hard_MAE	hard_bias	soft_MAE	baseline_MAE	beats_baseline	n_units	n_skipped	coverage_pct	notes
r1	jishnu	2026-11-14 20:38	WI	2024	IA;55025	example	NDVI;NDMI	clear>=60%	False	xgboost	7.50	2.50	5.00	10.00	True	2	2	98.48	first run
```
