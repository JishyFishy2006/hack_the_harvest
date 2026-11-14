import pandas as pd

from eval.from_keeboh import convert

HEAD = ("year,aggregation_level,state_name,state_ansi,county_name,county_ansi,commodity,crop_use,measurement,"
        "statistic,unit,value,cv_percent,source,domain,domain_category,reference_period,frequency,short_description")


def row(level, county_ansi, crop, value, cv, source, desc=None, year=2022, state="ALABAMA", ansi="1"):
    desc = desc or f"CORN, {crop.upper()} - ACRES HARVESTED"
    return (f'{year},{level},{state},{ansi},AUTAUGA,{county_ansi},CORN,{crop},harvested,AREA HARVESTED,ACRES,'
            f'"{value}",{cv},{source},TOTAL,NOT SPECIFIED,YEAR,ANNUAL,"{desc}"')


def test_convert(tmp_path):
    rows = [
        row("COUNTY", "1", "grain", "1,525", "19.6", "CENSUS"),
        row("COUNTY", "1", "silage", "(D)", "(D)", "CENSUS"),
        row("COUNTY", "1", "grain", "9999", "", "SURVEY"),  # survey county row duplicating census: ignored
        row("COUNTY", "1", "grain", "77", "", "CENSUS", desc="CORN, GRAIN, IRRIGATED - ACRES HARVESTED"),
        row("COUNTY", "998", "grain", "500", "", "CENSUS"),  # "other counties": dropped
        row("STATE", "", "grain", "100", "", "CENSUS"),
        row("STATE", "", "grain", "200", "", "SURVEY"),
        row("STATE", "", "silage", "30", "", "CENSUS"),  # no survey row -> census fallback
        row("STATE", "", "grain", "1000", "", "SURVEY", year=2021, state="WISCONSIN", ansi="55"),
    ]
    src = tmp_path / "k.csv"
    src.write_text(HEAD + "\n" + "\n".join(rows) + "\n")
    convert(src, tmp_path)

    c = pd.read_csv(tmp_path / "nass_county_2022.csv", dtype={"county_fips": str})
    assert list(c.columns) == ["county_fips", "state", "year", "silage_acres", "grain_acres", "silage_cv", "grain_cv"]
    assert len(c) == 1 and c.county_fips[0] == "01001" and c.state[0] == "AL"
    assert c.grain_acres[0] == 1525 and c.grain_cv[0] == 19.6
    assert pd.isna(c.silage_acres[0]) and pd.isna(c.silage_cv[0])  # (D) -> empty, never 0

    s = pd.read_csv(tmp_path / "nass_state_2022.csv").iloc[0]
    assert (s.state, s.grain_acres, s.silage_acres) == ("AL", 200, 30)  # survey wins, not 300
    s21 = pd.read_csv(tmp_path / "nass_state_2021.csv").iloc[0]
    assert s21.state == "WI" and s21.grain_acres == 1000 and pd.isna(s21.silage_acres)
    assert not (tmp_path / "nass_county_2021.csv").exists()
