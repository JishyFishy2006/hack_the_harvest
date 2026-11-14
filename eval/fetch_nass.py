"""Download NASS Quick Stats corn silage/grain area harvested -> data/truth/nass_{level}_{year}.csv"""
import argparse
import os
import sys
from pathlib import Path

import pandas as pd
import requests

URL = "https://quickstats.nass.usda.gov/api/api_GET/"


def parse_years(s):
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def fetch(year, level, key, util):
    params = {
        "key": key, "source_desc": "SURVEY", "commodity_desc": "CORN",
        "statisticcat_desc": "AREA HARVESTED", "unit_desc": "ACRES",
        "util_practice_desc": util, "agg_level_desc": level.upper(),
        "domain_desc": "TOTAL", "year": year, "format": "JSON",
    }
    r = requests.get(URL, params=params, timeout=120)
    if r.status_code == 400:  # Quick Stats returns 400 when no records match (unpublished year)
        return []
    r.raise_for_status()
    return r.json().get("data", [])


def to_acres(v):
    # withheld codes like (D), (Z) -> NaN, never 0
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return float("nan")


def build(year, level, key):
    frames = []
    for util, col in (("SILAGE", "silage_acres"), ("GRAIN", "grain_acres")):
        rows = fetch(year, level, key, util)
        if not rows:
            return None
        df = pd.DataFrame(rows)
        out = pd.DataFrame({"state": df["state_alpha"], "year": year, col: df["Value"].map(to_acres)})
        keys = ["state", "year"]
        if level == "county":
            out["county_fips"] = df["state_fips_code"].str.zfill(2) + df["county_code"].str.zfill(3)
            # 998 = "other (combined) counties", not a real county
            out = out[(df["county_code"].str.strip() != "") & (df["county_code"] != "998")]
            keys = ["county_fips"] + keys
        frames.append(out.drop_duplicates(keys).set_index(keys))
    res = frames[0].join(frames[1], how="outer").reset_index()
    cols = (["county_fips"] if level == "county" else []) + ["state", "year", "silage_acres", "grain_acres"]
    return res[cols]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", required=True, help="e.g. 2019-2025 or 2024")
    ap.add_argument("--level", choices=["county", "state"], default="county")
    ap.add_argument("--out-dir", default="data/truth")
    a = ap.parse_args(argv)
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    key = os.environ.get("NASS_API_KEY")
    if not key:
        sys.exit("NASS_API_KEY not set (put it in .env or the environment)")
    Path(a.out_dir).mkdir(parents=True, exist_ok=True)
    for y in parse_years(a.years):
        df = build(y, a.level, key)
        if df is None or df.empty:
            print(f"WARNING: NASS has no {a.level} data for {y} yet; skipped", file=sys.stderr)
            continue
        p = Path(a.out_dir) / f"nass_{a.level}_{y}.csv"
        df.to_csv(p, index=False)
        print(f"wrote {p} ({len(df)} rows)")


if __name__ == "__main__":
    main()
