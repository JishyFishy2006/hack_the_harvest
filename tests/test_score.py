import json

import pandas as pd
import pytest

from eval.score import score


def make(tmp_path, meta_extra=None, years=(2024,), nfields=None):
    # A(55001): 20 fields x 10ac, 5 silage (p=.9) 15 grain (p=.1) -> hard .25, soft .3
    # B(55002): 20 fields x 10ac, 10 silage (p=1) 10 grain (p=0)   -> hard .5,  soft .5
    # C(55003): 5 fields only -> skipped (<20); D(19001): withheld in NASS -> skipped
    nfields = nfields or {"55001": (5, 15), "55002": (10, 10), "55003": (2, 3), "19001": (10, 10)}
    ps = {"55001": (0.9, 0.1), "55002": (1.0, 0.0), "55003": (1.0, 0.0), "19001": (1.0, 0.0)}
    rows = []
    for fips, (ns, ng) in nfields.items():
        for i in range(ns + ng):
            sil = i < ns
            rows.append({"field_id": f"{fips}-{i}", "county_fips": fips, "state": "WI" if fips[:2] == "55" else "IA",
                         "year": years[0], "acres": 10.0, "pred_label": "silage" if sil else "grain",
                         "p_silage": ps[fips][0] if sil else ps[fips][1], "passed_qc": True})
    rows.append({"field_id": "x", "county_fips": "55001", "state": "WI", "year": years[0], "acres": 10.0,
                 "pred_label": "silage", "p_silage": 1.0, "passed_qc": False})  # excluded by QC
    if len(years) > 1:
        rows.append({**rows[0], "year": years[1]})
    run = tmp_path / "runs" / "r1"
    run.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(run / "predictions.csv", index=False)
    meta = {"who": "t", "train_years": [2023], "train_counties": "none", **(meta_extra or {})}
    (run / "meta.json").write_text(json.dumps(meta))
    td = tmp_path / "truth"
    td.mkdir()
    nan = float("nan")
    for y, vals in ((2024, {"55001": (30, 70), "55002": (40, 60), "55003": (50, 50), "19001": (nan, 100)}),
                    (2023, {"55001": (20, 80), "55002": (50, 50), "55003": (50, 50), "19001": (10, 90)})):
        pd.DataFrame([{"county_fips": k, "state": "WI", "year": y, "silage_acres": s, "grain_acres": g}
                      for k, (s, g) in vals.items()]).to_csv(td / f"nass_county_{y}.csv", index=False)
    split = tmp_path / "split.txt"
    split.write_text("# c\n55001\n55002\n55003\n19001\n\n")
    return run, split, td


def test_math_skips_and_baseline(tmp_path):
    run, split, td = make(tmp_path)
    res, pu, _ = score(run, split, "county", td)
    assert res["n_units"] == 2 and res["n_skipped"] == 2
    assert set(res["skipped"]) == {"<20 QC fields", "NASS withheld/missing"}
    p = pu.set_index("unit")
    assert p.hard_share["55001"] == pytest.approx(0.25) and p.soft_share["55001"] == pytest.approx(0.3)
    assert p.hard_share["55002"] == pytest.approx(0.5) and p.true_share["55002"] == pytest.approx(0.4)
    assert res["hard"]["MAE"] == pytest.approx((5 + 10) / 2)  # |.25-.3|, |.5-.4| in pp
    assert res["hard"]["bias"] == pytest.approx((-5 + 10) / 2)
    assert res["soft"]["MAE"] == pytest.approx(5.0)  # soft errors 0 and 10
    assert res["baseline"]["MAE"] == pytest.approx((10 + 10) / 2)  # .2 vs .3, .5 vs .4
    assert res["beats_baseline"] is True
    assert res["coverage_pct"] == pytest.approx(100 * 650 / 660)  # 65 QC fields x 10ac, plus one non-QC field


def test_leakage(tmp_path):
    run, split, td = make(tmp_path, {"train_years": [2024], "train_counties": ["WI"]})
    with pytest.raises(SystemExit, match="leakage"):
        score(run, split, "county", td)


def test_no_leakage_other_year(tmp_path):
    run, split, td = make(tmp_path, {"train_years": [2023], "train_counties": ["WI"]})
    assert score(run, split, "county", td)[0]["n_units"] == 2


def test_multi_year(tmp_path):
    run, split, td = make(tmp_path, years=(2024, 2023))
    with pytest.raises(SystemExit, match="one run per year"):
        score(run, split, "county", td)
