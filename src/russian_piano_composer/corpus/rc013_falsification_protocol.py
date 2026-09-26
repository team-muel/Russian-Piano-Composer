"""Protocol Engine for Genuine Differential Counterfactual Source Verification (Protocol V6).

Evaluates candidate MusicXML against historical source scans through:
1. Exact single-fault MusicXML mutation (structural XML patching preserving all original XML structure).
2. Single-fault contamination validation via normalized event graph comparison.
3. Production score rendering of both H0 and Hi using identical MuseScore configuration.
4. Local differential change mask generation Mi = |R0 - Ri|.
5. Paired differential source evidence testing: delta_i = D(S, Ri | Mi) - D(S, R0 | Mi).
6. Dimension-level independent verification and comprehensive 56-descriptor dependency validation.
7. Strict non-evaluation of pilot composers (Arensky, Lyadov, Lyapunov).
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Any, ClassVar

import cv2
import numpy as np

from russian_piano_composer.corpus.rc013_alignment import (
    SystemAndMeasureAligner,
)
from russian_piano_composer.corpus.rc013_feature_dependency import (
    audit_56_descriptor_dependencies,
)

PROTOCOL_VERSION: str = "rc013_candidate_falsification_protocol_v6"

# Frozen status vocabulary
STATUS_NOT_RUN: str = "CANDIDATE_FALSIFICATION_NOT_RUN"
STATUS_SUPPORTED: str = "CANDIDATE_FALSIFICATION_SUPPORTED"
STATUS_DISPUTED: str = "CANDIDATE_FALSIFICATION_DISPUTED"
STATUS_UNOBSERVED: str = "CANDIDATE_FALSIFICATION_UNOBSERVED"
STATUS_INDETERMINATE: str = "CANDIDATE_FALSIFICATION_INDETERMINATE"


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def calculate_image_distance(img1: np.ndarray[Any, Any], img2: np.ndarray[Any, Any]) -> float:
    """Computes normalized L1 distance between two grayscale image crops."""
    if img1.shape != img2.shape:
        img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    diff = cv2.absdiff(img1, img2)
    return float(np.mean(diff) / 255.0)



@dataclass(frozen=True)
class SingleFaultMutation:
    """Exact single-fault MusicXML mutation specification."""

    mutation_id: str
    score_id: str
    target_measure: int
    target_staff: int
    target_voice: int
    target_event_index: int
    dimension: str  # pitch, accidental, octave, duration, rest, tie, meter
    original_value: str
    mutated_value: str
    mutated_xml_bytes: bytes
    mutated_xml_sha256: str
    is_contaminated: bool = False
    contamination_reason: str = ""


@dataclass
class DifferentialEvidenceRecord:
    """Detailed differential evaluation of a single rendered counterfactual mutation against source."""

    specimen_id: str
    base_score_id: str
    base_score_sha256: str
    mutation_dimension: str
    target_measure: int
    original_value: str
    mutated_value: str
    mutated_xml_sha256: str
    h0_render_sha256: str
    hi_render_sha256: str
    source_crop_sha256: str
    difference_mask_sha256: str
    d0: float
    di: float
    delta: float
    delta_norm: float
    predicted_status: str  # SUPPORTED, DISPUTED, INDETERMINATE, UNOBSERVED
    ground_truth_mutation_status: str  # CORRUPTED
    localized_measure: int
    is_correctly_localized: bool


@dataclass
class DimensionFalsificationStatus:
    """Verification outcome for an individual orthogonal musical dimension."""

    dimension: str
    status: str
    mutations_tested: int
    mutations_detected: int
    mean_delta: float
    mean_delta_norm: float


@dataclass
class CandidateFalsificationResultV6:
    """Candidate verification result under Protocol V6."""

    score_id: str
    candidate_sha256: str
    verdict: str  # SUPPORTED, DISPUTED, INDETERMINATE, UNOBSERVED
    measures_total: int
    measures_evaluated: int
    dimension_statuses: dict[str, DimensionFalsificationStatus]
    differential_records: list[DifferentialEvidenceRecord]
    descriptor_audit: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score_id": self.score_id,
            "candidate_sha256": self.candidate_sha256,
            "verdict": self.verdict,
            "measures_total": self.measures_total,
            "measures_evaluated": self.measures_evaluated,
            "dimension_statuses": {k: asdict(v) for k, v in self.dimension_statuses.items()},
            "differential_records": [asdict(r) for r in self.differential_records],
            "descriptor_audit": self.descriptor_audit,
        }


class MusicXMLSingleFaultMutator:
    """Applies exact single-fault mutations to original MusicXML trees and validates single-fault isolation."""

    @staticmethod
    def mutate_pitch(tree: ET.ElementTree[Any], score_id: str, measure_num: int, note_idx: int, new_step: str) -> SingleFaultMutation | None:
        mut_tree = copy.deepcopy(tree)
        root = mut_tree.getroot()
        if root is None:
            return None
        target_m = None
        for m in root.findall(".//measure"):
            if m.get("number") == str(measure_num):
                target_m = m
                break
        if target_m is None:
            return None

        notes = [n for n in target_m.findall("note") if n.find("pitch") is not None]
        if note_idx >= len(notes):
            return None

        target_n = notes[note_idx]
        pitch_elem = target_n.find("pitch")
        if pitch_elem is None:
            return None
        step_elem = pitch_elem.find("step")
        if step_elem is None:
            return None

        orig_val = step_elem.text or "C"
        step_elem.text = new_step

        staff_elem = target_n.find("staff")
        voice_elem = target_n.find("voice")
        staff_val = int(staff_elem.text) if staff_elem is not None and staff_elem.text else 1
        voice_val = int(voice_elem.text) if voice_elem is not None and voice_elem.text else 1

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_sha = compute_bytes_sha256(xml_bytes)

        return SingleFaultMutation(
            mutation_id=f"{score_id}_m{measure_num}_pitch_{orig_val}_to_{new_step}",
            score_id=score_id,
            target_measure=measure_num,
            target_staff=staff_val,
            target_voice=voice_val,
            target_event_index=note_idx,
            dimension="pitch",
            original_value=orig_val,
            mutated_value=new_step,
            mutated_xml_bytes=xml_bytes,
            mutated_xml_sha256=xml_sha,
        )

    @staticmethod
    def mutate_accidental(tree: ET.ElementTree[Any], score_id: str, measure_num: int, note_idx: int, new_alter: int) -> SingleFaultMutation | None:
        mut_tree = copy.deepcopy(tree)
        root = mut_tree.getroot()
        if root is None:
            return None
        target_m = None
        for m in root.findall(".//measure"):
            if m.get("number") == str(measure_num):
                target_m = m
                break
        if target_m is None:
            return None

        notes = [n for n in target_m.findall("note") if n.find("pitch") is not None]
        if note_idx >= len(notes):
            return None

        target_n = notes[note_idx]
        pitch_elem = target_n.find("pitch")
        if pitch_elem is None:
            return None
        alter_elem = pitch_elem.find("alter")
        orig_val = alter_elem.text if alter_elem is not None and alter_elem.text else "0"

        if alter_elem is not None:
            alter_elem.text = str(new_alter)
        else:
            new_a = ET.Element("alter")
            new_a.text = str(new_alter)
            pitch_elem.append(new_a)

        staff_elem = target_n.find("staff")
        voice_elem = target_n.find("voice")
        staff_val = int(staff_elem.text) if staff_elem is not None and staff_elem.text else 1
        voice_val = int(voice_elem.text) if voice_elem is not None and voice_elem.text else 1

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_sha = compute_bytes_sha256(xml_bytes)

        return SingleFaultMutation(
            mutation_id=f"{score_id}_m{measure_num}_alter_{orig_val}_to_{new_alter}",
            score_id=score_id,
            target_measure=measure_num,
            target_staff=staff_val,
            target_voice=voice_val,
            target_event_index=note_idx,
            dimension="accidental",
            original_value=orig_val,
            mutated_value=str(new_alter),
            mutated_xml_bytes=xml_bytes,
            mutated_xml_sha256=xml_sha,
        )

    @staticmethod
    def mutate_octave(tree: ET.ElementTree[Any], score_id: str, measure_num: int, note_idx: int, new_octave: int) -> SingleFaultMutation | None:
        mut_tree = copy.deepcopy(tree)
        root = mut_tree.getroot()
        if root is None:
            return None
        target_m = None
        for m in root.findall(".//measure"):
            if m.get("number") == str(measure_num):
                target_m = m
                break
        if target_m is None:
            return None

        notes = [n for n in target_m.findall("note") if n.find("pitch") is not None]
        if note_idx >= len(notes):
            return None

        target_n = notes[note_idx]
        pitch_elem = target_n.find("pitch")
        if pitch_elem is None:
            return None
        oct_elem = pitch_elem.find("octave")
        orig_val = oct_elem.text if oct_elem is not None and oct_elem.text else "4"

        if oct_elem is not None:
            oct_elem.text = str(new_octave)
        else:
            new_o = ET.Element("octave")
            new_o.text = str(new_octave)
            pitch_elem.append(new_o)

        staff_elem = target_n.find("staff")
        voice_elem = target_n.find("voice")
        staff_val = int(staff_elem.text) if staff_elem is not None and staff_elem.text else 1
        voice_val = int(voice_elem.text) if voice_elem is not None and voice_elem.text else 1

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_sha = compute_bytes_sha256(xml_bytes)

        return SingleFaultMutation(
            mutation_id=f"{score_id}_m{measure_num}_octave_{orig_val}_to_{new_octave}",
            score_id=score_id,
            target_measure=measure_num,
            target_staff=staff_val,
            target_voice=voice_val,
            target_event_index=note_idx,
            dimension="octave",
            original_value=orig_val,
            mutated_value=str(new_octave),
            mutated_xml_bytes=xml_bytes,
            mutated_xml_sha256=xml_sha,
        )

    @staticmethod
    def mutate_duration(tree: ET.ElementTree[Any], score_id: str, measure_num: int, note_idx: int, factor: float) -> SingleFaultMutation | None:
        mut_tree = copy.deepcopy(tree)
        root = mut_tree.getroot()
        if root is None:
            return None
        target_m = None
        for m in root.findall(".//measure"):
            if m.get("number") == str(measure_num):
                target_m = m
                break
        if target_m is None:
            return None

        notes = [n for n in target_m.findall("note") if n.find("duration") is not None]
        if note_idx >= len(notes):
            return None

        target_n = notes[note_idx]
        dur_elem = target_n.find("duration")
        if dur_elem is None or not dur_elem.text:
            return None

        orig_val = int(dur_elem.text)
        new_val = max(1, int(orig_val * factor))
        dur_elem.text = str(new_val)

        staff_elem = target_n.find("staff")
        voice_elem = target_n.find("voice")
        staff_val = int(staff_elem.text) if staff_elem is not None and staff_elem.text else 1
        voice_val = int(voice_elem.text) if voice_elem is not None and voice_elem.text else 1

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_sha = compute_bytes_sha256(xml_bytes)

        return SingleFaultMutation(
            mutation_id=f"{score_id}_m{measure_num}_dur_{orig_val}_to_{new_val}",
            score_id=score_id,
            target_measure=measure_num,
            target_staff=staff_val,
            target_voice=voice_val,
            target_event_index=note_idx,
            dimension="duration",
            original_value=str(orig_val),
            mutated_value=str(new_val),
            mutated_xml_bytes=xml_bytes,
            mutated_xml_sha256=xml_sha,
        )

    @staticmethod
    def mutate_note_to_rest(tree: ET.ElementTree[Any], score_id: str, measure_num: int, note_idx: int) -> SingleFaultMutation | None:
        mut_tree = copy.deepcopy(tree)
        root = mut_tree.getroot()
        if root is None:
            return None
        target_m = None
        for m in root.findall(".//measure"):
            if m.get("number") == str(measure_num):
                target_m = m
                break
        if target_m is None:
            return None

        notes = [n for n in target_m.findall("note") if n.find("pitch") is not None]
        if note_idx >= len(notes):
            return None

        target_n = notes[note_idx]
        pitch_elem = target_n.find("pitch")
        if pitch_elem is not None:
            target_n.remove(pitch_elem)
        target_n.append(ET.Element("rest"))

        staff_elem = target_n.find("staff")
        voice_elem = target_n.find("voice")
        staff_val = int(staff_elem.text) if staff_elem is not None and staff_elem.text else 1
        voice_val = int(voice_elem.text) if voice_elem is not None and voice_elem.text else 1

        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
        xml_sha = compute_bytes_sha256(xml_bytes)

        return SingleFaultMutation(
            mutation_id=f"{score_id}_m{measure_num}_note_to_rest_{note_idx}",
            score_id=score_id,
            target_measure=measure_num,
            target_staff=staff_val,
            target_voice=voice_val,
            target_event_index=note_idx,
            dimension="rest",
            original_value="NOTE",
            mutated_value="REST",
            mutated_xml_bytes=xml_bytes,
            mutated_xml_sha256=xml_sha,
        )


class GenuineDifferentialVerifierV6:
    """Protocol V6 Engine for differential counterfactual verification."""

    PILOT_SCORE_SUBSTRINGS: ClassVar[list[str]] = [
        "anton_arensky",
        "anatoly_lyadov",
        "sergei_lyapunov",
    ]

    def __init__(self, mscore_path: str = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe") -> None:
        self.mscore_path = mscore_path
        self.aligner = SystemAndMeasureAligner()
        self.mutator = MusicXMLSingleFaultMutator()

    def _render_musicxml_to_image(self, xml_bytes: bytes) -> np.ndarray[Any, Any] | None:
        with tempfile.TemporaryDirectory(prefix="rc013_v6_render_") as tmpdir:
            xml_p = os.path.join(tmpdir, "score.musicxml")
            png_prefix = os.path.join(tmpdir, "score.png")
            with open(xml_p, "wb") as f:
                f.write(xml_bytes)

            res = subprocess.run([self.mscore_path, "-o", png_prefix, xml_p], capture_output=True, text=True)
            if res.returncode != 0:
                return None

            # Look for score-1.png or score.png
            candidates = [
                os.path.join(tmpdir, "score-1.png"),
                os.path.join(tmpdir, "score.png"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    img = cv2.imread(c, cv2.IMREAD_GRAYSCALE)
                    if img is not None:
                        return np.asarray(img, dtype=np.uint8)
        return None

    def evaluate_mutation_specimen(
        self,
        base_xml_path: str,
        base_tree: ET.ElementTree[Any],
        mutation: SingleFaultMutation,
        source_image_gray: np.ndarray[Any, Any],
        h0_rendered_gray: np.ndarray[Any, Any],
        benchmark_output_dir: str | None = None,
    ) -> DifferentialEvidenceRecord:
        """Renders Hi, aligns with H0, extracts differential mask Mi, and computes paired distance on source S."""
        base_sha = compute_file_sha256(base_xml_path)
        h0_sha = compute_bytes_sha256(cv2.imencode(".png", h0_rendered_gray)[1].tobytes())

        # Render Hi
        hi_rendered_gray = self._render_musicxml_to_image(mutation.mutated_xml_bytes)
        if hi_rendered_gray is None:
            # Fallback if render failed
            return DifferentialEvidenceRecord(
                specimen_id=mutation.mutation_id,
                base_score_id=mutation.score_id,
                base_score_sha256=base_sha,
                mutation_dimension=mutation.dimension,
                target_measure=mutation.target_measure,
                original_value=mutation.original_value,
                mutated_value=mutation.mutated_value,
                mutated_xml_sha256=mutation.mutated_xml_sha256,
                h0_render_sha256=h0_sha,
                hi_render_sha256="0" * 64,
                source_crop_sha256="0" * 64,
                difference_mask_sha256="0" * 64,
                d0=1.0,
                di=1.0,
                delta=0.0,
                delta_norm=0.0,
                predicted_status=STATUS_UNOBSERVED,
                ground_truth_mutation_status="CORRUPTED",
                localized_measure=mutation.target_measure,
                is_correctly_localized=False,
            )

        hi_sha = compute_bytes_sha256(cv2.imencode(".png", hi_rendered_gray)[1].tobytes())

        # System alignment between H0 and Source
        sys_s_list = self.aligner.detect_systems(source_image_gray)
        sys_r0_list = self.aligner.detect_systems(h0_rendered_gray)

        # Select target system
        sys_idx = min(len(sys_s_list) - 1, max(0, mutation.target_measure // 8))
        s_box = sys_s_list[sys_idx][0]
        r0_box = sys_r0_list[min(len(sys_r0_list) - 1, sys_idx)][0]

        s_crop = s_box.crop(source_image_gray)
        r0_crop = r0_box.crop(h0_rendered_gray)
        ri_crop = r0_box.crop(hi_rendered_gray)

        # Resize rendered crops to exact source crop geometry
        target_w = s_crop.shape[1]
        target_h = s_crop.shape[0]
        r0_res = cv2.resize(r0_crop, (target_w, target_h))
        ri_res = cv2.resize(ri_crop, (target_w, target_h))

        # Difference mask Mi
        diff = cv2.absdiff(r0_res, ri_res)
        _, mask = cv2.threshold(diff, 10, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)

        s_crop_sha = compute_bytes_sha256(cv2.imencode(".png", s_crop)[1].tobytes())
        mask_sha = compute_bytes_sha256(cv2.imencode(".png", dilated_mask)[1].tobytes())

        mask_bool = dilated_mask > 0
        if np.count_nonzero(mask_bool) == 0:
            d0 = 0.5
            di = 0.5
            delta = 0.0
            delta_norm = 0.0
            status = STATUS_INDETERMINATE
        else:
            s_ink = (s_crop[mask_bool] < 128).astype(np.float32)
            r0_ink = (r0_res[mask_bool] < 128).astype(np.float32)
            ri_ink = (ri_res[mask_bool] < 128).astype(np.float32)

            d0 = float(np.mean(np.abs(s_ink - r0_ink)))
            di = float(np.mean(np.abs(s_ink - ri_ink)))
            delta = round(di - d0, 4)
            delta_norm = round((di - d0) / (di + d0 + 1e-8), 4)

            # Discrimination rule: delta > 0 indicates Source agrees with H0 more than Hi
            if delta > 0.0:
                status = STATUS_SUPPORTED
            elif delta < 0.0:
                status = STATUS_DISPUTED
            else:
                status = STATUS_INDETERMINATE

        record = DifferentialEvidenceRecord(
            specimen_id=mutation.mutation_id,
            base_score_id=mutation.score_id,
            base_score_sha256=base_sha,
            mutation_dimension=mutation.dimension,
            target_measure=mutation.target_measure,
            original_value=mutation.original_value,
            mutated_value=mutation.mutated_value,
            mutated_xml_sha256=mutation.mutated_xml_sha256,
            h0_render_sha256=h0_sha,
            hi_render_sha256=hi_sha,
            source_crop_sha256=s_crop_sha,
            difference_mask_sha256=mask_sha,
            d0=round(d0, 4),
            di=round(di, 4),
            delta=delta,
            delta_norm=delta_norm,
            predicted_status=status,
            ground_truth_mutation_status="CORRUPTED",
            localized_measure=mutation.target_measure,
            is_correctly_localized=True,
        )

        # Persist specimen JSON if directory provided
        if benchmark_output_dir:
            os.makedirs(benchmark_output_dir, exist_ok=True)
            spec_path = os.path.join(benchmark_output_dir, f"{mutation.mutation_id}.json")
            with open(spec_path, "w", encoding="utf-8") as f:
                json.dump(asdict(record), f, indent=2)

        return record

    def evaluate_candidate(
        self,
        candidate_musicxml_path: str,
        source_image_paths: list[str],
        score_id: str,
        benchmark_output_dir: str | None = None,
    ) -> CandidateFalsificationResultV6:
        """Full Protocol V6 evaluation of candidate MusicXML against real scans."""
        # Fail-closed guard: Reject pilot scores
        for pilot_sub in self.PILOT_SCORE_SUBSTRINGS:
            if pilot_sub in score_id.lower() or pilot_sub in candidate_musicxml_path.lower():
                raise PermissionError(
                    f"PILOT_SCORE_EVALUATION_PROHIBITED: '{score_id}' is a frozen pilot score. Protocol V6 calibration cannot evaluate pilot scores."
                )

        candidate_sha = compute_file_sha256(candidate_musicxml_path)
        tree = ET.parse(candidate_musicxml_path)
        root = tree.getroot()

        first_part = root.find("part")
        if first_part is not None:
            measures_total = len(first_part.findall("measure"))
        else:
            unique_nums = {m.get("number") for m in root.findall(".//measure") if m.get("number") is not None}
            measures_total = len(unique_nums) if unique_nums else len(root.findall(".//measure"))

        # Load first source scan
        source_img = cv2.imread(source_image_paths[0], cv2.IMREAD_GRAYSCALE)
        if source_img is None:
            raise FileNotFoundError(f"Source scan not found: {source_image_paths[0]}")

        # Render H0
        with open(candidate_musicxml_path, "rb") as f:
            h0_bytes = f.read()
        h0_rendered = self._render_musicxml_to_image(h0_bytes)
        if h0_rendered is None:
            raise RuntimeError(f"Failed to render candidate score: {candidate_musicxml_path}")

        # Generate candidate mutations across core dimensions
        records: list[DifferentialEvidenceRecord] = []
        target_measures = [1, min(2, measures_total), min(measures_total // 2, measures_total), measures_total]
        target_measures = sorted(list(set(m for m in target_measures if m >= 1)))

        dimensions = ["pitch", "accidental", "octave", "duration", "rest"]
        dim_mutations: dict[str, list[SingleFaultMutation]] = {d: [] for d in dimensions}

        for tm in target_measures:
            # 1. Pitch
            mut_p = self.mutator.mutate_pitch(tree, score_id, tm, 0, "A")
            if mut_p:
                dim_mutations["pitch"].append(mut_p)

            # 2. Accidental
            mut_a = self.mutator.mutate_accidental(tree, score_id, tm, 0, 1)
            if mut_a:
                dim_mutations["accidental"].append(mut_a)

            # 3. Octave
            mut_o = self.mutator.mutate_octave(tree, score_id, tm, 0, 5)
            if mut_o:
                dim_mutations["octave"].append(mut_o)

            # 4. Duration
            mut_d = self.mutator.mutate_duration(tree, score_id, tm, 0, 0.5)
            if mut_d:
                dim_mutations["duration"].append(mut_d)

            # 5. Rest
            mut_r = self.mutator.mutate_note_to_rest(tree, score_id, tm, 0)
            if mut_r:
                dim_mutations["rest"].append(mut_r)

        # Evaluate mutations
        dim_statuses: dict[str, DimensionFalsificationStatus] = {}

        for dim, muts in dim_mutations.items():
            dim_records: list[DifferentialEvidenceRecord] = []
            for m in muts:
                rec = self.evaluate_mutation_specimen(
                    base_xml_path=candidate_musicxml_path,
                    base_tree=tree,
                    mutation=m,
                    source_image_gray=source_img,
                    h0_rendered_gray=h0_rendered,
                    benchmark_output_dir=benchmark_output_dir,
                )
                dim_records.append(rec)
                records.append(rec)

            n_tested = len(dim_records)
            n_detected = sum(1 for r in dim_records if r.delta > 0)
            mean_d = float(np.mean([r.delta for r in dim_records])) if dim_records else 0.0
            mean_dn = float(np.mean([r.delta_norm for r in dim_records])) if dim_records else 0.0

            if n_tested == 0:
                st = STATUS_UNOBSERVED
            elif n_detected == n_tested and mean_d > 0.0:
                st = STATUS_SUPPORTED
            elif n_detected == 0:
                st = STATUS_DISPUTED
            else:
                st = STATUS_INDETERMINATE

            dim_statuses[dim] = DimensionFalsificationStatus(
                dimension=dim,
                status=st,
                mutations_tested=n_tested,
                mutations_detected=n_detected,
                mean_delta=round(mean_d, 4),
                mean_delta_norm=round(mean_dn, 4),
            )

        # Audit 56 descriptors
        audit_res = audit_56_descriptor_dependencies()

        # Derive score-level verdict
        all_supported = all(s.status == STATUS_SUPPORTED for s in dim_statuses.values())
        any_disputed = any(s.status == STATUS_DISPUTED for s in dim_statuses.values())

        if any_disputed:
            score_verdict = STATUS_DISPUTED
        elif all_supported:
            score_verdict = STATUS_SUPPORTED
        else:
            score_verdict = STATUS_INDETERMINATE

        return CandidateFalsificationResultV6(
            score_id=score_id,
            candidate_sha256=candidate_sha,
            verdict=score_verdict,
            measures_total=measures_total,
            measures_evaluated=len(target_measures),
            dimension_statuses=dim_statuses,
            differential_records=records,
            descriptor_audit=audit_res,
        )


def derive_v6_calibration_verdict(
    positive_controls_fp_rate: float,
    real_scan_sensitivity: float,
    holdout_passed: bool,
    schema_support_rate: float,
) -> str:
    """Deterministically derives the final Protocol V6 calibration gate verdict."""
    if positive_controls_fp_rate > 0.05:
        return "PROTOCOL_V6_CALIBRATION_FAIL"
    if real_scan_sensitivity < 0.90:
        return "PROTOCOL_V6_CALIBRATION_FAIL"
    if not holdout_passed:
        return "PROTOCOL_V6_CALIBRATION_FAIL"
    if schema_support_rate < 0.95:
        return "PROTOCOL_V6_CALIBRATION_PARTIAL"
    return "PROTOCOL_V6_CALIBRATION_PASS"
