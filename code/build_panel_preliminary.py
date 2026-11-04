"""Assemble the preliminary Step 5 country-year panel without resolving open coding issues.

The current accepted coding state is merged onto the untouched 1945-2019 spine.
RegimeChange, PowerStructure, apparatus, and coalition missingness is preserved.
Post-2015 Turnover values are included but flagged as unverified.

Realignment event indicators use interval starts for the compatibility columns and
also provide midpoint and endpoint variants. Threats and non-panel calibration cases
are excluded from Severance/Entry. Entry covers all coded entries; entry_richer is
the H2 subset under R5. The episode-level coding table retains all intervals and
review flags. Disruption uses the exact annual screen, not segmented episode spans.
"""
import numpy as np
import pandas as pd

Y0, Y1 = 1945, 2019
KEYS = ["iso3", "year"]
SPINE = "data_clean/panel_spine.csv"
OUT = "data_clean/panel_preliminary.csv"

spine = pd.read_csv(SPINE)
panel = spine[["iso3", "country", "region", "year"]].copy()
keys = spine[["iso3", "year"]]
countries = pd.read_csv("data_clean/countries.csv")
panel_iso = set(countries["iso3"])


def merge_keys(frame, addition):
    return frame.merge(addition, on=KEYS, how="left", validate="one_to_one")


def join_unique(values):
    seen = []
    for value in values:
        if pd.isna(value) or value == "":
            continue
        value = str(value)
        if value not in seen:
            seen.append(value)
    return ";".join(seen)


def set_event_indicator(frame, events, year_column, output_column, mask):
    selected = events[mask]
    event_keys = set(zip(selected["iso3"], selected[year_column]))
    frame[output_column] = pd.array(
        [int((iso3, year) in event_keys) for iso3, year in zip(frame["iso3"], frame["year"])],
        dtype="Int64",
    )


# WDI controls remain source-specific and unspliced.
wdi_years = [str(y) for y in range(1960, 2020)]
wdi = pd.read_csv(
    "data_raw/WDI/WDICSV.csv",
    usecols=["Country Code", "Indicator Code"] + wdi_years,
    dtype=str,
)
wdi = wdi[wdi["Country Code"].isin(panel_iso)]
controls = keys.copy()
for code, name in [
    ("NY.GDP.PETR.RT.ZS", "oil_rents_pct_gdp"),
    ("SP.POP.TOTL", "population"),
    ("NE.GDI.TOTL.ZS", "investment_pct_gdp"),
]:
    series = wdi[wdi["Indicator Code"] == code][["Country Code"] + wdi_years]
    series = series.set_index("Country Code").stack().rename(name).rename_axis(KEYS).reset_index()
    series["year"] = series["year"].astype(int)
    series[name] = pd.to_numeric(series[name], errors="coerce")
    controls = merge_keys(controls, series)
controls.insert(0, "analysis_status", "preliminary")
controls.to_csv("data_clean/controls_preliminary.csv", index=False)

outcomes = pd.read_csv("data_clean/outcomes.csv").rename(columns={
    "gdppc": "gdp_pc_const",
    "gdppc_source": "gdp_pc_source",
    "growth_pc": "gdp_pc_growth",
    "growth_source": "gdp_pc_growth_source",
    "seam": "gdp_pc_seam",
    "inflation": "inflation_annual",
    "infl_source": "inflation_source",
})
panel = merge_keys(panel, outcomes)
panel = merge_keys(panel, controls)

turnover = pd.read_csv("data_clean/turnover.csv").rename(columns={"source": "turnover_source"})
panel = merge_keys(panel, turnover)
panel["turnover_evidence_status"] = "archigos"
panel.loc[panel["year"] >= 2016, "turnover_evidence_status"] = "hand_unverified"
panel.loc[panel["iso3"] == "CHE", "turnover_evidence_status"] = "excluded_collective_executive"

coalition = pd.read_csv("data_clean/coalition.csv").rename(columns={"source": "coalition_source"})
coalition["coalition_change"] = pd.array(coalition["coalition_change"], dtype="Int64")
panel = merge_keys(panel, coalition)

for variable, path in [
    ("regime_change", "data_clean/regime_change.csv"),
    ("power_structure", "data_clean/power_structure.csv"),
    ("apparatus_restructuring", "data_clean/apparatus_restructuring.csv"),
]:
    domestic = pd.read_csv(path, keep_default_na=True)
    domestic[variable] = pd.array(domestic[variable], dtype="Int64")
    rename = {"evidence_status": f"{variable}_evidence_status"}
    if "episode_id" in domestic:
        rename["episode_id"] = f"{variable}_episode_id"
    domestic = domestic.rename(columns=rename)
    panel = merge_keys(panel, domestic)

# Preserve every realignment interval and derive R5 without consulting outcomes.
events = pd.read_csv("data_clean/episodes.csv")
events = events.merge(countries[["iso3", "region"]], on="iso3", how="left", validate="many_to_one")
events["in_panel"] = events["iso3"].isin(panel_iso)
events["midpoint_year"] = (events["start_year"] + events["end_year"]) // 2
events["voluntariness_base"] = events["voluntariness"].str.split("(").str[0].str.strip()
events["window_edge_outcome_indeterminate"] = events["notes"].str.contains(
    r"window-edge|outcome test (?:structurally )?indeterminate", case=False, regex=True, na=False
)
events["open_case_review"] = events["episode_id"].isin({"E020", "E059", "E067"})
events["r5_reference_year"] = pd.NA
events["r5_patron_gdppc"] = np.nan
events["r5_region_median_gdppc"] = np.nan
events["richer_sphere"] = pd.NA
r5 = pd.read_csv("data_clean/r5_reference.csv")
patron_columns = {
    "USA": "usa_gdppc",
    "USA/EU": "usa_gdppc",
    "USSR": "ussr_rus_gdppc",
    "USSR/RUS": "ussr_rus_gdppc",
}
for idx, event in events.iterrows():
    if event["type"] != "entry" or not event["in_panel"]:
        continue
    patron_column = patron_columns[event["patron"]]
    classifications = []
    references = {}
    for label, year in [("start", event["start_year"]), ("end", event["end_year"])]:
        reference = r5[(r5["region"] == event["region"]) & (r5["year"] == year)]
        assert len(reference) == 1, f"Missing R5 region-year: {event['episode_id']} {year}"
        reference = reference.iloc[0]
        patron_gdppc = reference[patron_column]
        regional_median = reference["median_gdppc"]
        references[label] = (year, patron_gdppc, regional_median)
        if pd.notna(patron_gdppc) and pd.notna(regional_median):
            classifications.append(bool(patron_gdppc > regional_median))
    assert classifications, f"No R5 classification: {event['episode_id']}"
    assert len(set(classifications)) == 1, f"R5 changes across interval: {event['episode_id']}"
    year, patron_gdppc, regional_median = references["end"]
    if pd.isna(patron_gdppc) or pd.isna(regional_median):
        year, patron_gdppc, regional_median = references["start"]
    events.at[idx, "r5_reference_year"] = year
    events.at[idx, "r5_patron_gdppc"] = patron_gdppc
    events.at[idx, "r5_region_median_gdppc"] = regional_median
    events.at[idx, "richer_sphere"] = classifications[0]

coding_columns = [
    "episode_id", "iso3", "country", "region", "type", "in_panel", "start_year", "midpoint_year",
    "end_year", "patron", "voluntariness", "voluntariness_base", "systemic_shift_flag",
    "richer_sphere", "r5_reference_year", "r5_patron_gdppc", "r5_region_median_gdppc",
    "window_edge_outcome_indeterminate", "open_case_review",
]
event_codings = events[coding_columns]
event_codings.insert(0, "analysis_status", "preliminary")
event_codings.to_csv("data_clean/realignment_event_codings_preliminary.csv", index=False)

coded = events[events["in_panel"]]
consummated = coded[coded["type"].isin(["entry", "severance"])]
for rule, year_column in [
    ("start", "start_year"),
    ("midpoint", "midpoint_year"),
    ("end", "end_year"),
]:
    suffix = "" if rule == "start" else f"_{rule}"
    set_event_indicator(panel, coded, year_column, f"severance{suffix}", coded["type"] == "severance")
    set_event_indicator(panel, coded, year_column, f"entry{suffix}", coded["type"] == "entry")
    set_event_indicator(
        panel, coded, year_column, f"entry_richer{suffix}",
        (coded["type"] == "entry") & (coded["richer_sphere"] == True),
    )
    set_event_indicator(
        panel, coded, year_column, f"imposed_severance{suffix}",
        (coded["type"] == "severance") & (coded["voluntariness_base"] == "imposed"),
    )
set_event_indicator(panel, coded, "start_year", "severance_threat", coded["type"] == "severance_threat")

metadata = {}
for key, group in consummated.groupby(["iso3", "start_year"], sort=False):
    metadata[key] = {
        "realignment_episode_ids": join_unique(group["episode_id"]),
        "patron": join_unique(group["patron"]),
        "voluntariness": join_unique(group["voluntariness_base"]),
        "systemic_shift_flag": int((group["systemic_shift_flag"] == 1).any()),
        "realignment_open_review": int(group["open_case_review"].any()),
        "window_edge_realignment": int(group["window_edge_outcome_indeterminate"].any()),
    }
for column in [
    "realignment_episode_ids", "patron", "voluntariness", "systemic_shift_flag",
    "realignment_open_review", "window_edge_realignment",
]:
    if column in {"systemic_shift_flag", "realignment_open_review", "window_edge_realignment"}:
        panel[column] = pd.array(
            [metadata.get((iso3, year), {}).get(column, 0)
             for iso3, year in zip(panel["iso3"], panel["year"])],
            dtype="Int64",
        )
    else:
        panel[column] = [metadata.get((iso3, year), {}).get(column, "")
                         for iso3, year in zip(panel["iso3"], panel["year"])]

# Exact annual disruption union; acceleration episodes have continuous screened spans.
disruption = pd.read_csv("data_clean/disruption_years_preliminary.csv").rename(columns={
    "episode_id": "disruption_episode_id",
    "rules": "disruption_rules",
})
disruption["disruption"] = pd.array(disruption["disruption"], dtype="Int64")
panel = merge_keys(panel, disruption)

acceleration_rows = []
for _, episode in pd.read_csv("data_clean/acceleration_episodes.csv").iterrows():
    for year in range(int(episode["start_year"]), int(episode["end_year"]) + 1):
        acceleration_rows.append({
            "iso3": episode["iso3"], "year": year, "acceleration": 1,
            "acceleration_episode_id": episode["episode_id"],
        })
acceleration = pd.DataFrame(acceleration_rows).groupby(KEYS).agg(
    acceleration=("acceleration", "max"),
    acceleration_episode_id=("acceleration_episode_id", join_unique),
).reset_index()
acceleration = merge_keys(keys, acceleration)
acceleration["acceleration"] = pd.array(acceleration["acceleration"].fillna(0), dtype="Int64")
panel = merge_keys(panel, acceleration)
panel["analysis_status"] = "preliminary"

columns = [
    "analysis_status", "iso3", "country", "region", "year",
    "turnover", "coalition_change", "regime_change", "power_structure", "apparatus_restructuring",
    "severance", "entry", "entry_richer", "imposed_severance", "severance_threat",
    "patron", "voluntariness", "systemic_shift_flag", "realignment_episode_ids",
    "disruption", "acceleration", "gdp_pc_growth", "gdp_pc_const", "inflation_annual",
    "oil_rents_pct_gdp", "population", "investment_pct_gdp",
    "leader_in", "irregular_exit", "turnover_source", "turnover_evidence_status",
    "exec_party", "coalition_source", "regime_change_evidence_status",
    "power_structure_evidence_status", "power_structure_episode_id",
    "apparatus_restructuring_evidence_status", "apparatus_restructuring_episode_id",
    "severance_midpoint", "entry_midpoint", "entry_richer_midpoint", "imposed_severance_midpoint",
    "severance_end", "entry_end", "entry_richer_end", "imposed_severance_end",
    "realignment_open_review", "window_edge_realignment",
    "disruption_episode_id", "disruption_rules", "acceleration_episode_id",
    "gdp_pc_source", "gdp_pc_growth_source", "inflation_source", "gdp_pc_seam",
]
panel = panel[columns]
panel.to_csv(OUT, index=False)

print(f"wrote {OUT}: {len(panel)} rows, {panel['iso3'].nunique()} countries, {Y0}-{Y1}")
print(f"controls: {controls.notna().sum().to_dict()}")
for variable in [
    "turnover", "coalition_change", "regime_change", "power_structure", "apparatus_restructuring",
    "severance", "entry", "entry_richer", "imposed_severance", "severance_threat",
    "disruption", "acceleration",
]:
    print(f"{variable}: positives={int((panel[variable] == 1).sum())}, missing={int(panel[variable].isna().sum())}")
print(f"post-2015 turnover rows flagged unverified: {int((panel['turnover_evidence_status'] == 'hand_unverified').sum())}")
print(f"realignment event codings: {len(event_codings)} total; {int(event_codings['in_panel'].sum())} panel")
