"""Phase C audit for Step 3 (realignment coding).

Checks, in four blocks:
  A. episodes.csv internal integrity (IDs, vocabularies, intervals, fields)
  B. per-country chain logic (entry/severance ordering, overlaps)
  C. cross-file consistency (episode_sources.csv, screen-candidate resolution,
     panel coverage with documented determinations)
  D. case-note presence

Exit 0 with all PASS, exit 1 if any FAIL. Warnings are reported, not failed.
"""
import csv
import os
import re
import sys

DC = "data_clean"
CN = "case_notes"
FAILS = []
WARNS = []


def check(name, ok, detail=""):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}" + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILS.append(f"{name}: {detail}")


def warn(name, detail):
    print(f"[warn] {name} -- {detail}")
    WARNS.append(f"{name}: {detail}")


eps = list(csv.DictReader(open(f"{DC}/episodes.csv")))
panel = {r["iso3"]: r for r in csv.DictReader(open(f"{DC}/countries.csv"))}

# ---------- A. internal integrity ----------
ids = [e["episode_id"] for e in eps]
expect = [f"E{i:03d}" for i in range(1, 74)]
check("A1 IDs contiguous E001-E073, unique", ids == expect,
      f"n={len(ids)}, first bad: {next((a for a, b in zip(ids, expect) if a != b), 'none')}")

types = {e["type"] for e in eps}
check("A2 type vocabulary", types <= {"entry", "severance", "severance_threat"}, str(types))

bad_years = []
for e in eps:
    try:
        s, t = int(e["start_year"]), int(e["end_year"])
        if not (1945 <= s <= t <= 2019):
            bad_years.append(e["episode_id"])
    except ValueError:
        bad_years.append(e["episode_id"])
check("A3 years int, 1945<=start<=end<=2019", not bad_years, str(bad_years))

mism = []
for e in eps:
    m = re.match(r"^(\d{4})(?:-(\d{4}))?", e["interval_coded"])
    if not m:
        mism.append((e["episode_id"], e["interval_coded"]))
        continue
    s2 = int(m.group(1))
    t2 = int(m.group(2)) if m.group(2) else s2
    if s2 != int(e["start_year"]) or t2 != int(e["end_year"]):
        mism.append((e["episode_id"], e["interval_coded"],
                     f"cols {e['start_year']}-{e['end_year']}"))
check("A3b interval_coded matches start/end columns", not mism, str(mism))

CALIB_ONLY = {"YUG", "EGY"}
not_panel = sorted({e["iso3"] for e in eps if e["iso3"] not in panel})
check("A4 iso3 in panel or calibration-only set", set(not_panel) <= CALIB_ONLY, str(not_panel))

req = ["patron", "families_affected", "voluntariness", "source1", "coder", "confidence"]
empty = [(e["episode_id"], c) for e in eps for c in req if not (e[c] or "").strip()]
check("A5 required fields non-empty", not empty, str(empty))

PATRON_SIDE = {"USA": "WEST", "USA/EU": "WEST", "EU/eurozone (sub-sphere)": "WEST",
               "USSR": "EAST", "USSR/RUS": "EAST"}
bad_patron = [e["episode_id"] for e in eps if e["patron"] not in PATRON_SIDE]
check("A6 patron vocabulary (CP section 6.2 set; China = pre-activation, none expected)",
      not bad_patron, str(bad_patron))

bad_fam = []
for e in eps:
    if e["type"] == "severance_threat":
        if "none terminated" not in e["families_affected"]:
            bad_fam.append((e["episode_id"], "threat without zero-termination record"))
        continue
    fams = set(re.findall(r"F[1-4]", e["families_affected"].split("(")[0]))
    if len(fams) < 2:
        bad_fam.append((e["episode_id"], e["families_affected"]))
check("A7 families: >=2 for consummated; zero-termination record on threats (R2)",
      not bad_fam, str(bad_fam))

bad_vol = []
for e in eps:
    base = e["voluntariness"].split("(")[0].strip()
    if base not in {"imposed", "chosen", "n/a"}:
        bad_vol.append((e["episode_id"], e["voluntariness"]))
    if e["type"] == "severance_threat" and base != "n/a":
        bad_vol.append((e["episode_id"], "threat without n/a"))
    if e["type"] != "severance_threat" and base == "n/a":
        bad_vol.append((e["episode_id"], "n/a on consummated episode"))
check("A8 voluntariness vocabulary; n/a exactly on threats", not bad_vol, str(bad_vol))

bad_conf = [e["episode_id"] for e in eps
            if e["confidence"].split("(")[0].strip() not in {"high", "medium-high", "medium"}]
check("A9 confidence vocabulary", not bad_conf, str(bad_conf))

bad_r6 = [e["episode_id"] for e in eps if e["systemic_shift_flag"] not in {"0", "1"}]
check("A10 systemic_shift_flag in {0,1}", not bad_r6, str(bad_r6))
r6 = sorted((e["episode_id"], e["iso3"], e["start_year"]) for e in eps if e["systemic_shift_flag"] == "1")
warn("A10 R6=1 episodes (expect 1989-91 window class)", str(r6))

# ---------- B. chain logic ----------
def side(e):
    return PATRON_SIDE[e["patron"]]

by_cs = {}
for e in eps:
    by_cs.setdefault((e["iso3"], side(e)), []).append(e)
first_sev = []
chain_bad = []
overlap_bad = []
for (iso3, sd), evs in sorted(by_cs.items()):
    evs.sort(key=lambda e: int(e["start_year"]))
    prev_membership = None  # None unknown / True member / False not member
    for i, e in enumerate(evs):
        if e["type"] == "entry":
            if prev_membership is True:
                chain_bad.append((e["episode_id"], "entry while already member"))
            prev_membership = True
        else:  # severance or severance_threat
            if prev_membership is None:
                first_sev.append((e["episode_id"], iso3, sd))
            elif prev_membership is False:
                chain_bad.append((e["episode_id"], "severance without membership"))
        if e["type"] == "severance":
            prev_membership = False
    for a, b in zip(evs, evs[1:]):
        if int(b["start_year"]) <= int(a["end_year"]):
            overlap_bad.append((a["episode_id"], b["episode_id"], iso3, sd))
check("B1/B2 chain ordering (entry<->severance per country+patron-side)",
      not chain_bad, str(chain_bad))
check("B4 no same-side interval overlaps", not overlap_bad, str(overlap_bad))
warn("B1 first-event severances needing documented initial condition (manual confirm)",
     str(first_sev))

cross = []
by_c = {}
for e in eps:
    by_c.setdefault(e["iso3"], []).append(e)
for iso3, evs in by_c.items():
    evs.sort(key=lambda e: int(e["start_year"]))
    for a, b in zip(evs, evs[1:]):
        if side(a) != side(b) and int(b["start_year"]) <= int(a["end_year"]):
            cross.append((a["episode_id"], b["episode_id"]))
warn("cross-patron transition overlaps (expected class)", str(cross))

# ---------- C. cross-file ----------
src = list(csv.DictReader(open(f"{DC}/episode_sources.csv")))
check("C1 episode_sources.csv rows and IDs", [r["episode_id"] for r in src] == expect,
      f"n={len(src)}")
bad_grade = [r["episode_id"] for r in src if r["quality_grade"] not in {"A", "B", "C"}]
check("C1b grades in {A,B,C}", not bad_grade, str(bad_grade))
empty_anch = [r["episode_id"] for r in src if not r["anchors_change"].strip()]
check("C1c anchors_change non-empty for all episodes", not empty_anch, str(empty_anch))

cands = list(csv.DictReader(open(f"{DC}/realignment_candidates.csv")))
REGION_NOTES = {
    "Post-Soviet": ["PostSoviet_batch_note.md"],
    "Europe": ["EURO_batch_note.md", "EURO_formation_Soviet.md", "EURO_formation_Western.md",
               "PostSocialist_severance_1989.md", "PostSocialist_entry_Western.md"],
    "Latin America": ["LATAM_batch_note.md", "LATAM_formation_initial_condition.md",
                      "Caribbean_entries.md"],
    "East Asia": ["EA_batch_note.md", "EA_formation_entries.md"],
}
note_text = {}
for rg, files in REGION_NOTES.items():
    txt = ""
    for fn in files:
        p = os.path.join(CN, fn)
        if os.path.exists(p):
            txt += open(p).read()
    note_text[rg] = txt
calib_txt = "".join(open(os.path.join(CN, fn)).read() for fn in os.listdir(CN)
                    if fn.endswith(".md"))
unresolved = []
for c in cands:
    cs, ce = int(c["window_start"]), int(c["window_end"])
    hit = any(e["iso3"] == c["iso3"] and int(e["start_year"]) <= ce and int(e["end_year"]) >= cs
              for e in eps)
    if hit:
        continue
    if re.search(rf"\b{c['iso3']}\b", note_text.get(c["region"], "")):
        continue
    if c.get("calibration_overlap", "").strip().lower() in {"1", "true", "yes"}:
        continue
    unresolved.append((c["iso3"], c["patron"], c["window_start"], c["window_end"], c["region"]))
check("C2 every screen candidate resolved (episode, batch note, or calibration overlap)",
      not unresolved, f"{len(unresolved)} unresolved: {unresolved[:20]}")

with_eps = {e["iso3"] for e in eps}
no_eps = sorted(set(panel) - with_eps)
undoc = [iso3 for iso3 in no_eps if not re.search(rf"\b{iso3}\b", calib_txt)]
check("C3 every no-episode panel country has a documented determination",
      not undoc, str(undoc))
print(f"       coverage: {len(with_eps & set(panel))} countries with episodes, "
      f"{len(no_eps)} with documented no-realignment, 2 calibration-only (EGY, YUG)")

# ---------- D. case notes ----------
low_txt = calib_txt.lower()
no_note = [e["episode_id"] for e in eps
           if not (re.search(rf"\b{e['iso3']}\b", calib_txt)
                   or re.search(rf"\b{re.escape(e['country'].lower())}\b", low_txt))]
check("D1 every episode country appears in case_notes (iso3 or name)", not no_note, str(no_note))

print()
print(f"FAILS: {len(FAILS)}  WARNINGS: {len(WARNS)}")
sys.exit(1 if FAILS else 0)
