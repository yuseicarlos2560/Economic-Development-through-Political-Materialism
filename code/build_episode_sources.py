"""Build data_clean/episode_sources.csv and inject the per-episode mapping
table into docs/EPISODE_SOURCES.md between the AUTO markers.

One row per episode in data_clean/episodes.csv. Anchor IDs (M/B/N/U/C/D series)
are defined in docs/EPISODE_SOURCES.md. Grades: A primary-anchored, B dataset+acts
with secondary dating or pending flag, C qualitative by construction.
"""
import csv
import re
import sys

EPISODES = "data_clean/episodes.csv"
OUT_CSV = "data_clean/episode_sources.csv"
REGISTER = "docs/EPISODE_SOURCES.md"

# episode_id -> (prior, change, voluntariness, validation, grade, status, notes)
M = {
"E001": ("B6; D1-3020", "M7 (28 Jun 1948); B6 denunciation Sep 1949 (FLAG 1); C-21",
         "C-21; M7 (coerced: bloc embargo/expulsion)", "D1; D2", "A", "SR; FLAG 1", "Calibration-only (YUG not in panel)"),
"E002": ("none (post-1945 isolation)", "B12 (26 Sep 1953); B32", "B12 (voluntary; executive agreements, not a treaty)",
         "U1 (14 Dec 1955); D1-3480", "A", "SR", "Calibration"),
"E003": ("M2; M3 (member)", "N3; M2 exclusion 31 Jan 1962; C-51/59/65/74", "D2 cases (coerced)",
         "D2; M2; M3", "A", "SR", "Calibration"),
"E004": ("severed US tie (E003)", "B15 (13 Feb 1960)", "qualitative (S)",
         "D4; S", "C", "SR", "Calibration; no treaty-grade instrument (FLAG 7)"),
"E005": ("M5 member; B15-derived tie", "B16 (world prices Jan 1991); M5 dissolution 28 Jun 1991; M12",
         "patron collapse (M12)", "D3", "A", "V-2026-11 (M5)", "Calibration"),
"E006": ("B11 (27 May 1971); D1-3670", "B11 expulsion 18 Jul 1972; B11 abrogation 14 Mar 1976; C-198",
         "mixed: Egyptian initiative; Soviet retaliation C-198", "D2; D3", "A", "V-2026-11", "Calibration"),
"E007": ("severed (E006)", "B19 milestones (1974-1980)", "B19 (voluntary; Sadat initiative)",
         "D3", "B", "SR", "Calibration; interval partly secondary dating"),
"E008": ("M5 (1978); B10; D1-3825", "Soviet aid cuts 1989; M5 dissolution; Cam Ranh withdrawal; B10 lapse 1994",
         "patron collapse", "D3; D1", "A", "V-2026-11 (M5)", "Calibration"),
"E009": ("post-embargo (C-201 ends)", "B30 (3 Feb 1994; 11 Jul 1995; ASEAN 28 Jul 1995)", "voluntary",
         "D3", "B", "SR", "Calibration; confidence medium"),
"E010": ("M12 (incorporation)", "B27 (30 Mar 1990 act); C-385; ruble exit 1992; troops out 31 Aug 1994",
         "C-385 (Soviet pressure resisted)", "U1 (17 Sep 1991); D3", "A", "V-2026-11", "Calibration (Baltics)"),
"E011": ("M12 (incorporation)", "B27 (4 May 1990 act); C-385; ruble exit 1992; troops out 31 Aug 1994",
         "C-385 (Soviet pressure resisted)", "U1 (17 Sep 1991); D3", "A", "V-2026-11", "Calibration (Baltics)"),
"E012": ("M12 (incorporation)", "B27 (11 Mar 1990 act); C-385; ruble exit 1992; troops out 31 Aug 1993",
         "C-385 (Soviet pressure resisted)", "U1 (17 Sep 1991); D3", "A", "V-2026-11", "Calibration (Baltics)"),
"E013": ("severed (E010)", "M8 EA 12 Jun 1995; M1 29 Mar 2004; EU 1 May 2004", "voluntary (referendum 14 Sep 2003)",
         "D3; U1", "A", "SR", ""),
"E014": ("severed (E011)", "M8 EA 12 Jun 1995; M1 29 Mar 2004; EU 1 May 2004", "voluntary (referendum 20 Sep 2003)",
         "D3; U1", "A", "SR", ""),
"E015": ("severed (E012)", "M8 EA 12 Jun 1995; M1 29 Mar 2004; EU 1 May 2004", "voluntary (referendum 10-11 May 2003)",
         "D3; U1", "A", "SR", ""),
"E016": ("M2; M3 (member)", "B29 (Apr 2002); C-802/827; N6 (8 Mar 2015); M3 exit 2015; M2 denunciation 27 Apr 2017",
         "US coercion record (D2); Venezuelan initiative on M2/M3", "D2; D3", "A", "V-2026-11 (OAS dates)", "Calibration"),
"E017": ("M1; M8 (member)", "B28 (capital controls 28 Jun; referendum 5 Jul; MoU 19 Aug 2015)",
         "creditor pressure (institutional, not patron sanctions)", "D2 (no GSDB case); D1 (M1 intact)", "A", "SR",
         "Calibration; severance_threat only"),
"E018": ("M10 (CIS; no CST); B17 (31 May 1997)",
         "C-1031; B17 Kharkiv denounced 2 Apr 2014; N9 (19 May 2018); B17 lapse 31 Mar 2019; DCFTA 1 Jan 2016",
         "C-1031 (coerced by patron)", "D3", "A", "V-2026-11 (N9)", ""),
"E019": ("M10 (CIS 1993; CST 1993-99)", "C-780/781/834; N10 (Aug 2008); M10 effective Aug 2009 (FLAG 4)",
         "C-780/781 (coerced)", "D3", "A", "SR; FLAG 4", ""),
"E020": ("M10 (CIS; CST 24 Sep 1993)", "B34 (no basing; CST non-renewal Apr 1999; GUAM)", "voluntary balancing",
         "D3 FLAGGED", "B", "FLAG 9 (OPEN_ISSUES)", "Pending user ruling"),
"E021": ("M12 (union republic)", "B33 (Jan 1992); U2 (12 Dec 1995); never CST/CSTO", "voluntary neutrality",
         "D3", "A", "SR; interval end medium", ""),
"E022": ("occupied/liberated; no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E023": ("occupied/liberated; no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E024": ("no patron (post-Liberation)", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E025": ("no patron (victor)", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E026": ("occupied/liberated; no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E027": ("no patron (post-1943 armistice)", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E028": ("occupied/liberated; no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E029": ("occupied/liberated; no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E030": ("no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E031": ("no patron", "M1 (4 Apr 1949); M9; N1", "voluntary", "D1", "A", "SR", ""),
"E032": ("British sphere (1944-47)", "N2 (12 Mar / 22 May 1947); M1 accession 18 Feb 1952", "voluntary (government request)",
         "D1", "A", "SR", ""),
"E033": ("occupation (N8)", "N8 (23 May 1949); M8 ECSC 18 Apr 1951; M1 5 May 1955", "voluntary (Adenauer)",
         "D1", "A", "SR", ""),
"E034": ("B1 (21 Apr 1945)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Soviet imposition)",
         "D1", "A", "SR", ""),
"E035": ("B3 (18 Feb 1948)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Soviet imposition)",
         "D1", "A", "SR", ""),
"E036": ("B4 (4 Feb 1948)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Soviet imposition)",
         "D1", "A", "SR", ""),
"E037": ("B5 (18 Mar 1948)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Soviet imposition)",
         "D1", "A", "SR", ""),
"E038": ("B2 (12 Dec 1943)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Feb 1948 coup)",
         "D1", "A", "SR", ""),
"E039": ("B2 (12 Dec 1943)", "M7 (Sep 1947); M5 founding (Jan 1949; FLAG 2)", "coerced (Feb 1948 coup)",
         "D1", "A", "SR", "Czechoslovak record"),
"E040": ("YUG tie to 1948; Soviet credits late 1940s", "M5 accession Feb 1949; M6 founding 14 May 1955",
         "voluntary (Hoxha turn to USSR vs YUG)", "D1", "A", "SR", ""),
"E041": ("B1; M6; M5", "M6 military structures 25 Feb 1991; M6 Prague protocol 1 Jul 1991; M5 dissolution 28 Jun 1991",
         "voluntary (1989)", "D1; D3", "A", "V-2026-11", ""),
"E042": ("B3; M6; M5", "M6 25 Feb / 1 Jul 1991; M5 dissolution 28 Jun 1991", "voluntary (1989)",
         "D1; D3", "A", "V-2026-11", ""),
"E043": ("B2; M6; M5", "M6 25 Feb / 1 Jul 1991; M5 dissolution 28 Jun 1991; Velvet Revolution Nov 1989",
         "voluntary (1989)", "D1; D3", "A", "V-2026-11", ""),
"E044": ("B2; M6; M5", "M6 25 Feb / 1 Jul 1991; M5 dissolution 28 Jun 1991; Velvet Revolution Nov 1989",
         "voluntary (1989)", "D1; D3", "A", "V-2026-11", ""),
"E045": ("B4; M6; M5", "M6 25 Feb / 1 Jul 1991; M5 dissolution 28 Jun 1991; revolution Dec 1989",
         "voluntary (1989)", "D1; D3", "A", "V-2026-11", ""),
"E046": ("B5; M6; M5", "M6 25 Feb / 1 Jul 1991; M5 dissolution 28 Jun 1991", "voluntary (1989)",
         "D1; D3", "A", "V-2026-11", ""),
"E047": ("M5; M6", "C-56/64 (1960-61); Vlore eviction May-Jun 1961; CMEA participation ends end-1961; M6 withdrawal 13 Sep 1968",
         "coerced (Soviet sanctions), then voluntary defiance", "D2", "A", "V-2026-11 (13 Sep 1968)", ""),
"E048": ("B7 (6 Apr 1948)", "M12; B7 replaced 20 Jan 1992", "voluntary (post-USSR settlement)",
         "D1-3140", "A", "V-2026-11 (month); FLAG 5", ""),
"E049": ("severed (E041)", "M8 EA 16 Dec 1991; M1 12 Mar 1999; EU 1 May 2004", "voluntary (referendum 7-8 Jun 2003)",
         "D3", "A", "SR", ""),
"E050": ("severed (E042)", "M8 EA 16 Dec 1991; M1 12 Mar 1999; EU 1 May 2004", "voluntary (referendum 12 Apr 2003)",
         "D3", "A", "SR", ""),
"E051": ("severed (E043)", "M8 EA 16 Dec 1991 (CSFR), re-signed 4 Oct 1993; M1 12 Mar 1999; EU 1 May 2004",
         "voluntary (referendum 13-14 Jun 2003)", "D3", "A", "V-2026-11 (EA 1993)", ""),
"E052": ("severed (E044)", "M8 EA 4 Oct 1993; M1 29 Mar 2004; EU 1 May 2004", "voluntary (referendum 16-17 May 2003)",
         "D3", "A", "V-2026-11 (EA 1993)", ""),
"E053": ("severed (E045)", "M8 EA 1 Feb 1993; M1 29 Mar 2004; EU 1 Jan 2007", "voluntary (referendum 18-19 Oct 2003)",
         "D3", "A", "SR", ""),
"E054": ("severed (E046)", "M8 EA 8 Mar 1993; M1 29 Mar 2004; EU 1 Jan 2007", "voluntary",
         "D3", "A", "SR", ""),
"E055": ("severed (SFRY succession; B26)", "M8 EA 10 Jun 1996; M1 29 Mar 2004; EU 1 May 2004",
         "voluntary (referendum 23 Mar 2003)", "D3", "A", "SR", ""),
"E056": ("severed (SFRY succession; B26)", "M8 SAA 29 Oct 2001; M1 1 Apr 2009; EU 1 Jul 2013",
         "voluntary", "D3", "A", "SR", ""),
"E057": ("severed (E047); isolation", "B35 (15 Mar 1991); M8 SAA 12 Jun 2006; M1 1 Apr 2009",
         "voluntary", "D1", "A", "SR", ""),
"E058": ("B7 (to 1992)", "M8 EEA 2 May 1992 (1 Jan 1994); B31 referendum 16 Oct 1994; EU 1 Jan 1995",
         "voluntary (referendum)", "D1", "A", "SR", ""),
"E059": ("B20 base closure 31 Mar 1979; neutrality", "N11 (16 Jul 1990); EU 1 May 2004; no NATO",
         "voluntary (PN government)", "D3", "B", "FLAG (OPEN_ISSUES)", "Pending user ruling"),
"E060": ("US sphere (M3 member)", "B22 (FSLN victory 19 Jul 1979; Soviet credits/oil 1980-81)",
         "voluntary (revolution)", "D3; S", "C", "SR", "FLAG 7 qualitative"),
"E061": ("US sphere; aid relationship", "N7 (Apr/Dec 1981); N4 (1 May 1985); C-296/306/464; harbor mining 1984",
         "coerced (US sanctions)", "D2", "A", "V-2026-11 (N4)", ""),
"E062": ("B22 tie", "Soviet aid ends 1990-91 (M12); Chamorro elected 25 Feb, inaugurated 25 Apr 1990",
         "mixed: patron collapse + electoral", "D3", "A", "SR", ""),
"E063": ("N4 embargo", "N5 (13 Mar 1990); aid resumption", "US voluntary lift post-election",
         "D3", "B", "V-2026-11 (N5)", ""),
"E064": ("UK colony", "independence 31 Aug 1962; M3 accession 1967; M2 1967", "voluntary",
         "D1-3075; D3", "A", "SR", ""),
"E065": ("UK colony", "independence 6 Aug 1962; M2 1969", "voluntary", "D1; D3", "A", "SR", ""),
"E066": ("NL colony", "independence 25 Nov 1975; M2 1977", "voluntary", "D1; D3", "A", "SR", ""),
"E067": ("UK colony to 1966; Burnham nonalignment", "B21 (Hoyte 6 Aug 1985; ERP 1988; OAS Jan 1991)",
         "voluntary (post-Burnham reorientation)", "D3", "B", "V-2026-11 (OAS); FLAG (OPEN_ISSUES)", "Pending user ruling"),
"E068": ("US sphere", "Allende inaugurated 3 Nov 1970; B23 covert programme; C-147/179",
         "coerced threat (destabilization; no formal severance)", "D3", "A", "DS+P", "severance_threat"),
"E069": ("empire/defeat", "B24 (2 Sep 1945; Peace Treaty 8 Sep 1951); B13 (8 Sep 1951; rev. 19 Jan/23 Jun 1960); IMF 1952/GATT 1955",
         "occupation-imposed, then voluntary (1960 revision)", "D1; U1 (JPN 18 Dec 1956)", "A", "SR", ""),
"E070": ("USAMGIK occupation", "B25 (15 Aug 1948; armistice 27 Jul 1953); B14 (1 Oct 1953 / 17 Nov 1954)",
         "voluntary (Rhee sought guarantee)", "D1; U1 (17 Sep 1991)", "A", "SR", ""),
"E071": ("partition; Soviet/Chinese aid", "B37 (Paris 27 Jan 1973; Saigon 30 Apr 1975; reunification 2 Jul 1976); M5 approved 29 Jun 1978; B10 (3 Nov 1978)",
         "voluntary", "D3; U1 (20 Sep 1977)", "A", "V-2026-11 (M5)", ""),
"E072": ("B8 (1966 pact); M5 (1962)", "Soviet aid cuts; B36 withdrawal agreements 1990 (complete 1992); B8 replaced 20 Jan 1993",
         "patron collapse", "D1 (3535->4395); D3", "A", "V-2026-11 (1993 treaty)", ""),
"E073": ("B9 (6 Jul 1961 USSR; 11 Jul 1961 PRC)", "B18 (30 Sep 1990); Soviet aid termination; B9 lapse 1996 (formal tail); B9 2000 (no defense clause)",
         "patron-driven (USSR initiative)", "shadow-case estimates (FLAG 6)", "B", "V-2026-11 (B9 days)", "Shadow case caveat"),
}

HEADER = ["episode_id", "iso3", "type", "anchors_prior_tie", "anchors_change",
          "anchors_voluntariness", "validation_sources", "quality_grade",
          "verification_status", "notes"]

def main():
    with open(EPISODES) as f:
        eps = {r["episode_id"]: r for r in csv.DictReader(f)}
    missing = [e for e in eps if e not in M]
    extra = [e for e in M if e not in eps]
    if missing or extra:
        sys.exit(f"mapping mismatch: missing={missing} extra={extra}")

    with open(OUT_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for eid in sorted(eps):
            p, c, v, val, g, s, n = M[eid]
            w.writerow([eid, eps[eid]["iso3"], eps[eid]["type"], p, c, v, val, g, s, n])

    lines = ["| Episode | Prior tie | Change | Voluntariness | Validation | Grade | Status |",
             "|---------|-----------|--------|---------------|------------|-------|--------|"]
    for eid in sorted(eps):
        p, c, v, val, g, s, n = M[eid]
        label = f"{eid} {eps[eid]['iso3']}"
        lines.append(f"| {label} | {p} | {c} | {v} | {val} | {g} | {s} |")
    table = "\n".join(lines)

    with open(REGISTER) as f:
        doc = f.read()
    pat = re.compile(r"(<!-- BEGIN AUTO EPISODE TABLE -->).*?(<!-- END AUTO EPISODE TABLE -->)", re.S)
    if not pat.search(doc):
        sys.exit("markers not found in register")
    doc = pat.sub(lambda m: m.group(1) + "\n" + table + "\n" + m.group(2), doc)
    with open(REGISTER, "w") as f:
        f.write(doc)

    grades = {}
    for eid in eps:
        grades[M[eid][4]] = grades.get(M[eid][4], 0) + 1
    print(f"wrote {OUT_CSV}: {len(eps)} rows; grades {grades}; register table injected")

if __name__ == "__main__":
    main()
