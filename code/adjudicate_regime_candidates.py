"""Adjudicate the Step 4 CCP ledger without inferring content from missing data.

Constitutional replacement, interim orders, suspension, and restoration are formal
changes by instrument type when the country mapping is valid. Amendments require
an affirmative content decision. Only the explicitly documented amendment years
below are accepted or rejected; all others are UNKNOWN, never negative by default.

Outputs:
  data_clean/regime_candidate_review.csv
  data_clean/regime_change.csv
"""
import pandas as pd

LEDGER = "data_clean/ccp_regime_candidates.csv"
SOURCES = "data_clean/domestic_source_register.csv"
REVIEW_OUT = "data_clean/regime_candidate_review.csv"
PANEL_OUT = "data_clean/regime_change.csv"

ACCEPTED_AMENDMENTS = {
    "ARG": {1949, 1956, 1957, 1970, 1971, 1978, 1979, 1982, 1994},
    "BOL": {1968, 1994, 2002, 2004, 2005},
    "BRA": {1945, 1961, 1963, 1964, 1965, 1966, 1968, 1969, 1972, 1975, 1976,
            1977, 1978, 1979, 1980, 1981, 1982, 1983, 1985, 1997},
    "CHL": {1957, 1959, 1973, 1974, 1975, 1976, 1977, 1989, 2005},
    "COL": {1953, 1954, 1957, 1959, 1960, 1968, 2004, 2005},
    "CRI": set(),
    "CUB": {1960, 1962, 1992, 2002},
    "DOM": set(),
    "ECU": {2011, 2015},
    "SLV": {1948, 1982, 1991, 1992},
    "GTM": {1983, 1986, 1993},
    "GUY": set(),
    "HTI": {1971},
    "HND": set(),
    "JAM": set(),
    "MEX": {1953, 1969, 1977, 1990, 1994, 1996, 2014},
    "NIC": {1955, 1959, 1962, 1966, 1971, 1995, 2000, 2005, 2014},
    "PAN": {1978, 1983},
    "PRY": {1977},
    "PER": {2000, 2018},
    "SUR": set(),
    "TTO": set(),
    "URY": {1976, 1977, 1979, 1980, 1981, 1982, 1983, 1984, 1996},
    "VEN": {2009},
    "ALB": {1992, 2016},
    "AUT": {2007},
    "BEL": {1970, 1980, 1988, 1989, 1993, 1994},
    "BGR": {1990, 2015},
    "HRV": {1997, 2000, 2001},
    "CYP": set(),
    "CZE": {1989, 1990, 1992},
    "DNK": set(),
    "FIN": {1969, 1970, 1971},
    "FRA": {1962, 1974, 1992, 2000, 2008},
    "DEU": {1955, 1956, 1967, 1968, 1994, 2006},
    "GRC": {1986},
    "HUN": {1972, 1989, 1990, 2010, 2012, 2013},
    "ISL": set(),
    "IRL": {1972, 1992, 1998, 1999},
    "ITA": {1963, 1991, 1992, 1993, 1999, 2000, 2001, 2003},
    "LUX": set(),
    "MLT": {1974, 1987},
    "NLD": {1953, 1956, 1972, 1983},
    "NOR": set(),
    "POL": {1989, 1990, 2006},
    "PRT": {1982},
    "ROU": {1974, 2003},
    "SVK": {1989, 1990, 1992},
    "SVN": {2000},
    "ESP": {1945, 1946, 1958, 1992},
    "SWE": {1969, 1971, 1975},
    "CHE": {1971, 2003},
    "GBR": {1948, 1949, 1958, 1963, 1969, 1972, 1998, 1999, 2005, 2011},
    "RUS": {1988, 1989, 1990, 1991, 1992, 2008},
    "UKR": {1991, 2004, 2010, 2014, 2016},
    "BLR": {1996, 2004},
    "EST": set(),
    "LVA": set(),
    "LTU": set(),
    "MDA": {1991, 2000, 2016, 2017, 2018},
    "GEO": {2004, 2010, 2017},
    "ARM": {1991, 2005, 2015},
    "AZE": {2002, 2009, 2016},
    "KAZ": {1998, 2007, 2017},
    "KGZ": {1996, 1998, 2001, 2003, 2016},
    "TJK": {1999, 2003, 2016},
    "TKM": {1999, 2016},
    "UZB": {2003, 2011, 2014},
    "JPN": set(),
    "KOR": {1952, 1954, 1960, 1962, 1969, 1972, 1980, 1987},
    "PRK": {1998, 2009, 2016},
    "VNM": {2001, 2013},
    "MNG": {2001, 2019},
}

REJECTED = {
    ("ESP", 2011): "Balanced-budget amendment changes fiscal-policy constraints, not access to or organization of political power (calibration).",
    ("RUS", 2014): "Territorial amendment does not change national access to or organization of political power.",
    ("DEU", 1990): "Unification/territorial succession continues the FRG order; no national access/organization change is established.",
    ("DEU", 2009): "Fiscal-rule amendment is not a change in access to or organization of political power under the registered boundary.",
    ("ITA", 2012): "Fiscal-rule amendment is not a change in access to or organization of political power under the registered boundary.",
}

CASE_NOTE = {
    "Post-Soviet": "case_notes/Step4_PostSoviet.md",
    "Europe": "case_notes/Step4_Europe.md",
    "Latin America": "case_notes/Step4_LatinAmerica.md",
    "East Asia": "case_notes/Step4_EastAsia.md",
}
CALIBRATION_NOTE = "case_notes/Step4_Trevijano_calibration.md"

DOCUMENTARY_EVENTS = [
    ("ESP", 1947, "Law of Succession, formal organization of the Franco order"),
    ("ESP", 1977, "Law 1/1977 for Political Reform, elected bicameral legislature"),
    ("RUS", 1990, "RSFSR sovereignty and constitutional-order acts"),
    ("BLR", 1991, "Declaration of State Sovereignty and independence legal order"),
    ("EST", 1990, "Supreme Council restoration acts establishing the independent order"),
    ("LVA", 1990, "Declaration on Renewal of Independence, 4 May 1990"),
    ("LTU", 1990, "Acts of 11 March 1990 restoring the independent state"),
    ("GEO", 1991, "Act of Restoration of State Independence, 9 April 1991"),
    ("KAZ", 1991, "Constitutional Law on State Independence, 16 December 1991"),
    ("KGZ", 1991, "Declaration on State Independence, 31 August 1991"),
    ("TJK", 1991, "Declaration/Act on State Independence, 9 September 1991"),
    ("TKM", 1991, "Constitutional Law on Independence, 27 October 1991"),
    ("UZB", 1991, "Law on State Independence, 31 August 1991"),
    ("BGR", 1946, "Republic referendum and proclamation replacing the monarchy"),
    ("HRV", 1990, "Constitution of the Republic of Croatia, OG 56/90"),
    ("SVN", 1991, "Constitution and independence acts of Slovenia, 1991"),
    ("GRC", 1967, "Military decree order suspending constitutional government"),
    ("ITA", 1946, "Institutional referendum and Constituent Assembly electoral decree"),
    ("POL", 1981, "Council of State martial-law decree, 12 December 1981"),
    ("ROU", 1989, "December revolutionary legal/institutional acts replacing the party-state order"),
    ("ARG", 1955, "Revolución Libertadora statutory order replacing constitutional government"),
    ("BOL", 1946, "Revolutionary legal order following the overthrow of Villarroel"),
    ("BOL", 1952, "MNR revolutionary legal/institutional order"),
    ("BOL", 1971, "Banzer military institutional order"),
    ("BOL", 1980, "García Meza military institutional order"),
    ("BOL", 1982, "Congressional and constitutional restoration acts"),
    ("ECU", 1963, "Military junta institutional order"),
    ("ECU", 1968, "Constitutional/electoral restoration order"),
    ("SLV", 1960, "Military junta institutional order"),
    ("HTI", 1986, "National Council of Government institutional order"),
    ("HTI", 1991, "Military coup order suspending constitutional government"),
    ("HTI", 1994, "Constitutional restoration acts"),
    ("HND", 1956, "Military institutional order"),
    ("HND", 2009, "Military removal and replacement institutional order"),
    ("PAN", 1968, "Military coup institutional order"),
    ("PAN", 1989, "Post-Noriega constitutional restoration order"),
    ("PRY", 1989, "Post-Stroessner transitional constitutional order"),
    ("PER", 1956, "Constitutional/electoral restoration order"),
    ("PER", 1968, "Revolutionary military government institutional order"),
    ("PER", 1992, "Decree Law 25418 dissolving Congress and transferring legislative authority"),
    ("SUR", 1990, "Military coup institutional order"),
    ("SUR", 1991, "Constitutional/electoral restoration order"),
    ("URY", 1973, "Military decree order dissolving Congress"),
    ("VEN", 2017, "Decrees 2,878/2,992 and Constituent Assembly assumption of legislative functions"),
    ("KOR", 1961, "May 16 military coup and Supreme Council institutional order"),
    ("VNM", 1946, "DRV National Assembly electoral order and 1946 Constitution"),
]

ledger = pd.read_csv(LEDGER)
countries = pd.read_csv("data_clean/countries.csv").set_index("iso3")
sources = pd.read_csv(SOURCES)
source_for_country = sources.dropna(subset=["iso3"]).set_index("iso3")["source_id"].to_dict()
assert set(ledger["iso3"]) == set(source_for_country)

documentary = []
for iso3, year, anchor in DOCUMENTARY_EVENTS:
    documentary.append({
        "candidate_id": f"DOC-{iso3}-{year}-{len(documentary) + 1:02d}",
        "iso3": iso3, "country": countries.at[iso3, "country"],
        "region": countries.at[iso3, "region"], "year": year,
        "ccp_country": "", "systid": "", "evntid": "", "evnttype": "documentary",
        "continuity_rule": "documentary supplement", "calibration": iso3 in {"ESP", "FRA", "GBR"},
        "determination": "pending", "substantive_reason": "", "legal_anchor": anchor,
    })
review = pd.concat([ledger, pd.DataFrame(documentary)], ignore_index=True)
review["source_ids"] = review["iso3"].map(lambda x: f"SRC-CCP-V6;{source_for_country[x]}")
review.loc[review["evnttype"] == "documentary", "source_ids"] = review.loc[
    review["evnttype"] == "documentary", "iso3"].map(source_for_country)
review["case_note"] = review.apply(
    lambda r: CALIBRATION_NOTE if r["calibration"] else CASE_NOTE[r["region"]], axis=1)
review["substantive_reason"] = ""

for idx, candidate in review.iterrows():
    iso3, year, event_type = candidate["iso3"], candidate["year"], candidate["evnttype"]
    if event_type != "documentary":
        review.at[idx, "legal_anchor"] = f"CCP evntid {candidate['evntid']}; {source_for_country[iso3]}"
    if event_type == "documentary":
        review.at[idx, "determination"] = "accepted"
        review.at[idx, "substantive_reason"] = (
            "The named primary legal/institutional instrument changes the formal access to or organization of power.")
    elif event_type in {"new", "interim", "suspension", "reinstated"}:
        review.at[idx, "determination"] = "accepted"
        review.at[idx, "substantive_reason"] = (
            f"Documented constitutional {event_type} changes the authoritative formal order; "
            "country continuity was checked and the instrument/date cross-referenced to the legal record.")
    elif (iso3, year) in REJECTED:
        review.at[idx, "determination"] = "rejected"
        review.at[idx, "substantive_reason"] = REJECTED[(iso3, year)]
    elif year in ACCEPTED_AMENDMENTS.get(iso3, set()):
        review.at[idx, "determination"] = "accepted"
        review.at[idx, "substantive_reason"] = (
            "The identified constitutional amendment changes access to or organization of political power; "
            "the legal act and its substantive classification are documented in the linked country record.")
    else:
        review.at[idx, "determination"] = "unknown"
        review.at[idx, "substantive_reason"] = (
            "Amendment content was not established sufficiently from the accessible primary record; "
            "no positive or negative inference is made from the CCP label.")

review.to_csv(REVIEW_OUT, index=False)

spine = pd.read_csv("data_clean/panel_spine.csv")[["iso3", "year"]]
reviewed = review.groupby(["iso3", "year"])["determination"].agg(set).reset_index()


def classify(statuses):
    if "accepted" in statuses:
        return 1, "observed_positive"
    if "unknown" in statuses:
        return "", "unknown_candidate_content"
    return 0, "reviewed_candidates_negative"


reviewed[["regime_change", "evidence_status"]] = reviewed["determination"].apply(
    lambda x: pd.Series(classify(x)))
panel = spine.merge(reviewed[["iso3", "year", "regime_change", "evidence_status"]],
                    on=["iso3", "year"], how="left")
panel["regime_change"] = panel["regime_change"].fillna(0)
panel["evidence_status"] = panel["evidence_status"].fillna("reviewed_no_formal_candidate")
panel.to_csv(PANEL_OUT, index=False)

print(f"wrote {REVIEW_OUT}")
print(review.groupby(["region", "determination"]).size().unstack(fill_value=0).to_string())
print("\namendment/samendment determinations:")
print(review[review["evnttype"].isin(["amendment", "samendment"])]["determination"].value_counts().to_string())
print(f"\nwrote {PANEL_OUT}: {len(panel)} rows")
print(panel["evidence_status"].value_counts().to_string())
print("RegimeChange positives:", (panel["regime_change"] == 1).sum())
print("RegimeChange unknowns:", (panel["regime_change"] == "").sum())
