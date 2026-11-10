from pathlib import Path
import textwrap

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK = "#17212B"
MUTED = "#5D6873"
GRID = "#DCE1E6"
NEUTRAL = "#777D84"
SEVERANCE = "#D55E00"
ENTRY = "#0072B2"
ONGOING = "#E69F00"
PAIRED = "#9AA0A6"
BACKGROUND = "#FFFFFF"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 11,
    "axes.labelcolor": INK,
    "axes.edgecolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": INK,
    "text.color": INK,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.facecolor": BACKGROUND,
})


def aggregate(frame):
    growth_n = int(frame["n_growth_5y"].sum())
    disruption_n = int(frame["n_disruption_5y"].sum())
    acceleration_n = int(frame["n_acceleration_onset_8y"].sum())
    disruption_count = int(frame["count_disruption_5y"].sum())
    acceleration_count = int(frame["count_acceleration_onset_8y"].sum())
    return {
        "n": int(frame["n_country_years"].sum()),
        "growth": np.average(frame["mean_growth_5y"], weights=frame["n_growth_5y"]),
        "disruption": 100 * disruption_count / disruption_n,
        "disruption_count": disruption_count,
        "disruption_n": disruption_n,
        "acceleration": 100 * acceleration_count / acceleration_n,
        "acceleration_count": acceleration_count,
        "acceleration_n": acceleration_n,
    }


def figure_shell(width, height, title, subtitle, note, note_width=125):
    fig = plt.figure(figsize=(width, height), facecolor=BACKGROUND)
    fig.text(0.055, 0.965, title, ha="left", va="top", fontsize=18, fontweight="bold")
    fig.text(0.055, 0.918, subtitle, ha="left", va="top", fontsize=11.5, color=MUTED)
    fig.text(
        0.055,
        0.025,
        textwrap.fill(note, width=note_width),
        ha="left",
        va="bottom",
        fontsize=9.5,
        color=MUTED,
        linespacing=1.35,
    )
    return fig


def clean_axis(ax, grid_axis="x"):
    ax.set_facecolor(BACKGROUND)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(GRID)
    ax.spines[["left", "bottom"]].set_linewidth(0.8)
    ax.tick_params(length=0, pad=6)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.7, linestyle="-", zorder=0)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", facecolor=BACKGROUND)
    fig.savefig(OUT / f"{name}.png", dpi=240, facecolor=BACKGROUND)
    plt.close(fig)
    (OUT / f"{name}.tex").unlink(missing_ok=True)
    print(f"wrote paper/figures/{name}.pdf and .png")


frequencies = pd.read_csv(ROOT / "data_clean" / "step6_cell_frequencies_preliminary.csv")
baseline = frequencies[
    (frequencies["date_rule"] == "start")
    & (frequencies["case_selection"] == "current_coded_state")
].copy()

cell_specs = [
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
external_info = {
    "none": {"label": "No realignment", "color": NEUTRAL, "marker": "o"},
    "severance": {"label": "Severance", "color": SEVERANCE, "marker": "s"},
    "entry_richer": {"label": "Richer entry", "color": ENTRY, "marker": "^"},
}
records = []
for group_label, domestic, external in cell_specs:
    row = baseline[
        (baseline["domestic_change"] == domestic)
        & (baseline["external_realignment"] == external)
    ].iloc[0]
    records.append({
        "group": group_label,
        "external": external,
        "value": row["mean_growth_5y"],
        "n": int(row["n_country_years"]),
    })

fig = figure_shell(
    10,
    7,
    "Forward growth across baseline cells",
    "Mean real GDP-per-capita growth over complete five-year forward windows, 1960–2019",
    "Descriptive means using interval-start coding, not causal effects. N is the number of country-years in each cell; realignment cells have only 2–11. "
    "Deep transformation denotes power-structure or apparatus change.",
    note_width=105,
)
ax = fig.add_axes([0.25, 0.18, 0.55, 0.66])
rows = []
for group_label in dict.fromkeys(record["group"] for record in records):
    rows.append(("header", group_label))
    rows.extend(("data", record) for record in records if record["group"] == group_label)
y_positions = np.arange(len(rows))[::-1]
data_positions = []
for y, (kind, row) in zip(y_positions, rows):
    if kind == "header":
        continue
    data_positions.append(y)
    info = external_info[row["external"]]
    value = row["value"]
    ax.hlines(y, 0, value, color=info["color"], linewidth=2.4, zorder=2)
    ax.scatter(value, y, s=85, marker=info["marker"], color=info["color"], zorder=3)
    offset = 0.22 if value >= 0 else -0.22
    ax.text(
        value + offset,
        y,
        f"{value:.2f}",
        ha="left" if value >= 0 else "right",
        va="center",
        fontsize=13,
        color=info["color"],
        fontweight="bold",
    )
    ax.text(
        1.06,
        y,
        f"{row['n']:,}",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=12,
        color=MUTED,
        fontweight="bold" if row["n"] <= 11 else "normal",
    )
ax.axvline(0, color=INK, linewidth=1.0, zorder=1)
ax.axhline(7.5, color=GRID, linewidth=1.0)
ax.axhline(3.5, color=GRID, linewidth=1.0)
ax.set_yticks(y_positions)
ax.set_yticklabels([
    row if kind == "header" else external_info[row["external"]]["label"]
    for kind, row in rows
])
for tick, (kind, _) in zip(ax.get_yticklabels(), rows):
    tick.set_fontsize(13 if kind == "header" else 12.5)
    tick.set_fontweight("bold" if kind == "header" else "normal")
ax.text(
    1.06,
    11.55,
    "Cell N",
    transform=ax.get_yaxis_transform(),
    ha="left",
    va="center",
    fontsize=12,
    color=INK,
    fontweight="bold",
)
ax.set_xlim(-7.5, 5.5)
ax.set_xticks([-6, -4, -2, 0, 2, 4])
ax.tick_params(axis="x", labelsize=12.5)
ax.tick_params(axis="y", pad=8)
ax.set_xlabel("Mean five-year forward growth (%)", labelpad=10, fontsize=13)
ax.set_ylim(-0.7, 11.7)
clean_axis(ax)
ax.spines["left"].set_visible(False)
save(fig, "step6_baseline_growth_preliminary")

fig = figure_shell(
    10,
    6.4,
    "Disruption and acceleration by external category",
    "Forward outcome rates using interval-start coding, 1960–2019",
    "Descriptive results aggregated across domestic rows, not causal effects. Disruption uses five forward years and new acceleration onset uses eight; the outcomes are not mutually exclusive. "
    "Valid denominators vary with data coverage.",
    note_width=105,
)
ax = fig.add_axes([0.30, 0.20, 0.47, 0.63])
outcome_specs = [
    ("disruption", "Disruption (5 years)", SEVERANCE, "o"),
    ("acceleration", "New acceleration onset (8 years)", ENTRY, "^"),
]
rows = []
for external, category in [("none", "No realignment"), ("severance", "Severance"), ("entry_richer", "Richer entry")]:
    result = aggregate(baseline[baseline["external_realignment"] == external])
    rows.append(("header", category))
    for measure, label, color, marker in outcome_specs:
        rows.append(("data", {
            "label": label,
            "value": result[measure],
            "count": result[f"{measure}_count"],
            "n": result[f"{measure}_n"],
            "color": color,
            "marker": marker,
        }))
y_positions = np.arange(len(rows))[::-1]
for y, (kind, row) in zip(y_positions, rows):
    if kind == "header":
        continue
    value = row["value"]
    ax.hlines(y, 0, value, color=row["color"], linewidth=2.2, zorder=2)
    ax.scatter(value, y, s=90, color=row["color"], marker=row["marker"], zorder=3)
    ax.text(
        value + 2.0,
        y,
        f"{value:.1f}%",
        ha="left",
        va="center",
        fontsize=13,
        color=row["color"],
        fontweight="bold",
    )
    ax.text(
        1.10,
        y,
        f"{row['count']:,} / {row['n']:,}",
        transform=ax.get_yaxis_transform(),
        ha="left",
        va="center",
        fontsize=12,
        color=MUTED,
        fontweight="bold" if row["n"] <= 23 else "normal",
    )
ax.axvline(0, color=INK, linewidth=1.0, zorder=1)
ax.axhline(5.5, color=GRID, linewidth=1.0)
ax.axhline(2.5, color=GRID, linewidth=1.0)
ax.set_yticks(y_positions)
ax.set_yticklabels([row if kind == "header" else row["label"] for kind, row in rows])
for tick, (kind, _) in zip(ax.get_yticklabels(), rows):
    tick.set_fontsize(13 if kind == "header" else 12)
    tick.set_fontweight("bold" if kind == "header" else "normal")
ax.text(
    1.10,
    8.55,
    "Outcomes / valid N",
    transform=ax.get_yaxis_transform(),
    ha="left",
    va="center",
    fontsize=12,
    color=INK,
    fontweight="bold",
)
ax.set_xlim(0, 100)
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.tick_params(axis="x", labelsize=12.5)
ax.tick_params(axis="y", pad=8)
ax.set_xlabel("Country-years with outcome (%)", labelpad=10, fontsize=13)
ax.set_ylim(-0.7, 8.7)
clean_axis(ax)
ax.spines["left"].set_visible(False)
save(fig, "step6_signed_outcomes_preliminary")

scenarios = [
    ("start", "current_coded_state", "Start"),
    ("midpoint", "current_coded_state", "Midpoint"),
    ("end", "current_coded_state", "End"),
    ("start", "exclude_open_cases", "Exclude open cases"),
    ("start", "exclude_systemic_shift", "Exclude systemic shifts"),
    ("start", "imposed_severance_only", "Imposed severance only"),
]
series = {"severance": [], "entry_richer": []}
for external in series:
    for date_rule, selection, scenario_label in scenarios:
        if external == "entry_richer" and selection == "imposed_severance_only":
            continue
        rows = frequencies[
            (frequencies["date_rule"] == date_rule)
            & (frequencies["case_selection"] == selection)
            & (frequencies["external_realignment"] == external)
        ]
        series[external].append((scenario_label, aggregate(rows)))
no_realignment = aggregate(baseline[baseline["external_realignment"] == "none"])

fig = figure_shell(
    10,
    7.8,
    "Sensitivity to dating and case selection",
    "Alternative scenario estimates; dashed lines mark start-date no-realignment aggregates",
    "Preliminary descriptive results, not causal effects. Alternative dates change timing and paired-event classification; exclusions remove event-years. "
    "Imposed severance only has no richer-entry bar. Sample sizes and valid denominators are reported in the sensitivity table.",
    note_width=105,
)
fig.legend(
    handles=[
        Line2D([0], [0], marker="s", color=SEVERANCE, linewidth=0, markersize=9, label="Severance"),
        Line2D([0], [0], marker="s", color=ENTRY, linewidth=0, markersize=9, label="Richer entry"),
    ],
    loc="upper center",
    bbox_to_anchor=(0.57, 0.88),
    ncol=2,
    frameon=False,
    fontsize=12,
)
row_specs = [("header", "Dating convention")]
row_specs.extend(("data", label) for _, _, label in scenarios[:3])
row_specs.append(("header", "Case selection"))
row_specs.extend(("data", label) for _, _, label in scenarios[3:])
y_positions = np.arange(len(row_specs))[::-1]
y_map = {label: y for y, (kind, label) in zip(y_positions, row_specs) if kind == "data"}
panel_specs = [
    ("growth", "A  Mean five-year forward growth (%)", (-7, 6), [-6, -4, -2, 0, 2, 4, 6], "", [0.24, 0.53, 0.70, 0.24]),
    ("acceleration", "B  New acceleration onset within eight years", (0, 80), [0, 15, 30, 45, 60, 75], "Acceleration-onset rate (%)", [0.24, 0.19, 0.70, 0.26]),
]
for measure, title, xlim, xticks, xlabel, rect in panel_specs:
    ax = fig.add_axes(rect)
    for external, dodge in [("severance", 0.17), ("entry_richer", -0.17)]:
        info = external_info[external]
        results = dict(series[external])
        for label, result in results.items():
            value = result[measure]
            y = y_map[label] + dodge
            ax.barh(y, value, height=0.28, color=info["color"], zorder=3)
            if measure == "growth":
                label_left = value < 0
                offset = 0.18
                value_label = f"{value:.2f}%"
            else:
                label_left = False
                offset = 1.5
                value_label = f"{value:.1f}%"
            ax.text(
                value - offset if label_left else value + offset,
                y,
                value_label,
                ha="right" if label_left else "left",
                va="center",
                fontsize=12,
                color=info["color"],
                fontweight="bold",
            )
    ax.axvline(0, color=INK, linewidth=1.0, zorder=1)
    ax.axvline(no_realignment[measure], color=NEUTRAL, linewidth=1.5, linestyle=(0, (4, 3)), zorder=2)
    ax.axhline(3.5, color=GRID, linewidth=1.0)
    ax.set_yticks(y_positions)
    ax.set_yticklabels([label for _, label in row_specs])
    for tick, (kind, _) in zip(ax.get_yticklabels(), row_specs):
        tick.set_fontsize(12.5)
        tick.set_fontweight("bold" if kind == "header" else "normal")
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks)
    ax.tick_params(axis="x", labelsize=12)
    ax.tick_params(axis="y", pad=8)
    ax.set_xlabel(xlabel, labelpad=8, fontsize=12.5)
    ax.set_ylim(-0.7, 7.7)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=10)
    clean_axis(ax)
    ax.spines["left"].set_visible(False)
save(fig, "step6_sensitivity_preliminary")

episodes = pd.read_csv(ROOT / "data_clean" / "step6_realignment_outcomes_preliminary.csv")
episodes = episodes[
    (episodes["date_rule"] == "start")
    & episodes["eligible_1960_2019"]
    & (
        episodes["type"].eq("severance")
        | (episodes["type"].eq("entry") & episodes["richer_sphere"])
    )
].copy()
status_specs = [
    ("signed_outcome_observed_after_event", "Expected outcome after event", INK),
    ("ongoing_outcome_at_event", "Expected outcome already active", ONGOING),
    ("paired_transition_not_clean_single_treatment", "Paired transition", PAIRED),
    ("signed_outcome_not_observed_in_window", "Expected outcome not observed", SEVERANCE),
]
categories = [
    ("severance", "Severance\n(expected: disruption)"),
    ("entry", "Richer entry\n(expected: acceleration)"),
]
counts = {
    event_type: [
        int((episodes["type"].eq(event_type) & episodes["descriptive_timing_status"].eq(status)).sum())
        for status, _, _ in status_specs
    ]
    for event_type, _ in categories
}
assert all(sum(values) == 23 for values in counts.values())

fig = figure_shell(
    10,
    5,
    "Most expected outcomes are already active at the event",
    "Interval-start coding; 23 severance episodes and 23 richer-entry episodes",
    "Numbers inside segments are episode counts. Already-active outcomes and paired transitions are not clean post-event effects; these are preliminary descriptive classifications.",
    note_width=105,
)
ax = fig.add_axes([0.24, 0.35, 0.70, 0.40])
y_positions = [1, 0]
for (event_type, category), y in zip(categories, y_positions):
    left = 0
    for count, (_, label, color) in zip(counts[event_type], status_specs):
        ax.barh(y, count, left=left, height=0.42, color=color, edgecolor=BACKGROUND, linewidth=1.0)
        if count:
            ax.text(left + count / 2, y, str(count), ha="center", va="center",
                    fontsize=13, color="white" if color in [INK, SEVERANCE] else INK,
                    fontweight="bold")
        left += count
ax.set_yticks(y_positions)
ax.set_yticklabels([item[1] for item in categories])
ax.tick_params(axis="y", labelsize=12.5, pad=10)
ax.set_xlim(0, 23)
ax.set_xticks([])
ax.set_ylim(-0.55, 1.55)
clean_axis(ax)
ax.grid(False)
ax.spines[["left", "bottom"]].set_visible(False)
fig.legend(
    handles=[Line2D([0], [0], marker="s", color=color, linewidth=0, markersize=9, label=label)
             for _, label, color in status_specs],
    loc="lower center",
    bbox_to_anchor=(0.54, 0.18),
    ncol=2,
    frameon=False,
    columnspacing=2.0,
    fontsize=11.5,
)
save(fig, "step6_timing_preliminary")
