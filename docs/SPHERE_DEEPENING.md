# Within-Sphere Deepening Events

**Status: PRELIMINARY; plotting only; classification pending.**

## Purpose and analytical boundary

`data_clean/sphere_deepening_events.csv` is a **preliminary, plotting-only annotation layer** for acts that may strengthen, formalize, or institutionalize ties within an existing sphere. The label “deepening” is used for visual exposition and does not constitute a settled analytical classification. In particular, the register does not create new `Entry` episodes or alter the meaning of any existing episode.

The dataset does not feed into `panel_preliminary.csv`, `realignment_event_codings_preliminary.csv`, any Step 5–6 outcome or frequency table, or the hypothesis tests. It is read only by `code/plot_country_timeline.py`, where it appears as a separate visual layer. Existing analysis files and codings remain unchanged. Classification of the expanded register is logged as an open issue in `docs/OPEN_ISSUES.md`.

## Coverage and schema

The register contains 91 records across 59 countries: 44 are explicitly described as deepening, strengthening, tightening, or consolidation in the project record (`classification_status = documented_deepening`), while 47 are formalization, continuation, or re-engagement records plotted provisionally as deepening (`classification_status = provisional_plotting_only`). Five records lack a defensible point year and are retained for documentation but omitted from plots.

Coverage includes the European accessions in `case_notes/EURO_batch_note.md`; Spain's 1963, 1982, and 1986 institutional milestones; the Latin American Rio/OAS institutionalization block and later economic/security deepening; Cuba and Mongolia's CMEA accessions; Japan's treaty revision and Vietnam's WTO accession; and documented post-Soviet successor-institution, basing, and re-engagement events. Events already incorporated into a coded realignment interval are generally not duplicated. Malta and Guyana remain governed by their existing open entry-versus-deepening questions rather than being silently recoded here.

Each row records:

- `analysis_status = preliminary` on every record;
- `deepening_id`: stable identifier prefixed `SD-`;
- `iso3`, `country`, `year`, and `patron`;
- `event` and the affected `indicator_families` (F1 security, F2 economic, F3 institutional);
- `classification = within_sphere_deepening` and `analysis_role = plot_context_only`;
- `classification_status`: `documented_deepening` or `provisional_plotting_only`;
- `source_refs`: existing primary-instrument or dataset references;
- `existing_log`: the project document containing the determination or event record;
- `notes`: scope, dating, and classification qualifications.

A blank `year` means that the documentation does not support a precise plotting date. No midpoint or year is imputed.

## Source basis

The register reuses the project's existing records rather than introducing new treatment decisions:

- **Spain 1963:** US–Spain Defense Agreement, ATOP 3480; `EPISODE_SOURCES` B12 and `case_notes/ESP_1953.md`.
- **Spain 1982:** NATO accession, 30 May 1982; `EPISODE_SOURCES` M1/B32 and `bloc_membership.csv`.
- **EC/EU/EEA accessions:** `EPISODE_SOURCES` M8 and `bloc_membership.csv`; the no-new-entry determinations are in `case_notes/EURO_batch_note.md` under “Convention: deepening is not entry.”
- **CMEA accessions:** `EPISODE_SOURCES` M5, `bloc_membership.csv`, and the Latin America/East Asia batch notes.
- **Latin American institutionalization and deepening:** `case_notes/LATAM_formation_initial_condition.md` and `case_notes/LATAM_batch_note.md`.
- **Post-Soviet continuation and re-engagement:** `case_notes/PostSoviet_batch_note.md` and `bloc_membership.csv`.

The register is descriptive plot context, not evidence that these acts caused a subsequent growth, disruption, or acceleration outcome. Before any use beyond plotting, provisional records require an explicit substantive determination of whether the act strengthened ties or merely continued an existing institutional relationship.
