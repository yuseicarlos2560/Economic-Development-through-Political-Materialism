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

## 5. Q3 — State-apparatus restructuring

- **Anchors:** Skocpol (1979), Tilly (1990), Weber. Distinct from §4: targets the *machinery* (coercive, administrative, judicial, fiscal), not the rules of power.
- **Observable events:** military leadership purges or reorganizations; creation/abolition of security ministries; mass bureaucratic dismissals or politicization; fiscal centralization reforms. Sources: primary government records, IISS *Military Balance* for the coercive apparatus.
- Same ≥2-indicators-in-3-years rule.

## 6. Q4 — External realignment: severance and entry episodes

**Definition** (Keal 1983; Hast 2014): a sphere of influence exists where an outside power exercises *predominant influence* and members' independence is *constrained* — formal control is not required. Consequence: **informal spheres must be codable** (Cuba was never in the Warsaw Pact, yet was inside the Soviet sphere).

**Indicator families** (Lake 2009's measurable dimensions of hierarchy):

- **F1 Security ties:** alliance obligations (ATOP 1815–2018, Leeds et al. 2002; COW alliances 1816–2012, Gibler & Sarkees 2004); troop presence and bases.
- **F2 Economic dependence:** trade concentration with the patron (IMF DOTS); aid and subsidy flows (OECD DAC; historical estimates for the Soviet bloc, e.g., Soviet inflows ≈ 23% of Cuban GDP in 1985–88).
- **F3 Institutional bloc membership:** Warsaw Pact, CMEA, NATO, EU/EEA, OAS, EAEU, ALBA — objective entry/exit dates.
- **F4 Coercion:** sanctions episodes (Global Sanctions Data Base; Felbermayr et al. 2020) — severance is often *enforced* by the former patron (Venezuela 2017+).

**Validation layer:** UN General Assembly voting ideal points (Bailey, Strezhnev & Voeten 2017, 1946–present). A coded severance should coincide with ideal-point *divergence* from the patron; an entry with *convergence*. This is the quantitative cross-check on the qualitative coding.

**Decision rules:**

- **R1 (membership):** a state is inside a sphere when predominant influence is documented in ≥2 indicator families.
- **R2 (severance):** termination of ≥2 of {security guarantee, subsidized trade/aid, bloc membership} within a 3-year window, on either side's initiative. If the process is gradual (Venezuela–US, 2002–2017), the episode is **interval-coded** (earliest and latest defensible years) with robustness at both endpoints and the midpoint.
- **R3 (entry):** symmetric to R2 — establishment of ≥2 of the same ties.
- **R4 (voluntariness):** *imposed* if the patron ceased to exist or withdrew (USSR 1989–91) or the severance was enforced by sanctions; *chosen* otherwise (Walt 1987's balancing/bandwagoning logic guides the judgment). Imposed severances carry the causal identification of the design.
- **R5 (richer-sphere criterion):** for the sign prediction, a sphere counts as "richer" if the patron's GDP per capita exceeds the regional median in the entry year (Maddison; WDI) — making the sign rule mechanical, not judgmental.
- **R6 (systemic-shift flag):** episodes coinciding with a change in the global distribution of capabilities (1989–91) are flagged, keeping realignment and systemic shift distinct (Waltz 1979; Gilpin 1981).

**Episode table fields:** country; start/end (or interval); patron; direction (severance/entry); indicator families affected; voluntariness; systemic flag; capability flows (Δ trade share; subsidy share of GDP); ≥2 sources; coder; confidence.

**Calibration episodes (no China):** Yugoslavia–USSR 1948 (severance by expulsion); Spain–US bases agreement 1953 (entry); Cuba–USSR 1960 and 1989–91 (entry, then severance — the full cycle in one country); Egypt 1972–76 (Soviet expulsion followed by US entry — severance *and* entry in sequence); Vietnam 1989–95 (severance absorbed below threshold, then entry — tests both the threshold and the timing rule); the Baltics 1991 and 2004 (severance and entry as two dated episodes); Venezuela–US 2002–17 (interval-coded severance); Greece 2015 (threatened but unconsummated severance — coded with a "threat" flag, matching the sub-threshold outcome).

## 7. Q5 — Outcomes

- **Disruption (negative):** Rodrik-style collapse criterion — real GDP per capita contraction ≥ 15% peak-to-trough within ≤ 5 years, **or** deceleration ≥ 3 pp below the prior 5-year average sustained ≥ 3 years; hyperinflation (≥ 500% annual) or a sudden stop qualify independently. (Calibration anchors: Greece −26% in; Spain and Brexit below or near the threshold — the calibration cases exist precisely to fix these bounds.)
- **Acceleration (positive):** Hausmann–Pritchett–Rodrik-style — growth ≥ 3.5% per year sustained ≥ 8 years, ≥ 2 pp above the prior growth regime, with post-acceleration output above the pre-acceleration maximum.
- Both thresholds are fixed **before** case coding and are symmetric by construction, as required by `draft2.tex` §4.

## 8. Window and coverage

- **Coding window: 1945–2019** (case narratives may extend to 2023). The panel regression starts in 1960 (WDI availability); the 1945 start supplies pre-period baselines and early canonical episodes (e.g., Yugoslavia 1948).
- **Regions:** Latin America, Europe, post-Soviet space, East Asia (Koreas, Japan, Vietnam) — ~75 countries. China is excluded from the design.
- **Units:** country–year panel plus a separate episode table (§6 fields).

## 9. Sufficiency verdict

With all five questions codified, every variable in equation (1) and every cell of Table 1 is generated by a published rule: **the methodology is sufficient.** The only additions are data/method citations (no change to the theory): Bailey, Strezhnev & Voeten (2017); Felbermayr et al. (2020); IMF DOTS; Elkins, Ginsburg & Melton (2009). Known residual risks, stated honestly: informal-sphere coding is the judgment-heaviest part (mitigated by the ≥2-families rule and the UN-voting cross-check), and gradual severances require interval coding with endpoint robustness.

**Positive-cell coverage:** Vietnam is added as the entry case with an intact power structure (Đổi Mới 1986 = policy change; US normalization 1995 = entry; power structure untouched throughout). Caveat recorded in the case file: its 1989–91 Soviet severance did not produce a threshold-level collapse, so Vietnam enters the design as an entry case and as a calibration case for the severance threshold, not as severance evidence.
