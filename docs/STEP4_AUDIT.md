# Step 4 audit — domestic political events

**Date:** 4 Nov 2026 | **Status:** COMPLETE with documented evidence gaps; substantive coding subject to user review.
**Scripts:** `code/screen_domestic.py`, `code/adjudicate_regime_candidates.py`, `code/build_domestic_events.py`, `code/audit_domestic.py` (exit 0; all checks PASS).

## Scope and non-contamination

The sweep covers all 73 panel countries over 1945–2019, including explicit negative determinations. The four regional case notes record legal/institutional evidence, process intervals, principal effective years, dimensions/components, confidence, and rejected candidates. Spain/France/UK calibration determinations are carried forward; the US remains non-panel calibration. No outcome series or expert-coded regime index was used to set candidates, dates, or acceptance.

## Sources and candidate coverage

`data_clean/domestic_source_register.csv` contains 74 unique source records: 65 primary legal texts (`P-text`), eight official institutional records (`I-official`), and the CCP v6 candidate dataset (`D`). Every formal candidate has a substantive reason, legal anchor, case-note reference, and resolving source IDs.

Formal-event review in `data_clean/regime_candidate_review.csv`:

- 1,414 mapped CCP candidates plus **46 documentary supplements** = **1,460 reviewed candidates**.
- 459 accepted candidates, producing **458 distinct positive country-years**.
- Five explicitly rejected candidates.
- **996 unknown amendment-content candidates**, preserved as unknown rather than rejected.
- No candidate remains `pending` or `calibration_review`.

The documentary supplement includes formal instruments absent from CCP, including Spain's 1947 Law of Succession and 1977 Political Reform Law, Croatia 1990, Slovenia 1991, Baltic restoration acts, post-Soviet independence acts, and documented coup/restoration orders. This corrects the false inference that a CCP-only ledger was exhaustive.

## Substantive episode record

`data_clean/domestic_episodes.csv` contains 300 structured rows:

| Category | Accepted | Conditional/unknown | Countries with accepted episodes |
|---|---:|---:|---:|
| Power structure | 177 | 1 (PS-FRA-02) | 64 |
| Apparatus restructuring | 121 | 1 (AR-GUY-02) | 62 |

Accepted events by region:

| Region | Power structure | Apparatus restructuring |
|---|---:|---:|
| Post-Soviet | 29 | 15 |
| Europe | 38 | 27 |
| Latin America | 98 | 69 |
| East Asia | 12 | 10 |

The nine panel countries with no accepted power-structure episode are BEL, CHE, DNK, FIN, IRL, ISL, LUX, NLD, and NOR. Their negative determinations are explicit in `case_notes/Step4_Europe.md`.

## Generated country-year outputs

All three outputs contain the full 5,475-row spine and preserve missing values:

- `data_clean/regime_change.csv`: **458 positive years**, 996 unknown-content years, five reviewed-negative candidate years, and 4,016 reviewed years with no formal candidate.
- `data_clean/power_structure.csv`: **177 positive event-years** across 64 countries; France 1988 is missing because PS-FRA-02 lacks proof of dimension (c).
- `data_clean/apparatus_restructuring.csv`: **121 positive event-years** across 62 countries; Guyana 1980 is missing because AR-GUY-02 lacks a sufficiently precise second component.

Unknown and conditional evidence is blank with an `evidence_status` explanation, never recoded as zero. No output is merged into the main panel; panel assembly remains Step 5.

## Internal checks

`venv/bin/python code/audit_domestic.py` reports **0 FAIL**:

- candidate-ledger integrity, country coverage, vocabularies, and years;
- final accepted/rejected/unknown disposition for every CCP and documentary candidate;
- a substantive reason, legal anchor, case-note reference, and valid source IDs on every candidate;
- unique episode IDs and valid panel countries;
- valid process intervals and in-window principal years (1944 starts retained where the effective threshold falls inside the window);
- at least two dimensions/components on every substantive episode;
- all 73 countries covered by substantive notes;
- complete, unique 5,475-row outputs with values in {0, 1, missing};
- exact correspondence between accepted candidates/episodes and positive country-years;
- exact correspondence between unknown candidates/conditional episodes and missing country-years;
- formal calibration anchors ESP 1977/1978, FRA 2008, HRV 1990, SVN 1991, and VEN 1999;
- power/apparatus calibration anchors ESP 1977, GBR 1950/2007, and FRA 1958/1959/2009;
- Venezuela power-structure anchors 2003/2009/2017, with 1999 formal-only;
- Spain 2011 explicitly rejected as `RegimeChange`;
- France 1988 and Guyana 1980 missing rather than positive or zero.

## Audit-time corrections

- Corrected AR-CZE-02's principal year to 1993, matching the effective fiscal-succession component.
- Added AR-MLT-01 to make the Malta independence determination explicit.
- Added the documentary formal-event supplement after the Spain 1977 cross-check exposed CCP-only omissions.
- Parser/audit fail closed on malformed rows, missing dimensions/components, duplicate IDs, source mismatches, and panel mismatches.
- Shared Czechoslovak records inherit dimensions/components from their referenced episode rather than being treated as empty rows.

## Verification limits

This is a complete, internally consistent coding workflow, not a claim that inaccessible historical evidence has been recovered or that every judgment has been independently double-coded. The 996 unknown formal candidates and two conditional substantive episodes are the registered evidence gaps. Source-precision caveats remain in the case notes, especially early communist-takeover and repeated-coup apparatus episodes.

**Step 4 is complete on the best-available evidence, with missingness preserved.** User review of substantive coding remains open; reliability double-coding and Cohen's κ remain Step 8. No Step 1–3 values were changed, no outcome data were used, and no Step 5 panel merge was performed.
