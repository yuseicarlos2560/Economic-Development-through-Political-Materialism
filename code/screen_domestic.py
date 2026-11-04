"""Build the CCP candidate ledger for Step 4 (Coding_Protocol section 4.2).

The ledger is a recall floor for formal regime change, not a regime-change
variable. Every mapped CCP event in 1945-2019 requires a later content decision.
Power-structure and apparatus candidates are supplemented from documentary
records; absence from this ledger is never evidence of continuity.

Output: data_clean/ccp_regime_candidates.csv
"""
import pandas as pd

Y0, Y1 = 1945, 2019
CCP = "data_raw/CCP/ccpcce_v6/ccpcce/ccpcce_v6.csv"
OUT = "data_clean/ccp_regime_candidates.csv"

COUNTRY_MAP = {
    "SUR": ["Surinam"],
    "CZE": ["Czechoslovakia", "Czech Republic"],
    "SVK": ["Czechoslovakia", "Slovakia"],
    "DEU": ["German Federal Republic"],
    "ITA": ["Italy/Sardinia"],
    "RUS": ["Russia (Soviet Union)"],
    "BLR": ["Belarus (Byelorussia)"],
    "KGZ": ["Kyrgyz Republic"],
    "KOR": ["Korea, Republic of"],
    "PRK": ["Korea, People's Republic of"],
    "VNM": ["Vietnam, Democratic Republic of"],
}
CONTINUITY = {
    "CZE": "Czechoslovakia through 1992; Czech Republic from 1993",
    "SVK": "Czechoslovakia through 1992; Slovakia from 1993",
    "DEU": "FRG/unified Germany only; GDR excluded",
    "RUS": "USSR/Russia continuity",
    "VNM": "DRV/unified Vietnam continuity; Republic of Vietnam excluded",
    "KOR": "Republic of Korea from 1948",
    "PRK": "Democratic People's Republic of Korea from 1948",
}
CALIBRATION = {"ESP", "FRA", "GBR"}
EVENT_TYPES = {"new", "interim", "suspension", "reinstated", "amendment", "samendment"}

countries = pd.read_csv("data_clean/countries.csv")
ccp = pd.read_csv(CCP)

rows = []
for _, country in countries.iterrows():
    iso3 = country["iso3"]
    source_names = COUNTRY_MAP.get(iso3, [country["country"]])
    events = ccp[
        ccp["country"].isin(source_names)
        & ccp["year"].between(Y0, Y1)
        & ccp["evnttype"].isin(EVENT_TYPES)
    ]
    if iso3 in {"CZE", "SVK"}:
        events = events[
            ((events["country"] == "Czechoslovakia") & (events["year"] <= 1992))
            | ((events["country"] != "Czechoslovakia") & (events["year"] >= 1993))
        ]
    for _, event in events.sort_values(["year", "evntid"]).iterrows():
        rows.append({
            "candidate_id": f"CCP-{iso3}-{event['year']}-{event['evntid']}",
            "iso3": iso3,
            "country": country["country"],
            "region": country["region"],
            "year": event["year"],
            "ccp_country": event["country"],
            "systid": event["systid"],
            "evntid": event["evntid"],
            "evnttype": event["evnttype"],
            "continuity_rule": CONTINUITY.get(iso3, "panel country record"),
            "calibration": iso3 in CALIBRATION,
            "determination": "calibration_review" if iso3 in CALIBRATION else "pending",
            "substantive_reason": "",
            "legal_anchor": "",
        })

ledger = pd.DataFrame(rows)
assert len(countries) == 73
assert ledger["candidate_id"].is_unique
assert set(ledger["iso3"]) == set(countries["iso3"])
assert not ledger.duplicated(["iso3", "year", "evntid"]).any()
ledger.to_csv(OUT, index=False)

print(f"wrote {OUT}: {len(ledger)} CCP candidates across {ledger['iso3'].nunique()} countries")
print(ledger.groupby(["region", "evnttype"]).size().unstack(fill_value=0).to_string())
print("\ncountry coverage and candidate counts:")
print(ledger.groupby(["region", "iso3"]).size().to_string())
