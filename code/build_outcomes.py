"""Build the outcome series for the panel, following Coding_Protocol.md §7.1.

Hierarchy: WDI first, Maddison 2023 for gaps, WEO as last fallback (growth/inflation
only — WEO levels are current USD and never spliced into the level series).

Outputs data_clean/outcomes.csv with one row per country-year (1945-2019):
  gdppc          spliced real GDP per capita level (WDI or Maddison only)
  gdppc_source   'wdi' | 'maddison'
  growth_pc      real GDP per capita growth, % (WEO fallback is total-GDP growth)
  growth_source  'wdi' | 'maddison' | 'weo_total'
  seam           True when the level source changes between t-1 and t
  inflation      CPI inflation, %
  infl_source    'wdi' | 'weo'
"""
import pandas as pd
import numpy as np

SPINE = "data_clean/panel_spine.csv"
OUT = "data_clean/outcomes.csv"

spine = pd.read_csv(SPINE)[["iso3", "year"]]
iso = set(spine["iso3"])
years = [str(y) for y in range(1960, 2020)]  # WDI starts in 1960

# --- WDI ---
wdi = pd.read_csv("data_raw/WDI/WDICSV.csv", dtype=str)
wdi = wdi[wdi["Country Code"].isin(iso)]

def wdi_series(code, name):
    d = wdi[wdi["Indicator Code"] == code][["Country Code"] + years]
    d = d.set_index("Country Code").stack().rename(name)
    d = d.rename_axis(["iso3", "year"]).reset_index()
    d["year"] = d["year"].astype(int)
    d[name] = pd.to_numeric(d[name], errors="coerce")
    return d

wdi_lvl = wdi_series("NY.GDP.PCAP.KD", "wdi_lvl")
wdi_g = wdi_series("NY.GDP.PCAP.KD.ZG", "wdi_g")
wdi_cpi = wdi_series("FP.CPI.TOTL.ZG", "wdi_cpi")

# --- Maddison ---
mpd = pd.read_csv("data_raw/mpd2023_full.csv")
mpd = mpd[(mpd["countrycode"].isin(iso)) & (mpd["year"] >= 1944) & (mpd["year"] <= 2019)]
mpd = mpd[["countrycode", "year", "gdppc"]].rename(
    columns={"countrycode": "iso3", "gdppc": "mpd_lvl"})
mpd["mpd_g"] = mpd.groupby("iso3")["mpd_lvl"].pct_change() * 100

# --- WEO (growth and inflation only) ---
def weo_series(code, name):
    d = pd.read_csv(f"data_raw/WEO/weo_{code}.csv")
    d = d.rename(columns={"value": name})
    d = d[(d["iso3"].isin(iso)) & (d["year"] >= 1945) & (d["year"] <= 2019)]
    return d[["iso3", "year", name]]

weo_g = weo_series("NGDP_RPCH", "weo_g")
weo_cpi = weo_series("PCPIPCH", "weo_cpi")

# --- merge everything onto the spine ---
df = spine
for d in (wdi_lvl, wdi_g, wdi_cpi, mpd, weo_g, weo_cpi):
    df = df.merge(d, on=["iso3", "year"], how="left")

# --- level series: WDI > Maddison ---
df["gdppc"] = df["wdi_lvl"].fillna(df["mpd_lvl"])
df["gdppc_source"] = np.where(df["wdi_lvl"].notna(), "wdi",
                     np.where(df["mpd_lvl"].notna(), "maddison", None))

# --- growth: WDI official > Maddison computed > WEO total-GDP ---
df["growth_pc"] = df["wdi_g"].fillna(df["mpd_g"]).fillna(df["weo_g"])
df["growth_source"] = np.where(df["wdi_g"].notna(), "wdi",
                      np.where(df["mpd_g"].notna(), "maddison",
                      np.where(df["weo_g"].notna(), "weo_total", None)))

# --- seam flag: level source at t differs from source at t-1 ---
df = df.sort_values(["iso3", "year"])
prev = df.groupby("iso3")["gdppc_source"].shift(1)
df["seam"] = df["gdppc_source"].notna() & prev.notna() & (df["gdppc_source"] != prev)

# --- inflation: WDI > WEO ---
df["inflation"] = df["wdi_cpi"].fillna(df["weo_cpi"])
df["infl_source"] = np.where(df["wdi_cpi"].notna(), "wdi",
                    np.where(df["weo_cpi"].notna(), "weo", None))

out = df[["iso3", "year", "gdppc", "gdppc_source", "growth_pc", "growth_source",
          "seam", "inflation", "infl_source"]]
out.to_csv(OUT, index=False)

# --- coverage report ---
print(f"rows: {len(out)}")
for col, src in [("gdppc", "gdppc_source"), ("growth_pc", "growth_source"),
                 ("inflation", "infl_source")]:
    n = out[col].notna().sum()
    print(f"\n{col}: {n}/{len(out)} cells ({100*n/len(out):.1f}%)")
    print(out[src].value_counts(dropna=False).to_string())
print(f"\nseam cells: {out['seam'].sum()}")
print("\ncountries with zero gdppc coverage:")
none = out.groupby("iso3")["gdppc"].apply(lambda s: s.notna().sum())
print(none[none == 0].index.tolist() or "  (none)")
print("\nleast-covered countries (gdppc cells):")
print(none.sort_values().head(8).to_string())
