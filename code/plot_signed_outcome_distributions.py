from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

EXTERNAL_SPECS = [
    ("none", "No realignment"),
    ("severance", "Severance"),
    ("entry_richer", "Richer entry"),
]
OUTCOME_INFO = {
    "disruption": {
        "column": "disruption_forward_5y",
        "label": "Disruption (t+1 to t+5)",
        "color": "#D55E00",
    },
    "acceleration": {
        "column": "acceleration_onset_forward_8y",
        "label": "New acceleration onset (t+1 to t+8)",
        "color": "#0072B2",
    },
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

cells = pd.read_csv(ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv")
records = []
rows = []
for external, external_label in EXTERNAL_SPECS:
    rows.append(("header", external_label))
    for outcome, info in OUTCOME_INFO.items():
        values = cells.loc[
            cells["external_realignment"].eq(external), info["column"]
        ].dropna().to_numpy()
        assert len(values) > 0 and np.isin(values, [0, 1]).all(), (external, outcome)
        record = {
            "external": external,
            "outcome": outcome,
            "values": values,
            "n": len(values),
            "count": int(values.sum()),
        }
        records.append(record)
        rows.append(("data", record))

y_positions = np.arange(len(rows))[::-1]
data_positions = [y for y, (kind, _) in zip(y_positions, rows) if kind == "data"]


def make_figure(kind):
    fig, ax = plt.subplots(figsize=(12, 7.5))
    fig.subplots_adjust(left=0.31, right=0.77, top=0.81, bottom=0.19)
    subtitle = (
        "Country-year histograms of binary forward outcomes"
        if kind == "distributions"
        else "Country-year box plots of binary forward outcomes"
    )
    fig.suptitle(
        "Forward outcomes by external category",
        x=0.06,
        y=0.96,
        ha="left",
        fontsize=18,
        fontweight="bold",
    )
    fig.text(
        0.06,
        0.90,
        f"{subtitle}; interval-start coding, current coded state, 1960–2019",
        ha="left",
        fontsize=12,
        color="#555555",
    )

    if kind == "distributions":
        for y, record in zip(data_positions, records):
            counts = np.array([
                (record["values"] == 0).sum(),
                (record["values"] == 1).sum(),
            ])
            ax.bar(
                [0, 1],
                0.7 * counts / record["n"],
                width=0.16,
                bottom=y - 0.35,
                align="center",
                color=OUTCOME_INFO[record["outcome"]]["color"],
                edgecolor="#333333",
                linewidth=0.5,
                alpha=0.7,
            )
    else:
        parts = ax.boxplot(
            [record["values"] for record in records],
            positions=data_positions,
            orientation="horizontal",
            widths=0.55,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "#111111", "linewidth": 1.5},
            whiskerprops={"color": "#444444"},
            capprops={"color": "#444444"},
        )
        for box, record in zip(parts["boxes"], records):
            box.set_facecolor(OUTCOME_INFO[record["outcome"]]["color"])
            box.set_edgecolor("#333333")
            box.set_alpha(0.7)

    for y, (row_kind, row) in zip(y_positions, rows):
        if row_kind == "data":
            ax.text(
                1.05,
                y,
                f"{row['count']:,} / {row['n']:,}",
                transform=ax.get_yaxis_transform(),
                ha="left",
                va="center",
                fontsize=11,
            )

    ax.set_yticks(y_positions)
    ax.set_yticklabels([
        row if row_kind == "header" else OUTCOME_INFO[row["outcome"]]["label"]
        for row_kind, row in rows
    ])
    for tick, (row_kind, _) in zip(ax.get_yticklabels(), rows):
        tick.set_fontweight("bold" if row_kind == "header" else "normal")
    ax.text(
        1.05,
        8.55,
        "Outcomes / valid N",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontweight="bold",
    )
    ax.set_xlim(-0.3, 1.3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["0\nNot observed", "1\nObserved"])
    ax.set_ylim(-0.7, 8.7)
    ax.set_xlabel("Forward outcome", labelpad=10, fontsize=12)
    ax.grid(axis="x", color="#E5E5E5", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    explanation = (
        "Histogram bar heights show within-category shares at 0 and 1 on a common scale."
        if kind == "distributions"
        else "Boxes, medians, and whiskers summarize binary observations, so they can coincide at 0 or 1."
    )
    fig.text(
        0.06,
        0.045,
        f"Preliminary descriptive results, not causal effects. {explanation} Disruption uses five forward years and acceleration onset uses eight; the outcomes are not mutually exclusive. Valid N varies with data coverage.",
        ha="left",
        va="bottom",
        fontsize=9.5,
        color="#555555",
        wrap=True,
    )
    return fig


for kind in ["distributions", "boxplots"]:
    figure = make_figure(kind)
    stem = f"step6_signed_outcomes_{kind}_preliminary"
    figure.savefig(OUT / f"{stem}.png", dpi=240)
    figure.savefig(OUT / f"{stem}.pdf")
    plt.close(figure)
    print(f"wrote paper/figures/{stem}.png and .pdf")
