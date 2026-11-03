"""Build UN ideal-point distances to patrons (Bailey, Strezhnev & Voeten 2017;
Coding_Protocol §6 validation layer). Source: UN_IdealPoints_Jul2025.csv.

Uses idealpointfp (foreign-policy votes) — the series used in the calibration
episodes. Distance = |idealpoint_country - idealpoint_patron| per year.
Patrons by COW code (USSR/Russia share 365; iso3c label changes but the code
is continuous): USA=2, USSR/RUS=365, CHN=710.

Output: data_clean/idealpoint_distances.csv
  iso3, year, patron, ip_country, ip_patron, distance
"""
import pandas as pd

OUT = "data_clean/idealpoint_distances.csv"
PATRONS = {2: "USA", 365: "USSR/RUS", 710: "CHN"}

ip = pd.read_csv("data_raw/UN_IdealPoints_Jul2025.csv",
                 usecols=["ccode", "iso3c", "year", "idealpointfp"])
ip = ip.dropna(subset=["idealpointfp"])
ip["year"] = ip["year"].astype(int)

iso = set(pd.read_csv("data_clean/countries.csv")["iso3"])
me = ip[ip["iso3c"].isin(iso)][["iso3c", "year", "idealpointfp"]].rename(
    columns={"iso3c": "iso3", "idealpointfp": "ip_country"})
pat = ip[ip["ccode"].isin(PATRONS)].copy()
pat["patron"] = pat["ccode"].map(PATRONS)
pat = pat[["patron", "year", "idealpointfp"]].rename(columns={"idealpointfp": "ip_patron"})

out = me.merge(pat, on="year").dropna()
out["distance"] = (out["ip_country"] - out["ip_patron"]).abs()
out = out[["iso3", "year", "patron", "ip_country", "ip_patron", "distance"]]
out = out.sort_values(["iso3", "patron", "year"])
out.to_csv(OUT, index=False)
print(f"wrote {OUT}: {len(out)} dyad-years, {out['iso3'].nunique()} countries")

# calibration spot checks (from PHASE3_LOG case notes):
def show(iso3, patron, years):
    s = out[(out.iso3 == iso3) & (out.patron == patron) & (out.year.isin(years))]
    print(f"  {iso3}-{patron}:", s[["year", "distance"]].round(2).values.tolist())

print("\nE001 YUG n/a (not panel); E005 CUB-USSR (expect ~0 pre-1989, then gap held by Cuba):")
show("CUB", "USSR/RUS", [1985, 1989, 1990, 1991, 1992])
print("E016 VEN-USA (expect monotone divergence -0.18 1995 -> -1.71 2019 in ip terms):")
show("VEN", "USA", [1995, 2000, 2005, 2010, 2015, 2019])
print("E010-12 Baltics-USA (expect Western alignment from 1991):")
show("EST", "USA", [1991, 1995, 2000, 2004])
