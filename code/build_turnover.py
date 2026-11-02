"""Build the turnover variable from Archigos 4.1 (Coding_Protocol §2).

Turnover = 1 in the year a new effective leader's spell begins (a replacement),
0 otherwise. A country's FIRST spell in the record is an initial condition, not
a replacement (post-Soviet first leaders, founding leaders), so it is not coded
as turnover.

irregular_exit = 1 in the year the outgoing leader left by an irregular manner
(Archigos exit in {Irregular, Foreign}); natural death, ill health, and regular
exits are not irregular. Suicide is rare (3 cases); none in our sample's window.

Code mapping (Archigos uses Gleditsch-Ward alpha codes, NOT ISO3). Documented
collisions found during construction (see docs/PHASE3_LOG.md):
  KOR(our South Korea) -> ROK   [Archigos KOR = historical Korea 1907-10]
  VNM -> DRV                    [Archigos VNM has no post-1900 spells]
  MNG -> MON                    [Archigos MNG has no post-1900 spells]
  SLV(our El Salvador) -> SAL   [Archigos SLV = Slovenia!]
  SVN -> SLV, SVK -> SLO, DEU -> GFR [GDR not in sample], CZE -> CZE+CZR
  [Archigos CZE = Czechoslovakia 1918-92, CZR = Czechia 1993-]
  SRB not in sample; GDR/DDR not in sample; AUS(GW)=Austria (our AUT)

Special case: Switzerland (CHE). Archigos records the annually rotating Swiss
president, so turnover would be 1 every year — meaningless for a collective
executive (Federal Council). CHE is coded 0 and flagged for qualitative
treatment in the case notes.

Post-2015 (Archigos ends 2015): hand-coded entries live in
data_clean/turnover_post2015_checklist.csv with verified=False until checked
against constitutional records. Output: data_clean/turnover.csv
"""
import pandas as pd

OUT = "data_clean/turnover.csv"

CODE_MAP = {  # our iso3 -> Archigos idacr code(s)
    "KOR": ["ROK"], "VNM": ["DRV"], "MNG": ["MON"],
    "SLV": ["SAL"], "SVN": ["SLV"], "SVK": ["SLO"],
    "DEU": ["GFR"], "CZE": ["CZE", "CZR"],
    "AUT": ["AUS"], "BGR": ["BUL"], "CHE": ["SWZ"], "CRI": ["COS"],
    "DNK": ["DEN"], "ESP": ["SPN"], "FRA": ["FRN"], "GBR": ["UKG"],
    "GEO": ["GRG"], "GTM": ["GUA"], "HND": ["HON"], "HRV": ["CRO"],
    "HTI": ["HAI"], "IRL": ["IRE"], "ISL": ["ICE"], "KAZ": ["KZK"],
    "KGZ": ["KYR"], "LTU": ["LIT"], "LVA": ["LAT"], "MDA": ["MLD"],
    "NLD": ["NTH"], "PRT": ["POR"], "PRY": ["PAR"], "ROU": ["RUM"],
    "SWE": ["SWD"], "TJK": ["TAJ"], "TTO": ["TRI"], "URY": ["URU"],
}
IRREGULAR = {"Irregular", "Foreign"}

spine = pd.read_csv("data_clean/panel_spine.csv")[["iso3", "year"]]
countries = pd.read_csv("data_clean/countries.csv")
a = pd.read_csv("data_raw/archigos_4_1.csv", low_memory=False)

rows = []
unmapped = []
for _, crow in countries.iterrows():
    iso3 = crow["iso3"]
    codes = CODE_MAP.get(iso3, [iso3])
    spells = a[a["idacr"].isin(codes)].copy()
    if spells.empty:
        unmapped.append(iso3)
        continue
    spells["start"] = pd.to_datetime(spells["startdate"], errors="coerce")
    spells = spells.sort_values("start")
    first_start = spells["start"].min()
    prev_exit = None
    for _, s in spells.iterrows():
        if pd.isna(s["start"]):
            continue
        y = s["start"].year
        exit_manner = prev_exit  # manner of the OUTGOING leader (the event's manner)
        prev_exit = s["exit"]
        if not (1945 <= y <= 2015):
            continue
        if s["start"] == first_start:
            continue  # initial condition, not a replacement
        rows.append(dict(iso3=iso3, year=y, leader_in=s["leader"],
                         exit_manner=exit_manner, source="archigos"))

ev = pd.DataFrame(rows)
turn = spine.merge(
    ev.groupby(["iso3", "year"]).agg(
        leader_in=("leader_in", lambda x: "; ".join(x)),
        irregular_exit=("exit_manner", lambda x: int(any(e in IRREGULAR for e in x))),
        source=("source", "first")).reset_index(),
    on=["iso3", "year"], how="left")
turn["turnover"] = turn["leader_in"].notna().astype(int)
turn["irregular_exit"] = turn["irregular_exit"].fillna(0).astype(int)

# Switzerland: rotating presidency is not a leader replacement (see docstring)
che = turn["iso3"] == "CHE"
turn.loc[che, ["turnover", "irregular_exit"]] = 0
turn.loc[che & turn["leader_in"].notna(), "source"] = "excluded_collective_executive"

# post-2015 hand-coded (unverified until checked; see checklist file)
post = pd.read_csv("data_clean/turnover_post2015_checklist.csv")
post = post[post["turnover"] == 1]
for _, p in post.iterrows():
    m = (turn["iso3"] == p["iso3"]) & (turn["year"] == p["year"])
    turn.loc[m, ["turnover", "leader_in", "irregular_exit", "source"]] = \
        [1, p["leader_in"], p.get("irregular_exit", 0), "hand_unverified"]

turn.to_csv(OUT, index=False)

n_ev = turn["turnover"].sum()
print(f"turnover events coded: {n_ev} across {turn.loc[turn['turnover']==1, 'iso3'].nunique()} countries")
print(f"irregular exits: {turn.loc[turn['turnover']==1, 'irregular_exit'].sum()}")
print(f"by source: {turn.loc[turn['turnover']==1, 'source'].value_counts().to_dict()}")
print(f"unmapped countries: {unmapped or 'none'}")
zero = [c for c in countries["iso3"] if turn[(turn['iso3']==c)]['turnover'].sum() == 0]
print(f"countries with zero turnover 1945-2019 (verify!): {zero}")
