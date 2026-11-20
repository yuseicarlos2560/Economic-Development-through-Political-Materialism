# Cross-Examination — The "Standard Boring" Talk vs. Our Plan

Companion to `PRESENTATION_PLAN.md`. Here we contrast our design (built from
economics/political-science exemplars) against the modal presentation at top
technical venues — ICML/NeurIPS/ICLR orals, IEEE talks, *Science*-style seminars —
and against the opposite pole, the Nobel lecture. The point is not to mock the
standard format: it survives because it solves real problems. The point is to know
exactly which of its conventions we are rejecting, and why.

Sources: [ICML 2025 presenter instructions](https://icml.cc/Conferences/2025/PresenterInstructions)
(12-minute orals + 2 min Q&A), [NeurIPS oral guidance](https://qrsntu.org/service/neurips26/oral/)
(~one slide per minute: title, problem, why hard, idea, method, main result),
[ETH Zürich MLSys seminar guide](https://ethz.ch/content/dam/ethz/special-interest/infk/inst-cp/inst-cp-dam/education/courses/2022-autumn/mlsys-seminar/MLSysSeminar22_how_to_read_review_papers.pdf)
(hook + T-shaped structure), [Andrej Karpathy, "A Survival Guide to a PhD"](http://karpathy.github.io/2016/09/07/phd/)
(insider account of how ML talks are actually built and received), plus the Nobel
lecture literature (autobiographical, retrospective, authorial voice rather than
fixed structure).

---

## 1. How the typical ICML/NeurIPS/IEEE talk is actually built

The modal contributed talk is the paper, serialized. The implicit template:

1. **Title slide** with full author list, affiliations, logos, conference branding.
2. **Outline slide** ("First I will motivate… then I will present our method…").
3. **Introduction/Problem** — usually 2–4 slides, often text-heavy bullets.
4. **Related Work** — a slide of citation thumbnails or logos.
5. **Method** — one dense architecture/pipeline diagram, then several slides walking
   through it block by block; equations included.
6. **Experiments** — tables of benchmark numbers with the best column bolded;
   ablation tables; sometimes a qualitative results grid.
7. **Conclusion + future work.**

Timing: 12 minutes at ICML, roughly one slide per minute at NeurIPS orals. The
structure is simply IMRaD — the paper's section headings — projected onto a screen.

## 2. The pattern underneath: the talk as compressed paper, not as story

Three features define the pattern:

- **Chronological/logical order of the paper, not causal order for the listener.**
  The audience hears motivation only after sitting through outline and related work;
  results arrive in the final two minutes, often rushed (Karpathy's first pitfall:
  "speakers spend too much time on the early intro parts and then frantically speed
  through the last few slides that contain the most interesting results").
- **Completeness as insurance.** Dense tables, all ablations, every baseline: the
  slides function as a pre-emptive defense against reviewers-in-the-audience. The
  talk is built to be *unattackable*, not to be *followed*.
- **The gestalt signal.** Karpathy describes how senior researchers judge a paper in
  seconds by its *look*: pull figure on page 1, system figure on page 3, math
  symbols present, results table with bolded numbers, exactly 8 pages. The standard
  talk performs the same gestalt live — it certifies "this is a real, complete,
  technically serious paper" to an audience that will mostly read the PDF later
  anyway.

## 3. How detailed are they? Very — and deliberately so

Detail is concentrated in method and experiments, which routinely consume 60–70% of
the talk. This inverts the econ/polisci exemplars, where results and the puzzle get
the time and method is compressed to its identifying logic. The ML talk's detail is
partly rational for its setting: the talk is recorded (SlidesLive), the audience
contains the three reviewers of the paper, and the poster session afterwards is
where actual discussion happens. The talk is advertising plus legal record; depth is
for the recording, not the room.

## 4. Why do people tolerate (and even like) these talks?

- **The audience is pre-filtered.** Attendees of a NeurIPS oral already care about
  the problem; the talk doesn't need to sell the question, only locate the
  contribution. Shapiro's "your audience does not care about your topic" is false
  there — which is exactly why the formula survives there and fails elsewhere.
- **Predictability is a feature for specialists.** A formulaic structure lets an
  expert audience skim in real time: they know when the method diagram is coming
  and can re-tune-in after zoning out. Karpathy concedes outline slides earn their
  place in 30+ minute talks for exactly this reason.
- **Hallways and posters carry the real load.** "The real action is in the
  hallways" (Karpathy). The talk's job is to make people visit the poster or read
  the paper — "the primary purpose of a talk is advertising, not science" (Jeff
  Leek, quoted in the World Bank tips).
- **It is a low-variance strategy.** For a nervous PhD student presenting in a
  second language to 2,000 people, the template guarantees a passing grade.
  Formula is risk management.

## 5. Why are they (narrowly) effective — and where they fail

**Effective at:** certifying completeness; transferring technical specifics to the
10 specialists in the room who need them; generating a citable recording; feeding
the poster session.

**Failure modes** (all named by insiders, not outsiders):

- *Bored-then-confused* (Karpathy): too-general first half, too-technical second
  half; the audience learns nothing at either altitude.
- *The laundry list*: "first we do X, then Y, then Z, and here is what we get" —
  enumeration without justification, chronology instead of argument (Karpathy flags
  this as the cardinal paper-writing sin; talks inherit it).
- *The outline slide as spoiler*: "This movie is about a ring of power. In chapter
  one…" (Karpathy) — structure announced instead of story told.
- *Dense result tables as social anesthesia*: Karpathy's empirical test — put up a
  complex table, watch half the audience open their phones.
- *Results rushed at the end*: the most interesting 20% of the content gets the
  last 5% of the time.

## 6. The opposite pole: the Nobel lecture

The Nobel lecture inverts nearly every convention of the contributed talk:

- **Narrative arc of discovery**, not paper structure: where the problem came from,
  the wrong turns, the moment it cracked. Retrospective, personal, "authorial
  voice" — the format explicitly permits it (laureates are "free to implement their
  author's voice," including the look back).
- **One idea, built slowly**, for a general educated audience; equations nearly
  absent; the technical record is delegated entirely to the published work.
- **Significance is the content.** The lecture exists to say why the work matters
  for the field and for society — the thing contributed talks squeeze into one
  bullet under "future work."
- **Time scale**: ~45 minutes, of which the story of *why* often takes half.

Why people love them: they deliver what a formula cannot — a causal story of how
knowledge actually got made, told by the person who made it. They are effective
because memory is narrative: audiences retain stories and meaning, not tables.

The interesting fact for us: the econ/polisci exemplars in `PRESENTATION_PLAN.md`
(Shapiro, La Ferrara, *PS*) sit **much closer to the Nobel pole than to the
ICML pole**, despite being written for 15-minute contributed talks. Puzzle-first,
preview the answer, one diagram for the theory, one figure per claim, own the
limitations, end on one sentence. The cross-field convergence of *good* practice is
real; the boring talk is not "how science presents itself," it is a local
equilibrium of specific venues.

## 7. The cross-examination: what survives contact with our thesis talk

### What the standard format would do to our presentation

| Standard ML/IEEE move | Applied to our thesis | Verdict |
|---|---|---|
| Outline slide | "First motivation, then framework, then data…" | **Reject.** 15 min; Karpathy's spoiler objection applies; the puzzle *is* the map. |
| Related work slide with many citations | V-Dem, Polity, AJR, democratization-growth lit as name list | **Reject.** *PS*: name lists inform no one. One slide, two strands, one line each. |
| Method walked through in full | Coding protocol R1–R6, indicator families, merging steps slide by slide | **Reject in core, keep in backup.** Shapiro's "underwear" rule; the *rule and its credibility* stay (Slide 7), the plumbing goes to B2–B3. |
| Dense results tables | Pasted regression/output tables | **Reject absolutely.** Bar charts and one contrast per slide (La Ferrara, *PS*). |
| Completeness as insurance | Every sensitivity check on core slides | **Reject in core.** Audit trail exists and is cited; sensitivities live in B4. |
| Results rushed at the end | (the failure we must actively avoid) | Our timing table puts ~4 min on results mid-talk plus the preview up front. |

### What we should *steal* from the standard format

1. **The gestalt instinct is legitimate for a defense panel.** A committee, like
   Karpathy's Fei-Fei flipping papers, judges seriousness by visible markers: an
   equation that exists, a coding protocol with explicit rules, source grades, an
   audit trail. We don't put these on core slides, but they must be *one click
   away and visibly numbered* — our B1–B7 backup block is exactly the gestalt,
   relocated. Consider one reassuring line on Slide 8 ("73 episodes, every coding
   decision sourced and audited; details in the appendix slides") that signals the
   record without showing it.
2. **Recorded-talk logic.** If the defense is recorded, slides should be
   self-explanatory enough to survive without voice — a point in favor of
   assertion-style slide titles (already in the plan).
3. **NeurIPS pacing discipline as a check**: one slide per minute as an upper bound
   confirms our 13-slide ceiling for 15 minutes.

### What we steal from the Nobel pole

1. **The story of the puzzle, told causally**: our Slide 2 paired-case figure is
   the discovery narrative in miniature — "the field thought regime change moves
   economies; here are two ruptures that look identical and end opposite."
2. **Significance as content, not coda**: the takeaway slide carries why it matters
   (a replicable event taxonomy replacing contested indices), not "future work" as
   a formality.
3. **Authorial honesty**: Nobel lectures include the wrong turns. Our limitations
   slide does the same at smaller scale — and our preliminary, non-causal status
   makes this mandatory, not optional.

## 8. One-paragraph verdict

The boring conference talk is a *compliance document*: it mirrors the paper to
prove completeness to a pre-filtered audience that will read the PDF anyway. Our
situation is the opposite — a mixed panel, a conceptual contribution that must be
*felt* before it can be *checked*, and preliminary results that require honest
framing. So we keep the standard format's backstage rigor (every claim auditable,
backup slides as gestalt) and the Nobel/econ-exemplar front stage (puzzle, story,
one diagram, one figure per claim, one sentence to remember). The boring talk asks
the audience to trust the process; ours asks them to remember the point — and shows
them where to verify the process if they want to.
