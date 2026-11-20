"""Colored reference table of the 73-country panel.

One row per panel country (grouped by region, in the canonical region order of
data_clean/countries.csv), with per-country counts of coded realignment
episodes, disruption episodes, and acceleration episodes. Region cells are
color-coded; count cells are shaded in proportion to the column maximum.
Output: paper/figures/country_panel_table.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import to_rgb
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

COUNTRIES = ROOT / "data_clean" / "countries.csv"
EPISODES = ROOT / "data_clean" / "episodes.csv"
DISRUPTIONS = ROOT / "data_clean" / "disruption_episodes.csv"
ACCELERATIONS = ROOT / "data_clean" / "acceleration_episodes.csv"

REGION_ORDER = ["Latin America", "Europe", "Post-Soviet", "East Asia"]
REGION_COLORS = {
    "Latin America": "#009E73",
    "Europe": "#0072B2",
    "Post-Soviet": "#E69F00",
    "East Asia": "#CC79A7",
}
COUNT_COLORS = {
    "Realignments": "#0072B2",
    "Disruptions": "#D55E00",
    "Accelerations": "#009E73",
}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def text_on(color_hex):
    r, g, b = to_rgb(color_hex)
    return "#FFFFFF" if 0.299 * r + 0.587 * g + 0.114 * b < 0.55 else "#1A1A1A"


def shade(color_hex, intensity):
    """color at alpha=intensity over a white background"""
    r, g, b = to_rgb(color_hex)
    return (1 - intensity) + intensity * r, (1 - intensity) + intensity * g, (1 - intensity) + intensity * b


def load_table():
    countries = pd.read_csv(COUNTRIES)
    episodes = pd.read_csv(EPISODES)
    disruptions = pd.read_csv(DISRUPTIONS)
    accelerations = pd.read_csv(ACCELERATIONS)

    # drop calibration-only episodes (Egypt, Yugoslavia are not panel rows)
    episodes = episodes[episodes["iso3"].isin(countries["iso3"])]
    df = countries.merge(
        episodes["iso3"].value_counts().rename("Realignments"),
        left_on="iso3", right_index=True, how="left",
    ).merge(
        disruptions["iso3"].value_counts().rename("Disruptions"),
        left_on="iso3", right_index=True, how="left",
    ).merge(
        accelerations["iso3"].value_counts().rename("Accelerations"),
        left_on="iso3", right_index=True, how="left",
    )
    df[list(COUNT_COLORS)] = df[list(COUNT_COLORS)].fillna(0).astype(int)
    df["region"] = pd.Categorical(df["region"], categories=REGION_ORDER, ordered=True)
    return df.sort_values(["region", "country"], kind="stable")


def main():
    df = load_table()
    count_cols = list(COUNT_COLORS)
    maxima = {c: max(int(df[c].max()), 1) for c in count_cols}

    columns = ["ISO3", "Country", "Region", "Coding window"] + count_cols
    cell_text = [
        [row["iso3"], row["country"], row["region"], f"{row['coding_start']}\u2013{row['coding_end']}"]
        + [str(row[c]) for c in count_cols]
        for _, row in df.iterrows()
    ]

    n_rows = len(df)
    fig = plt.figure(figsize=(12.5, 0.235 * n_rows + 2.6))
    ax = fig.add_axes([0.025, 0.035, 0.95, 0.815])
    ax.axis("off")

    table = ax.table(
        cellText=cell_text,
        colLabels=columns,
        colWidths=[0.07, 0.24, 0.155, 0.12, 0.135, 0.135, 0.145],
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1, 1.32)

    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#C9C9C9")
        cell.set_linewidth(0.4)
        if row == 0:
            cell.set_facecolor("#333333")
            cell.set_text_props(color="#FFFFFF", fontweight="bold", fontsize=10.5)
            cell.set_height(cell.get_height() * 1.3)
            continue
        rec = df.iloc[row - 1]
        if col == 2:
            color = REGION_COLORS[str(rec["region"])]
            cell.set_facecolor(color)
            cell.set_text_props(color=text_on(color), fontsize=9.5)
        elif columns[col] in count_cols:
            value = rec[columns[col]]
            intensity = 0.10 + 0.85 * (value / maxima[columns[col]]) if value > 0 else 0.0
            cell.set_facecolor(shade(COUNT_COLORS[columns[col]], intensity))
        elif col == 1:
            cell.set_text_props(ha="left")

    legend_handles = [
        Patch(facecolor=REGION_COLORS[r], edgecolor="none",
              label=f"{r}  ({int((df['region'] == r).sum())})")
        for r in REGION_ORDER
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.905),
        ncol=4,
        frameon=False,
        fontsize=11.5,
        handlelength=1.4,
        columnspacing=1.6,
    )

    fig.text(0.5, 0.978, "The 73-country panel, 1945\u20132019",
             ha="center", fontsize=20, fontweight="bold")
    fig.text(
        0.5, 0.952,
        "One row per panel country, grouped by region \u00b7 cell shading scales with each column's maximum",
        ha="center", fontsize=11, color="#444444",
    )
    fig.text(
        0.5, 0.939,
        "Realignments = coded episodes E001\u2013E073 \u00b7 Disruptions = output collapse, sustained deceleration, or hyperinflation",
        ha="center", fontsize=10, color="#666666",
    )
    fig.text(
        0.5, 0.9265,
        "Accelerations = sustained take-offs (HPR-style filter)",
        ha="center", fontsize=10, color="#666666",
    )
    fig.text(
        0.5, 0.008,
        "Sources: data_clean/{countries, episodes, disruption_episodes, acceleration_episodes}.csv \u00b7 "
        "Egypt & Yugoslavia calibration-only \u00b7 China excluded by design",
        ha="center", fontsize=9, color="#777777",
    )

    out_png = OUT / "country_panel_table.png"
    fig.savefig(out_png, dpi=200, facecolor="white")
    print(f"wrote {out_png} ({n_rows} countries)")
    plt.close(fig)


if __name__ == "__main__":
    main()
