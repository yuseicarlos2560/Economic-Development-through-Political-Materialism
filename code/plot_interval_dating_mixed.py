from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RULES = [("start", "Start"), ("midpoint", "Midpoint"), ("end", "End")]
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

episodes = pd.read_csv(ROOT / "data_clean" / "step6_realignment_outcomes_preliminary.csv")
episodes = episodes[episodes["eligible_1960_2019"]].copy()

records = []
for date_rule, date_label in DATE_RULES:
    dated = episodes[episodes["date_rule"].eq(date_rule)]
    for external in EXTERNAL_INFO:
        subset = dated[dated["external_realignment"].eq(external)]
        record = {"date_rule": date_rule, "date_label": date_label, "external": external}
        for measure, column in [
            ("growth", "growth_forward_5y"),
            ("acceleration", "acceleration_onset_forward_8y"),
        ]:
            values = subset[column].dropna().to_numpy()
            assert len(values) > 0, (date_rule, external, measure)
            record[measure] = values
        records.append(record)

fig, axes = plt.subplots(1, 2, figsize=(14, 7))
fig.subplots_adjust(left=0.14, right=0.83, top=0.73, bottom=0.24, wspace=0.22)
fig.suptitle(
    "Growth distributions and acceleration rates by interval dating",
    x=0.05,
    y=0.96,
    ha="left",
    fontsize=18,
    fontweight="bold",
)
fig.text(
    0.05,
    0.89,
    "Start, midpoint, and end coding, 1960–2019; preliminary descriptive results",
    ha="left",
    fontsize=12,
    color="#555555",
)

y_base = np.arange(len(DATE_RULES))[::-1]
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
        "Country-years with acceleration onset (%)",
    ),
]):
    panel_records = []
    positions = []
    for y, (date_rule, _) in zip(y_base, DATE_RULES):
        for external, dodge in [("severance", 0.17), ("entry_richer", -0.17)]:
            record = next(
                r for r in records
                if r["date_rule"] == date_rule and r["external"] == external
            )
            panel_records.append(record)
            positions.append(y + dodge)

    if measure == "growth":
        parts = ax.boxplot(
            [record[measure] for record in panel_records],
            positions=positions,
            orientation="horizontal",
            widths=0.28,
            patch_artist=True,
            showfliers=True,
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
    else:
        for position, record in zip(positions, panel_records):
            values = record[measure]
            rate = 100 * values.mean()
            color = EXTERNAL_INFO[record["external"]][1]
            ax.barh(position, rate, height=0.28, color=color, alpha=0.75)
            ax.text(
                rate + 1.5,
                position,
                f"{rate:.1f}%",
                ha="left",
                va="center",
                fontsize=10,
                fontweight="bold",
                color=color,
            )

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
        count_header = "Valid n"
    else:
        ax.set_xlim(0, 80)
        ax.set_xticks([0, 20, 40, 60, 80])
        count_header = "Onsets / valid n"
    ax.axvline(0, color="#333333", linewidth=0.9)
    ax.set_yticks(y_base)
    ax.set_yticklabels([label for _, label in DATE_RULES] if panel_index == 0 else [])
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
    "Growth boxes show medians and interquartile ranges; whiskers extend to 1.5 times the interquartile range and points are outliers. Acceleration bars show new-onset rates. Alternative dates shift forward windows and can change paired-event classification. No causal effects or uncertainty intervals are shown.",
    ha="left",
    va="bottom",
    fontsize=9.5,
    color="#555555",
    wrap=True,
)

for extension in ["png", "pdf"]:
    fig.savefig(
        OUT / f"step6_interval_dating_mixed_preliminary.{extension}",
        dpi=240 if extension == "png" else None,
    )
plt.close(fig)
print("wrote paper/figures/step6_interval_dating_mixed_preliminary.png and .pdf")
