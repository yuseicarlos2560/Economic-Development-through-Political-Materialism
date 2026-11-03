"""Build F4 sanctions signals from GSDB-R5 (Coding_Protocol §6 F4, §6.2 screen).
Source: data_raw/GSDB-R5/GSDB-R5.csv (1,794 cases, 1949-2025).

Sender classification (sender = patron, CP §6.2):
  exact 'United States' / contains 'United States'          -> USA (mult flag if joint)
  exact 'Soviet Union' or 'Russia'                          -> USSR/RUS
  exact 'China'                                             -> CHN
  sender contains 'EU' or 'EEC'                             -> EU* (Western-sphere context,
                                                              eurozone sub-sphere per E017;
                                                              the four judgments decide)
  'CoCom' / 'ChinCom'                                       -> US-led regime* (Cold War
                                                              export-control regimes)
Targets mapped by name to our 73 ISO3; historical states (USSR, Yugoslavia,
Czechoslovakia, GDR, FRY, South Vietnam...) left unmapped and reported — region
batches handle them case by case (e.g. 1990s 'Yugoslavia' sanctions target FRY,
NOT HRV/SVN, so no fan-out is applied here).

Output: data_clean/sanctions_signals.csv
  iso3, sender, case_id, begin_year, end_year (NaN = ongoing), trade, arms,
  military, financial, travel, other, objective, mult
"""
import pandas as pd

OUT = "data_clean/sanctions_signals.csv"

NAME2ISO = {
    "Argentina": "ARG", "Bolivia": "BOL", "Brazil": "BRA", "Chile": "CHL",
    "Colombia": "COL", "Costa Rica": "CRI", "Cuba": "CUB", "Dominican Republic": "DOM",
    "Ecuador": "ECU", "El Salvador": "SLV", "Guatemala": "GTM", "Guyana": "GUY",
    "Haiti": "HTI", "Honduras": "HND", "Jamaica": "JAM", "Mexico": "MEX",
    "Nicaragua": "NIC", "Panama": "PAN", "Paraguay": "PRY", "Peru": "PER",
    "Suriname": "SUR", "Trinidad and Tobago": "TTO", "Uruguay": "URY", "Venezuela": "VEN",
    "Albania": "ALB", "Austria": "AUT", "Belgium": "BEL", "Bulgaria": "BGR",
    "Croatia": "HRV", "Cyprus": "CYP", "Czech Republic": "CZE", "Denmark": "DNK",
    "Finland": "FIN", "France": "FRA", "Germany": "DEU", "Greece": "GRC",
    "Hungary": "HUN", "Iceland": "ISL", "Ireland": "IRL", "Italy": "ITA",
    "Luxembourg": "LUX", "Malta": "MLT", "Netherlands": "NLD", "Norway": "NOR",
    "Poland": "POL", "Portugal": "PRT", "Romania": "ROU", "Slovakia": "SVK",
    "Slovenia": "SVN", "Spain": "ESP", "Sweden": "SWE", "Switzerland": "CHE",
    "United Kingdom": "GBR",
    "Russia": "RUS", "Ukraine": "UKR", "Belarus": "BLR", "Estonia": "EST",
    "Latvia": "LVA", "Lithuania": "LTU", "Moldova": "MDA", "Georgia": "GEO",
    "Armenia": "ARM", "Azerbaijan": "AZE", "Kazakhstan": "KAZ", "Kyrgyzstan": "KGZ",
    "Tajikistan": "TJK", "Turkmenistan": "TKM", "Uzbekistan": "UZB",
    "Japan": "JPN", "Korea, South": "KOR", "Korea, North": "PRK",
    "Vietnam": "VNM", "Mongolia": "MNG",
    "Soviet Union": "RUS",  # state continuity, same convention as COW code 365
}

def classify_sender(s):
    if not isinstance(s, str):
        return None, False
    if s in ("CoCom", "ChinCom"):
        return "US-led regime*", False
    if s == "United States":
        return "USA", False
    if s == "Soviet Union" or s == "Russia":
        return "USSR/RUS", False
    if s == "China":
        return "CHN", False
    if "United States" in s:
        return "USA", True
    if "EU" in s.split(", ") or "EEC" in s.split(", ") or s == "EU":
        return "EU*", False
    return None, False

g = pd.read_csv("data_raw/GSDB-R5/GSDB-R5.csv")

# Multi-target strings ("Estonia, Latvia, Lithuania", "Korea, North, China"):
# exact NAME2ISO match first (protects names containing ", " like "Congo,
# Democratic Republic of the"); otherwise split and keep mapped fragments.
def map_targets(name):
    if name in NAME2ISO:
        return [NAME2ISO[name]]
    return [NAME2ISO[f] for f in str(name).split(", ") if f in NAME2ISO]

g["iso3_list"] = g["sanctioned_state"].apply(map_targets)
g = g.explode("iso3_list").rename(columns={"iso3_list": "iso3"})
send = g["sanctioning_state"].apply(classify_sender)
g["sender"] = [a for a, _ in send]
g["mult"] = [b for _, b in send]

out = g[g["iso3"].notna() & g["sender"].notna()].copy()
out = out.rename(columns={"case_id": "case_id"})
keep = ["iso3", "sender", "case_id", "begin_year", "end_year", "trade", "arms",
        "military", "financial", "travel", "other", "objective", "mult"]
out = out[keep].sort_values(["iso3", "sender", "begin_year"])
out.to_csv(OUT, index=False)

print(f"wrote {OUT}: {len(out)} cases, {out['iso3'].nunique()} target countries")
print("per sender:", out.groupby("sender").size().to_dict())
print("\nkey checks:")
print("  VEN-USA case_ids (expect 802/827/1051/1098):",
      sorted(out[(out.iso3 == "VEN") & (out.sender == "USA")]["case_id"].tolist()))
print("  CUB-USA case_ids (expect 51/59/65/74/443):",
      sorted(out[(out.iso3 == "CUB") & (out.sender == "USA")]["case_id"].tolist()))
print("  GRC-EU* 2014-16 (expect empty per E017):",
      sorted(out[(out.iso3 == "GRC")]["case_id"].tolist()))
print("  YUG-era: LTU USSR/RUS (expect 385 per E010-12):",
      sorted(out[(out.iso3.isin(['EST', 'LVA', 'LTU'])) & (out.sender == 'USSR/RUS')]["case_id"].tolist()))
unmapped = sorted(set(g.loc[g["sender"].notna() & g["iso3"].isna(), "sanctioned_state"]))
print("\npatron-sender cases with unmapped target (historical states, no panel fragment):")
print(" ", unmapped)
