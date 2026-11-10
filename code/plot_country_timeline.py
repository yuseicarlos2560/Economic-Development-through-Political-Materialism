"""Plot a preliminary country timeline of outcomes and coded political events."""
import argparse
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_clean"
DEFAULT_OUT = ROOT / "paper" / "figures" / "timelines"

INK = "#17212B"
MUTED = "#5D6873"
GRID = "#DCE1E6"
GROWTH = "#263746"
SEVERANCE = "#D55E00"
ENTRY = "#0072B2"
DEEPENING = "#56B4E9"
POWER = "#7A5195"
APPARATUS = "#00876C"
FORMAL = "#C49102"
TURNOVER = "#66717C"
DISRUPTION = "#F4A582"
ACCELERATION = "#92C5DE"
BACKGROUND = "#FFFFFF"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 10.5,
    "axes.labelcolor": INK,
    "axes.edgecolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "text.color": INK,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.facecolor": BACKGROUND,
})


def read_country_data(iso3):
    usecols = [
        "iso3", "country", "year", "gdp_pc_growth", "gdp_pc_const",
        "gdp_pc_source", "gdp_pc_seam", "turnover", "coalition_change",
        "regime_change",
    ]
    panel = pd.read_csv(DATA / "panel_preliminary.csv", usecols=usecols)
    panel = panel[panel["iso3"].eq(iso3)].sort_values("year").copy()
    if panel.empty:
        raise ValueError(f"Unknown or unavailable ISO3 code: {iso3}")

    realignments = pd.read_csv(DATA / "realignment_event_codings_preliminary.csv")
    realignments = realignments[
        realignments["iso3"].eq(iso3) & realignments["in_panel"]
    ].sort_values(["start_year", "episode_id"])
    deepening = pd.read_csv(DATA / "sphere_deepening_events.csv")
    deepening["year"] = pd.to_numeric(deepening["year"], errors="coerce")
    deepening = deepening[
        deepening["iso3"].eq(iso3) & deepening["year"].notna()
    ].sort_values(["year", "deepening_id"])

    domestic = pd.read_csv(DATA / "domestic_episodes.csv")
    domestic = domestic[
        domestic["iso3"].eq(iso3) & domestic["status"].eq("accepted")
    ].sort_values(["start_year", "episode_id"])

    disruptions = pd.read_csv(DATA / "disruption_episodes.csv")
    disruptions = disruptions[disruptions["iso3"].eq(iso3)]
    accelerations = pd.read_csv(DATA / "acceleration_episodes.csv")
    accelerations = accelerations[accelerations["iso3"].eq(iso3)]
    return panel, realignments, deepening, domestic, disruptions, accelerations


def clean_axis(ax, grid_axis="y"):
    ax.set_facecolor(BACKGROUND)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.spines[["left", "bottom"]].set_linewidth(0.8)
    ax.tick_params(length=0, pad=6)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)


def episode_band(ax, row, y, color, label=None, marker="o", label_offset=0.30):
    start = int(row["start_year"])
    end = int(row["end_year"])
    if end > start:
        ax.barh(
            y, end - start + 0.9, left=start - 0.45, height=0.32,
            color=color, alpha=0.30, edgecolor=color, linewidth=1.0, zorder=2,
        )
    event_year = int(row["event_year"]) if "event_year" in row else start
    ax.scatter(
        event_year, y, s=55, marker=marker, color=color,
        edgecolor=BACKGROUND, linewidth=0.8, zorder=4,
    )
    if label:
        midpoint = (start + end) / 2
        left, right = ax.get_xlim()
        if midpoint < left + 10:
            label_x, horizontal_alignment = start, "left"
        elif midpoint > right - 10:
            label_x, horizontal_alignment = end, "right"
        else:
            label_x, horizontal_alignment = midpoint, "center"
        ax.text(
            label_x, y + label_offset, label, ha=horizontal_alignment,
            va="center", fontsize=8.8, color=color, fontweight="bold",
        )


def build_figure(iso3, panel, realignments, deepening, domestic, disruptions, accelerations):
    country = panel["country"].iloc[0]
    first_year = int(panel["year"].min())
    last_year = int(panel["year"].max())
    fig = plt.figure(figsize=(12.5, 8.5), facecolor=BACKGROUND)
    fig.text(
        0.065, 0.965, f"{country}: growth and coded political events",
        ha="left", va="top", fontsize=19, fontweight="bold",
    )
    fig.text(
        0.065, 0.922,
        f"Annual real GDP-per-capita growth and level with preliminary event coding, {first_year}–{last_year}",
        ha="left", va="top", fontsize=11.5, color=MUTED,
    )

    grid = fig.add_gridspec(
        2, 1, height_ratios=[3.4, 1.9], hspace=0.12,
        left=0.13, right=0.90, top=0.82, bottom=0.22,
    )
    ax = fig.add_subplot(grid[0])
    level_ax = ax.twinx()
    events_ax = fig.add_subplot(grid[1], sharex=ax)
    level_ax.set_zorder(ax.get_zorder() - 1)
    ax.set_zorder(level_ax.get_zorder() + 1)
    ax.patch.set_visible(False)

    for _, episode in disruptions.iterrows():
        ax.axvspan(
            episode["start_year"] - 0.5, episode["end_year"] + 0.5,
            color=DISRUPTION, alpha=0.32, linewidth=0, zorder=0,
        )
    for _, episode in accelerations.iterrows():
        ax.axvspan(
            episode["start_year"] - 0.5, episode["end_year"] + 0.5,
            color=ACCELERATION, alpha=0.30, linewidth=0, zorder=0,
        )

    for _, event in realignments.iterrows():
        color = SEVERANCE if event["type"] == "severance" else ENTRY
        if event["end_year"] > event["start_year"]:
            ax.axvspan(
                event["start_year"] - 0.5, event["end_year"] + 0.5,
                color=color, alpha=0.09, linewidth=0, zorder=1,
            )
        ax.axvline(
            event["start_year"], color=color, linewidth=1.35,
            linestyle=(0, (4, 3)), alpha=0.85, zorder=2,
        )
    for year in deepening["year"]:
        ax.axvline(
            year, color=DEEPENING, linewidth=1.2,
            linestyle=(0, (1, 2)), alpha=0.9, zorder=2,
        )

    has_level = panel["gdp_pc_const"].notna().any()
    if has_level:
        source_change = (
            panel["gdp_pc_source"].ne(panel["gdp_pc_source"].shift())
            | panel["gdp_pc_seam"].fillna(False).astype(bool)
        )
        for _, segment in panel.groupby(source_change.cumsum()):
            level_ax.plot(
                segment["year"], segment["gdp_pc_const"], color=POWER,
                linewidth=1.35, alpha=0.75, zorder=1,
            )
        level_ax.set_ylim(bottom=0)
    level_ax.set_ylabel(
        "Real GDP per capita\n(source-specific units)", fontsize=10.5,
        color=POWER, rotation=270, labelpad=20,
    )
    level_ax.tick_params(axis="y", colors=POWER, length=0, pad=6)
    level_ax.ticklabel_format(style="plain", axis="y")
    level_ax.spines[["top", "left", "bottom"]].set_visible(False)
    level_ax.spines["right"].set_color(POWER)
    level_ax.spines["right"].set_linewidth(0.8)
    level_ax.grid(False)

    ax.axhline(0, color=MUTED, linewidth=0.9, zorder=1)
    ax.plot(
        panel["year"], panel["gdp_pc_growth"], color=GROWTH,
        linewidth=1.65, marker="o", markersize=2.8,
        markerfacecolor=GROWTH, markeredgewidth=0, zorder=3,
    )
    ax.set_ylabel("Annual growth (%)", fontsize=11.5, labelpad=9)
    ax.set_xlim(first_year - 1, last_year + 1)
    growth = panel["gdp_pc_growth"].dropna()
    if not growth.empty:
        lower = min(-2.0, np.floor(growth.min() / 2) * 2 - 1)
        upper = max(2.0, np.ceil(growth.max() / 2) * 2 + 1)
        ax.set_ylim(lower, upper)
    clean_axis(ax)
    ax.tick_params(axis="x", labelbottom=False)

    handles = [Line2D([0], [0], color=GROWTH, linewidth=1.8, marker="o",
                      markersize=4, label="Annual GDP-per-capita growth")]
    if has_level:
        handles.append(Line2D([0], [0], color=POWER, linewidth=1.5,
                              label="Real GDP per capita (right axis)"))
    if not disruptions.empty:
        handles.append(Patch(facecolor=DISRUPTION, alpha=0.45, label="Disruption episode"))
    if not accelerations.empty:
        handles.append(Patch(facecolor=ACCELERATION, alpha=0.45, label="Acceleration episode"))
    if realignments["type"].eq("severance").any():
        handles.append(Line2D([0], [0], color=SEVERANCE, linewidth=1.4,
                              linestyle=(0, (4, 3)), label="Severance start"))
    if realignments["type"].eq("entry").any():
        handles.append(Line2D([0], [0], color=ENTRY, linewidth=1.4,
                              linestyle=(0, (4, 3)), label="Entry start"))
    if not deepening.empty:
        handles.append(Line2D([0], [0], color=DEEPENING, linewidth=1.4,
                              linestyle=(0, (1, 2)), label="Within-sphere deepening"))
    ax.legend(
        handles=handles, loc="upper left", bbox_to_anchor=(0, 1.08),
        ncol=min(len(handles), 4), frameon=False, fontsize=9.8,
        handlelength=2.1, columnspacing=1.6,
    )

    lanes = {}
    if not deepening.empty:
        lanes["Sphere deepening"] = 5
    lanes.update({
        "External realignment": 4,
        "Power structure": 3,
        "Apparatus restructuring": 2,
        "Formal regime change": 1,
        "Turnover / coalition": 0,
    })
    for event_number, (_, event) in enumerate(realignments.iterrows()):
        color = SEVERANCE if event["type"] == "severance" else ENTRY
        direction = "Severance" if event["type"] == "severance" else "Entry"
        if event["type"] == "entry" and event["richer_sphere"] == True:
            direction = "Richer entry"
        label = (
            event["episode_id"] if len(realignments) > 3
            else f"{event['episode_id']} · {direction} ({event['patron']})"
        )
        episode_band(
            events_ax, event, lanes["External realignment"], color, label,
            label_offset=0.30 if event_number % 2 == 0 else -0.30,
        )
    dense_deepening = len(deepening) > 3
    for event_number, (_, event) in enumerate(deepening.iterrows()):
        year = int(event["year"])
        y = lanes["Sphere deepening"]
        events_ax.scatter(
            year, y, s=58, marker="D", facecolor=BACKGROUND,
            edgecolor=DEEPENING, linewidth=1.5, zorder=4,
        )
        label = str(year) if dense_deepening else f"{year} · {event['event']}"
        if year < first_year + 8:
            horizontal_alignment = "left"
        elif year > last_year - 8:
            horizontal_alignment = "right"
        else:
            horizontal_alignment = "center"
        events_ax.text(
            year, y + (0.30 if event_number % 2 == 0 else -0.30),
            label, ha=horizontal_alignment, va="center",
            fontsize=8.8, color=ENTRY, fontweight="bold",
        )

    deep_specs = [
        ("power_structure", "Power structure", POWER, "s"),
        ("apparatus_restructuring", "Apparatus restructuring", APPARATUS, "^"),
    ]
    for category, lane, color, marker in deep_specs:
        for _, event in domestic[domestic["category"].eq(category)].iterrows():
            episode_band(events_ax, event, lanes[lane], color, marker=marker)

    for variable, lane, color, marker, size in [
        ("regime_change", "Formal regime change", FORMAL, "D", 43),
        ("turnover", "Turnover / coalition", TURNOVER, "o", 35),
    ]:
        years = panel.loc[pd.to_numeric(panel[variable], errors="coerce").eq(1), "year"]
        events_ax.scatter(
            years, np.full(len(years), lanes[lane]), s=size, marker=marker,
            color=color, edgecolor=BACKGROUND, linewidth=0.6, zorder=4,
        )
    coalition_years = panel.loc[
        pd.to_numeric(panel["coalition_change"], errors="coerce").eq(1), "year"
    ]
    events_ax.scatter(
        coalition_years, np.full(len(coalition_years), lanes["Turnover / coalition"]),
        s=50, marker="o", facecolor=BACKGROUND, edgecolor=TURNOVER,
        linewidth=1.2, zorder=3,
    )

    events_ax.set_yticks(list(lanes.values()))
    events_ax.set_yticklabels(lanes.keys(), fontsize=10.5)
    events_ax.set_ylim(-0.65, max(lanes.values()) + 0.65)
    events_ax.set_xticks(np.arange(first_year + (5 - first_year % 5), last_year + 1, 5))
    events_ax.set_xlabel("Year", fontsize=11.5, labelpad=8)
    clean_axis(events_ax, grid_axis="x")
    events_ax.spines["left"].set_visible(False)
    events_ax.tick_params(axis="y", pad=10)

    note = (
        "Preliminary descriptive coding; event proximity does not establish causation. "
        "The GDP-per-capita level uses source-specific units and is broken at source seams; level jumps across sources are not comparable. "
        "Bands in the growth panel mark only disruption/acceleration episodes meeting the project's outcome thresholds. "
        "External and deep-domestic bands show process intervals; markers show start or principal event years. "
        "Dotted lines and open diamonds are separately logged within-sphere deepening, not new realignment episodes. "
        "In the bottom lane, filled circles are leader turnover and open circles are coalition change."
    )
    fig.text(
        0.065, 0.035, textwrap.fill(note, width=145), ha="left", va="bottom",
        fontsize=9.2, color=MUTED, linespacing=1.4,
    )
    return fig


def main():
    parser = argparse.ArgumentParser(
        description="Plot a country's growth, outcome episodes, and coded political events."
    )
    parser.add_argument(
        "-c", "--country", required=True,
        help="Three-letter ISO country code, for example ESP or esp.",
    )
    parser.add_argument(
        "--out-dir", type=Path, default=DEFAULT_OUT,
        help="Output directory (default: paper/figures/timelines).",
    )
    args = parser.parse_args()
    iso3 = args.country.strip().upper()
    try:
        data = read_country_data(iso3)
    except ValueError as error:
        parser.error(str(error))

    fig = build_figure(iso3, *data)
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"{iso3.lower()}_timeline"
    fig.savefig(stem.with_suffix(".pdf"), facecolor=BACKGROUND, bbox_inches="tight")
    fig.savefig(stem.with_suffix(".png"), dpi=240, facecolor=BACKGROUND, bbox_inches="tight")
    plt.close(fig)
    for path in [stem.with_suffix(".pdf"), stem.with_suffix(".png")]:
        display_path = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        print(f"Wrote {display_path}")


if __name__ == "__main__":
    main()
