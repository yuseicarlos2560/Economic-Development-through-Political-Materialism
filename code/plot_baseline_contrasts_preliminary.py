from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

OUTCOMES = [
    ("growth_forward_5y", "A  Five-year forward growth"),
    ("disruption_forward_5y", "B  Forward disruption"),
    ("acceleration_onset_forward_8y", "C  New acceleration onset"),
]
MODEL_INFO = {
    "raw": ("Raw cell difference", "#616161", "o", 0.16),
    "fixed_effects": ("Country and year FE", "#0072B2", "D", -0.16),
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def short_label(row, family):
    domestic = {
        "none": "No domestic event",
        "turnover_or_formal_only": "Turnover/formal only",
        "power_or_apparatus_transformation": "Deep transformation",
    }[row["domestic_change"]]
    external = {
        "none": "no realignment",
        "severance": "severance",
        "entry_richer": "richer entry",
    }[row["external_realignment"]]
    if family == "primary_theory_aligned" and row["hypothesis"] == "H1":
        label = "H1: Turnover/no realignment vs no domestic/no realignment"
    elif family == "primary_theory_aligned":
        label = f"{domestic}: {external} vs no realignment"
    else:
        label = f"{domestic}: {external}"
    return f"{label}\n{row['cell_n']:,} country-years; {row['cell_countries']} countries"


def make_plot(results, family, stem, title, note):
    data = results[results["comparison_family"].eq(family)].copy()
    contrast_order = list(dict.fromkeys(data["contrast_id"]))
    y_map = {contrast: y for contrast, y in zip(contrast_order, np.arange(len(contrast_order))[::-1])}
    labels = data.drop_duplicates("contrast_id").set_index("contrast_id")
    fig, axes = plt.subplots(1, 3, figsize=(18, 10))
    fig.subplots_adjust(left=0.25, right=0.985, top=0.77, bottom=0.22, wspace=0.48)
    fig.suptitle(title, x=0.04, y=0.965, ha="left", fontsize=19, fontweight="bold")
    fig.text(
        0.04,
        0.91,
        "PRELIMINARY • Exploratory, non-causal contrasts • Start coding, current coded state, 1960–2019",
        ha="left",
        fontsize=11.5,
        color="#555555",
    )

    for panel_index, (ax, (outcome, panel_title)) in enumerate(zip(axes, OUTCOMES)):
        outcome_data = data[data["outcome"].eq(outcome)]
        for estimate_type, (model_label, color, marker, dodge) in MODEL_INFO.items():
            model = outcome_data[outcome_data["estimate_type"].eq(estimate_type)]
            for _, row in model.iterrows():
                y = y_map[row["contrast_id"]] + dodge
                significant = row["p_holm"] < 0.05
                ax.plot(
                    [row["ci95_low_pp"], row["ci95_high_pp"]],
                    [y, y],
                    color=color,
                    linewidth=1.5,
                    alpha=0.85,
                    zorder=2,
                )
                ax.scatter(
                    row["estimate_pp"],
                    y,
                    s=55,
                    marker=marker,
                    facecolor=color if significant else "white",
                    edgecolor=color,
                    linewidth=1.5,
                    zorder=3,
                )
        ax.axvline(0, color="#222222", linewidth=0.9, linestyle="--")
        ax.set_yticks(list(y_map.values()))
        ax.set_yticklabels(
            [short_label(labels.loc[c], family) for c in contrast_order]
            if panel_index == 0 else []
        )
        ax.set_ylim(-0.7, len(contrast_order) - 0.3)
        values = outcome_data[["estimate_pp", "ci95_low_pp", "ci95_high_pp"]].to_numpy()
        low, high = np.nanmin(values), np.nanmax(values)
        span = high - low
        ax.set_xlim(low - 0.08 * span, high + 0.08 * span)
        ax.set_title(panel_title, loc="left", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("Difference in percentage points", labelpad=8)
        ax.grid(axis="x", color="#E3E3E3", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", length=0)

    handles = [
        Line2D([0], [0], marker=marker, color=color, markerfacecolor=color,
               linewidth=1.5, markersize=8, label=label)
        for label, color, marker, _ in MODEL_INFO.values()
    ]
    handles.extend([
        Line2D([0], [0], marker="o", color="#555555", markerfacecolor="#555555",
               linewidth=0, markersize=8, label="Holm-adjusted p < 0.05"),
        Line2D([0], [0], marker="o", color="#555555", markerfacecolor="white",
               linewidth=0, markersize=8, label="Holm-adjusted p ≥ 0.05"),
    ])
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.60, 0.855), ncol=4, frameon=False)
    fig.text(
        0.04,
        0.05,
        note,
        ha="left",
        va="bottom",
        fontsize=9.5,
        color="#555555",
        wrap=True,
    )
    for extension in ["png", "pdf"]:
        fig.savefig(OUT / f"{stem}.{extension}", dpi=240 if extension == "png" else None)
    plt.close(fig)
    print(f"wrote paper/figures/{stem}.png and .pdf")


results = pd.read_csv(ROOT / "data_clean" / "baseline_cell_contrasts_preliminary.csv")
make_plot(
    results,
    "primary_theory_aligned",
    "baseline_contrasts_primary_preliminary",
    "Theory-aligned baseline-cell contrasts",
    "PRELIMINARY. Points are differences in percentage points; lines are 95% wild-cluster-bootstrap-t intervals clustered by country, without multiplicity adjustment to interval width. Holm p-values are adjusted across 21 primary raw or fixed-effects tests. Binary-outcome intervals can exceed logical bounds in sparse cells; this is a warning about inference, not a substantive finding.",
)
make_plot(
    results,
    "secondary_common_reference",
    "baseline_contrasts_secondary_preliminary",
    "Secondary contrasts with the no-domestic-event/no-realignment cell",
    "PRELIMINARY. Points are differences in percentage points; lines are 95% wild-cluster-bootstrap-t intervals clustered by country, without multiplicity adjustment to interval width. Holm p-values are adjusted across 24 secondary raw or fixed-effects tests. These common-reference contrasts can combine domestic and external differences; the within-row contrasts are primary.",
)
