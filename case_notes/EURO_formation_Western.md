# Case note — Western sphere formation block 1947–1955 (entries E022–E033)

**Episode IDs:** E022–E033 (12 entries) | **Status:** Phase B batch 2 (Europe)
| **Coder:** assistant + user, review pending | **Confidence:** medium
(window-edge block: the episode-level outcome test is structurally
indeterminate — see below)

| ID | Country | Interval | Formal consummation |
|----|---------|----------|---------------------|
| E022 | BEL | [1947, 1949] | NATO 4 Apr 1949 |
| E023 | DNK | [1947, 1949] | NATO 4 Apr 1949 |
| E024 | FRA | [1947, 1949] | NATO 4 Apr 1949 |
| E025 | GBR | [1947, 1949] | NATO 4 Apr 1949 |
| E026 | ISL | [1947, 1949] | NATO 4 Apr 1949 (+ US bilateral 1951) |
| E027 | ITA | [1947, 1949] | NATO 4 Apr 1949 |
| E028 | LUX | [1947, 1949] | NATO 4 Apr 1949 |
| E029 | NLD | [1947, 1949] | NATO 4 Apr 1949 |
| E030 | NOR | [1947, 1949] | NATO 4 Apr 1949 |
| E031 | PRT | [1947, 1949] | NATO 4 Apr 1949 |
| E032 | GRC | [1947, 1952] | Truman Doctrine 1947 → NATO 18 Feb 1952 |
| E033 | DEU (FRG) | [1949, 1955] | FRG founding/ERP → NATO 5 May 1955 |

## Why a block note

The 1947–49 acts constitute the sphere itself (Truman Doctrine articulation
Mar 1947, ERP/OEEC Apr 1948, Washington Treaty Apr 1949). The four judgments
are identical across members; coding them separately would repeat one judgment
twelve times. Country-specific deviations are recorded per row in
`data_clean/episodes.csv`.

## The four judgments (CP §6.1), applied to the block

**1. Membership (R1).** Pre-1947: none of these countries belonged to a
peacetime sphere. The WWII Grand Alliance was a war coalition, not a sphere
(no standing peacetime security guarantee, no subsidized trade/aid regime, no
bloc institution); it dissolved in 1945–46 (Lend-Lease terminated Aug 1945).
Occupied states (BEL, DNK, FRA, LUX, NLD, NOR, ITA) and neutrals (PRT; ISL
under wartime US/UK occupation) emerge into non-membership. R1 for entry: not
a member of any sphere at interval start — satisfied.

**2. Change (R3 — entry).** ≥2 of {security guarantee, subsidized trade/aid,
bloc membership} established within 3 years:
- F2: Marshall Plan/ERP from Apr 1948 (all twelve recipients; ~2–3% of
  recipient GDP/yr 1948–52 — historical estimates, pre-WDI window); OEEC
  founded Apr 1948 administers it.
- F1: Washington Treaty 4 Apr 1949 (ATOP 3180) for the ten founding members
  in the panel; GRC accedes 18 Feb 1952; DEU 5 May 1955.
- GRC: the two-family threshold is met by 1947–48 (Truman Doctrine = informal
  security guarantee + aid, E002 executive-agreement convention); NATO 1952
  is the formal treaty tail. DEU: met by 1949–50 (occupation statute = de
  facto US security guarantee + ERP participation); NATO 1955 formalizes;
  EEC 1957 recorded as formal tail.
Intervals: [1947, 1949] block-wide; GRC [1947, 1952]; DEU [1949, 1955].

**3. Voluntariness (R4).** **Chosen** for all twelve — governments negotiated
and ratified entry, several against domestic opposition (FRA/ITA communist
parties; NOR neutrality tradition; ISL contested, riots 1949). Flags, not
overrides: GRC — entry bound to US intervention in the civil war (dependence
noted); DEU — chosen by the Adenauer government under occupation constraint
(full sovereignty only 1955); PRT — authoritarian regime choice (Salazar).

**4. Sign (R5).** Mechanical: US GDP pc 1947 = 14,312 vs Europe median 5,925
(Maddison, `data_clean/r5_reference.csv`) — richer sphere, sign + for all.
**R6 = 0** (sphere formation at the start of the bipolar order; the 1989–91
flag class is the shift, not this).

## Validation

- UN ideal points begin 1946 and are not informative on the window edge (no
  pre-formation baseline); post-1946 Western voting alignment is consistent
  but cannot discriminate. Recorded as validation-limited, not failed.
- Outcome record (read after dates were fixed): NO acceleration episodes are
  attributable to formation — the prior regime is pre-1945 and undefined at
  the window edge, so A3's prior-regime comparison cannot be constructed
  (E002's window-edge class). Recorded as supportive-but-indeterminate for
  H2 at the episode level; post-war reconstruction growth is the obvious
  confound. ISL A032, LUX A039, PRT A050 are late episodes unrelated to
  formation (checked); IRL A030/A031 likewise unrelated (IRL itself is coded
  deepening, see `case_notes/EURO_batch_note.md`).

## Conventions fixed by this block

1. Sphere-formation acts shared by N countries are coded as one block note
   with per-country rows; the judgments are stated once, deviations per row.
2. Window-edge formation (prior regime outside the 1945–2019 panel) makes
   the episode-level outcome test structurally indeterminate; such episodes
   enter the episode table (the sphere record must be complete) but are
   excluded from episode-level outcome counts by construction — registered
   here, before Step 6, so it cannot be read as ex-post selection.
3. Wartime alliances are not peacetime spheres; formation intervals start
   from non-membership.
