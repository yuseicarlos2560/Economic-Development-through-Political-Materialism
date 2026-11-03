"""Build F1 alliance signals with patrons from ATOP 5.1 (Coding_Protocol §6 F1,
§6.2 screen). Sources: data_raw/ATOP/.../atop5_1m.csv (member spells);
COW alliance_v4.1_by_dyad_yearly.csv (<=2012 cross-check, per CP §6).

Patrons (COW codes, CP §6.2): USA=2, USSR/Russia=365, China=710.
COW<->ISO3 mapping from UN_IdealPoints_Jul2025.csv (most recent year per iso3).

Predecessor fan-out (screen convenience, year-bounded; succession questions go
to the four judgments, not decided here):
  Czechoslovakia 315 -> CZE, SVK (spells clipped at 1992)
  Yugoslavia     345 -> HRV, SVN (spells clipped at 1991)
  GDR            265 -> DEU      (spells clipped at 1990)
USSR->Russia needs no mapping (COW 365 continuous). Post-Soviet republics do
NOT inherit USSR memberships: they were incorporation, not alliance (E010-E012).

Output: data_clean/alliance_signals.csv
  iso3, patron, atopid, yrent, yrexit (0=ongoing per ATOP), defense, offense,
  neutral, nonagg, consul, termmode, source_note
"""
import pandas as pd

OUT = "data_clean/alliance_signals.csv"
PATRONS = {2: "USA", 365: "USSR/RUS", 710: "CHN"}
PREDECESSORS = {315: (["CZE", "SVK"], 1992), 345: (["HRV", "SVN"], 1991), 265: (["DEU"], 1990)}

ip = pd.read_csv("data_raw/UN_IdealPoints_Jul2025.csv", usecols=["ccode", "iso3c", "year"])
iso = set(pd.read_csv("data_clean/countries.csv")["iso3"])
cow2iso = (ip[ip["iso3c"].isin(iso)].sort_values("year")
           .groupby("iso3c").last()["ccode"].astype(int)
           .reset_index().set_index("ccode")["iso3c"].to_dict())

m = pd.read_csv("data_raw/ATOP/ATOP 5.1 (.csv)/atop5_1m.csv", low_memory=False)
# treaty size + strongest obligation: omnibus multilateral consultative acts
# (>30 members, no defense/offense anywhere, e.g. the 1975 CSCE act) are NOT
# patron security ties; the screen drops them via these columns
tsize = m.groupby("atopid")["member"].transform("size")
m["treatysize"] = tsize
tdef = m.groupby("atopid")[["defense", "offense"]].transform("max")
m["treaty_defense"] = tdef["defense"]
m["treaty_offense"] = tdef["offense"]
patron_treaties = {p: set(m.loc[m["member"] == c, "atopid"]) for c, p in PATRONS.items()}

rows = []
for _, s in m.iterrows():
    mem = s["member"]
    iso3 = cow2iso.get(mem)
    targets = [(iso3, None)] if iso3 else []
    if mem in PREDECESSORS:
        succ, clip = PREDECESSORS[mem]
        targets += [(x, clip) for x in succ]
    if not targets:
        continue
    for c, p in PATRONS.items():
        if s["atopid"] not in patron_treaties[p] or mem == c:
            continue
        for t_iso, clip in targets:
            if t_iso is None:
                continue
            yrent, yrexit = int(s["yrent"]), int(s["yrexit"])
            if clip is not None:
                if yrent > clip:
                    continue
                if yrexit == 0 or yrexit > clip:
                    yrexit = clip
            rows.append(dict(iso3=t_iso, patron=p, atopid=s["atopid"], yrent=yrent,
                             yrexit=yrexit, defense=int(s["defense"]), offense=int(s["offense"]),
                             neutral=int(s["neutral"]), nonagg=int(s["nonagg"]),
                             consul=int(s["consul"]), termmode=s.get("termmode", ""),
                             treatysize=int(s["treatysize"]),
                             treaty_defense=int(s["treaty_defense"]),
                             treaty_offense=int(s["treaty_offense"]),
                             source_note="predecessor-clipped" if clip is not None else "own"))

out = pd.DataFrame(rows).drop_duplicates().sort_values(["iso3", "patron", "yrent"])
out.to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(out)} spells, {out['iso3'].nunique()} countries")
print("\nspells per patron:", out.groupby("patron").size().to_dict())
print("\nkey checks:")
for iso3, p in [("JPN", "USA"), ("KOR", "USA"), ("ESP", "USA"), ("POL", "USSR/RUS"),
                ("CUB", "USSR/RUS"), ("EGY", "USSR/RUS"), ("MNG", "USSR/RUS"), ("VEN", "USA")]:
    s = out[(out["iso3"] == iso3) & (out["patron"] == p)]
    print(f"  {iso3}-{p}:", s[["atopid", "yrent", "yrexit", "defense"]].values.tolist() if len(s) else "none")

# --- COW cross-check (<=2012): dyad-years with a defense pact with patron ---
cow = pd.read_csv("data_raw/version4.1_csv/alliance_v4.1_by_dyad_yearly.csv", low_memory=False)
cow = cow[["ccode1", "ccode2", "year", "defense", "neutrality", "nonaggression", "entente"]]
pcodes = set(PATRONS)
ours = set(cow2iso)
sel = cow[((cow["ccode1"].isin(pcodes) & cow["ccode2"].isin(ours)) |
           (cow["ccode2"].isin(pcodes) & cow["ccode1"].isin(ours))) & (cow["year"] >= 1945)]
cow_pairs = set()
skipped = set()
for _, r in sel.iterrows():
    p = r["ccode1"] if r["ccode1"] in pcodes else r["ccode2"]
    o = r["ccode2"] if r["ccode1"] in pcodes else r["ccode1"]
    iso_o = cow2iso.get(int(o))
    if iso_o is None:
        skipped.add(int(o))
        continue
    cow_pairs.add((iso_o, PATRONS[int(p)], int(r["year"]), int(r["defense"])))
if skipped:
    print(f"COW dyads skipped, non-panel/historical states: {sorted(skipped)}")
cow_def = {(i, p, y) for i, p, y, d in cow_pairs if d == 1}
cow_any = {(i, p, y) for i, p, y, _ in cow_pairs}

atop_years = set()
for _, r in out.iterrows():
    end = r["yrexit"] if r["yrexit"] > 0 else 2018
    for y in range(max(r["yrent"], 1945), min(end, 2012) + 1):
        atop_years.add((r["iso3"], r["patron"], y))

inter = atop_years & cow_any
print(f"\nCOW cross-check (1945-2012): ATOP dyad-years={len(atop_years)}, "
      f"COW dyad-years={len(cow_any)}, overlap={len(inter)}")
only_atop = sorted({(i, p) for i, p, y in atop_years - cow_any})
only_cow = sorted({(i, p) for i, p, y in cow_any - atop_years})
print("ATOP-only dyads:", only_atop)
print("COW-only dyads:", only_cow)
