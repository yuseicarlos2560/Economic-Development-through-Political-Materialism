"""Candidate-generation screen for the realignment sweep (Coding_Protocol §6.2).
MECHANICAL and OUTCOME-BLIND: uses only F1-F4 indicator data, never outcomes.

Rule (CP §6.2): for each panel country x patron, a candidate window opens where
>=2 indicator families signal change within a 3-year window:
  F1 alliance establishment/termination with patron (alliance_signals.csv; ATOP)
  F2 DOTS trade-share break: |share_t - share_{t-3}| >= 12pp, larger side >= 8pp
     (trade_shares.csv; USSR/RUS excluded pre-1992 — CMEA blindness documented
     in build_trade_shares.py; CHN windows starting <2013 excluded per CP §6.2)
  F3 bloc entry/exit (bloc_membership.csv; ALBA sphere=n/a excluded per §6.2)
  F4 GSDB-R5 sanctions begin_year with sender = patron (sanctions_signals.csv)

Patron harmonization: EU* / USA/EU / US-led regime* -> USA (one Western sphere,
CP §6.2; original labels kept in details). China candidates before 2013 are
dropped (activation date); 2008-2012 sensitivity noted in the log.

Outputs:
  data_clean/realignment_candidates.csv — iso3, patron, window_start, window_end,
    direction, families, n_events, calibration_overlap, details
  data_clean/sphere_roster_screen.csv — iso3, year, patron, basis (F1/F3 active)
Phase B decides every candidate with the four judgments (CP §6.1); rejections
are recorded with reasons.
"""
import pandas as pd

Y0, Y1 = 1945, 2019

countries = pd.read_csv("data_clean/countries.csv")[["iso3", "region"]]
episodes = pd.read_csv("data_clean/episodes.csv")

events = []  # iso3, patron, year, family, direction, detail

# --- F1: alliance spells with patrons ---
# drop omnibus multilateral consultative acts (>30 members, no defense/offense
# obligation anywhere in the treaty — e.g. CSCE 1975): not patron security ties
al = pd.read_csv("data_clean/alliance_signals.csv")
al = al[~((al["treatysize"] > 30) & (al["treaty_defense"] == 0) & (al["treaty_offense"] == 0))]
for _, r in al.iterrows():
    strong = "defense" if (r["defense"] or r["offense"]) else "weak"
    if Y0 <= r["yrent"] <= Y1:
        events.append((r["iso3"], r["patron"], int(r["yrent"]), "F1", "entry",
                       f"ATOP {int(r['atopid'])} enters ({strong})"))
    if 0 < r["yrexit"] <= Y1:
        events.append((r["iso3"], r["patron"], int(r["yrexit"]), "F1", "severance",
                       f"ATOP {int(r['atopid'])} exits ({strong})"))

# --- F3: bloc entry/exit ---
# Security blocs (NATO, WarsawPact, CSTO) are the SAME tie as an ATOP defense
# pact: joining NATO establishes the security guarantee; counting it as F1 AND
# F3 would double-count one act as two families (R2/R3 want two DISTINCT ties:
# security guarantee / subsidized trade-aid / bloc membership). Security blocs
# therefore feed F1 here; F3 carries economic-institutional blocs (CMEA,
# EU/EEA, OAS, EAEU). Screen convention logged in PHASE3_LOG (2026-11-03).
bl = pd.read_csv("data_clean/bloc_membership.csv")
bl = bl[bl["sphere"] != "n/a"]
bl["patron"] = bl["sphere"].replace({"USA/EU": "USA"})
SECURITY_BLOCS = {"NATO", "WarsawPact", "CSTO", "CST"}
bl["family"] = bl["bloc"].isin(SECURITY_BLOCS).map({True: "F1", False: "F3"})
for _, r in bl.iterrows():
    if Y0 <= r["entry"] <= Y1:
        events.append((r["iso3"], r["patron"], int(r["entry"]), r["family"], "entry",
                       f"{r['bloc']} entry"))
    if pd.notna(r["exit"]) and Y0 <= r["exit"] <= Y1:
        events.append((r["iso3"], r["patron"], int(r["exit"]), r["family"], "severance",
                       f"{r['bloc']} exit"))

# --- F4: sanctions with sender = patron ---
sa = pd.read_csv("data_clean/sanctions_signals.csv")
sa["patron"] = sa["sender"].replace({"EU*": "USA", "US-led regime*": "USA"})
for _, r in sa.iterrows():
    if Y0 <= r["begin_year"] <= Y1:
        events.append((r["iso3"], r["patron"], int(r["begin_year"]), "F4", "severance",
                       f"GSDB {int(r['case_id'])} ({r['sender']}, {r['objective']})"))

# --- F2: DOTS trade-share breaks ---
# Western sphere is screened against TWO counterparts (one sphere, CP §6.2):
# the US hegemon (USA) and Germany (DEU*) as the EU-core proxy — EU-accession
# entries move trade with the EU, not necessarily with the US. Screen only;
# the four judgments still inspect the actual documentary trade/aid record.
ts = pd.read_csv("data_clean/trade_shares.csv")
PROXY = {"USA": "USA", "DEU*": "USA", "USSR/RUS": "USSR/RUS", "CHN": "CHN"}
ts = ts[ts["patron"].isin(PROXY)]
ts["pgroup"] = ts["patron"].map(PROXY)
ts = ts[~((ts["pgroup"] == "USSR/RUS") & (ts["year"] < 1992))]  # CMEA blindness
ts = ts[~((ts["iso3"] == "DEU") & (ts["pgroup"] == "USA"))]  # DEU* self-proxy
ts = ts.sort_values(["iso3", "patron", "year"])
ts["share_l3"] = ts.groupby(["iso3", "patron"])["share"].shift(3)
ts["year_l3"] = ts.groupby(["iso3", "patron"])["year"].shift(3)
brk = ts[(ts["year"] - ts["year_l3"] == 3)]
brk = brk[(brk["share"] - brk["share_l3"]).abs() >= 0.12]
brk = brk[brk[["share", "share_l3"]].max(axis=1) >= 0.08]
for _, r in brk.iterrows():
    direction = "severance" if r["share"] < r["share_l3"] else "entry"
    events.append((r["iso3"], r["pgroup"], int(r["year"]), "F2", direction,
                   f"share vs {r['patron']} {r['share_l3']:.2f}->{r['share']:.2f}"))

ev = pd.DataFrame(events, columns=["iso3", "patron", "year", "family", "direction", "detail"])
n_pre = len(ev)
ev_china_pre = ev[(ev["patron"] == "CHN") & (ev["year"] < 2013)]
ev = ev[~((ev["patron"] == "CHN") & (ev["year"] < 2013))]
print(f"events: {n_pre} total; dropped {len(ev_china_pre)} CHN pre-2013 (activation, "
      f"sensitivity 2008-12); {len(ev)} used")

# --- candidate windows: >=2 families within any 3-year span ---
cands = []
for (iso3, patron), g in ev.groupby(["iso3", "patron"]):
    g = g.sort_values("year")
    years = sorted(g["year"].unique())
    hot = []
    for t in range(Y0, Y1 + 1):
        fams = set(g.loc[(g["year"] >= t) & (g["year"] <= t + 2), "family"])
        if len(fams) >= 2:
            hot.append(t)
    if not hot:
        continue
    # merge consecutive starts into one candidate
    start, prev = hot[0], hot[0]
    for t in hot[1:] + [None]:
        if t is None or t > prev + 1:
            w = g[(g["year"] >= start) & (g["year"] <= prev + 2)]
            dirs = w["direction"].value_counts()
            cands.append(dict(
                iso3=iso3, patron=patron,
                window_start=int(w["year"].min()), window_end=int(w["year"].max()),
                direction=dirs.index[0] if len(dirs) == 1 else "mixed(" + "+".join(dirs.index) + ")",
                families="+".join(sorted(w["family"].unique())),
                n_events=len(w),
                details=" | ".join(w.apply(lambda r: f"{r['year']}:{r['family']}:{r['detail']}", axis=1))))
            if t is None:
                break
            start = t
        prev = t

c = pd.DataFrame(cands)

# --- economic-bloc auto-candidates (user decision 2026-11-03: code ALL EU
# accessions meeting R1-R3) ---
# Membership in an economic-institutional bloc (EU/EEA, CMEA, EAEU) legally
# entails the F2-family tie (structural funds/CAP, CMEA transfer trade, EAEU
# funds), so DOTS never shows the break and the >=2-families screen misses
# these by construction. They enter the candidate list on the bloc event alone,
# flagged auto_bloc=True; Phase B documents the aid/trade tie and still applies
# the four judgments (rejection possible).
auto = []
for _, r in bl[bl["bloc"].isin({"EU/EEA", "CMEA", "EAEU"})].iterrows():
    for direction, year in (("entry", r["entry"]), ("severance", r["exit"])):
        if pd.isna(year) or not (Y0 <= year <= Y1):
            continue
        year = int(year)
        hit = c[(c["iso3"] == r["iso3"]) & (c["patron"] == r["patron"]) &
                (c["window_start"] <= year + 2) & (c["window_end"] >= year - 2)]
        if hit.empty:
            auto.append(dict(iso3=r["iso3"], patron=r["patron"], window_start=year,
                             window_end=year, direction=direction,
                             families="F3(+F2 aid constitutive)", n_events=1,
                             details=f"{year}:F3:{r['bloc']} {direction} (auto: "
                                     f"aid/trade tie constitutive of membership)"))
if auto:
    c = pd.concat([c, pd.DataFrame(auto)], ignore_index=True)

# calibration overlap: same country, same patron group, and window within
# +-3 years of an already-coded episode (country-patron alone is too coarse:
# ESP-USA has both E002/1953 and a separate 1986 EU-entry candidate)
PMAP = {"USA": "USA", "USA/EU": "USA", "USSR": "USSR/RUS", "EU/eurozone (sub-sphere)": "USA"}
cal = [(r["iso3"], PMAP.get(r["patron"], r["patron"]), r["start_year"], r["end_year"])
       for _, r in episodes.iterrows()]

def overlaps(row):
    for i, p, s, e in cal:
        if i == row["iso3"] and p == row["patron"] and \
           row["window_start"] <= e + 3 and row["window_end"] >= s - 3:
            return True
    return False

c["calibration_overlap"] = c.apply(overlaps, axis=1)
c = c.merge(countries, on="iso3").sort_values(["region", "iso3", "window_start"])
c.to_csv("data_clean/realignment_candidates.csv", index=False)

# --- R1 screen roster: sphere membership from active F1/F3 ---
roster = []
for _, r in al.iterrows():
    end = r["yrexit"] if r["yrexit"] > 0 else Y1
    for y in range(max(Y0, r["yrent"]), min(Y1, end) + 1):
        roster.append((r["iso3"], y, r["patron"], "F1"))
for _, r in bl.iterrows():
    end = r["exit"] if pd.notna(r["exit"]) else Y1
    for y in range(max(Y0, r["entry"]), min(Y1, int(end)) + 1):
        roster.append((r["iso3"], y, r["patron"], r["family"]))
ro = pd.DataFrame(roster, columns=["iso3", "year", "patron", "src"])
ro = ro.groupby(["iso3", "year", "patron"])["src"].agg(lambda s: "+".join(sorted(set(s)))).reset_index()
ro.columns = ["iso3", "year", "patron", "basis"]
ro.to_csv("data_clean/sphere_roster_screen.csv", index=False)

print(f"\nwrote data_clean/realignment_candidates.csv: {len(c)} candidates")
print(c.groupby(["region", "direction"]).size().unstack(fill_value=0).to_string())
print("\nNEW candidates (no calibration overlap):")
new = c[~c["calibration_overlap"]]
for _, r in new.iterrows():
    print(f"  {r['iso3']} {r['patron']:9s} {r['window_start']}-{r['window_end']} "
          f"{r['direction']:18s} {r['families']:8s} n={r['n_events']}")
print(f"\nwrote data_clean/sphere_roster_screen.csv: {len(ro)} country-year-sphere rows")
