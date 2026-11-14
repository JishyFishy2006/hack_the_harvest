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
python -m eval.from_keeboh <keeboh.csv> [--out-dir data/truth]   # alternative: truth from a Keeboh NASS CSV
python -m eval.score --run runs/<run_id> --split splits/<name>.txt [--level county|state] [--truth-dir data/truth] [--max-cv 30]
```
Needs truth for the run's year and at least one earlier year; the persistence baseline uses the most recent earlier
year that has a truth file (`baseline_year`). Writes `runs/<run_id>/per_unit.csv` (with `silage_cv` when the truth
file has it) and prints a TSV row for the sheet.
Units with < 20 QC fields or withheld NASS values are skipped and counted, as are units with silage CV above
`--max-cv` ("high CV"; needs Keeboh-converted truth). Same-year + overlapping train county/state exits non-zero.

## Run on Keeboh
County truth is census-only (2012, 2017, 2022): score 2022 as the target, and the baseline is 2017. State truth exists every year.
```
!git clone https://github.com/JishyFishy2006/hack_the_harvest.git
%cd hack_the_harvest
!pip install -q -r requirements.txt
!python -m eval.from_keeboh /path/to/keeboh_nass.csv --out-dir data/truth
!python -m eval.score --run runs/<run_id> --split splits/<name>.txt --level county
```

## Example output row
```
run_id	who	time	region	train_years	train_counties	test_split	indices	quality_filter	dairy_dist	model	hard_MAE	hard_bias	soft_MAE	baseline_MAE	baseline_year	beats_baseline	n_units	n_skipped	coverage_pct	notes
r1	jishnu	2026-11-14 20:38	WI	2024	IA;55025	example	NDVI;NDMI	clear>=60%	False	xgboost	7.50	2.50	5.00	10.00	2023	True	2	2	98.48	first run
```
