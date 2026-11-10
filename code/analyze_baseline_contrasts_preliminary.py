"""Preliminary baseline-cell contrasts with country-clustered wild bootstrap-t inference."""
from pathlib import Path
import argparse

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data_clean" / "baseline_cell_contrasts_preliminary.csv"

CELL_SPECS = [
    ("none", "none"),
    ("none", "severance"),
    ("none", "entry_richer"),
    ("turnover_or_formal_only", "none"),
    ("turnover_or_formal_only", "severance"),
    ("turnover_or_formal_only", "entry_richer"),
    ("power_or_apparatus_transformation", "none"),
    ("power_or_apparatus_transformation", "severance"),
    ("power_or_apparatus_transformation", "entry_richer"),
]
CELLS = [f"{domestic}__{external}" for domestic, external in CELL_SPECS]
DOMESTIC_LABELS = {
    "none": "No domestic event",
    "turnover_or_formal_only": "Turnover/formal only",
    "power_or_apparatus_transformation": "Deep transformation",
}
EXTERNAL_LABELS = {
    "none": "No realignment",
    "severance": "Severance",
    "entry_richer": "Richer entry",
}
OUTCOMES = {
    "growth_5y": ("growth_forward_5y", 1.0),
    "disruption_5y": ("disruption_forward_5y", 100.0),
    "acceleration_onset_8y": ("acceleration_onset_forward_8y", 100.0),
}
WEBB_WEIGHTS = np.array([
    -np.sqrt(3 / 2), -1.0, -np.sqrt(1 / 2),
    np.sqrt(1 / 2), 1.0, np.sqrt(3 / 2),
])


def cell_name(domestic, external):
    return f"{domestic}__{external}"


def contrast_record(family, domestic, external, control_domestic, control_external, hypothesis):
    cell = cell_name(domestic, external)
    control = cell_name(control_domestic, control_external)
    return {
        "comparison_family": family,
        "contrast_id": f"{cell}__vs__{control}",
        "hypothesis": hypothesis,
        "domestic_change": domestic,
        "external_realignment": external,
        "cell": cell,
        "control_cell": control,
        "cell_label": f"{DOMESTIC_LABELS[domestic]}: {EXTERNAL_LABELS[external]}",
        "control_label": f"{DOMESTIC_LABELS[control_domestic]}: {EXTERNAL_LABELS[control_external]}",
    }


def build_contrasts():
    contrasts = []
    for domestic in DOMESTIC_LABELS:
        for external, hypothesis in [("severance", "H2_severance"), ("entry_richer", "H2_entry")]:
            contrasts.append(contrast_record(
                "primary_theory_aligned", domestic, external, domestic, "none", hypothesis
            ))
    contrasts.append(contrast_record(
        "primary_theory_aligned", "turnover_or_formal_only", "none", "none", "none", "H1"
    ))
    for domestic, external in CELL_SPECS[1:]:
        hypothesis = "H1" if (domestic, external) == ("turnover_or_formal_only", "none") else "secondary_descriptive"
        contrasts.append(contrast_record(
            "secondary_common_reference", domestic, external, "none", "none", hypothesis
        ))
    return contrasts


def design_matrix(frame, fixed_effects):
    cell_index = frame["primary_3x3_cell"].map({cell: i for i, cell in enumerate(CELLS)}).to_numpy()
    assert not pd.isna(cell_index).any()
    matrices = [np.eye(len(CELLS))[cell_index.astype(int)]]
    if fixed_effects:
        country = pd.get_dummies(frame["iso3"], drop_first=True, dtype=float)
        year = pd.get_dummies(frame["year"], drop_first=True, dtype=float)
        matrices.extend([country.to_numpy(), year.to_numpy()])
    x = np.column_stack(matrices)
    assert np.linalg.matrix_rank(x) == x.shape[1], "Design matrix is rank deficient"
    return x


def cluster_variance(x, residuals, inverse_crossprod, contrast, cluster_indices, n_clusters):
    influence = x @ (inverse_crossprod @ contrast)
    scores = np.array([np.sum(influence[idx] * residuals[idx]) for idx in cluster_indices])
    n, k = x.shape
    correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
    return correction * np.sum(scores ** 2)


def holm_adjust(results):
    results = results.copy()
    results["p_holm"] = np.nan
    group_columns = ["comparison_family", "estimate_type"]
    for _, indices in results.groupby(group_columns).groups.items():
        indices = list(indices)
        ordered = sorted(indices, key=lambda idx: results.at[idx, "p_bootstrap"])
        m = len(ordered)
        running = 0.0
        for rank, idx in enumerate(ordered):
            adjusted = min(1.0, (m - rank) * results.at[idx, "p_bootstrap"])
            running = max(running, adjusted)
            results.at[idx, "p_holm"] = running
    return results


def fit_model(frame, outcome, scale, fixed_effects, estimate_type, contrasts, bootstraps, seed):
    y = frame[outcome].to_numpy(dtype=float) * scale
    x = design_matrix(frame, fixed_effects)
    n, k = x.shape
    crossprod = x.T @ x
    inverse_crossprod = np.linalg.inv(crossprod)
    projection = inverse_crossprod @ x.T
    beta = projection @ y
    fitted = x @ beta
    residuals = y - fitted
    cluster_codes, cluster_names = pd.factorize(frame["iso3"], sort=True)
    cluster_indices = [np.flatnonzero(cluster_codes == code) for code in range(len(cluster_names))]
    n_clusters = len(cluster_names)

    contrast_vectors = []
    for record in contrasts:
        vector = np.zeros(len(CELLS))
        vector[CELLS.index(record["cell"])] = 1
        vector[CELLS.index(record["control_cell"])] = -1
        contrast_vectors.append(np.pad(vector, (0, k - len(CELLS))))
    contrast_matrix = np.stack(contrast_vectors)
    estimates = contrast_matrix @ beta
    standard_errors = np.sqrt([
        cluster_variance(x, residuals, inverse_crossprod, contrast, cluster_indices, n_clusters)
        for contrast in contrast_matrix
    ])
    t_observed = estimates / standard_errors

    rng = np.random.default_rng(seed)
    t_boot = np.empty((len(contrasts), bootstraps))
    batch_size = 250
    for start in range(0, bootstraps, batch_size):
        b = min(batch_size, bootstraps - start)
        weights = rng.choice(WEBB_WEIGHTS, size=(n_clusters, b))
        y_boot = fitted[:, None] + residuals[:, None] * weights[cluster_codes, :]
        beta_boot = projection @ y_boot
        residuals_boot = y_boot - x @ beta_boot
        estimates_boot = contrast_matrix @ beta_boot
        for j, contrast in enumerate(contrast_matrix):
            influence = x @ (inverse_crossprod @ contrast)
            scores = np.stack([
                np.sum(influence[idx, None] * residuals_boot[idx, :], axis=0)
                for idx in cluster_indices
            ])
            correction = (n_clusters / (n_clusters - 1)) * ((n - 1) / (n - k))
            se_boot = np.sqrt(correction * np.sum(scores ** 2, axis=0))
            t_boot[j, start:start + b] = (estimates_boot[j] - estimates[j]) / se_boot

    p_values = (1 + np.sum(np.abs(t_boot) >= np.abs(t_observed[:, None]), axis=1)) / (bootstraps + 1)
    lower_quantile = np.quantile(t_boot, 0.025, axis=1)
    upper_quantile = np.quantile(t_boot, 0.975, axis=1)
    ci_lower = estimates - upper_quantile * standard_errors
    ci_upper = estimates - lower_quantile * standard_errors

    rows = []
    for j, record in enumerate(contrasts):
        cell_frame = frame[frame["primary_3x3_cell"].eq(record["cell"])]
        control_frame = frame[frame["primary_3x3_cell"].eq(record["control_cell"])]
        cell_mean = cell_frame[outcome].mean() * scale
        control_mean = control_frame[outcome].mean() * scale
        if estimate_type == "raw":
            assert np.isclose(estimates[j], cell_mean - control_mean), record["contrast_id"]
        rows.append({
            "analysis_status": "preliminary",
            "inference_status": "preliminary_exploratory_noncausal",
            "date_rule": "start",
            "case_selection": "current_coded_state",
            "sample_years": "1960-2019",
            "outcome": outcome,
            **record,
            "estimate_type": estimate_type,
            "estimate_pp": estimates[j],
            "cluster_se_pp": standard_errors[j],
            "ci95_low_pp": ci_lower[j],
            "ci95_high_pp": ci_upper[j],
            "t_statistic": t_observed[j],
            "p_bootstrap": p_values[j],
            "raw_cell_mean": cell_mean,
            "raw_control_mean": control_mean,
            "cell_n": len(cell_frame),
            "control_n": len(control_frame),
            "cell_countries": cell_frame["iso3"].nunique(),
            "control_countries": control_frame["iso3"].nunique(),
            "model_n": n,
            "model_countries": n_clusters,
            "model_parameters": k,
            "country_fixed_effects": fixed_effects,
            "year_fixed_effects": fixed_effects,
            "bootstrap_replications": bootstraps,
            "bootstrap_method": "unrestricted_wild_cluster_bootstrap_t_webb_by_country",
            "ci_method": "95_percent_wild_cluster_bootstrap_t_not_multiplicity_adjusted",
            "random_seed": seed,
        })
    return rows


def main(bootstraps):
    cells = pd.read_csv(ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv")
    cells = cells[cells["primary_3x3_cell"].isin(CELLS)].copy()
    contrasts = build_contrasts()
    rows = []
    for outcome_index, (outcome, (column, scale)) in enumerate(OUTCOMES.items()):
        frame = cells[cells[column].notna()].copy()
        for model_index, (fixed_effects, estimate_type) in enumerate([
            (False, "raw"), (True, "fixed_effects")
        ]):
            seed = 20261105 + 100 * outcome_index + model_index
            rows.extend(fit_model(
                frame, column, scale, fixed_effects, estimate_type,
                contrasts, bootstraps, seed,
            ))
            print(f"{outcome}: {estimate_type}, N={len(frame)}, bootstrap={bootstraps}")
    results = holm_adjust(pd.DataFrame(rows))
    results["significant_holm_05"] = results["p_holm"] < 0.05
    results.to_csv(OUT, index=False)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(results)} preliminary contrasts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstraps", type=int, default=1999)
    args = parser.parse_args()
    if args.bootstraps < 99:
        parser.error("Use at least 99 bootstrap replications")
    main(args.bootstraps)
