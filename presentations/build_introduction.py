"""Build and validate Slides 1–16 under SLIDE_BUILD_PROTOCOL.md."""
from pathlib import Path
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "presentations"
DATA = ROOT / "data_clean"
ASSETS = HERE / "assets"
OUTPUT = HERE / "thesis_introduction.pptx"
PUZZLE_FIGURE = ASSETS / "introduction_puzzle.png"

FONT = "Arial"
WHITE = "FFFFFF"
OFFWHITE = "F5F6F8"
INK = "17212B"
MUTED = "58636E"
FAINT = "89939D"
GRID = "DDE3E8"
NAVY = "102A43"
BLUE = "2878A5"
BLUE_LIGHT = "E8F1F6"
ORANGE = "C56A1A"
ORANGE_LIGHT = "FAEEE2"
GRAY_LIGHT = "ECEFF2"
CAVEAT = "Descriptive, non-causal, preliminary"
SLIDE_W = 13.333
SLIDE_H = 7.5


def rgb(value):
    return RGBColor.from_string(value)


def add_shape(slide, x, y, w, h, fill, rounded=True, line=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(0.8)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, x, y, w, h, text, size=20, color=INK, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, italic=False,
             line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = 0
    frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    paragraph.line_spacing = line_spacing
    paragraph.space_after = Pt(0)
    paragraph.font.name = FONT
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.italic = italic
    paragraph.font.color.rgb = rgb(color)
    return box


def add_line(slide, x, y, w, color=GRID):
    return add_shape(slide, x, y, w, 0.015, color, rounded=False)


def add_header(slide, number, section, title):
    add_text(slide, 0.68, 0.28, 10.8, 0.34, section.upper(), 20, BLUE, True)
    add_text(slide, 12.05, 0.28, 0.60, 0.34, str(number), 20, MUTED, True,
             align=PP_ALIGN.RIGHT)
    title_size = 30 if len(title) <= 65 else 28
    add_text(slide, 0.68, 0.72, 12.0, 0.80, title, title_size, INK, True,
             valign=MSO_ANCHOR.MIDDLE)
    add_line(slide, 0.68, 1.55, 11.97)


def add_footer(slide, source):
    add_line(slide, 0.68, 6.75, 11.97)
    add_text(slide, 0.68, 6.91, 11.97, 0.35, source, 20, MUTED)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def new_slide(prs, background=WHITE):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(background)
    return slide


def weighted_mean(frame, value, weight):
    valid = frame[value].notna() & frame[weight].notna()
    return np.average(frame.loc[valid, value], weights=frame.loc[valid, weight])


def verify_source_numbers():
    cells = pd.read_csv(DATA / "step6_cell_frequencies_preliminary.csv")
    cells = cells[
        cells["analysis_status"].eq("preliminary")
        & cells["date_rule"].eq("start")
        & cells["case_selection"].eq("current_coded_state")
    ]
    results = {}
    for category in ["severance", "entry_richer", "none"]:
        group = cells[cells["external_realignment"].eq(category)]
        results[category] = {
            "n": int(group["n_country_years"].sum()),
            "growth": weighted_mean(group, "mean_growth_5y", "n_growth_5y"),
            "growth_n": int(group["n_growth_5y"].sum()),
            "disruption_count": int(group["count_disruption_5y"].sum()),
            "disruption_n": int(group["n_disruption_5y"].sum()),
            "acceleration_count": int(group["count_acceleration_onset_8y"].sum()),
            "acceleration_n": int(group["n_acceleration_onset_8y"].sum()),
        }
    assert results["severance"]["n"] == 20
    assert results["entry_richer"]["n"] == 20
    assert results["none"]["n"] == 4335
    assert np.isclose(results["severance"]["growth"], -3.28, atol=0.005)
    assert np.isclose(results["entry_richer"]["growth"], 3.43, atol=0.005)
    assert np.isclose(results["none"]["growth"], 2.23, atol=0.005)
    assert results["severance"]["disruption_count"] == 15
    assert results["severance"]["disruption_n"] == 20
    assert results["entry_richer"]["acceleration_count"] == 12
    assert results["entry_richer"]["acceleration_n"] == 20

    baseline_h1 = cells[
        cells["external_realignment"].eq("none")
        & cells["domestic_change"].eq("none")
    ].iloc[0]
    results["h1"] = {
        "none": {
            "growth": float(baseline_h1["mean_growth_5y"]),
            "growth_n": int(baseline_h1["n_growth_5y"]),
            "disruption": float(baseline_h1["rate_disruption_5y"] * 100),
            "disruption_n": int(baseline_h1["n_disruption_5y"]),
            "acceleration": float(baseline_h1["rate_acceleration_onset_8y"] * 100),
            "acceleration_n": int(baseline_h1["n_acceleration_onset_8y"]),
        }
    }

    country_cells = pd.read_csv(DATA / "step6_country_year_cells_preliminary.csv")
    panel = pd.read_csv(
        DATA / "panel_preliminary.csv",
        usecols=["iso3", "year", "turnover", "regime_change"],
    )
    country_cells = country_cells.merge(
        panel, on=["iso3", "year"], how="left", validate="one_to_one",
    )
    turnover = country_cells[
        country_cells["analysis_status"].eq("preliminary")
        & country_cells["domestic_change"].eq("turnover_or_formal_only")
        & country_cells["external_realignment"].eq("none")
        & country_cells["turnover"].eq(1)
        & country_cells["regime_change"].eq(0)
    ]
    growth = turnover["growth_forward_5y"].dropna()
    disruption = turnover["disruption_forward_5y"].dropna()
    acceleration = turnover["acceleration_onset_forward_8y"].dropna()
    results["h1"]["turnover_only"] = {
        "growth": float(growth.mean()),
        "growth_n": len(growth),
        "disruption": float(disruption.mean() * 100),
        "disruption_n": len(disruption),
        "acceleration": float(acceleration.mean() * 100),
        "acceleration_n": len(acceleration),
    }
    assert results["h1"]["turnover_only"]["growth_n"] == 417
    assert results["h1"]["turnover_only"]["disruption_n"] == 417
    assert results["h1"]["turnover_only"]["acceleration_n"] == 390
    assert np.isclose(results["h1"]["none"]["growth"], 2.19, atol=0.005)
    assert np.isclose(results["h1"]["turnover_only"]["growth"], 2.41, atol=0.005)
    assert np.isclose(results["h1"]["none"]["disruption"], 22.8, atol=0.05)
    assert np.isclose(results["h1"]["turnover_only"]["disruption"], 17.7, atol=0.05)
    assert np.isclose(results["h1"]["none"]["acceleration"], 13.1, atol=0.05)
    assert np.isclose(results["h1"]["turnover_only"]["acceleration"], 15.1, atol=0.05)
    return results


def country_panel(iso3, start, end):
    columns = [
        "iso3", "year", "gdp_pc_growth", "turnover", "regime_change",
        "power_structure", "apparatus_restructuring", "severance", "entry",
        "disruption_forward_5y",
    ]
    available = pd.read_csv(DATA / "panel_preliminary.csv", nrows=0).columns
    columns = [c for c in columns if c in available]
    panel = pd.read_csv(DATA / "panel_preliminary.csv", usecols=columns)
    selected = panel[
        panel["iso3"].eq(iso3) & panel["year"].between(start, end)
    ].sort_values("year")
    if selected.empty or selected["gdp_pc_growth"].isna().any():
        raise ValueError(f"Incomplete puzzle series for {iso3}")
    return selected


def build_puzzle_figure():
    cuba = country_panel("CUB", 1984, 1995)
    colombia = country_panel("COL", 1997, 2008)
    colombia_2002 = colombia[colombia["year"].eq(2002)].iloc[0]
    assert colombia_2002["turnover"] == 1
    assert colombia_2002["power_structure"] == 0
    assert colombia_2002["apparatus_restructuring"] == 0
    assert colombia_2002["severance"] == 0
    assert colombia_2002["entry"] == 0

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "text.color": f"#{INK}",
        "axes.labelcolor": f"#{INK}",
        "axes.edgecolor": f"#{GRID}",
        "xtick.color": f"#{MUTED}",
        "ytick.color": f"#{MUTED}",
        "savefig.facecolor": "white",
    })
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 4.55), sharey=True)
    fig.subplots_adjust(left=0.13, right=0.985, top=0.78, bottom=0.19, wspace=0.13)
    specifications = [
        (axes[0], cuba, "Cuba: Soviet severance", "1989–91\nSoviet withdrawal", BLUE),
        (axes[1], colombia, "Colombia: government turnover", "2002\nTurnover", MUTED),
    ]
    for index, (ax, frame, title, event_label, accent) in enumerate(specifications):
        if index == 0:
            ax.axvspan(1989, 1991, color=f"#{accent}", alpha=0.10, linewidth=0)
            ax.axvline(1989, color=f"#{accent}", linewidth=2.0,
                       linestyle=(0, (4, 3)))
            ax.text(1990, 14.8, event_label, ha="center", va="top",
                    fontsize=20, color=f"#{accent}", fontweight="bold",
                    linespacing=1.15)
        else:
            ax.axvline(2002, color=f"#{accent}", linewidth=2.0,
                       linestyle=(0, (2, 2)))
            ax.text(2002.2, 14.8, event_label, ha="left", va="top",
                    fontsize=20, color=f"#{accent}", fontweight="bold",
                    linespacing=1.15)
        ax.axhline(0, color=f"#{FAINT}", linewidth=1.0, zorder=1)
        ax.plot(
            frame["year"], frame["gdp_pc_growth"],
            color=f"#{INK}" if index == 0 else f"#{MUTED}",
            linewidth=2.8 if index == 0 else 2.5,
            linestyle="-" if index == 0 else (0, (5, 2)),
            marker="o" if index == 0 else "s", markersize=5.5,
            markeredgewidth=0, zorder=3,
        )
        ax.set_ylim(-21, 17)
        ax.set_yticks([-20, -10, 0, 10])
        ax.set_xlim(frame["year"].min() - 0.5, frame["year"].max() + 0.5)
        ax.set_xticks(np.arange(frame["year"].min() + 1, frame["year"].max() + 1, 4))
        ax.set_title(title, loc="left", fontsize=23, fontweight="bold", pad=18,
                     color=f"#{accent}")
        ax.tick_params(length=0, labelsize=20, pad=6)
        ax.grid(axis="y", color=f"#{GRID}", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(f"#{GRID}")
        ax.set_xlabel("Year", fontsize=20, labelpad=8)
    axes[0].set_ylabel("Annual growth (%)", fontsize=20, labelpad=10)
    fig.savefig(PUZZLE_FIGURE, dpi=200, facecolor="white")
    plt.close(fig)


def build_model_formula():
    fig = plt.figure(figsize=(12.0, 1.15), facecolor="none")
    fig.text(
        0.5, 0.70,
        r"$g_{it} = \alpha_i + \lambda_t + \beta_1\,\mathrm{Severance}_{it}"
        r" + \beta_2\,\mathrm{Entry}_{it} + \beta_3\,\mathrm{Turnover}_{it}$",
        ha="center", va="center", fontsize=27, color=f"#{INK}",
    )
    fig.text(
        0.5, 0.25,
        r"$\quad + \beta_4\,\mathrm{RegimeChange}_{it}"
        r" + \beta_5\,\mathrm{PowerStructure}_{it}"
        r" + \gamma'X_{it} + \varepsilon_{it}$",
        ha="center", va="center", fontsize=27, color=f"#{INK}",
    )
    fig.savefig(ASSETS / "empirical_model.png", dpi=220, transparent=True)
    plt.close(fig)


def build_results_figures(results):
    with plt.rc_context({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "text.color": f"#{INK}",
        "axes.labelcolor": f"#{INK}",
        "xtick.color": f"#{MUTED}",
        "ytick.color": f"#{MUTED}",
    }):
        categories = ["severance", "entry_richer", "none"]
        labels = [
            f"Severance\n{results['severance']['n']} country-years",
            f"Richer entry\n{results['entry_richer']['n']} country-years",
            f"No realignment\n{results['none']['n']:,} country-years",
        ]
        values = [results[category]["growth"] for category in categories]
        colors = [f"#{BLUE}", f"#{ORANGE}", f"#{FAINT}"]
        fig, ax = plt.subplots(figsize=(11.7, 3.45))
        fig.subplots_adjust(left=0.09, right=0.99, top=0.94, bottom=0.25)
        bars = ax.bar(np.arange(3), values, width=0.58, color=colors)
        ax.axhline(0, color=f"#{MUTED}", linewidth=1.1)
        ax.set_ylim(-5, 5)
        ax.set_yticks([-4, -2, 0, 2, 4])
        ax.set_ylabel("Mean annual growth (%)", fontsize=20, labelpad=8)
        ax.set_xticks(np.arange(3), labels, fontsize=20)
        ax.tick_params(axis="y", labelsize=20, length=0, pad=5)
        ax.tick_params(axis="x", length=0, pad=8)
        ax.grid(axis="y", color=f"#{GRID}", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        for bar, value in zip(bars, values):
            label = f"{value:+.2f}%"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + (0.25 if value >= 0 else -0.25),
                label, ha="center", va="bottom" if value >= 0 else "top",
                fontsize=25, fontweight="bold",
                color=bar.get_facecolor(),
            )
        fig.savefig(ASSETS / "results_growth.png", dpi=220, facecolor="white")
        plt.close(fig)

        outcomes = [
            ("Disruption after severance\nwithin five years",
             results["severance"]["disruption_count"] / results["severance"]["disruption_n"] * 100,
             results["severance"]["disruption_count"], results["severance"]["disruption_n"], BLUE),
            ("New acceleration after richer entry\nwithin eight years",
             results["entry_richer"]["acceleration_count"] / results["entry_richer"]["acceleration_n"] * 100,
             results["entry_richer"]["acceleration_count"], results["entry_richer"]["acceleration_n"], ORANGE),
        ]
        fig, ax = plt.subplots(figsize=(11.7, 3.20))
        fig.subplots_adjust(left=0.40, right=0.97, top=0.93, bottom=0.25)
        y = np.arange(2)[::-1]
        rates = [outcome[1] for outcome in outcomes]
        bars = ax.barh(y, rates, height=0.46,
                       color=[f"#{outcome[4]}" for outcome in outcomes])
        ax.set_yticks(y, [outcome[0] for outcome in outcomes], fontsize=20)
        ax.set_xlim(0, 112)
        ax.set_ylim(-0.65, 1.65)
        ax.set_xticks([0, 25, 50, 75, 100])
        ax.set_xlabel("Country-years with outcome (%)", fontsize=20, labelpad=8)
        ax.tick_params(axis="x", labelsize=20, length=0, pad=5)
        ax.tick_params(axis="y", length=0, pad=10)
        ax.grid(axis="x", color=f"#{GRID}", linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        for bar, (_, rate, count, denominator, color) in zip(bars, outcomes):
            ax.text(rate + 2, bar.get_y() + bar.get_height() / 2 + 0.10,
                    f"{rate:.0f}%", va="center", ha="left", fontsize=28,
                    fontweight="bold", color=f"#{color}")
            ax.text(rate + 2, bar.get_y() + bar.get_height() / 2 - 0.19,
                    f"{count} / {denominator}", va="center", ha="left",
                    fontsize=20, color=f"#{MUTED}")
        fig.savefig(ASSETS / "results_discontinuities.png", dpi=220, facecolor="white")
        plt.close(fig)

        h1 = results["h1"]
        fig, axes = plt.subplots(1, 2, figsize=(11.7, 3.35))
        fig.subplots_adjust(left=0.07, right=0.99, top=0.80, bottom=0.29, wspace=0.28)
        panels = [
            (axes[0], "growth", "growth_n", "Five-year forward growth (%)", 3.2, [0, 1, 2, 3]),
            (axes[1], "disruption", "disruption_n", "Disruption within five years (%)", 30, [0, 10, 20, 30]),
        ]
        for ax, metric, n_key, title, upper, ticks in panels:
            values = [h1["none"][metric], h1["turnover_only"][metric]]
            labels = [
                f"No domestic\nevent\n{h1['none'][n_key]:,} valid N",
                f"Turnover\nonly\n{h1['turnover_only'][n_key]:,} valid N",
            ]
            bars = ax.bar(np.arange(2), values, width=0.52,
                          color=[f"#{FAINT}", f"#{BLUE}"])
            ax.set_title(title, fontsize=21, fontweight="bold", pad=12)
            ax.set_ylim(0, upper)
            ax.set_yticks(ticks)
            ax.set_xticks(np.arange(2), labels, fontsize=20)
            ax.tick_params(axis="y", labelsize=20, length=0)
            ax.tick_params(axis="x", length=0, pad=8)
            ax.grid(axis="y", color=f"#{GRID}", linewidth=0.8)
            ax.set_axisbelow(True)
            ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width() / 2, value + upper * 0.025,
                        f"{value:.1f}%" if metric == "disruption" else f"{value:.2f}%",
                        ha="center", va="bottom", fontsize=24, fontweight="bold",
                        color=bar.get_facecolor())
        fig.savefig(ASSETS / "results_h1.png", dpi=220, facecolor="white")
        plt.close(fig)


def build_deck(results):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    prs.core_properties.title = "Economic Development, a Political Materialism perspective"
    prs.core_properties.subject = "Thesis proposal presentation — Slides 1–16"
    prs.core_properties.author = "Carlos Gustavo Salas Flores"
    prs.core_properties.keywords = "political materialism, economic development, realignment"

    slide = new_slide(prs, NAVY)
    add_shape(slide, 0, 0, 0.14, 7.5, BLUE, rounded=False)
    add_text(slide, 0.85, 1.45, 11.6, 1.75,
             "Economic Development,\na Political Materialism perspective",
             40, WHITE, True, valign=MSO_ANCHOR.MIDDLE, line_spacing=0.95)
    add_line(slide, 0.85, 3.55, 3.0, "5E92B2")
    add_text(slide, 0.85, 4.05, 10.8, 0.45,
             "Carlos Gustavo Salas Flores", 24, WHITE, True)
    add_text(slide, 0.85, 4.72, 10.8, 0.40,
             "Beijing Normal University", 22, "D6E1EA")
    add_text(slide, 0.85, 5.32, 10.8, 0.40, "Oct 2026", 22, "D6E1EA")
    add_notes(slide, """
[0:00–0:40]
Thank you. I want to start with two political episodes. Cuba lost Soviet support between 1989 and 1991 without a corresponding transformation of its domestic power structure. Colombia changed president in 2002 without a coded change in external alignment or deep political power. Their economic trajectories look very different. That contrast introduces the question of this thesis: when does political change coincide with a major break in economic performance?
""")

    slide = new_slide(prs)
    add_header(slide, 2, "Motivation",
               "Cuba’s economy collapsed after losing Soviet support; Colombia’s continued after a presidential election")
    slide.shapes.add_picture(
        str(PUZZLE_FIGURE), Inches(0.68), Inches(1.72),
        width=Inches(11.97), height=Inches(4.54),
    )
    add_footer(slide,
               "WDI real GDP p.c. growth; panel_preliminary.csv; CUB_1989.md; Cases.md.")
    add_notes(slide, """
[0:40–2:30]
The left panel shows annual real GDP-per-capita growth in Cuba. Growth was already weak before 1989, so I do not date the whole decline to severance. The collapse proper followed the withdrawal of Soviet subsidies, trade privileges, and institutional ties: output contracted sharply from 1990 through 1993. The domestic ruler, ruling coalition, power structure, and state apparatus remained intact.

The right panel shows Colombia around the 2002 government turnover. The current coding records no realignment, power-structure transformation, or apparatus restructuring. Growth continued after the turnover, and no disruption is recorded in the following five years. The earlier 1999 recession remains visible; I am not claiming that Colombia was crisis-free.

These two cases illustrate the puzzle rather than identify an effect. Similar attention to a political event can conceal very different changes in a state's material position. The thesis separates those changes explicitly.
""")

    slide = new_slide(prs)
    add_header(slide, 3, "Research question", "The study separates political change at home and abroad")
    add_shape(slide, 0.85, 2.02, 0.10, 2.65, BLUE, rounded=False)
    add_text(slide, 1.20, 2.00, 10.95, 2.70,
             "Which changes in a country's political and international situation produce major economic discontinuities?",
             32, INK, False, valign=MSO_ANCHOR.MIDDLE, line_spacing=1.08)
    add_text(slide, 1.20, 5.10, 10.95, 0.95,
             "The project separates rulers, effective political power, and external alignment using observable events.",
             22, MUTED, line_spacing=1.08)
    add_footer(slide, "Source: proposal_thesis.tex, Research Question and Contribution.")
    add_notes(slide, """
[2:30–3:30]
Here is the research question. A major economic discontinuity is a sharp and sustained break in the prior trajectory, either downward or upward. The question is deliberately broader than whether democracy raises growth. It asks which political and international changes coincide with these breaks.

The measurement issue is part of the question. Regime change can mean a new ruler, new formal rules, a transformation of effective power, or a restructuring of the state. External realignment is a separate event. The framework codes these categories from observable records so that their economic associations can be compared.
""")

    slide = new_slide(prs)
    add_header(slide, 4, "Findings preview",
               "Early results show lower growth after severance and higher growth after richer entry")
    add_text(slide, 0.72, 1.74, 11.90, 0.42,
             "Mean annual real GDP-per-capita growth, years 1–5 after interval start",
             22, MUTED)
    cards = [
        (2.35, BLUE_LIGHT, BLUE, "1", "Severance",
         f"{results['severance']['growth']:.2f}%", "20 country-years"),
        (3.55, ORANGE_LIGHT, ORANGE, "2", "Richer entry",
         f"+{results['entry_richer']['growth']:.2f}%", "20 country-years"),
        (4.75, GRAY_LIGHT, INK, "3", "No realignment",
         f"+{results['none']['growth']:.2f}%", "4,335 country-years"),
    ]
    for y, fill, accent, number, label, value, sample in cards:
        add_shape(slide, 0.72, y, 11.90, 0.98, fill)
        add_text(slide, 0.98, y + 0.23, 0.40, 0.40, number, 22, accent, True)
        add_text(slide, 1.62, y + 0.21, 3.20, 0.44, label, 24, INK, True)
        add_text(slide, 5.18, y + 0.10, 2.50, 0.62, value, 36, accent, True,
                 align=PP_ALIGN.RIGHT)
        add_text(slide, 8.15, y + 0.26, 3.95, 0.40, sample, 20, MUTED,
                 align=PP_ALIGN.RIGHT)
    add_text(slide, 0.72, 6.10, 11.90, 0.42, CAVEAT, 20, BLUE, True,
             align=PP_ALIGN.CENTER)
    add_footer(slide,
               "Source: step6_cell_frequencies_preliminary.csv; interval-start coding, 1960–2019.")
    add_notes(slide, """
[3:30–4:30]
The preliminary results already give the project a clear direction. Under interval-start coding, mean annual real GDP-per-capita growth over the next five years is minus 3.28 percent across 20 bare-severance country-years. It is plus 3.43 percent across 20 richer-entry country-years. The no-realignment average is plus 2.23 percent.

These are descriptive, non-causal, preliminary associations. The event cells are small, forward windows overlap, and the estimates are sensitive to dating and case selection. Later slides will show the underlying distributions and the cases that do not fit. The next section locates the contribution in the literature before I present the framework and design.
""")

    slide = new_slide(prs)
    add_header(slide, 5, "Roadmap", "Agenda")
    sections = [
        "Literature",
        "Framework & Hypotheses",
        "Data & Measurement",
        "Empirical Design",
        "Results",
        "Robustness & Limitations",
        "Conclusion",
    ]
    for index, section in enumerate(sections, start=1):
        y = 1.82 + (index - 1) * 0.66
        add_text(slide, 0.90, y, 0.62, 0.40, f"{index:02d}", 22, BLUE, True)
        add_text(slide, 1.78, y - 0.01, 10.45, 0.43, section, 24, INK,
                 bold=index == 1)
        if index < len(sections):
            add_line(slide, 1.78, y + 0.49, 10.45)
    add_notes(slide, """
[4:30–4:50]
The rest of the presentation follows a standard sequence. I first locate the project in the literature, then present the framework and hypotheses, the data and measurement rules, and the empirical design. I then turn to the preliminary results, their limitations, and the contribution and next steps.
""")

    slide = new_slide(prs)
    add_header(slide, 6, "Literature", "Three issues motivate the research design")
    literature = [
        (
            1.70, "01", "Political measurement",
            "Polity scores contain measurement error that can distort inference. Recent backsliding trends also differ between expert-coded and objective indicators.",
            "Treier & Jackman 2008; Little & Meng 2024",
        ),
        (
            3.22, "02", "Institutional classifications",
            "Inclusive/extractive categories rely partly on property rights and expropriation outcomes. An unspecified time horizon also makes delayed failure difficult to falsify.",
            "Acemoglu et al. 2001, 2005; Acemoglu & Robinson 2012",
        ),
        (
            4.74, "03", "Democracy and growth",
            "Existing estimates do not separately identify government turnover, power-structure transformation, and external realignment as distinct events.",
            "Acemoglu et al. 2019",
        ),
    ]
    for y, number, heading, statement, citation in literature:
        add_shape(slide, 0.72, y, 11.90, 1.42, OFFWHITE)
        add_text(slide, 0.96, y + 0.18, 0.45, 0.38, number, 22, BLUE, True)
        add_text(slide, 1.58, y + 0.17, 2.90, 0.84, heading, 22, INK, True)
        add_text(slide, 4.62, y + 0.10, 7.55, 0.94, statement, 22, INK,
                 line_spacing=1.0)
        add_text(slide, 4.62, y + 1.10, 7.55, 0.28, citation, 20, MUTED)
    add_shape(slide, 0.72, 6.34, 11.90, 0.82, NAVY)
    add_text(slide, 1.00, 6.43, 11.34, 0.60,
             "This project compares observable domestic and international events with separately coded outcomes.",
             20, WHITE, True, align=PP_ALIGN.CENTER)
    add_notes(slide, """
[4:50–6:35]
Three issues guide the research design. The first is measurement. Treier and Jackman show that measurement error in Polity scores can affect inference. Little and Meng show that recent expert-coded and objective indicators imply different trends in democratic backsliding. The implication for this project is concrete: the political variables need dated, observable records, and the economic outcomes must be coded separately.

The second issue concerns institutional classification. Inclusive institutions are partly identified through secure property rights and low expropriation risk. When those same features become outcomes, the classification risks circularity. The absence of a specified time horizon creates a second problem: continued growth under extractive institutions can always be treated as failure postponed. My design instead asks whether a defined event is followed by a defined outcome within five or eight years.

The third issue is the object of explanation. Acemoglu, Naidu, Restrepo, and Robinson estimate growth after democratic transitions using a dynamic panel. Their approach is a methodological starting point. The gap addressed here is the need to separate government turnover, formal regime change, effective power transformation, and external realignment. This separation lets me ask whether changes at home or abroad account for the subsequent economic trajectory.
""")

    slide = new_slide(prs)
    add_header(slide, 7, "Theoretical framework",
               "The framework separates domestic political change from international position")
    add_text(slide, 0.72, 1.72, 2.10, 0.40, "AJR, simplified", 20, MUTED, True)
    add_shape(slide, 3.10, 1.68, 2.30, 0.66, GRAY_LIGHT)
    add_text(slide, 3.22, 1.80, 2.06, 0.38, "Institutions", 22, INK, True,
             align=PP_ALIGN.CENTER)
    add_text(slide, 5.56, 1.75, 0.48, 0.45, "→", 26, MUTED, True,
             align=PP_ALIGN.CENTER)
    add_shape(slide, 6.22, 1.68, 3.00, 0.66, ORANGE_LIGHT)
    add_text(slide, 6.34, 1.80, 2.76, 0.38, "Economic outcomes", 22, ORANGE, True,
             align=PP_ALIGN.CENTER)
    add_text(slide, 0.72, 2.60, 2.10, 0.40, "This project", 20, BLUE, True)
    framework = [
        (0.72, GRAY_LIGHT, INK, "Who rules"),
        (3.13, GRAY_LIGHT, INK, "How power\nis organized"),
        (5.54, GRAY_LIGHT, INK, "Through what\napparatus"),
        (7.95, BLUE_LIGHT, BLUE, "International\nposition"),
        (10.36, ORANGE_LIGHT, ORANGE, "Economic\noutcomes"),
    ]
    for index, (x, fill, accent, label) in enumerate(framework):
        add_shape(slide, x, 2.98, 2.00, 1.42, fill)
        add_text(slide, x + 0.12, 3.08, 1.76, 1.20, label, 22, accent, True,
                 align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
                 line_spacing=1.05)
        if index < len(framework) - 1:
            add_text(slide, x + 2.02, 3.43, 0.38, 0.48, "→", 26, MUTED, True,
                     align=PP_ALIGN.CENTER)
    add_shape(slide, 0.72, 4.78, 11.64, 0.92, OFFWHITE)
    add_text(slide, 0.98, 4.90, 11.12, 0.66,
             "External realignment changes international position; material capabilities link that change to economic outcomes.",
             22, INK, align=PP_ALIGN.CENTER)
    add_text(slide, 0.82, 5.98, 11.44, 0.58,
             "Market access · capital · technology · energy · security guarantees",
             20, MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: Acemoglu & Robinson 2012; Core_Concepts.md; Lake 2009.")
    add_notes(slide, """
[6:35–8:10]
For comparison, I simplify the AJR framework as institutions leading to economic outcomes. This is a schematic summary of a richer research program. My project separates the domestic side into who rules, how power is organized, and through what apparatus rule is exercised. It then adds international position as a separate component.

These categories can change independently. A new president can change who rules without changing the power structure or state apparatus. A state can also change its international position without a domestic transformation. The purpose of the decomposition is to identify which component changed and when.

The international link works through material capabilities. Severance can withdraw market access, capital, technology, energy support, subsidies, or security guarantees. Entry into a richer sphere can expand them. Economic outcomes are measured separately. H1 concerns the domestic components, H2 concerns international position and outcomes, and H3 examines their interaction. Material endowments remain a comparison condition for the matched cases.
""")

    slide = new_slide(prs)
    add_header(slide, 8, "Hypotheses",
               "Three hypotheses connect domestic and international change")
    hypotheses = [
        (
            1.75, 1.22, "H1",
            "Turnover or nominal regime change alone produces no major economic discontinuity.",
            "Domestic events",
        ),
        (
            3.15, 1.22, "H2",
            "Severance produces disruption; entry into a richer sphere produces acceleration.",
            "International position → outcomes",
        ),
        (
            4.55, 1.45, "H3",
            "Domestic change produces discontinuity only with realignment; realignment produces the predicted outcome with or without domestic change.",
            "Domestic × international",
        ),
    ]
    for y, height, label, statement, link in hypotheses:
        add_shape(slide, 0.72, y, 11.90, height, OFFWHITE)
        add_text(slide, 0.98, y + 0.20, 0.68, 0.45, label, 26, BLUE, True)
        add_text(slide, 1.86, y + 0.13, 7.95, height - 0.24, statement, 22, INK,
                 valign=MSO_ANCHOR.MIDDLE, line_spacing=1.02)
        add_text(slide, 10.08, y + 0.15, 2.18, height - 0.30, link, 20, MUTED,
                 align=PP_ALIGN.RIGHT, valign=MSO_ANCHOR.MIDDLE)
    add_footer(slide, "Source: proposal_thesis.tex; comparable material endowments assumed.")
    add_notes(slide, """
[8:05–9:05]
H1 says that turnover or nominal regime change alone should leave the economic trajectory intact when effective power and external alignment remain unchanged. H2 supplies the signed external prediction: severance produces disruption, while entry into a richer sphere produces acceleration. H3 has two parts. Domestic political change produces a major discontinuity only when it coincides with realignment, and realignment produces the predicted outcome whether or not domestic change accompanies it.

These hypotheses require separate comparisons. I need cases with domestic change alone, realignment alone, and both together. I also need to record wrong-sign outcomes and cases where no discontinuity follows. The next two slides explain the data and the empirical design used to make those comparisons.
""")

    slide = new_slide(prs)
    add_header(slide, 9, "Data and measurement",
               "The dataset links observable events to economic outcomes")
    episodes = pd.read_csv(DATA / "episodes.csv")
    sources = pd.read_csv(DATA / "episode_sources.csv")
    panel = pd.read_csv(DATA / "panel_preliminary.csv", usecols=["iso3", "year"])
    episode_counts = episodes["type"].value_counts()
    grade_counts = sources["quality_grade"].value_counts()
    assert len(episodes) == 73
    assert episode_counts.to_dict() == {"entry": 46, "severance": 25, "severance_threat": 2}
    assert grade_counts.to_dict() == {"A": 64, "B": 7, "C": 2}
    assert panel["iso3"].nunique() == 73
    assert (panel["year"].min(), panel["year"].max()) == (1945, 2019)
    metrics = [
        (0.72, "73", "countries", 30),
        (3.72, "1945–2019", "event-coding window", 26),
        (6.72, "73", "realignment episodes", 30),
        (9.72, "64 / 7 / 2", "source grades A / B / C", 26),
    ]
    for x, value, label, size in metrics:
        add_shape(slide, x, 1.75, 2.90, 1.30, OFFWHITE)
        add_text(slide, x + 0.16, 1.93, 2.58, 0.50, value, size, BLUE, True,
                 align=PP_ALIGN.CENTER)
        add_text(slide, x + 0.16, 2.40, 2.58, 0.58, label, 20, MUTED,
                 align=PP_ALIGN.CENTER)
    add_shape(slide, 0.72, 3.35, 5.74, 0.92, OFFWHITE)
    add_text(slide, 0.94, 3.51, 5.30, 0.58,
             "46 entries · 25 severances · 2 threats", 22, INK, True,
             align=PP_ALIGN.CENTER)
    add_shape(slide, 6.72, 3.35, 5.90, 0.92, BLUE_LIGHT)
    add_text(slide, 6.94, 3.44, 5.46, 0.70,
             "Realignment: ≥2 of 4 indicator families within 3 years",
             20, BLUE, True, align=PP_ALIGN.CENTER)
    add_shape(slide, 0.72, 4.58, 11.90, 0.82, GRAY_LIGHT)
    add_text(slide, 0.96, 4.76, 11.42, 0.42,
             "Security · economic dependence · bloc membership · coercion",
             22, INK, align=PP_ALIGN.CENTER)
    add_shape(slide, 0.72, 5.74, 11.90, 0.74, NAVY)
    add_text(slide, 0.98, 5.88, 11.38, 0.44,
             "Every episode has a source trail · coding rules and sources in B2–B3",
             20, WHITE, True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: episodes.csv; episode_sources.csv; panel_preliminary.csv.")
    add_notes(slide, """
[9:05–10:35]
The event register covers 73 countries over the 1945–2019 coding window. The statistical analysis begins in 1960 because of outcome-data coverage. There are 73 coded realignment episodes: 46 entries, 25 severances, and two unconsummated threats.

A country enters or leaves a sphere when at least two of four indicator families change within three years: security ties, economic dependence, institutional bloc membership, and coercion. This rule allows informal relationships to count and prevents a single treaty or trade movement from determining the classification.

Every episode has a source trail. The current source-quality distribution is 64 A, seven B, and two C. These grades describe the evidence behind the coding, not the economic outcome. The protocol records gradual episodes as intervals and keeps unknown evidence missing. The backup slides provide the coding rules and episode-level sources.
""")

    slide = new_slide(prs)
    add_header(slide, 10, "Empirical design",
               "The empirical design uses three complementary tests")
    layers = [
        (
            0.72, "01", "Descriptive event screen", "Done — preliminary",
            "Compare growth and discontinuity rates across event cells.",
        ),
        (
            4.78, "02", "Panel models", "Next",
            "Use country and year fixed effects for domestic and external events.",
        ),
        (
            8.84, "03", "Matched cases and process tracing", "Next",
            "Trace events, capability flows, and outcomes; double-code a subset.",
        ),
    ]
    for x, number, heading, status, body in layers:
        add_shape(slide, x, 1.82, 3.72, 3.74, OFFWHITE)
        add_text(slide, x + 0.24, 2.06, 0.55, 0.40, number, 22, BLUE, True)
        add_text(slide, x + 0.24, 2.62, 3.24, 0.98, heading, 24, INK, True,
                 line_spacing=1.02)
        add_text(slide, x + 0.24, 3.72, 3.24, 0.40, status, 20, BLUE, True)
        add_line(slide, x + 0.24, 4.28, 3.24)
        add_text(slide, x + 0.24, 4.42, 3.24, 1.00, body, 20, MUTED,
                 line_spacing=1.02)
    add_shape(slide, 0.72, 5.90, 11.90, 0.70, NAVY)
    add_text(slide, 0.98, 6.02, 11.38, 0.44,
             "This talk reports Layer 1 · Empirical model on the next slide",
             20, WHITE, True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Source: ROADMAP.md, Steps 6–8.")
    add_notes(slide, """
[10:35–11:35]
The design has three layers. The first is the descriptive event screen reported in this presentation. It compares subsequent growth, disruption, and acceleration across cells defined by domestic and external events. These results are preliminary and non-causal.

The second layer estimates the panel model with country and year fixed effects and distributed event lags. This will ask whether the same associations remain within countries after common year shocks and measured controls are included. The next slide presents the formal equation and defines each component.

The third layer uses matched comparisons and process tracing. It examines the sequence from a political or international event through changes in material-capability flows to the outcome. Independent double-coding will assess reliability. The case layer is especially important for imposed severances and for outcomes that run contrary to the hypotheses.
""")

    slide = new_slide(prs)
    add_header(slide, 11, "Empirical model",
               "The panel model separates domestic and international events")
    add_shape(slide, 0.72, 1.68, 11.90, 1.48, BLUE_LIGHT)
    slide.shapes.add_picture(
        str(ASSETS / "empirical_model.png"), Inches(0.98), Inches(1.76),
        width=Inches(11.38), height=Inches(1.09),
    )
    add_text(slide, 0.94, 2.85, 11.46, 0.28,
             "H1: β₃ = β₄ = 0 · H2: β₁ < 0, β₂ > 0 · H3: domestic × realignment interactions",
             20, BLUE, True, align=PP_ALIGN.CENTER)

    cards = [(0.72, "OUTCOME & TERMS"),
             (4.78, "DOMESTIC EVENTS"),
             (8.84, "EXTERNAL EVENTS & X")]
    for x, heading in cards:
        add_shape(slide, x, 3.34, 3.72, 3.05, OFFWHITE)
        add_text(slide, x + 0.22, 3.48, 3.28, 0.34, heading, 20, BLUE, True)

    add_text(slide, 0.94, 3.92, 3.28, 0.58,
             "gᵢₜ: annual real GDP-per-capita growth.", 20, INK)
    add_text(slide, 0.94, 4.58, 3.28, 0.40,
             "αᵢ: stable country traits.", 20, INK)
    add_text(slide, 0.94, 5.16, 3.28, 0.52,
             "λₜ: common year shocks.", 20, INK)
    add_text(slide, 0.94, 5.74, 3.28, 0.40,
             "εᵢₜ: unobserved factors.", 20, INK)

    add_text(slide, 5.00, 3.82, 3.28, 0.60,
             "1 = event year; 0 = other years.", 20, MUTED)
    add_text(slide, 5.00, 4.50, 3.28, 0.34,
             "Turnover: new leader.", 20, INK)
    add_text(slide, 5.00, 4.94, 3.28, 0.34,
             "Regime: new rules.", 20, INK)
    add_text(slide, 5.00, 5.44, 3.28, 0.85,
             "PowerStructure: ≥2 of 4 power dimensions change within 3 years.", 20, INK)

    add_text(slide, 9.06, 3.84, 3.28, 0.85,
             "Severance: 1 if ≥2 ties end within 3 years; 0 otherwise.", 20, INK)
    add_text(slide, 9.06, 4.76, 3.28, 0.60,
             "Entry: 1 if ≥2 ties begin; H2 uses richer entry.", 20, INK)
    add_text(slide, 9.06, 5.48, 3.28, 0.85,
             "Xᵢₜ: oil rents (% GDP), population, investment (% GDP).", 20, INK)
    add_text(slide, 0.72, 6.40, 11.90, 0.30,
             "Event lags · Binary models: disruption (5 years), acceleration onset (8 years)",
             20, MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: proposal_thesis.tex, eq. (1); Coding_Protocol.md; WDI controls.")
    add_notes(slide, """
[11:35–13:45]
The dependent variable in equation (1) is annual real GDP-per-capita growth for country i in year t. This is a continuous measure. Separate binary models record a new disruption within five years or a new acceleration onset within eight years. Outcomes already underway are not counted as new.

The five political regressors are event indicators. Severance equals one when at least two sphere ties end within three years. Entry equals one when at least two ties begin. For the signed H2 test, richer entry means that patron GDP per capita exceeds the regional median. Turnover records replacement of the effective leader from Archigos. Regime change records a formal change in the rules of political power from constitutional and legal records. PowerStructure records change in at least two of four dimensions of effective power within three years. Each indicator is zero in other years, and lags allow outcomes to develop over several years. Apparatus restructuring is not a separate regressor in equation (1); it is combined with power transformation in the descriptive deep-transformation row.

Country fixed effects remove stable national differences, so the comparison is within a country over time. Year fixed effects account for shocks shared by all countries in a given year. X contains three WDI controls: oil rents as a share of GDP for commodity dependence, population for demographic scale, and gross capital formation as a share of GDP for investment. These controls are not spliced across sources. Gamma collects their coefficients, and epsilon records remaining unobserved factors. Standard errors will be clustered by country. H1 predicts zero coefficients for turnover and formal regime change, H2 predicts a negative severance coefficient and a positive richer-entry coefficient, and H3 requires interactions between domestic events and realignment.
""")

    slide = new_slide(prs)
    add_header(slide, 12, "Preliminary results",
               "Five-year growth is lower after severance and higher after richer entry")
    add_text(slide, 0.72, 1.68, 11.90, 0.38,
             "Mean annual real GDP-per-capita growth, years 1–5 after interval start",
             20, MUTED)
    slide.shapes.add_picture(
        str(ASSETS / "results_growth.png"), Inches(0.68), Inches(2.08),
        width=Inches(11.97), height=Inches(3.53),
    )
    add_text(slide, 0.72, 5.86, 11.90, 0.38, CAVEAT, 20, BLUE, True,
             align=PP_ALIGN.CENTER)
    add_text(slide, 0.72, 6.30, 11.90, 0.36,
             "All domestic rows combined; complete five-year outcome windows.",
             20, MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide,
               "Source: step6_cell_frequencies_preliminary.csv; interval-start coding, 1960–2019.")
    add_notes(slide, """
[13:45–14:35]
This slide reports mean annual real GDP-per-capita growth over the five complete years after the start of an event. Across all domestic rows, severance country-years average minus 3.28 percent. Richer-entry country-years average plus 3.43 percent, and the no-realignment average is plus 2.23 percent. The signs match H2 under this dating rule.

The event groups contain 20 country-years each, while the no-realignment group contains 4,335. These are descriptive, non-causal, preliminary means. Forward windows overlap, and later dating and case-selection checks show substantial sensitivity. I use this result to motivate the formal tests, not to claim that the panel coefficients have already been estimated.
""")

    slide = new_slide(prs)
    add_header(slide, 13, "Preliminary results",
               "Disruption is common after severance; acceleration after richer entry")
    add_text(slide, 0.72, 1.68, 11.90, 0.38,
             "Forward outcome frequencies under interval-start coding",
             20, MUTED)
    slide.shapes.add_picture(
        str(ASSETS / "results_discontinuities.png"), Inches(0.68), Inches(2.10),
        width=Inches(11.97), height=Inches(3.27),
    )
    add_text(slide, 0.72, 5.66, 11.90, 0.38, CAVEAT, 20, BLUE, True,
             align=PP_ALIGN.CENTER)
    add_text(slide, 0.72, 6.12, 11.90, 0.48,
             "Disruption and acceleration use different windows and are not mutually exclusive.",
             20, MUTED, align=PP_ALIGN.CENTER)
    add_footer(slide,
               "Source: step6_cell_frequencies_preliminary.csv; current coded state, 1960–2019.")
    add_notes(slide, """
[14:35–15:25]
The discontinuity measures tell a related story. Fifteen of the 20 severance observations, or 75 percent, have a disruption in the following five years. Twelve of the 20 richer-entry observations, or 60 percent, have a new acceleration onset in the following eight years.

Disruption includes a severe output contraction, a sustained growth collapse, or very high inflation. Acceleration onset marks the beginning of a sustained growth episode. The two outcomes use different windows and can both occur, so these percentages do not sum to one. Already-active outcomes are not counted as new onsets. These rates aggregate domestic rows and remain descriptive, non-causal, and preliminary.
""")

    slide = new_slide(prs)
    add_header(slide, 14, "Preliminary results",
               "Turnover-only growth and disruption are near baseline")
    add_text(slide, 0.72, 1.67, 11.90, 0.38,
             "No realignment; turnover-only excludes formal regime change; interval-start coding",
             20, MUTED)
    slide.shapes.add_picture(
        str(ASSETS / "results_h1.png"), Inches(0.68), Inches(2.05),
        width=Inches(11.97), height=Inches(3.43),
    )
    add_shape(slide, 0.72, 5.62, 11.90, 0.62, ORANGE_LIGHT)
    add_text(slide, 0.96, 5.73, 11.42, 0.40,
             "Acceleration onset: 13.1% baseline; 15.1% turnover only.",
             20, ORANGE, True, align=PP_ALIGN.CENTER)
    add_text(slide, 0.72, 6.34, 11.90, 0.36, CAVEAT, 20, BLUE, True,
             align=PP_ALIGN.CENTER)
    add_footer(slide,
               "Sources: Step 6 country-year cells; panel_preliminary.csv; no realignment, 1960–2019.")
    add_notes(slide, """
[15:25–16:15]
H1 receives a narrow, qualified result here. This version uses strict leader turnover only: no external realignment, no formal regime change, and known absence of power-structure or apparatus transformation. Five-year forward growth averages 2.19 percent when no domestic event is observed and 2.41 percent after leader turnover only. The raw difference is about 0.22 percentage points. Disruption occurs in 22.8 percent and 17.7 percent of the respective samples, a difference of about five percentage points in the opposite direction.

The acceleration result still qualifies a blanket claim that turnover changes nothing. New acceleration onset is 13.1 percent at baseline and 15.1 percent after leader turnover only. These strict comparisons use 417 valid growth and disruption observations and 390 valid acceleration observations. The previous fixed-effects statement applied to the broader turnover/formal category and has been removed. Formal panel estimates and matched-case tests remain for the next stage.
""")

    slide = new_slide(prs)
    add_header(slide, 15, "Robustness and limitations",
               "Three limitations guide the next stage")
    add_text(slide, 1.58, 1.70, 4.20, 0.36, "LIMITATION", 20, MUTED, True)
    add_text(slide, 6.50, 1.70, 5.60, 0.36, "NEXT STEP", 20, MUTED, True)
    limitations = [
        (
            2.12, "01", "Small cells and overlapping windows",
            "Estimate country/year fixed-effects models; examine imposed severances. (B7)",
        ),
        (
            3.48, "02", "Results depend on interval dating",
            "Report start, midpoint, and endpoint estimates; audit case selection. (B4)",
        ),
        (
            4.84, "03", "Wrong-sign and pre-existing outcomes",
            "Trace capability flows and alternative explanations in the cases. (B5)",
        ),
    ]
    for y, number, limitation, remedy in limitations:
        add_shape(slide, 0.72, y, 11.90, 1.14, OFFWHITE)
        add_text(slide, 0.96, y + 0.35, 0.45, 0.40, number, 22, BLUE, True)
        add_text(slide, 1.58, y + 0.17, 4.35, 0.80, limitation, 22, INK, True,
                 valign=MSO_ANCHOR.MIDDLE)
        add_text(slide, 6.50, y + 0.13, 5.65, 0.88, remedy, 20, INK,
                 valign=MSO_ANCHOR.MIDDLE, line_spacing=1.02)
    add_shape(slide, 0.72, 6.20, 11.90, 0.48, NAVY)
    add_text(slide, 0.96, 6.26, 11.42, 0.34,
             "Anomalous cases remain in the data; open coding judgments remain documented.",
             20, WHITE, True, align=PP_ALIGN.CENTER)
    add_footer(slide, "Sources: proposal_thesis.tex; STEP6_PRELIMINARY.md; OPEN_ISSUES.md.")
    add_notes(slide, """
[Limitations — 55 seconds]
Three limitations define the next stage. First, the event cells are small and the forward windows overlap. The current results are descriptive associations. The planned panel models will add country and year fixed effects, and imposed severances caused by a patron's collapse or withdrawal provide an especially useful comparison.

Second, the results depend on where a gradual realignment is dated. The registered start, midpoint, and endpoint variants must be reported together, together with the case-selection audits. Third, some cases have pre-existing outcomes or outcomes with the opposite sign. The case analysis will trace capability flows and examine war, commodity prices, financial crises, and policy change. These cases stay in the dataset, and unresolved coding judgments remain documented.
""")

    slide = new_slide(prs)
    add_header(slide, 16, "Conclusion", "The project links domestic political change to international position")
    conclusion = [
        (1.72, "QUESTION",
         "Which domestic and international changes coincide with major economic discontinuities?"),
        (2.94, "EVIDENCE",
         "Start-date associations match H2; H1 is near baseline for growth and disruption, with an acceleration qualification."),
        (4.16, "CONTRIBUTION",
         "A replicable event taxonomy and a comparative test of domestic power and international position."),
    ]
    for y, label, statement in conclusion:
        add_shape(slide, 0.72, y, 11.90, 1.00, OFFWHITE)
        add_text(slide, 0.98, y + 0.31, 1.65, 0.38, label, 20, BLUE, True)
        add_text(slide, 2.78, y + 0.12, 9.48, 0.76, statement, 22, INK,
                 valign=MSO_ANCHOR.MIDDLE, line_spacing=1.02)
    add_shape(slide, 0.72, 5.52, 11.90, 1.10, NAVY)
    add_text(slide, 1.02, 5.63, 11.30, 0.88,
             "International realignment matters when it changes the material capabilities available to the state.",
             24, WHITE, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE,
             line_spacing=1.02)
    add_footer(slide, "Source: proposal_thesis.tex, Expected Contribution and Remaining Work.")
    add_notes(slide, """
[Conclusion — 60 seconds]
The project asks which domestic and international changes coincide with major economic discontinuities. The preliminary evidence provides a reason to pursue the full design. Under start coding, severance is associated with weaker growth and more frequent disruption, while richer entry is associated with stronger growth and more frequent acceleration. Turnover-only growth and disruption are near baseline, although the acceleration result qualifies H1.

The contribution is a replicable event taxonomy that separates rulers, formal rules, effective power, the state apparatus, and international alignment. The next stage will estimate the panel models, complete matched comparisons and process tracing, and measure changes in market access, capital, technology, energy prices, subsidies, and security guarantees. The central claim to test is that international realignment matters when it changes the material capabilities available to the state.
""")

    if len(prs.slides) != 16:
        raise AssertionError("The deck must contain slides 1–16")
    prs.save(OUTPUT)


def validate_output():
    with zipfile.ZipFile(OUTPUT) as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise ValueError(f"Corrupt PPTX member: {bad_file}")
        notes = [
            name for name in archive.namelist()
            if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
        ]
        if len(notes) != 16:
            raise ValueError(f"Expected sixteen speaker-note pages, found {len(notes)}")

    check = Presentation(OUTPUT)
    tolerance = Inches(0.02)
    for index, slide in enumerate(check.slides, start=1):
        if not slide.notes_slide.notes_text_frame.text.strip():
            raise ValueError(f"Missing speaker notes on slide {index}")
        for shape in slide.shapes:
            if shape.left < -tolerance or shape.top < -tolerance:
                raise ValueError(f"Negative shape position on slide {index}")
            if shape.left + shape.width > check.slide_width + tolerance:
                raise ValueError(f"Shape exceeds right edge on slide {index}")
            if shape.top + shape.height > check.slide_height + tolerance:
                raise ValueError(f"Shape exceeds bottom edge on slide {index}")
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                if paragraph.text.strip() and paragraph.font.size is not None:
                    if paragraph.font.size < Pt(20):
                        raise ValueError(f"Text below 20 pt on slide {index}")
    print(f"Validated {OUTPUT.relative_to(ROOT)}: sixteen slides, notes, bounds, and fonts")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    results = verify_source_numbers()
    build_puzzle_figure()
    build_model_formula()
    build_results_figures(results)
    build_deck(results)
    validate_output()


if __name__ == "__main__":
    main()
