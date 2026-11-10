"""Audit preliminary baseline-cell contrast estimates and sensitivity artifacts."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "data_clean" / "baseline_cell_contrasts_preliminary.csv"
SENSITIVITY = ROOT / "data_clean" / "baseline_contrast_sensitivity_preliminary.csv"
LEAVE_ONE_OUT = ROOT / "data_clean" / "baseline_contrast_leave_one_country_out_preliminary.csv"

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


main = pd.read_csv(MAIN)
sensitivity = pd.read_csv(SENSITIVITY)
leave_one = pd.read_csv(LEAVE_ONE_OUT)

check(len(main) == 90, "Main results must contain 90 rows")
check(main["analysis_status"].eq("preliminary").all(), "Main preliminary labels")
check(main["inference_status"].eq("preliminary_exploratory_noncausal").all(), "Main inference labels")
check(main["bootstrap_replications"].eq(1999).all(), "Main bootstrap count")
check(main["date_rule"].eq("start").all(), "Main date rule")
check(main["case_selection"].eq("current_coded_state").all(), "Main case selection")
check(not main.duplicated([
    "outcome", "comparison_family", "contrast_id", "estimate_type"
]).any(), "Main result keys must be unique")
check(main["p_bootstrap"].between(0, 1).all(), "Bootstrap p-values must be in [0,1]")
check(main["p_holm"].between(0, 1).all(), "Holm p-values must be in [0,1]")
check((main["p_holm"] >= main["p_bootstrap"]).all(), "Holm adjustment cannot reduce p-values")
check((main["ci95_low_pp"] <= main["ci95_high_pp"]).all(), "Confidence interval order")

raw = main[main["estimate_type"].eq("raw")]
check(np.allclose(
    raw["estimate_pp"], raw["raw_cell_mean"] - raw["raw_control_mean"]
), "Raw contrasts must equal raw cell differences")
check((~raw["country_fixed_effects"] & ~raw["year_fixed_effects"]).all(), "Raw model FE flags")
fixed = main[main["estimate_type"].eq("fixed_effects")]
check((fixed["country_fixed_effects"] & fixed["year_fixed_effects"]).all(), "FE model flags")

for _, group in main.groupby(["comparison_family", "estimate_type"]):
    ordered = group.sort_values("p_bootstrap")
    m = len(ordered)
    expected = np.maximum.accumulate([
        min(1.0, (m - rank) * p) for rank, p in enumerate(ordered["p_bootstrap"])
    ])
    check(np.allclose(expected, ordered["p_holm"]), "Holm calculation")

check(len(sensitivity) == 252, "Sensitivity must contain 252 rows")
check(sensitivity["analysis_status"].eq("preliminary").all(), "Sensitivity preliminary labels")
check(sensitivity["inference_status"].eq(
    "preliminary_sensitivity_point_estimate_only_noncausal"
).all(), "Sensitivity inference labels")
check(sensitivity.loc[
    sensitivity["estimation_status"].eq("not_estimable"), "estimate_pp"
].isna().all(), "Non-estimable sensitivity contrasts must have missing estimates")

keys = ["outcome", "comparison_family", "contrast_id", "estimate_type"]
current = sensitivity[
    sensitivity["date_rule"].eq("start")
    & sensitivity["case_selection"].eq("current_coded_state")
]
comparison = current.merge(main, on=keys, suffixes=("_sensitivity", "_main"))
check(len(comparison) == 42, "Current sensitivity should reproduce 42 main primary rows")
check(np.allclose(
    comparison["estimate_pp_sensitivity"], comparison["estimate_pp_main"]
), "Current sensitivity estimates must reproduce main estimates")

check(len(leave_one) == 3066, "Leave-one-country-out must contain 3,066 rows")
check(leave_one["analysis_status"].eq("preliminary").all(), "Leave-one-out preliminary labels")
check(leave_one["dropped_iso3"].nunique() == 73, "Leave-one-out country coverage")
check(leave_one["inference_status"].eq(
    "preliminary_leave_one_country_out_point_estimate_only_noncausal"
).all(), "Leave-one-out inference labels")
check(np.allclose(
    leave_one["estimate_change_pp"],
    leave_one["estimate_pp"] - leave_one["full_sample_estimate_pp"],
    equal_nan=True,
), "Leave-one-out estimate changes")

if failures:
    for failure in failures:
        print(f"FAIL: {failure}")
    raise SystemExit(1)
print(f"PASS: {len(main)} main contrasts, {len(sensitivity)} sensitivity rows, {len(leave_one)} leave-one-out rows")
print("All artifacts are preliminary; raw identities, Holm adjustments, and current-scenario reproduction pass")
