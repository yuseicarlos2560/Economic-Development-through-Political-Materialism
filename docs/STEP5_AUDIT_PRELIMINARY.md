# Step 5 audit — preliminary panel assembly

**Date:** 4 Nov 2026 | **Status:** PRELIMINARY COMPLETE; no open substantive coding issue is resolved by this merge.
**Scripts:** `code/build_panel_preliminary.py`, `code/audit_panel_preliminary.py`; annual preliminary disruption support added to `code/screen_disruptions.py`.

## Outputs

Every Step 5-specific output has a `_preliminary` filename and an `analysis_status = preliminary` field.

- `data_clean/panel_preliminary.csv`: 5,475 unique country-years, 73 countries, 1945–2019, 55 columns.
- `data_clean/controls_preliminary.csv`: WDI oil rents, population, and gross capital formation.
- `data_clean/realignment_event_codings_preliminary.csv`: all 73 episodes with panel status, interval start/midpoint/end years, R5 classification, and review flags.
- `data_clean/disruption_years_preliminary.csv`: exact annual union of the D1–D3 screen, separate from segmented episode ranges.
- `data_clean/panel_spine.csv` remains the untouched merge template.

## Assembly conventions

- Current accepted Step 1–4 values are merged without substantive re-adjudication.
- `RegimeChange`, `PowerStructure`, apparatus, and coalition missingness is preserved. Unknown or conditional evidence is never converted to zero.
- Post-2015 turnover values are retained from the current build but marked `hand_unverified`; Switzerland retains its collective-executive exclusion.
- `severance` and `entry` are interval-start compatibility indicators. Explicit `_midpoint` and `_end` variants are supplied for every consummated realignment; midpoint is the floor of the mean year. No variant is privileged as a final causal date.
- `severance_threat` is separate and never enters `severance`. Egypt and Yugoslavia are calibration-only and do not enter panel treatments.
- `entry` covers all coded entries. `entry_richer` is the H2/R5 subset; `imposed_severance` is the stronger causal-identification subset. Equivalent midpoint/end variants are included.
- R5 was checked at both interval endpoints where data exist. No classification changes across endpoints. The endpoint reference is stored because it supplies the 1949 comparison for the 1945–49 Soviet formation entries. Seven poorer-sphere Soviet entries are therefore outside `entry_richer`.
- Paired and simultaneous events remain separate. Multiple patrons and episode IDs are retained rather than overwritten.
- `disruption` uses 572 exact flagged country-years, not the 575 years implied by filling every segmented episode span; three clean-gap years remain unflagged. D4 sudden-stop coding remains pending.
- `acceleration` covers 788 country-years within the 69 continuous screened episodes.
- Controls use WDI `NY.GDP.PETR.RT.ZS`, `SP.POP.TOTL`, and `NE.GDI.TOTL.ZS`, without cross-source splicing.

## Coverage

| Measure | Count |
|---|---:|
| Turnover events | 904 |
| Coalition changes | 372 |
| RegimeChange positive / missing years | 458 / 996 |
| PowerStructure positive / missing years | 177 / 1 |
| Apparatus restructuring positive / missing years | 121 / 1 |
| Severance start-year events | 23 |
| Entry start-year events | 45 |
| Richer-entry start-year events | 38 |
| Imposed-severance start-year events | 9 |
| Severance threats | 2 |
| Oil rents / population / investment nonmissing cells | 3,014 / 4,380 / 3,128 |
| Analysis-period rows, 1960–2019 | 4,380 |
| Analysis-period nonmissing growth | 4,036 |

## Verification

`venv/bin/python code/audit_panel_preliminary.py` exits 0 with 0 FAIL. It checks spine integrity and order, exact source-table fidelity, domestic missingness, all three realignment date variants, threat exclusion, R5 values, paired Cuba 1960 events, Venezuela's 2002/2009/2017 interval variants, and exact annual outcome-event coverage.

Regression checks also pass:

- `venv/bin/python code/audit_episodes.py`: 0 FAIL; the three established warning classes remain.
- `venv/bin/python code/audit_domestic.py`: 0 FAIL.
- Re-running `screen_disruptions.py` left `disruption_episodes.csv` byte-for-byte unchanged.

## Remaining limits

This is an analysis-ready preliminary panel, not a final adjudicated dataset. Step 3 conventions and E020/E059/E067 remain open; MDA/UZB remain no-episode determinations under review; Step 4 substantive coding awaits user review and double-coding; all non-Swiss post-2015 turnover rows remain unverified; and D4 is not coded. Window-edge realignments are flagged, not silently deleted. No Step 6 frequencies or causal findings are reported here.
