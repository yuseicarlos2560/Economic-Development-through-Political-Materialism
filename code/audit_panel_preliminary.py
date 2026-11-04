"""Audit the preliminary Step 5 panel against its source tables and coding rules."""
import sys
import pandas as pd

FAILS = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILS.append(name)


def compare_source(panel, source, mapping, label):
    panel_part = panel[["iso3", "year"] + list(mapping.values())].rename(
        columns={column: f"{column}_panel" for column in mapping.values()})
    source_part = source[["iso3", "year"] + list(mapping.keys())].rename(
        columns={column: f"{column}_source" for column in mapping.keys()})
    merged = panel_part.merge(source_part, on=["iso3", "year"], how="left", validate="one_to_one")
    for source_column, panel_column in mapping.items():
        left = merged[f"{panel_column}_panel"]
        right = merged[f"{source_column}_source"]
        equal = ((left == right) | (left.isna() & right.isna())).all()
        check(f"{label}: {panel_column} matches {source_column}", equal)


def event_keys(events, year_column, mask):
    selected = events[mask]
    return set(zip(selected["iso3"], selected[year_column]))


def observed_keys(panel, column):
    selected = panel[panel[column] == 1]
    return set(zip(selected["iso3"], selected["year"]))


panel = pd.read_csv("data_clean/panel_preliminary.csv")
spine = pd.read_csv("data_clean/panel_spine.csv")
check("A1 full spine and source order", panel[["iso3", "country", "region", "year"]].equals(
    spine[["iso3", "country", "region", "year"]]), f"{len(panel)} rows")
check("A2 unique country-years", not panel.duplicated(["iso3", "year"]).any())
check("A3 73 countries and 1945-2019", panel["iso3"].nunique() == 73
      and panel["year"].min() == 1945 and panel["year"].max() == 2019)
check("A4 every country has 75 years", (panel.groupby("iso3")["year"].nunique() == 75).all())

outcomes = pd.read_csv("data_clean/outcomes.csv")
compare_source(panel, outcomes, {
    "growth_pc": "gdp_pc_growth", "growth_source": "gdp_pc_growth_source",
    "gdppc": "gdp_pc_const", "gdppc_source": "gdp_pc_source",
    "inflation": "inflation_annual", "infl_source": "inflation_source", "seam": "gdp_pc_seam",
}, "B outcomes")
controls = pd.read_csv("data_clean/controls_preliminary.csv")
compare_source(panel, controls, {
    "oil_rents_pct_gdp": "oil_rents_pct_gdp", "population": "population",
    "investment_pct_gdp": "investment_pct_gdp",
}, "B controls")

turnover = pd.read_csv("data_clean/turnover.csv")
compare_source(panel, turnover, {
    "turnover": "turnover", "leader_in": "leader_in", "irregular_exit": "irregular_exit",
    "source": "turnover_source",
}, "C turnover")
post = (panel["year"] >= 2016) & (panel["iso3"] != "CHE")
check("C2 all non-Swiss post-2015 turnover rows flagged unverified",
      (panel.loc[post, "turnover_evidence_status"] == "hand_unverified").all()
      and (panel.loc[~post & (panel["year"] >= 2016), "turnover_evidence_status"] ==
           "excluded_collective_executive").all())

coalition = pd.read_csv("data_clean/coalition.csv")
compare_source(panel, coalition, {
    "coalition_change": "coalition_change", "exec_party": "exec_party", "source": "coalition_source",
}, "D coalition")

for variable, path in [
    ("regime_change", "data_clean/regime_change.csv"),
    ("power_structure", "data_clean/power_structure.csv"),
    ("apparatus_restructuring", "data_clean/apparatus_restructuring.csv"),
]:
    source = pd.read_csv(path)
    mapping = {variable: variable, "evidence_status": f"{variable}_evidence_status"}
    if "episode_id" in source:
        mapping["episode_id"] = f"{variable}_episode_id"
    compare_source(panel, source, mapping, f"E {variable}")
check("E4 domestic missingness preserved", panel["regime_change"].isna().sum() == 996
      and panel["power_structure"].isna().sum() == 1
      and panel["apparatus_restructuring"].isna().sum() == 1)
check("E5 conditional France 1988 remains missing", panel.loc[
    (panel["iso3"] == "FRA") & (panel["year"] == 1988), "power_structure"].isna().all())
check("E6 conditional Guyana 1980 remains missing", panel.loc[
    (panel["iso3"] == "GUY") & (panel["year"] == 1980), "apparatus_restructuring"].isna().all())

events = pd.read_csv("data_clean/realignment_event_codings_preliminary.csv")
coded = events[events["in_panel"]]
check("F1 only Egypt and Yugoslavia excluded as calibration-only",
      set(events.loc[~events["in_panel"], "iso3"]) == {"EGY", "YUG"})
check("F2 all 70 panel episodes represented", len(coded) == 70)
check("F3 midpoint lies inside every interval", ((coded["start_year"] <= coded["midpoint_year"])
      & (coded["midpoint_year"] <= coded["end_year"])).all())

for rule, year_column in [("start", "start_year"), ("midpoint", "midpoint_year"), ("end", "end_year")]:
    suffix = "" if rule == "start" else f"_{rule}"
    specifications = [
        (f"severance{suffix}", coded["type"] == "severance"),
        (f"entry{suffix}", coded["type"] == "entry"),
        (f"entry_richer{suffix}", (coded["type"] == "entry") & (coded["richer_sphere"] == True)),
        (f"imposed_severance{suffix}", (coded["type"] == "severance")
         & (coded["voluntariness_base"] == "imposed")),
    ]
    for column, mask in specifications:
        check(f"F4 {column} matches episode {rule} dates",
              observed_keys(panel, column) == event_keys(coded, year_column, mask))
check("F5 threats use start dates and never enter severance",
      observed_keys(panel, "severance_threat") == event_keys(
          coded, "start_year", coded["type"] == "severance_threat")
      and not ((panel["severance_threat"] == 1) & (panel["severance"] == 1)).any())

panel_entries = coded[coded["type"] == "entry"]
check("G1 R5 known for every panel entry", panel_entries["richer_sphere"].notna().all())
check("G2 R5 values match patron/median comparison", (panel_entries["richer_sphere"] ==
      (panel_entries["r5_patron_gdppc"] > panel_entries["r5_region_median_gdppc"])).all())
check("G3 seven poorer Soviet formation entries excluded from richer-entry H2 subset",
      (panel_entries["richer_sphere"] == False).sum() == 7
      and (panel["entry_richer"] == 1).sum() == 38)

for (iso3, year), group in coded[coded["type"].isin(["entry", "severance"])].groupby(["iso3", "start_year"]):
    row = panel[(panel["iso3"] == iso3) & (panel["year"] == year)]
    if len(row) != 1:
        check(f"H1 metadata unique {iso3} {year}", False)
        continue
    row = row.iloc[0]
    check(f"H1 episode IDs {iso3} {year}", row["realignment_episode_ids"] == ";".join(group["episode_id"]))
    check(f"H2 systemic flag {iso3} {year}", row["systemic_shift_flag"] ==
          int((group["systemic_shift_flag"] == 1).any()))

cuba = panel[(panel["iso3"] == "CUB") & (panel["year"] == 1960)].iloc[0]
check("H3 paired Cuba 1960 severance and entry remain separate",
      cuba["severance"] == 1 and cuba["entry_richer"] == 1
      and set(cuba["patron"].split(";")) == {"USA", "USSR"})
ven = panel[panel["iso3"] == "VEN"].set_index("year")
check("H4 Venezuela interval variants retained", ven.loc[2002, "severance"] == 1
      and ven.loc[2009, "severance_midpoint"] == 1 and ven.loc[2017, "severance_end"] == 1)
grc = panel[(panel["iso3"] == "GRC") & (panel["year"] == 2015)].iloc[0]
check("H5 Greece 2015 threat is not severance", grc["severance_threat"] == 1 and grc["severance"] == 0)

annual_disruption = pd.read_csv("data_clean/disruption_years_preliminary.csv")
compare_source(panel, annual_disruption, {
    "disruption": "disruption", "episode_id": "disruption_episode_id", "rules": "disruption_rules",
}, "I annual disruption")
check("I2 annual disruption union count", (panel["disruption"] == 1).sum() == 572)
expected_acceleration = set()
for _, episode in pd.read_csv("data_clean/acceleration_episodes.csv").iterrows():
    expected_acceleration.update((episode["iso3"], year) for year in
                                 range(episode["start_year"], episode["end_year"] + 1))
check("I3 acceleration country-years match continuous episodes",
      observed_keys(panel, "acceleration") == expected_acceleration
      and (panel["acceleration"] == 1).sum() == 788)
for label, frame in [
    ("panel", panel), ("controls", controls), ("event codings", events),
    ("annual disruption", annual_disruption),
]:
    check(f"J1 {label} explicitly preliminary", "analysis_status" in frame
          and frame["analysis_status"].eq("preliminary").all())

print()
print(f"FAILS: {len(FAILS)}")
print("Preliminary status: open Step 3/4 judgments and post-2015 turnover verification remain unresolved.")
sys.exit(1 if FAILS else 0)
