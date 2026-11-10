# Step 6 — PRELIMINARY descriptive results

**Date:** 4 Nov 2026 | **Status:** PRELIMINARY, model-free, descriptive, and non-causal. No open Step 3/4 issue is resolved by these results, and no Step 7 regression is reported.

## Preliminary artifacts

All Step 5/6-specific scripts, datasets, and reports use `_preliminary`; every generated CSV contains `analysis_status = preliminary`. Established Step 1–4 source datasets retain their original names and values.

- `code/analyze_step6_preliminary.py`
- `code/audit_step6_preliminary.py`
- `data_clean/step6_country_year_cells_preliminary.csv`
- `data_clean/step6_cell_frequencies_preliminary.csv`
- `data_clean/step6_realignment_outcomes_preliminary.csv`
- `code/plot_realignment_event_time.py`
- `data_clean/cultural_regions_plotting_preliminary.csv`
- `paper/figures/event_time/` (PNG/PDF event-time figures)
- `code/analyze_baseline_contrasts_preliminary.py`
- `code/analyze_baseline_contrast_sensitivity_preliminary.py`
- `code/audit_baseline_contrasts_preliminary.py`
- `code/plot_baseline_contrasts_preliminary.py`
- `data_clean/baseline_cell_contrasts_preliminary.csv`
- `data_clean/baseline_contrast_sensitivity_preliminary.csv`
- `data_clean/baseline_contrast_leave_one_country_out_preliminary.csv`
- `paper/figures/baseline_contrasts_primary_preliminary.{png,pdf}`
- `paper/figures/baseline_contrasts_secondary_preliminary.{png,pdf}`

## Registered preliminary rules

- Primary sample: 1960–2019, 73 countries, 4,380 country-years.
- Domestic rows: deep power/apparatus transformation; turnover/formal change only with known absence of deep transformation; four observed zeroes for no domestic event; otherwise `unknown`.
- External columns: severance; R5 richer entry; no realignment. Paired transitions, poorer entries, threats, and unknown domestic evidence remain separate.
- Growth means use complete forward windows t+1 through t+1/t+3/t+5. Disruption uses any exact annual D1–D3 flag in t+1..t+5. Acceleration uses a new episode onset in t+1..t+8. Incomplete horizons or wholly unobserved outcome windows are missing.
- Same-year and already-active outcomes are flagged, not presented as new effects. Forward windows overlap, especially for no-realignment country-years; observations are not independent.
- Scenarios: start/midpoint/end dates; exclusion of E020/E059/E067; exclusion of systemic-shift event-years; and imposed-only severance. Excluded event-years are removed, not relabelled as no-realignment observations.
- Disruption and acceleration are not mutually exclusive within these different forward windows. Rates need not sum to one.

## Baseline 3×3 cells: start-year coding

Growth is mean real GDP-per-capita growth over the following five years. Disruption and acceleration columns use their respective five-/eight-year forward windows. Denominators vary with outcome coverage; full denominators are in the CSV.

| Domestic event | External event | Country-years | Valid growth n | Mean growth % | Disruption rate % | Acceleration-onset rate % |
|---|---|---:|---:|---:|---:|---:|
| None | None | 2,654 | 2,119 | 2.19 | 22.8 | 13.1 |
| None | Severance | 5 | 5 | −1.67 | 80.0 | 20.0 |
| None | Richer entry | 7 | 7 | 2.73 | 42.9 | 71.4 |
| Turnover/formal only | None | 836 | 768 | 2.49 | 20.8 | 17.4 |
| Turnover/formal only | Severance | 2 | 2 | −6.03 | 100.0 | 0.0 |
| Turnover/formal only | Richer entry | 3 | 3 | 3.86 | 66.7 | 100.0 |
| Power/apparatus transformation | None | 139 | 131 | 0.84 | 37.1 | 37.7 |
| Power/apparatus transformation | Severance | 11 | 11 | −5.10 | 81.8 | 60.0 |
| Power/apparatus transformation | Richer entry | 7 | 7 | 3.74 | 28.6 | 28.6 |

Three additional severance observations are paired with entry and excluded from the bare-severance cells. Three richer-entry observations have unknown domestic classifications. The small event cells must not be read as precise population estimates.

## Aggregate sensitivity

Each row aggregates domestic categories within the indicated external category. `N` is country-years; `G5` is mean five-year forward growth; `D5` and `A8` are forward disruption and acceleration-onset rates.

| Scenario | External category | N | G5 % | D5 % | A8 % |
|---|---|---:|---:|---:|---:|
| Start, current coding | No realignment | 4,335 | 2.23 | 21.1 | 14.4 |
| Start, current coding | Severance | 20 | −3.28 | 75.0 | 42.1 |
| Midpoint, current coding | Severance | 23 | −0.16 | 72.7 | 63.6 |
| End, current coding | Severance | 23 | 2.70 | 61.9 | 66.7 |
| Start, excluding open cases | Severance | 19 | −2.59 | 73.7 | 38.9 |
| Start, excluding systemic shifts | Severance | 5 | 2.53 | 40.0 | 25.0 |
| Start, imposed severance only | Severance | 6 | −3.29 | 83.3 | 33.3 |
| Start, current coding | Richer entry | 20 | 3.43 | 35.0 | 60.0 |
| Midpoint, current coding | Richer entry | 23 | 3.74 | 8.7 | 13.0 |
| End, current coding | Richer entry | 23 | 2.75 | 17.4 | 13.6 |
| Start, excluding open cases | Richer entry | 18 | 3.68 | 33.3 | 61.1 |
| Start, excluding systemic shifts | Richer entry | 16 | 3.37 | 31.3 | 50.0 |

The date variants change both event timing and whether simultaneous episodes are classified as paired, so N is not constant. The systemic-shift and imposed-only severance cells are especially small.

## Preliminary baseline-cell contrasts

`venv/bin/python code/analyze_baseline_contrasts_preliminary.py --bootstraps 1999` reports raw cell differences and saturated cell models with country and year fixed effects. Growth uses OLS; disruption and acceleration use linear probability models scaled to percentage points. The primary family contains 21 tests per estimator: six within-domestic-row external contrasts across three outcomes plus three H1 turnover/no-realignment contrasts. The secondary family contains 24 common-reference contrasts per estimator against no domestic event/no realignment.

Inference uses an unrestricted country-level wild cluster bootstrap-t with Webb weights and 1,999 replications. Holm p-values are adjusted separately within each family and estimator. Reported 95% bootstrap-t intervals are not multiplicity-adjusted. These are preliminary, exploratory, non-causal estimates; two- and three-country cells and intervals beyond logical probability-difference bounds are warnings about inferential support.

After Holm adjustment, the primary raw contrasts that remain significant are deep-transformation severance growth (−5.94 pp), turnover-only severance disruption (+79.19 pp; two countries), deep-transformation severance disruption (+44.70 pp), turnover-only severance acceleration (−17.38 pp; two countries), and turnover-only richer-entry acceleration (+82.62 pp; three countries). Fixed-effects significant contrasts are turnover-only severance disruption (+47.26 pp; two countries), turnover-only richer-entry acceleration (+55.33 pp; three countries), and the H1 turnover/no-realignment acceleration difference (+4.74 pp). The no-domestic-event severance and richer-entry contrasts do not survive Holm adjustment. H1 equivalence has not been tested; non-significance is not evidence of equivalence.

`code/analyze_baseline_contrast_sensitivity_preliminary.py` reports point-estimate sensitivity across all registered dating/exclusion scenarios and 73 leave-one-country-out refits. These files contain no new p-values. Non-estimable cells remain explicit with missing estimates. In particular, deep-severance growth changes sign in one-observation endpoint/systemic-excluded subsets, and turnover-only richer-entry acceleration falls sharply under midpoint/end dating. These checks reinforce the preliminary status.

## Episode timing audit

Under start-year coding, 23 severance and 23 richer-entry episodes fall inside 1960–2019:

- Severance: 14 have an outcome already active at the event, three are paired transitions, two show the signed outcome after the event, and four do not show it in the registered window.
- Richer entry: 14 have an outcome already active, three are paired transitions, three show a later acceleration onset, and three do not.

After excluding open cases and paired transitions, the start-date descriptive sets contain 19 severances and 18 richer entries. These counts demonstrate why the aggregate rates cannot be interpreted as clean causal episode effects. Cuba 1989 and Venezuela 2002 are explicitly marked as having ongoing disruption; Vietnam 1994 is marked as having an ongoing acceleration.

## Event-time growth figures

`venv/bin/python code/plot_realignment_event_time.py` generates one pooled figure and nine event-bearing cultural-group figures in `paper/figures/event_time/`, in both PNG and PDF. Each figure shows annual real GDP-per-capita growth from three, five, and eight years before through the same number of years after the realignment start. Severance and richer entry remain separate because their predicted signs differ. Gray lines are country-event trajectories at 0.5 opacity; black lines are equally weighted means of the episodes observed at each event year. Missing annual observations break lines and change the mean's composition; the figures report the per-year observation range.

The pooled figure contains 46 episodes in 28 countries. Paired transitions remain visible in their respective event-type panels. These are descriptive event-time profiles, not causal event-study estimates, and they do not resolve ongoing-outcome or date-sensitivity issues.

`data_clean/cultural_regions_plotting_preliminary.csv` assigns the 28 event countries to mutually exclusive, provisional plotting-only groups based on broad linguistic, historical, and regional-cultural context. The register is labelled `preliminary`, `plot_context_only`, and `provisional_plotting_only`; it is not an analytical variable and is not connected to the treatment, outcome, or Step 5–6 analysis files. Groups without eligible realignments are not plotted. Singleton black means simply reproduce the sole observed trajectory and are not independent aggregate evidence.

## Preliminary interpretation

- Start-year severance averages have the predicted negative growth sign and elevated disruption frequency; start-year richer entry has positive mean growth and a 60% acceleration-onset rate.
- These patterns are **not robust enough for a hypothesis verdict**. Severance mean growth approaches zero at midpoints, turns positive at endpoints, and is positive in the five-case systemic-shift-excluded subset.
- Wrong-sign and no-realignment outcomes remain visible: severance also has subsequent acceleration onsets, richer entry has subsequent disruptions, and no-realignment country-years are not outcome-free. These observations require policy-shock, war, commodity, financial-crisis, and process-tracing analysis rather than relabelling.
- The results are preliminary descriptive diagnostics, not estimates of β₁–β₅ and not evidence that either layer of the theory has passed its falsification test.

## Verification and limits

`venv/bin/python code/audit_step6_preliminary.py` exits 0 with 0 FAIL. It checks preliminary labels, domestic missingness, scenario denominators, every baseline aggregate, all 204 episode-date rows, window-edge indeterminacy, ongoing-outcome flags, and Cuba/Vietnam/Venezuela timing anchors. Step 5, Step 3, and Step 4 audits also exit 0.

`venv/bin/python code/audit_baseline_contrasts_preliminary.py` also exits 0. It checks all 90 main contrasts, 252 scenario rows, and 3,066 leave-one-country-out rows; preliminary labels; raw arithmetic identities; Holm adjustments; interval ordering; and exact reproduction of current-scenario point estimates.

D4 sudden stops remain uncoded; formal/substantive missingness and unverified post-2015 turnover remain unchanged; open coding judgments and independent double-coding remain unresolved. No results have been written into `paper/draft2.tex`.
