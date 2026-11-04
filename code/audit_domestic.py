"""Audit Step 4 domestic-event candidates, episodes, and country-year outputs.

FAIL means an internal inconsistency. Pending CCP content adjudications are
reported as incomplete work, not converted into negative formal determinations.
"""
from pathlib import Path
import csv
import re
import sys

FAILS = []


def check(name, condition, detail=""):
    print(f"[{'PASS' if condition else 'FAIL'}] {name}" + (f" -- {detail}" if detail else ""))
    if not condition:
        FAILS.append(name)


def read_csv(path):
    return list(csv.DictReader(open(path)))


countries = read_csv("data_clean/countries.csv")
panel_iso = {r["iso3"] for r in countries}
spine = read_csv("data_clean/panel_spine.csv")
ledger = read_csv("data_clean/ccp_regime_candidates.csv")
episodes = read_csv("data_clean/domestic_episodes.csv")

check("A1 panel spine", len(spine) == 5475 and len(panel_iso) == 73, f"{len(spine)} rows/73 countries")
check("A2 CCP ledger row count", len(ledger) == 1414, f"{len(ledger)}")
check("A3 CCP ledger country coverage", {r["iso3"] for r in ledger} == panel_iso)
check("A4 CCP IDs unique", len({r["candidate_id"] for r in ledger}) == len(ledger))
check("A5 CCP event vocabulary",
      {r["evnttype"] for r in ledger} <= {"new", "interim", "suspension", "reinstated", "amendment", "samendment"})
check("A6 CCP years", all(1945 <= int(r["year"]) <= 2019 for r in ledger))
print("A7 raw-ledger status is superseded by the final candidate review in section E")

ids = [r["episode_id"] for r in episodes]
check("B1 episode IDs unique", len(ids) == len(set(ids)), f"{len(ids)} episodes")
check("B2 episode country vocabulary", {r["iso3"] for r in episodes} <= panel_iso)
check("B3 category/status vocabulary",
      {r["category"] for r in episodes} == {"power_structure", "apparatus_restructuring"}
      and {r["status"] for r in episodes} <= {"accepted", "conditional"})
bad_intervals = [r["episode_id"] for r in episodes if not (
    int(r["start_year"]) <= int(r["event_year"]) <= int(r["end_year"])
    and 1945 <= int(r["event_year"]) <= 2019 and int(r["end_year"]) <= 2019)]
check("B4 intervals and principal years", not bad_intervals, str(bad_intervals))
check("B5 every power episode has >=2 dimensions", all(
    len(r["dimensions_or_components"].split("+")) >= 2
    for r in episodes if r["category"] == "power_structure"))
check("B6 every apparatus episode has >=2 components", all(
    len(r["dimensions_or_components"].split("+")) >= 2
    for r in episodes if r["category"] == "apparatus_restructuring"))
check("B7 episode notes exist", all(Path(r["case_note"]).is_file() for r in episodes))

note_files = ["case_notes/Step4_PostSoviet.md", "case_notes/Step4_Europe.md",
              "case_notes/Step4_LatinAmerica.md", "case_notes/Step4_EastAsia.md"]
note_text = "\n".join(Path(p).read_text() for p in note_files)
uncovered = sorted(iso for iso in panel_iso if not re.search(rf"\b{iso}\b", note_text))
check("B8 all 73 panel countries covered in substantive notes", not uncovered, str(uncovered))

outputs = {}
for variable, path in [("power_structure", "data_clean/power_structure.csv"),
                       ("apparatus_restructuring", "data_clean/apparatus_restructuring.csv"),
                       ("regime_change", "data_clean/regime_change.csv")]:
    rows = read_csv(path)
    outputs[variable] = rows
    check(f"C1 {variable} full spine", len(rows) == 5475)
    check(f"C2 {variable} unique country-years",
          len({(r["iso3"], r["year"]) for r in rows}) == 5475)
    check(f"C3 {variable} binary or missing", {r[variable] for r in rows} <= {"0", "1", ""})
    if variable == "regime_change":
        continue
    accepted = [r for r in episodes if r["category"] == variable and r["status"] == "accepted"]
    conditional = [r for r in episodes if r["category"] == variable and r["status"] == "conditional"]
    expected = {(r["iso3"], r["event_year"]) for r in accepted}
    expected_unknown = {(r["iso3"], r["event_year"]) for r in conditional}
    observed = {(r["iso3"], r["year"]) for r in rows if r[variable] == "1"}
    observed_unknown = {(r["iso3"], r["year"]) for r in rows if r[variable] == ""}
    check(f"C4 {variable} matches accepted episode years", observed == expected,
          f"missing={sorted(expected - observed)}; extra={sorted(observed - expected)}")
    check(f"C5 {variable} preserves conditional episodes as missing", observed_unknown == expected_unknown,
          f"expected={sorted(expected_unknown)}; observed={sorted(observed_unknown)}")

review = read_csv("data_clean/regime_candidate_review.csv")
source_register = read_csv("data_clean/domestic_source_register.csv")
known_sources = {r["source_id"] for r in source_register}
check("E1 every CCP and documentary candidate has a final disposition",
      len(review) > len(ledger) and {r["determination"] for r in review} <= {"accepted", "rejected", "unknown"},
      f"{len(review)} reviewed; {len(review) - len(ledger)} documentary supplements")
check("E2 every candidate has a reason and legal/source reference", all(
    r["substantive_reason"].strip() and r["legal_anchor"].strip() and r["source_ids"].strip() for r in review))
check("E3 all candidate source IDs resolve", all(
    set(r["source_ids"].split(";")) <= known_sources for r in review))
accepted_formal = {(r["iso3"], r["year"]) for r in review if r["determination"] == "accepted"}
unknown_formal = {(r["iso3"], r["year"]) for r in review
                  if r["determination"] == "unknown"} - accepted_formal
observed_formal = {(r["iso3"], r["year"]) for r in outputs["regime_change"] if r["regime_change"] == "1"}
observed_formal_unknown = {(r["iso3"], r["year"]) for r in outputs["regime_change"] if r["regime_change"] == ""}
check("E4 RegimeChange positives match accepted formal candidates", observed_formal == accepted_formal)
check("E5 RegimeChange missingness matches unresolved content", observed_formal_unknown == unknown_formal)


def value(variable, iso3, year):
    return next(r[variable] for r in outputs[variable] if r["iso3"] == iso3 and r["year"] == str(year))


for variable, iso3, year in [
    ("power_structure", "ESP", 1977), ("power_structure", "GBR", 1950),
    ("power_structure", "FRA", 1958), ("power_structure", "FRA", 2009),
    ("apparatus_restructuring", "ESP", 1977), ("apparatus_restructuring", "GBR", 2007),
    ("apparatus_restructuring", "FRA", 1959),
    ("power_structure", "VEN", 2003), ("power_structure", "VEN", 2009),
    ("power_structure", "VEN", 2017), ("regime_change", "VEN", 1999),
    ("regime_change", "ESP", 1977), ("regime_change", "ESP", 1978),
    ("regime_change", "FRA", 2008), ("regime_change", "HRV", 1990),
    ("regime_change", "SVN", 1991),
]:
    check(f"D1 calibration/crux {iso3} {year} {variable}=1", value(variable, iso3, year) == "1")
check("D2 conditional France 1988 is missing, not positive or negative", value("power_structure", "FRA", 1988) == "")
check("D3 conditional Guyana 1980 apparatus is missing, not positive or negative",
      value("apparatus_restructuring", "GUY", 1980) == "")
check("D4 Venezuela 1999 formal-only is not a power event", value("power_structure", "VEN", 1999) == "0")
check("D5 explicit formal rejection Spain 2011", value("regime_change", "ESP", 2011) == "0")

print()
print(f"FAILS: {len(FAILS)}")
print("Unknown formal-amendment content and conditional substantive episodes are retained as missing, never recoded as zero.")
sys.exit(1 if FAILS else 0)
