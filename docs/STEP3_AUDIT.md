# Step 3 — Phase C audit report

**Date:** 3 Nov 2026 | **Script:** `code/audit_episodes.py` (exit 0; 16 PASS, 0 FAIL, 3 warning classes)
**Objects audited:** `data_clean/episodes.csv` (73 rows), `data_clean/episode_sources.csv` (73 rows),
`data_clean/realignment_candidates.csv` (128 rows), `case_notes/*.md` (33 files), `data_clean/countries.csv` (73 panel countries).

## 1. Coverage statement

Every panel country has either coded episodes or a documented no-realignment determination.
No country is unexamined.

| Class | n | Countries | Documentation |
|-------|---|-----------|----------------|
| Episodes coded | 44 | ALB, AZE, BEL, BGR, CHL, CUB, CZE, DEU, DNK, ESP, EST, FIN, FRA, GBR, GEO, GRC, GUY, HRV, HUN, ISL, ITA, JAM, JPN, KOR, LTU, LUX, LVA, MLT, MNG, NIC, NLD, NOR, POL, PRK, PRT, ROU, SUR, SVK, SVN, TKM, TTO, UKR, VEN, VNM | 73 episode rows E001–E073 + per-batch case notes |
| No-realignment determination | 29 | ARG, ARM, AUT, BLR, BOL, BRA, CHE, COL, CRI, CYP, DOM, ECU, GTM, HND, HTI, IRL, KAZ, KGZ, MDA, MEX, PAN, PER, PRY, RUS, SLV, SWE, TJK, URY, UZB | `PostSoviet_batch_note.md` (ARM, BLR, KAZ, KGZ, TJK continuity; MDA, UZB sub-threshold — OPEN_ISSUES; RUS = patron), `EURO_batch_note.md` (AUT, CHE, CYP, IRL, SWE — deepening convention), `LATAM_formation_initial_condition.md` + `LATAM_batch_note.md` (16 countries) |
| Calibration-only (not in panel) | 2 | EGY, YUG | `EGY_1972.md`, `YUG_1948.md` |

**Screen candidates:** 128/128 resolved — 53 episode-matched, 75 documented rejections in batch
notes (Europe 45, Latin America 39, Post-Soviet 34, East Asia 10). Zero orphans. One documentation
gap was found and fixed during the audit (GEO 1993, see §4).

## 2. Consistency results (episodes.csv)

- **Integrity:** IDs contiguous E001–E073; types ∈ {entry 46, severance 25, severance_threat 2};
  all years integer, 1945 ≤ start ≤ end ≤ 2019; `interval_coded` matches the year columns everywhere.
- **Vocabularies:** patron ∈ {USA 26, USSR 28, USA/EU 14, USSR/RUS 4, EU/eurozone sub-sphere 1} —
  all inside the CP §6.2 patron set (China episodes: none, consistent with the pre-activation
  convention). Voluntariness bases ∈ {chosen 55, imposed 16, n/a 2}; n/a occurs exactly on the two
  threat episodes. Confidence ∈ {high 46, medium 25, medium-high 2} (qualifiers preserved).
- **R2 family rule:** all 71 consummated episodes carry ≥2 of F1–F4; the 2 threat episodes carry the
  required zero-termination record.
- **Chain logic:** per country × patron-side, every entry follows a severance (or opens the chain),
  every severance follows a membership (entry or documented initial condition); no same-side interval
  overlaps.
- **R6 flag:** 23 episodes flagged, all with start_year ∈ {1989, 1990, 1991} — the systemic-shift
  window class, as designed.

## 3. Warnings (expected classes, manually confirmed during audit)

1. **First-event severances (16):** each requires a documented initial condition — confirmed for all:
   CUB/NIC/VEN/CHL via the LATAM initial-condition roster; Baltics via the 1940 incorporation record;
   FIN (YYA 1948), MNG (ATOP 2370/3535), PRK (1961 treaties), EGY (1971 treaty + 1955 alignment),
   UKR/GEO/AZE/TKM (CIS/CST record), YUG (1945 treaty). GEO's prior condition is now also explicit
   in the batch-note addendum (§4).
2. **Cross-patron transition overlaps (8 pairs):** the designed overlapping exit/entry intervals
   (CUB 1960, EGY 1974–76, POL/HUN/CZE 1991, FIN 1991–92, NIC 1979–81 and 1990–91). Not errors.
3. **R6 distribution:** see §2 — expected window class.

## 4. Findings and audit-time fixes

- **GEO–USSR/RUS 1993 screen candidate** was not documented anywhere. Determination added to
  `case_notes/PostSoviet_batch_note.md`: rejected as re-engagement with the sphere Georgia never left
  (BLR/ARM/KAZ class); it is the documented prior condition of E019, not an episode. No coding change.
- **Check calibration:** the ≥2-family rule was refined to exempt threat episodes (they must instead
  record zero termination — the convention-8 semantics); case-note presence matches iso3 or country
  name (prose notes use names). Neither affects any coded value.

## 5. Deferred items (unchanged, pending user ruling)

All items in `docs/OPEN_ISSUES.md` remain open: conventions 1–10; E020 AZE, E059 MLT, E067 GUY
confidence flags; MDA/UZB sub-threshold determinations; turnover checklist; screen conventions.
Per ROADMAP these are to be resolved **before Step 6** (items 3–5 affect how evidence is counted).
The audit did not touch any coded value.

## 6. Verdict

Step 3 coding is **complete, internally consistent, fully sourced, and fully covered**: 73 episodes,
128/128 screen candidates resolved, 73/73 panel countries accounted for, all four judgment areas
anchored per episode (`episode_sources.csv`: A 64 / B 7 / C 2). Step 3 can be marked done subject to
the deferred rulings in §5.
