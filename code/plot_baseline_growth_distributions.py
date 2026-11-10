from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

CELL_SPECS = [
    ("No domestic event", "none", "none"),
    ("No domestic event", "none", "severance"),
    ("No domestic event", "none", "entry_richer"),
    ("Turnover/formal only", "turnover_or_formal_only", "none"),
    ("Turnover/formal only", "turnover_or_formal_only", "severance"),
    ("Turnover/formal only", "turnover_or_formal_only", "entry_richer"),
    ("Deep transformation", "power_or_apparatus_transformation", "none"),
    ("Deep transformation", "power_or_apparatus_transformation", "severance"),
    ("Deep transformation", "power_or_apparatus_transformation", "entry_richer"),
]
EXTERNAL_INFO = {
    "none": ("No realignment", "#777777"),
    "severance": ("Severance", "#D55E00"),
    "entry_richer": ("Richer entry", "#0072B2"),
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

cells = pd.read_csv(ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv")
records = []
for group_label, domestic, external in CELL_SPECS:
    values = cells.loc[
        cells["domestic_change"].eq(domestic)
        & cells["external_realignment"].eq(external),
        "growth_forward_5y",
    ].dropna().to_numpy()
    assert len(values) > 0, (domestic, external)
    records.append({
        "group": group_label,
        "domestic": domestic,
        "external": external,
        "values": values,
        "n": len(values),
    })

rows = []
for group_label in dict.fromkeys(record["group"] for record in records):
    rows.append(("header", group_label))
    rows.extend(("data", record) for record in records if record["group"] == group_label)
y_positions = np.arange(len(rows))[::-1]
data_records = [row for kind, row in rows if kind == "data"]
data_positions = [y for y, (kind, _) in zip(y_positions, rows) if kind == "data"]


def make_figure(kind):
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.subplots_adjust(left=0.25, right=0.86, top=0.82, bottom=0.16)
    title = "Five-year forward growth across baseline cells"
    subtitle = (
        "Country-year distributions"
        if kind == "distributions"
        else "Country-year box plots"
    )
    fig.suptitle(title, x=0.06, y=0.96, ha="left", fontsize=18, fontweight="bold")
    fig.text(
        0.06,
        0.90,
        f"{subtitle}; interval-start coding, current coded state, 1960–2019",
        ha="left",
        fontsize=12,
        color="#555555",
    )

    if kind == "distributions":
        bin_edges = np.arange(-25, 25, 2.5)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        for y, record in zip(data_positions, data_records):
            counts, _ = np.histogram(record["values"], bins=bin_edges)
            heights = 1.2 * counts / record["n"]
            ax.bar(
                bin_centers,
                heights,
                width=2.4,
                bottom=y - 0.35,
                align="center",
                color=EXTERNAL_INFO[record["external"]][1],
                edgecolor="#333333",
                linewidth=0.4,
                alpha=0.65,
            )
    else:
        parts = ax.boxplot(
            [record["values"] for record in data_records],
            positions=data_positions,
            orientation="horizontal",
            widths=0.55,
            patch_artist=True,
            showfliers=True,
            medianprops={"color": "#111111", "linewidth": 1.5},
            whiskerprops={"color": "#444444"},
            capprops={"color": "#444444"},
            flierprops={
                "marker": "o",
                "markersize": 2.5,
                "markerfacecolor": "#666666",
                "markeredgecolor": "none",
                "alpha": 0.35,
            },
        )
        for box, record in zip(parts["boxes"], data_records):
            box.set_facecolor(EXTERNAL_INFO[record["external"]][1])
            box.set_edgecolor("#333333")
            box.set_alpha(0.65)

    for y, (row_kind, row) in zip(y_positions, rows):
        if row_kind == "data":
            ax.text(
                1.04,
                y,
                f"{row['n']:,}",
                transform=ax.get_yaxis_transform(),
                ha="left",
                va="center",
                fontsize=11,
            )

    ax.axvline(0, color="#222222", linewidth=0.9, zorder=0)
    ax.axhline(7.5, color="#DDDDDD", linewidth=0.8)
    ax.axhline(3.5, color="#DDDDDD", linewidth=0.8)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([
        row if row_kind == "header" else EXTERNAL_INFO[row["external"]][0]
        for row_kind, row in rows
    ])
    for tick, (row_kind, _) in zip(ax.get_yticklabels(), rows):
        tick.set_fontweight("bold" if row_kind == "header" else "normal")
    ax.text(
        1.04,
        11.55,
        "Valid N",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontweight="bold",
    )
    ax.set_xlim(-26, 22)
    ax.set_xticks([-20, -15, -10, -5, 0, 5, 10, 15, 20])
    ax.set_ylim(-0.7, 11.7)
    ax.set_xlabel(
        "Real GDP-per-capita growth, annual mean over years t+1 to t+5 (%)",
        labelpad=10,
        fontsize=12,
    )
    ax.grid(axis="x", color="#E5E5E5", linewidth=0.7)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(axis="y", length=0)

    explanation = (
        "Histograms use common 2.5-percentage-point bins; bar heights show within-cell shares on a common scale across cells."
        if kind == "distributions"
        else "Boxes show the median and interquartile range; whiskers extend to 1.5 times the interquartile range; points are outliers."
    )
    fig.text(
        0.06,
        0.045,
        f"Preliminary descriptive results, not causal effects. {explanation} Valid N counts country-years with complete five-year growth windows.",
        ha="left",
        va="bottom",
        fontsize=9.5,
        color="#555555",
        wrap=True,
    )
    return fig


for kind in ["distributions", "boxplots"]:
    figure = make_figure(kind)
    stem = f"step6_baseline_growth_{kind}_preliminary"
    figure.savefig(OUT / f"{stem}.png", dpi=240)
    figure.savefig(OUT / f"{stem}.pdf")
    plt.close(figure)
    print(f"wrote paper/figures/{stem}.png and .pdf")
