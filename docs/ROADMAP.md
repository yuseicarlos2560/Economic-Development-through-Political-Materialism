# Roadmap — Remaining Work (as of 2026-11-02)

Status of the full plan after Phase 2 (outcome screens) was completed and reviewed.
Each step lists where it is supported: `paper/draft2.tex` §5–6 (Methodology/Data),
`docs/Coding_Protocol.md` (CP), `docs/DATA_SOURCES.md` (DSM).
Progress is logged step by step in `docs/PHASE2_LOG.md` (outcomes) and
`docs/PHASE3_LOG.md` (from step 1 below onward).

## Done

- Phase 0: scaffolding, `docs/thresholds.md` registered, panel spine (73 countries × 1945–2019).
- Phase 1: data acquisition (WDI, Maddison 2023, WEO via API, Archigos, COW alliances,
  UN ideal points). Manual items pending, see step 2.
- Phase 2: `data_clean/outcomes.csv` (WDI>Maddison>WEO hierarchy, CP §7.1);
  disruption screen (93 episodes/60 countries) and acceleration screen
  (69 episodes/54 countries); all calibration anchors pass; episode segmentation
  rule fixed (CP §7); user review of episode lists completed.

## Remaining

### Step 1 — Turnover merge (Archigos) — DONE (2026-11-02), pending checklist verification
- Coalition-change variable added same day via DPI2020 (`code/build_coalition.py`);
  1960–1974 gap and CHE gap documented in `docs/PHASE3_LOG.md`.
- **What:** `Turnover` indicator (leader replaced in year t) + manner-of-exit flag,
  1945–2015 from Archigos; 2016–2019 hand-coded with per-entry sources.
  Coalition change tracked separately (pending source decision).
- **Why:** β₃ in equation (1), the H1 control (draft2.tex:196); CP §2;
  draft2.tex:214, 232.
- **Output:** `data_clean/turnover.csv`, merged into the panel.

### Step 2 — Manual data acquisition (user tasks, fire early due to latency)
- ATOP (browser download, atopdata.org/data.html) — alliance coding past 2012.
- GSDB Release 4 (email GSDB@drexel.edu) — sanctions, treatment intensity.
- IMF DOTS (data.imf.org/DOT) — bilateral trade shares, the Δ-trade variable.
- CCP (comparativeconstitutionsproject.org) — constitutional events for RegimeChange.
- **Why:** CP §6 indicator families F1–F4; CP §3; DSM "Requires manual action".

### Step 3 — Realignment coding (severance/entry)
- **What:** fill `data_clean/episodes.csv` per rules R1–R6 (≥2 of 4 indicator
  families, 3-year windows, interval coding for gradual cases, voluntariness,
  richer-sphere criterion, systemic-shift flag). Start with the calibration
  episodes (CP §6): Yugoslavia 1948, Spain 1953, Cuba 1960 & 1989–91, Egypt
  1972–76, Vietnam 1989–95, Baltics 1991 & 2004, Venezuela 2002–17, Greece 2015.
  Validate against UN ideal points (divergence/convergence).
- **Why:** β₁, β₂ in equation (1), the H2 test (draft2.tex:203); CP §6;
  draft2.tex:216.
- **Depends on:** step 2 (ATOP, GSDB, DOTS). Judgment-heaviest step; done together.

### Step 4 — RegimeChange and PowerStructure coding
- **What:** `RegimeChange` from constitutional events (CP §3, uses CCP);
  `PowerStructure` per the four-dimension, ≥2-in-3-years rule (CP §4);
  apparatus restructuring for Table 1 row 2 (CP §5).
- **Why:** β₄, β₅ (draft2.tex:214); resolves the Venezuela crux determinately (CP §4).
- **Depends on:** step 2 (CCP) + case-document reading.

### Step 5 — Panel assembly
- **What:** merge outcomes + turnover + realignment episodes + controls
  (oil rents, population, investment share — already in our WDI download)
  onto `data_clean/panel_spine.csv`.
- **Why:** equation (1) dataset (draft2.tex:201, 234).

### Step 6 — Descriptive layer (no model)
- **What:** classify country-years into Table 1 cells; discontinuity frequencies
  per cell; mean growth after each realignment type.
- **Why:** draft2.tex §5.2 step 1 (line 191): cheap falsification before any regression.

### Step 7 — Regression layer + robustness
- **What:** equation (1), country and year fixed effects, lags, clustered SEs
  (extends Acemoglu et al. 2019). Robustness: per-source episode re-screens
  (CP §7.1d — still owed), alternative thresholds, exclude 1989–91,
  synthetic control for Venezuela and Cuba (draft2.tex:205).
- **Why:** draft2.tex §5.2 step 2 (lines 193–205).

### Step 8 — Comparative case layer + reliability
- **What:** matched pairs from `docs/Cases.md`, process tracing with the timing
  rule; double-code a random subset, Cohen's κ ≥ 0.7.
- **Why:** draft2.tex §5.1 (line 185), §5.3 reliability (line 218); CP principle 4.

### Step 9 — Write results into the paper
- Fill Table 1 and the regression table in `paper/draft2.tex`; keep logs current; commit.
