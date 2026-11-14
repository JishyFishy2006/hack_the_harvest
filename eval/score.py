"""Score a run's silage-vs-grain predictions against NASS silage share. See eval/README.md."""
import argparse
import json
import math
from datetime import datetime
from pathlib import Path

import pandas as pd

MIN_FIELDS = 20
HEADER = ["run_id", "who", "time", "region", "train_years", "train_counties", "test_split", "indices",
          "quality_filter", "dairy_dist", "model", "hard_MAE", "hard_bias", "soft_MAE", "baseline_MAE",
          "beats_baseline", "n_units", "n_skipped", "coverage_pct", "notes"]


def read_split(path):
    lines = (ln.split("#")[0].strip() for ln in Path(path).read_text().splitlines())
    return [ln for ln in lines if ln]


def load_truth(truth_dir, level, year):
    p = Path(truth_dir) / f"nass_{level}_{year}.csv"
    if not p.exists():
        raise SystemExit(f"missing {p}; create it with: python -m eval.fetch_nass --years {year} --level {level}")
    df = pd.read_csv(p, dtype={"county_fips": str, "state": str})
    key = "county_fips" if level == "county" else "state"
    tot = df.silage_acres + df.grain_acres  # NaN if either withheld
    return pd.Series((df.silage_acres / tot).where(tot > 0).values, index=df[key].values)


def check_leakage(preds, meta, units, level):
    tc = meta.get("train_counties", "none")
    year = int(preds.year.iloc[0])
    if tc == "none" or year not in meta.get("train_years", []):
        return
    tc = set(tc)
    p = preds[preds[("county_fips" if level == "county" else "state")].isin(units)]
    hits = set()
    for u, st in p[["county_fips" if level == "county" else "state", "state"]].drop_duplicates().values:
        if u in tc or st in tc:
            hits.add(u)
    if hits:
        raise SystemExit(f"leakage: year {year} is a training year and test units overlap train_counties: "
                         f"{sorted(hits)}")


def stats(pred, true):
    err = (pred - true) * 100  # percentage points
    r = pred.corr(true) if len(pred) > 1 else float("nan")
    return {"MAE": err.abs().mean(), "bias": err.mean(), "std": err.std(), "r": r}


def score(run_dir, split_path, level="county", truth_dir="data/truth"):
    run_dir = Path(run_dir)
    preds = pd.read_csv(run_dir / "predictions.csv", dtype={"county_fips": str, "state": str})
    meta = json.loads((run_dir / "meta.json").read_text())
    if preds.year.nunique() != 1:
        raise SystemExit("predictions contain multiple years: split into one run per year")
    year = int(preds.year.iloc[0])
    split = read_split(split_path)
    ucol = "county_fips" if level == "county" else "state"
    check_leakage(preds, meta, set(split), level)
    truth, base = load_truth(truth_dir, level, year), load_truth(truth_dir, level, year - 1)

    preds = preds[preds[ucol].isin(split)].copy()
    preds["passed_qc"] = preds.passed_qc.astype(str).str.lower() == "true"
    total_acres = preds.acres.sum()
    qc = preds[preds.passed_qc].copy()
    coverage = 100 * qc.acres.sum() / total_acres if total_acres else float("nan")
    qc["silage_a"] = qc.acres.where(qc.pred_label == "silage", 0)
    qc["soft_a"] = qc.p_silage * qc.acres
    g = qc.groupby(ucol).agg(acres=("acres", "sum"), silage_a=("silage_a", "sum"), soft_a=("soft_a", "sum"),
                             n_fields=("acres", "size"))

    rows, skipped = [], {}
    for u in split:
        n = int(g.n_fields.get(u, 0))
        t, b = truth.get(u, math.nan), base.get(u, math.nan)
        if n < MIN_FIELDS:
            reason = f"<{MIN_FIELDS} QC fields"
        elif pd.isna(t) or pd.isna(b):
            reason = "NASS withheld/missing"
        else:
            reason = None
        if reason:
            skipped.setdefault(reason, []).append(u)
            continue
        r = g.loc[u]
        rows.append({"unit": u, "true_share": t, "hard_share": r.silage_a / r.acres,
                     "soft_share": r.soft_a / r.acres, "baseline_share": b, "n_fields": n, "qc_acres": r.acres})
    per_unit = pd.DataFrame(rows, columns=["unit", "true_share", "hard_share", "soft_share", "baseline_share",
                                           "n_fields", "qc_acres"])
    hard = stats(per_unit.hard_share, per_unit.true_share)
    soft = stats(per_unit.soft_share, per_unit.true_share)
    basel = stats(per_unit.baseline_share, per_unit.true_share)
    n_skipped = sum(len(v) for v in skipped.values())
    res = {"year": year, "hard": hard, "soft": soft, "baseline": basel, "n_units": len(per_unit),
           "n_skipped": n_skipped, "skipped": skipped, "coverage_pct": coverage,
           "beats_baseline": bool(hard["MAE"] < basel["MAE"]) if len(per_unit) else False}
    per_unit.to_csv(run_dir / "per_unit.csv", index=False)
    return res, per_unit, meta


def tsv_row(run_id, split_path, meta, res):
    j = lambda v: ";".join(map(str, v)) if isinstance(v, list) else str(v)
    f = lambda x: f"{x:.2f}"
    vals = [run_id, meta.get("who", ""), datetime.now().strftime("%Y-%m-%d %H:%M"), meta.get("region", ""),
            j(meta.get("train_years", [])), j(meta.get("train_counties", "none")), Path(split_path).stem,
            j(meta.get("indices", [])), meta.get("quality_filter", ""), meta.get("dairy_dist", ""),
            meta.get("model", ""), f(res["hard"]["MAE"]), f(res["hard"]["bias"]), f(res["soft"]["MAE"]),
            f(res["baseline"]["MAE"]), res["beats_baseline"], res["n_units"], res["n_skipped"],
            f(res["coverage_pct"]), str(meta.get("notes", "")).replace("\t", " ").replace("\n", " ")]
    return "\t".join(HEADER) + "\n" + "\t".join(map(str, vals))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--level", choices=["county", "state"], default="county")
    ap.add_argument("--truth-dir", default="data/truth")
    a = ap.parse_args(argv)
    res, _, meta = score(a.run, a.split, a.level, a.truth_dir)
    print(f"Run {Path(a.run).name}  year {res['year']}  level {a.level}  units scored {res['n_units']}")
    for name in ("hard", "soft", "baseline"):
        s = res[name]
        print(f"  {name:8s} MAE {s['MAE']:.2f}pp  bias {s['bias']:+.2f}pp  std {s['std']:.2f}pp  r {s['r']:.3f}")
    print(f"  coverage {res['coverage_pct']:.1f}%  beats persistence baseline: {res['beats_baseline']}")
    print(f"  skipped {res['n_skipped']}: " + ("; ".join(f"{k}: {v}" for k, v in res["skipped"].items()) or "none"))
    print("\nPaste into the sheet:")
    print(tsv_row(Path(a.run).name, a.split, meta, res))


if __name__ == "__main__":
    main()
