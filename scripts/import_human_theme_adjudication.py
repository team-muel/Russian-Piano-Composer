"""
CLI tool to validate and import completed human theme adjudication decisions.
Ensures double-blind provenance integrity, validates review packet hash, checks for explicit
human declaration, and builds human-adjudicated ThemeAnnotation records without overwriting AI candidate lineage.
"""
import argparse
import io
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from russian_piano_composer.corpus.theme_annotations import (
    ThemeAnnotationSet,
    accepted_annotations,
    load_theme_annotation_manifest,
)
from russian_piano_composer.domain.annotations import (
    AnnotationStatus,
    AnnotatorType,
    ReviewDecision,
    ReviewerType,
    ReviewRecord,
    ScorePosition,
    ThemeAnnotation,
    ThemeRole,
    ThemeSpan,
    compute_annotation_id,
)

VALID_THEMATIC_DECISIONS = {"YES", "NO", "UNCERTAIN"}
VALID_BOUNDARY_DECISIONS = {"ACCEPT", "CHANGE", "UNCERTAIN"}
VALID_THEME_ROLES = {
    "PRIMARY_THEME",
    "SECONDARY_THEME",
    "RECURRING_THEME",
    "MOTTO",
    "EPISODIC_THEME",
    "OTHER_THEME",
    "UNCERTAIN",
}
VALID_CONFIDENCE_LEVELS = {1, 2, 3}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and import completed human theme adjudication YAML decisions."
    )
    parser.add_argument(
        "--path",
        default="data/annotations/theme_v1/pilots/rc008c/human_review_template_v1.yaml",
        help="Path to completed human decision YAML file.",
    )
    parser.add_argument(
        "--mapping-path",
        default="data/annotations/theme_v1/pilots/rc008c/human_review_mapping_v1.yaml",
        help="Path to human review mapping YAML file.",
    )
    parser.add_argument(
        "--candidates-path",
        default="data/annotations/theme_v1/pilots/rc008b/candidates.yaml",
        help="Path to baseline pilot AI candidate manifest.",
    )
    parser.add_argument(
        "--output-path",
        default="data/annotations/theme_v1/pilots/rc008c/human_adjudicated_v1.yaml",
        help="Output path for imported human-adjudicated annotation set.",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate decision file without writing output.",
    )
    return parser


def validate_human_decision_file(
    decision_data: dict[str, Any],
    mapping_data: dict[str, Any],
) -> tuple[bool, list[str]]:
    errors: list[str] = []

    # 1. Packet Hash Validation
    expected_packet_hash = mapping_data.get("human_review_packet_hash")
    actual_packet_hash = decision_data.get("human_review_packet_hash")
    if actual_packet_hash != expected_packet_hash:
        errors.append(
            f"Packet Hash Mismatch: decision hash '{actual_packet_hash}' != expected '{expected_packet_hash}'"
        )

    # 2. Provenance Validation
    prov = decision_data.get("reviewer_provenance", {})
    reviewer_type = str(prov.get("reviewer_type", "")).upper()
    if reviewer_type not in ("HUMAN", "HUMAN_REVIEWER"):
        errors.append(f"Invalid Reviewer Type: '{prov.get('reviewer_type')}'. Must be HUMAN.")

    reviewer_id = prov.get("reviewer_id")
    if not reviewer_id or not str(reviewer_id).strip():
        errors.append("Missing Reviewer ID: reviewer_id must be a non-empty human identifier string.")

    completed_at = prov.get("review_completed_at")
    if not completed_at:
        errors.append("Missing Timestamp: review_completed_at must be populated.")

    declaration = prov.get("declaration")
    if not declaration or not str(declaration).strip():
        errors.append("Missing Declaration: declaration must explicitly state independent human review.")

    # 3. Candidate Decision Completeness Validation
    candidate_decisions = decision_data.get("candidate_decisions", [])
    if not candidate_decisions:
        errors.append("Empty Decisions: No candidate decisions found in template.")

    mappings_by_h_id = {m["review_id"]: m for m in mapping_data.get("mappings", [])}

    for dec in candidate_decisions:
        h_id = dec.get("review_id")
        if h_id not in mappings_by_h_id:
            errors.append(f"Unknown Review ID: '{h_id}' not found in mapping artifact.")
            continue

        d = dec.get("decision", {})
        is_them = d.get("is_thematic_statement")
        if is_them is None or is_them not in VALID_THEMATIC_DECISIONS:
            errors.append(f"[{h_id}] Invalid or missing is_thematic_statement: '{is_them}'")

        sb = d.get("start_boundary")
        if sb is None or sb not in VALID_BOUNDARY_DECISIONS:
            errors.append(f"[{h_id}] Invalid or missing start_boundary: '{sb}'")
        elif sb == "CHANGE":
            rev_start = d.get("revised_start_measure")
            if rev_start is None or not isinstance(rev_start, int) or rev_start < 0:
                errors.append(f"[{h_id}] Invalid revised_start_measure for CHANGE: '{rev_start}'")

        eb = d.get("end_boundary")
        if eb is None or eb not in VALID_BOUNDARY_DECISIONS:
            errors.append(f"[{h_id}] Invalid or missing end_boundary: '{eb}'")
        elif eb == "CHANGE":
            rev_end = d.get("revised_end_measure")
            if rev_end is None or not isinstance(rev_end, int) or rev_end <= 0:
                errors.append(f"[{h_id}] Invalid revised_end_measure for CHANGE: '{rev_end}'")

        role = d.get("theme_role")
        if role is None or role not in VALID_THEME_ROLES:
            errors.append(f"[{h_id}] Invalid or missing theme_role: '{role}'")

        conf = d.get("confidence")
        if conf is None or conf not in VALID_CONFIDENCE_LEVELS:
            errors.append(f"[{h_id}] Invalid or missing confidence: '{conf}'")

    return (len(errors) == 0, errors)


def process_adjudicated_annotations(
    decision_data: dict[str, Any],
    mapping_data: dict[str, Any],
    baseline_manifest: ThemeAnnotationSet,
) -> ThemeAnnotationSet:

    prov = decision_data["reviewer_provenance"]
    reviewer_id = str(prov["reviewer_id"])
    mappings_by_cand = {m["candidate_id"]: m for m in mapping_data["mappings"]}
    decisions_by_h = {d["review_id"]: d for d in decision_data["candidate_decisions"]}

    updated_annotations: list[ThemeAnnotation] = []

    for orig_ann in baseline_manifest.annotations:
        cand_id = orig_ann.annotation_id
        if cand_id not in mappings_by_cand:
            updated_annotations.append(orig_ann)
            continue

        mapping_rec = mappings_by_cand[cand_id]
        h_id = mapping_rec["review_id"]
        user_dec = decisions_by_h[h_id]
        d = user_dec["decision"]

        is_them = d["is_thematic_statement"]
        start_dec = d["start_boundary"]
        end_dec = d["end_boundary"]
        user_role = ThemeRole(d["theme_role"]) if d["theme_role"] != "UNCERTAIN" else ThemeRole.PRIMARY_THEME
        user_conf = int(d["confidence"])

        # Resolve start position
        if start_dec == "CHANGE" and d.get("revised_start_measure") is not None:
            start_pos = ScorePosition(measure_index=int(d["revised_start_measure"]), offset=str(d.get("revised_start_offset", "0")))
        else:
            start_pos = orig_ann.span.start

        # Resolve end position
        if end_dec == "CHANGE" and d.get("revised_end_measure") is not None:
            end_pos = ScorePosition(measure_index=int(d["revised_end_measure"]), offset=str(d.get("revised_end_offset", "0")))
        else:
            end_pos = orig_ann.span.end

        new_span = ThemeSpan(start=start_pos, end=end_pos)

        # Status resolution
        if is_them == "YES" and user_conf >= 2:
            new_status = AnnotationStatus.ACCEPTED
        elif is_them == "NO":
            new_status = AnnotationStatus.REJECTED
        else:
            new_status = AnnotationStatus.REVIEWED

        # Build human review record
        human_review = ReviewRecord(
            reviewer_id=reviewer_id,
            reviewer_type=ReviewerType.SECOND_HUMAN_REVIEW,
            decision=ReviewDecision.APPROVE if is_them == "YES" else (ReviewDecision.DISAGREE if is_them == "NO" else ReviewDecision.REQUEST_CHANGE),
            boundary_assessment=f"Human start={start_dec}, end={end_dec}.",
            role_assessment=f"Human role choice: {user_role.value}.",
            confidence_assessment=f"Human confidence level {user_conf}.",
            notes=str(d.get("notes") or "Genuine human adjudication."),
        )

        # If boundaries or role changed, create a child annotation linked to parent candidate
        is_boundary_revised = (start_dec == "CHANGE") or (end_dec == "CHANGE")
        is_role_revised = (user_role != orig_ann.theme_role)

        if is_boundary_revised or is_role_revised:
            new_ann_id = compute_annotation_id(orig_ann.piece_id, new_span, user_role)
            adj_ann = ThemeAnnotation(
                annotation_id=new_ann_id,
                piece_id=orig_ann.piece_id,
                corpus_id=orig_ann.corpus_id,
                score_entry_id=orig_ann.score_entry_id,
                span=new_span,
                theme_role=user_role,
                confidence=user_conf,
                status=new_status,
                annotator_id=reviewer_id,
                annotator_type=AnnotatorType.HUMAN,
                reviews=tuple([*orig_ann.reviews, human_review]),
                evidence_tags=orig_ann.evidence_tags,
                rationale=f"Human-revised theme annotation (parent: {orig_ann.annotation_id}).",
                manifest_hash=orig_ann.manifest_hash,
                canonical_piece_hash=orig_ann.canonical_piece_hash,
                canonical_schema_version=orig_ann.canonical_schema_version,
                annotation_schema_version=orig_ann.annotation_schema_version,
            )
            # Preserve original candidate in set, add revised interpretation
            updated_annotations.append(orig_ann)
            updated_annotations.append(adj_ann)
        else:
            # Update candidate status and append human review without altering AI records
            existing_reviews = list(orig_ann.reviews)
            updated_ann = ThemeAnnotation(
                annotation_id=orig_ann.annotation_id,
                piece_id=orig_ann.piece_id,
                corpus_id=orig_ann.corpus_id,
                score_entry_id=orig_ann.score_entry_id,
                span=orig_ann.span,
                theme_role=user_role,
                confidence=user_conf,
                status=new_status,
                annotator_id=orig_ann.annotator_id,
                annotator_type=orig_ann.annotator_type,
                reviews=tuple([*existing_reviews, human_review]),
                evidence_tags=orig_ann.evidence_tags,
                rationale=orig_ann.rationale,
                manifest_hash=orig_ann.manifest_hash,
                canonical_piece_hash=orig_ann.canonical_piece_hash,
                canonical_schema_version=orig_ann.canonical_schema_version,
                annotation_schema_version=orig_ann.annotation_schema_version,
            )
            updated_annotations.append(updated_ann)

    return ThemeAnnotationSet(
        annotation_schema_version=baseline_manifest.annotation_schema_version,
        canonical_schema_version=baseline_manifest.canonical_schema_version,
        manifest_hash=baseline_manifest.manifest_hash,
        piece_records=baseline_manifest.piece_records,
        annotations=tuple(updated_annotations),
    )


def save_adjudicated_manifest(manifest: ThemeAnnotationSet, output_path: Path) -> None:
    human_accepted = len(accepted_annotations(manifest))
    dict_repr = {
        "annotation_schema_version": manifest.annotation_schema_version,
        "canonical_schema_version": manifest.canonical_schema_version,
        "corpus_manifest_hash": manifest.manifest_hash,
        "human_accepted_count": human_accepted,
        "annotations": [
            {
                "annotation_id": a.annotation_id,
                "piece_id": a.piece_id,
                "corpus_id": a.corpus_id,
                "score_entry_id": a.score_entry_id,
                "span": {
                    "start": {"measure_index": a.span.start.measure_index, "offset": str(a.span.start.offset)},
                    "end": {"measure_index": a.span.end.measure_index, "offset": str(a.span.end.offset)},
                },
                "theme_role": a.theme_role.value,
                "confidence": a.confidence,
                "status": a.status.value,
                "annotator_id": a.annotator_id,
                "annotator_type": a.annotator_type.value,
                "reviews": [
                    {
                        "reviewer_id": r.reviewer_id,
                        "reviewer_type": r.reviewer_type.value,
                        "decision": r.decision.value,
                        "boundary_assessment": r.boundary_assessment,
                        "role_assessment": r.role_assessment,
                        "confidence_assessment": r.confidence_assessment,
                        "notes": r.notes,
                    }
                    for r in a.reviews
                ],
                "evidence_tags": [t.value for t in a.evidence_tags],
                "rationale": a.rationale,
                "manifest_hash": a.manifest_hash,
                "canonical_piece_hash": a.canonical_piece_hash,
                "canonical_schema_version": a.canonical_schema_version,
                "annotation_schema_version": a.annotation_schema_version,
            }
            for a in manifest.annotations
        ],
    }
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(dict_repr, f, sort_keys=False, default_flow_style=False)


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args()

    decision_path = Path(args.path)
    mapping_path = Path(args.mapping_path)
    candidates_path = Path(args.candidates_path)

    if not decision_path.exists():
        print(f"Error: Decision file not found: {decision_path}", file=sys.stderr)
        return 1

    if not mapping_path.exists():
        print(f"Error: Mapping file not found: {mapping_path}", file=sys.stderr)
        return 1

    if not candidates_path.exists():
        print(f"Error: Candidates file not found: {candidates_path}", file=sys.stderr)
        return 1

    with open(decision_path, encoding="utf-8") as f:
        decision_data = yaml.safe_load(f)

    with open(mapping_path, encoding="utf-8") as f:
        mapping_data = yaml.safe_load(f)

    valid, errors = validate_human_decision_file(decision_data, mapping_data)

    print("=" * 70)
    print("HUMAN ADJUDICATION DECISION IMPORT REPORT")
    print("=" * 70)
    print(f"Decision File:        {decision_path}")
    print(f"Mapping File:         {mapping_path}")
    print(f"Validation Status:    {'SUCCESS' if valid else 'FAILED'}")
    print("-" * 70)

    if not valid:
        print("Validation Errors Found:")
        for err in errors:
            print(f"  - {err}")
        print("=" * 70)
        return 1

    print("Validation SUCCESS: Human decision file satisfies all provenance and completeness rules.")

    if args.check_only:
        print("Check-only mode requested. No output file written.")
        print("=" * 70)
        return 0

    baseline_manifest = load_theme_annotation_manifest(candidates_path)
    adjudicated_set = process_adjudicated_annotations(decision_data, mapping_data, baseline_manifest)

    output_path = Path(args.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_adjudicated_manifest(adjudicated_set, output_path)

    accepted_cnt = len(accepted_annotations(adjudicated_set))
    print(f"Imported Adjudicated Manifest Saved: {output_path}")
    print(f"Human Accepted Count:               {accepted_cnt}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
