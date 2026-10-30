"""Screen for acceleration episodes per docs/thresholds.md (all four must hold,
following Hausmann, Pritchett & Rodrik 2005):

  A1  real GDP pc growth >= 3.5% per year (8-year window average)
  A2  sustained >= 8 years
  A3  >= 2 pp above the prior growth regime (mean of the prior 8 years)
  A4  post-acceleration output pc above the pre-acceleration maximum
      (levels compared within a single source only, per Coding_Protocol 7.1c)

Candidate 8-year windows passing A1/A3/A4 are merged into episodes (overlapping
windows extend the episode, so duration can exceed 8 years).
Output: data_clean/acceleration_episodes.csv
"""
import pandas as pd
import numpy as np

OUT = "data_clean/acceleration_episodes.csv"
MIN_G = 3.5     # % per year
W = 8           # window length, years
REGIME_PP = 2.0 # pp above prior regime

df = pd.read_csv("data_clean/outcomes.csv")
episodes = []

for iso3, c in df.groupby("iso3"):
    c = c.sort_values("year").reset_index(drop=True)
    g = c.set_index("year")["growth_pc"]
    lvl = c.set_index("year")["gdppc"]
    src = c.set_index("year")["gdppc_source"]
    years = list(g.index)

    windows = []
    for s in years:
        win_years = [y for y in range(s, s + W)]
        prior_years = [y for y in range(s - W, s)]
        win = g.reindex(win_years)
        prior = g.reindex(prior_years)
        if win.isna().any() or prior.isna().any():
            continue
        if win.mean() < MIN_G:                      # A1+A2
            continue
        if win.mean() < prior.mean() + REGIME_PP:   # A3
            continue
        # A4: within-source level check
        end_year = s + W - 1
        post_lvl = lvl.reindex([end_year]).iloc[0]
        pre_lvls = lvl.reindex(prior_years)
        if pd.isna(post_lvl) or pre_lvls.isna().any():
            continue
        if src.reindex([end_year]).iloc[0] != src.reindex(prior_years).iloc[0]:
            continue
        if post_lvl <= pre_lvls.max():              # A4 fails
            continue
        windows.append((s, end_year, win.mean()))

    # merge overlapping windows into episodes
    for s, e, m in windows:
        if episodes and episodes[-1]["iso3"] == iso3 and s <= episodes[-1]["end_year"]:
            episodes[-1]["end_year"] = max(episodes[-1]["end_year"], e)
        else:
            episodes.append(dict(iso3=iso3, type="acceleration", rules="A1-A4",
                                 start_year=s, end_year=e, avg_growth=round(m, 2)))

out = pd.DataFrame(episodes)
if len(out):
    out = out.sort_values(["iso3", "start_year"]).reset_index(drop=True)
    out.insert(0, "episode_id", [f"A{i+1:03d}" for i in range(len(out))])
    out.to_csv(OUT, index=False)
    print(f"{len(out)} acceleration episodes across {out['iso3'].nunique()} countries\n")
    print(out.to_string(index=False))
    print("\ncalibration anchors:")
    for iso, expect in [("KOR", "long acceleration from ~1960s"), ("VNM", "acceleration from ~1990"),
                        ("CHL", "acceleration post-1985"), ("PRK", "none")]:
        hit = out[out["iso3"] == iso]
        print(f"{iso} (expected {expect}):")
        print(hit[["episode_id", "start_year", "end_year", "avg_growth"]].to_string(index=False) if len(hit) else "  no episode")
else:
    print("no acceleration episodes found")
