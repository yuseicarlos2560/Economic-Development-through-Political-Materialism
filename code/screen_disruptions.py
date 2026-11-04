"""Screen for disruption episodes per docs/thresholds.md.

Rules (any one qualifies):
  D1  real GDP pc contracts >= 15% peak-to-trough within <= 5 years
      (levels compared within a single source only, per Coding_Protocol 7.1c)
  D2  growth >= 3 pp below the prior 5-year average, sustained >= 3 years
  D3  annual inflation >= 500%
  D4  documented sudden stop -- qualitative, coded in Phase 3 from case
      literature; cannot be computed from macro series

Overlapping flagged years for the same country are unioned into the panel
indicator; for the episode table, an episode ends after 3+ consecutive clean
years (split rule, decided 2026-10-30 after Venezuela chained 1978-2019).
Outputs: data_clean/disruption_episodes.csv and disruption_years_preliminary.csv.
The latter is explicitly preliminary, preserves the exact union of flagged
country-years, including clean gaps inside segmented episodes, and is marked
analysis_status=preliminary for preliminary Step 5 panel assembly.
"""
import pandas as pd
import numpy as np

OUT = "data_clean/disruption_episodes.csv"
MAX_DD = 5          # peak-to-trough window, years
DD_THRESH = -15.0   # percent
DECEL_PP = 3.0      # pp below prior 5-yr average
DECEL_MIN_YRS = 3
HYPER = 500.0       # annual inflation, %

df = pd.read_csv("data_clean/outcomes.csv")
episodes = []

for iso3, c in df.groupby("iso3"):
    c = c.sort_values("year").reset_index(drop=True)

    # --- D1: drawdowns, within-source levels only ---
    d1_windows = []
    for t in range(len(c)):
        row = c.loc[t]
        if pd.isna(row["gdppc"]):
            continue
        for p in range(max(0, t - MAX_DD), t):
            peak = c.loc[p]
            if peak["gdppc_source"] != row["gdppc_source"]:
                continue
            window = c.loc[p:t]
            if window["gdppc"].isna().any() or (window["gdppc_source"] != peak["gdppc_source"]).any():
                continue
            dd = (row["gdppc"] / peak["gdppc"] - 1) * 100
            if dd <= DD_THRESH:
                d1_windows.append((int(peak["year"]), int(row["year"]), dd))
    if d1_windows:
        # one entry per qualifying window; segmentation below does the merging
        for ps, pe, dd in d1_windows:
            episodes.append(dict(iso3=iso3, type="disruption", rules="D1",
                                 start_year=ps, end_year=pe,
                                 depth_pct=round(dd, 1), qualifier=""))

    # --- D2: sustained deceleration ---
    g = c.set_index("year")["growth_pc"]
    flags = []
    for y, gy in g.items():
        if pd.isna(gy):
            continue
        prior = g.loc[y - 5:y - 1].dropna()
        if len(prior) < 5:
            continue
        if gy <= prior.mean() - DECEL_PP:
            flags.append(y)
    # runs of >= DECEL_MIN_YRS consecutive flagged years
    run = []
    for y in flags:
        if run and y == run[-1] + 1:
            run.append(y)
        else:
            if len(run) >= DECEL_MIN_YRS:
                episodes.append(dict(iso3=iso3, type="disruption", rules="D2",
                                     start_year=run[0], end_year=run[-1],
                                     depth_pct=np.nan, qualifier=""))
            run = [y]
    if len(run) >= DECEL_MIN_YRS:
        episodes.append(dict(iso3=iso3, type="disruption", rules="D2",
                             start_year=run[0], end_year=run[-1],
                             depth_pct=np.nan, qualifier=""))

    # --- D3: hyperinflation ---
    h = c[c["inflation"] >= HYPER]
    for _, r in h.iterrows():
        episodes.append(dict(iso3=iso3, type="disruption", rules="D3",
                             start_year=int(r["year"]), end_year=int(r["year"]),
                             depth_pct=np.nan,
                             qualifier=f"inflation {r['inflation']:.0f}%"))

# --- segment flagged years into episodes: an episode ends after 3+ consecutive
# clean years (gap > 2). The panel indicator is the union of all flagged years
# and is unaffected by segmentation (panel merging per Protocol 7).
ep = pd.DataFrame(episodes)
merged = []
annual = []
for iso3, grp in ep.groupby("iso3"):
    flagged = set()
    for _, e in grp.iterrows():
        flagged.update(range(e["start_year"], e["end_year"] + 1))
    years = sorted(flagged)
    for y in years:
        hit_year = grp[(grp["start_year"] <= y) & (grp["end_year"] >= y)]
        rules = "+".join(sorted({r for rs in hit_year["rules"] for r in rs.split("+")}))
        annual.append(dict(iso3=iso3, year=y, disruption=1, rules=rules))
    segments, cur = [], [years[0]]
    for y in years[1:]:
        if y <= cur[-1] + 2:
            cur.append(y)
        else:
            segments.append(cur); cur = [y]
    segments.append(cur)
    for seg in segments:
        s, e = seg[0], seg[-1]
        hit = grp[(grp["start_year"] <= e) & (grp["end_year"] >= s)]
        rules = "+".join(sorted({r for rs in hit["rules"] for r in rs.split("+")}))
        depths = hit["depth_pct"].dropna()
        quals = "; ".join(q for q in hit["qualifier"] if q)
        merged.append(dict(iso3=iso3, type="disruption", rules=rules,
                           start_year=s, end_year=e,
                           depth_pct=round(depths.min(), 1) if len(depths) else np.nan,
                           qualifier=quals))

out = pd.DataFrame(merged).sort_values(["iso3", "start_year"]).reset_index(drop=True)
out.insert(0, "episode_id", [f"D{i+1:03d}" for i in range(len(out))])
out["D4_sudden_stop"] = False  # qualitative rule, coded in Phase 3
out.to_csv(OUT, index=False)

annual_out = pd.DataFrame(annual)
annual_out["episode_id"] = ""
for idx, row in annual_out.iterrows():
    hit = out[(out["iso3"] == row["iso3"]) &
              (out["start_year"] <= row["year"]) & (out["end_year"] >= row["year"])]
    assert len(hit) == 1, f"Annual disruption does not map to one episode: {row.to_dict()}"
    annual_out.at[idx, "episode_id"] = hit.iloc[0]["episode_id"]
spine = pd.read_csv("data_clean/panel_spine.csv")[["iso3", "year"]]
annual_out = spine.merge(annual_out, on=["iso3", "year"], how="left", validate="one_to_one")
annual_out["disruption"] = annual_out["disruption"].fillna(0).astype(int)
annual_out.insert(0, "analysis_status", "preliminary")
annual_out.to_csv("data_clean/disruption_years_preliminary.csv", index=False)

print(f"{len(out)} merged disruption episodes across {out['iso3'].nunique()} countries\n")

# --- calibration anchors (thresholds.md) ---
cal = [("GRC", 2007, 2013, "IN"), ("ESP", 2007, 2013, "borderline/below"),
       ("GBR", 2016, 2019, "borderline/below"), ("MEX", 1994, 1995, "OUT (short crisis)"),
       ("VNM", 1989, 1991, "OUT (below threshold)")]
for iso, a, b, expect in cal:
    hit = out[(out["iso3"] == iso) & (out["start_year"] <= b) & (out["end_year"] >= a - 2)]
    status = hit[["episode_id", "start_year", "end_year", "rules", "depth_pct"]].to_string(index=False) if len(hit) else "no episode"
    print(f"{iso} {a}-{b} (expected {expect}):\n{status}\n")
