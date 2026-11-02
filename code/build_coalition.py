"""Build the coalition-change variable from DPI2020 (Coding_Protocol §2).

coalition_change = 1 in year t when the chief executive's party (DPI variable
execme, "Name of Executive Party") differs from the previous year; 0 otherwise.
The first observed year per country is an initial condition, not a change
(same convention as build_turnover.py). One-party states (PRK=KWP, CUB=PCC) are
correctly constant — zero coalition change, which is what the theory expects.

Coverage: DPI2020 covers 1975-2020 (ours used to 2019). 1960-1974 is empty for
ALL countries (documented limitation; filling via Nohlen handbooks is possible
but deferred). CHE is entirely missing in DPI (collective executive — same
problem as in Archigos, documented in docs/PHASE3_LOG.md). Romania is coded ROM
in DPI. Missing cells (-999) are left empty, never imputed.

Output: data_clean/coalition.csv (iso3, year, coalition_change, exec_party, source)
"""
import pandas as pd

OUT = "data_clean/coalition.csv"

spine = pd.read_csv("data_clean/panel_spine.csv")[["iso3", "year"]]
ours = pd.read_csv("data_clean/countries.csv")["iso3"].tolist()
dpi = pd.read_csv("data_raw/DPI2020.csv", low_memory=False)

dpi["iso3"] = dpi["ifs"].replace({"ROM": "ROU"})
dpi = dpi[dpi["iso3"].isin(ours) & (dpi["year"] >= 1975) & (dpi["year"] <= 2019)]
dpi["exec_party"] = dpi["execme"].astype(str).replace({"-999": None, "nan": None})
dpi = dpi[["iso3", "year", "exec_party"]].sort_values(["iso3", "year"])

dpi["prev"] = dpi.groupby("iso3")["exec_party"].shift(1)
dpi["coalition_change"] = (
    dpi["exec_party"].notna() & dpi["prev"].notna() & (dpi["exec_party"] != dpi["prev"])
).astype(int)
dpi["source"] = "dpi2020"

out = spine.merge(dpi[["iso3", "year", "coalition_change", "exec_party", "source"]],
                  on=["iso3", "year"], how="left")
out.to_csv(OUT, index=False)

ev = out[out["coalition_change"] == 1]
print(f"coalition changes coded: {len(ev)} across {ev['iso3'].nunique()} countries (1975-2019)")
zero = [c for c in ours
        if out[(out['iso3'] == c) & out['exec_party'].notna()]['coalition_change'].sum() == 0]
print(f"countries with zero coalition change (one-party states expected here): {sorted(zero)}")
no_data = [c for c in ours if out[(out['iso3'] == c)]['exec_party'].notna().sum() == 0]
print(f"countries with no DPI party data at all: {no_data}")
print("\nspot checks:")
for iso in ["VEN", "KOR", "GRC", "CUB", "PRK"]:
    sub = out[(out.iso3 == iso) & (out.coalition_change == 1)]
    print(f"  {iso}: {sub['year'].tolist()}")
