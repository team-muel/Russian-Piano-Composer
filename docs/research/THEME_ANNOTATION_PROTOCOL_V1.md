# Theme Annotation Protocol (v1)

## Purpose
This protocol provides step-by-step instructions for musicological reviewers annotating themes in the **Russian Piano Composer** corpus.

---

## Protocol Rules & Guidelines

### Step 1: Inspect Full Score Context
- Do not annotate a theme from an isolated 2-bar snippet.
- Review surrounding structural context to establish presentation, continuation, return, development, and cadential articulation.

### Step 2: Evaluate Thematic Status
- Determine whether the material functions as a recognizable thematic statement.
- Consider identity, recurrence, phrase organization, texture, and salience.
- **Rule**: Do not mark a passage thematic merely because it satisfies a hand-coded checklist or is memorable.

### Step 3: Determine Start Boundary ($start$)
- Place the start boundary at the onset of the thematic statement.
- Pickups / anacrusis belong to the theme when integral to its motivic identity.
- Record start as `measure_index` and exact rational `offset` in whole-note fractions.

### Step 4: Determine End Boundary ($end$)
- Place the end boundary at the conclusion of the thematic statement.
- **Flexibility Rule**: Historical themes MUST NOT be artificially truncated to 2–4 bars. Annotate the full defensible phrase (whether 2, 4, 8, 12 bars or an irregular phrase).
- The span is half-open $[start, end)$.

### Step 5: Assign Role & Confidence
- Select `theme_role` from the taxonomy.
- Assign `confidence`:
  - `1` (Uncertain): Ambiguous boundaries or competing interpretations.
  - `2` (Plausible): Defensible statement with minor ambiguity.
  - `3` (Clear): Strong structural and cadential boundaries.

### Step 6: Document Evidence
- Attach structured `evidence_tags` (e.g. `INITIAL_PRESENTATION`, `RECURRENCE`, `CADENTIAL_ARTICULATION`).
- Include concise rationale text (do not store copyrighted note sequences).

### Step 7: Perform Review
- An independent reviewer must evaluate boundary defensibility, role, and confidence.
- Approve (`APPROVE`), request changes (`REQUEST_CHANGE`), or disagree (`DISAGREE`).

### Step 8: Handle Control Corpora
- Annotate Chopin, Liszt, and Schumann control corpora using the exact same standard as Russian corpora.
- Control themes provide critical comparative benchmarks.

---

## Negative Result Protocol
If a piece or region contains no clear defensible thematic statement after thorough inspection:
- Record a `PieceAnnotationRecord` with status `NO_CLEAR_THEME`.
- Do not force fake annotations.
