# Slide Build Protocol — 15-Minute Thesis Talk

Companion to `PRESENTATION_PLAN.md` (v2, standard model). This document is the
*build order*, not the deck order. Guiding logic: a PhD student's scarcest
resources are time and committee goodwill, and the highest-risk items are the
figures that carry the argument. So we build evidence first, packaging last, and
verify every number against the data before it touches a slide.

**Ground rules for every step:**
- Every number on a slide must be traceable to a file in `data_clean/` or a doc in
  `docs/`. If you can't point to the source, the number doesn't ship.
- Slide titles are assertions, not labels ("Severance is followed by collapse", not
  "Results").
- One finding per slide. If a slide needs the word "also", split it.
- Font check: nothing below ~20pt equivalent; readable from the back row.

---

## Phase 0 — Lock the message before opening any slide software (≈1 hour)

The single highest-leverage hour of the whole process. Everything else is execution.

1. **Write the takeaway sentence by hand, on paper.** Current candidate (from the
   plan, Slide 15): *"It is not who governs that moves economies — it is whether a
   change in the state's international position changes the material capabilities it
   commands."* Edit until you'd be willing to have it quoted back to you by the
   panel.
2. **Verify the three preview numbers** that headline the talk against
   `data_clean/baseline_cell_contrasts_preliminary.csv` and
   `docs/STEP6_PRELIMINARY.md`: −3.28% (severance, 5-yr forward), +3.43% (richer
   entry), +2.23% (no realignment); 15/20 disruption frequency; 12/20 acceleration
   onset. Write down the exact dating variant they come from (interval-start coding)
   and the sample sizes (n=20 each). If any number has moved since the abstract was
   written, the abstract numbers win only if they're still reproducible — check.
3. **Write the one-sentence research question** exactly as it will appear on Slide 3.
4. **Decide the H1 framing** (absence-as-falsification) and confirm the preliminary
   data support it — pull the turnover-only cell frequencies from the Step 6 outputs.
   If turnover-only cells show elevated discontinuities, stop: Slide 13 needs
   redesigning before anything else is built.

*Done when:* you can say the question, the three numbers, and the takeaway out loud
in under 60 seconds without notes.

---

## Phase 1 — Build the evidence slides first (Slides 11, 12, 13, 2)

These four slides carry the argument. They get first claim on your best hours, and
their final form constrains everything else.

### Step 1.1 — Slide 11 (Result 1: severance vs. entry growth) — highest priority

- **Input:** `data_clean/baseline_cell_contrasts_preliminary.csv`; plotting code in
  `code/analyze_baseline_contrasts_preliminary.py` (adapt, don't hand-draw).
- **Build:** mean post-event growth by group (severance / richer entry / no
  realignment). Prefer a bar chart with confidence intervals or a simple forward-path
  plot — whichever is cleaner at a glance. No more than 3 series/bars.
- **Checks:** axis labels in plain language ("Mean annual real GDP p.c. growth, years
  1–5 after event"), not variable names; sample sizes printed on the slide; the
  "descriptive, non-causal" flag visible.
- *Done when:* a colleague glancing for 5 seconds can state the direction and rough
  magnitude correctly.

### Step 1.2 — Slide 12 (Result 2: discontinuity frequencies)

- **Input:** forward-outcome frequency tables from Step 6 outputs
  (`data_clean/`, see `docs/STEP6_PRELIMINARY.md` for exact files).
- **Build:** two bars — 75% (15/20) disruption after severance; 60% (12/20)
  acceleration onset after richer entry. Percentages big, fractions small underneath.
- *Done when:* the slide makes the point with zero verbal explanation.

### Step 1.3 — Slide 13 (Result 3: H1, the dog that doesn't bark)

- **Input:** turnover-only / nominal-regime-change-only cell frequencies (same Step 6
  outputs; cross-check `data_clean/turnover.csv` merge).
- **Build:** baseline vs. turnover-only discontinuity rate, side by side. Title frames
  it as falsification of the blob category, e.g., *"Turnover without realignment
  changes nothing — 'regime change' as usually measured is the wrong category."*
- **Risk check:** this is the slide the panel will probe hardest. Prepare the exact
  cell counts and be ready to name one turnover-only case that *did* disrupt and why
  (that's backup material, B5).
- *Done when:* you can defend the claim "near baseline" with counts, not adjectives.

### Step 1.4 — Slide 2 (Motivation: the puzzle figure)

- **Input:** outcome series from `data_clean/outcomes.csv`; case documentation from
  `case_notes/CUB_1960.md`, `case_notes/CUB_1989.md`, and the matched turnover case
  (choose from `docs/Cases.md` pairs).
- **Build:** 2–3 GDP-per-capita trajectories with the political rupture marked.
  Cuba 1960 or 1989–91 vs. a turnover-without-realignment case is the current
  candidate. This is the most design-intensive slide in the deck — budget for 2–3
  iterations.
- **Checks:** the contrast must be visible without color alone (panel members print
  in grayscale); event markers labeled in words ("Soviet withdrawal 1989–91"), not
  just vertical lines.
- *Done when:* the puzzle is visible before you say a word.

---

## Phase 2 — Build the motivation close (Slides 1, 3, 4)

Cheap slides, but they must interlock with Phase 1 exactly.

5. **Slide 4 — Preview of findings.** The three verified numbers from Phase 0, as
   bullets. The wording of the caveat ("descriptive, non-causal, preliminary") must
   match Slide 11's flag verbatim — the panel will notice inconsistency.
6. **Slide 3 — Research question.** The sentence from Phase 0 plus one line of
   significance. No more.
7. **Slide 1 — Title.** Title, name, affiliation, date. Check against the thesis
   cover page (`paper/deliverable_draft_thesis.tex`) so they match exactly.

*Done when:* Slides 1–4 can be presented as a self-contained 4-minute mini-talk that
ends with the numbers Slides 11–13 will later prove.

---

## Phase 3 — Build the standard sections (Slides 5–10, 14, 15)

Deliberately built *after* the evidence: these sections exist to frame the results,
and they're faster to write once the results are fixed. Don't gold-plate them.

8. **Slide 7 — Framework diagram.** Build the five-link chain (who rules → how power
   is organized → apparatus → external position → outcomes) directly from
   `docs/Core_Concepts.md` §"Compact conceptual chain". One diagram, no definitional
   text walls. This is the second-most design-intensive slide; budget iterations.
9. **Slide 8 — Hypotheses.** H1–H3, one line each, copied from the thesis abstract
   and compressed. Annotate each with the diagram link it tests.
10. **Slide 6 — Literature.** Three strands, one line each + our position
    (Treier–Jackman; Little–Meng; AJR circularity; ANRR 2019 inheritance). Resist
    adding a fourth strand. Citations as author-year only, small font, bottom.
11. **Slide 9 — Data.** Episode counts from `data_clean/episodes.csv` (46 entry /
    25 severance / 2 threats), panel coverage (73 countries, 1945–2019), coding rule
    (≥2 of 4 families, 3-year windows), source grades (A 64 / B 7 / C 2 from
    `data_clean/episode_sources.csv`), plus the reassurance line pointing to backup.
12. **Slide 10 — Design.** The three layers from `docs/ROADMAP.md` (Steps 6–8), one
    line each, with status: done-preliminary / next / next. This slide answers "is
    this student going to finish?" — make the progress visible.
13. **Slide 5 — Outline.** Seven section names. Built late because it must match the
    final deck, not the plan.
14. **Slide 14 — Limitations.** Three items, each paired with its remedy and a backup
    reference (B4, B5, B7). Pull the honest language from the abstract's final
    sentences — it has already survived scrutiny.
15. **Slide 15 — Conclusion.** What was asked / what the evidence shows / what the
    project contributes, then the takeaway sentence set apart visually.

*Done when:* each of these slides passes the "so what?" test and none exceeds one
minute of speaking.

---

## Phase 4 — Build the backup deck (B1–B7)

A PhD student wins or loses a defense in Q&A. The backup deck is not an appendix of
leftovers; it is pre-committed answers.

16. **B1** — Formal H1–H3 and equation (1) from `paper/deliverable_draft_thesis.tex`
    §1.3 and §5.
17. **B2** — Coding rules R1–R6 from `docs/Coding_Protocol.md`, one rule per line,
    with one worked example.
18. **B3** — Episode table excerpt + source-grade distribution from
    `data_clean/episodes.csv` / `docs/EPISODE_SOURCES.md`.
19. **B4** — Sensitivity summary from
    `data_clean/baseline_contrast_sensitivity_preliminary.csv` and
    `baseline_contrast_leave_one_country_out_preliminary.csv`: dating variants,
    excluding 1989–91, systemic-shift cases. One slide, three mini-panels max.
20. **B5** — Three case vignettes (Venezuela, Cuba 1989–91, Baltics 2004), one
    paragraph + one number each, from `case_notes/`.
21. **B6** — Panel construction and missingness from `docs/STEP5_AUDIT_PRELIMINARY.md`.
22. **B7** — Planned regression specification and robustness menu from
    `paper/draft2.tex` §5.2.

*Done when:* for every core slide, you can name the backup slide that defends it.
Add a visible "Backup" divider slide and slide numbers throughout — "go back to
slide 9" must be answerable in two seconds.

---

## Phase 5 — Assembly and design pass (one sitting, fresh eyes)

23. **Title audit:** read only the slide titles, top to bottom. They should tell the
    story as assertions. Any label-title ("Data", "Results") gets rewritten.
24. **Density audit:** any slide you can't read aloud in its entirety in 20 seconds
    is overloaded — cut, don't shrink font.
25. **Consistency audit:** same caveat wording everywhere; same case examples on
    Slides 2 and B5; numbers identical between Slides 4, 11, 12, 13.
26. **Grayscale print test** for all figures.

---

## Phase 6 — Rehearsal protocol (non-negotiable)

27. **Rehearsal 1 (alone, timed):** expect ~20–25 minutes. Record where you overrun.
28. **Cut by rule, not by taste:** cut from Literature (Slide 6) and Data (Slide 9)
    first — the standard sections tolerate compression. Never cut Results or the
    puzzle. If still long, demote Slide 12's detail to speech.
29. **Rehearsal 2 (alone, timed):** target 13:30–14:00. Practice the transitions
    between sections out loud — section boundaries are where defenses stall.
30. **Rehearsal 3 (live audience — labmates, anyone):** the only way to discover
    which slide confuses people. Ask each listener: "what was my main claim?" If the
    answer isn't the takeaway sentence, the deck is wrong, not the listener.
31. **Interruption drill:** have a friend stop you mid-Slide 9 with a hard question;
    practice answering in ≤45 seconds and resuming without losing the thread. A
    defense is interrupt-driven by design.

---

## Phase 7 — Red-team the Q&A (1–2 days before)

32. Write the **five questions you most fear** and draft 2–3 sentence answers, each
    ending with a pointer to a backup slide. Predictable ones for this thesis:
    - "Your contrasts are non-causal — why should we care?" → Slide 10's design
      ladder + B7.
    - "Venezuela: coding judgment call, yes?" → B5 + `docs/OPEN_ISSUES.md`.
    - "How is this different from ANRR (2019)?" → Slide 6 answer, tightened.
    - "Why these 73 countries / why 1945–2019?" → B6.
    - "What happens to H1 if you exclude 1989–91?" → B4.
33. Confirm the state of open coding issues (`docs/OPEN_ISSUES.md`) so no panel
    question catches you on an item you haven't adjudicated.

---

## Phase 8 — Logistics (day before)

34. Export PDF (fonts embedded) + native format; test on the actual projector if
    possible; bring the clicker and a USB copy.
35. Print one grayscale copy for yourself with speaker notes.
36. Final number check: Slides 4, 11, 12, 13 against `data_clean/` one last time.

---

## Priority summary (if time runs short, cut from the bottom)

| Priority | Item | Why |
|---|---|---|
| 1 | Phase 0 message lock | Everything depends on it; costs 1 hour |
| 2 | Slides 11–13 + Slide 2 | The argument lives here |
| 3 | Backup deck + red-team | Defenses are won in Q&A |
| 4 | Rehearsals 1–3 | A mediocre deck rehearsed beats a great deck cold |
| 5 | Motivation close (1–4) | Cheap, high polish value |
| 6 | Standard sections (5–10, 14–15) | Necessary but compressible |
| 7 | Design pass | Do it, but never at the expense of 1–4 |
