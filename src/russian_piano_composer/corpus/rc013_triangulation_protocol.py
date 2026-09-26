"""Machine-Triangulated Source-Fidelity Validation Protocol Engine for RC-013 (Protocol V4).

Coordinates external multi-channel OMR (Audiveris + homr) and MuseScore visual alignment triangulation,
evaluates sequence-aware disagreement taxonomy, bounded multi-page coverage, and inspectable calibration gates.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import dataclass
from typing import Any

from russian_piano_composer.corpus.rc013_event_graph import (
    EventComparisonResult,
    compare_event_graphs,
    extract_event_graph_from_musicxml,
)
from russian_piano_composer.corpus.rc013_image_mutations import (
    EndToEndImageMutationEngine,
    ImageMutationBenchmarkResult,
)
from russian_piano_composer.corpus.rc013_mutations import (
    RC013MutationEngine,
)
from russian_piano_composer.corpus.rc013_omr_adapters import (
    ExternalAudiverisOMREngine,
    ExternalHomrNeuralOMREngine,
    ScoreScanStructuralAlignmentEngine,
)
from russian_piano_composer.corpus.rc013_renderer import (
    MuseScoreProductionScoreRenderer,
)

PROTOCOL_VERSION: str = "rc013_machine_triangulation_protocol_v4"

# Frozen Structural Rules & Dimensions
CRITICAL_DIMENSIONS: list[str] = [
    "pitch",
    "accidental",
    "octave",
    "onset",
    "duration",
    "rest",
    "staff",
    "voice",
    "key_signature",
    "time_signature",
    "tie",
    "tuplet",
    "repeat_structure",
    "measure_sequence",
]

SECONDARY_DIMENSIONS: list[str] = [
    "dynamic",
    "articulation",
    "slur",
    "pedal",
    "tempo",
]


@dataclass
class TriangulationEvaluationResult:
    """Consolidated outcome of evaluating a score candidate across all 3 independent channels (Protocol V4)."""

    score_id: str
    verdict: str  # "MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS", "MACHINE_TRIANGULATION_FAILED", "MACHINE_TRIANGULATION_INDETERMINATE"
    disagreement_category: str
    overall_omr_ned: float
    channel_a_distance: float
    channel_b_distance: float
    channel_c_discrepancy: float
    channel_a_page_coverage: float
    channel_a_measure_coverage: float
    channel_a_event_recall: float
    channel_a_event_precision: float
    channel_b_page_coverage: float
    channel_b_measure_coverage: float
    channel_b_event_recall: float
    channel_b_event_precision: float
    channel_c_page_coverage: float
    critical_mismatches_total: int
    discrepant_measures: list[int]
    channel_results: list[dict[str, Any]]
    dimension_reliability: dict[str, dict[str, float]]
    validation_timestamp: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "score_id": self.score_id,
            "verdict": self.verdict,
            "disagreement_category": self.disagreement_category,
            "overall_omr_ned": self.overall_omr_ned,
            "channel_a_distance": self.channel_a_distance,
            "channel_b_distance": self.channel_b_distance,
            "channel_c_discrepancy": self.channel_c_discrepancy,
            "channel_a_page_coverage": self.channel_a_page_coverage,
            "channel_a_measure_coverage": self.channel_a_measure_coverage,
            "channel_a_event_recall": self.channel_a_event_recall,
            "channel_a_event_precision": self.channel_a_event_precision,
            "channel_b_page_coverage": self.channel_b_page_coverage,
            "channel_b_measure_coverage": self.channel_b_measure_coverage,
            "channel_b_event_recall": self.channel_b_event_recall,
            "channel_b_event_precision": self.channel_b_event_precision,
            "channel_c_page_coverage": self.channel_c_page_coverage,
            "critical_mismatches_total": self.critical_mismatches_total,
            "discrepant_measures": self.discrepant_measures,
            "channel_results": self.channel_results,
            "dimension_reliability": self.dimension_reliability,
            "validation_timestamp": self.validation_timestamp,
        }


def derive_calibration_verdict(
    evaluations: list[dict[str, Any]],
    holdout_evaluations: list[dict[str, Any]],
    mutation_result: ImageMutationBenchmarkResult,
    feature_dep_result: dict[str, Any],
    conditions_gate: dict[str, bool],
) -> tuple[str, dict[str, Any]]:
    """Derives scientific calibration verdict deterministically from inspectable multi-channel gate conditions."""
    gate_details: dict[str, Any] = {
        "conditions": conditions_gate,
        "all_conditions_satisfied": all(conditions_gate.values()),
    }

    if not conditions_gate.get("external_engines_available", False):
        return "PROTOCOL_V4_CALIBRATION_BLOCKED", gate_details

    if not conditions_gate.get("real_scan_bytes_valid", False) or not conditions_gate.get("reference_bytes_valid", False):
        return "PROTOCOL_V4_CALIBRATION_FAIL", gate_details

    if not conditions_gate.get("complete_source_page_coverage", False):
        return "PROTOCOL_V4_CALIBRATION_FAIL", gate_details

    if not conditions_gate.get("required_mutation_recall_satisfied", False):
        return "PROTOCOL_V4_CALIBRATION_FAIL", gate_details

    if all(conditions_gate.values()):
        return "PROTOCOL_V4_CALIBRATION_PASS", gate_details

    # Partial pass if engines work and mutations pass but real scan noise bounds threshold
    if conditions_gate.get("required_mutation_recall_satisfied", False) and conditions_gate.get("synthetic_controls_pass", False):
        return "PROTOCOL_V4_CALIBRATION_PARTIAL", gate_details

    return "PROTOCOL_V4_CALIBRATION_FAIL", gate_details


class MachineTriangulationProtocol:
    """Protocol Engine for Machine-Triangulated Source-Fidelity Verification (Protocol V4)."""

    def __init__(
        self,
        max_omr_ned_threshold: float = 0.05,
        max_critical_mismatches: int = 0,
        max_image_discrepancy: float = 0.35,
        min_measure_coverage_threshold: float = 0.50,
        required_mutation_recall: float = 1.0,
    ) -> None:
        self.max_omr_ned_threshold = max_omr_ned_threshold
        self.max_critical_mismatches = max_critical_mismatches
        self.max_image_discrepancy = max_image_discrepancy
        self.min_measure_coverage_threshold = min_measure_coverage_threshold
        self.required_mutation_recall = required_mutation_recall

        self.engine_a = ExternalAudiverisOMREngine()
        self.engine_b = ExternalHomrNeuralOMREngine()
        self.engine_c = ScoreScanStructuralAlignmentEngine()
        self.renderer = MuseScoreProductionScoreRenderer()
        self.mutation_engine = RC013MutationEngine()
        self.image_mutation_engine = EndToEndImageMutationEngine()

    def evaluate_candidate(
        self,
        candidate_musicxml_path: str,
        source_image_paths: list[str],
        score_id: str,
        output_scratch_dir: str | None = None,
        rendered_images: list[str] | None = None,
    ) -> TriangulationEvaluationResult:
        """Executes full multi-page 3-channel triangulation on a candidate MusicXML file."""
        candidate_graph = extract_event_graph_from_musicxml(candidate_musicxml_path, score_id=score_id)
        expected_pages_total = max(len(source_image_paths), 1)

        # 1. Run Channel A (External Audiveris)
        res_a = self.engine_a.process_source_pages(source_image_paths, score_id=score_id)

        # 2. Run Channel B (External homr Neural)
        res_b = self.engine_b.process_source_pages(source_image_paths, score_id=score_id)

        # 3. Production Rendering if not pre-rendered
        if not rendered_images:
            render_dir = output_scratch_dir or f"data/calibration/rc013_machine_validation/rendered_production/{score_id}"
            rendered_images = self.renderer.render_musicxml_to_images(
                musicxml_path=candidate_musicxml_path,
                output_dir=render_dir,
                score_id=score_id,
            )

        # 4. Run Channel C (Structural Alignment)
        res_c = self.engine_c.align_score_to_scan(
            rendered_images=rendered_images,
            historical_scan_images=source_image_paths,
            score_id=score_id,
        )

        # Evaluate Channel A metrics
        dist_a = 0.0
        cov_a_page = 0.0
        cov_a_m = 0.0
        rec_a = 0.0
        prec_a = 0.0
        comp_a: EventComparisonResult | None = None
        if res_a.extracted_event_graph:
            comp_a = compare_event_graphs(candidate_graph, res_a.extracted_event_graph, expected_pages_total=expected_pages_total)
            dist_a = comp_a.overall_omr_ned
            cov_a_page = comp_a.page_coverage
            cov_a_m = comp_a.measure_coverage
            rec_a = comp_a.event_recall
            prec_a = comp_a.event_precision

        # Evaluate Channel B metrics
        dist_b = 0.0
        cov_b_page = 0.0
        cov_b_m = 0.0
        rec_b = 0.0
        prec_b = 0.0
        comp_b: EventComparisonResult | None = None
        if res_b.extracted_event_graph:
            comp_b = compare_event_graphs(candidate_graph, res_b.extracted_event_graph, expected_pages_total=expected_pages_total)
            dist_b = comp_b.overall_omr_ned
            cov_b_page = comp_b.page_coverage
            cov_b_m = comp_b.measure_coverage
            rec_b = comp_b.event_recall
            prec_b = comp_b.event_precision

        c_disc = float(res_c.execution_metadata.get("mean_discrepancy", 0.0))
        c_page_cov = float(res_c.execution_metadata.get("page_alignment_coverage", 0.0))

        # Check Channel Disagreements
        disagreements_a = dist_a > self.max_omr_ned_threshold or cov_a_m < self.min_measure_coverage_threshold
        disagreements_b = dist_b > self.max_omr_ned_threshold or cov_b_m < self.min_measure_coverage_threshold
        disagreements_c = c_disc > self.max_image_discrepancy or c_page_cov < 1.0

        critical_mismatches = 0
        discrepant_measures: set[int] = set()
        dim_rel: dict[str, dict[str, float]] = {}

        if comp_a:
            critical_mismatches += comp_a.critical_mismatches_count
            discrepant_measures.update(comp_a.discrepant_measures)
            dim_rel = comp_a.dimension_reliability
        if comp_b:
            critical_mismatches += comp_b.critical_mismatches_count
            discrepant_measures.update(comp_b.discrepant_measures)
            if not dim_rel:
                dim_rel = comp_b.dimension_reliability

        if not disagreements_a and not disagreements_b and not disagreements_c and critical_mismatches == 0:
            verdict = "MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS"
            category = "NONE"
        elif disagreements_a and not disagreements_b and not disagreements_c:
            verdict = "MACHINE_TRIANGULATION_INDETERMINATE"
            category = "ENGINE_A_ONLY_DISAGREEMENT"
        elif disagreements_b and not disagreements_a and not disagreements_c:
            verdict = "MACHINE_TRIANGULATION_INDETERMINATE"
            category = "ENGINE_B_ONLY_DISAGREEMENT"
        elif disagreements_a and disagreements_b:
            verdict = "MACHINE_TRIANGULATION_FAILED"
            category = "BOTH_OMR_AGREE_AGAINST_CANDIDATE"
        elif disagreements_c and not disagreements_a and not disagreements_b:
            verdict = "MACHINE_TRIANGULATION_INDETERMINATE"
            category = "IMAGE_ALIGNMENT_DISAGREEMENT"
        else:
            verdict = "MACHINE_TRIANGULATION_FAILED"
            category = "MULTI_CHANNEL_DISAGREEMENT"

        return TriangulationEvaluationResult(
            score_id=score_id,
            verdict=verdict,
            disagreement_category=category,
            overall_omr_ned=round(max(dist_a, dist_b), 4),
            channel_a_distance=dist_a,
            channel_b_distance=dist_b,
            channel_c_discrepancy=c_disc,
            channel_a_page_coverage=cov_a_page,
            channel_a_measure_coverage=cov_a_m,
            channel_a_event_recall=rec_a,
            channel_a_event_precision=prec_a,
            channel_b_page_coverage=cov_b_page,
            channel_b_measure_coverage=cov_b_m,
            channel_b_event_recall=rec_b,
            channel_b_event_precision=prec_b,
            channel_c_page_coverage=c_page_cov,
            critical_mismatches_total=critical_mismatches,
            discrepant_measures=sorted(discrepant_measures),
            channel_results=[res_a.to_dict(), res_b.to_dict(), res_c.to_dict()],
            dimension_reliability=dim_rel,
            validation_timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
        )

    def run_image_mutation_benchmark(
        self,
        base_musicxml_paths: list[str],
    ) -> ImageMutationBenchmarkResult:
        """Evaluates end-to-end image-level mutation sensitivity across all 19 mutation families."""
        return self.image_mutation_engine.run_benchmark(base_musicxml_paths)

    def generate_frozen_protocol_manifest(
        self,
        calibration_corpus_hash: str,
        end_to_end_mutation_suite_hash: str,
        calibration_result_hash: str,
        external_engine_bundle_hash: str,
        real_scan_benchmark_hash: str,
    ) -> dict[str, Any]:
        """Generates the canonical frozen protocol manifest payload (Protocol V4)."""
        manifest: dict[str, Any] = {
            "protocol_version": PROTOCOL_VERSION,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "FROZEN_PRE_REGISTERED",
            "calibration_corpus_hash": calibration_corpus_hash,
            "end_to_end_mutation_suite_hash": end_to_end_mutation_suite_hash,
            "calibration_result_hash": calibration_result_hash,
            "external_engine_bundle_hash": external_engine_bundle_hash,
            "real_scan_benchmark_hash": real_scan_benchmark_hash,
            "engines": {
                "channel_a": {
                    "name": self.engine_a.ENGINE_NAME,
                    "version": self.engine_a.ENGINE_VERSION,
                    "architecture": self.engine_a.ARCHITECTURE,
                },
                "channel_b": {
                    "name": self.engine_b.ENGINE_NAME,
                    "version": self.engine_b.ENGINE_VERSION,
                    "architecture": self.engine_b.ARCHITECTURE,
                },
                "channel_c": {
                    "name": self.engine_c.ENGINE_NAME,
                    "version": self.engine_c.ENGINE_VERSION,
                    "architecture": self.engine_c.ARCHITECTURE,
                    "renderer": self.renderer.RENDERER_NAME,
                    "renderer_version": self.renderer.RENDERER_VERSION,
                },
            },
            "dimensions": {
                "critical": list(CRITICAL_DIMENSIONS),
                "secondary": list(SECONDARY_DIMENSIONS),
            },
            "acceptance_thresholds": {
                "max_omr_ned": self.max_omr_ned_threshold,
                "max_critical_mismatches": self.max_critical_mismatches,
                "max_image_discrepancy": self.max_image_discrepancy,
                "min_measure_coverage_threshold": self.min_measure_coverage_threshold,
                "required_mutation_recall": self.required_mutation_recall,
            },
            "qualification_policy": {
                "machine_receipts_can_qualify_composer": False,
                "current_n_russian": 2,
                "rc012_resumption_status": "BLOCKED",
            },
        }

        manifest_payload = json.dumps(manifest, sort_keys=True)
        manifest["protocol_hash"] = hashlib.sha256(manifest_payload.encode("utf-8")).hexdigest()
        return manifest
