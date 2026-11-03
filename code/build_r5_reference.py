"""Build the R5 reference: regional GDP-pc medians + patron GDP-pc series
(Coding_Protocol §6 R5, mechanical richer-sphere test).

Rule (fixed): a sphere counts as richer when the patron's GDP per capita
exceeds the regional median in the entry year. Regional median = median over
OUR 73 panel countries within OUR four region labels (countries.csv) — the
regions were defined for this sample, so the reference set is the sample.
Patron wealth = the sphere hegemon's GDP pc (Lake 2009's one-hierarchy logic;
E013-E015 precedent used US for the Western sphere): USA, USSR/RUS (USSR
series to 1990, Russia from 1990 — Maddison covers both), CHN.

Source: Maddison 2023 (mpd2023_full.csv) — covers 1945-2022 for all patrons
and panel countries. WDI cross-check reported, never spliced in.

Output: data_clean/r5_reference.csv
  year, region, median_gdppc, n_countries, usa_gdppc, ussr_rus_gdppc, chn_gdppc
"""
import pandas as pd

OUT = "data_clean/r5_reference.csv"

countries = pd.read_csv("data_clean/countries.csv")[["iso3", "region"]]
mpd = pd.read_csv("data_raw/mpd2023_full.csv")
mpd = mpd[["countrycode", "year", "gdppc"]].dropna()
mpd = mpd[(mpd["year"] >= 1945) & (mpd["year"] <= 2022)]
mpd["year"] = mpd["year"].astype(int)

panel = mpd.merge(countries, left_on="countrycode", right_on="iso3")
med = (panel.groupby(["region", "year"])["gdppc"]
       .agg(median_gdppc="median", n_countries="size").reset_index())

def patron_series(codes, label):  # codes: list tried in order per year
    d = mpd[mpd["countrycode"].isin(codes)]
    d = d.sort_values(["year", "countrycode"]).drop_duplicates("year", keep="last")
    return d[["year", "gdppc"]].rename(columns={"gdppc": label})

# USSR code in Maddison 2023 is 'SUN'; Russia 'RUS' begins 1990 -> USSR first,
# RUS from 1991 (drop_duplicates keep='last' would pick RUS in 1990 overlap,
# so split explicitly)
ussr = mpd[mpd["countrycode"] == "SUN"]
rus = mpd[(mpd["countrycode"] == "RUS") & (mpd["year"] >= 1991)]
urr = pd.concat([ussr, rus]).drop_duplicates("year")[["year", "gdppc"]].rename(
    columns={"gdppc": "ussr_rus_gdppc"})

pat = patron_series(["USA"], "usa_gdppc").merge(urr, on="year", how="outer")
pat = pat.merge(patron_series(["CHN"], "chn_gdppc"), on="year", how="outer")

out = med.merge(pat, on="year", how="left").sort_values(["region", "year"])
out.to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(out)} region-years")
print(out.groupby("region")["year"].agg(["min", "max"]).to_string())

# calibration check: E002 (1953, Europe): US 16917 vs Europe median 6594
r = out[(out.region == "Europe") & (out.year == 1953)].iloc[0]
print(f"\nE002 check 1953 Europe: median={r.median_gdppc:.0f} (expect ~6594), "
      f"USA={r.usa_gdppc:.0f} (expect ~16917)")
# E013 check: 2004 post-Soviet median 7782, US 48493
r = out[(out.region == "Post-Soviet") & (out.year == 2004)].iloc[0]
print(f"E013 check 2004 Post-Soviet: median={r.median_gdppc:.0f} (expect ~7782), "
      f"USA={r.usa_gdppc:.0f} (expect ~48493)")
