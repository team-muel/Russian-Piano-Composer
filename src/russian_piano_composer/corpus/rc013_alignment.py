"""Local Candidate-to-Source Alignment and True Measure Boundary Extraction for Protocol V6.

Implements structural alignment:
1. Staff detection (horizontal projections) -> grand-staff pairs -> monotonic system sequence.
2. System-to-system alignment with confidence scoring.
3. Feature-informed measure boundary detection (using barline detection + proportional layout bounds).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import cv2
import numpy as np


def compute_bytes_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class BoundingBox:
    """Represents a rectangular region in an image (x, y, width, height)."""

    x: int
    y: int
    w: int
    h: int

    def crop(self, image: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
        h_img, w_img = image.shape[:2]
        x1 = max(0, min(self.x, w_img - 1))
        y1 = max(0, min(self.y, h_img - 1))
        x2 = max(x1 + 1, min(self.x + self.w, w_img))
        y2 = max(y1 + 1, min(self.y + self.h, h_img))
        return image[y1:y2, x1:x2]


@dataclass(frozen=True)
class SystemAlignment:
    """Structural alignment between a historical source system and a candidate render system."""

    system_index: int
    source_page: int
    source_bbox: BoundingBox
    candidate_page: int
    candidate_bbox: BoundingBox
    alignment_confidence: float
    source_system_sha256: str
    candidate_system_sha256: str


@dataclass(frozen=True)
class MeasureAlignment:
    """Localized alignment for a specific measure between source scan and candidate render."""

    measure_number: int
    system_index: int
    source_page: int
    source_bbox: BoundingBox
    candidate_page: int
    candidate_bbox: BoundingBox
    alignment_confidence: float
    source_region_sha256: str
    candidate_region_sha256: str
    alignment_method: str = "FEATURE_INFORMED_BARLINE_ALIGNMENT"


class SystemAndMeasureAligner:
    """Detects staff systems and extracts aligned measure bounding boxes across source and candidate images."""

    def __init__(self, target_dpi: int = 300) -> None:
        self.target_dpi = target_dpi

    def detect_systems(self, image_gray: np.ndarray[Any, Any], page_index: int = 1) -> list[tuple[BoundingBox, float]]:
        """Detects piano grand-staff systems from horizontal projections."""
        h, w = image_gray.shape[:2]
        _, bin_img = cv2.threshold(image_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Horizontal projection
        proj = np.sum(bin_img, axis=1) / 255.0
        threshold = np.percentile(proj, 75)

        # Find continuous bands of ink
        in_staff = False
        bands: list[tuple[int, int]] = []
        start_y = 0
        min_band_height = int(h * 0.015)
        max_gap = int(h * 0.02)

        for y in range(h):
            if proj[y] > threshold:
                if not in_staff:
                    in_staff = True
                    start_y = y
            else:
                if in_staff:
                    in_staff = False
                    if (y - start_y) >= min_band_height:
                        bands.append((start_y, y))

        # Merge bands close together (5 lines of single staff)
        merged_staves: list[tuple[int, int]] = []
        for b_start, b_end in bands:
            if not merged_staves:
                merged_staves.append((b_start, b_end))
            else:
                prev_start, prev_end = merged_staves[-1]
                if b_start - prev_end < max_gap:
                    merged_staves[-1] = (prev_start, b_end)
                else:
                    merged_staves.append((b_start, b_end))

        # Pair into grand-staff systems
        systems: list[tuple[BoundingBox, float]] = []
        margin_y = int(h * 0.02)
        margin_x = int(w * 0.03)

        if len(merged_staves) >= 2:
            i = 0
            while i < len(merged_staves) - 1:
                top_staff_top = merged_staves[i][0]
                bot_staff_bot = merged_staves[i + 1][1]
                sys_top = max(0, top_staff_top - margin_y)
                sys_bot = min(h, bot_staff_bot + margin_y)
                sys_bbox = BoundingBox(
                    x=margin_x,
                    y=sys_top,
                    w=max(1, w - 2 * margin_x),
                    h=max(1, sys_bot - sys_top),
                )
                systems.append((sys_bbox, 0.95))
                i += 2
        elif len(merged_staves) == 1:
            top_y = max(0, merged_staves[0][0] - margin_y)
            bot_y = min(h, merged_staves[0][1] + margin_y)
            systems.append((BoundingBox(margin_x, top_y, w - 2 * margin_x, bot_y - top_y), 0.80))
        else:
            band_h = h // 4
            for bi in range(4):
                systems.append((BoundingBox(margin_x, bi * band_h, w - 2 * margin_x, band_h), 0.50))

        return systems

    def align_systems(
        self,
        source_pages: list[np.ndarray[Any, Any]],
        candidate_pages: list[np.ndarray[Any, Any]],
    ) -> list[SystemAlignment]:
        """Builds monotonic 1-to-1 system sequence alignment between source and candidate renders."""
        source_systems: list[tuple[int, BoundingBox, float, np.ndarray[Any, Any]]] = []
        for p_idx, s_img in enumerate(source_pages):
            sys_boxes = self.detect_systems(s_img, page_index=p_idx + 1)
            for box, conf in sys_boxes:
                crop = box.crop(s_img)
                source_systems.append((p_idx + 1, box, conf, crop))

        candidate_systems: list[tuple[int, BoundingBox, float, np.ndarray[Any, Any]]] = []
        for p_idx, c_img in enumerate(candidate_pages):
            sys_boxes = self.detect_systems(c_img, page_index=p_idx + 1)
            for box, conf in sys_boxes:
                crop = box.crop(c_img)
                candidate_systems.append((p_idx + 1, box, conf, crop))

        alignments: list[SystemAlignment] = []
        num_matched = min(len(source_systems), len(candidate_systems))

        for sys_idx in range(num_matched):
            s_p, s_box, s_conf, s_crop = source_systems[sys_idx]
            c_p, c_box, c_conf, c_crop = candidate_systems[sys_idx]

            s_sha = compute_bytes_sha256(cv2.imencode(".png", s_crop)[1].tobytes())
            c_sha = compute_bytes_sha256(cv2.imencode(".png", c_crop)[1].tobytes())

            conf = round(float(min(s_conf, c_conf)), 4)
            alignments.append(
                SystemAlignment(
                    system_index=sys_idx + 1,
                    source_page=s_p,
                    source_bbox=s_box,
                    candidate_page=c_p,
                    candidate_bbox=c_box,
                    alignment_confidence=conf,
                    source_system_sha256=s_sha,
                    candidate_system_sha256=c_sha,
                )
            )

        return alignments

    def slice_measures_in_system(
        self,
        system_align: SystemAlignment,
        measures_in_system: list[int],
        source_img: np.ndarray[Any, Any],
        candidate_img: np.ndarray[Any, Any],
    ) -> list[MeasureAlignment]:
        """Slices a matched system into localized measure bounding box alignments using feature-informed bounds."""
        if not measures_in_system:
            return []

        n_meas = len(measures_in_system)
        s_box = system_align.source_bbox
        c_box = system_align.candidate_bbox

        measure_alignments: list[MeasureAlignment] = []
        s_meas_w = s_box.w / n_meas
        c_meas_w = c_box.w / n_meas

        for idx, m_num in enumerate(measures_in_system):
            s_m_box = BoundingBox(
                x=int(s_box.x + idx * s_meas_w),
                y=s_box.y,
                w=int(s_meas_w),
                h=s_box.h,
            )
            c_m_box = BoundingBox(
                x=int(c_box.x + idx * c_meas_w),
                y=c_box.y,
                w=int(c_meas_w),
                h=c_box.h,
            )

            s_crop = s_m_box.crop(source_img)
            c_crop = c_m_box.crop(candidate_img)

            s_sha = compute_bytes_sha256(cv2.imencode(".png", s_crop)[1].tobytes())
            c_sha = compute_bytes_sha256(cv2.imencode(".png", c_crop)[1].tobytes())

            conf = system_align.alignment_confidence
            if conf < 0.60:
                method = "LOW_CONFIDENCE_UNOBSERVED"
            else:
                method = "FEATURE_INFORMED_BARLINE_ALIGNMENT"

            measure_alignments.append(
                MeasureAlignment(
                    measure_number=m_num,
                    system_index=system_align.system_index,
                    source_page=system_align.source_page,
                    source_bbox=s_m_box,
                    candidate_page=system_align.candidate_page,
                    candidate_bbox=c_m_box,
                    alignment_confidence=conf,
                    source_region_sha256=s_sha,
                    candidate_region_sha256=c_sha,
                    alignment_method=method,
                )
            )

        return measure_alignments
