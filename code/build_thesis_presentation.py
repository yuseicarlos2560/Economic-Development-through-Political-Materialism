"""Build the preliminary thesis-proposal presentation and its custom graphics."""
from pathlib import Path
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

from plot_realignment_event_time import episode_matrix, load_data

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_clean"
PAPER = ROOT / "paper"
FIGURES = PAPER / "figures" / "presentation"
OUTPUT = PAPER / "thesis_proposal_presentation.pptx"

FONT = "Arial"
WHITE = "FFFFFF"
OFFWHITE = "F7F8FA"
INK = "17212B"
MUTED = "5E6872"
FAINT = "8B949D"
GRID = "DDE3E8"
NAVY = "102A43"
BLUE = "2878A5"
BLUE_LIGHT = "E8F1F6"
ORANGE = "D97925"
ORANGE_LIGHT = "FBF0E5"
GRAY_LIGHT = "EEF1F4"
GROWTH = "263746"
LEVEL = "9AA3AB"

SLIDE_W = 13.333
SLIDE_H = 7.5

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 12,
    "text.color": f"#{INK}",
    "axes.labelcolor": f"#{INK}",
    "axes.edgecolor": f"#{GRID}",
    "xtick.color": f"#{MUTED}",
    "ytick.color": f"#{MUTED}",
    "savefig.facecolor": "white",
})


def rgb(value):
    return RGBColor.from_string(value)


def set_background(slide, color=WHITE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb(color)


def add_shape(slide, x, y, w, h, fill, radius=True, line=None):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(0.8)
    else:
        shape.line.fill.background()
    return shape


def add_text(slide, x, y, w, h, text, size=18, color=INK, bold=False,
             align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, italic=False,
             margin=0, font=FONT, line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    frame.vertical_anchor = valign
    paragraph = frame.paragraphs[0]
    paragraph.text = text
    paragraph.alignment = align
    paragraph.line_spacing = line_spacing
    paragraph.space_after = Pt(0)
    paragraph.font.name = font
    paragraph.font.size = Pt(size)
    paragraph.font.bold = bold
    paragraph.font.italic = italic
    paragraph.font.color.rgb = rgb(color)
    return box


def add_paragraphs(slide, x, y, w, h, paragraphs, margin=0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = frame.margin_right = Inches(margin)
    frame.margin_top = frame.margin_bottom = Inches(margin)
    for index, spec in enumerate(paragraphs):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = spec["text"]
        paragraph.font.name = FONT
        paragraph.font.size = Pt(spec.get("size", 17))
        paragraph.font.bold = spec.get("bold", False)
        paragraph.font.italic = spec.get("italic", False)
        paragraph.font.color.rgb = rgb(spec.get("color", INK))
        paragraph.alignment = spec.get("align", PP_ALIGN.LEFT)
        paragraph.line_spacing = spec.get("line_spacing", 1.0)
        paragraph.space_before = Pt(spec.get("before", 0))
        paragraph.space_after = Pt(spec.get("after", 0))
        if spec.get("bullet", False):
            paragraph.text = "•  " + paragraph.text
    return box


def add_line(slide, x, y, w, color=GRID, height=0.015):
    return add_shape(slide, x, y, w, height, color, radius=False)


def add_header(slide, number, title, kicker, subtitle=None):
    add_text(slide, 0.68, 0.28, 11.7, 0.25, kicker.upper(), 10, BLUE, True)
    title_size = 28 if len(title) <= 52 else 25 if len(title) <= 68 else 22
    add_text(slide, 0.68, 0.62, 12.0, 0.66, title, title_size, INK, True)
    if subtitle:
        add_text(slide, 0.68, 1.25, 12.0, 0.32, subtitle, 13, MUTED)
    add_line(slide, 0.68, 1.56 if subtitle else 1.34, 11.97)


def add_footer(slide, number, source, dark=False):
    color = "C7D2DE" if dark else MUTED
    add_text(slide, 0.68, 7.12, 11.8, 0.20, source, 8.5, color)
    add_text(slide, 12.55, 7.08, 0.25, 0.22, str(number), 9, color, True,
             align=PP_ALIGN.RIGHT)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


def add_chevron(slide, x, y, w=0.38, h=0.44, color=FAINT):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.CHEVRON, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    shape.line.fill.background()
    return shape


def add_metric_card(slide, x, y, w, h, value, label, accent=INK, fill=OFFWHITE,
                    value_size=27, label_size=13):
    add_shape(slide, x, y, w, h, fill)
    add_text(slide, x + 0.20, y + 0.17, w - 0.4, 0.43, value, value_size,
             accent, True)
    add_text(slide, x + 0.20, y + 0.69, w - 0.4, h - 0.79, label, label_size,
             MUTED, line_spacing=1.05)


def country_panel(iso3, start, end):
    columns = [
        "iso3", "country", "year", "gdp_pc_growth", "gdp_pc_const",
        "gdp_pc_source", "gdp_pc_seam",
    ]
    panel = pd.read_csv(DATA / "panel_preliminary.csv", usecols=columns)
    selected = panel[
        panel["iso3"].eq(iso3) & panel["year"].between(start, end)
    ].sort_values("year")
    if selected.empty:
        raise ValueError(f"No panel observations for {iso3}, {start}–{end}")
    return selected


def draw_case_chart(filename, iso3, start, end, bands, domestic=None,
                    outcome=None, y_limits=None, y_ticks=None):
    panel = country_panel(iso3, start, end)
    fig, ax = plt.subplots(figsize=(9.0, 4.65))
    fig.subplots_adjust(left=0.085, right=0.89, top=0.91, bottom=0.16)
    level_ax = ax.twinx()
    level_ax.set_zorder(ax.get_zorder() - 1)
    ax.set_zorder(level_ax.get_zorder() + 1)
    ax.patch.set_visible(False)

    growth = panel["gdp_pc_growth"].dropna()
    lower = min(-2, np.floor(growth.min() / 2) * 2 - 2)
    upper = max(4, np.ceil(growth.max() / 2) * 2 + 2)
    if y_limits:
        lower, upper = y_limits
    ax.set_ylim(lower, upper)

    for band in bands:
        color = band["color"]
        ax.axvspan(
            band["start"] - 0.35, band["end"] + 0.35,
            color=color, alpha=0.10, linewidth=0, zorder=0,
        )
        ax.axvline(
            band["start"], color=color, linewidth=1.6,
            linestyle=(0, (4, 3)), alpha=0.9, zorder=2,
        )
        ax.text(
            (band["start"] + band["end"]) / 2, upper - (upper - lower) * 0.045,
            band["label"], ha="center", va="top", fontsize=11.5,
            color=color, fontweight="bold", linespacing=1.25,
        )

    source_change = (
        panel["gdp_pc_source"].ne(panel["gdp_pc_source"].shift())
        | panel["gdp_pc_seam"].fillna(False).astype(bool)
    )
    for _, segment in panel.groupby(source_change.cumsum()):
        level_ax.plot(
            segment["year"], segment["gdp_pc_const"], color=f"#{LEVEL}",
            linewidth=1.5, alpha=0.72, zorder=1,
        )
    level_ax.set_ylim(bottom=0)
    level_ax.set_ylabel("Real GDP per capita", fontsize=10.5, color=f"#{FAINT}",
                        rotation=270, labelpad=17)
    level_ax.tick_params(axis="y", colors=f"#{FAINT}", length=0, labelsize=9)
    level_ax.ticklabel_format(style="plain", axis="y")
    level_ax.spines[["top", "left", "bottom", "right"]].set_visible(False)
    level_ax.grid(False)

    ax.axhline(0, color=f"#{FAINT}", linewidth=0.9, zorder=1)
    ax.plot(
        panel["year"], panel["gdp_pc_growth"], color=f"#{GROWTH}",
        linewidth=2.0, marker="o", markersize=3.8, markeredgewidth=0,
        zorder=3,
    )
    ax.set_xlim(start - 0.6, end + 0.6)
    ax.set_ylabel("Annual real GDP-per-capita growth (%)", fontsize=11.5,
                  labelpad=9)
    ax.set_xticks(np.arange(start + ((5 - start) % 5), end + 1, 5))
    if y_ticks:
        ax.set_yticks(y_ticks)
    ax.tick_params(length=0, labelsize=10.5, pad=5)
    ax.grid(axis="y", color=f"#{GRID}", linewidth=0.75)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(f"#{GRID}")

    for marker in domestic or []:
        ax.axvline(
            marker["year"], color=f"#{MUTED}", linewidth=1.2,
            linestyle=(0, (1, 2)), zorder=2,
        )
        ax.text(
            marker["year"], lower + (upper - lower) * marker.get("height", 0.16),
            marker["label"], ha=marker.get("align", "center"), va="bottom",
            fontsize=10.5, color=f"#{MUTED}", linespacing=1.15,
        )

    if outcome:
        y = lower + (upper - lower) * 0.055
        ax.plot(
            [outcome["start"], outcome["end"]], [y, y],
            color=outcome["color"], linewidth=4.0, solid_capstyle="butt",
        )
        ax.text(
            (outcome["start"] + outcome["end"]) / 2,
            y + (upper - lower) * 0.025,
            outcome["label"], ha="center", va="bottom", fontsize=10.5,
            color=outcome["color"], fontweight="bold",
        )

    fig.savefig(FIGURES / filename, dpi=220, facecolor="white")
    plt.close(fig)


def draw_event_time():
    panel, events, _ = load_data()
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.3))
    fig.subplots_adjust(left=0.065, right=0.99, top=0.77, bottom=0.16, wspace=0.13)
    specifications = [
        ("severance", "Severance", BLUE),
        ("entry_richer", "Richer entry", ORANGE),
    ]
    for index, (event_type, label, accent) in enumerate(specifications):
        ax = axes[index]
        typed = events[events["event_type"].eq(event_type)]
        matrix = episode_matrix(typed, panel, 5)
        for _, trajectory in matrix.iterrows():
            ax.plot(
                matrix.columns, trajectory.to_numpy(), color="#73777C",
                alpha=0.5, linewidth=0.75, solid_capstyle="round", zorder=2,
            )
        ax.plot(
            matrix.columns, matrix.mean(axis=0).to_numpy(), color="#000000",
            linewidth=2.5, solid_capstyle="round", zorder=4,
        )
        ax.set_xlim(-5.15, 5.15)
        ax.set_ylim(-15, 15)
        ax.set_xticks([-5, -3, 0, 3, 5])
        ax.set_yticks([-15, -10, -5, 0, 5, 10, 15])
        ax.axhline(0, color=f"#{FAINT}", linewidth=0.8, zorder=1)
        ax.axvline(0, color=f"#{MUTED}", linewidth=1.0,
                   linestyle=(0, (2, 3)), zorder=1)
        ax.grid(axis="y", color=f"#{GRID}", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(f"#{GRID}")
        ax.tick_params(length=0, labelsize=10.5, pad=5)
        if index == 1:
            ax.tick_params(axis="y", labelleft=False)
        else:
            ax.set_ylabel("Annual real GDP-per-capita growth (%)", fontsize=11.5)
        ax.set_xlabel("Years from realignment start", fontsize=11.5, labelpad=7)
        ax.set_title(label, loc="left", fontsize=16, fontweight="bold",
                     color=f"#{accent}", pad=27)
        counts = matrix.notna().sum(axis=0)
        ax.text(
            0, 1.035,
            f"{len(matrix)} episodes · {counts.min()}–{counts.max()} observed per event year",
            transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5,
            color=f"#{MUTED}",
        )
    fig.legend(
        handles=[
            Line2D([0], [0], color="#73777C", alpha=0.5, linewidth=1.0,
                   label="Country-event trajectory"),
            Line2D([0], [0], color="#000000", linewidth=2.4,
                   label="Average across observed episodes"),
        ],
        loc="upper left", bbox_to_anchor=(0.065, 0.985), frameon=False,
        ncol=2, fontsize=10.5, handlelength=2.5, columnspacing=2.0,
    )
    fig.savefig(FIGURES / "event_time_five_year.png", dpi=220, facecolor="white")
    plt.close(fig)


def prepare_graphics():
    FIGURES.mkdir(parents=True, exist_ok=True)
    draw_event_time()
    draw_case_chart(
        "case_cuba.png", "CUB", 1984, 1995,
        [{"start": 1989, "end": 1991, "color": f"#{BLUE}",
          "label": "1989–91\nSoviet severance"}],
        outcome={"start": 1990, "end": 1993, "color": f"#{BLUE}",
                 "label": "Collapse proper"},
        y_limits=(-18, 12), y_ticks=[-15, -10, -5, 0, 5, 10],
    )
    draw_case_chart(
        "case_estonia.png", "EST", 1988, 2007,
        [
            {"start": 1990, "end": 1994, "color": f"#{BLUE}",
             "label": "1990–94\nSoviet severance"},
            {"start": 1995, "end": 2004, "color": f"#{ORANGE}",
             "label": "1995–2004\nUS/EU entry"},
        ],
        outcome={"start": 1998, "end": 2007, "color": f"#{ORANGE}",
                 "label": "A018 · acceleration"},
        y_limits=(-23, 19), y_ticks=[-20, -10, 0, 10],
    )
    draw_case_chart(
        "case_vietnam.png", "VNM", 1984, 2001,
        [
            {"start": 1989, "end": 1991, "color": f"#{BLUE}",
             "label": "1989–91\nSoviet severance"},
            {"start": 1994, "end": 1995, "color": f"#{ORANGE}",
             "label": "1994–95\nUS entry"},
        ],
        domestic=[{"year": 1986, "label": "1986\nĐổi Mới", "height": 0.17}],
        outcome={"start": 1992, "end": 2001, "color": f"#{ORANGE}",
                 "label": "A069 · acceleration begins before US entry"},
        y_limits=(-8, 15), y_ticks=[-5, 0, 5, 10, 15],
    )
    draw_case_chart(
        "case_peru.png", "PER", 1980, 1993,
        [],
        domestic=[
            {"year": 1985, "label": "1985\nGarcía", "height": 0.60},
            {"year": 1992, "label": "1992 power\ntransformation", "height": 0.18},
        ],
        outcome={"start": 1985, "end": 1993, "color": f"#{BLUE}",
                 "label": "D064 · no coded external realignment"},
        y_limits=(-17, 11), y_ticks=[-15, -10, -5, 0, 5, 10],
    )


def new_slide(prs, background=WHITE):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_background(slide, background)
    return slide


def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)
    prs.core_properties.title = "Economic Development, a Political Materialism Perspective"
    prs.core_properties.subject = "Thesis research proposal — preliminary results"
    prs.core_properties.author = "Carlos Gustavo Salas Flores"
    prs.core_properties.keywords = "political materialism, economic development, realignment"

    slide = new_slide(prs, NAVY)
    add_shape(slide, 0.0, 0.0, 0.14, 7.5, BLUE, radius=False)
    add_text(slide, 0.78, 0.55, 7.0, 0.3, "THESIS RESEARCH PROPOSAL", 11,
             "9FC4D8", True)
    add_text(slide, 0.78, 1.18, 8.5, 1.5,
             "Economic Development,\na Political Materialism Perspective",
             33, WHITE, True, line_spacing=0.95)
    add_text(slide, 0.80, 3.10, 7.5, 0.3, "RESEARCH QUESTION", 10,
             "9FC4D8", True)
    add_text(slide, 0.80, 3.52, 7.75, 1.25,
             "Which changes in domestic power and international alignment produce major economic discontinuities?",
             23, WHITE, line_spacing=1.08)
    add_text(slide, 0.80, 6.20, 7.6, 0.55,
             "Carlos Gustavo Salas Flores\nBeijing Normal University · 15-minute presentation",
             13, "C7D2DE", line_spacing=1.25)
    add_shape(slide, 9.30, 1.18, 3.15, 1.25, "173D59")
    add_text(slide, 9.55, 1.42, 2.65, 0.3, "SEVERANCE", 11, "9FC4D8", True)
    add_text(slide, 9.55, 1.83, 2.65, 0.4, "Disruption  ↓", 23, WHITE, True)
    add_shape(slide, 9.30, 2.72, 3.15, 1.25, "49351F")
    add_text(slide, 9.55, 2.96, 2.65, 0.3, "RICHER ENTRY", 11, "E9B27D", True)
    add_text(slide, 9.55, 3.37, 2.65, 0.4, "Acceleration  ↑", 23, WHITE, True)
    add_text(slide, 9.32, 4.48, 3.1, 1.15,
             "Material capabilities\nMarkets · capital · technology\nEnergy · security guarantees",
             14, "C7D2DE", line_spacing=1.25)
    add_text(slide, 9.32, 6.25, 3.0, 0.4, "Includes preliminary results", 11,
             "9FC4D8", italic=True)
    add_footer(slide, 1, "Accepted coding state · 1960–2019 · All empirical results are preliminary", dark=True)
    add_notes(slide, """
[0:00–0:45]
Thank you for making the time. The project asks a simple question: which political and international changes actually break a country's economic trajectory? I approach this through political materialism. The central object is a change in the material capabilities available to the state, including market access, capital, technology, energy, subsidies, and security guarantees. I will give you the framework and research design in three minutes, show the strongest preliminary patterns, and then spend most of the presentation on four cases. Cuba and Estonia fit the signed predictions. Vietnam and Peru expose different problems that the next stage needs to resolve.
""")

    slide = new_slide(prs)
    add_header(slide, 2, "Economic breaks follow material capabilities",
               "Framework")
    add_shape(slide, 0.72, 1.87, 2.25, 1.23, GRAY_LIGHT)
    add_text(slide, 0.94, 2.07, 1.82, 0.7, "External\nrealignment", 21, INK, True,
             valign=MSO_ANCHOR.MIDDLE)
    add_chevron(slide, 3.18, 2.25)
    add_shape(slide, 3.78, 1.56, 2.20, 0.72, BLUE_LIGHT)
    add_text(slide, 3.96, 1.76, 1.85, 0.3, "Severance", 18, BLUE, True)
    add_shape(slide, 3.78, 2.55, 2.20, 0.72, ORANGE_LIGHT)
    add_text(slide, 3.96, 2.75, 1.85, 0.3, "Richer entry", 18, ORANGE, True)
    add_chevron(slide, 6.18, 1.70, color=BLUE)
    add_chevron(slide, 6.18, 2.69, color=ORANGE)
    add_shape(slide, 6.77, 1.56, 2.30, 0.72, BLUE_LIGHT)
    add_text(slide, 6.96, 1.64, 1.95, 0.56, "Capabilities\nwithdrawn", 16, BLUE, True)
    add_shape(slide, 6.77, 2.55, 2.30, 0.72, ORANGE_LIGHT)
    add_text(slide, 6.96, 2.63, 1.95, 0.56, "Capabilities\nsupplied", 16, ORANGE, True)
    add_chevron(slide, 9.27, 1.70, color=BLUE)
    add_chevron(slide, 9.27, 2.69, color=ORANGE)
    add_shape(slide, 9.86, 1.56, 2.70, 0.72, BLUE)
    add_text(slide, 10.05, 1.76, 2.32, 0.3, "Disruption", 19, WHITE, True)
    add_shape(slide, 9.86, 2.55, 2.70, 0.72, ORANGE)
    add_text(slide, 10.05, 2.75, 2.32, 0.3, "Acceleration", 19, WHITE, True)
    add_shape(slide, 0.72, 3.60, 11.84, 0.64, OFFWHITE)
    add_text(slide, 0.96, 3.79, 11.35, 0.27,
             "Material capabilities: market access · capital · technology · energy prices · subsidies · security guarantees",
             14, MUTED, align=PP_ALIGN.CENTER)
    hypotheses = [
        (0.72, "H1", "Turnover or nominal regime change alone leaves the trajectory intact."),
        (4.78, "H2", "Severance produces disruption; richer entry produces acceleration."),
        (8.84, "H3", "Realignment works with or without domestic political transformation."),
    ]
    for x, label, body in hypotheses:
        add_shape(slide, x, 4.60, 3.72, 1.72, OFFWHITE)
        add_text(slide, x + 0.22, 4.82, 0.55, 0.35, label, 19, BLUE, True)
        add_text(slide, x + 0.22, 5.25, 3.28, 0.85, body, 15.5, INK,
                 line_spacing=1.08)
    add_footer(slide, 2, "Lake (2009); Rodrik (1999); Hausmann, Pritchett & Rodrik (2005). Predictions assume comparable material endowments.")
    add_notes(slide, """
[0:45–2:10]
The framework separates domestic political labels from changes in effective power and international alignment. H1 says that replacing rulers or changing formal rules should leave the economy on its previous path when effective power and external alignment remain untouched. H2 supplies the signed mechanism. Severance withdraws capabilities associated with a dominant-power relationship and predicts disruption. Entry into a richer sphere supplies capabilities and predicts acceleration. H3 says realignment should generate its outcome with or without a domestic political transformation; domestic change alone is insufficient under H1.

The important empirical implication is that alliances, subsidies, market access, and security guarantees are observable separately from GDP. I can therefore code the proposed cause before examining the outcome. Material endowments remain a comparison condition: the strongest qualitative tests use countries with similar structural constraints.
""")

    slide = new_slide(prs)
    add_header(slide, 3, "Observable events make the theory testable", "Research design")
    metrics = [
        (0.72, "73", "countries"),
        (3.72, "4,380", "country-years"),
        (6.72, "1960–2019", "four regions"),
        (9.72, "46 / 28", "episodes / countries"),
    ]
    for x, value, label in metrics:
        add_metric_card(slide, x, 1.62, 2.84, 1.12, value, label,
                        value_size=25, label_size=13)
    add_shape(slide, 0.72, 3.06, 5.90, 3.45, OFFWHITE)
    add_text(slide, 0.98, 3.29, 5.35, 0.3, "EVENTS CODED INDEPENDENTLY OF OUTCOMES", 11,
             BLUE, True)
    rows = [
        (3.84, "Domestic", "Turnover · formal regime change · effective power · apparatus"),
        (4.70, "External", "Two or more security, economic, institutional, or coercive ties"),
        (5.56, "Outcome", "Disruption within 5 years · acceleration onset within 8 years"),
    ]
    for y, label, body in rows:
        add_text(slide, 0.98, y, 1.10, 0.30, label, 15, INK, True)
        add_text(slide, 2.22, y - 0.02, 4.03, 0.60, body, 14, MUTED,
                 line_spacing=1.05)
    add_shape(slide, 6.84, 3.06, 5.72, 3.45, OFFWHITE)
    add_text(slide, 7.10, 3.29, 5.18, 0.3, "THREE COMPLEMENTARY TESTS", 11,
             BLUE, True)
    tests = [
        (3.83, "01", "Matched comparisons", "Comparable material endowments"),
        (4.68, "02", "Process tracing", "Event sequence and capability flows"),
        (5.53, "03", "Panel models", "Country and year fixed effects · planned"),
    ]
    for y, number, title, body in tests:
        add_text(slide, 7.10, y, 0.42, 0.3, number, 13, BLUE, True)
        add_text(slide, 7.62, y - 0.02, 4.48, 0.34, title, 15, INK, True)
        add_text(slide, 7.62, y + 0.39, 4.48, 0.30, body, 13, MUTED)
    add_footer(slide, 3, "Sources: WDI; IMF WEO; Maddison; Archigos; Comparative Constitutions Project; ATOP/COW; legal and historical records.")
    add_notes(slide, """
[2:10–3:25]
The accepted coding state covers 73 countries and 4,380 country-years across Latin America, post-Soviet Eurasia, East Asia, and Europe. The event-time analysis uses 46 severance or richer-entry episodes in 28 countries. Domestic events come from leader records, constitutional documents, and legal evidence. External realignment requires the establishment or termination of at least two documented ties within three years. Unknown evidence stays missing.

The outcomes are fixed independently. Disruption includes a severe peak-to-trough contraction, a sustained growth collapse, or inflation above 500 percent. Acceleration requires at least 3.5 percent annual growth for eight years and a two-point improvement over the previous regime. The design combines matched comparisons, process tracing, and, in the next stage, country and year fixed-effects models. Today's numerical results are descriptive; the case evidence is what lets me examine sequence and mechanism.
""")

    slide = new_slide(prs)
    add_header(slide, 4, "The aggregate associations have the predicted signs",
               "Preliminary evidence", "Mean annual real GDP-per-capita growth during t+1 to t+5 · interval-start coding")
    add_text(slide, 0.82, 1.73, 6.9, 0.3, "FIVE-YEAR FORWARD GROWTH", 11, BLUE, True)
    zero_x = 4.45
    scale = 0.53
    add_line(slide, zero_x, 2.17, 0.012, GRAY_LIGHT, height=3.18)
    bars = [
        (2.30, "Severance", -3.28, BLUE, "20 country-years"),
        (3.35, "No realignment", 2.23, FAINT, "4,335 country-years"),
        (4.40, "Richer entry", 3.43, ORANGE, "20 country-years"),
    ]
    for y, label, value, color, sample in bars:
        add_text(slide, 0.82, y - 0.02, 1.88, 0.31, label, 15, INK, True)
        add_text(slide, 0.82, y + 0.34, 1.88, 0.25, sample, 10.5, MUTED)
        width = abs(value) * scale
        x = zero_x - width if value < 0 else zero_x
        add_shape(slide, x, y, width, 0.48, color, radius=False)
        if value < 0:
            add_text(slide, x + 0.12, y + 0.06, width - 0.24, 0.32,
                     f"{value:+.2f}%", 16, WHITE, True)
        else:
            add_text(slide, x + width + 0.12, y + 0.06, 0.92, 0.32,
                     f"{value:+.2f}%", 16, color, True)
    add_text(slide, 2.63, 5.53, 1.45, 0.30, "Negative growth", 10.5, MUTED)
    add_text(slide, 4.42, 5.53, 1.45, 0.30, "Positive growth", 10.5, MUTED)
    add_shape(slide, 0.82, 6.00, 7.10, 0.55, OFFWHITE)
    add_text(slide, 1.02, 6.16, 6.70, 0.24,
             "Reference: no realignment combines all domestic-event rows.", 12, MUTED)
    add_metric_card(slide, 8.35, 1.74, 4.15, 1.42, "75.0%  vs  21.1%",
                    "Forward disruption after severance vs no realignment",
                    accent=BLUE, fill=BLUE_LIGHT, value_size=24, label_size=13)
    add_metric_card(slide, 8.35, 3.40, 4.15, 1.42, "60.0%  vs  14.4%",
                    "New acceleration onset after richer entry vs no realignment",
                    accent=ORANGE, fill=ORANGE_LIGHT, value_size=24, label_size=13)
    add_shape(slide, 8.35, 5.12, 4.15, 1.43, OFFWHITE)
    add_text(slide, 8.57, 5.33, 3.70, 0.24, "IMPOSED SEVERANCES", 10.5, BLUE, True)
    add_text(slide, 8.57, 5.70, 3.70, 0.33, "−3.29%  ·  83.3%", 22, INK, True)
    add_text(slide, 8.57, 6.11, 3.70, 0.24, "Mean growth · disruption rate", 12, MUTED)
    add_footer(slide, 4, "PRELIMINARY · Descriptive associations, not regression estimates. Small event cells; forward windows overlap.")
    add_notes(slide, """
[3:25–5:05]
These are the central model-free associations. Growth is measured as annual real GDP-per-capita growth averaged over complete forward windows from t plus one through t plus five. Bare severance country-years average minus 3.28 percent, compared with plus 2.23 without realignment. Bare richer-entry country-years average plus 3.43. The outcome frequencies point in the same direction: disruption occurs in 75 percent of severance observations versus 21.1 percent without realignment, while new acceleration onset occurs in 60 percent of richer-entry observations versus 14.4 percent.

The imposed-severance subset is especially useful because patron withdrawal reduces the concern that a country chose to leave in anticipation of decline. It retains mean growth of minus 3.29 percent and an 83.3 percent disruption rate. These cells are small, their windows overlap, and wrong-sign outcomes remain common. I read the pattern as a promising motivation for the formal tests. The next figure shows why timing and case selection matter.
""")

    slide = new_slide(prs)
    add_header(slide, 5, "Growth shifts around realignment",
               "Preliminary evidence", "Annual real GDP-per-capita growth · five years before and after interval start")
    slide.shapes.add_picture(
        str(FIGURES / "event_time_five_year.png"),
        Inches(0.67), Inches(1.68), width=Inches(12.0), height=Inches(4.16),
    )
    takeaways = [
        (0.75, BLUE, "Severance", "The average falls sharply after the interval start."),
        (4.73, ORANGE, "Richer entry", "The average rises, then levels off above zero."),
        (8.71, MUTED, "Dispersion", "Gray paths reveal pre-event breaks and wrong-sign cases."),
    ]
    for x, color, title, body in takeaways:
        add_text(slide, x, 6.03, 3.65, 0.25, title, 13, color, True)
        add_text(slide, x, 6.35, 3.65, 0.48, body, 12.5, MUTED,
                 line_spacing=1.05)
    add_footer(slide, 5, "PRELIMINARY · 46 episodes in 28 countries. Black means weight observed episodes equally; composition can change across event time.")
    add_notes(slide, """
[5:05–6:30]
This figure moves from five-year averages to annual trajectories. Each gray line is one country-event, and the black line is the equally weighted average of episodes observed at that event year. Year zero is the start of the realignment interval. Severance is on the left and richer entry on the right, with identical vertical scales.

The severance average declines sharply after year zero and reaches its lowest level around years two and three. The richer-entry average rises after year zero and then stabilizes at roughly three to four percent. Those average paths match H2. The gray lines also show why the aggregate means cannot carry the argument alone: some countries were already declining or accelerating, and others move in the opposite direction. Missing observations can change the composition of the mean. This is exactly why the case narratives and the dating robustness checks are central to the project.
""")

    slide = new_slide(prs)
    add_header(slide, 6, "Cuba: imposed severance, intact domestic power",
               "Supporting case · H2 negative")
    slide.shapes.add_picture(
        str(FIGURES / "case_cuba.png"), Inches(0.66), Inches(1.63),
        width=Inches(8.28), height=Inches(4.28),
    )
    add_shape(slide, 9.18, 1.63, 3.38, 4.28, BLUE_LIGHT)
    add_text(slide, 9.43, 1.88, 2.90, 0.25, "IMPOSED SEVERANCE", 10.5, BLUE, True)
    add_text(slide, 9.43, 2.25, 2.90, 0.40, "1989–1991", 25, INK, True)
    add_line(slide, 9.43, 2.83, 2.88, "C6DCE8")
    add_text(slide, 9.43, 3.07, 2.90, 0.40, "≈23% of GDP", 23, BLUE, True)
    add_text(slide, 9.43, 3.52, 2.90, 0.46, "Soviet subsidies before the shock", 13, MUTED)
    add_text(slide, 9.43, 4.18, 2.90, 0.44, "≈−33%", 28, BLUE, True)
    add_text(slide, 9.43, 4.68, 2.90, 0.35, "Contraction during 1990–93", 13, MUTED)
    add_text(slide, 9.43, 5.25, 2.90, 0.56, "Domestic power structure intact", 14,
             INK, True)
    add_shape(slide, 0.74, 6.12, 11.82, 0.72, OFFWHITE)
    add_text(slide, 0.96, 6.22, 11.38, 0.46,
             "Timing qualification: stagnation preceded severance; the collapse proper followed it. New-onset coding remains sensitive to the timing rule.",
             12.5, MUTED)
    add_footer(slide, 6, "PRELIMINARY · E005 / D019 · WDI growth and level · Case note: CUB_1989.md")
    add_notes(slide, """
[6:30–8:10]
Cuba is the strongest negative process-tracing case. Before the shock, Soviet subsidies were approximately 23 percent of GDP, alongside subsidized trade and security ties. The severance was imposed: the patron withdrew support and then ceased to exist. The power structure, ruling coalition, and state apparatus in Cuba remained intact. The collapse proper then ran from 1990 through 1993, with annual per-capita contractions reaching minus 15.3 percent and a cumulative contraction of roughly one third.

One timing detail matters. The registered D019 drawdown uses a 1985 peak, so its full peak-to-trough depth includes earlier stagnation. I therefore distinguish that stagnation from the 1990–93 collapse. Under the strict new-onset rule, Cuba can be classified as having a pre-existing disruption rather than a new consequence. That does not weaken the observed mechanism, but it does affect episode counts. The case supports the material-capability mechanism while also demonstrating why onset and drawdown measures must be reported separately.
""")

    slide = new_slide(prs)
    add_header(slide, 7, "Estonia displays the complete signed sequence",
               "Supporting case · H2 negative and positive")
    slide.shapes.add_picture(
        str(FIGURES / "case_estonia.png"), Inches(0.66), Inches(1.63),
        width=Inches(8.28), height=Inches(4.28),
    )
    add_shape(slide, 9.18, 1.63, 3.38, 4.28, OFFWHITE)
    add_text(slide, 9.43, 1.86, 2.90, 0.25, "SEVERANCE · 1990–94", 10.5, BLUE, True)
    add_text(slide, 9.43, 2.23, 2.90, 0.45, "−28.2%", 28, BLUE, True)
    add_text(slide, 9.43, 2.73, 2.90, 0.32, "D027 · 1990–95", 13, MUTED)
    add_line(slide, 9.43, 3.23, 2.88)
    add_text(slide, 9.43, 3.48, 2.90, 0.25, "RICHER ENTRY · 1995–2004", 10.5,
             ORANGE, True)
    add_text(slide, 9.43, 3.86, 2.90, 0.45, "6.78% / year", 26, ORANGE, True)
    add_text(slide, 9.43, 4.38, 2.90, 0.35, "A018 · 1998–2007", 13, MUTED)
    add_text(slide, 9.43, 5.07, 2.90, 0.55,
             "Acceleration begins inside the entry interval", 14, INK, True)
    add_shape(slide, 0.74, 6.12, 11.82, 0.72, OFFWHITE)
    add_text(slide, 0.96, 6.22, 11.38, 0.46,
             "Domestic transformation and the Soviet systemic shift coincide with severance; the within-case sequence carries more weight than a single before/after contrast.",
             12.5, MUTED)
    add_footer(slide, 7, "PRELIMINARY · E010 / E013 / D027 / A018 · WDI/Maddison · Accepted episode register")
    add_notes(slide, """
[8:10–9:35]
Estonia supplies the positive counterpart and a complete signed sequence. Soviet severance during 1990–94 coincides with D027, a 28.2 percent peak-to-trough disruption. Entry into the US and EU sphere then runs from the 1995 Europe Agreement through NATO and EU accession in 2004. The qualifying acceleration, A018, runs from 1998 through 2007 and averages 6.78 percent annually. Its onset falls inside the entry interval, which avoids Vietnam's timing problem.

Estonia is not a clean isolation of external realignment. Independence, domestic power transformation, and the Soviet systemic shift all overlap the negative phase. I would therefore use process tracing to establish which trade, subsidy, financial, and security flows changed, and compare Estonia with other post-Soviet republics whose domestic paths differed. The case is valuable because it shows both signs within one country and because the positive phase has a defensible temporal sequence.
""")

    slide = new_slide(prs)
    add_header(slide, 8, "Vietnam: realignment without the predicted timing",
               "Contradictory case · H2")
    slide.shapes.add_picture(
        str(FIGURES / "case_vietnam.png"), Inches(0.66), Inches(1.63),
        width=Inches(8.28), height=Inches(4.28),
    )
    add_shape(slide, 9.18, 1.63, 3.38, 1.92, BLUE_LIGHT)
    add_text(slide, 9.43, 1.86, 0.38, 0.30, "01", 13, BLUE, True)
    add_text(slide, 9.93, 1.84, 2.30, 0.32, "No collapse", 18, BLUE, True)
    add_text(slide, 9.43, 2.36, 2.88, 1.02,
             "Growth remained positive during the 1989–91 Soviet severance: +5.2%, +2.9%, +3.8%.",
             13.5, INK, line_spacing=1.08)
    add_shape(slide, 9.18, 3.78, 3.38, 2.13, ORANGE_LIGHT)
    add_text(slide, 9.43, 4.00, 0.38, 0.30, "02", 13, ORANGE, True)
    add_text(slide, 9.93, 3.98, 2.42, 0.32, "Acceleration first", 16, ORANGE, True)
    add_text(slide, 9.43, 4.51, 2.88, 0.95,
             "A069 begins in 1992, before US entry in 1994–95. Đổi Mới began in 1986.",
             13.5, INK, line_spacing=1.08)
    add_shape(slide, 0.74, 6.12, 11.82, 0.72, OFFWHITE)
    add_text(slide, 0.96, 6.22, 11.38, 0.46,
             "Research implications: measure dependence and replacement flows · separate domestic policy reform · distinguish economic-order from security-sphere entry.",
             12.5, MUTED)
    add_footer(slide, 8, "PRELIMINARY · E008 / E009 / A069 · E009 medium confidence; UN-voting validation flag · Case note: VNM_1989.md")
    add_notes(slide, """
[9:35–11:20]
Vietnam is the most informative anomaly. It experienced an imposed Soviet severance over 1989–91, but growth stayed positive: 5.2, 2.9, and 3.8 percent. No qualifying disruption followed. One plausible explanation is that Đổi Mới had already begun reorienting the economy toward East Asian markets, so the lost Soviet capabilities mattered less than the membership record alone would suggest.

The positive event also fails the timing rule. Acceleration A069 begins in 1992 and averages 6.13 percent through 2001, but the coded US entry begins in 1994. The acceleration therefore cannot be attributed to that entry. E009 itself is a partial, medium-confidence coding: Vietnam entered the US-led economic order without joining its security sphere, and UN voting does not converge. Vietnam gives me three concrete refinements: measure the degree of dependence and replacement flows, keep domestic policy reform analytically separate from power transformation, and distinguish economic-order entry from full security-sphere entry.
""")

    slide = new_slide(prs)
    add_header(slide, 9, "Peru: disruption without external realignment",
               "Contradictory case · H3 and scope")
    slide.shapes.add_picture(
        str(FIGURES / "case_peru.png"), Inches(0.66), Inches(1.63),
        width=Inches(8.28), height=Inches(4.28),
    )
    add_shape(slide, 9.18, 1.63, 3.38, 4.28, OFFWHITE)
    add_text(slide, 9.43, 1.88, 2.90, 0.25, "D064 · 1985–93", 10.5, BLUE, True)
    add_text(slide, 9.43, 2.25, 2.90, 0.43, "−31.2%", 28, BLUE, True)
    add_text(slide, 9.43, 2.74, 2.90, 0.33, "Peak-to-trough output", 13, MUTED)
    add_text(slide, 9.43, 3.32, 2.90, 0.43, "7,482%", 26, INK, True)
    add_text(slide, 9.43, 3.81, 2.90, 0.33, "Inflation in 1990", 13, MUTED)
    add_line(slide, 9.43, 4.35, 2.88)
    add_text(slide, 9.43, 4.60, 2.90, 0.52, "No coded external realignment", 16,
             INK, True)
    add_text(slide, 9.43, 5.23, 2.90, 0.42,
             "The 1992 deep transformation follows the crisis", 13, MUTED)
    add_shape(slide, 0.74, 6.12, 11.82, 0.72, OFFWHITE)
    add_text(slide, 0.96, 6.22, 11.38, 0.46,
             "Required scope condition: H1–H3 address changes of rulers, rules, power, and alignment; they do not imply immunity from paradigm-level domestic policy shocks.",
             12.5, MUTED)
    add_footer(slide, 9, "PRELIMINARY · PER has no external-realignment episode in the current register · Outcome: WDI · Hard case retained by design")
    add_notes(slide, """
[11:20–12:55]
Peru challenges a broad necessity reading of H3. D064 records a 31.2 percent peak-to-trough contraction and inflation above 7,000 percent in 1990, without a coded external realignment. The crisis begins under García's domestic policy program, before Fujimori's 1990 turnover and before the 1992 power-structure and apparatus transformation. The sequence rules out the later institutional transformation as an explanation of the initial collapse.

I would keep Peru as a hard case. Its implication is that the hypotheses need an explicit scope condition: changes of rulers, rules, effective power, and alignment are the political events under test; paradigm-level domestic policy shocks form a separate category. With that scope condition, Peru does not directly falsify narrow H1. It does falsify any broader claim that all major disruption requires realignment. The next stage must code policy change systematically enough that this defense cannot become an ad hoc exemption.
""")

    slide = new_slide(prs)
    add_header(slide, 10, "A sharper test of material capabilities",
               "Conclusion")
    columns = [
        (0.72, BLUE_LIGHT, BLUE, "WHAT WE SEE", [
            "Severance: weaker growth and more disruption",
            "Richer entry: stronger growth and more acceleration",
            "Imposed severances retain the negative pattern",
        ]),
        (4.78, ORANGE_LIGHT, ORANGE, "WHAT ANOMALIES TEACH", [
            "Dating and pre-existing outcomes matter",
            "Replacement flows can absorb severance",
            "Domestic policy shocks require explicit treatment",
        ]),
        (8.84, GRAY_LIGHT, INK, "NEXT STAGE", [
            "Estimate country and year fixed-effects models",
            "Complete matched comparisons and process tracing",
            "Measure market, capital, technology, energy, subsidy, and security flows",
        ]),
    ]
    for x, fill, accent, title, bullets in columns:
        add_shape(slide, x, 1.68, 3.72, 3.96, fill)
        add_text(slide, x + 0.23, 1.95, 3.25, 0.27, title, 11, accent, True)
        for index, bullet in enumerate(bullets):
            y = 2.48 + index * 0.94
            add_text(slide, x + 0.23, y, 0.20, 0.35, "•", 18, accent, True)
            add_text(slide, x + 0.53, y, 2.91, 0.76, bullet, 14.5, INK,
                     line_spacing=1.06)
    add_shape(slide, 0.72, 5.98, 11.84, 0.78, NAVY)
    add_text(slide, 1.00, 6.08, 11.28, 0.58,
             "Payoff: identify when political change produces economic discontinuity—and when it leaves trajectories intact.",
             15, WHITE, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    add_footer(slide, 10, "All empirical findings remain preliminary. Anomalous cases remain in the data and guide the next stage.")
    add_notes(slide, """
[12:55–14:10]
The preliminary evidence gives the project a clear empirical foundation. The aggregate signs match the realignment predictions, and the imposed-severance pattern is especially encouraging. The anomalies are equally useful: they identify the measurements and scope conditions that the formal stage must address.

The next stage has three priorities. First, estimate the country and year fixed-effects models with alternative dating and outcome definitions. Second, complete matched comparisons and process tracing so that the sequence of events carries the causal interpretation. Third, measure the proposed mechanism directly: market access, capital, technology, energy prices, subsidies, and security guarantees. The payoff is an account of economic discontinuity that can explain both major breaks and cases where conspicuous political events leave economic trajectories intact. I will stop here and welcome your criticism, especially on case coding and the proposed scope conditions.
[14:10–15:00] Reserve for initial questions and transitions.
""")

    slide = new_slide(prs)
    add_header(slide, 11, "Appendix: interval dating changes the onset results",
               "Robustness · backup")
    slide.shapes.add_picture(
        str(PAPER / "figures" / "step6_interval_dating_mixed_preliminary.png"),
        Inches(1.27), Inches(1.57), width=Inches(10.8), height=Inches(5.4),
    )
    add_footer(slide, 11, "PRELIMINARY · Severance endpoint growth: +2.70%. Richer-entry acceleration onset: 13.0% at midpoint and 13.6% at endpoint.")
    add_notes(slide, """
Backup slide. Use this if asked about dating sensitivity. Alternative interval dates move the forward windows and can change paired-event classification. Severance mean growth rises from minus 3.28 percent at interval starts to plus 2.70 at endpoints. Richer-entry growth remains positive, but its new-acceleration-onset rate falls from 60 percent at starts to approximately 13 percent at midpoints and endpoints. Growth levels and onset rates therefore respond differently to the dating convention.
""")

    slide = new_slide(prs)
    add_header(slide, 12, "Appendix: case selection and the strongest patterns",
               "Robustness · backup")
    slide.shapes.add_picture(
        str(PAPER / "figures" / "step6_case_selection_mixed_preliminary.png"),
        Inches(1.27), Inches(1.57), width=Inches(10.8), height=Inches(5.4),
    )
    add_footer(slide, 12, "PRELIMINARY · Excluding systemic shifts leaves only five bare-severance observations; imposed severance remains negative but historically clustered.")
    add_notes(slide, """
Backup slide. Use this if asked about open cases, systemic shifts, or imposed severance. Excluding open cases removes unresolved classifications rather than reassigning them to no realignment. Excluding systemic shifts removes episodes associated with changes in the wider distribution of capabilities, especially the Soviet collapse; only five bare-severance observations remain, so their positive mean growth is highly fragile. The imposed-severance subset retains negative mean growth and high disruption, but it is small and historically clustered.
""")

    if len(prs.slides) != 12:
        raise AssertionError("Expected ten main slides and two appendix slides")
    prs.save(OUTPUT)
    return prs


def validate_output():
    with zipfile.ZipFile(OUTPUT) as archive:
        bad_file = archive.testzip()
        if bad_file:
            raise ValueError(f"Corrupt PPTX member: {bad_file}")
        notes = [name for name in archive.namelist()
                 if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")]
        if len(notes) != 12:
            raise ValueError(f"Expected 12 speaker-note pages, found {len(notes)}")
    check = Presentation(OUTPUT)
    if len(check.slides) != 12:
        raise ValueError("Saved presentation has the wrong slide count")
    tolerance = Inches(0.02)
    for index, slide in enumerate(check.slides, start=1):
        for shape in slide.shapes:
            if shape.left < -tolerance or shape.top < -tolerance:
                raise ValueError(f"Negative shape position on slide {index}")
            if shape.left + shape.width > check.slide_width + tolerance:
                raise ValueError(f"Shape exceeds right edge on slide {index}")
            if shape.top + shape.height > check.slide_height + tolerance:
                raise ValueError(f"Shape exceeds bottom edge on slide {index}")
        if not slide.notes_slide.notes_text_frame.text.strip():
            raise ValueError(f"Missing speaker notes on slide {index}")
    print(f"Validated {OUTPUT.relative_to(ROOT)}: 12 slides, 12 speaker-note pages")


def main():
    prepare_graphics()
    build_deck()
    validate_output()


if __name__ == "__main__":
    main()
