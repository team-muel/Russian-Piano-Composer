# Theme Annotation Schema Specification (v1)

## Overview
This document specifies the formal schema, coordinate system, review state machine, and lineage binding rules for curated theme annotations in the **Russian Piano Composer** repository.

---

## 1. Canonical Coordinate System

Theme boundaries point directly into the RC-007 canonical score representation.

### `ScorePosition`
```yaml
measure_index: <int >= 0>
offset: <exact rational Fraction >= 0>
```
- `measure_index`: Zero-based contiguous index within the canonical score measure array.
- `offset`: Exact rational metric offset inside the measure measured in whole-note fractions (e.g. `0` for bar start, `1/4` for beat 2 in 4/4).

### Half-Open Metric Span $[start, end)$
Theme spans use the strict mathematical convention:
$$\text{ThemeSpan} = [\text{start}, \text{end})$$
- `start` boundary: **Inclusive**.
- `end` boundary: **Exclusive**.

Validation Invariant:
$$\text{end} > \text{start} \quad \text{in global metric time}$$

---

## 2. Review State Machine (`AnnotationStatus`)

| Status | Semantics |
| :--- | :--- |
| `CANDIDATE` | Proposed boundary (human or algorithm). Unreviewed, not trusted. |
| `REVIEWED` | Inspected by a reviewer, but pending final acceptance approval. |
| `ACCEPTED` | Approved for inclusion in research annotation datasets. |
| `DISPUTED` | Qualified reviewers disagree materially on boundaries or thematic role. |
| `REJECTED` | Reviewed and intentionally excluded from thematic status. |
| `STALE` | Invalidation flag triggered when underlying canonical piece SHA-256 changes. |

### Hard Review Rules
1. **No Self-Acceptance**: Proposals with `annotator_type == ALGORITHM_CANDIDATE` can **never** set `status = ACCEPTED` without independent human review approval.
2. **Acceptance Policy**: `ACCEPTED` status requires:
   - `confidence >= 2`
   - At least one `ReviewRecord` with `decision == APPROVE`
   - Valid, non-stale canonical score lineage match.

---

## 3. Confidence Scale

| Confidence | Description | Meaning |
| :---: | :--- | :--- |
| `1` | **Uncertain** | Multiple plausible boundaries or ambiguous thematic status. Preserved in dataset, excluded from research filtering. |
| `2` | **Plausible** | Defensible thematic statement with minor boundary ambiguity. Included in research analysis. |
| `3` | **Clear** | Strong thematic identity, clear cadential/motivic boundaries. Included in research analysis. |

*Decimal pseudo-precision (e.g. 0.85) is strictly forbidden for human annotations.*

---

## 4. Theme Role Taxonomy

- `PRIMARY_THEME`: Main thematic statement / principal melody.
- `SECONDARY_THEME`: Subsidiary thematic material.
- `RECURRING_THEME`: Rondo refrain or recurring thematic subject.
- `MOTTO`: Short head-motive or recurring structural motto.
- `EPISODIC_THEME`: Episode theme in compound/rondo forms.
- `OTHER_THEME`: Distinct thematic statement not fitting above categories.

---

## 5. Provenance & Lineage Binding

Every annotation record stores:
- `manifest_hash`: 64-character SHA-256 hash of `corpus_manifest.yaml`.
- `canonical_piece_hash`: 64-character SHA-256 semantic hash of the `CanonicalScore`.
- `canonical_schema_version`: `1`
- `annotation_schema_version`: `1`

If the canonical piece hash changes, the validator fails closed and marks the annotation `STALE`.

---

## 6. Rights & Generative Isolation

$$\text{Generative Training Eligibility} = \text{ACCEPTED} \land \text{confidence} \ge 2 \land \text{GENERATIVE\_RUSSIAN} \land \text{generative\_eligible}$$

- **Non-Russian Control Themes**: Can be `ACCEPTED` with `confidence = 3`, but can **NEVER** enter generative training.
- **Unapproved Russian Themes**: Themes in corpora with `rights_review_required: true` (all current Russian sources) can enter **Russian Research Analysis**, but can **NEVER** enter generative training selection.
