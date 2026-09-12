"""
Script to prepare RC-008C double-blind human theme adjudication packets.
Generates deterministic blinded review order (H001..H020), blank decision template,
anonymous ID mapping, reviewer guide, and human review form.
"""
import hashlib
import io
import shutil
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.corpus.theme_annotations import load_theme_annotation_manifest

PROTOCOL_VERSION = "1"
PILOT_SELECTION_HASH = "d7d718e0ae44256ced833944c396cb216fc5ec1b252cf7effd13e9f99a78b936"
PILOT_CANDIDATE_HASH = "1b7c3255e19465d3f9c79a69cb350afa447edf1b31260dd4f6fa420c86f0163c"


def derive_candidate_digest(pilot_selection_hash: str, protocol_version: str, candidate_id: str) -> str:
    seed = f"{pilot_selection_hash}:{protocol_version}:{candidate_id}".encode()
    return hashlib.sha256(seed).hexdigest()


def compute_human_review_packet_hash(
    protocol_version: str,
    candidate_set_hash: str,
    mapping_records: list[dict[str, Any]],
) -> str:
    items_str = ";".join(
        f"{r['review_id']}={r['candidate_id']}:{r['piece_id']}"
        for r in mapping_records
    )
    payload = f"protocol={protocol_version}|candidate_set_hash={candidate_set_hash}|items={items_str}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def probe_musescore() -> str | None:
    executables = [
        "mscore",
        "musescore",
        "MuseScore3",
        "MuseScore4",
        "MuseScore 3",
        "MuseScore 4",
        "MuseScore Studio",
    ]
    for exe in executables:
        path = shutil.which(exe)
        if path:
            return path
    # Windows standard installation paths
    win_paths = [
        r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe",
        r"C:\Program Files\MuseScore 3\bin\MuseScore3.exe",
        r"C:\Program Files (x86)\MuseScore 3\bin\MuseScore3.exe",
    ]
    for p in win_paths:
        if Path(p).exists():
            return p
    return None


def get_piece_metadata(corpus_manifest: Any, corpus_id: str, score_entry_id: str) -> dict[str, Any]:
    interim_base = Path("data/interim/canonical") / corpus_manifest.compute_manifest_hash()
    corpus_dir = interim_base / corpus_id
    piece_id = f"{corpus_id}:{score_entry_id}"

    metadata = {
        "total_measures": 0,
        "meter": "3/4",
        "source_score_path": f"data/raw/corpora/{corpus_id}/{score_entry_id}.mscx",
    }

    if corpus_dir.exists():
        df_measures = pd.read_parquet(corpus_dir / "measures.parquet")
        p_measures = df_measures[df_measures["piece_id"] == piece_id]
        if not p_measures.empty:
            metadata["total_measures"] = len(p_measures)
            first_m = p_measures.sort_values("measure_index").iloc[0]
            num = int(first_m["meter_numerator"])
            den = int(first_m["meter_denominator"])
            metadata["meter"] = f"{num}/{den}"

    return metadata


def build_blank_template(
    packet_hash: str,
    mapping_records: list[dict[str, Any]],
) -> dict[str, Any]:
    # Group by piece_id for piece-level missing theme questions
    piece_ids_seen = set()
    piece_records = []
    for r in mapping_records:
        pid = r["piece_id"]
        if pid not in piece_ids_seen:
            piece_ids_seen.add(pid)
            piece_records.append({
                "piece_id": pid,
                "missing_thematic_statement": None,  # YES / NO / UNCERTAIN
                "missing_theme_measure_range": None,
                "notes": None,
            })

    candidate_decisions = []
    for r in mapping_records:
        dec = {
            "review_id": r["review_id"],
            "candidate_id": r["candidate_id"],
            "piece_id": r["piece_id"],
            "span_start": {
                "measure_index": r["span_start_measure"],
                "offset": "0",
            },
            "span_end": {
                "measure_index": r["span_end_measure"],
                "offset": "0",
            },
            "decision": {
                "is_thematic_statement": None,  # YES / NO / UNCERTAIN
                "start_boundary": None,        # ACCEPT / CHANGE / UNCERTAIN
                "revised_start_measure": None,
                "revised_start_offset": None,
                "end_boundary": None,          # ACCEPT / CHANGE / UNCERTAIN
                "revised_end_measure": None,
                "revised_end_offset": None,
                "theme_role": None,            # PRIMARY_THEME, SECONDARY_THEME, RECURRING_THEME, MOTTO, EPISODIC_THEME, OTHER_THEME, UNCERTAIN
                "confidence": None,            # 1, 2, 3
                "notes": None,
            },
            "diagnostics": {
                "opening_bias_question": None,  # YES / NO / UNCERTAIN
                "full_span_question": None,    # ENTIRE_SPAN_IS_THEME / THEME_IS_SHORTER / MULTIPLE_UNITS / UNCERTAIN
            },
        }
        candidate_decisions.append(dec)

    return {
        "human_review_schema_version": 1,
        "protocol_version": int(PROTOCOL_VERSION),
        "pilot_candidate_annotation_hash": PILOT_CANDIDATE_HASH,
        "human_review_packet_hash": packet_hash,
        "role_blind": True,
        "ai_verdict_blind": True,
        "reviewer_provenance": {
            "reviewer_id": None,
            "reviewer_type": "HUMAN",
            "review_completed_at": None,
            "declaration": None,
        },
        "piece_evaluations": piece_records,
        "candidate_decisions": candidate_decisions,
    }


def generate_human_review_form(
    packet_hash: str,
    mapping_records: list[dict[str, Any]],
    musescore_path: str | None,
) -> str:
    lines = [
        "# RC-008C Blinded Human Theme Adjudication Form",
        "",
        "## Review Metadata",
        f"- **Protocol Version**: `{PROTOCOL_VERSION}`",
        f"- **Pilot Candidate Annotation Hash**: `{PILOT_CANDIDATE_HASH}`",
        f"- **Human Review Packet Hash**: `{packet_hash}`",
        "- **Role Blindness**: `ACTIVE` (Corpus group and role labels hidden)",
        "- **AI Verdict Blindness**: `ACTIVE` (Pass-A/Pass-B proposals, AI confidence, and rationale hidden)",
        f"- **Score Rendering Engine**: `{musescore_path or 'NOT AVAILABLE (Locators provided below)'}`",
        "",
        "---",
        "",
        "## Review Instructions",
        "1. For each item `H001` .. `H020`, inspect the score at the indicated measure range.",
        "2. Evaluate whether the candidate represents a thematic statement, whether boundaries are exact, and assign a theme role and confidence level.",
        "3. Complete diagnostic questions for opening themes (m.0) and full-span themes (12 or 16 bars).",
        "4. Record piece-level evaluation: note if any major thematic statement was omitted from the candidate set.",
        "5. Save your completed choices into `data/annotations/theme_v1/pilots/rc008c/human_review_template_v1.yaml`.",
        "",
        "---",
        "",
        "## Candidate Review Items",
        "",
    ]

    for r in mapping_records:
        m_start = r["span_start_measure"]
        m_end = r["span_end_measure"]
        m_len = r["span_length"]
        total_m = r["total_measures"]
        meter = r["meter"]
        h_id = r["review_id"]
        score_path = r["source_score_path"]

        lines.extend([
            f"### Item `{h_id}`",
            f"- **Score Location**: `{r['score_entry_id']}` ([source score](file:///{score_path}))",
            f"- **Candidate Metric Span**: Measures `{m_start}` to `{m_end}` (Duration: {m_len} measures, Time Signature: {meter})",
            f"- **Piece Total Length**: {total_m} measures",
            f"- **Score Context Window**: Measures `max(0, {m_start}-8)` ({max(0, m_start-8)}) to `{min(total_m, m_end+8)}`",
            "",
            "#### 1. Thematic Judgment",
            "**Is this a thematic statement?**",
            "- [ ] `YES`",
            "- [ ] `NO`",
            "- [ ] `UNCERTAIN`",
            "",
            "#### 2. Boundary Assessment",
            f"**Start Boundary (Current: Measure {m_start}, offset 0)**:",
            "- [ ] `ACCEPT`",
            "- [ ] `CHANGE` (Specify Measure: ____, Offset: ____)",
            "- [ ] `UNCERTAIN`",
            "",
            f"**End Boundary (Current: Measure {m_end}, offset 0)**:",
            "- [ ] `ACCEPT`",
            "- [ ] `CHANGE` (Specify Measure: ____, Offset: ____)",
            "- [ ] `UNCERTAIN`",
            "",
            "#### 3. Theme Role Selection",
            "Select one role:",
            "- [ ] `PRIMARY_THEME`",
            "- [ ] `SECONDARY_THEME`",
            "- [ ] `RECURRING_THEME`",
            "- [ ] `MOTTO`",
            "- [ ] `EPISODIC_THEME`",
            "- [ ] `OTHER_THEME`",
            "- [ ] `UNCERTAIN`",
            "",
            "#### 4. Confidence Level",
            "- [ ] `3` (High confidence: clear metric, cadential, and textural boundaries)",
            "- [ ] `2` (Moderate confidence: plausible theme with minor boundary ambiguity)",
            "- [ ] `1` (Low confidence: speculative boundary)",
            "",
        ])

        if m_start == 0:
            lines.extend([
                "#### Diagnostic: Opening-Bias Question",
                "**Would you still call this passage thematic if it were not the opening of the piece?**",
                "- [ ] `YES`",
                "- [ ] `NO`",
                "- [ ] `UNCERTAIN`",
                "",
            ])

        if m_len in (12, 16):
            lines.extend([
                "#### Diagnostic: Full-Span Continuation Question",
                "**Does the full candidate span represent one thematic statement, or does it include continuation/development beyond the thematic core?**",
                "- [ ] `ENTIRE_SPAN_IS_THEME`",
                "- [ ] `THEME_IS_SHORTER`",
                "- [ ] `MULTIPLE_UNITS`",
                "- [ ] `UNCERTAIN`",
                "",
            ])

        lines.extend([
            "**Optional Notes**:",
            "```text",
            "",
            "```",
            "",
            "---",
            "",
        ])

    lines.extend([
        "## Piece-Level Comprehensive Evaluations",
        "For each of the 18 pilot pieces, evaluate whether important thematic material was omitted:",
        "",
    ])

    seen_pieces = set()
    for r in mapping_records:
        pid = r["piece_id"]
        if pid in seen_pieces:
            continue
        seen_pieces.add(pid)
        lines.extend([
            f"### Piece `{pid}`",
            "**Does this piece contain another important thematic statement not represented in the candidate set?**",
            "- [ ] `YES` (Approximate measure range: ____)",
            "- [ ] `NO`",
            "- [ ] `UNCERTAIN`",
            "",
        ])

    return "\n".join(lines)


def generate_human_adjudication_guide() -> str:
    return """# RC-008C — Human Theme Adjudication Musicological Guide

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
"""


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    repo_root = Path(__file__).resolve().parent.parent
    corpus_manifest_path = repo_root / "data/manifests/corpus_manifest.yaml"
    corpus_manifest = load_manifest(corpus_manifest_path)

    candidates_path = repo_root / "data/annotations/theme_v1/pilots/rc008b/candidates.yaml"
    annotation_set = load_theme_annotation_manifest(candidates_path)

    print("=" * 70)
    print("RC-008C PREPARE BLINDED HUMAN REVIEW PACKET")
    print("=" * 70)
    print(f"Loaded {len(annotation_set.annotations)} candidate annotations.")

    # 1. Deterministic Blinded Review Order
    items = []
    for ann in annotation_set.annotations:
        digest = derive_candidate_digest(PILOT_SELECTION_HASH, PROTOCOL_VERSION, ann.annotation_id)
        items.append({
            "digest": digest,
            "annotation": ann,
        })

    # Sort by digest deterministically
    items.sort(key=lambda x: x["digest"])

    mapping_records = []
    for idx, item in enumerate(items, start=1):
        ann = item["annotation"]
        review_id = f"H{idx:03d}"
        piece_meta = get_piece_metadata(corpus_manifest, ann.corpus_id, ann.score_entry_id)

        m_start = ann.span.start.measure_index
        m_end = ann.span.end.measure_index
        m_len = m_end - m_start

        rec = {
            "review_id": review_id,
            "candidate_id": ann.annotation_id,
            "piece_id": ann.piece_id,
            "corpus_id": ann.corpus_id,
            "score_entry_id": ann.score_entry_id,
            "span_start_measure": m_start,
            "span_end_measure": m_end,
            "span_length": m_len,
            "total_measures": piece_meta["total_measures"],
            "meter": piece_meta["meter"],
            "source_score_path": piece_meta["source_score_path"],
            "digest": item["digest"],
        }
        mapping_records.append(rec)

    # Compute human review packet hash
    packet_hash = compute_human_review_packet_hash(PROTOCOL_VERSION, PILOT_CANDIDATE_HASH, mapping_records)
    print(f"Computed Human Review Packet Hash: {packet_hash}")

    # Probe MuseScore
    musescore_path = probe_musescore()
    if musescore_path:
        print(f"Score Rendering Probe: Available ({musescore_path})")
    else:
        print("Score Rendering Probe: Not available (no MuseScore binary found in PATH or standard system paths)")

    # 2. Output Paths
    out_dir = repo_root / "data/annotations/theme_v1/pilots/rc008c"
    out_dir.mkdir(parents=True, exist_ok=True)

    template_path = out_dir / "human_review_template_v1.yaml"
    mapping_path = out_dir / "human_review_mapping_v1.yaml"
    guide_path = repo_root / "docs/research/THEME_PILOT_V1_HUMAN_ADJUDICATION_GUIDE.md"
    form_path = repo_root / "docs/research/THEME_PILOT_V1_HUMAN_REVIEW_FORM.md"

    # Write blank template YAML
    blank_data = build_blank_template(packet_hash, mapping_records)
    with open(template_path, "w", encoding="utf-8") as f:
        yaml.dump(blank_data, f, sort_keys=False, default_flow_style=False)
    print(f"Wrote Blank Template:  {template_path}")

    # Write mapping YAML
    mapping_data = {
        "human_review_schema_version": 1,
        "protocol_version": int(PROTOCOL_VERSION),
        "pilot_selection_hash": PILOT_SELECTION_HASH,
        "pilot_candidate_annotation_hash": PILOT_CANDIDATE_HASH,
        "human_review_packet_hash": packet_hash,
        "role_blind": True,
        "ai_verdict_blind": True,
        "mappings": mapping_records,
    }
    with open(mapping_path, "w", encoding="utf-8") as f:
        yaml.dump(mapping_data, f, sort_keys=False, default_flow_style=False)
    print(f"Wrote Mapping Artifact:{mapping_path}")

    # Write guide MD
    guide_content = generate_human_adjudication_guide()
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(guide_content)
    print(f"Wrote Adjudication Guide:{guide_path}")

    # Write form MD
    form_content = generate_human_review_form(packet_hash, mapping_records, musescore_path)
    with open(form_path, "w", encoding="utf-8") as f:
        f.write(form_content)
    print(f"Wrote Human Review Form: {form_path}")

    # Optional local score index directory if rendering is available
    if musescore_path:
        interim_review_dir = repo_root / "data/interim/theme_human_review" / packet_hash
        interim_review_dir.mkdir(parents=True, exist_ok=True)
        index_html = interim_review_dir / "index.html"
        html_lines = ["<!DOCTYPE html><html><head><title>Theme Review Index</title></head><body>"]
        html_lines.append(f"<h1>Human Review Index ({packet_hash[:12]})</h1><ul>")
        for r in mapping_records:
            html_lines.append(f"<li><b>{r['review_id']}</b>: {r['piece_id']} (m.{r['span_start_measure']}-{r['span_end_measure']})</li>")
        html_lines.append("</ul></body></html>")
        with open(index_html, "w", encoding="utf-8") as f:
            f.write("\n".join(html_lines))
        print(f"Generated Local Index:  {index_html}")

    print("-" * 70)
    print("Prepare Blind Human Review Packet SUCCESS.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
