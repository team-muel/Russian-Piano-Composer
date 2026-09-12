"""
CLI summary tool to summarize human theme adjudication status and statistics.
Reports candidates reviewed, accepted, rejected, uncertain, boundary revisions,
role revisions, confidence revisions, and missing secondary theme flags.
"""
import argparse
import io
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from russian_piano_composer.corpus.theme_annotations import load_theme_annotation_manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize human theme adjudication status and statistics."
    )
    parser.add_argument(
        "--decision-path",
        default="data/annotations/theme_v1/pilots/rc008c/human_review_template_v1.yaml",
        help="Path to human decision template or completed decision file.",
    )
    parser.add_argument(
        "--adjudicated-manifest",
        default=None,
        help="Optional path to imported human-adjudicated manifest YAML.",
    )
    return parser


def main() -> int:
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args()

    decision_path = Path(args.decision_path)
    if not decision_path.exists():
        print(f"Error: Decision file not found: {decision_path}", file=sys.stderr)
        return 1

    with open(decision_path, encoding="utf-8") as f:
        decision_data = yaml.safe_load(f)

    prov = decision_data.get("reviewer_provenance", {})
    candidate_decisions = decision_data.get("candidate_decisions", [])
    piece_evaluations = decision_data.get("piece_evaluations", [])

    total_candidates = len(candidate_decisions)
    completed_decisions = 0
    accepted_count = 0
    rejected_count = 0
    uncertain_count = 0

    start_revisions = 0
    end_revisions = 0
    role_revisions = 0

    for dec in candidate_decisions:
        d = dec.get("decision", {})
        is_them = d.get("is_thematic_statement")
        if is_them is not None:
            completed_decisions += 1
            if is_them == "YES":
                accepted_count += 1
            elif is_them == "NO":
                rejected_count += 1
            else:
                uncertain_count += 1

        if d.get("start_boundary") == "CHANGE":
            start_revisions += 1
        if d.get("end_boundary") == "CHANGE":
            end_revisions += 1
        if d.get("theme_role") is not None:
            role_revisions += 1

    missing_themes_reported = 0
    for pe in piece_evaluations:
        if pe.get("missing_thematic_statement") == "YES":
            missing_themes_reported += 1

    print("=" * 70)
    print("HUMAN THEME ADJUDICATION SUMMARY REPORT")
    print("=" * 70)
    print(f"Decision File:                {decision_path}")
    print(f"Reviewer Provenance Type:     {prov.get('reviewer_type')}")
    print(f"Reviewer ID:                  {prov.get('reviewer_id') or 'UNASSIGNED (Blank Template)'}")
    print(f"Review Completed At:          {prov.get('review_completed_at') or 'PENDING'}")
    print(f"Role Blindness Active:        {decision_data.get('role_blind')}")
    print(f"AI Verdict Blindness Active:  {decision_data.get('ai_verdict_blind')}")
    print("-" * 70)
    print(f"Total Candidates:             {total_candidates}")
    print(f"Completed Decisions:          {completed_decisions} / {total_candidates}")
    print(f"Human Accepted Candidates:    {accepted_count}")
    print(f"Human Rejected Candidates:    {rejected_count}")
    print(f"Human Uncertain Candidates:   {uncertain_count}")
    print("-" * 70)
    print(f"Start Boundary Revisions:     {start_revisions}")
    print(f"End Boundary Revisions:       {end_revisions}")
    print(f"Role Selections Specified:    {role_revisions}")
    print(f"Pieces with Missing Themes:   {missing_themes_reported} / {len(piece_evaluations)}")
    print("=" * 70)

    if args.adjudicated_manifest:
        adj_path = Path(args.adjudicated_manifest)
        if adj_path.exists():
            manifest = load_theme_annotation_manifest(adj_path)
            print(f"Adjudicated Manifest Loaded:  {adj_path}")
            print(f"Manifest Human Accepted Count:{manifest.human_accepted_count}")
            print(f"Manifest Total Annotations:  {len(manifest.annotations)}")
            print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
