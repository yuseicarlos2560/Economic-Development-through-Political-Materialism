# Phase 3 Methods Log

Running record, continuing `docs/PHASE2_LOG.md`. Steps follow `docs/ROADMAP.md`.
Newest entries last.

---

## 2026-11-02 — Step 1: Turnover variable (`code/build_turnover.py`)

**Task.** Code `Turnover` = 1 in the year the effective leader is replaced, plus an
`irregular_exit` flag for the manner of the outgoing leader's exit, for all
73 countries × 1945–2019. This is β₃ in equation (1) — the H1 control
(draft2.tex:196; Coding_Protocol §2). It must be mechanical: if the control
variable were judgment-coded, the H1 null could not be tested cleanly.

**Source and why it is reliable.** Archigos 4.1 (Goemans, Gleditsch & Chiozza
2009): 3,409 leader spells, 1875–2015, coding the *effective* leader (not the
titular one) with documented entry/exit dates and manner of exit. It fits the
protocol's first principle — observable events (inaugurations, coups, deaths),
not expert ratings. Post-2015 is outside Archigos, so 2016–2019 is hand-coded
in `data_clean/turnover_post2015_checklist.csv` with `verified=False` until each
entry is checked against constitutional records.

**Coding rules.**
- Turnover is a *replacement*: a country's first spell in the record (founding
  leaders, post-1990 first presidents) is an initial condition, not an event.
- `irregular_exit` describes the event's manner = how the *outgoing* leader
  left (Archigos exit in {Irregular, Foreign}); natural death and ill health
  are regular.
- Multiple leaders starting in the same year collapse to one indicator.

**Problems found and fixed (documented honestly):**
1. *Gleditsch–Ward codes ≠ ISO3.* A naive join silently matched 41 of 73 codes —
  but three of those matches were traps: Archigos `KOR` is the historical Korean
  kingdom (last spell 1910), and `VNM`/`MNG` have no post-1900 spells at all.
  Correct mappings: KOR→ROK, VNM→DRV, MNG→MON.
2. *Collision:* Archigos `SLV` is Slovenia, but `SLV` in our sample is El
  Salvador (Archigos: SAL). Fixed: SLV→SAL, SVN→SLV, SVK→SLO.
3. *Other mappings:* DEU→GFR (GDR not in our sample); CZE→CZE+CZR (Archigos
  CZE = Czechoslovakia 1918–92, CZR = Czechia 1993–2015); 26 further GW codes
  mapped one-to-one (full table in the script's CODE_MAP).
4. *Manner bug:* first version attached each incoming leader's own eventual
  exit manner instead of the outgoing leader's. Caught in spot checks (Castro
  1959 showed regular; Pinochet 1973 showed regular). Fixed; spot checks now
  historically correct (Castro 1959 = 1, Allende 1970 = 0, Pinochet 1973 = 1,
  Gorbachev 1985 = 0, Yeltsin 1991 = 1, Moon 2017 = 1).
5. *Switzerland:* Archigos records the annually rotating (ceremonial) Swiss
  president — turnover would be 1 every year, meaningless for a collective
  executive. Decision: CHE coded 0 and flagged for qualitative treatment in
  case notes.
6. *Effective-leader ambiguity (deferred, not guessed):* GEO, LTU, MDA, MNG
  post-2015 entries are left at 0 with a note — the "effective leader" is
  ambiguous (president vs PM) and needs constitutional checking, same for
  Vietnam's collective rotation.

**Result.** `data_clean/turnover.csv`: 904 turnover events across 72 countries
(CHE intentionally zero), 132 with irregular manner; 860 from Archigos, 44
hand-coded post-2015 (unverified). No unmapped countries.

**Pending for this step:**
- User verification of the 44 post-2015 entries and the four deferred countries.
- Merge into the panel happens at step 5 (panel assembly).

## 2026-11-02 — Coalition-change variable (`code/build_coalition.py`)

**Decision.** User rule: adopt DPI only if it does not shrink the sample. Checked
before deciding: DPI2020 covers 182 countries 1975–2020; 73/73 of ours are in it
(Romania coded ROM). Coalition change is a companion variable for the descriptive
layer (CP §2), not a regressor in equation (1), so no sample is lost. **Adopted.**

**Source.** DPI2020 (Cruz, Keefer & Scartascini 2021), downloaded via the IDB
CKAN API after publications.iadb.org returned 403 to scripted access (same class
of problem as ATOP; logged). Added to DATA_SOURCES.md and bib.bib.

**Construction.** `coalition_change` = 1 when the chief executive's party
(`execme`, "Name of Executive Party") differs from the previous year. First
observed year = initial condition (same convention as turnover). -999 treated
as missing, never imputed.

**Result.** `data_clean/coalition.csv`: 372 coalition changes across 67 countries
(1975–2019). Zero-change countries: BLR, CUB, PRK, TKM, VNM (one-party/personalist
systems — exactly what the theory expects) and CHE (no DPI data, same
collective-executive problem as Archigos). Spot checks historically correct:
VEN 1979 (AD→COPEI), 1984, 1994, 1999 (Chávez/MVR), 2007 (MVR→PSUV).

**Honest limitations (documented):**
- 1960–1974 is empty for ALL countries (DPI starts 1975). Filling via Nohlen
  handbooks is feasible but deferred; flagged as a limitation.
- DPI party-name strings can change for spelling/merger reasons (e.g., some GRC
  years), which can overstate changes; to be checked when the variable is used.
- CHE has no coalition variable (documented, consistent with turnover).
