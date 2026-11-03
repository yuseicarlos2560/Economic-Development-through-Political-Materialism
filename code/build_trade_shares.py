"""Build patron trade-share series from IMF DOTS bulk file (Coding_Protocol §6 F2,
§6.2 candidate screen). Source: data_raw/IMF_DOT.csv (1.6 GB SDMX, streamed).

For each panel country (reporter) x patron (counterpart), per year:
  trade = exports of goods FOB (IMF_DOT_TXG_FOB_USD)
        + imports of goods CIF (IMF_DOT_TMG_CIF_USD)
  share = trade with patron / trade with World (counterpart code 1)

Patrons (IMF counterpart codes, per CP §6.2 patron set):
  USA=111 (1948-), USSR=974 (1948-91) / Russia=922 (1992-) -> combined 'USSR/RUS'
  China=924 (screen uses it from 2013 per CP §6.2; full series kept)
Context for the Western sphere (NOT separate patrons): UK=112, France=132,
Germany=134. EU accession signals come from the F3 bloc-date table instead.

Known limitations (honest, logged in PHASE3_LOG):
  - DOTS does NOT see CMEA-bloc trade (non-convertible currencies): USSR share
    for Soviet-sphere members pre-1991 is absent or near-zero even where
    dependence is historically documented (Cuba: USA 0.64-0.73 in 1948-57
    confirms E003's '~2/3 pre-1959', then a reporter gap 1958-80; the 1980s
    Soviet share is missing, not zero). F2 for USSR-sphere membership/severance
    pre-1991 must use historical estimates per CP §6 — DOTS carries USA/CHN/RUS.
  - Reporter coverage is thin before 1960; missing cells stay missing, never
    imputed. Mirror asymmetries exist (PRK 1996 RUS spike).
  - E016 used export share; this file uses total goods trade share (X+M).
    Same break pattern (VEN-USA 45.7% 2000 -> 32.7% 2017 -> 12.6% 2019).

Output: data_clean/trade_shares.csv (iso3, year, patron, trade_usd, world_usd, share)
"""
import pandas as pd

OUT = "data_clean/trade_shares.csv"

COUNTERPARTS = {  # IMF code -> patron label
    "IMF_CNT_COUNTRY_1": "WORLD",
    "IMF_CNT_COUNTRY_111": "USA",
    "IMF_CNT_COUNTRY_974": "USSR/RUS",
    "IMF_CNT_COUNTRY_922": "USSR/RUS",
    "IMF_CNT_COUNTRY_924": "CHN",
    "IMF_CNT_COUNTRY_112": "GBR*",
    "IMF_CNT_COUNTRY_132": "FRA*",
    "IMF_CNT_COUNTRY_134": "DEU*",
}
INDICATORS = {"IMF_DOT_TXG_FOB_USD": "x", "IMF_DOT_TMG_CIF_USD": "m"}
USE = ["REF_AREA", "INDICATOR", "COMP_BREAKDOWN_1", "TIME_PERIOD", "OBS_VALUE"]

iso = set(pd.read_csv("data_clean/countries.csv")["iso3"])

rows = []
unmatched_refs = set()
for ch in pd.read_csv("data_raw/IMF_DOT.csv", usecols=USE, dtype=str, chunksize=400000):
    ch = ch[ch["COMP_BREAKDOWN_1"].isin(COUNTERPARTS) & ch["INDICATOR"].isin(INDICATORS)]
    if ch.empty:
        continue
    unmatched_refs.update(set(ch["REF_AREA"]) - iso)
    ch = ch[ch["REF_AREA"].isin(iso)]
    if ch.empty:
        continue
    ch["patron"] = ch["COMP_BREAKDOWN_1"].map(COUNTERPARTS)
    ch["flow"] = ch["INDICATOR"].map(INDICATORS)
    ch["val"] = pd.to_numeric(ch["OBS_VALUE"], errors="coerce")
    rows.append(ch[["REF_AREA", "TIME_PERIOD", "patron", "flow", "val"]])

d = pd.concat(rows, ignore_index=True)
d.columns = ["iso3", "year", "patron", "flow", "val"]
d["year"] = d["year"].astype(int)
d = d[d["val"].notna() & (d["val"] > 0)]

# exports + imports per reporter-year-patron
d = d.groupby(["iso3", "year", "patron"], as_index=False)["val"].sum()

world = d[d["patron"] == "WORLD"][["iso3", "year", "val"]].rename(columns={"val": "world_usd"})
out = d[d["patron"] != "WORLD"].merge(world, on=["iso3", "year"], how="left")
out = out.rename(columns={"val": "trade_usd"})
out["share"] = out["trade_usd"] / out["world_usd"]
out = out.sort_values(["iso3", "patron", "year"])
out.to_csv(OUT, index=False)

print(f"wrote {OUT}: {len(out)} rows, {out['iso3'].nunique()} countries, "
      f"years {out['year'].min()}-{out['year'].max()}")
print("patrons:", sorted(out["patron"].unique()))
if unmatched_refs:
    print(f"note: {len(unmatched_refs)} non-panel reporters ignored (sample: {sorted(unmatched_refs)[:8]})")

# --- sanity checks against calibration episodes ---
def check(iso3, patron, years):
    s = out[(out["iso3"] == iso3) & (out["patron"] == patron) & (out["year"].isin(years))]
    return s[["year", "share"]].assign(share=(s["share"] * 100).round(1)).values.tolist()

print("\nE016 VEN-USA (expect ~52.1% 2000, ~36.6% 2017, ~12.0% 2019):", check("VEN", "USA", [2000, 2017, 2019]))
print("E003 CUB-USA (expect collapse to ~0 by 1961):", check("CUB", "USA", [1958, 1959, 1960, 1961, 1962]))
print("E004 CUB-USSR (expect rise from 1960):", check("CUB", "USSR/RUS", [1959, 1960, 1961, 1962, 1985]))
print("E002 ESP-USA (fills pending cell):", check("ESP", "USA", [1952, 1953, 1954, 1955]))
