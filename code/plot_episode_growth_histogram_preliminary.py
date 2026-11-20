from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_clean" / "step6_realignment_outcomes_preliminary.csv"
CELL_DATA = ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv"
OUT = ROOT / "paper" / "figures"
STEM = "step6_episode_growth_histogram_preliminary"
RANDOM_SEED = 20261119

BLUE = "#2878A5"
ORANGE = "#C56A1A"
GRAY = "#C7CDD2"
INK = "#17212B"
MUTED = "#58636E"
GRID = "#DDE3E8"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 11,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


def main():
    episodes = pd.read_csv(DATA)
    episodes = episodes[
        episodes["analysis_status"].eq("preliminary")
        & episodes["date_rule"].eq("start")
        & episodes["eligible_1960_2019"]
        & episodes["type"].isin(["severance", "entry"])
    ].copy()
    values = episodes["growth_forward_5y"].dropna()

    cells = pd.read_csv(CELL_DATA)
    comparison_pool = cells[
        cells["analysis_status"].eq("preliminary")
        & cells["domestic_change"].eq("none")
        & cells["external_realignment"].eq("none")
        & cells["growth_forward_5y"].notna()
    ]
    comparison = comparison_pool.sample(n=46, replace=False, random_state=RANDOM_SEED)
    comparison_values = comparison["growth_forward_5y"]

    assert len(episodes) == 46
    assert len(values) == 46
    assert episodes["type"].value_counts().to_dict() == {"severance": 23, "entry": 23}
    assert len(comparison_pool) == 2119
    assert len(comparison) == 46

    bin_width = 2.5
    all_values = pd.concat([values, comparison_values], ignore_index=True)
    lower = np.floor(all_values.min() / bin_width) * bin_width
    upper = np.ceil(all_values.max() / bin_width) * bin_width + bin_width
    bin_edges = np.arange(lower, upper + bin_width / 2, bin_width)

    comparison_counts, _ = np.histogram(comparison_values, bins=bin_edges)
    severance_counts, _ = np.histogram(
        episodes.loc[episodes["type"].eq("severance"), "growth_forward_5y"],
        bins=bin_edges,
    )
    entry_counts, _ = np.histogram(
        episodes.loc[episodes["type"].eq("entry"), "growth_forward_5y"],
        bins=bin_edges,
    )
    assert comparison_counts.sum() == 46
    assert severance_counts.sum() == 23
    assert entry_counts.sum() == 23

    fig, ax = plt.subplots(figsize=(12, 7.2))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.79, bottom=0.23)
    fig.suptitle(
        "Five-year growth after realignment and in comparison periods",
        x=0.06, y=0.95, ha="left", fontsize=20, fontweight="bold",
    )
    fig.text(
        0.06, 0.885,
        "46 realignment episodes and 46 sampled comparison periods; interval-start coding, 1960–2019",
        ha="left", fontsize=13, color=MUTED,
    )

    ax.bar(
        bin_edges[:-1], comparison_counts, width=bin_width, align="edge",
        color=GRAY, edgecolor="white", linewidth=0.8, zorder=2,
    )
    ax.bar(
        bin_edges[:-1], severance_counts, width=bin_width, align="edge",
        color=BLUE, edgecolor=BLUE, linewidth=0.8, alpha=0.5, zorder=3,
    )
    ax.bar(
        bin_edges[:-1], entry_counts, width=bin_width, align="edge",
        color=ORANGE, edgecolor=ORANGE, linewidth=0.8, alpha=0.5, zorder=3,
    )
    ax.axvline(0, color=INK, linewidth=1.0, zorder=4)

    ax.set_xlim(bin_edges[0], bin_edges[-1])
    ax.set_xticks(np.arange(np.ceil(lower / 5) * 5, upper, 5))
    ax.set_ylim(0, max(comparison_counts.max(), severance_counts.max(), entry_counts.max()) + 1.4)
    ax.set_yticks(np.arange(0, int(ax.get_ylim()[1]) + 1, 2))
    ax.set_xlabel(
        "Mean annual real GDP-per-capita growth, years t+1 to t+5 (%)",
        fontsize=13, labelpad=10,
    )
    ax.set_ylabel("Observations", fontsize=13, labelpad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, labelsize=11)

    handles = [
        Patch(facecolor=GRAY, edgecolor="none", label="No realignment / no turnover (46)"),
        Patch(facecolor=BLUE, edgecolor=BLUE, alpha=0.5, label="Severance (23)"),
        Patch(facecolor=ORANGE, edgecolor=ORANGE, alpha=0.5, label="Entry (23)"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=12)

    fig.text(
        0.06, 0.055,
        "PRELIMINARY • Descriptive, non-causal outcomes. Gray bars are a reproducible random sample of 46 no-realignment, no-domestic-event country-years "
        f"(seed {RANDOM_SEED}). Colored bars count each event type; three paired transitions appear in both series. Growth requires a complete five-year window.",
        ha="left", va="bottom", fontsize=10, color=MUTED, wrap=True,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.png", dpi=240, facecolor="white")
    fig.savefig(OUT / f"{STEM}.pdf", facecolor="white")
    plt.close(fig)
    print(f"wrote paper/figures/{STEM}.png and .pdf")


if __name__ == "__main__":
    main()
