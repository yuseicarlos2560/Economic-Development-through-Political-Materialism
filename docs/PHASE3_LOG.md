# Phase 3 Methods Log

Running record, continuing `docs/PHASE2_LOG.md`. Steps follow `docs/ROADMAP.md`.
Newest entries last.

---

## 2026-11-02 — Step 2 complete: manual datasets acquired (user)

User downloaded the four manual items from DATA_SOURCES.md; moved from
~/Downloads to `data_raw/` and verified:
- ATOP 5.1 (12 CSVs: members, dyads, directed-dyad-years, state-years), 1815–2018.
- GSDB **Release 5** (newer than the planned R4): 1,794 sanction cases, 1949–2025,
  plus GSDB-FS (1,072 rows, 1950–2025), both with codebooks.
- CCP Chronology of Constitutional Events v6 (`ccpcce_v6.csv` + codebook).
- IMF DOTS full bulk CSV (1.6 GB, SDMX format; will be filtered to our 73
  countries × patrons when the Δ-trade-share variable is built).
DATA_SOURCES.md updated: nothing is left on the manual list except the optional
EBRD/CEPALSTAT case-work sources. Step 2 of ROADMAP.md is done.

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

## 2026-11-02 — Step 3 begins: calibration episode E001 (Yugoslavia–USSR 1948–49)

Protocol §6.1 (four judgments + non-contamination rule) added to the Coding
Protocol before coding started. E001 coded: severance, imposed, interval
1948–1949, families F1+F2+F3+F4. Evidence: ATOP treaty 3020 (denounced Sep 1949),
GSDB-R5 case 21 (complete trade embargo, formal record Mar 1950–Mar 1955),
Cominform resolution 28 Jun 1948. UN ideal-point validation passes (gap ~0 in
1948 → 2.2 by 1952). Yugoslavia is not in the 73-country panel (dissolved;
successor states not in sample) — the episode serves to fix coding conventions,
exactly as CP §6 prescribes for calibration episodes. Conventions fixed are
listed in `case_notes/YUG_1948.md` (bloc-membership termination counts as a full
family; interval anchored to documentary events, not to the sanctions database's
formal start; expulsion = imposed under R4).

## 2026-11-03 — Calibration episode E002 (Spain–US 1953, entry)

Entry from isolation (Spain was in no sphere 1945–53). F1 bases + F2 aid
established by the Pact of Madrid (26 Sep 1953); F3 corroborates (UN Dec 1955).
Chosen, richer sphere (R5 mechanical: US 16,917 vs Europe median 6,594), R6=0.
UN ideal-point convergence confirmed from 1956.
Important calibration finding: growth breaks +3.9pp from 1961 (timing rule
satisfied) but NO acceleration episode is coded — the 1961–68 window crosses
the Maddison→WDI seam and A4 (within-source levels) correctly excludes it;
fully-WDI windows fail A3 (prior regime already contains the boom). Recorded
honestly as a failed episode test with mean-growth support for H2 — Spain
becomes the entry-side calibration case (mirror of Vietnam for severance).
Code fix: A4 check hardened (all comparison cells must share one source);
re-run leaves the episode list unchanged (69/54). Conventions fixed listed in
case_notes/ESP_1953.md.

## 2026-11-03 — Calibration episodes E003/E004 (Cuba 1959–62, paired severance+entry)

E003 severance from US (imposed; interval 1960–62: embargo 1960, rupture 1961,
OAS expulsion 1962; GSDB-R5 cases 51/59/65/74). E004 entry into Soviet sphere
(1960 point; F2 trade pact Feb 1960 + F1 missions/arms; NO treaty — informal
sphere per Keal/Hast; chosen, balancing under coercion noted). R5 for entry:
USSR richer than LatAm median (6,288 vs 3,572). UN ideal points give the
cleanest validation yet (Cuba=US 1958; Soviet-level by 1961).
Two findings of substance: (1) the imposed US severance produced NO threshold
disruption because the Soviet entry replaced capability flows in the same
window — paired severance+entry must stay separable in the episode table;
(2) the entry's H2 sign (richer sphere → acceleration) is NOT confirmed in the
1960s (stagnation) — recorded as a non-confirming case, not hidden.
Convention fixed: paired episodes get separate rows (E003/E004).

## 2026-11-03 — Calibration episode E005 (Cuba–USSR 1989–91, severance)

Imposed severance by patron collapse (R4 first clause); interval 1989–91; all
three families terminate (subsidies ~23% GDP ended, CMEA dissolved Jun 1991,
brigade withdrawal Sep 1991). R6 systemic-shift flag = 1 (first case carrying
it). UN validation: patron-driven divergence (Russia moved toward the US; Cuba
did not move) — independently supports the *imposed* coding.
Timing-rule examination (important): screen-coded D019 peaks in 1985, BEFORE
the severance; year detail shows 1985–89 flat (rectification) and the collapse
proper 1990–93 (−33% in four years), which FOLLOWS the severance window. New
convention: report peak year and contraction phase separately; the timing rule
is evaluated against the contraction phase. H2 negative sign strongly confirmed
(showcase case). US embargo tightening 1992 (GSDB 443) recorded as context, not
as part of the severance coding.

## 2026-11-03 — Calibration episodes E006/E007 (Egypt 1972–79)

E006 severance from USSR, CHOSEN (client-initiated: Sadat expels the mission
Jul 1972, abrogates the 1971 treaty Mar 1976 — ATOP 3670, renounced). GSDB-R5
case 198 documents Soviet retaliation (1976–84, arms+financial) — coded as an
F4 record, not a voluntariness override (new convention). E007 entry into US
sphere, chosen, interval 1974–79 (relations+aid 1974 → Camp David 1978-79);
informal, no treaty. R5: richer sphere (US 26,286 vs EGY 2,099, 1974).
UN ideal points show both the divergence (from 1972–74) and the convergence
(toward US by 1979–82). Outcome: NO disruption after the severance; growth
accelerates 1975–80 — replicates Cuba 1960's paired logic (severance+entry
within ~2 years ≠ bare severance) and supports H2's entry sign at the
mean-growth level. Egypt not in panel — calibration only.

## 2026-11-03 — Calibration episodes E008/E009 (Vietnam 1989–95)

E008 severance from USSR, imposed (patron collapse), interval 1989–91, R6=1;
families F1+F2+F3 (CMEA member since 1978; Cam Ranh withdrawal; 1978 treaty
lapses 1994 = formal tail, not the severance date). UN validation: patron-driven
divergence again (same signature as Cuba 1989–91). Outcome absorbed below
threshold — the registered threshold-calibration case holds.
E009 US normalization 1994–95 coded as entry (chosen, richer sphere) BUT with
medium confidence and a published validation flag: UN ideal points show NO
convergence to the US through 2000. Vietnam integrated into the US-led economic
order without entering the US security sphere — new explicit subtype
(economic-order vs security-sphere entry). Timing honesty: acceleration A069
(1992–2001) PRECEDES the entry and cannot be attributed to it; it follows
Đổi Mới 1986 (domestic policy change, power structure intact).
New conventions: validation failures are published, not fatal; formal treaty
lapses trailing the effective rupture are noted as formal tails.

## 2026-11-03 — Calibration episodes E010–E015 (Baltics 1990–2004)

Severance from USSR (EST/LVA/LTU): interval 1990–94 (declarations + Soviet
blockade of Lithuania 1990 [GSDB 385] → independence/CMEA/USSR dissolution 1991
→ ruble exit 1992–93 → troops out 1993–94). Voluntariness: CHOSEN with a new
mixed flag (initiative predates the patron's collapse; usable in the
imposed-only robustness variant). Disruptions follow (EST −28.2%, LVA −41.4%,
LTU −43.2%) — H2 negative confirmed 3/3, timing satisfied.
Entry into US/EU sphere: interval 1995–2004 (Europe Agreements 1995 → NATO
26 Mar 2003 [ATOP 3180] + EU 1 May 2004), chosen, richer (R5 verified).
Accelerations begin 1998, INSIDE the entry interval — timing satisfied via the
interval convention (a 2004 point coding would have failed it; entry was a
process). UN ideal points: Western alignment from the first UN session (1991).
New conventions: chosen-with-collapse mixed flag; entry intervals may bracket
an acceleration (timing evaluated against the interval's start).
Note for later: Baltic 2007–10 disruptions are the GFC (year-FE matter), not
realignment-driven.

## 2026-11-03 — Calibration episode E016 (Venezuela–US 2002–17)

Gradual severance, interval [2002, 2017] with endpoint+midpoint robustness.
Families terminate across 15 years (military ties 2004–05, sanctions escalation
GSDB 802/827/1051/1098, Rio Treaty exit 2015 per ATOP, OAS withdrawal 2017).
Voluntariness: chosen (mixed: patron enforcement from 2015) — new convention.
DOTS used quantitatively for the first time: US share of VEN exports 52.1%
(2000) → 36.6% (2017) → 12.0% (2019), confirming the interval and the 2017
endpoint. UN ideal points: country-driven monotone divergence (contrast with
patron-driven Cuba/Vietnam) — consistent with chosen.
CRUX HONESTY: onset of D091 (2014) is the oil-price crash, pre-enforcement;
deepest years (2016–19) follow enforcement. And by Protocol §4 the power
structure was transformed by 2009, so Venezuela 2011–19 sits in Table 1's
bottom row — it must NOT be presented as clean H2 evidence. This is why the
power-structure variable is indispensable.

## 2026-11-03 — Calibration episode E017 (Greece 2015, negative control)

Threatened eurozone exit unconsummated (capital controls Jun, referendum Jul,
third MoU Aug 2015). Zero indicator families terminated -> coded
severance_threat/unconsummated, NOT a severance. UN ideal points flat (no
divergence even in 2015); GSDB empty for Greece 2015; NATO continuous.
Outcome +0.4% in 2015; the existing disruption D031 precedes the threat and
cannot be attributed to it (timing rule both ways). New convention: threat
episodes enter the table but are excluded from the Severance regressor
(robustness may include them). Sub-sphere nuance recorded (eurozone vs EU/US
sphere). CALIBRATION PHASE COMPLETE: 17 episodes, conventions fixed.
