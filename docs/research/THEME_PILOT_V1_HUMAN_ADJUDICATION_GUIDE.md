# RC-008C — Human Theme Adjudication Musicological Guide

## Purpose & Scope

This guide defines the scientific standards and musicological criteria for human adjudication of candidate theme boundaries in the **Russian Piano Composer** research project.

The pilot candidate dataset contains 20 candidate theme spans across 18 solo piano works. Every candidate span requires independent human evaluation before it can be admitted as ground truth.

---

## 1. What Defines a "Theme"?

In this project, a **Theme** is defined as a salient, structurally significant musical unit characterized by:

1. **Melodic / Rhythmic Identity**: A distinct profile in pitch contour, rhythm, and articulation that serves as a recognizable thematic gesture or subject.
2. **Structural Presentation**: Initial statement (antecedent/consequent, period, sentence, or motto) or formal recurrence within the movement.
3. **Harmonic / Cadential Closure**: Metric articulation or cadential arrival defining phrase completeness.

---

## 2. Theme Roles Taxonomy

Reviewers must assign exactly one of the following roles to approved themes:

- `PRIMARY_THEME`: Main thematic group or principal theme of the piece/movement (e.g. principal theme in sonata form, main melody of a mazurka or tale).
- `SECONDARY_THEME`: Contrasting thematic group (e.g. secondary theme in sonata form, contrasting B-section theme).
- `RECURRING_THEME`: Theme that recurs periodically throughout the work (e.g. rondo refrain, ritornello).
- `MOTTO`: A short, striking thematic motif or fanfare that recurs as a unifying signifier (e.g. opening storm motif in Liszt *Orage*).
- `EPISODIC_THEME`: Theme appearing within a distinct episode or middle section that does not serve as primary or secondary theme.
- `OTHER_THEME`: A thematic statement that does not fit the above categories.
- `UNCERTAIN`: Role cannot be definitively assigned.

---

## 3. Half-Open Interval Boundary Convention

All measure spans use **half-open metric notation** $[start, end)$:

- `start`: Measure index and offset where the theme begins (inclusive). Measure `0` denotes the first measure (or pickup measure if designated).
- `end`: Measure index and offset where the theme ends (exclusive). For example, a 16-bar theme spanning measures 0 to 15 ends at measure `16`, offset `0`.

### Boundary Revision Guidelines

If you decide that the theme boundary is incorrect:
1. Select `CHANGE` for Start or End boundary.
2. Provide the exact revised measure index and offset.
3. Common boundary corrections include excluding introductory pickup flourishes, excluding post-cadential extensions, or trimming phrase continuations.

---

## 4. Confidence Scale Definitions

- `3` (**High Confidence**): Boundary is unambiguous, supported by metric alignment, clear cadential arrival, and textural separation.
- `2` (**Moderate Confidence**): Plausible thematic boundary with minor ambiguity (e.g. elided cadence, overlapping counterpoint).
- `1` (**Low Confidence**): Speculative boundary where phrase boundaries are highly ambiguous or diffuse.

---

## 5. Special Repertoire Adjudication Guidelines

### A. Rachmaninoff Op. 42 (Variations on a Theme of Corelli)
- Selections in the pilot are variation statements.
- **Key Question**: Is the candidate span a standalone thematic statement, or is it a variation-level realization of the underlying Corelli theme?
- Evaluate whether thematic identity occupies the entire encoded variation or only a smaller structural region. Do not automatically treat an entire variation as a theme span if only a core melodic motif is thematic.

### B. Liszt *Orage* (Op. 160 No. 5)
- Distinguish between a virtuosic **MOTTO** (opening chromatic octave motif) and a broader **SECONDARY_THEME**.

### C. Medtner *Tales* (Skazki)
- Pay attention to polyphonic textures and imitative counterpoint. Ensure boundaries capture the complete thematic statement rather than stopping at the first imitative entry.

---

## 6. Diagnostic Questions

### Opening-Bias Question
For candidates starting at measure 0:
*Would you still call this passage thematic if it were not the opening of the piece?*
This diagnostic tests whether opening placement creates an artificial bias toward calling a passage a primary theme.

### Full-Span Continuation Question
For candidates spanning 12 or 16 measures:
*Does the full candidate span represent one thematic statement, or does it include continuation/development beyond the thematic core?*
Select whether the entire span is a single theme, whether the theme is shorter, or whether it comprises multiple distinct units.

---

## 7. Submission

Record all decisions in `data/annotations/theme_v1/pilots/rc008c/human_review_template_v1.yaml`.
Ensure `reviewer_id` and `declaration` are completed prior to importing.
