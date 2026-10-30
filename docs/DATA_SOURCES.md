# Data Sources Manifest — Phase 0/1

Compiled: 2026-10-30. All downloaded files live in `data_raw/` (originals kept untouched).
Project-generated files: `data_clean/countries.csv` (73 countries, 4 regions, China excluded),
`data_clean/panel_spine.csv` (5,475 country-year rows, 1945–2019), `data_clean/episodes.csv`
(header only, to be filled in Phase 2), `docs/thresholds.md` (registered event thresholds).

## Downloaded and ready

| Source | File(s) | Version/vintage | Coverage | Purpose | Bib key |
|---|---|---|---|---|---|
| World Bank WDI | `data_raw/WDI/WDICSV.csv` (+ country/series metadata) | Oct 2025 release | 1960–2024, 217 economies | Outcomes: GDP pc (constant), growth, CPI inflation, oil rents, trade shares, FDI, exchange rate | worldbank_wdi |
| Maddison Project Database 2023 | `data_raw/mpd2023_web.xlsx`, `mpd2023_full.csv` (131,144 rows) | MPD 2023 | 1–2022 AD, 169 countries | Long-run GDP pc; covers Cuba and North Korea where WDI is absent; post-Soviet series start 1990 | bolt_vanzanden_2024 |
| IMF WEO (IMF Data Portal API, `IMF.RES:WEO` v9.0.0) | `data_raw/WEO/weo_{NGDP_RPCH,PCPIPCH,LP,NGDPDPC}.csv` | Oct 2026 API pull | 1980–2019, our 73 countries | Real GDP growth, CPI inflation, population, GDP pc (USD); includes staff estimates for Venezuela's recent collapse years | imf_weo |
| Archigos 4.1 (leaders) | `data_raw/Archigos_4.1_stata14.dta`, `archigos_4_1.csv` (3,409 leader spells) | v4.1 | 1875–2015 | Leader entry/exit/manner of exit: domestic-leadership-change control | goemans_gleditsch_chiozza_2009 |
| COW Formal Interstate Alliances v4.1 | `data_raw/version4.1_csv/*.csv` | v4.1 | 1816–2012 | Alliance membership: binary realignment coding (severance/entry) | gibler_sarkees_2004 |
| UN Ideal Points (Bailey–Strezhnev–Voeten) | `data_raw/UN_IdealPoints_Jul2025.tab`, `.csv` (11,440 obs) | Jul 2025 release | 1946–2024, 199 countries | Continuous alignment measure: distance from US/USSR-Russia ideal points; extends beyond alliance data | bailey_strezhnev_voeten_2017 |

## Requires manual action (not scriptable)

| Source | How to get it | Coverage | Purpose | Bib key |
|---|---|---|---|---|
| ATOP (Alliance Treaty Obligations and Provisions) | Browser download at atopdata.org/data.html (site blocks scripted downloads; returns 403 to curl) | 1815–2018 | Extends alliance coding past COW's 2012 endpoint; obligation detail | leeds_etal_2002 |
| Global Sanctions Data Base (GSDB), Release 4 | Email request to GSDB@drexel.edu | 1950–2023 | Sanctions episodes: treatment intensity, a key channel of severance | felbermayr_etal_2020 |
| IMF DOTS (Direction of Trade Statistics) | data.imf.org/DOT bulk download or API | 1947–present | Bilateral trade shares with patron before/after episodes: the Δ-trade-share variable in episodes.csv | imf_dots |
| Comparative Constitutions Project | comparativeconstitutionsproject.org (free registration) | 1789–present | Constitutional change: nominal regime-change control for the power-structure distinction | elkins_ginsburg_melton_2009 |
| EBRD Transition Reports | ebrd.com (annual PDFs, free) | 1989–present | Transition indicators for post-socialist cases; qualitative corroboration | ebrd_transition |
| ECLAC CEPALSTAT | cepalstat.cepal.org (web query) | varies | Cuban and Latin American series where WDI/WEO have gaps (Cuba national accounts) | eclac_cepalstat |

## Known coverage gaps (to flag during coding)

- North Korea: absent from WDI and WEO. Outcomes come from Maddison only (estimates; low confidence).
- Cuba: partial in WDI (GDP pc present, many indicators missing); absent from WEO. Supplement with CEPALSTAT/Maddison.
- Post-Soviet states: no data before 1990 (Maddison/WDI); episodes before independence use USSR aggregates where relevant.
- Archigos ends 2015: post-2015 leadership changes must be hand-coded (small number in our window).
- COW alliances end 2012; ATOP (manual) covers to 2018; UN ideal points cover the whole window and are the fallback for post-2012 alignment.
- Venezuela: WEO figures for 2015–2019 are staff estimates, not official statistics — treat with care in coding.
