"""Convert a Keeboh NASS CSV -> data/truth/nass_{level}_{year}.csv (plus silage_cv, grain_cv). See eval/README.md."""
import argparse
from pathlib import Path

import pandas as pd

from eval.fetch_nass import to_acres

CROPS = {"CORN, GRAIN - ACRES HARVESTED": "grain", "CORN, SILAGE - ACRES HARVESTED": "silage"}
COLS = ["silage_acres", "grain_acres", "silage_cv", "grain_cv"]
STATES = {
    "ALABAMA": "AL", "ALASKA": "AK", "ARIZONA": "AZ", "ARKANSAS": "AR", "CALIFORNIA": "CA", "COLORADO": "CO",
    "CONNECTICUT": "CT", "DELAWARE": "DE", "FLORIDA": "FL", "GEORGIA": "GA", "HAWAII": "HI", "IDAHO": "ID",
    "ILLINOIS": "IL", "INDIANA": "IN", "IOWA": "IA", "KANSAS": "KS", "KENTUCKY": "KY", "LOUISIANA": "LA",
    "MAINE": "ME", "MARYLAND": "MD", "MASSACHUSETTS": "MA", "MICHIGAN": "MI", "MINNESOTA": "MN",
    "MISSISSIPPI": "MS", "MISSOURI": "MO", "MONTANA": "MT", "NEBRASKA": "NE", "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH", "NEW JERSEY": "NJ", "NEW MEXICO": "NM", "NEW YORK": "NY", "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND", "OHIO": "OH", "OKLAHOMA": "OK", "OREGON": "OR", "PENNSYLVANIA": "PA",
    "RHODE ISLAND": "RI", "SOUTH CAROLINA": "SC", "SOUTH DAKOTA": "SD", "TENNESSEE": "TN", "TEXAS": "TX",
    "UTAH": "UT", "VERMONT": "VT", "VIRGINIA": "VA", "WASHINGTON": "WA", "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI", "WYOMING": "WY",
}


def convert(src, out_dir="data/truth"):
    df = pd.read_csv(src, dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()
    df = df.apply(lambda c: c.str.strip())
    df = df[df.short_description.isin(CROPS) & (df.domain == "TOTAL") & (df.unit == "ACRES")
            & df.aggregation_level.isin(["COUNTY", "STATE"])].copy()
    df["crop"] = df.short_description.map(CROPS)
    df["value"] = df.value.map(to_acres)  # (D), (Z), (NA) -> NaN, commas stripped
    df["cv"] = df.cv_percent.map(to_acres)
    df["year"] = df.year.astype(int)
    df["state"] = df.state_name.str.upper().map(STATES)
    bad = sorted(set(df.state_name[df.state.isna()]))
    if bad:
        raise SystemExit(f"unknown state_name values: {bad}")

    county = df[(df.aggregation_level == "COUNTY") & (df.source == "CENSUS")
                & ~df.county_ansi.isin(["", "998"])].copy()  # 998 = "other (combined) counties"
    county["county_fips"] = county.state_ansi.str.zfill(2) + county.county_ansi.str.zfill(3)
    state = df[(df.aggregation_level == "STATE") & df.source.isin(["SURVEY", "CENSUS"])].copy()
    # SURVEY wins over CENSUS (never summed); annual figure wins over any forecast rows
    state["rank_src"], state["rank_ref"] = state.source != "SURVEY", state.reference_period != "YEAR"
    state = state.sort_values(["rank_src", "rank_ref"], kind="stable")

    Path(out_dir).mkdir(parents=True, exist_ok=True)
    written = []
    for level, d, keys in (("county", county, ["county_fips", "state", "year"]), ("state", state, ["state", "year"])):
        if d.empty:
            continue
        d = d.drop_duplicates(keys + ["crop"])
        wide = d.pivot(index=keys, columns="crop", values=["value", "cv"])
        wide.columns = [f"{c}_{'acres' if v == 'value' else 'cv'}" for v, c in wide.columns]
        wide = wide.reindex(columns=COLS).reset_index()
        for y, g in wide.groupby("year"):
            p = Path(out_dir) / f"nass_{level}_{y}.csv"
            g.to_csv(p, index=False)
            wh = d[(d.year == y) & d.value.isna()].crop.value_counts()
            print(f"wrote {p} ({len(g)} rows; withheld silage {wh.get('silage', 0)}, grain {wh.get('grain', 0)})")
            written.append(p)
    return written


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="Keeboh NASS CSV")
    ap.add_argument("--out-dir", default="data/truth")
    a = ap.parse_args(argv)
    convert(a.src, a.out_dir)


if __name__ == "__main__":
    main()
