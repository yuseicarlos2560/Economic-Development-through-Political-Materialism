# Registered Outcome Thresholds

**Registered:** 2026-10-30, before any case coding or data inspection.
**Source:** `draft2.tex` §5.3 (Coding rules). Any later change must be logged below with a reason, and all results re-run as robustness — thresholds are never changed silently.

## Disruption (negative discontinuity)

Coded when **any** of the following holds (following Rodrik 1999's growth-collapse logic):

1. Real GDP per capita contracts **≥ 15% peak-to-trough within ≤ 5 years**; or
2. Growth falls **≥ 3 percentage points below its prior 5-year average, sustained ≥ 3 years**; or
3. Annual inflation **≥ 500%** (hyperinflation qualifier); or
4. A documented sudden stop / capital-flight episode (independent qualifier).

## Acceleration (positive discontinuity)

All of the following (following Hausmann, Pritchett & Rodrik 2005):

1. Real GDP per capita growth **≥ 3.5% per year**;
2. Sustained for **≥ 8 years**;
3. **≥ 2 percentage points above** the prior growth regime;
4. Post-acceleration output per capita above the pre-acceleration maximum.

## Rationale

The rules identify large and lasting changes in economic trajectories. They are coding benchmarks, not natural constants. Their value comes from measuring distinct economic processes, classifying clear and borderline cases consistently, and producing results that survive alternative cutoffs.

- **D1 — severe output loss.** The 15% peak-to-trough cutoff follows Barro's (2006) definition of a macroeconomic disaster. The five-year limit requires a sharp loss rather than a slow decline over a much longer period.
- **D2 — sustained deceleration.** Pritchett (2000) reports an average absolute growth shift of 3.4 percentage points in developing countries. The three-point cutoff is close to that magnitude. Requiring the shortfall relative to the prior five-year average for three consecutive years excludes a one-year fluctuation and captures a lasting slowdown that need not produce a 15% contraction.
- **D3 — extreme inflation.** Reinhart and Rogoff (2011) use 500% annual inflation for modern hyperinflation. At that rate, the price level rises at least sixfold in one year. The annual rule matches the project's annual data and differs from Cagan's monthly definition.
- **A1–A4 — sustained acceleration.** HPR's filter combines rapid growth (3.5%), a clear improvement over the prior regime (2 points), persistence (eight years), and output above the previous peak. These conditions exclude both ordinary growth and a short rebound after a crisis. HPR describe the numerical choices as defensible but arbitrary, which makes alternative-threshold checks necessary.

Disruption and acceleration have different time horizons because output collapse and sustained take-off are different processes. They are signed outcomes of the framework, not numerically symmetric filters.

## Calibration cases

The cases were chosen before the full sweep to cover distinct classification problems. They are not a random sample and are not used to estimate the effect of realignment.

| Case | Classification problem |
|---|---|
| Greece 2007–13 | Clear severe collapse; positive anchor for D1/D2 |
| Spain 2007–13 | Prolonged but less severe downturn; tests depth and persistence |
| Mexico 1994–95 | Short V-shaped financial crisis; tests whether a temporary contraction is mistaken for a lasting break |
| Vietnam 1989–91 | Imposed severance with continued positive growth; tests whether realignment alone is mistaken for disruption |
| Brexit 2016–23 | Negotiated partial exit with continued market access; tests a sub-threshold outcome and proportional effects |
| South Korea and Chile | Clear sustained accelerations; positive anchors for A1–A4 |

These cases check the coding rules, not whether H2 is true. Core hypothesis-testing cases such as Cuba are not used to set the outcome cutoffs. The full-panel analysis and alternative thresholds determine whether the results depend on these choices.

## Change log

| Date | Change | Reason | Re-run as robustness? |
|---|---|---|---|
| 2026-11-13 | Documentation only: added the rationale, literature anchors, and calibration-case selection logic; no numerical rule changed | Make threshold construction explicit and correct the earlier attribution | Not applicable; thresholds unchanged |
