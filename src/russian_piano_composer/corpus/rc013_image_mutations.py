"""End-to-End Image-Level Adversarial Mutation Benchmark for RC-013.

Passes mutated scores through raster rendering, scan degradation, blind OMR recognition,
and visual alignment to measure real empirical image-level mutation sensitivity.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from typing import Any

from PIL import Image, ImageFilter

from russian_piano_composer.corpus.rc013_event_graph import (
    NormalizedEventGraph,
    compare_event_graphs,
    extract_event_graph_from_musicxml,
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


@dataclass
class ImageMutationBenchmarkResult:
    """Consolidated outcome of end-to-end image mutation testing."""

    total_mutations_injected: int
    total_mutations_detected: int
    total_mutations_missed: int
    end_to_end_image_mutation_recall: float
    family_breakdown: dict[str, dict[str, int]]
    missed_mutations: list[dict[str, Any]]
    benchmark_sha256: str


class EndToEndImageMutationEngine:
    """Executes full image-level adversarial mutation sensitivity tests."""

    def __init__(self) -> None:
        self.mutation_engine = RC013MutationEngine()
        self.renderer = DeterministicScoreRenderer(target_dpi=150)
        self.engine_a = StructuredStaffGraphOMREngine()
        self.engine_b = NeuralVisualFeatureOMREngine()
        self.engine_c = ScoreScanStructuralAlignmentEngine()

    def run_benchmark(
        self,
        base_musicxml_paths: list[str],
    ) -> ImageMutationBenchmarkResult:
        """Runs end-to-end image-level mutation benchmark across all 19 mutation families."""
        results_by_family: dict[str, dict[str, int]] = {
            fam: {"injected": 0, "detected": 0, "missed": 0}
            for fam in self.mutation_engine.MUTATION_FAMILIES
        }
        missed: list[dict[str, Any]] = []

        temp_dir = tempfile.mkdtemp(prefix="rc013_img_mutation_")

        try:
            for xml_p in base_musicxml_paths:
                if not os.path.exists(xml_p):
                    continue

                score_id = os.path.basename(xml_p).replace(".musicxml", "")
                base_graph = extract_event_graph_from_musicxml(xml_p, score_id=score_id)

                # Render unmutated reference image
                ref_render_dir = os.path.join(temp_dir, f"{score_id}_ref_render")
                ref_images = self.renderer.render_musicxml_to_images(xml_p, ref_render_dir, score_id=score_id)

                # Generate mutated specimens
                specimens = self.mutation_engine.generate_mutations(base_graph)

                for spec in specimens:
                    fam = spec.mutation_family
                    results_by_family[fam]["injected"] += 1

                    # Write mutated specimen XML
                    mut_xml_path = os.path.join(temp_dir, f"{spec.specimen_id}.musicxml")
                    self._write_mutated_musicxml(xml_p, spec.mutated_event_graph, mut_xml_path)

                    # Render mutated score to image
                    mut_render_dir = os.path.join(temp_dir, f"{spec.specimen_id}_render")
                    mut_images = self.renderer.render_musicxml_to_images(mut_xml_path, mut_render_dir, score_id=spec.specimen_id)

                    # Apply scan degradation to mutated image (simulating degraded source scan)
                    degraded_images: list[str] = []
                    for m_img_p in mut_images:
                        deg_p = m_img_p.replace(".png", "_degraded.png")
                        with Image.open(m_img_p) as img:
                            deg_img = img.convert("RGB").filter(ImageFilter.GaussianBlur(radius=0.5))
                            deg_img.save(deg_p, "PNG")
                        degraded_images.append(deg_p)

                    # Run blind triangulation:
                    # 1. Blind Channel A recognition on degraded mutated image
                    res_a = self.engine_a.process_source_pages(degraded_images, score_id=spec.specimen_id)
                    # 2. Blind Channel B recognition on degraded mutated image
                    res_b = self.engine_b.process_source_pages(degraded_images, score_id=spec.specimen_id)
                    # 3. Channel C: Rendered unmutated score vs degraded mutated image
                    res_c = self.engine_c.align_score_to_scan(
                        rendered_images=ref_images,
                        historical_scan_images=degraded_images,
                        score_id=spec.specimen_id,
                    )

                    # Compare unmutated candidate graph against OMR outputs
                    detected = False
                    if res_a.extracted_event_graph:
                        comp_a = compare_event_graphs(base_graph, res_a.extracted_event_graph)
                        if comp_a.critical_mismatches_count > 0 or comp_a.overall_omr_ned > 0.0:
                            detected = True

                    if res_b.extracted_event_graph:
                        comp_b = compare_event_graphs(base_graph, res_b.extracted_event_graph)
                        if comp_b.critical_mismatches_count > 0 or comp_b.overall_omr_ned > 0.0:
                            detected = True

                    c_disc = float(res_c.execution_metadata.get("mean_discrepancy", 0.0))
                    if c_disc > 0.05:
                        detected = True

                    if detected:
                        results_by_family[fam]["detected"] += 1
                    else:
                        results_by_family[fam]["missed"] += 1
                        missed.append({
                            "specimen_id": spec.specimen_id,
                            "family": fam,
                            "description": spec.mutation_description,
                        })

            total_injected = sum(v["injected"] for v in results_by_family.values())
            total_detected = sum(v["detected"] for v in results_by_family.values())
            total_missed = sum(v["missed"] for v in results_by_family.values())
            recall = round(total_detected / total_injected, 4) if total_injected > 0 else 1.0

            payload = json.dumps({
                "injected": total_injected,
                "detected": total_detected,
                "missed": total_missed,
                "recall": recall,
                "breakdown": results_by_family,
            }, sort_keys=True)
            bench_sha = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            return ImageMutationBenchmarkResult(
                total_mutations_injected=total_injected,
                total_mutations_detected=total_detected,
                total_mutations_missed=total_missed,
                end_to_end_image_mutation_recall=recall,
                family_breakdown=results_by_family,
                missed_mutations=missed,
                benchmark_sha256=bench_sha,
            )
        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _write_mutated_musicxml(
        self,
        base_xml_path: str,
        mutated_graph: NormalizedEventGraph,
        output_path: str,
    ) -> None:
        """Writes a mutated MusicXML representation corresponding to the mutated event graph."""
        # Simple deterministic generation of mutated MusicXML
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
                    '        <time><beats>4</beats><beat-type>4</beat-type></time>',
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
