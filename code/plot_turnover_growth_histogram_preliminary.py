from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CELL_DATA = ROOT / "data_clean" / "step6_country_year_cells_preliminary.csv"
PANEL_DATA = ROOT / "data_clean" / "panel_preliminary.csv"
OUT = ROOT / "paper" / "figures"
STEM = "step6_turnover_growth_histogram_preliminary"

BLUE = "#2878A5"
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
    cells = pd.read_csv(CELL_DATA)
    panel = pd.read_csv(
        PANEL_DATA,
        usecols=["iso3", "year", "turnover", "regime_change"],
    )
    data = cells.merge(panel, on=["iso3", "year"], how="left", validate="one_to_one")

    baseline = data[
        data["analysis_status"].eq("preliminary")
        & data["domestic_change"].eq("none")
        & data["external_realignment"].eq("none")
        & data["growth_forward_5y"].notna()
    ]["growth_forward_5y"]
    turnover = data[
        data["analysis_status"].eq("preliminary")
        & data["domestic_change"].eq("turnover_or_formal_only")
        & data["external_realignment"].eq("none")
        & data["turnover"].eq(1)
        & data["regime_change"].eq(0)
        & data["growth_forward_5y"].notna()
    ]["growth_forward_5y"]

    assert len(baseline) == 2119
    assert len(turnover) == 417

    bin_width = 2.5
    all_values = pd.concat([baseline, turnover], ignore_index=True)
    lower = np.floor(all_values.min() / bin_width) * bin_width
    upper = np.ceil(all_values.max() / bin_width) * bin_width + bin_width
    bin_edges = np.arange(lower, upper + bin_width / 2, bin_width)

    baseline_counts, _ = np.histogram(baseline, bins=bin_edges)
    turnover_counts, _ = np.histogram(turnover, bins=bin_edges)
    baseline_shares = 100 * baseline_counts / len(baseline)
    turnover_shares = 100 * turnover_counts / len(turnover)
    assert baseline_counts.sum() == len(baseline)
    assert turnover_counts.sum() == len(turnover)

    fig, ax = plt.subplots(figsize=(12, 7.2))
    fig.subplots_adjust(left=0.10, right=0.97, top=0.79, bottom=0.23)
    fig.suptitle(
        "Five-year growth with and without leader turnover",
        x=0.06, y=0.95, ha="left", fontsize=20, fontweight="bold",
    )
    fig.text(
        0.06, 0.885,
        "No realignment in either group; interval-start coding, 1960–2019",
        ha="left", fontsize=13, color=MUTED,
    )

    ax.bar(
        bin_edges[:-1], baseline_shares, width=bin_width, align="edge",
        color=GRAY, edgecolor="white", linewidth=0.8, zorder=2,
    )
    ax.bar(
        bin_edges[:-1], turnover_shares, width=bin_width, align="edge",
        color=BLUE, edgecolor=BLUE, linewidth=0.8, alpha=0.5, zorder=3,
    )
    ax.axvline(0, color=INK, linewidth=1.0, zorder=4)

    upper_y = np.ceil(max(baseline_shares.max(), turnover_shares.max()) * 1.15 / 5) * 5
    ax.set_xlim(bin_edges[0], bin_edges[-1])
    ax.set_xticks(np.arange(np.ceil(lower / 5) * 5, upper, 5))
    ax.set_ylim(0, upper_y)
    ax.set_yticks(np.arange(0, upper_y + 1, 5))
    ax.set_xlabel(
        "Mean annual real GDP-per-capita growth, years t+1 to t+5 (%)",
        fontsize=13, labelpad=10,
    )
    ax.set_ylabel("Share within group (%)", fontsize=13, labelpad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(length=0, labelsize=11)

    handles = [
        Patch(facecolor=GRAY, edgecolor="none",
              label=f"No realignment / no turnover ({len(baseline):,})"),
        Patch(facecolor=BLUE, edgecolor=BLUE, alpha=0.5,
              label=f"Turnover only / no realignment ({len(turnover):,})"),
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False, fontsize=12)

    fig.text(
        0.06, 0.055,
        "PRELIMINARY • Descriptive, non-causal outcomes. Bars show within-group percentages in common 2.5-point bins. "
        "The baseline excludes all observed domestic events. Turnover-only requires leader turnover, no formal regime change, "
        "and known absence of power/apparatus transformation. Growth requires a complete five-year forward window.",
        ha="left", va="bottom", fontsize=10, color=MUTED, wrap=True,
    )

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{STEM}.png", dpi=240, facecolor="white")
    fig.savefig(OUT / f"{STEM}.pdf", facecolor="white")
    plt.close(fig)
    print(f"wrote paper/figures/{STEM}.png and .pdf")


if __name__ == "__main__":
    main()
