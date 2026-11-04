"""Build Step 4 power-structure and apparatus event tables from reviewed notes.

The Markdown case notes are the human-auditable source. This builder extracts only
structured table rows, preserves process intervals and evidence, and excludes
conditional episodes from the country-year indicators. It does not construct
RegimeChange: CCP formal-candidate adjudication is tracked separately.

Outputs:
  data_clean/domestic_episodes.csv
  data_clean/power_structure.csv
  data_clean/apparatus_restructuring.csv
"""
from pathlib import Path
import re
import pandas as pd

Y0, Y1 = 1945, 2019
NOTE_FILES = [
    "case_notes/Step4_PostSoviet.md",
    "case_notes/Step4_Europe.md",
    "case_notes/Step4_LatinAmerica.md",
    "case_notes/Step4_EastAsia.md",
]


def parse_date(text):
    event_match = re.search(r"\*\*(\d{4})\*\*", text)
    if not event_match:
        raise ValueError(f"No bold principal year: {text}")
    event_year = int(event_match.group(1))
    years = [int(y) for y in re.findall(r"(?<!\d)(\d{4})(?!\d)", text)]
    start_year = years[0]
    end_year = years[1] if len(years) > 1 else start_year
    return start_year, end_year, event_year


def components(text):
    found = []
    for component in ["coercive", "administrative", "judicial", "fiscal"]:
        if re.search(component, text, re.I):
            found.append(component)
    return "+".join(found)


def dimensions(text):
    found = []
    for dim in re.findall(r"\(([abcd])\)", text):
        if dim not in found:
            found.append(dim)
    return "+".join(found)


def row(category, episode_id, iso3, dates, evidence, confidence, note):
    start, end, event = parse_date(dates)
    status = "conditional" if "conditional" in confidence.lower() else "accepted"
    if category == "power_structure":
        detail = dimensions(evidence)
    else:
        detail = components(evidence)
        if iso3 == "GUY" and event == 1980:
            status = "conditional"
    return {
        "episode_id": episode_id,
        "iso3": iso3,
        "category": category,
        "start_year": start,
        "end_year": end,
        "event_year": event,
        "dimensions_or_components": detail,
        "status": status,
        "confidence": confidence,
        "evidence": evidence,
        "case_note": note,
        "coder": "assistant",
    }


rows = []
for note in NOTE_FILES:
    current_country = None
    in_latam_apparatus = False
    for line in Path(note).read_text().splitlines():
        if note.endswith("Step4_LatinAmerica.md"):
            if line.startswith("## 3. Apparatus"):
                in_latam_apparatus = True
                continue
            if line.startswith("## 4."):
                in_latam_apparatus = False
        if line.startswith("### ") and not line.startswith("####"):
            current_country = line[4:].strip()
        if not line.startswith("|") or "---" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if re.fullmatch(r"(?:PS|AR)-[A-Z]{3}-\d{2}", first):
            category = "power_structure" if first.startswith("PS-") else "apparatus_restructuring"
            iso3 = first.split("-")[1]
            if len(cells) == 6 and category == "apparatus_restructuring":
                _, _, dates, coercive, fiscal, confidence = cells
                evidence = f"Coercive: {coercive}. Fiscal: {fiscal}"
            elif len(cells) == 5:
                _, _, dates, evidence, confidence = cells
            elif len(cells) == 4:
                _, dates, evidence, confidence = cells
            else:
                raise ValueError(f"Unexpected episode row in {note}: {line}")
            rows.append(row(category, first, iso3, dates, evidence, confidence, note))
        elif in_latam_apparatus and len(cells) == 4 and re.search(r"\*\*\d{4}\*\*", cells[1]):
            iso3 = first
            if not re.fullmatch(r"[A-Z]{3}", iso3):
                continue
            for segment in cells[1].split(";"):
                if not re.search(r"\*\*\d{4}\*\*", segment):
                    continue
                event = int(re.search(r"\*\*(\d{4})\*\*", segment).group(1))
                sequence = 1 + sum(r["iso3"] == iso3 and r["category"] == "apparatus_restructuring" for r in rows)
                episode_id = f"AR-{iso3}-{sequence:02d}"
                interval = re.search(r"(\d{4})[–-](\d{2,4})", segment)
                if interval:
                    start = int(interval.group(1))
                    end = int(interval.group(2))
                    if end < 100:
                        end += (start // 100) * 100
                    date_text = f"{start}–{end}; **{event}**"
                else:
                    date_text = f"**{event}**"
                rows.append(row("apparatus_restructuring", episode_id, iso3, date_text,
                                cells[2], cells[3], note))

events = pd.DataFrame(rows).sort_values(["category", "iso3", "event_year", "episode_id"])
for idx, event in events[events["dimensions_or_components"] == ""].iterrows():
    reference = re.search(r"\b(?:PS|AR)-[A-Z]{3}-\d{2}\b", event["evidence"])
    if not reference:
        continue
    referenced = events[events["episode_id"] == reference.group(0)]
    assert len(referenced) == 1, f"Unresolved shared record in {event['episode_id']}"
    events.at[idx, "dimensions_or_components"] = referenced.iloc[0]["dimensions_or_components"]
assert not events["episode_id"].duplicated().any()
assert events["event_year"].between(Y0, Y1).all()
assert (events["start_year"] <= events["event_year"]).all()
assert (events["event_year"] <= events["end_year"]).all()
ps = events[events["category"] == "power_structure"]
ar = events[events["category"] == "apparatus_restructuring"]
bad_ps = ps[ps["dimensions_or_components"].str.count(r"\+").add(1).lt(2)]
bad_ar = ar[ar["dimensions_or_components"].str.count(r"\+").add(1).lt(2)]
assert bad_ps.empty, f"Power rows below two dimensions: {bad_ps[['episode_id', 'evidence']].to_dict('records')}"
assert bad_ar.empty, f"Apparatus rows below two components: {bad_ar[['episode_id', 'evidence']].to_dict('records')}"
events.to_csv("data_clean/domestic_episodes.csv", index=False)

spine = pd.read_csv("data_clean/panel_spine.csv")[["iso3", "year"]]
for category, variable, output in [
    ("power_structure", "power_structure", "data_clean/power_structure.csv"),
    ("apparatus_restructuring", "apparatus_restructuring", "data_clean/apparatus_restructuring.csv"),
]:
    accepted = events[(events["category"] == category) & (events["status"] == "accepted")]
    grouped = accepted.groupby(["iso3", "event_year"])["episode_id"].agg(";".join).reset_index()
    panel = spine.merge(grouped, left_on=["iso3", "year"], right_on=["iso3", "event_year"], how="left")
    panel[variable] = panel["episode_id"].notna().astype(int).astype(object)
    panel["evidence_status"] = panel["episode_id"].notna().map({True: "observed_positive", False: "reviewed_no_event"})
    conditional = events[(events["category"] == category) & (events["status"] == "conditional")]
    for _, episode in conditional.iterrows():
        mask = (panel["iso3"] == episode["iso3"]) & (panel["year"] == episode["event_year"])
        panel.loc[mask, variable] = ""
        panel.loc[mask, "evidence_status"] = "unknown_episode_evidence"
    panel = panel[["iso3", "year", variable, "evidence_status", "episode_id"]]
    panel.to_csv(output, index=False)
    print(f"{variable}: {(panel[variable] == 1).sum()} events, {panel.loc[panel[variable] == 1, 'iso3'].nunique()} countries; "
          f"{(panel[variable] == '').sum()} unknown")

print(f"wrote data_clean/domestic_episodes.csv: {len(events)} episodes")
print(events.groupby(["category", "status"]).size().to_string())
