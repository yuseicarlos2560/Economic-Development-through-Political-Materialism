# Thesis Presentation Plan

**Format:** 15-minute talk to a panel of professors (expert audience, thesis defense style).
**Structure decision (v2):** the deck follows the **standard model** of academic
presentations (outline → literature → framework → data → design → results → robustness →
conclusion), **except the Introduction/Motivation block**, which keeps the hook-driven
format from the exemplar research (puzzle first, question explicit, findings previewed).
Everything after motivation is deliberately conventional: a defense panel navigates by
familiar landmarks, and the standard structure is itself a credibility signal.

---

## Part I — Essential Elements to Keep in Mind

Distilled from four exemplars in economics and political science (Shapiro; La Ferrara;
*PS: Political Science & Politics*, "Cheating Death-by-PowerPoint"; Goldstein & Evans /
World Bank), reconciled with the standard model now adopted.

### A. Content principles (apply to the whole deck)

1. **The opening is a transaction.** The audience does not yet care about the topic; the
   Introduction/Motivation block exists to change that (Shapiro). Open with a real-world
   puzzle or stylized fact, never with the literature (La Ferrara). The canonical arc:
   *they thought the answer was X, but X cannot explain wrinkle Y; I propose Z* (*PS*).
2. **State the research question explicitly within the first minutes.** It should be a
   policy/counterfactual question or a test of theoretical predictions — not "what happens
   if I re-estimate X on new data" (Shapiro).
3. **Preview the findings early.** "Assume the audience is about to leave" (Shapiro); "this
   isn't a murder mystery" (Bellemare). The preview is the last slide of the Motivation
   block; the Results section then delivers what was promised.
4. **One finding per slide; figures over tables; titles are assertions.** Never paste a
   paper table. Slide titles state the claim, not the container (La Ferrara, AEA CSWEP,
   *PS*). This rule survives the move to the standard model intact — it governs how each
   standard section is filled, not how the deck is organized.
5. **Interpret, don't just describe.** Every result slide answers: what does this mean for
   the hypothesis, how confident are we, what would falsify it.
6. **Own the limitations.** The standard model gives them a dedicated place
   (Robustness/Limitations section); the exemplars tell us how to fill it — name the
   concern yourself, pair each with its remedy, no kamikaze (*PS*, La Ferrara).
7. **End with one sentence.** A single takeaway the panel remembers a week later
   (Shapiro's "bottom line"). In the standard model this lives on the Conclusion slide.

### B. Design and delivery principles

8. **Time discipline is design.** A 15-minute talk is not a 90-minute talk at triple
   speed (Rabin via Shapiro; World Bank). The standard model inflates slide counts;
   cap the core deck at ~15 slides and ~1 minute per slide (NeurIPS pacing rule as
   upper bound), with results never squeezed into the final minutes (Karpathy's
   pitfall — explicitly avoided in the timing table below).
9. **Slides support the voice; they don't replace it.** Nothing on a slide you won't say;
   space corresponds to intended emphasis (Shapiro). No full sentences lifted from the
   thesis; no equations the audience can't parse in 20 seconds (*PS*).
10. **The framework is a diagram, not a wall of definitions.** One picture that carries
    the intuition, talked through "like a weather presenter" (*PS*). In the standard
    model this is the Theoretical Framework slide — it stays visual even though the
    section is conventional.
11. **No data-plumbing slides.** "No one wants to see your underwear" (Shapiro). The
    standard model's Data section states sources, coverage, and coding rules at the level
    of credibility, not process; the pipeline lives in backup.
12. **Practice out loud, timed.** The first rehearsal will reveal a 25-minute talk
    (World Bank). Cut from Literature and Data before touching Results.

### C. Panel-of-professors specifics

13. **A defense is an evaluation, not a seminar.** Every claim on a core slide must have
    a backup slide behind it (formal hypotheses, coding rules, episode sources,
    sensitivities, regression spec). This is where the standard model's completeness
    instinct is legitimately relocated.
14. **Feasibility and progress matter.** The panel judges what is done, what is
    preliminary, and what remains. The Empirical Design slide states the three-layer
    plan and says plainly which layer this talk reports.
15. **The "so what?" test on every slide.** If a slide's role in the storyline isn't
    obvious, cut it or fold it into backup.

---

## Part II — Page-by-Page Layout, Standard Model (15 core slides + backup)

Conventions: **[STD]** = slide exists because the standard model requires the section;
**[EXM]** = slide shaped by the exemplar research (PRESENTATION_PLAN v1 / Part I).
Timing target ~14 minutes, leaving buffer for interruptions.

### INTRODUCTION & MOTIVATION — kept from the original format (Slides 1–4)

**Slide 1 — Title (≈30–45 s, stays up during the opening story) [EXM]**
Title, name, affiliation, date. Nothing else.
*Justification:* *PS* — keep the title slide up while telling the opening story so
attention stays on the speaker; no conference-name boilerplate.

**Slide 2 — Motivation: the puzzle (≈2 min) [EXM]**
One figure: paired GDP-per-capita trajectories around political ruptures — Cuba
1960/1989–91 (realignment → collapse) against a matched turnover without deeper change
(trajectory intact). Assertion title, e.g., *"Some political ruptures break economies;
most pass unnoticed."*
*Justification:* Shapiro's "1–2 slides to change their minds"; La Ferrara's stylized-fact
motivation. Cases from calibrated episodes (`case_notes/`, `docs/Cases.md`), so every
visual claim is documented.

**Slide 3 — Research question (≈1 min) [EXM]**
The question verbatim: *which changes in a country's political and international
situation produce major economic discontinuities?* One line on why it matters
(measurement critique in one sentence — full treatment deferred to Literature, per the
standard model).
*Justification:* Shapiro — a real, explicit question early. The "why it matters" teaser
hands off to the Literature section without duplicating it.

**Slide 4 — Preview of findings (≈1 min) [EXM]**
Three numbered bullets: severance → −3.28% mean annual growth over five years; richer
entry → +3.43%; no realignment → +2.23%. Flag: descriptive, non-causal, preliminary.
*Justification:* "Assume the audience is about to leave" (Shapiro). Numbers plus the
honesty flag in the same breath.

### ROADMAP (Slide 5)

**Slide 5 — Outline (≈20 s) [STD]**
One line per section: Literature → Framework & Hypotheses → Data & Measurement →
Empirical Design → Results → Robustness & Limitations → Conclusion.
*Justification:* Standard model. Karpathy's spoiler objection is real for 12-minute ML
orals, but a defense panel navigates by landmarks and will interrupt; the outline is
their map. Keep it to seconds, not a narration.

### LITERATURE (Slide 6)

**Slide 6 — Literature and gap (≈1.5 min) [STD structure, EXM discipline]**
Three strands, one line each plus our position: (i) expert-coded indices carry
measurement error (Treier–Jackman; Little–Meng); (ii) inclusive/extractive
classifications are outcome-contaminated and unfalsifiable on horizon (AJR critique);
(iii) democratization–growth estimates inherit both problems (ANRR 2019). Bottom line:
we need observable event coding.
*Justification:* The standard model requires a literature section; the exemplars dictate
its form — framed as contribution, not attack (La Ferrara), no citation lists (*PS*).
This slide now carries the full measurement argument that v1 used as motivation.

### THEORETICAL FRAMEWORK & HYPOTHESES (Slides 7–8)

**Slide 7 — The framework in one diagram (≈1.5 min) [STD section, EXM form]**
The compact conceptual chain as a flow diagram: who rules → how power is organized →
through what apparatus → external position → outcomes.
*Justification:* Standard model requires a theory section; *PS* dictates its form — one
diagram, talked through, no definitional walls. Anchored in `docs/Core_Concepts.md`.

**Slide 8 — Hypotheses (≈1 min) [STD]**
H1–H3 stated in one line each, each annotated with the link of the diagram it tests
(H1 domestic, H2 external, H3 interaction).
*Justification:* Standard placement of hypotheses after the framework. Moving them here
(from v1's Slide 3) follows convention; one-line statements keep them memorable.

### DATA & MEASUREMENT (Slide 9)

**Slide 9 — Data: events, not opinions (≈1.5 min) [STD section, EXM discipline]**
73 realignment episodes (46 entry, 25 severance, 2 threats); 73-country panel,
1945–2019; coding rule ≥2 of 4 observable indicator families in 3-year windows; source
grades A 64 / B 7 / C 2. One reassurance line: "every coding decision sourced and
audited — details in the appendix slides."
*Justification:* Standard Data section; Shapiro's credit-for-novel-measurement rule sets
the altitude; the reassurance line is the relocated gestalt signal (see
`CROSS_EXAMINATION.md` §7).

### EMPIRICAL DESIGN (Slide 10)

**Slide 10 — Design: three layers, falsification first (≈1 min) [STD]**
(1) descriptive event-screen — done, preliminary, reported here; (2) country & year
fixed-effects panel with turnover and regime-change controls — next; (3) matched-case
process tracing + double-coding reliability — next. Reference to equation (1) by name;
the equation itself is backup slide B1.
*Justification:* Standard Methods section; La Ferrara's pre-emption rule (shows where
causal claims will be earned); panel-specific feasibility signal (principle 14).

### RESULTS (Slides 11–13)

**Slide 11 — Result 1: severance breaks, entry accelerates (≈1.5 min) [EXM form]**
One figure: post-event growth for severance vs. richer entry vs. no-realignment years.
Assertion title: *"Leaving a sphere costs ~5.7 points of growth; joining a richer one
gains ~1.2."*
*Justification:* H2's centerpiece. One finding per slide, figure not table, assertion
title (La Ferrara, *PS*).

**Slide 12 — Result 2: discontinuities cluster where predicted (≈1 min) [EXM form]**
Two-bar chart: disruption within 5 years in 15/20 severance windows (75%); acceleration
onset within 8 years in 12/20 richer-entry windows (60%).
*Justification:* Frequencies complement means; reads as robust to outliers. One finding
per slide.

**Slide 13 — Result 3: the dog that doesn't bark — H1 (≈1.5 min) [EXM form]**
Turnover and nominal regime change without realignment: discontinuity rates near
baseline. Framed as falsification of the undifferentiated "regime change" category.
*Justification:* The hardest sell — an absence. Tie it to what it falsifies so it reads
as contribution, not null result (interpretation-over-description, principle 5).

### ROBUSTNESS & LIMITATIONS (Slide 14)

**Slide 14 — Limitations and what fixes them (≈1 min) [STD section, EXM content]**
Three items + remedies: (i) non-causal descriptives → FE panel and patron-collapse
severances (Step 7); (ii) dating sensitivity → start/midpoint/endpoint variants audited
(B4); (iii) wrong-sign cases exist → case layer will trace them (Step 8, B5).
*Justification:* The standard model's robustness slot, filled per *PS*'s closing rule —
own the concern so Q&A is about fixes. Matches the abstract's register.

### CONCLUSION (Slide 15)

**Slide 15 — Conclusion and takeaway (≈1 min) [STD section, EXM ending]**
Three bullets: what was asked, what the preliminary evidence shows, what the project
contributes (replicable event taxonomy replacing contested indices) — then one sentence,
visually set apart: *"It is not who governs that moves economies — it is whether a
change in the state's international position changes the material capabilities it
commands."*
*Justification:* Standard conclusion slot; Shapiro's bottom-line rule and *PS*'s
"choose the one point for them" govern its content. Contribution + plan is what a
thesis panel is asked to judge.

### BACKUP SLIDES (not presented; for Q&A only)

- B1: Full H1–H3 formal statements and equation (1).
- B2: Coding protocol rules R1–R6 with examples (`docs/Coding_Protocol.md`).
- B3: Episode list and source grades (`data_clean/episodes.csv`, `docs/EPISODE_SOURCES.md`).
- B4: Sensitivities: start/midpoint/endpoint dating, excluding 1989–91, systemic-shift
  cases (`data_clean/baseline_contrast_*_preliminary.csv`).
- B5: Case vignettes for hard questions: Venezuela (determinacy crux), Cuba 1989–91,
  Baltics 2004 (`case_notes/`).
- B6: Panel construction and missingness policy (`docs/STEP5_AUDIT_PRELIMINARY.md`).
- B7: Planned regression specification and robustness menu (draft2.tex §5.2).

*Justification:* principle 13 — the standard model's completeness instinct lives here,
one click away, not on core slides.

---

## Part III — Timing check

| Section | Slides | Time |
|---|---|---|
| Introduction & Motivation | 1–4 | ~4.5 min |
| Roadmap | 5 | ~0.5 min |
| Literature | 6 | ~1.5 min |
| Framework & Hypotheses | 7–8 | ~2.5 min |
| Data & Design | 9–10 | ~2.5 min |
| Results | 11–13 | ~4 min |
| Limitations & Conclusion | 14–15 | ~2 min |
| **Total** | 15 | **~15 min (target 14)** |

Guards against the standard model's known failure modes (see `CROSS_EXAMINATION.md`):
results are previewed at Slide 4 and never rushed at the end (Karpathy's pitfall);
literature is one slide, not a survey (La Ferrara); no pasted tables anywhere
(AEA/*PS*); the outline slide costs 20 seconds, not a narration.

---

## Changelog

- **v1:** exemplar-driven structure throughout (puzzle-first, no outline slide,
  hypotheses inside the motivation block, design folded into a single "cheap
  falsification" slide, 13 core slides).
- **v2 (current):** standard model adopted — outline, dedicated Literature, Framework
  & Hypotheses, Data, Design, Robustness & Limitations, Conclusion sections.
  Introduction & Motivation block (Slides 1–4) kept from v1 unchanged. Hypotheses moved
  from the opening to the Framework section per convention; the measurement critique
  moved from motivation to the Literature section. 15 core slides; timing rebalanced so
  Results still receive the largest single block.
