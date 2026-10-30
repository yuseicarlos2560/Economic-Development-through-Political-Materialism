# Phase 2 Methods Log

Running record of every step, result, decision, and problem encountered while building
the outcome data. Newest entries last. Related documents: `docs/thresholds.md`
(registered thresholds), `docs/Coding_Protocol.md` (rules), `docs/DATA_SOURCES.md`
(data provenance).

---

## 2026-10-30 — Outcome series construction (`code/build_outcomes.py`)

**What:** merged WDI + Maddison 2023 + WEO onto `data_clean/panel_spine.csv`
(73 countries × 1945–2019 = 5,475 rows) following the source hierarchy in
Coding_Protocol §7.1: WDI > Maddison for GDP pc levels; WDI > Maddison > WEO for
growth; WDI > WEO for inflation. Provenance flag per cell; seam flag where the
level source changes between consecutive years.

**Output:** `data_clean/outcomes.csv`.

**Coverage:**
- GDP pc: 4,814/5,475 cells (87.9%) — 3,608 WDI, 1,206 Maddison. Every country has
  some coverage. Least covered: PRK 30 cells (Maddison only), post-Soviet states ~41
  (series start 1990 by design).
- Growth: 4,765 cells (87.0%) — 3,536 WDI, 1,229 Maddison. The WEO total-GDP
  fallback was never needed (Venezuela's collapse years are in WDI).
- Inflation: 3,385 cells (61.8%) — gaps are pre-1960 (WDI starts 1960) and Cuba.
- 69 seam cells, all in the 1990s post-Soviet transition.

**Problems hit:**
1. *WDI starts in 1960* — first run crashed with KeyError on 1945–59 columns.
   Fixed by restricting WDI extraction to 1960–2019; pre-1960 cells come from
   Maddison only.
2. *PEP 668 externally-managed Python* — system Python refuses pip installs.
   All analysis runs in `venv/` (`venv/bin/python`).
3. *WEO bulk download URLs dead* — IMF retired the old .ashx files (404 "Blob not
   found"). The new IMF Data Portal SDMX API works without a key; WEO indicators
   were pulled per-indicator per-country-group via the API instead.
4. *ATOP blocks scripted downloads* (403 for all agents) — moved to the
   manual-download list in DATA_SOURCES.md.

## 2026-10-30 — Source-agreement check (justification for the hierarchy)

Before any episode coding: across 3,398 country-years where WDI and Maddison
overlap (70/73 countries), growth-rate correlation = 0.90, median absolute
difference = 0.49 pp, sign disagreement = 6.2%. Level ratio Maddison/WDI for
identical country-years ranges 0.44–13.84 (median 1.32) — levels are
incommensurable across sources, growth rates are not. This is now Coding_Protocol
§7.1 with citations (Johnson et al. 2013; Feenstra, Inklaar & Timmer 2015; both
added to `paper/bib.bib`). This check compared raw series only; it reveals nothing
about which episodes the screens flag.

## 2026-10-30 — Disruption screen (`code/screen_disruptions.py`)

**What:** implements D1 (≥15% peak-to-trough within ≤5 years, within-source levels),
D2 (growth ≥3 pp below prior 5-yr average for ≥3 consecutive years), D3 (inflation
≥500%). D4 (sudden stop) is qualitative and deferred to Phase 3 case work
(column present, all False).

**Calibration anchors (thresholds.md) — all pass:**
- Greece 2006–2015 in (−26.2%, D1+D2). Spain 2007–13, UK 2016–19, Mexico 1994–95,
  Vietnam 1989–91: all correctly out. Korea 1997–98 also out (V-shaped recovery).

**Problems hit:**
1. *Chaining bug.* First version merged same-country episodes with gap ≤ 1 year,
   chaining Venezuela 1978–2019 into one 41-year episode. First fix attempt
   (segmentation at gaps > 2 clean years) did not help because D1 windows were
   pre-collapsed into one min-to-max country episode *before* segmentation.
   Root cause: the collapse step, not the segmentation. Fixed by keeping each
   qualifying D1 window as a separate entry and letting segmentation merge.
2. *Decision (user, 2026-10-30):* option 1 — the panel indicator is the union of
   flagged years (merging irrelevant); the episode table splits at > 2 consecutive
   clean years. Recorded in Coding_Protocol §7.

**Result:** 93 disruption episodes across 60 countries (Latin America 40, Europe 28,
post-Soviet 19, East Asia 6). Venezuela now splits
into four historically sensible episodes: 1978–85 (−23.3%, debt crisis),
1988–89 (−16.1%), 1997–2003 (−22.7%, incl. 2002–03 oil strike), 2011–19
(−60.1%, with hyperinflation 65,374% in 2018 and 19,906% in 2019 flagged by D3).

## 2026-10-30 — Acceleration screen (`code/screen_accelerations.py`)

**What:** HPR-faithful — 8-year windows, average growth ≥3.5% (A1+A2), ≥2 pp above
the prior 8-year regime (A3), post-episode level above pre-episode maximum computed
within a single source (A4, per Protocol 7.1c). Overlapping windows merge into
longer episodes.

**Calibration anchors — all pass:** KOR 1968–76 (8.9%) and 1982–90 (9.3%) — two
episodes, not one, because the early-80s recession breaks the window; 1968 is the
earliest possible start since A3 needs 8 prior years of data (WDI starts 1960).
VNM 1992–2001 (6.1%, Đổi Mới). CHL 1984–98. PRK: none, as expected.

**Result:** 69 acceleration episodes across 54 countries.

## Pending / known limitations

- D4 sudden-stop coding (Phase 3, qualitative, from case literature).
- Cuba inflation gaps; North Korea = Maddison estimates only (low confidence, will
  be flagged in `episodes.csv`).
- Korea's acceleration start (1968) is a data-availability boundary, not a claim
  that growth began in 1968.
- Post-Soviet pre-1990 cells are empty by design; USSR-era episodes for successor
  states use the Soviet aggregate only if needed in case narratives.
- Robustness re-runs per Protocol 7.1d (WDI-only vs Maddison-only screens) not yet
  executed.
- Next: user reviews the episode lists against case knowledge; then turnover merge
  (Archigos) and realignment episode coding (Phase 3 per Coding_Protocol §6).
