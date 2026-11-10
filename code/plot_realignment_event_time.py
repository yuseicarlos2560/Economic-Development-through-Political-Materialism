"""Plot preliminary event-time growth trajectories by cultural plotting group."""
import argparse
from pathlib import Path
import re
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_clean"
DEFAULT_OUT = ROOT / "paper" / "figures" / "event_time"
HORIZONS = (3, 5, 8)
EVENT_TYPES = ("severance", "entry_richer")
TYPE_LABELS = {"severance": "Severance", "entry_richer": "Richer entry"}

INK = "#171717"
MUTED = "#62676C"
GRID = "#E2E5E8"
COUNTRY_LINE = "#73777C"
AVERAGE_LINE = "#000000"
BACKGROUND = "#FFFFFF"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10,
    "axes.labelcolor": INK,
    "axes.edgecolor": GRID,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "text.color": INK,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.facecolor": BACKGROUND,
})


def load_data():
    panel = pd.read_csv(
        DATA / "panel_preliminary.csv",
        usecols=["iso3", "country", "year", "gdp_pc_growth"],
    )
    events = pd.read_csv(DATA / "realignment_event_codings_preliminary.csv")
    eligible = (
        events["in_panel"]
        & events["start_year"].between(1960, 2019)
        & (
            events["type"].eq("severance")
            | (events["type"].eq("entry") & events["richer_sphere"].eq(True))
        )
    )
    events = events[eligible].copy()
    events["event_type"] = np.where(
        events["type"].eq("severance"), "severance", "entry_richer"
    )
    groups = pd.read_csv(DATA / "cultural_regions_plotting_preliminary.csv")
    if groups["iso3"].duplicated().any():
        raise ValueError("Cultural plotting groups must assign each country at most once.")
    if not groups["analysis_status"].eq("preliminary").all():
        raise ValueError("Cultural plotting groups must be labelled preliminary.")
    unmapped = sorted(set(events["iso3"]) - set(groups["iso3"]))
    if unmapped:
        raise ValueError(f"Event countries missing cultural plotting groups: {unmapped}")
    return panel, events, groups


def episode_matrix(episodes, panel, horizon):
    times = np.arange(-horizon, horizon + 1)
    series = {}
    for _, event in episodes.iterrows():
        country = panel[panel["iso3"].eq(event["iso3"])].set_index("year")
        years = int(event["start_year"]) + times
        series[event["episode_id"]] = country["gdp_pc_growth"].reindex(years).to_numpy()
    return pd.DataFrame.from_dict(series, orient="index", columns=times, dtype=float)


def clean_axis(ax, horizon):
    ax.set_facecolor(BACKGROUND)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.spines[["left", "bottom"]].set_linewidth(0.8)
    ax.tick_params(length=0, pad=5)
    ax.grid(axis="y", color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    ax.axhline(0, color=MUTED, linewidth=0.8, zorder=1)
    ax.axvline(0, color=MUTED, linewidth=0.9, linestyle=(0, (2, 3)), zorder=1)
    ticks = [-horizon, -(horizon // 2), 0, horizon // 2, horizon]
    ax.set_xticks(sorted(set(ticks)))
    ax.set_xlim(-horizon - 0.15, horizon + 0.15)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.margins(y=0.08)


def build_figure(label, episodes, panel, members=None):
    present_types = [kind for kind in EVENT_TYPES if episodes["event_type"].eq(kind).any()]
    nrows = len(present_types)
    two_rows = nrows == 2
    fig = plt.figure(figsize=(13.2, 7.8 if two_rows else 5.3), facecolor=BACKGROUND)
    grid = fig.add_gridspec(
        nrows, 3,
        left=0.075, right=0.985,
        top=0.77 if two_rows else 0.68,
        bottom=0.19 if two_rows else 0.30,
        hspace=0.48, wspace=0.10,
    )
    axes = np.empty((nrows, 3), dtype=object)
    first_ax = None
    for row, event_type in enumerate(present_types):
        typed = episodes[episodes["event_type"].eq(event_type)]
        for col, horizon in enumerate(HORIZONS):
            sharey = first_ax if col > 0 else None
            ax = fig.add_subplot(grid[row, col], sharey=sharey)
            if first_ax is None:
                first_ax = ax
            axes[row, col] = ax
            matrix = episode_matrix(typed, panel, horizon)
            counts = matrix.notna().sum(axis=0)
            for _, trajectory in matrix.iterrows():
                ax.plot(
                    matrix.columns, trajectory.to_numpy(),
                    color=COUNTRY_LINE, alpha=0.5, linewidth=0.9,
                    solid_capstyle="round", zorder=2,
                )
            ax.plot(
                matrix.columns, matrix.mean(axis=0).to_numpy(),
                color=AVERAGE_LINE, linewidth=2.25,
                solid_capstyle="round", zorder=4,
            )
            clean_axis(ax, horizon)
            if members is None:
                ax.set_ylim(-15, 15)
            ax.set_title(
                f"−{horizon} to +{horizon} years",
                loc="left", fontsize=12, fontweight="bold", pad=26,
            )
            episode_word = "episode" if len(matrix) == 1 else "episodes"
            count_label = (
                f"{len(matrix)} {episode_word} · {counts.min()}–{counts.max()} observed per event year"
                if counts.min() != counts.max()
                else f"{len(matrix)} {episode_word} · {counts.max()} observed per event year"
            )
            ax.text(
                0, 1.025, count_label, transform=ax.transAxes,
                ha="left", va="bottom", fontsize=9, color=MUTED,
            )
            if col == 0:
                ax.set_ylabel(
                    f"{TYPE_LABELS[event_type]}\nAnnual growth (%)",
                    fontsize=10.5, labelpad=10,
                )
            else:
                ax.tick_params(axis="y", labelleft=False)
            if row == nrows - 1:
                ax.set_xlabel("Years from realignment start", fontsize=10, labelpad=7)
            else:
                ax.tick_params(axis="x", labelbottom=False)

    country_count = episodes["iso3"].nunique()
    episode_word = "episode" if len(episodes) == 1 else "episodes"
    country_word = "country" if country_count == 1 else "countries"
    fig.text(
        0.055, 0.955, f"{label}: growth around realignments",
        ha="left", va="top", fontsize=19, fontweight="bold",
    )
    fig.text(
        0.055, 0.910,
        f"Annual real GDP-per-capita growth · {len(episodes)} {episode_word} in {country_count} {country_word} · event year 0",
        ha="left", va="top", fontsize=11, color=MUTED,
    )
    fig.legend(
        handles=[
            Line2D([0], [0], color=COUNTRY_LINE, alpha=0.5, linewidth=1.1,
                   label="Country-event trajectory"),
            Line2D([0], [0], color=AVERAGE_LINE, linewidth=2.25,
                   label="Average across observed episodes"),
        ],
        loc="upper right", bbox_to_anchor=(0.985, 0.905),
        frameon=False, ncol=2, fontsize=9.5, handlelength=2.4,
        columnspacing=1.8,
    )
    note = (
        "Preliminary descriptive trajectories, not causal estimates. Start-dated severance and richer-entry "
        "episodes from the 1960–2019 sample; paired transitions are retained and shown separately. Gray lines "
        "break where annual growth is missing. The black line gives equal weight to episodes observed at each "
        "event year, so its composition can change across time."
    )
    if members:
        note += (
            " Cultural groups are provisional plotting-only categories, not analytical variables. Countries: "
            + ", ".join(members) + "."
        )
    fig.text(
        0.055, 0.035, textwrap.fill(note, width=190 if members is None else 160),
        ha="left", va="bottom", fontsize=9.4 if members is None else 8.8,
        color=MUTED, linespacing=1.4,
    )
    return fig


def slugify(label):
    slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return f"{slug}_event_time_preliminary"


def main():
    parser = argparse.ArgumentParser(
        description="Plot annual growth around all eligible realignments and by cultural plotting group."
    )
    parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT,
        help="Output directory (default: paper/figures/event_time).",
    )
    args = parser.parse_args()
    panel, events, groups = load_data()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    selections = [("All countries", events, None)]
    for label, group in groups.groupby("cultural_region", sort=True):
        selected = events[events["iso3"].isin(group["iso3"])]
        selections.append((label, selected, group["country"].tolist()))

    for label, selected, members in selections:
        fig = build_figure(label, selected, panel, members)
        stem = out_dir / slugify(label)
        fig.savefig(stem.with_suffix(".pdf"), facecolor=BACKGROUND, bbox_inches="tight")
        fig.savefig(stem.with_suffix(".png"), dpi=240, facecolor=BACKGROUND, bbox_inches="tight")
        plt.close(fig)
        for path in (stem.with_suffix(".pdf"), stem.with_suffix(".png")):
            display_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
            print(f"Wrote {display_path}")


if __name__ == "__main__":
    main()
