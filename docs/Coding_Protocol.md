# Coding Protocol: Domestic Political Events and External Realignment Episodes

**Status.** Working document. Guides the construction of every variable in equation (1) and Table 1 of `draft2.tex`. Not part of the thesis draft. All China-related cases are excluded from the design.

**Principles.**

1. *Observable events over expert judgment* — this is the thesis's own measurement critique applied to itself (Treier & Jackman 2008; Little & Meng 2024). Every coding decision must rest on primary documents or behavioral data, not on country ratings.
2. *Multi-indicator rules* — every judgment-heavy category is decided by a "≥2 indicator families within a 3-year window" rule, so that no single subjective judgment decides a case.
3. *Timing rule* (from `draft2.tex` §4): an outcome is attributed to a realignment only if it follows it.
4. *Two independent sources* per episode; a random subset double-coded; target Cohen's κ ≥ 0.7; disagreements and their resolutions published with the replication files.
5. Expert-coded indices (V-Dem, Polity) are used **only as validation benchmarks** for convergence checks — never as regressors (consistent with the Data section).

---

## 1. Why all five framework questions must be codified

Each question of the framework generates specific variables; without any one of them, a part of the design is untestable.

| Framework question | Variables generated | Where they enter |
|---|---|---|
| Who governs | `Turnover`, coalition change | β₃; Table 1 row 1 |
| How is power organized | `RegimeChange` (formal), `PowerStructure` (effective) | β₄, β₅; Table 1 rows 1–2 |
| Through which institutions | Apparatus restructuring | Table 1 row 2 |
| Where the state stands | `Severance`, `Entry`, voluntariness, systemic-shift flag | β₁, β₂; Table 1 columns |
| What outcomes follow | `Disruption`, `Acceleration` (the DV) | g_it; thresholds |

The critical case is the **structure of political power**. H1 states a null *conditional on* the power structure remaining untouched — "untouched" is a measurement claim, not a logical one. Without a coding rule: (i) H1 cannot be tested, (ii) Table 1's middle row cannot be filled, and (iii) the Venezuela crux (was 1998–2009 a transformation?) stays a matter of opinion. The rule in §4.2 resolves it.

---

## 2. Q1 — Who governs: turnover and coalition change

- **Source:** Archigos (Goemans, Gleditsch & Chiozza 2009), covering every effective leader's entry and exit, and its manner (election, coup, succession, natural death), 1875–2015. Post-2015 turnover is hand-coded from constitutional records and news archives.
- **Variables:** `Turnover` = 1 in the year the effective leader is replaced. Irregular manner (coup, forced removal) flagged separately — manner matters for the narrative layer.
- **Coalition change:** change in the party or coalition holding the executive, coded from election records and government composition (Bueno de Mesquita et al. 2003 motivate the distinction between replacing the leader and replacing the support coalition).

## 3. Q2a — Formal regime change

- **Definition** (Linz & Stepan 1996; Linz 2000): change in the formal rules governing access to and organization of power.
- **Observable events:** constitutional replacement or suspension (Comparative Constitutions Project; Elkins, Ginsburg & Melton 2009), abolition/suspension of elections, change in executive-selection rules.
- **Variable:** `RegimeChange` = 1 in the year of such an event. A new constitution that leaves effective arrangements unchanged is coded here and *not* in §4 — that separation is exactly what the framework is for.
- **Uncodified orders:** a formal political order does not require a single codified constitution. Constitutional statutes, authoritative conventions, parliamentary rules, and succession arrangements can supply the baseline and the formal event. CCP is a catalogue and candidate source, not proof that an uncodified order is absent or unchanged.
- **Formal dating:** use promulgation or formal entry into force. Keep that date separate from the effective-implementation date used in §4.

## 4. Q2b — Structure of political power (the hard category)

**Definition** (García-Trevijano): the *effective* organization and control of power — separation or concentration of powers in practice, independence of representation, party–state relationship, capacity to control rulers.

**Four dimensions, each with observable proxies:**

| Dimension | Observable proxies (examples) |
|---|---|
| (a) Separation/concentration of powers in practice | Enabling laws granting decree powers (Venezuela 2000, 2007, 2013); court-packing or judicial purges (TSJ expansion 2004); legislature dissolved or replaced (Venezuela 2017) |
| (b) Independence of representation | Electoral-rule changes eliminating territorial or direct representation; bans on opposition participation |
| (c) Party–state fusion | Ruling-party control over apparatus appointments (PDVSA purge 2002–03); state resources systematically funding the ruling party |
| (d) Control of rulers | Abolition of term limits (Venezuela 2009 referendum); instances of rulers actually removed by institutional checks |

**Decision rule:** `PowerStructure` transformation = documented change in **≥2 of the 4 dimensions within a 3-year window**, each anchored to a primary legal or institutional act. This deliberately mirrors the severance rule in §6 — the domestic and international sides of the model use the same evidentiary standard.

**What this resolves:** Venezuela is no longer "contested" by opinion — the rule produces a determinate coding (transformation, consummated by 2009 at the latest). Borderline cases get interval codes with robustness at both endpoints.

**Validation:** convergence check against V-Dem's judicial-independence and election-quality items, used strictly as a benchmark for inter-coder reliability, never as data.

### 4.1 Operational clarifications from the Spain/UK/US/France calibration

- **Change is not completion.** A positive code records effective change, not arrival at democracy, Trevijano's republican ideal, or complete representation/separation/control. Do not add an unregistered magnitude or democratic-completion threshold.
- **Representation:** franchise expansion changes access but does not automatically change independence of representation. Vertical devolution changes the allocation of authority but does not by itself change the independence of the existing national representation. Electoral-system changes must affect direct/territorial representation, opposition participation, or representatives' dependence on party leadership.
- **Party financing:** systematic state financing of permanent party organizations can support dimension (c) only when the record demonstrates durable party–state integration. Candidate-specific subsidies, election-cost reimbursement, and campaign-finance regulation do not qualify automatically. Apply the same organizational-integration test in every country; if that evidence is unresolved, the contributing dimension and episode remain provisional.
- **Control of rulers:** routine elections, parliamentary resistance, court decisions, and removals under existing rules document the operation of a check, not a change in that check. Formal succession rules are not relabelled as a new capacity to control rulers.
- **Effective dating:** the principal panel year is the year the second qualifying dimension becomes effective. Preserve the full process interval and endpoint/midpoint robustness for uncertain cases. Persistence does not generate a new event each year.
- **No relabelling:** one act cannot satisfy two dimensions merely because it has two descriptions. Distinct substantive effects must be independently demonstrated.

### 4.2 Full-sweep candidate generation and country continuity

- **Coverage:** every one of the 73 panel countries is reviewed over 1945–2019. The Spain/UK/France calibration determinations are carried into the sweep; the US remains a non-panel calibration reference. A country with no accepted episode receives an explicit negative determination.
- **Formal-event candidates:** every mapped CCP `new`, `interim`, `suspension`, `reinstated`, `amendment`, or `samendment` record in the window enters a candidate ledger. CCP event type never substitutes for content review: amendments can qualify or fail, and non-CCP constitutional statutes can qualify in uncodified orders.
- **Effective-power and apparatus candidates:** CCP is a recall floor, not the universe of cases. Each country review also examines coups and emergency rule, electoral and party laws, enabling acts, judicial restructuring, control-of-rulers rules, and durable coercive, administrative, judicial, and fiscal reorganizations. A CCP `non-event` cannot establish continuity on these dimensions.
- **Country continuity:** Russia inherits the USSR record; Czechia and Slovakia share the Czechoslovak record through 1992; Germany follows the FRG, not the GDR; Vietnam follows the DRV/unified state; the Koreas follow their respective post-1948 states. Other Soviet and Yugoslav successor states do not import the predecessor's domestic events before independence; their foundational orders and restoration acts are coded on their own documentary records.
- **Decision record:** accepted, rejected, conditional, and unknown candidates retain their substantive reason and legal/institutional anchors. Formal and effective dates, process intervals, qualifying dimensions/components, coder, and confidence are recorded separately. Unknown content produces a missing country-year value, never a zero. Conditional episodes likewise remain outside the accepted event set and are missing in the country-year output. No outcome series or expert-coded regime index may alter candidate generation, dates, or acceptance.

## 5. Q3 — State-apparatus restructuring

- **Anchors:** Skocpol (1979), Tilly (1990), Weber. Distinct from §4: targets the *machinery* (coercive, administrative, judicial, fiscal), not the rules of power.
- **Observable events:** military leadership purges or reorganizations; creation/abolition of security ministries; mass bureaucratic dismissals or politicization; fiscal centralization reforms. Sources: primary government records, IISS *Military Balance* for the coercive apparatus.
- **Decision rule:** documented change in **≥2 distinct components** among coercive, administrative, judicial, and fiscal machinery within a 3-year window. The principal panel year is the year the second component becomes effective; preserve the full interval.
- **Substantive reorganization required:** record an actual transfer, consolidation, abolition, or politicization of durable functions and authority. Departmental renaming, routine agency creation, and administrative convenience alone do not qualify.
- **Fiscal boundary:** durable revenue, treasury, budgetary, extraction, and fiscal-control machinery can qualify. Tax rates, annual budgets, spending programs, and other fiscal-policy settings do not.
- **No relabelling:** one act cannot satisfy two components merely through two descriptions; each component needs its own substantive organizational change.

## 6. Q4 — External realignment: severance and entry episodes

**Definition** (Keal 1983; Hast 2014): a sphere of influence exists where an outside power exercises *predominant influence* and members' independence is *constrained* — formal control is not required. Consequence: **informal spheres must be codable** (Cuba was never in the Warsaw Pact, yet was inside the Soviet sphere).

**Indicator families** (Lake 2009's measurable dimensions of hierarchy):

- **F1 Security ties:** alliance obligations (ATOP 1815–2018, Leeds et al. 2002; COW alliances 1816–2012, Gibler & Sarkees 2004); troop presence and bases.
- **F2 Economic dependence:** trade concentration with the patron (IMF DOTS); aid and subsidy flows (OECD DAC; historical estimates for the Soviet bloc, e.g., Soviet inflows ≈ 23% of Cuban GDP in 1985–88).
- **F3 Institutional bloc membership:** Warsaw Pact, CMEA, NATO, EU/EEA, OAS, EAEU, ALBA — objective entry/exit dates.
- **F4 Coercion:** sanctions episodes (Global Sanctions Data Base; Felbermayr et al. 2020) — severance is often *enforced* by the former patron (Venezuela 2017+).

**Validation layer:** UN General Assembly voting ideal points (Bailey, Strezhnev & Voeten 2017, 1946–present). A coded severance should coincide with ideal-point *divergence* from the patron; an entry with *convergence*. This is the quantitative cross-check on the qualitative coding.

### 6.1 The four judgments, made explicit (added 2026-11-02)

Each candidate episode is decided by answering four narrow factual questions, in order:

1. **Membership (R1):** was the country inside a sphere, and whose? Predominant influence documented in ≥2 indicator families (Keal 1983; Hast 2014; Lake 2009). Formal control is not required — informal spheres are codable.
2. **Change (R2/R3):** did ≥2 of {security guarantee, subsidized trade/aid, bloc membership} terminate (severance) or establish (entry) within a 3-year window? Gradual processes are interval-coded (earliest and latest defensible years), never forced into a single year.
3. **Voluntariness (R4):** imposed (patron collapsed/withdrew, or enforced the break by sanctions) or chosen (Walt 1987). Imposed severances carry the causal identification.
4. **Sign (R5, entry only):** was the new sphere richer — patron GDP pc above the regional median in the entry year (Maddison/WDI)? Mechanical, not judgmental. R6 (systemic-shift flag) is recorded alongside.

**Non-contamination rule.** Outcomes were coded blind to realignment dates (Phase 2). The reverse must also hold: realignment dates are fixed by the documentary record only, and must never be adjusted to fit the already-coded outcomes. An episode whose outcome does not match the prediction is a falsification, not a coding error to be repaired.

**Working order.** The nine calibration episodes below are coded first and fix the conventions; only then the full sweep. Each episode gets: a row in `data_clean/episodes.csv`, a case note in `case_notes/`, a log entry in `docs/PHASE3_LOG.md`, and the UN ideal-point divergence/convergence check.

**Decision rules:**

- **R1 (membership):** a state is inside a sphere when predominant influence is documented in ≥2 indicator families.
- **R2 (severance):** termination of ≥2 of {security guarantee, subsidized trade/aid, bloc membership} within a 3-year window, on either side's initiative. If the process is gradual (Venezuela–US, 2002–2017), the episode is **interval-coded** (earliest and latest defensible years) with robustness at both endpoints and the midpoint.
- **R3 (entry):** symmetric to R2 — establishment of ≥2 of the same ties.
- **R4 (voluntariness):** *imposed* if the patron ceased to exist or withdrew (USSR 1989–91) or the severance was enforced by sanctions; *chosen* otherwise (Walt 1987's balancing/bandwagoning logic guides the judgment). Imposed severances carry the causal identification of the design.
- **R5 (richer-sphere criterion):** for the sign prediction, a sphere counts as "richer" if the patron's GDP per capita exceeds the regional median in the entry year (Maddison; WDI) — making the sign rule mechanical, not judgmental.
- **R6 (systemic-shift flag):** episodes coinciding with a change in the global distribution of capabilities (1989–91) are flagged, keeping realignment and systemic shift distinct (Waltz 1979; Gilpin 1981).

**Episode table fields:** country; start/end (or interval); patron; direction (severance/entry); indicator families affected; voluntariness; systemic flag; capability flows (Δ trade share; subsidy share of GDP); ≥2 sources; coder; confidence.

**Calibration episodes (no China):** Yugoslavia–USSR 1948 (severance by expulsion); Spain–US bases agreement 1953 (entry); Cuba–USSR 1960 and 1989–91 (entry, then severance — the full cycle in one country); Egypt 1972–76 (Soviet expulsion followed by US entry — severance *and* entry in sequence); Vietnam 1989–95 (severance absorbed below threshold, then entry — tests both the threshold and the timing rule); the Baltics 1991 and 2004 (severance and entry as two dated episodes); Venezuela–US 2002–17 (interval-coded severance); Greece 2015 (threatened but unconsummated severance — coded with a "threat" flag, matching the sub-threshold outcome).

### 6.2 Patron set and candidate generation for the full sweep (added 2026-11-03)

**Patron set.** Three candidate sphere holders, grounded only in the framework's existing sources:

1. **The US-led Western sphere** — one sphere, not three: the UK and the European allies are subordinate members of the US-centered hierarchy (Lake 2009); NATO and EU alignment is alignment with that sphere (Walt 1987; Buzan & Wæver 2003). The "USA/EU" co-patron convention from calibration (E013–E015) stands.
2. **The USSR/Russia sphere** — the second pole of the 1945–91 bipolar distribution (Waltz 1979), great-power status resting on military capability (Mearsheimer 2001); Russia inherits the residual sphere (CSTO/EAEU as F3).
3. **China, from 2013** — a rising great power in Gilpin's (1981) differential-growth logic and Mearsheimer's (2001) great-power sense; activation anchored to the Belt & Road launch (2013), with sensitivity at 2008 recorded in affected case notes. China's pre-2013 relationship with North Korea (1961 treaty) is handled in the PRK shadow-case note, not by moving the activation date.

**Not sphere holders:** Venezuela and other regional powers. ALBA-type blocs are recorded in case notes as context, never coded as spheres. Consistently, Cuba–Venezuela 2000s is a documented patron–client subsidy relationship for the narrative layer (Step 8), not a coded sphere-entry episode; `docs/Cases.md` carries a reconciling note.

**Candidate generation (screen before coding).** The sweep's candidate list is generated mechanically and blind to outcomes. For each panel country × patron, a candidate window opens where **≥2 of the following signal change within a 3-year window**: F1 alliance establishment/termination with the patron (ATOP; COW cross-check ≤2012); F3 bloc entry/exit (Warsaw Pact, CMEA, NATO, EU/EEA, OAS, EAEU — objective dates); F4 GSDB-R5 sanctions episode with sender = patron; F2 DOTS trade-share break with the patron. UN ideal points remain the *validation* layer and are not a screen input. Every candidate is then decided by the four judgments of §6.1; rejected candidates are recorded with their rejection reasons, so the episode table's audit trail covers the whole panel, including countries with no realignment.

## 7. Q5 — Outcomes

- **Disruption (negative):** Rodrik-style collapse criterion — real GDP per capita contraction ≥ 15% peak-to-trough within ≤ 5 years, **or** deceleration ≥ 3 pp below the prior 5-year average sustained ≥ 3 years; hyperinflation (≥ 500% annual) or a sudden stop qualify independently. (Calibration anchors: Greece −26% in; Spain and Brexit below or near the threshold — the calibration cases exist precisely to fix these bounds.)
- **Acceleration (positive):** Hausmann–Pritchett–Rodrik-style — growth ≥ 3.5% per year sustained ≥ 8 years, ≥ 2 pp above the prior growth regime, with post-acceleration output above the pre-acceleration maximum.
- Both thresholds are fixed **before** case coding and are symmetric by construction, as required by `draft2.tex` §4.
- **Episode segmentation (added 2026-10-30):** the panel disruption indicator is the union of all flagged country-years. For the episode table, an episode ends after 3+ consecutive clean (unflagged) years; contiguous flagged runs are one episode. Decided after Venezuela's drawdown windows chained 1978–2019 into a single 41-year "episode," which is unusable for matching to realignments. The panel indicator is unaffected by segmentation.

### 7.1 Source hierarchy and splicing rules (added 2026-10-30)

The outcome series is built from WDI first, Maddison 2023 for gaps (Cuba, North Korea, pre-1990 post-Soviet states), WEO for politically censored years (Venezuela's collapse; staff estimates flagged). Three reasons:

1. **Threshold calibration.** The numeric thresholds come from Hausmann, Pritchett & Rodrik (2005) and Rodrik (1999), whose screens run on WDI-family national accounts. Applying their numbers to series with different statistical properties would use a ruler calibrated for another instrument.
2. **Levels across sources are not comparable.** WDI reports constant 2015 USD, Maddison 2011 PPP dollars; the Maddison/WDI level ratio for identical country-years ranges from 0.44 to 13.84 in our sample (median 1.32). Splicing levels would manufacture fake "disruptions" at the seam. A fixed hierarchy removes that discretion (Treier & Jackman 2008; Little & Meng 2024 applied to ourselves).
3. **Growth rates are far more robust to source choice than levels**, because base-year and PPP differences cancel in the ratio. Verified on our own data before any episode coding: across 3,398 country-years where WDI and Maddison overlap (70 of our 73 countries), growth-rate correlation is 0.90, median absolute difference 0.49 pp, sign disagreement 6.2%. Cross-source and cross-vintage growth discrepancies of this size are documented in the literature (Johnson, Larson, Papageorgiou & Subramanian 2013; Feenstra, Inklaar & Timmer 2015), which is why the robustness rule below exists.

**Splicing rules:**

- (a) Provenance flag per cell (which source supplied it).
- (b) Seam rule: a growth rate for year *t* is computed only when the same source covers *t* and *t−1*; otherwise the cell is marked as a seam and the rate taken from the source that has both years.
- (c) Level-based checks (acceleration rule 4: post-output above pre-max) computed strictly within a single source per episode.
- (d) Robustness: the episode screen is re-run on WDI-only and Maddison-only versions for overlapping countries; any episode that flips is flagged in the paper's robustness section, not silently absorbed.

**Why fill gaps at all:** missing data are not random — Cuba and North Korea are absent from WDI/WEO because of the same political conditions that make them theoretically central. Dropping them would censor key cases on the treatment itself; documented secondary estimates with provenance flags are the lesser error.

## 8. Window and coverage

- **Coding window: 1945–2019** (case narratives may extend to 2023). The panel regression starts in 1960 (WDI availability); the 1945 start supplies pre-period baselines and early canonical episodes (e.g., Yugoslavia 1948).
- **Regions:** Latin America, Europe, post-Soviet space, East Asia (Koreas, Japan, Vietnam) — ~75 countries. China is excluded from the design.
- **Units:** country–year panel plus a separate episode table (§6 fields).

## 9. Sufficiency verdict

With all five questions codified, every variable in equation (1) and every cell of Table 1 is generated by a published rule: **the methodology is sufficient.** The only additions are data/method citations (no change to the theory): Bailey, Strezhnev & Voeten (2017); Felbermayr et al. (2020); IMF DOTS; Elkins, Ginsburg & Melton (2009). Known residual risks, stated honestly: informal-sphere coding is the judgment-heaviest part (mitigated by the ≥2-families rule and the UN-voting cross-check), and gradual severances require interval coding with endpoint robustness.

**Positive-cell coverage:** Vietnam is added as the entry case with an intact power structure (Đổi Mới 1986 = policy change; US normalization 1995 = entry; power structure untouched throughout). Caveat recorded in the case file: its 1989–91 Soviet severance did not produce a threshold-level collapse, so Vietnam enters the design as an entry case and as a calibration case for the severance threshold, not as severance evidence.
