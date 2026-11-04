"""Run the explicitly preliminary, model-free Step 6 descriptive analysis.

Primary sample: 1960-2019. Domestic rows distinguish deep transformation, shallow
turnover/formal change, no observed domestic event, and unknown evidence. External
columns distinguish severance, richer entry, no realignment, paired transitions,
poorer entries, and threats. Outcomes follow year t: growth means use complete
1/3/5-year forward windows, disruption uses annual flags in t+1..t+5, and
acceleration uses episode onsets in t+1..t+8. Ongoing outcomes are not presented
as new effects. Start/midpoint/end dates and registered case exclusions are reported
without resolving the underlying open issues.
"""
import numpy as np
import pandas as pd

PANEL_PATH = "data_clean/panel_preliminary.csv"
EVENTS_PATH = "data_clean/realignment_event_codings_preliminary.csv"
CELLS_OUT = "data_clean/step6_country_year_cells_preliminary.csv"
FREQUENCIES_OUT = "data_clean/step6_cell_frequencies_preliminary.csv"
EPISODES_OUT = "data_clean/step6_realignment_outcomes_preliminary.csv"

panel = pd.read_csv(PANEL_PATH)
events = pd.read_csv(EVENTS_PATH)
events = events[events["in_panel"]].copy()
acceleration_onsets = set(zip(
    pd.read_csv("data_clean/acceleration_episodes.csv")["iso3"],
    pd.read_csv("data_clean/acceleration_episodes.csv")["start_year"],
))


def domestic_category(frame):
    ps, ar = frame["power_structure"], frame["apparatus_restructuring"]
    turnover, regime = frame["turnover"], frame["regime_change"]
    deep = ps.eq(1) | ar.eq(1)
    deep_absent_known = ps.eq(0) & ar.eq(0)
    shallow = turnover.eq(1) | regime.eq(1)
    result = pd.Series("unknown", index=frame.index, dtype="object")
    result.loc[deep_absent_known & shallow] = "turnover_or_formal_only"
    result.loc[deep_absent_known & turnover.eq(0) & regime.eq(0)] = "none"
    result.loc[deep] = "power_or_apparatus_transformation"
    return result


def external_category(frame, date_rule):
    suffix = "" if date_rule == "start" else f"_{date_rule}"
    severance = frame[f"severance{suffix}"].eq(1)
    entry = frame[f"entry{suffix}"].eq(1)
    richer_entry = frame[f"entry_richer{suffix}"].eq(1)
    threat = frame["severance_threat"].eq(1)
    result = pd.Series("none", index=frame.index, dtype="object")
    result.loc[threat] = "severance_threat"
    result.loc[entry & ~richer_entry] = "entry_poorer_outside_H2"
    result.loc[richer_entry] = "entry_richer"
    result.loc[severance] = "severance"
    result.loc[severance & entry] = "paired_severance_entry"
    return result


def add_forward_outcomes(frame):
    result = frame[["iso3", "year"]].copy()
    grouped = {iso3: group.set_index("year") for iso3, group in frame.groupby("iso3")}
    for horizon in [1, 3, 5]:
        result[f"growth_forward_{horizon}y"] = np.nan
    result["disruption_forward_5y"] = np.nan
    result["disruption_evidence_years_5y"] = np.nan
    result["acceleration_onset_forward_8y"] = np.nan
    result["acceleration_evidence_years_8y"] = np.nan
    result["disruption_at_event"] = frame["disruption"].to_numpy()
    result["acceleration_at_event"] = frame["acceleration"].to_numpy()
    for idx, row in frame[["iso3", "year"]].iterrows():
        iso3, year = row["iso3"], int(row["year"])
        country = grouped[iso3]
        for horizon in [1, 3, 5]:
            window = country.reindex(range(year + 1, year + horizon + 1))
            growth = window["gdp_pc_growth"]
            if len(window) == horizon and growth.notna().all():
                result.at[idx, f"growth_forward_{horizon}y"] = growth.mean()
        disruption_window = country.reindex(range(year + 1, year + 6))
        evidence = disruption_window[["gdp_pc_growth", "gdp_pc_const", "inflation_annual"]].notna().any(axis=1)
        result.at[idx, "disruption_evidence_years_5y"] = evidence.sum()
        if year + 5 <= 2019 and evidence.any():
            result.at[idx, "disruption_forward_5y"] = int(disruption_window["disruption"].eq(1).any())
        acceleration_window = country.reindex(range(year + 1, year + 9))
        growth_evidence = acceleration_window["gdp_pc_growth"].notna()
        result.at[idx, "acceleration_evidence_years_8y"] = growth_evidence.sum()
        if year + 8 <= 2019 and growth_evidence.any():
            result.at[idx, "acceleration_onset_forward_8y"] = int(any(
                (iso3, future_year) in acceleration_onsets
                for future_year in range(year + 1, year + 9)
            ))
    return result


def excluded_keys(date_rule, flag_column):
    year_column = {"start": "start_year", "midpoint": "midpoint_year", "end": "end_year"}[date_rule]
    selected = events[events[flag_column].astype(bool)]
    return set(zip(selected["iso3"], selected[year_column]))


def scenario_frame(base, date_rule, case_selection):
    frame = base.copy()
    frame["external_realignment"] = external_category(frame, date_rule)
    suffix = "" if date_rule == "start" else f"_{date_rule}"
    if case_selection == "exclude_open_cases":
        keys = excluded_keys(date_rule, "open_case_review")
        frame = frame[~frame.apply(lambda row: (row["iso3"], row["year"]) in keys, axis=1)]
    elif case_selection == "exclude_systemic_shift":
        keys = excluded_keys(date_rule, "systemic_shift_flag")
        frame = frame[~frame.apply(lambda row: (row["iso3"], row["year"]) in keys, axis=1)]
    elif case_selection == "imposed_severance_only":
        chosen_severance = frame[f"severance{suffix}"].eq(1) & frame[f"imposed_severance{suffix}"].eq(0)
        frame = frame[~chosen_severance]
    return frame


def summarize_cells(frame, date_rule, case_selection):
    rows = []
    for (domestic, external), group in frame.groupby(["domestic_change", "external_realignment"], sort=True):
        row = {
            "analysis_status": "preliminary", "date_rule": date_rule,
            "case_selection": case_selection, "domestic_change": domestic,
            "external_realignment": external, "n_country_years": len(group),
        }
        for horizon in [1, 3, 5]:
            values = group[f"growth_forward_{horizon}y"].dropna()
            row[f"n_growth_{horizon}y"] = len(values)
            row[f"mean_growth_{horizon}y"] = values.mean() if len(values) else np.nan
        for variable, prefix in [
            ("disruption_forward_5y", "disruption_5y"),
            ("acceleration_onset_forward_8y", "acceleration_onset_8y"),
        ]:
            values = group[variable].dropna()
            row[f"n_{prefix}"] = len(values)
            row[f"count_{prefix}"] = int(values.sum()) if len(values) else 0
            row[f"rate_{prefix}"] = values.mean() if len(values) else np.nan
        rows.append(row)
    return rows


forward = add_forward_outcomes(panel)
panel = panel.merge(forward, on=["iso3", "year"], how="left", validate="one_to_one")
panel["domestic_change"] = domestic_category(panel)
analysis = panel[panel["year"].between(1960, 2019)].copy()

scenarios = [
    ("start", "current_coded_state"),
    ("midpoint", "current_coded_state"),
    ("end", "current_coded_state"),
    ("start", "exclude_open_cases"),
    ("start", "exclude_systemic_shift"),
    ("start", "imposed_severance_only"),
]
frequency_rows = []
for date_rule, case_selection in scenarios:
    frame = scenario_frame(analysis, date_rule, case_selection)
    frequency_rows.extend(summarize_cells(frame, date_rule, case_selection))
frequencies = pd.DataFrame(frequency_rows)
frequencies.to_csv(FREQUENCIES_OUT, index=False)

baseline = scenario_frame(analysis, "start", "current_coded_state")
baseline["primary_3x3_cell"] = np.where(
    baseline["domestic_change"].isin(["none", "turnover_or_formal_only", "power_or_apparatus_transformation"])
    & baseline["external_realignment"].isin(["none", "severance", "entry_richer"]),
    baseline["domestic_change"] + "__" + baseline["external_realignment"],
    "outside_or_unknown",
)
baseline_columns = [
    "analysis_status", "iso3", "country", "region", "year", "domestic_change",
    "external_realignment", "primary_3x3_cell", "growth_forward_1y", "growth_forward_3y",
    "growth_forward_5y", "disruption_forward_5y", "disruption_evidence_years_5y",
    "acceleration_onset_forward_8y", "acceleration_evidence_years_8y", "disruption_at_event",
    "acceleration_at_event",
]
baseline[baseline_columns].to_csv(CELLS_OUT, index=False)

# Retain all panel episodes, including pre-1960/window-edge cases, with explicit eligibility.
episode_rows = []
for date_rule in ["start", "midpoint", "end"]:
    year_column = {"start": "start_year", "midpoint": "midpoint_year", "end": "end_year"}[date_rule]
    classified = scenario_frame(panel, date_rule, "current_coded_state")
    external_lookup = classified.set_index(["iso3", "year"])["external_realignment"].to_dict()
    for _, event in events[events["type"].isin(["entry", "severance"])].iterrows():
        iso3, year = event["iso3"], int(event[year_column])
        current = panel[(panel["iso3"] == iso3) & (panel["year"] == year)].iloc[0]
        external = external_lookup[(iso3, year)]
        signed_outcome = (current["disruption_forward_5y"] if event["type"] == "severance"
                          else current["acceleration_onset_forward_8y"])
        if event["window_edge_outcome_indeterminate"]:
            timing = "indeterminate_window_edge"
        elif event["type"] == "entry" and event["richer_sphere"] != True:
            timing = "outside_H2_sign_test"
        elif external == "paired_severance_entry":
            timing = "paired_transition_not_clean_single_treatment"
        elif current["disruption_at_event"] == 1 or current["acceleration_at_event"] == 1:
            timing = "ongoing_outcome_at_event"
        elif pd.isna(signed_outcome):
            timing = "missing_forward_outcome"
        elif signed_outcome == 1:
            timing = "signed_outcome_observed_after_event"
        else:
            timing = "signed_outcome_not_observed_in_window"
        episode_rows.append({
            "analysis_status": "preliminary", "episode_id": event["episode_id"],
            "iso3": iso3, "country": event["country"], "region": event["region"],
            "type": event["type"], "patron": event["patron"], "date_rule": date_rule,
            "event_year": year, "interval_start": event["start_year"], "interval_end": event["end_year"],
            "domestic_change": current["domestic_change"], "external_realignment": external,
            "richer_sphere": event["richer_sphere"], "voluntariness": event["voluntariness_base"],
            "systemic_shift_flag": event["systemic_shift_flag"],
            "open_case_review": event["open_case_review"],
            "window_edge_outcome_indeterminate": event["window_edge_outcome_indeterminate"],
            "eligible_1960_2019": 1960 <= year <= 2019,
            "growth_forward_1y": current["growth_forward_1y"],
            "growth_forward_3y": current["growth_forward_3y"],
            "growth_forward_5y": current["growth_forward_5y"],
            "disruption_at_event": current["disruption_at_event"],
            "disruption_forward_5y": current["disruption_forward_5y"],
            "disruption_evidence_years_5y": current["disruption_evidence_years_5y"],
            "acceleration_at_event": current["acceleration_at_event"],
            "acceleration_onset_forward_8y": current["acceleration_onset_forward_8y"],
            "acceleration_evidence_years_8y": current["acceleration_evidence_years_8y"],
            "descriptive_timing_status": timing,
        })
episode_outcomes = pd.DataFrame(episode_rows)
episode_outcomes.to_csv(EPISODES_OUT, index=False)

print(f"preliminary baseline country-years: {len(baseline)}")
print(f"preliminary frequency rows: {len(frequencies)} across {len(scenarios)} scenarios")
print(f"preliminary episode-date rows: {len(episode_outcomes)}")
print("\nBaseline 3x3 cell sizes:")
print(baseline[baseline["primary_3x3_cell"] != "outside_or_unknown"].groupby(
    ["domestic_change", "external_realignment"]).size().to_string())
print("\nBaseline realignment outcomes:")
for external in ["severance", "entry_richer", "paired_severance_entry"]:
    subset = baseline[baseline["external_realignment"] == external]
    print(external, {
        "n": len(subset),
        "mean_growth_5y": subset["growth_forward_5y"].mean(),
        "disruption_5y_rate": subset["disruption_forward_5y"].mean(),
        "acceleration_onset_8y_rate": subset["acceleration_onset_forward_8y"].mean(),
    })
