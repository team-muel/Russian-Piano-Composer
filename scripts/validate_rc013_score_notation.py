"""CLI Tool for Validating RC-013 MusicXML Scores and Generating Error Log.

Iterates over all scores in data/scores/rc013, runs RC013ScoreValidator,
and outputs data/manifests/rc013_error_log.json and summary statistics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from typing import Any

from russian_piano_composer.corpus.rc013_validator import RC013ScoreValidator


def compute_sha256(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RC-013 score notation integrity.")
    parser.add_argument("--scores-dir", default="data/scores/rc013", help="Directory with scores")
    parser.add_argument("--output-log", default="data/manifests/rc013_error_log.json", help="Path for JSON error log")
    args = parser.parse_args()

    scores_dir = args.scores_dir
    if not os.path.isdir(scores_dir):
        print(f"Error: {scores_dir} is not a directory.")
        return 1

    score_files = sorted([f for f in os.listdir(scores_dir) if f.endswith(".musicxml") or f.endswith(".xml")])
    print(f"Auditing {len(score_files)} scores in {scores_dir}...")

    validator = RC013ScoreValidator()
    all_reports: list[dict[str, Any]] = []
    total_errors = 0
    passed_count = 0

    for s_file in score_files:
        full_path = os.path.join(scores_dir, s_file)
        report = validator.validate_file(full_path)
        r_dict = report.to_dict()
        r_dict["file_sha256"] = compute_sha256(full_path)
        all_reports.append(r_dict)
        if report.valid:
            passed_count += 1
        else:
            total_errors += len(report.errors)
            print(f"  [FAIL] {s_file}: {len(report.errors)} errors")
            for err in report.errors:
                print(f"         - Bar {err.measure}: {err.code} - {err.message}")

    os.makedirs(os.path.dirname(args.output_log), exist_ok=True)
    summary_data = {
        "milestone": "RC-013",
        "total_scores_audited": len(score_files),
        "scores_passed": passed_count,
        "scores_failed": len(score_files) - passed_count,
        "total_errors": total_errors,
        "reports": all_reports,
    }

    with open(args.output_log, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, sort_keys=True)

    log_sha = compute_sha256(args.output_log)
    print("\n==========================================")
    print(f"RC-013 Notation Validation Complete: {passed_count}/{len(score_files)} Passed")
    print(f"Error Log SHA256: {log_sha}")
    print("==========================================")

    return 0 if (total_errors == 0 and len(score_files) > 0) else 1


if __name__ == "__main__":
    sys.exit(main())
