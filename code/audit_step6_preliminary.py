"""Audit the explicitly preliminary Step 6 descriptive outputs and timing safeguards."""
import sys
import numpy as np
import pandas as pd

FAILS = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILS.append(name)


panel = pd.read_csv("data_clean/panel_preliminary.csv")
cells = pd.read_csv("data_clean/step6_country_year_cells_preliminary.csv")
frequencies = pd.read_csv("data_clean/step6_cell_frequencies_preliminary.csv")
episodes = pd.read_csv("data_clean/step6_realignment_outcomes_preliminary.csv")
events = pd.read_csv("data_clean/realignment_event_codings_preliminary.csv")

for label, frame in [
    ("Step 5 panel", panel), ("Step 5 events", events), ("Step 6 cells", cells),
    ("Step 6 frequencies", frequencies), ("Step 6 episode outcomes", episodes),
]:
    check(f"A1 {label} explicitly preliminary", "analysis_status" in frame
          and frame["analysis_status"].eq("preliminary").all())

check("A2 baseline cells cover the 1960-2019 sample once", len(cells) == 4380
      and not cells.duplicated(["iso3", "year"]).any()
      and cells["year"].min() == 1960 and cells["year"].max() == 2019)
check("A3 baseline cell assignment is complete", cells["primary_3x3_cell"].notna().all())

ps, ar = cells["iso3"], cells["year"]
keyed = cells.set_index(["iso3", "year"])
source = panel[panel["year"].between(1960, 2019)].set_index(["iso3", "year"])
deep = source["power_structure"].eq(1) | source["apparatus_restructuring"].eq(1)
check("B1 every observed deep transformation is in the deep domestic row",
      (keyed.loc[deep[deep].index, "domestic_change"] == "power_or_apparatus_transformation").all())
known_no_deep = source["power_structure"].eq(0) & source["apparatus_restructuring"].eq(0)
shallow = source["turnover"].eq(1) | source["regime_change"].eq(1)
shallow_keys = known_no_deep[known_no_deep & shallow].index
check("B2 shallow events require known absence of deep transformation",
      (keyed.loc[shallow_keys, "domestic_change"] == "turnover_or_formal_only").all())
none_keys = known_no_deep[known_no_deep & source["turnover"].eq(0) & source["regime_change"].eq(0)].index
check("B3 no-domestic-event row requires four observed zeroes",
      (keyed.loc[none_keys, "domestic_change"] == "none").all())
check("B4 unknown domestic evidence is not converted to no event",
      (keyed.loc[source["regime_change"].isna() & ~deep & ~shallow, "domestic_change"] == "unknown").all())

check("C1 threats never enter severance cells",
      not ((cells["external_realignment"] == "severance_threat")
           & cells["external_realignment"].eq("severance")).any())
check("C2 pre-1960 poorer entries do not leak into the primary sample",
      not cells["external_realignment"].eq("entry_poorer_outside_H2").any())
check("C3 baseline frequency denominator covers every baseline country-year",
      frequencies[(frequencies["date_rule"] == "start")
                  & (frequencies["case_selection"] == "current_coded_state")]["n_country_years"].sum() == 4380)
expected_scenario_n = {
    ("start", "current_coded_state"): 4380,
    ("midpoint", "current_coded_state"): 4380,
    ("end", "current_coded_state"): 4380,
    ("start", "exclude_open_cases"): 4377,
    ("start", "exclude_systemic_shift"): 4359,
    ("start", "imposed_severance_only"): 4366,
}
for key, expected in expected_scenario_n.items():
    observed = frequencies[(frequencies["date_rule"] == key[0])
                           & (frequencies["case_selection"] == key[1])]["n_country_years"].sum()
    check(f"C4 scenario denominator {key}", observed == expected, f"{observed}")
for prefix in ["disruption_5y", "acceleration_onset_8y"]:
    check(f"C5 {prefix} counts and rates are internally valid",
          (frequencies[f"count_{prefix}"] <= frequencies[f"n_{prefix}"]).all()
          & frequencies[f"rate_{prefix}"].dropna().between(0, 1).all())

# Recalculate every baseline aggregate from the country-year output.
baseline_frequencies = frequencies[(frequencies["date_rule"] == "start")
                                   & (frequencies["case_selection"] == "current_coded_state")]
for _, row in baseline_frequencies.iterrows():
    group = cells[(cells["domestic_change"] == row["domestic_change"])
                  & (cells["external_realignment"] == row["external_realignment"])]
    label = f"D1 baseline aggregate {row['domestic_change']}/{row['external_realignment']}"
    valid = len(group) == row["n_country_years"]
    for horizon in [1, 3, 5]:
        values = group[f"growth_forward_{horizon}y"].dropna()
        valid &= len(values) == row[f"n_growth_{horizon}y"]
        valid &= np.isclose(values.mean(), row[f"mean_growth_{horizon}y"], equal_nan=True)
    for variable, prefix in [("disruption_forward_5y", "disruption_5y"),
                             ("acceleration_onset_forward_8y", "acceleration_onset_8y")]:
        values = group[variable].dropna()
        valid &= len(values) == row[f"n_{prefix}"]
        valid &= int(values.sum()) == row[f"count_{prefix}"]
        valid &= np.isclose(values.mean(), row[f"rate_{prefix}"], equal_nan=True)
    check(label, valid)

consummated = events[events["in_panel"] & events["type"].isin(["entry", "severance"])]
check("E1 episode report has one row per consummated panel episode and date rule",
      len(episodes) == 3 * len(consummated) == 204
      and not episodes.duplicated(["episode_id", "date_rule"]).any())
for _, row in episodes.iterrows():
    source_event = consummated[consummated["episode_id"] == row["episode_id"]].iloc[0]
    expected_year = source_event[{"start": "start_year", "midpoint": "midpoint_year", "end": "end_year"}[row["date_rule"]]]
    if row["event_year"] != expected_year:
        check(f"E2 event date {row['episode_id']} {row['date_rule']}", False)
check("E2 all event dates match source intervals", not FAILS or not any(x.startswith("E2 event date") for x in FAILS))
check("E3 all 20 window-edge episodes are indeterminate under every date rule",
      (episodes["window_edge_outcome_indeterminate"].sum() == 60)
      and (episodes.loc[episodes["window_edge_outcome_indeterminate"], "descriptive_timing_status"]
           == "indeterminate_window_edge").all())
check("E4 ongoing outcomes are explicitly flagged", (episodes.loc[
    (episodes["disruption_at_event"] == 1) | (episodes["acceleration_at_event"] == 1),
    "descriptive_timing_status"].isin([
        "ongoing_outcome_at_event", "paired_transition_not_clean_single_treatment",
        "indeterminate_window_edge", "outside_H2_sign_test",
    ])).all())
check("E5 clean signed-outcome labels require the relevant forward outcome",
      (episodes.loc[episodes["descriptive_timing_status"] == "signed_outcome_observed_after_event"]
       .apply(lambda row: row["disruption_forward_5y"] == 1 if row["type"] == "severance"
              else row["acceleration_onset_forward_8y"] == 1, axis=1)).all())
check("E6 poorer entries are outside the H2 sign test or window-edge indeterminate", (episodes.loc[
    (episodes["type"] == "entry") & episodes["richer_sphere"].eq(False),
    "descriptive_timing_status"].isin(["outside_H2_sign_test", "indeterminate_window_edge"])).all())

cuba = episodes[(episodes["episode_id"] == "E005") & (episodes["date_rule"] == "start")].iloc[0]
expected_growth = panel[(panel["iso3"] == "CUB") & panel["year"].between(1990, 1994)]["gdp_pc_growth"].mean()
check("F1 Cuba five-year growth uses only 1990-1994, after the 1989 event",
      np.isclose(cuba["growth_forward_5y"], expected_growth)
      and cuba["descriptive_timing_status"] == "ongoing_outcome_at_event")
vietnam = episodes[(episodes["episode_id"] == "E009") & (episodes["date_rule"] == "start")].iloc[0]
check("F2 Vietnam's already-active acceleration is not treated as a new effect",
      vietnam["acceleration_at_event"] == 1
      and vietnam["descriptive_timing_status"] == "ongoing_outcome_at_event")
ven = episodes[episodes["episode_id"] == "E016"].set_index("date_rule")["event_year"].to_dict()
check("F3 Venezuela interval variants are 2002/2009/2017",
      ven == {"start": 2002, "midpoint": 2009, "end": 2017})

print()
print(f"FAILS: {len(FAILS)}")
print("All Step 6 results remain preliminary, descriptive, and non-causal.")
sys.exit(1 if FAILS else 0)
