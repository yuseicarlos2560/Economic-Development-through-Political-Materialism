"""Preliminary point-estimate sensitivity for theory-aligned baseline-cell contrasts."""
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_baseline_contrasts_preliminary import (
    CELLS,
    OUTCOMES,
    build_contrasts,
)

ROOT = Path(__file__).resolve().parents[1]
SENSITIVITY_OUT = ROOT / "data_clean" / "baseline_contrast_sensitivity_preliminary.csv"
LEAVE_ONE_OUT = ROOT / "data_clean" / "baseline_contrast_leave_one_country_out_preliminary.csv"


def assign_cells(frame, date_rule):
    result = frame.copy()
    if date_rule != "start":
        suffix = f"_{date_rule}"
        severance = result[f"severance{suffix}"].eq(1)
        entry = result[f"entry{suffix}"].eq(1)
        richer = result[f"entry_richer{suffix}"].eq(1)
        external = pd.Series("none", index=result.index, dtype="object")
        external.loc[result["severance_threat"].eq(1)] = "severance_threat"
        external.loc[entry & ~richer] = "entry_poorer_outside_H2"
        external.loc[richer] = "entry_richer"
        external.loc[severance] = "severance"
        external.loc[severance & entry] = "paired_severance_entry"
        result["external_realignment"] = external
    known_domestic = result["domestic_change"].isin([
        "none", "turnover_or_formal_only", "power_or_apparatus_transformation"
    ])
    known_external = result["external_realignment"].isin(["none", "severance", "entry_richer"])
    result["primary_3x3_cell"] = np.where(
        known_domestic & known_external,
        result["domestic_change"] + "__" + result["external_realignment"],
        "outside_or_unknown",
    )
    return result


def fit_points(frame, outcome, scale, fixed_effects, estimate_type, contrasts):
    frame = frame[frame[outcome].notna() & frame["primary_3x3_cell"].isin(CELLS)].copy()
    occupied = [cell for cell in CELLS if frame["primary_3x3_cell"].eq(cell).any()]
    cell_index = frame["primary_3x3_cell"].map({cell: i for i, cell in enumerate(occupied)}).to_numpy()
    matrices = [np.eye(len(occupied))[cell_index.astype(int)]]
    if fixed_effects:
        matrices.extend([
            pd.get_dummies(frame["iso3"], drop_first=True, dtype=float).to_numpy(),
            pd.get_dummies(frame["year"], drop_first=True, dtype=float).to_numpy(),
        ])
    x = np.column_stack(matrices)
    y = frame[outcome].to_numpy(dtype=float) * scale
    full_rank = np.linalg.matrix_rank(x) == x.shape[1]
    beta = np.linalg.lstsq(x, y, rcond=None)[0] if full_rank else None
    rows = []
    for record in contrasts:
        available = record["cell"] in occupied and record["control_cell"] in occupied
        estimable = available and full_rank
        cell_frame = frame[frame["primary_3x3_cell"].eq(record["cell"])]
        control_frame = frame[frame["primary_3x3_cell"].eq(record["control_cell"])]
        estimate = np.nan
        if estimable:
            contrast = np.zeros(x.shape[1])
            contrast[occupied.index(record["cell"])] = 1
            contrast[occupied.index(record["control_cell"])] = -1
            estimate = float(contrast @ beta)
        rows.append({
            **record,
            "outcome": outcome,
            "estimate_type": estimate_type,
            "estimate_pp": estimate,
            "estimation_status": "estimated" if estimable else "not_estimable",
            "cell_n": len(cell_frame),
            "control_n": len(control_frame),
            "cell_countries": cell_frame["iso3"].nunique(),
            "control_countries": control_frame["iso3"].nunique(),
            "model_n": len(frame),
            "model_countries": frame["iso3"].nunique(),
            "country_fixed_effects": fixed_effects,
            "year_fixed_effects": fixed_effects,
        })
    return rows


def scenario_frames(cells):
    scenarios = []
    for date_rule in ["start", "midpoint", "end"]:
        scenarios.append((date_rule, "current_coded_state", assign_cells(cells, date_rule)))
    open_cases = assign_cells(cells, "start")
    scenarios.append((
        "start", "exclude_open_cases",
        open_cases[open_cases["realignment_open_review"].ne(1)].copy(),
    ))
    systemic = assign_cells(cells, "start")
    scenarios.append((
        "start", "exclude_systemic_shift",
        systemic[systemic["systemic_shift_flag"].ne(1)].copy(),
    ))
    imposed = assign_cells(cells, "start")
    imposed = imposed[
        imposed["external_realignment"].ne("severance") | imposed["imposed_severance"].eq(1)
    ].copy()
    scenarios.append(("start", "imposed_severance_only", imposed))
    return scenarios


def main():
    cells = pd.read_csv(ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv")
    panel = pd.read_csv(
        ROOT / "data_clean" / "panel_preliminary.csv",
        usecols=[
            "iso3", "year", "severance_midpoint", "entry_midpoint", "entry_richer_midpoint",
            "severance_end", "entry_end", "entry_richer_end", "severance_threat",
            "realignment_open_review", "systemic_shift_flag", "imposed_severance",
        ],
    )
    cells = cells.merge(panel, on=["iso3", "year"], how="left", validate="one_to_one")
    contrasts = [c for c in build_contrasts() if c["comparison_family"] == "primary_theory_aligned"]
    rows = []
    for date_rule, selection, frame in scenario_frames(cells):
        for outcome, (column, scale) in OUTCOMES.items():
            for fixed_effects, estimate_type in [(False, "raw"), (True, "fixed_effects")]:
                fitted = fit_points(frame, column, scale, fixed_effects, estimate_type, contrasts)
                for row in fitted:
                    row.update({
                        "analysis_status": "preliminary",
                        "inference_status": "preliminary_sensitivity_point_estimate_only_noncausal",
                        "date_rule": date_rule,
                        "case_selection": selection,
                    })
                rows.extend(fitted)
        print(f"{date_rule}: {selection}")
    sensitivity = pd.DataFrame(rows)
    sensitivity.to_csv(SENSITIVITY_OUT, index=False)

    baseline = assign_cells(cells, "start")
    main_results = pd.read_csv(ROOT / "data_clean" / "baseline_cell_contrasts_preliminary.csv")
    leave_one_rows = []
    countries = sorted(baseline["iso3"].unique())
    for dropped in countries:
        reduced = baseline[baseline["iso3"].ne(dropped)].copy()
        for outcome, (column, scale) in OUTCOMES.items():
            for fixed_effects, estimate_type in [(False, "raw"), (True, "fixed_effects")]:
                fitted = fit_points(reduced, column, scale, fixed_effects, estimate_type, contrasts)
                for row in fitted:
                    full = main_results[
                        main_results["outcome"].eq(column)
                        & main_results["comparison_family"].eq("primary_theory_aligned")
                        & main_results["contrast_id"].eq(row["contrast_id"])
                        & main_results["estimate_type"].eq(estimate_type)
                    ].iloc[0]
                    row.update({
                        "analysis_status": "preliminary",
                        "inference_status": "preliminary_leave_one_country_out_point_estimate_only_noncausal",
                        "date_rule": "start",
                        "case_selection": "current_coded_state",
                        "dropped_iso3": dropped,
                        "full_sample_estimate_pp": full["estimate_pp"],
                        "estimate_change_pp": row["estimate_pp"] - full["estimate_pp"],
                        "sign_flip_from_full_sample": (
                            bool(np.sign(row["estimate_pp"]) != np.sign(full["estimate_pp"]))
                            if np.isfinite(row["estimate_pp"]) else pd.NA
                        ),
                    })
                leave_one_rows.extend(fitted)
    leave_one = pd.DataFrame(leave_one_rows)
    leave_one.to_csv(LEAVE_ONE_OUT, index=False)
    print(f"wrote {SENSITIVITY_OUT.relative_to(ROOT)}: {len(sensitivity)} rows")
    print(f"wrote {LEAVE_ONE_OUT.relative_to(ROOT)}: {len(leave_one)} rows")


if __name__ == "__main__":
    main()
