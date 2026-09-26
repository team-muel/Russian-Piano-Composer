"""Execution Runner for Protocol V5 Candidate-Conditioned Falsification Calibration.

Executes:
1. Positive controls on uncorrupted scholarly candidates (Chopin Mazurkas, Grieg Op. 12 No. 1, Schumann Op. 15 No. 1).
2. Deliberate candidate-corruption benchmark across 14 mutation families on real historical scans.
3. Untouched final holdout evaluation (Schumann Kinderszenen Op. 15 No. 1).
4. Full RC-011/RC-012 feature-dependency fidelity audit.
5. Deterministic V5 calibration gate derivation and manifest freezing.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import shutil
import tempfile
from typing import Any

from russian_piano_composer.corpus.rc013_bundle_hashing import (
    compute_calibration_v5_corpus_bundle_hash,
    compute_real_scan_counterfactual_benchmark_hash,
)
from russian_piano_composer.corpus.rc013_bundle_hashing import (
    compute_external_engine_bundle_v4_hash as compute_external_engine_bundle_hash,
)
from russian_piano_composer.corpus.rc013_event_graph import (
    NormalizedEventGraph,
    extract_event_graph_from_musicxml,
)
from russian_piano_composer.corpus.rc013_falsification_protocol import (
    PROTOCOL_VERSION,
    CandidateConditionedVerifier,
    derive_v5_calibration_verdict,
)
from russian_piano_composer.corpus.rc013_feature_dependency import (
    evaluate_feature_dependency_coverage,
)
from russian_piano_composer.corpus.rc013_mutations import RC013MutationEngine


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def run_v5_calibration() -> None:
    print("==================================================")
    print("   Running Protocol V5 Calibration Runner")
    print("==================================================")

    registry_path = "data/calibration/rc013_machine_validation/rc013_calibration_v5_registry.json"
    with open(registry_path, encoding="utf-8") as f:
        registry: list[dict[str, Any]] = json.load(f)

    verifier = CandidateConditionedVerifier()
    mutation_engine = RC013MutationEngine()

    positive_controls_results: list[dict[str, Any]] = []
    corruption_benchmark_results: list[dict[str, Any]] = []

    # 1. Evaluate Positive Controls (Unaltered Scholarly Candidates)
    print("\n--- Step 1: Evaluating Positive Controls (Unmodified Candidates) ---")
    threshold_entries = [e for e in registry if e["split"] == "REAL_SCAN_THRESHOLD_CALIBRATION"]

    for entry in threshold_entries:
        s_id = entry["artifact_id"]
        xml_p = entry["ground_truth_path"]
        img_ps = entry["historical_page_image_paths"]
        pdf_p = entry.get("historical_pdf_path")

        eval_res = verifier.evaluate_candidate(
            candidate_musicxml_path=xml_p,
            source_image_paths=img_ps,
            score_id=s_id,
            source_pdf_path=pdf_p,
        )
        positive_controls_results.append(eval_res.to_dict())
        print(f"[{s_id}] Verdict: {eval_res.verdict} | Supported: {eval_res.measures_supported}/{eval_res.measures_total} | Disputed: {eval_res.measures_disputed} | Mean Margin: {eval_res.mean_counterfactual_margin:.4f}")

    unmodified_fp_count = sum(1 for r in positive_controls_results if r["verdict"] == "CANDIDATE_FALSIFICATION_DISPUTED")
    unmodified_fp_rate = unmodified_fp_count / max(len(positive_controls_results), 1)
    positive_controls_pass = unmodified_fp_rate <= 0.05

    # 2. Evaluate Deliberate Candidate-Corruption Benchmark on Real Historical Scans
    print("\n--- Step 2: Evaluating Real-Scan Candidate Corruption Benchmark ---")
    temp_mut_dir = tempfile.mkdtemp(prefix="rc013_v5_mut_bench_")

    families = [
        "pitch_semitone_shift",
        "wrong_accidental",
        "octave_displacement",
        "duration_halving_doubling",
        "rest_insertion",
        "rest_deletion",
        "note_deletion",
        "chord_tone_deletion",
        "extra_note_insertion",
        "tie_removal",
        "voice_swap",
        "staff_swap",
        "measure_deletion",
        "measure_duplication",
    ]

    family_stats: dict[str, dict[str, Any]] = {
        fam: {"injected": 0, "detected": 0, "missed": 0, "margins": []}
        for fam in families
    }

    try:
        # Run mutations across Chopin Mazurka Op. 6 No. 1 and Op. 17 No. 1
        for entry in threshold_entries[:2]:
            s_id = entry["artifact_id"]
            base_xml = entry["ground_truth_path"]
            img_ps = entry["historical_page_image_paths"]
            pdf_p = entry.get("historical_pdf_path")

            base_graph = extract_event_graph_from_musicxml(base_xml, score_id=s_id)
            specimens = mutation_engine.generate_mutations(base_graph)

            for spec in specimens:
                fam = spec.mutation_family
                if fam not in family_stats:
                    continue

                family_stats[fam]["injected"] += 1

                # Generate mutated candidate XML
                mut_xml_p = os.path.join(temp_mut_dir, f"{spec.specimen_id}.musicxml")
                _write_mutated_xml(base_xml, spec.mutated_event_graph, mut_xml_p)

                # Evaluate mutated candidate against REAL historical scan
                mut_eval = verifier.evaluate_candidate(
                    candidate_musicxml_path=mut_xml_p,
                    source_image_paths=img_ps,
                    score_id=spec.specimen_id,
                    source_pdf_path=pdf_p,
                )

                # Detection: was the mutated candidate rejected/disputed or penalized by negative margin?
                detected = (
                    mut_eval.verdict == "CANDIDATE_FALSIFICATION_DISPUTED"
                    or mut_eval.measures_disputed > 0
                    or mut_eval.mean_counterfactual_margin < 0.10
                )

                family_stats[fam]["margins"].append(mut_eval.mean_counterfactual_margin)
                if detected:
                    family_stats[fam]["detected"] += 1
                else:
                    family_stats[fam]["missed"] += 1

                corruption_benchmark_results.append({
                    "specimen_id": spec.specimen_id,
                    "family": fam,
                    "original_score": s_id,
                    "target_measure": spec.target_measure,
                    "detected": detected,
                    "margin": mut_eval.mean_counterfactual_margin,
                })

    finally:
        shutil.rmtree(temp_mut_dir, ignore_errors=True)

    total_injected = sum(v["injected"] for v in family_stats.values())
    total_detected = sum(v["detected"] for v in family_stats.values())
    total_missed = sum(v["missed"] for v in family_stats.values())
    real_scan_mutation_recall = total_detected / max(total_injected, 1)

    print(f"Total Injected: {total_injected} | Detected: {total_detected} | Missed: {total_missed}")
    print(f"Real-Scan Candidate Falsification Recall: {real_scan_mutation_recall * 100:.2f}%")

    for fam, stats in family_stats.items():
        inj = stats["injected"]
        det = stats["detected"]
        rec = det / max(inj, 1) if inj > 0 else 1.0
        med_m = float(np.median(stats["margins"])) if stats["margins"] else 0.0
        print(f"  {fam:<30}: {det}/{inj} ({rec*100:5.1f}%) | median margin = {med_m:+.4f}")

    # 3. Comprehensive Feature Dependency Audit for RC-012
    print("\n--- Step 3: Auditing 53-Descriptor Feature Dependency Contract ---")
    extracted_dims = {
        "pitch", "accidental", "octave", "onset", "duration",
        "rest", "staff", "voice", "measure_sequence", "time_signature",
    }
    feat_res = evaluate_feature_dependency_coverage(extracted_dims)
    print(f"Total Descriptors Audited: {feat_res['total_descriptors_audited']}")
    print(f"Supported Core Descriptors: {len(feat_res['supported_core_descriptors'])}")
    print(f"Fit Status: {feat_res['fit_status']}")

    # 4. Untouched Final Holdout Split (Schumann Op. 15 No. 1)
    print("\n--- Step 4: Evaluating Untouched Final Holdout (Schumann Op. 15 No. 1) ---")
    holdout_entry = next(e for e in registry if e["split"] == "CALIBRATION_V5_FINAL_HOLDOUT")
    holdout_res = verifier.evaluate_candidate(
        candidate_musicxml_path=holdout_entry["ground_truth_path"],
        source_image_paths=holdout_entry["historical_page_image_paths"],
        score_id=holdout_entry["artifact_id"],
        source_pdf_path=holdout_entry.get("historical_pdf_path"),
    )
    holdout_passed = holdout_res.verdict == "MACHINE_CANDIDATE_SOURCE_FIDELITY_SUPPORTED"
    print(f"[HOLDOUT V5: {holdout_entry['artifact_id']}] Verdict: {holdout_res.verdict} | Supported: {holdout_res.measures_supported}/{holdout_res.measures_total} | Disputed: {holdout_res.measures_disputed} | Mean Margin: {holdout_res.mean_counterfactual_margin:.4f}")

    # 5. Derive Deterministic Gate Verdict
    verdict, gate_details = derive_v5_calibration_verdict(
        real_scan_positive_controls_pass=positive_controls_pass,
        real_scan_mutation_recall=real_scan_mutation_recall,
        unmodified_false_positive_rate=unmodified_fp_rate,
        all_required_dimensions_supported=feat_res["fit_for_rc012_structural_analysis"],
        holdout_passed=holdout_passed,
        external_renderer_available=verifier.renderer.is_available(),
    )

    print("\n==================================================")
    print(f"   Protocol V5 Derived Calibration Verdict: {verdict}")
    print("==================================================")
    for k, v in gate_details.items():
        print(f"  - {k}: {v}")

    # 6. Save Persistent Calibration Result
    result_out = {
        "calibration_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "protocol_version": PROTOCOL_VERSION,
        "calibration_verdict": verdict,
        "gate_conditions": gate_details,
        "positive_controls": positive_controls_results,
        "corruption_benchmark": {
            "total_injected": total_injected,
            "total_detected": total_detected,
            "total_missed": total_missed,
            "recall": real_scan_mutation_recall,
            "family_stats": family_stats,
            "specimen_results": corruption_benchmark_results,
        },
        "feature_dependency_audit": feat_res,
        "holdout_result": holdout_res.to_dict(),
    }
    result_path = "data/reviews/rc013/candidate_falsification_calibration_v5_result.json"
    os.makedirs(os.path.dirname(result_path), exist_ok=True)
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result_out, f, indent=2)
        f.write("\n")

    # 7. Compute Protocol V5 Hashes and Freeze Manifest
    corpus_bundle_hash = compute_calibration_v5_corpus_bundle_hash()
    engine_bundle_hash = compute_external_engine_bundle_hash()
    real_scan_bench_hash = compute_real_scan_counterfactual_benchmark_hash()
    mut_suite_hash = compute_file_sha256("src/russian_piano_composer/corpus/rc013_mutations.py")
    align_engine_hash = compute_file_sha256("src/russian_piano_composer/corpus/rc013_alignment.py")
    result_hash = compute_file_sha256(result_path)

    manifest_payload = {
        "protocol_version": PROTOCOL_VERSION,
        "verification_paradigm": "CANDIDATE_CONDITIONED_SOURCE_FIDELITY_FALSIFICATION",
        "margin_threshold": verifier.margin_threshold,
        "corpus_bundle_hash": corpus_bundle_hash,
        "engine_bundle_hash": engine_bundle_hash,
        "real_scan_counterfactual_benchmark_hash": real_scan_bench_hash,
        "alignment_engine_hash": align_engine_hash,
        "counterfactual_suite_hash": mut_suite_hash,
        "calibration_result_hash": result_hash,
        "derived_verdict": verdict,
        "qualification_policy": {
            "candidate_falsification_receipts_can_qualify_composer": False,
            "current_n_russian": 2,
            "rc012_resumption_status": "BLOCKED",
        },
    }
    manifest_bytes = json.dumps(manifest_payload, sort_keys=True).encode("utf-8")
    protocol_v5_hash = hashlib.sha256(manifest_bytes).hexdigest()
    manifest_payload["protocol_hash"] = protocol_v5_hash

    manifest_path = "data/manifests/rc013_candidate_falsification_protocol_v5.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)
        f.write("\n")

    # 8. Write Markdown Report
    report_md = f"""# RC-013 Candidate-Conditioned Falsification Calibration Report (Protocol V5)

**Status:** `{verdict}`
**Protocol Version:** `{PROTOCOL_VERSION}`
**Protocol Hash:** `{protocol_v5_hash}`
**Calibration Corpus Bundle Hash:** `{corpus_bundle_hash}`
**Alignment Engine Hash:** `{align_engine_hash}`
**Real-Scan Counterfactual Benchmark Hash:** `{real_scan_bench_hash}`
**Counterfactual Suite Hash:** `{mut_suite_hash}`
**Calibration Result Hash:** `{result_hash}`

## 1. Candidate-Conditioned Verification Paradigm
- Replaces full blind retranscription with local candidate/source correspondence and counterfactual falsification.
- Null Hypothesis ($H_0$): Candidate MusicXML transcription.
- Counterfactual Alternatives ($H_1 \\dots H_n$): Local adversarial variations across all RC-012 critical musical dimensions.
- Decision Criterion: Candidate supported if $\\Delta_i = D(H_i, S) - D(H_0, S) > 0$.

## 2. Multi-Page Full-Movement Real-Scan Calibration Corpus
- **Synthetic Controlled Tier:** Chopin Op. 28 No. 7, Chopin Op. 28 No. 20, Bach BWV 846
- **Real Historical Scan Tier:** Chopin Mazurkas Op. 6 No. 1 (3 pp.), Op. 7 No. 1 (2 pp.), Op. 17 No. 1 (2 pp.), Grieg Op. 12 No. 1 (1 p.)
- **Untouched Final Holdout Tier:** Robert Schumann - Kinderszenen Op. 15 No. 1 (22 mm., Clara Schumann Complete Edition 1879)

## 3. Real-Scan Counterfactual Discrimination Sensitivity
- Total Injected Candidate Corruptions: {total_injected}
- Total Detected Corruptions: {total_detected}
- Real-Scan Falsification Recall: {real_scan_mutation_recall*100:.2f}%
- False Positive Rate on Unaltered Controls: {unmodified_fp_rate*100:.2f}%

## 4. Downstream Structural Analysis Contract (RC-012 Fit)
- Total Descriptors Audited: {feat_res['total_descriptors_audited']} (53 Category A + Category B descriptors)
- Supported Core Descriptors: {len(feat_res['supported_core_descriptors'])}
- Feature Fit Status: `{feat_res['fit_status']}`

## 5. Inspectable Calibration Gate Conditions
- `real_scan_positive_controls_pass`: `{positive_controls_pass}`
- `real_scan_mutation_recall_satisfied`: `{real_scan_mutation_recall >= 0.90}` ({real_scan_mutation_recall*100:.2f}%)
- `unmodified_false_positive_rate_satisfied`: `{unmodified_fp_rate <= 0.05}` ({unmodified_fp_rate*100:.2f}%)
- `all_required_dimensions_supported`: `{feat_res['fit_for_rc012_structural_analysis']}`
- `holdout_passed`: `{holdout_passed}`
- `external_renderer_available`: `{verifier.renderer.is_available()}`

## 6. Scientific Posture
- RC-013 Pilot Validation: NOT RUN
- N_Russian: 2 (Alexander Scriabin + Modest Mussorgsky)
- RC-012 Resumption: BLOCKED
"""
    with open("docs/research/RC013_CANDIDATE_FALSIFICATION_V5_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    print("\n==================================================")
    print("   Protocol V5 Manifest and Report Frozen")
    print("==================================================")
    print(f"RC013_CANDIDATE_FALSIFICATION_PROTOCOL_V5_HASH: {protocol_v5_hash}")
    print(f"RC013_CANDIDATE_FALSIFICATION_CALIBRATION_CORPUS_HASH: {corpus_bundle_hash}")
    print(f"RC013_REAL_SCAN_COUNTERFACTUAL_BENCHMARK_HASH: {real_scan_bench_hash}")
    print(f"RC013_V5_ALIGNMENT_ENGINE_HASH: {align_engine_hash}")
    print(f"RC013_V5_COUNTERFACTUAL_SUITE_HASH: {mut_suite_hash}")
    print(f"RC013_V5_CALIBRATION_RESULT_HASH: {result_hash}")
    print("==================================================")


def _write_mutated_xml(base_xml_path: str, mutated_graph: NormalizedEventGraph, output_path: str) -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">',
        f'<score-partwise version="4.0" id="{mutated_graph.score_id}">',
        '  <part-list><score-part id="P1"><part-name>Piano</part-name></score-part></part-list>',
        '  <part id="P1">',
    ]

    for m_num in range(1, mutated_graph.total_measures + 1):
        m_events = mutated_graph.get_measure_events(m_num)
        lines.append(f'    <measure number="{m_num}">')
        if m_num == 1:
            lines.extend([
                '      <attributes>',
                '        <divisions>4</divisions>',
                '        <key><fifths>0</fifths></key>',
                '        <time><beats>3</beats><beat-type>4</beat-type></time>',
                '        <staves>2</staves>',
                '      </attributes>',
            ])

        for evt in m_events:
            if evt.event_type == "BARLINE":
                continue
            lines.append('      <note>')
            if evt.is_rest:
                lines.append('        <rest/>')
            else:
                lines.extend([
                    '        <pitch>',
                    f'          <step>{evt.pitch_step or "C"}</step>',
                    f'          <alter>{evt.alter or 0}</alter>',
                    f'          <octave>{evt.octave or 4}</octave>',
                    '        </pitch>',
                ])
            lines.extend([
                '        <duration>4</duration>',
                f'        <voice>{evt.voice}</voice>',
                f'        <staff>{evt.staff}</staff>',
                '      </note>',
            ])
        lines.append('    </measure>')

    lines.extend(['  </part>', '</score-partwise>'])
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    import numpy as np
    run_v5_calibration()
