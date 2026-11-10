from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

SCENARIOS = [
    ("exclude_open_cases", "Exclude open cases"),
    ("exclude_systemic_shift", "Exclude systemic shifts"),
    ("imposed_severance_only", "Imposed severance only"),
]
EXTERNAL_INFO = {
    "severance": ("Severance", "#1F5A7A"),
    "entry_richer": ("Richer entry", "#C7620F"),
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

cells = pd.read_csv(ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv")
panel = pd.read_csv(
    ROOT / "data_clean" / "panel_preliminary.csv",
    usecols=[
        "iso3",
        "year",
        "realignment_open_review",
        "systemic_shift_flag",
        "imposed_severance",
    ],
)
cells = cells.merge(panel, on=["iso3", "year"], how="left", validate="one_to_one")

records = []
for selection, scenario_label in SCENARIOS:
    if selection == "exclude_open_cases":
        scenario = cells[cells["realignment_open_review"].ne(1)]
    elif selection == "exclude_systemic_shift":
        scenario = cells[cells["systemic_shift_flag"].ne(1)]
    else:
        scenario = cells[
            cells["external_realignment"].ne("severance")
            | cells["imposed_severance"].eq(1)
        ]
    for external in EXTERNAL_INFO:
        if external == "entry_richer" and selection == "imposed_severance_only":
            continue
        subset = scenario[scenario["external_realignment"].eq(external)]
        record = {"selection": selection, "scenario": scenario_label, "external": external}
        for measure, column in [
            ("growth", "growth_forward_5y"),
            ("acceleration", "acceleration_onset_forward_8y"),
        ]:
            values = subset[column].dropna().to_numpy()
            assert len(values) > 0, (selection, external, measure)
            record[measure] = values
        records.append(record)

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.subplots_adjust(left=0.18, right=0.83, top=0.73, bottom=0.24, wspace=0.25)
fig.suptitle(
    "Outcome distributions by case-selection scenario",
    x=0.05,
    y=0.96,
    ha="left",
    fontsize=18,
    fontweight="bold",
)
fig.text(
    0.05,
    0.89,
    "Interval-start coding, 1960–2019; preliminary descriptive results",
    ha="left",
    fontsize=12,
    color="#555555",
)

y_base = np.arange(len(SCENARIOS))[::-1]
for panel_index, (ax, measure, title, xlabel) in enumerate([
    (
        axes[0],
        "growth",
        "A  Five-year forward growth",
        "Real GDP-per-capita growth, annual mean over t+1 to t+5 (%)",
    ),
    (
        axes[1],
        "acceleration",
        "B  New acceleration onset within eight years",
        "Forward outcome (0 = no new onset; 1 = new onset)",
    ),
]):
    panel_records = []
    positions = []
    for y, (selection, _) in zip(y_base, SCENARIOS):
        for external, dodge in [("severance", 0.17), ("entry_richer", -0.17)]:
            matches = [r for r in records if r["selection"] == selection and r["external"] == external]
            if matches:
                panel_records.append(matches[0])
                positions.append(y + dodge)

    parts = ax.boxplot(
        [record[measure] for record in panel_records],
        positions=positions,
        orientation="horizontal",
        widths=0.28,
        patch_artist=True,
        showfliers=measure == "growth",
        medianprops={"color": "#111111", "linewidth": 1.4},
        whiskerprops={"color": "#444444"},
        capprops={"color": "#444444"},
        flierprops={
            "marker": "o",
            "markersize": 3,
            "markerfacecolor": "#666666",
            "markeredgecolor": "none",
            "alpha": 0.45,
        },
    )
    for box, record in zip(parts["boxes"], panel_records):
        box.set_facecolor(EXTERNAL_INFO[record["external"]][1])
        box.set_edgecolor("#333333")
        box.set_alpha(0.75)

    for position, record in zip(positions, panel_records):
        values = record[measure]
        annotation = (
            f"{len(values):,}"
            if measure == "growth"
            else f"{int(values.sum()):,} / {len(values):,}"
        )
        ax.text(
            1.04,
            position,
            annotation,
            transform=ax.get_yaxis_transform(),
            ha="left",
            va="center",
            fontsize=10,
        )

    if measure == "growth":
        ax.set_xlim(-23, 14)
        ax.set_xticks([-20, -15, -10, -5, 0, 5, 10])
        ax.axvline(0, color="#333333", linewidth=0.9)
        count_header = "Valid n"
    else:
        ax.set_xlim(-0.3, 1.3)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["0\nNo onset", "1\nOnset"])
        count_header = "Onsets / valid n"

    ax.set_yticks(y_base)
    ax.set_yticklabels([label for _, label in SCENARIOS] if panel_index == 0 else [])
    ax.set_ylim(-0.65, 2.75)
    ax.set_xlabel(xlabel, labelpad=9)
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=10)
    ax.text(
        1.04,
        2.65,
        count_header,
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
    )
    ax.grid(axis="x", color="#E2E2E2", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

fig.legend(
    handles=[Patch(facecolor=color, alpha=0.75, label=label) for label, color in EXTERNAL_INFO.values()],
    loc="upper center",
    bbox_to_anchor=(0.54, 0.82),
    ncol=2,
    frameon=False,
    fontsize=11,
)
fig.text(
    0.05,
    0.045,
    "Growth boxes show medians and interquartile ranges; whiskers extend to 1.5 times the interquartile range and points are outliers. Acceleration boxes summarize binary observations and can collapse at 0 or 1. Excluded event-years are removed, not recoded as no realignment. No causal effects or uncertainty intervals are shown.",
    ha="left",
    va="bottom",
    fontsize=9.5,
    color="#555555",
    wrap=True,
)

for extension in ["png", "pdf"]:
    fig.savefig(
        OUT / f"step6_case_selection_boxplot_preliminary.{extension}",
        dpi=240 if extension == "png" else None,
    )
plt.close(fig)
print("wrote paper/figures/step6_case_selection_boxplot_preliminary.png and .pdf")
