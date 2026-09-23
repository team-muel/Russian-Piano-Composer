"""Machine-Triangulated Source-Fidelity Validation Protocol Engine for RC-013 (Protocol V2).

Coordinates multi-channel OMR and visual alignment triangulation, evaluates disagreement taxonomy,
runs blind calibration and end-to-end image mutation benchmarks, and computes protocol freeze hashes.
"""

from __future__ import annotations

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
    NeuralVisualFeatureOMREngine,
    ScoreScanStructuralAlignmentEngine,
    StructuredStaffGraphOMREngine,
)
from russian_piano_composer.corpus.rc013_renderer import (
    DeterministicScoreRenderer,
)

PROTOCOL_VERSION: str = "rc013_machine_triangulation_protocol_v2"

# Frozen Structural Rules & Dimensions
CRITICAL_DIMENSIONS: list[str] = [
    "pitch",
    "accidental",
    "octave",
    "onset",
    "duration",
    "rest",
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
    """Consolidated outcome of evaluating a score candidate across all 3 independent channels."""

    score_id: str
    verdict: str  # "MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS", "MACHINE_TRIANGULATION_FAILED", "MACHINE_TRIANGULATION_INDETERMINATE"
    disagreement_category: str  # "NONE", "ENGINE_A_ONLY_DISAGREEMENT", "ENGINE_B_ONLY_DISAGREEMENT", "BOTH_OMR_AGREE_AGAINST_CANDIDATE", "IMAGE_ALIGNMENT_DISAGREEMENT", "MULTI_CHANNEL_DISAGREEMENT"
    overall_omr_ned: float
    channel_a_distance: float
    channel_b_distance: float
    channel_c_discrepancy: float
    critical_mismatches_total: int
    discrepant_measures: list[int]
    channel_results: list[dict[str, Any]]
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
            "critical_mismatches_total": self.critical_mismatches_total,
            "discrepant_measures": self.discrepant_measures,
            "channel_results": self.channel_results,
            "validation_timestamp": self.validation_timestamp,
        }


class MachineTriangulationProtocol:
    """Pre-registered calibration and evaluation protocol engine (V2)."""

    def __init__(
        self,
        max_omr_ned_threshold: float = 0.05,
        max_critical_mismatches: int = 0,
        max_image_discrepancy: float = 0.35,
    ) -> None:
        self.max_omr_ned_threshold = max_omr_ned_threshold
        self.max_critical_mismatches = max_critical_mismatches
        self.max_image_discrepancy = max_image_discrepancy

        self.engine_a = StructuredStaffGraphOMREngine()
        self.engine_b = NeuralVisualFeatureOMREngine()
        self.engine_c = ScoreScanStructuralAlignmentEngine()
        self.mutation_engine = RC013MutationEngine()
        self.renderer = DeterministicScoreRenderer(target_dpi=150)
        self.image_mutation_engine = EndToEndImageMutationEngine()

    def evaluate_candidate(
        self,
        candidate_musicxml_path: str,
        source_image_paths: list[str],
        score_id: str,
        rendered_score_image_paths: list[str] | None = None,
    ) -> TriangulationEvaluationResult:
        """Runs multi-channel blind triangulation on a candidate score.

        OMR Engines (Channels A and B) receive strictly source scan images.
        Alignment Engine (Channel C) compares rendered symbolic score images against source scan images.
        """
        import datetime
        import tempfile

        candidate_graph = extract_event_graph_from_musicxml(candidate_musicxml_path, score_id=score_id)

        # 1. Run Channel A (Structured OMR) - strictly blind
        res_a = self.engine_a.process_source_pages(
            source_image_paths,
            score_id=score_id,
        )

        # 2. Run Channel B (Neural Visual Feature OMR) - strictly blind
        res_b = self.engine_b.process_source_pages(
            source_image_paths,
            score_id=score_id,
        )

        # 3. Channel C: Render candidate score if not explicitly passed
        rendered_images = rendered_score_image_paths
        if not rendered_images:
            temp_render_dir = tempfile.mkdtemp(prefix="rc013_rend_eval_")
            rendered_images = self.renderer.render_musicxml_to_images(
                candidate_musicxml_path,
                temp_render_dir,
                score_id=score_id,
            )

        # Run Channel C (Structural Image Alignment) - comparing rendered symbolic images vs distinct scan images
        res_c = self.engine_c.align_score_to_scan(
            rendered_images=rendered_images,
            historical_scan_images=source_image_paths,
            score_id=score_id,
        )

        # Compute pairwise distances
        dist_a = 0.0
        comp_a: EventComparisonResult | None = None
        if res_a.extracted_event_graph:
            comp_a = compare_event_graphs(candidate_graph, res_a.extracted_event_graph)
            dist_a = comp_a.overall_omr_ned

        dist_b = 0.0
        comp_b: EventComparisonResult | None = None
        if res_b.extracted_event_graph:
            comp_b = compare_event_graphs(candidate_graph, res_b.extracted_event_graph)
            dist_b = comp_b.overall_omr_ned

        c_disc = float(res_c.execution_metadata.get("mean_discrepancy", 0.0))

        # Check disagreements
        disagreements_a = dist_a > self.max_omr_ned_threshold
        disagreements_b = dist_b > self.max_omr_ned_threshold
        disagreements_c = c_disc > self.max_image_discrepancy

        critical_mismatches = 0
        discrepant_measures: set[int] = set()
        if comp_a:
            critical_mismatches += comp_a.critical_mismatches_count
            discrepant_measures.update(comp_a.discrepant_measures)
        if comp_b:
            critical_mismatches += comp_b.critical_mismatches_count
            discrepant_measures.update(comp_b.discrepant_measures)

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
            critical_mismatches_total=critical_mismatches,
            discrepant_measures=sorted(discrepant_measures),
            channel_results=[res_a.to_dict(), res_b.to_dict(), res_c.to_dict()],
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
    ) -> dict[str, Any]:
        """Generates the canonical frozen protocol manifest payload."""
        import datetime

        manifest: dict[str, Any] = {
            "protocol_version": PROTOCOL_VERSION,
            "created_at": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "FROZEN_PRE_REGISTERED",
            "calibration_corpus_hash": calibration_corpus_hash,
            "end_to_end_mutation_suite_hash": end_to_end_mutation_suite_hash,
            "calibration_result_hash": calibration_result_hash,
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
                },
            },
            "dimensions": {
                "critical": CRITICAL_DIMENSIONS,
                "secondary": SECONDARY_DIMENSIONS,
            },
            "acceptance_thresholds": {
                "max_omr_ned": self.max_omr_ned_threshold,
                "max_critical_mismatches": self.max_critical_mismatches,
                "max_image_discrepancy": self.max_image_discrepancy,
                "required_mutation_recall": 1.0,
            },
            "qualification_policy": {
                "machine_receipts_can_qualify_composer": False,
                "current_n_russian": 2,
                "rc012_resumption_status": "BLOCKED",
            },
        }

        payload = json.dumps(manifest, sort_keys=True)
        manifest["protocol_hash"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return manifest
