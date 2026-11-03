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

## 2026-11-03 — Step 3 full sweep: design decisions registered (CP §6.2)

Before the sweep, four open design questions were put to the user and decided:
1. **Patron set** (CP previously undefined — only calibration episodes gave it
   content): US-led Western sphere as ONE sphere (UK/EU subordinate members,
   Lake 2009; Walt 1987; Buzan & Wæver 2003), USSR/Russia sphere (Waltz 1979;
   Mearsheimer 2001), and China from **2013** (BRI launch; Gilpin 1981;
   sensitivity at 2008 in affected case notes; PRK's 1961 treaty handled in
   its shadow-case note).
2. **EU entries:** all EEC/EU accessions meeting R1–R3 are coded as entry
   episodes (GRC 1981, ESP/PRT 1986, AUT/FIN/SWE 1995, post-socialist waves)
   — R3 is mechanical; excluding them would be selection on convenience.
3. **Working order:** screen first — the CP defined the *coding* methodology
   (§6.1 four judgments) but not candidate generation; a mechanical,
   outcome-blind screen (registered as CP §6.2) now generates the candidate
   list, then region batches are coded with user review per batch.
4. **ALBA / Venezuela-as-patron:** not sphere holders; recorded as context
   only. Cuba–Venezuela 2000s resolved by CONSISTENT EXCLUSION: patron–client
   subsidy relationship documented for the narrative layer (Step 8), not a
   coded sphere entry. Reconciling notes added to `docs/Cases.md` (Cuba
   framework reading and §7 signed-outcome pattern).

All four registered as **CP §6.2**. Next: Phase A construction — DOTS filter
(73 countries × patrons, incl. E002's pending Δ-trade cell), ATOP/GSDB
signals, bloc-date table, R5 regional medians, UN ideal-point distances,
then `code/screen_realignment.py`.

## 2026-11-03 — Step 3 Phase A COMPLETE: inputs built, screen run

Six mechanical inputs built and cross-checked, then the §6.2 screen.

**Outputs.**
- `data_clean/trade_shares.csv` (`code/build_trade_shares.py`): 24,516 rows,
  73 countries × {USA, USSR/RUS, CHN, DEU*, GBR*, FRA*} × 1948–2023; exports
  FOB + imports CIF over World total. E016 pattern reproduced (VEN-USA 45.7%
  2000 → 32.7% 2017 → 12.6% 2019; E016 used export share, this uses total
  trade — same break). E002's pending DOTS cell filled (ESP-USA ~11–15%,
  1952–55). CUB-USA 0.64–0.73 in 1948–57 confirms E003's "~2/3 pre-1959".
- `data_clean/alliance_signals.csv` (`code/build_alliance_signals.py`): 637
  patron-co-membership spells from ATOP 5.1 (COW↔ISO3 via the ideal-points
  file; predecessor fan-out CS→CZE/SVK≤1992, YU→HRV/SVN≤1991, GDR→DEU≤1990;
  post-Soviet republics do NOT inherit USSR memberships — incorporation, not
  alliance). COW cross-check 1945–2012: 99.6% of COW dyad-years (3,263/3,275)
  are inside ATOP; ATOP-only dyads = WWII coalitions and executive agreements
  COW excludes by design (e.g. US–Spain 1963, per E002); COW-only: GEO–USSR,
  TKM–CHN (flagged for region batches).
- `data_clean/sanctions_signals.csv` (`code/build_sanctions_signals.py`): 405
  patron-sender cases vs 62 panel targets (senders USA/USSR-RUS/CHN/EU*/
  US-led regimes; multi-target strings split; "Soviet Union"→RUS continuity).
  Calibration IDs reproduced (VEN 802/827/1051/1098; CUB 51/59/65/74/443;
  LTU 385). GRC has no 2014–16 case — E017 holds. Bloc-target cases
  ("Comecon" 1950–94, incl. CoCom) noted for region batches, not fanned out.
- `data_clean/bloc_membership.csv` (hand-built, treaty-record dates): 113
  rows, 8 blocs (NATO, EU/EEA, WarsawPact, CMEA, OAS, EAEU, CSTO, ALBA[n/a]),
  63 countries; validated (panel-only ISO3, entry<exit).
- `data_clean/r5_reference.csv` (`code/build_r5_reference.py`): regional
  GDP-pc medians (our regions, our panel) + patron series (USA, USSR→RUS
  splice at 1991, CHN), Maddison 1945–2022. Reproduces the calibration
  anchors exactly (E002: 16,917 vs 6,594; E013: 48,493 vs 7,782; E004: USSR
  6,288 in 1960).
- `data_clean/idealpoint_distances.csv`
  (`code/build_idealpoint_distances.py`): 12,572 dyad-years vs the three
  patrons (idealpointfp; COW 2/365/710). Calibration signatures reproduced
  (CUB–USSR 0.12→2.7, 1985–92; EST–USA ~1.5–1.8 from 1991).
- `data_clean/realignment_candidates.csv` + `sphere_roster_screen.csv`
  (`code/screen_realignment.py`): **118 candidates (109 new, 9 calibration
  overlaps)** from 1,016 screened events; roster = 6,747 country-year-sphere
  rows (F1/F3 active basis). New candidates by patron: USA 68, USSR/RUS 40,
  CHN 1 (TKM 2013–14).

**Screen conventions fixed today (ratification requested at Phase B start):**
1. Security blocs (NATO, Warsaw Pact, CSTO) feed **F1, not F3** — one act of
   accession is the security guarantee itself; counting it as two families
   would violate R2/R3's distinct-ties logic. F3 = economic-institutional
   blocs (CMEA, EU/EEA, OAS, EAEU).
2. Omnibus multilateral consultative acts (>30 members, no defense/offense
   obligation — e.g. CSCE 1975) excluded from F1 events.
3. Economic-bloc entries/exits (EU/EEA, CMEA, EAEU) are **auto-candidates**
   (35 of 118): the F2 aid/trade tie is constitutive of membership
   (structural funds/CAP, CMEA transfers), DOTS never shows it, so the
   ≥2-families screen would otherwise miss exactly the cases the user
   ordered coded (EU accessions). Flagged `auto` in the file; the four
   judgments still apply in Phase B. DOTS evidence confirms the point: DEU*
   share shows no break at accession (GRC ~17% flat 1976–85; ESP 8→15%
   gradually 1981–90).
4. F2 break rule: |share_t − share_{t−3}| ≥ 12pp with larger side ≥ 8%;
   Western sphere screened vs USA **and** DEU* (EU-core proxy).
5. CHN events pre-2013 dropped per §6.2 (119 events; 2008–12 sensitivity
   noted where relevant).

**Known blind spots (to be caught in Phase B roster review, not the screen):**
- Informal Soviet-sphere entries (Nicaragua 1979): no treaty/bloc, CMEA
  blindness — roster + case record carry them.
- KOR 1953 entry (Cases.md §7 expects it): single-family F1 at screen level;
  US aid 1953+ is the F2-family tie to document in the East Asia batch.
- LatAm 1947–48 Rio/OAS blocks = hemisphere entry into the US sphere at the
  window edge; Phase B decides initial-condition vs episode treatment.

**Phase A is outcome-blind throughout:** no outcome series was read by any
script above. Next: Phase B region batch 1 — post-Soviet (14 countries).

## 2026-11-03 — Phase A validation: screen vs analytical calibration coding

Systematic contrast of `realignment_candidates.csv` against the 15 panel
calibration episodes (E001/E006/E007 are non-panel by design).

**Reproduced — 9/15:** E003 (screen 1960–63, F1+F3+F4); E005 and E008 (1991,
CMEA exit auto-candidates); E012 (1990–92, F1+F4 — LTU surfaced by the Soviet
blockade GSDB 385); E013–E015 (2003–04, F1+F3); E016 (2015–17 and 2017–21 —
the screen sees the enforcement/consummation phase of the interval, exactly
what interval coding predicts). Direction matches in all nine.

**Missed — 5/15, each with a specific documented cause:**
- E002 (ESP 1953): the Pact of Madrid was an *executive agreement*; ATOP's
  first US–Spain treaty is 1963. Screen F1 is blind to sub-treaty ties;
  F2 aid flows (~1% GDP/yr) are not in DOTS shares.
- E004 (CUB 1960 USSR): informal sphere — no treaty ever existed, CMEA only
  1972, and DOTS is blind to CMEA trade. The Keal/Hast informal-sphere class
  is document-coded by design.
- E009 (VNM 1994–95 USA): economic-order entry — F1 absent *by the episode's
  own coding*; ASEAN is not a sphere bloc; GSDB 201 *ending* is not an event.
  Consistent with the episode's medium-confidence flag.
- E010/E011 (EST/LVA 1990–94): exit from *incorporation*, not from an
  alliance/bloc — no ATOP spell exits, no bloc exits, and the trade collapse
  predates DOTS coverage (EST 1993 opens at 19.7%, already post-collapse, no
  ≥12pp/3yr break). Russian sanctions 1992–93 (GSDB 446–52) give only F4 —
  single family, below the screen rule.

**Correct negative:** E017 (GRC 2015 threat) — no candidate, as coded.

**Interpretation (registered for Phase B):** screen and analytical coding
agree wherever the underlying *databases* carry the ties; misses concentrate
in exactly the classes CP §6 reserves for documentary coding (informal
spheres, incorporation exits, sub-treaty agreements, economic-order entries).
Consequences: (1) the screen is a recall *floor*, not an exhaustive list —
Phase B codes the post-Soviet 1990–91 severances from the documentary record
(independence declarations, CMEA/WP dissolution, troop withdrawals,
ruble-zone exit; R4 imposed-by-collapse is mechanical), with the screen as
corroboration, exactly as E010–E012 were coded in calibration; (2) long
intervals surface in the screen at their consummation phase — interval
coding remains Phase B's job; (3) aid flows (F2-family) are documented per
episode in Phase B, as the screen processes trade shares only.

## 2026-11-03 — Phase B batch 1 (post-Soviet, 15 countries) coded

**Preparatory fix:** bloc table was missing the 1992 Tashkent CST (the
CSTO's predecessor — the AZE/GEO/UZB 1999 non-renewals are
severance-relevant) and the CIS (the institutional-continuity framework that
decides the BLR/KAZ/ARM negative cells). 26 rows added with treaty-record
dates; CST classified security-bloc (F1), CIS institutional (F3); screen
re-run (128 candidates, roster continuity now correct for ARM/KAZ/etc. from
1992).

**New episodes (4):**
- **E018 UKR 2014–16, severance, high.** Kharkiv Pact denounced 2014, CIS
  participation ceased 2014, RUS trade share 27.3%→11.6% (2013–16), GSDB
  1031; chosen (mixed: patron enforcement); 1997 treaty non-renewal 2018–19
  coded as formal tail (E008 convention). Outcome −13.9% peak-to-trough,
  BELOW D1 — sub-threshold recorded honestly.
- **E019 GEO 2006–09, severance, high.** 2006 embargo (GSDB 780/781),
  bases returned 2007, Aug 2008 war, CIS exit 18 Aug 2009. UN divergence
  EARLY (2003–05, country-driven per E016). Outcome 2009 ~−3.7% (GFC
  confound) — sub-threshold recorded honestly.
- **E020 AZE 1991–99, severance, MEDIUM — user decision requested.**
  No bases from 1991, CST 1993→non-renewal 1999, oil reorientation
  (Contract of the Century 1994, BTC 1998); CIS never left (F3 intact);
  **UN validation FAILS** (distance falls 0.81→0.15, Aliyev balancing —
  published per E009 convention). Alternative defensible coding:
  sub-threshold gradual exit (as UZB). Borderline, flagged.
- **E021 TKM 1991–95, severance by neutrality, high (medium on interval
  end).** Own armed forces 1992, never CST, ruble exit 1993, UN-recognized
  neutrality 12 Dec 1995; UN divergence 1992–96 then re-convergence (gas
  normalization). TKM–CHN gas dependence (63.6% by 2019) + consultative
  ATOP 6085 = single-family, NOT consummated entry per R3 — E009 subtype,
  flagged for the reliability subset.

**No-episode determinations (documented in
`case_notes/PostSoviet_batch_note.md`):** BLR, ARM, KAZ, KGZ, TJK = Russian
sphere continuity throughout (UN distances 0.02–0.7, trade shares stable;
screen candidates rejected as continuation signals — entry into successor
institutions is not a realignment). MDA contested but sub-threshold
(Transnistria troops remain; EU AA unconsummated). UZB oscillation within
the sphere (single-family moves only). RUS = the patron (RUS–USA 1991–92
candidate rejected).

**Outcome record (read AFTER dates were fixed):** all no-episode republics
show 1986–99 threshold disruptions (BLR −34.7%, KAZ −37.0%, ARM −51.8%,
MDA −59.6%, UZB −27.6%) — transition collapses without severance inside the
R6 window, recorded neutrally for Step 6 (capability-flows channel, E005
convention; no conclusion drawn here).

**Batch status:** 21 episodes total. Conventions exercised: formal-tail
(E008), country-driven divergence (E016), chosen-mixed voluntariness
(E016/Baltics), unconsummated entries (E017), validation-flag publication
(E009). **User review pending** — particularly E020 (borderline) and the
MDA/UZB sub-threshold determinations. Next batch: Europe.

## 2026-11-03 — Phase B batch 2 (Europe, 29 countries) coded

**New episodes (38): E022–E059**, documented in seven case notes
(`case_notes/EURO_formation_Western.md`, `EURO_formation_Soviet.md`,
`PostSocialist_severance_1989.md`, `ALB_1960.md`, `FIN_1991.md`,
`PostSocialist_entry_Western.md`, `EURO_batch_note.md`).

1. **Western formation block (E022–E033, entries 1947–55, chosen, R6=0,
   medium confidence)** — Truman Doctrine Mar 1947 / ERP+OEEC Apr 1948 /
   Washington Treaty Apr 1949 (ATOP 3180); GRC [1947,1952] (informal F1+F2
   by 1947–48, NATO 1952 formal tail, E002 convention); DEU [1949,1955]
   (occupation guarantee + ERP, NATO 1955; EEC 1957 tail). Block note:
   judgments stated once, deviations per row. R5 richer verified (1947:
   14,312 vs 5,925). Window-edge finding: prior regime pre-1945 undefined →
   episode-level outcome test structurally indeterminate; registered
   pre-Step-6 (not ex-post selection). ISL/LUX/PRT/IRL A-episodes checked,
   unrelated.
2. **Soviet formation block (E034–E040, entries 1945–49, R6=0)** —
   bilateral treaties (ATOP 3025/3120/3115/3135/2563), Cominform 1947, CMEA
   Jan 1949 (ALB Feb 1949; WP 1955 = formal tail). **R4 imposed-entry class,
   first use** (occupation + takeovers); E040 ALB the chosen exception
   (indigenous partisan victory, no Soviet troops). **R5=0 poorer sphere
   (1949: 4,181 vs 5,426) — coded, outside the H2 sign test.** ROU D070
   (−36.7%, 1948–53) FOLLOWS the imposed entry — adverse-flows pattern
   recorded neutrally. GDR recorded as context (not in panel; screen
   fan-out artifact documented).
3. **Post-socialist severances (E041–E046, 1989–92, R6=1)** — WP dissolved
   1 Jul 1991 (military structures 25 Feb 1991), CMEA dissolved 28 Jun
   1991, world-price shift 1 Jan 1991, troops out 1991–93 (tails noted).
   UN validation passes 4/4 with data (POL 0.18→1.34, HUN 0.17→1.15, ROU
   0.01→1.14, BGR 0.17→1.03, 1990→91; convergence to USA 1980s→91);
   CZE/SVK validation-limited (ideal points from 1993; SVK Mečiar-era
   Russia-proximity corroborates E052's delayed interval). Voluntariness:
   chosen-mixed for POL/HUN/CZE/SVK/ROU; **BGR IMPOSED** (loyalist
   republic — BSP won the Jun 1990 election; exit driven by the patron's
   dissolution). Outcomes follow (POL D3 hyperinflation 568% 1990 ✓; HUN/
   SVK/ROU/BGR transition recessions ✓ per E005 convention); **CZE honest
   exception: no threshold disruption (~−12% < D1) — sub-threshold
   recorded, not adjusted** (non-confirming severance-side case for Step 6).
4. **E047 ALB 1960–68 severance, chosen (mixed: patron enforcement)** —
   GSDB-R5 56/64 (specialists/credits withdrawn 1960–61), Vlora base Jun
   1961, CMEA participation ends end-1961, WP denounced 13 Sep 1968
   (formal tail, E001 convention). UN passes (~0.01→0.15→0.39,
   country-driven). No disruption 1960–68 (Chinese replacement, E003/E006
   class); D001 (1986–94) NOT attributable. Sub-threshold recorded. China
   pre-2013 = context (§6.2).
5. **E048 FIN 1991–92 severance (imposed, patron collapse, R6=1) + E058
   FIN 1991–95 entry (chosen, R6=1), paired note** — membership coded as
   constraint set (YYA, ATOP 3140); replaced 20 Jan 1992 (military articles
   dropped); Soviet trade collapse 1991. UN patron-driven convergence
   (E005 convention). D030 timing mixed, recorded honestly (banking channel
   flagged for Step 7). E058: EEA 1994 → EU Jan 1995; F1 absent by design —
   E009 subtype; A019 inside ✓.
6. **Post-socialist entries (E049–E057, E059; chosen, richer)** — EA/SAA
   anchor → NATO → EU. **Consummation rule registered** (association F2/F3
   + security guarantee F1 = consummated: ALB/HRV 2009; association alone
   = unconsummated: UKR/GEO/MDA). SVK interval starts 1993 (Mečiar delay,
   UN-corroborated); SVN 1996 (succession-delayed EA). R6=1 for E049–E051
   and E057 (process opens inside the shift window), else 0. Accelerations
   inside intervals for 8/10 episodes with A-episodes; **HRV A026
   (1998–2007) precedes [2001,2013] — NOT attributable (E009 honesty)**;
   MLT A042/A043 not attributable. **E059 MLT medium confidence, flagged**:
   re-entry coding (Mintoff-era distancing 1971–87, discrete 1987–90
   return), E009 subtype, CYP asymmetry documented.

**New conventions (registered, user ratification pending):**
(1) deepening ≠ entry — EU/NATO accession by a country already inside the
Western sphere is intra-sphere deepening, no episode (ESP 1986, GRC 1981,
PRT 1986, DNK/IRL/GBR 1973, AUT/SWE 1995, CYP 2004, NOR-EEA 1994, CHE
never; FRA 1966 = single-family partial, no episode);
(2) succession ≠ sphere severance — Yugoslavia not a sphere holder
post-1948 → SVN/HRV 1991 = succession context (war collapses D041,
D077/D078 recorded as context);
(3) window-edge formation blocks = interval entries with structurally
indeterminate episode-level outcome test, registered pre-Step-6;
(4) R4 imposed class extended to imposed entries (Soviet block);
(5) R5=0 poorer-sphere entries coded but outside the H2 sign test;
(6) entry consummation rule (association + security guarantee).

**Rejected screen candidates** (batch note): NOR–RUS 2013–14 (pressure on
a NATO member), POL–USA 1961–62 (wrong-direction dyad), ROU–USA 1988–90
(MFN suspension), DEU–USSR 1990 (GDR fan-out artifact), DEU–USA 1975–77
(Ostpolitik diversification), FRA/BEL/etc. 1949–51 (WWII/CSCE noise; the
formation block covers the real event).

**Batch status:** 59 episodes total (E001–E059). **User review pending** —
E059 MLT (medium confidence), E020 AZE (carried from batch 1), MDA/UZB
determinations, formation-block conventions (3)–(6). Next batch: Latin
America (24 countries).

## 2026-11-03 — Phase B batch 3 (Latin America, 24 countries) coded

**New episodes (9): E060–E068**, documented in five case notes
(`case_notes/LATAM_formation_initial_condition.md`, `NIC_1979.md`,
`Caribbean_entries.md`, `CHL_1970.md`, `LATAM_batch_note.md`).

1. **1947–48 Rio/OAS block (20 screen candidates) → initial condition, no
   episodes.** ATOP shows F1 *continuity* (Act of Chapultepec 1945 [3010] →
   Rio Treaty 1947 [3075] + OAS Charter 1948 [3150]); trade dominance vs
   USA already in place at the window edge (CUB 0.64–0.73, Phase A). The
   acts institutionalize a pre-existing informal sphere (Keal/Hast class) —
   deepening, not entry. Roster: all 20 = US-sphere members from 1945.
   Consistent with Europe (there the acts constituted NEW memberships) and
   with CUB E003's presupposed membership. **Convention 7 registered.**
2. **E060–E063 NIC 1979–93, the showcase cycle of the batch.** E060 entry
   USSR [1979,1981] — the Phase-A-registered ROSTER CATCH (informal class:
   no treaty/bloc ever; missions/arms + credits/oil; chosen; R5 richer:
   10,316 vs 6,385). E061 severance USA [1981,1985] — imposed
   (patron-initiated rupture, E003 class): aid suspended Apr 1981, Contra
   Dec 1981, total embargo May 1985 (GSDB 296/306), harbor mining 1984 =
   guarantee inverted; Rio Treaty formal tail to 2014. E062 severance USSR
   [1990,1991] — imposed (patron collapse, R6=1). E063 re-entry USA
   [1990,1993] — chosen (embargo lifted Mar 1990, aid resumes, share
   0.02→0.31 by 1993; R6=1). UN validation passes on all four (NIC–USSR
   3.16→0.04 by 1987; NIC–USA 1.22→3.80 by 1986; full reversal 1990–93).
   Outcome honesty: D059 peak (1974) predates E060; E060's entry sign NOT
   confirmed (no acceleration — war/severance confound, recorded); the
   1983–89 collapse coincides with E061 but is WAR-CONFOUNDED (Step 7
   flag); contraction ends 1992 with the reversal (indeterminate).
3. **Caribbean accessions E064–E067** (entries from colonial status,
   chosen, R5 richer, R6=0): TTO [1962,1967] (Rio+OAS), JAM [1962,1969]
   (OAS charter only — NOT Rio, recorded exactly), SUR [1975,1977] (same),
   GUY [1985,1991] — **medium confidence, flagged**: 1966–85 non-alignment
   (UN-corroborated drift to the Soviet position without consummation) vs
   persistent Western economic ties (IMF 1978); borderline with the
   deepening convention. GUY A022 (1989–2000) overlaps the interval end ✓
   (E013 convention). JAM's Manley drift 1972–80 = within-sphere politics,
   no severance (zero families terminated).
4. **E068 CHL 1970–73 severance_threat (unconsummated)** — the region's
   negative control, E017 convention. Zero families terminated (no bloc
   exit, no Soviet treaty; the trade collapse was US-enforced — GSDB 147).
   UN shows the drift AND its reversal post-coup (USA 1.08, USSR 3.35,
   1974). Excluded from the Severance regressor. Coup = hierarchy
   enforcement, context. D015 (1970–76) attributed to polarization +
   destabilization + coup, not severance. **Convention 8 (threat
   threshold) registered.**
5. **Rejections** (batch note): DOM 1960–64, HTI 1986–87/2000–02, CRI
   1999–2003 (pressure within the sphere; **convention 9 made explicit —
   F4 is not an R2 family**); TIAR withdrawal wave BOL/NIC 2014, ECU 2016,
   MEX 2004 (single-family in the R2 set; NIC drift flagged for the
   reliability subset); drifts without consummation (GTM 1951–54, PER
   1968–75, SUR 1982–83); hierarchy-enforcement events (BRA 1964, ARG
   1976, PAN 1989, ARG 1982); ALBA = context per §6.2. CUB 1972 CMEA =
   deepening of E004. Calibration overlaps (CUB 1991, VEN 2015–21) already
   coded.

**Batch status:** 68 episodes total (E001–E068). Conventions 7–9 added to
`docs/OPEN_ISSUES.md` with E067 GUY for user ratification; earlier items
(E020 AZE, E059 MLT, MDA/UZB, batch-2 conventions) remain open. Next
batch: East Asia (4 countries — JPN/KOR entries, MNG severance, PRK shadow
case + VNM candidates per Phase A blind-spot notes), then Phase C audit.
