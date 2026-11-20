# External Realignment and Economic Discontinuities — Thesis Repository

**Panel:** 73 countries × 1945–2019 (5,475 country-years) · **Design:** mixed-methods
(panel descriptive layer → regression layer → matched comparative cases)

This repository contains the complete data pipeline, coding record, and paper draft for a
thesis on whether **external realignment** — a state entering or leaving a great power's
sphere of influence — causes **major economic discontinuities** (output collapse /
disruption, or sustained take-off / acceleration), and how this interacts with domestic
political change. China is excluded from the design by construction.

---

## 1. The project in one paragraph

The framework separates five questions: *who governs, how political power is organized,
through which institutions it is exercised, where the state stands internationally, and what
outcomes follow*. The panel codes every country-year on domestic political events
(leader turnover, coalition change, formal regime change, transformations of the power
structure, apparatus restructuring) and external realignment episodes (severance from /
entry into the US-led, USSR/Russian, or Chinese spheres), then asks whether realignments
are followed by signed economic discontinuities. Core hypotheses (see `docs/Cases.md` and
`paper/draft2.tex`): **H1** — domestic political change alone (turnover, formal regime
change) does not produce discontinuities; **H2** — severance from a sphere causes
disruption, entry into a richer sphere causes acceleration; **H3** — the effect is
confounded when domestic deep transformation coincides with realignment. Every coding rule
is registered *before* looking at outcomes (`docs/thresholds.md`, `docs/Coding_Protocol.md`),
and every judgment-heavy category uses a "≥2 indicator families within a 3-year window" rule.

---

## 2. Repository map

| Path | What it is |
|---|---|
| `docs/` | **All documentation lives here** — start with `ROADMAP.md` for status. |
| `code/` | All Python scripts (run with `venv/bin/python`). Naming: `build_*` constructs datasets, `screen_*` detects candidate events, `audit_*` validates outputs (exit 0 = pass), `analyze_*` computes results, `plot_*` produces figures. |
| `data_raw/` | Original downloaded sources, kept untouched (WDI, Maddison, WEO, Archigos, COW alliances, DPI2020, ATOP, GSDB, CCP, IMF DOTS). |
| `data_clean/` | Project-generated CSVs — the working datasets (breakdown in §3 below). |
| `case_notes/` | 38 markdown case notes: per-episode evidence and reasoning, regional batch notes (with documented no-realignment determinations), and Step 4 regional sweeps. |
| `paper/` | LaTeX thesis drafts (`draft2.tex` is the current draft), bibliography, and `paper/figures/` (all generated figures). |
| `presentations/` | Slide decks and build scripts. |
| `venv/` | Project virtual environment — **always** run scripts as `venv/bin/python code/<script>.py`. |

---

## 3. Data: what exists and where

### 3.1 Raw sources (`data_raw/`) — originals, never edited

Full provenance table with versions and bib keys: **`docs/DATA_SOURCES.md`**.

| Source | File(s) | Coverage | Used for |
|---|---|---|---|
| World Bank WDI | `data_raw/WDI/` | 1960–2024 | Primary outcome series (GDP pc, growth, inflation) + controls (oil rents, population, investment) |
| Maddison Project 2023 | `data_raw/mpd2023_*` | 1–2022 | Long-run GDP pc; fills Cuba, North Korea, pre-1990 post-Soviet gaps |
| IMF WEO (API pull) | `data_raw/WEO/` | 1980–2019 | Fallback for politically censored years (Venezuela collapse) |
| Archigos 4.1 | `data_raw/Archigos_*` | 1875–2015 | Leader entry/exit → `Turnover` (post-2015 hand-coded) |
| DPI2020 | `data_raw/DPI2020.csv` | 1975–2020 | Coalition change |
| COW Formal Alliances 4.1 | `data_raw/version4.1_csv/` | 1816–2012 | Alliance ties (F1) |
| ATOP 5.1 | `data_raw/ATOP/` | 1815–2018 | Alliance ties past COW's 2012 endpoint |
| GSDB Release 5 + GSDB-FS | `data_raw/GSDB-R5/`, `data_raw/GSDB-FS/` | 1949–2025 | Sanctions/coercion episodes (F4) |
| CCP Chronology of Constitutional Events v6 | `data_raw/CCP/` | 1789– | Candidate catalogue for formal regime change |
| IMF DOTS | `data_raw/IMF_DOT.csv` | 1947– | Bilateral trade shares with patrons (F2) |
| UN ideal points (via COW codes) | — | 1946– | Validation layer only: convergence/divergence after episodes |

Known coverage gaps (flagged in coding, not hidden): North Korea and Cuba are largely
Maddison-estimates only; post-Soviet series start ~1990 by design; Archigos ends 2015;
WEO Venezuela figures are staff estimates.

### 3.2 Clean datasets (`data_clean/`) — project-generated, final unless marked PRELIMINARY

**Panel backbone**

| File | Content |
|---|---|
| `countries.csv` | The 73 panel countries (ISO3, name, region, coding window, data notes) |
| `panel_spine.csv` | 5,475 country-year rows (1945–2019), the untouched merge template |
| `outcomes.csv` | GDP pc / growth / inflation per country-year with per-cell provenance flags and seam flags (WDI > Maddison > WEO hierarchy) |
| `controls_preliminary.csv` | WDI oil rents, population, gross capital formation — ⚠️ PRELIMINARY |

**External realignment layer (Step 3, final)** — the thesis's core treatment variable:

| File | Content |
|---|---|
| `episodes.csv` | **73 episodes (E001–E073): 46 entry, 25 severance, 2 severance_threat**, 1945–2019, with patron, interval coding, voluntariness, systemic-shift flag, sources |
| `episode_sources.csv` | One row per episode: anchor sources per judgment area, quality grade (A 64 / B 7 / C 2), verification status |
| `realignment_candidates.csv` | 128 screen candidates, all resolved (53 matched, 75 documented rejections) |
| `sphere_roster_screen.csv` | 6,747 country-year-sphere roster rows (screen basis) |
| `trade_shares.csv` | 24,516 rows: trade share with each patron, 1948–2023 (DOTS) |
| `alliance_signals.csv` | 637 patron co-membership spells (ATOP; COW cross-check) |
| `sanctions_signals.csv` | 405 patron-sender sanction cases (GSDB-R5) |
| `bloc_membership.csv` | Hand-built treaty dates: 8 blocs, 63 countries, 113 rows |
| `r5_reference.csv` | Regional GDP-pc medians + patron series for the richer-sphere (R5) rule |
| `idealpoint_distances.csv` | 12,572 dyad-years vs the three patrons (validation) |
| `sphere_deepening_events.csv` | 91 within-sphere deepening records — ⚠️ **PLOTTING ONLY, PRELIMINARY**; not an analytical classification |

**Domestic political layer (Step 4, final with documented evidence gaps)**:

| File | Content |
|---|---|
| `turnover.csv` | 904 leader-replacement events, 72 countries (Switzerland intentionally 0); post-2015 hand-coded and unverified — see `turnover_post2015_checklist.csv` |
| `coalition.csv` | 372 coalition changes, 67 countries (DPI2020; 1975+ only) |
| `regime_change.csv` | 5,475 rows: 458 positive country-years; 996 unknown-content years preserved as **missing, never zero** |
| `power_structure.csv` | 177 accepted transformation event-years, 64 countries (France 1988 missing/conditional) |
| `apparatus_restructuring.csv` | 121 accepted event-years, 62 countries (Guyana 1980 missing/conditional) |
| `domestic_episodes.csv` | 300 structured substantive episode rows |
| `regime_candidate_review.csv` | 1,460 adjudicated formal candidates (459 accepted / 5 rejected / 996 unknown) |
| `domestic_source_register.csv` | 74 registered sources (65 primary legal texts, 8 official records, CCP) |

**Outcome episodes (Phase 2, final)**:

| File | Content |
|---|---|
| `disruption_episodes.csv` | 93 episodes / 60 countries (D1 ≥15% contraction in ≤5y, D2 ≥3pp deceleration sustained ≥3y, D3 inflation ≥500%) |
| `acceleration_episodes.csv` | 69 episodes / 54 countries (HPR-style sustained take-off filter) |

**Panel assembly + analysis (Steps 5–6, ⚠️ ALL PRELIMINARY)** — every file carries a
`_preliminary` name and an `analysis_status=preliminary` field:

| File | Content |
|---|---|
| `panel_preliminary.csv` | 5,475 rows × 55 cols: outcomes + controls + all treatments merged; includes start/midpoint/end date variants |
| `realignment_event_codings_preliminary.csv` | All 73 episodes with panel status and review flags |
| `disruption_years_preliminary.csv` | Exact annual D1–D3 union (572 country-years) |
| `step6_country_year_cells_preliminary.csv` | 4,380 analysis-period country-years classified into the 3×3 design cells |
| `step6_cell_frequencies_preliminary.csv`, `step6_realignment_outcomes_preliminary.csv` | Cell frequencies and episode-date outcome summaries |
| `baseline_cell_contrasts_preliminary.csv`, `baseline_contrast_sensitivity_preliminary.csv`, `baseline_contrast_leave_one_country_out_preliminary.csv` | Preliminary contrasts with wild-cluster bootstrap inference |
| `cultural_regions_plotting_preliminary.csv` | Plotting metadata only |

**Rule of thumb:** anything with `_preliminary` in the name (or `analysis_status =
preliminary` inside) is an interim build that will be re-run after the open items in
`docs/OPEN_ISSUES.md` are ruled on. Everything else is the accepted coding state, each with
a passing audit.

---

## 4. Documentation guide (`docs/`)

Start here, in this order:

1. **`ROADMAP.md`** — current status of all 9 pipeline steps (what is done, what remains).
2. **`DATA_SOURCES.md`** — raw-source manifest with versions and coverage.
3. **`Coding_Protocol.md`** — every variable's coding rule (the methodology contract).
4. **`thresholds.md`** — outcome thresholds registered before any coding, with rationale.
5. **`Cases.md`** — case-study selection logic (post-Soviet cluster, Cuba, Koreas/Vietnam, Venezuela...).
6. **`Core_Concepts.md`** — theoretical vocabulary and source anchors.
7. **`PHASE2_LOG.md` / `PHASE3_LOG.md`** — running methods logs: every decision, bug, fix, and convention.
8. **`STEP3_AUDIT.md`, `STEP4_AUDIT.md`, `STEP5_AUDIT_PRELIMINARY.md`** — audit reports (all exit 0).
9. **`EPISODE_SOURCES.md`** — source register for all 73 realignment episodes.
10. **`OPEN_ISSUES.md`** — items awaiting your ruling (must be resolved before final analysis).
11. **`STEP6_PRELIMINARY.md`, `SPHERE_DEEPENING.md`** — preliminary-results report; plotting-only layer.

---

## 5. Status at a glance

- **Done:** data acquisition; outcome series + disruption/acceleration screens; turnover and
  coalition variables; full realignment episode coding (73 episodes, fully sourced, audited);
  full domestic-event sweep (regime change / power structure / apparatus, audited).
- **Preliminary (flagged):** panel assembly and the descriptive Step 6 layer — mixed,
  non-causal diagnostics, *no hypothesis verdict claimed*.
- **Remaining (see `ROADMAP.md`):** Step 7 regression layer + robustness; Step 8 matched
  comparative cases + double-coding (κ ≥ 0.7); Step 9 write results into `paper/draft2.tex`.

## 6. How to run

```bash
# every script runs against the project venv from the repo root
venv/bin/python code/build_outcomes.py          # example: rebuild a dataset
venv/bin/python code/audit_episodes.py          # example: validate an output (exit 0 = pass)
venv/bin/python code/plot_country_timeline.py   # example: regenerate a figure → paper/figures/
```

Audits fail closed (nonzero exit) on any inconsistency; treat a red audit as a stop sign,
not background noise.
