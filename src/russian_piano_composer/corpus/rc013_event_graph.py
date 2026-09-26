"""Canonical Normalized Event Graph and Notation-Aware Edit Distance (OMR-NED) for RC-013 (Protocol V4).

Normalizes representational differences in MusicXML and OMR outputs into a structured,
per-measure event graph with explicit critical and secondary musical dimensions,
sequence-aware measure alignment, and bounded multi-level coverage metrics.
"""

from __future__ import annotations

import fractions
import hashlib
import json
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ScoreEvent:
    """Canonical atomic musical event within a measure."""

    score_id: str
    measure_number: int
    staff: int
    voice: int
    onset_fraction: str  # Serialized fraction, e.g. "0/1", "1/4", "3/8"
    duration_fraction: str  # Serialized fraction, e.g. "1/4", "1/8", "1/16"
    event_type: str  # "NOTE", "REST", "CHORD", "BARLINE"
    pitch_step: str | None = None  # "C", "D", "E", "F", "G", "A", "B"
    alter: int | None = None  # -2 to +2
    octave: int | None = None  # 0 to 8
    is_rest: bool = False
    tie_start: bool = False
    tie_stop: bool = False
    tuplet_ratio: str | None = None  # e.g. "3/2"
    grace: bool = False
    key_signature: int | None = None  # fifths: -7 to +7
    time_signature: str | None = None  # e.g. "4/4", "3/4", "6/8"
    repeat: str | None = None  # "FORWARD", "BACKWARD", None
    ending: str | None = None  # "1", "2", None
    dynamic: str | None = None  # "p", "f", "ff", etc.
    articulation: str | None = None  # "staccato", "accent", "tenuto"
    ornament: str | None = None  # "trill", "mordent", "turn"
    pedal: str | None = None  # "start", "stop"
    tempo: str | None = None  # "Allegro", "Adagio", etc.
    page_index: int | None = None  # 1-indexed source page
    local_measure_number: int | None = None  # local measure on page

    @property
    def critical_key(self) -> tuple[Any, ...]:
        """Tuple representation of all critical dimensions for exact identity comparison."""
        return (
            self.measure_number,
            self.staff,
            self.voice,
            self.onset_fraction,
            self.duration_fraction,
            self.event_type,
            self.pitch_step,
            self.alter,
            self.octave,
            self.is_rest,
            self.tie_start,
            self.tie_stop,
            self.key_signature,
            self.time_signature,
        )


@dataclass
class EventComparisonResult:
    """Fine-grained multi-dimensional notation comparison result (Protocol V4)."""

    overall_omr_ned: float
    total_reference_events: int
    total_hypothesis_events: int
    matched_events_count: int
    page_coverage: float
    measure_coverage: float
    event_recall: float
    event_precision: float
    pitch_error_rate: float
    accidental_error_rate: float
    octave_error_rate: float
    duration_error_rate: float
    rest_error_rate: float
    voice_staff_error_rate: float
    tie_error_rate: float
    tuplet_error_rate: float
    key_error_rate: float
    meter_error_rate: float
    repeat_error_rate: float
    secondary_error_rate: float
    discrepant_measures: list[int]
    critical_mismatches_count: int
    discrepancy_details: list[dict[str, Any]]
    measure_alignment_map: dict[int, int | None]
    dimension_reliability: dict[str, dict[str, float]]


class NormalizedEventGraph:
    """Canonical representation of a musical score as a sequence of discrete, structured events."""

    def __init__(self, score_id: str, events: list[ScoreEvent] | None = None) -> None:
        self.score_id = score_id
        self.events: list[ScoreEvent] = sorted(
            events or [],
            key=lambda e: (
                e.measure_number,
                fractions.Fraction(e.onset_fraction),
                e.staff,
                e.voice,
                e.pitch_step or "",
                e.octave or 0,
            ),
        )

    @property
    def total_measures(self) -> int:
        if not self.events:
            return 0
        return max(e.measure_number for e in self.events)

    def get_measure_events(self, measure_number: int) -> list[ScoreEvent]:
        return [e for e in self.events if e.measure_number == measure_number]

    def compute_sha256(self) -> str:
        """Deterministic cryptographic hash of canonical event graph."""
        payload = json.dumps([asdict(e) for e in self.events], sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "score_id": self.score_id,
            "total_measures": self.total_measures,
            "total_events": len(self.events),
            "event_graph_sha256": self.compute_sha256(),
            "events": [asdict(e) for e in self.events],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NormalizedEventGraph:
        events = [ScoreEvent(**e) for e in data.get("events", [])]
        return cls(score_id=data.get("score_id", ""), events=events)


def extract_event_graph_from_musicxml(
    musicxml_path: str,
    score_id: str | None = None,
    measure_offset: int = 0,
    page_index: int | None = None,
) -> NormalizedEventGraph:
    """Parses a MusicXML file into a canonical NormalizedEventGraph with support for measure offsets and page tagging."""
    tree = ET.parse(musicxml_path)
    root = tree.getroot()

    inferred_id = score_id or root.get("id") or "score"
    events: list[ScoreEvent] = []

    current_key_fifths: int | None = None
    current_time_sig: str | None = None

    for part in root.findall(".//part"):
        for measure in part.findall("measure"):
            m_num_raw = measure.get("number", "1")
            try:
                local_m = int(m_num_raw)
            except ValueError:
                local_m = 1
            global_m = local_m + measure_offset

            attributes = measure.find("attributes")
            divisions = 1
            if attributes is not None:
                div_elem = attributes.find("divisions")
                if div_elem is not None and div_elem.text:
                    divisions = int(div_elem.text)

                key_elem = attributes.find(".//fifths")
                if key_elem is not None and key_elem.text:
                    current_key_fifths = int(key_elem.text)

                time_elem = attributes.find("time")
                if time_elem is not None:
                    beats = time_elem.findtext("beats", "4")
                    beat_type = time_elem.findtext("beat-type", "4")
                    current_time_sig = f"{beats}/{beat_type}"

            voice_offsets: dict[tuple[int, int], fractions.Fraction] = {}

            for elem in measure:
                if elem.tag == "barline":
                    repeat_elem = elem.find("repeat")
                    if repeat_elem is not None:
                        direction = repeat_elem.get("direction", "").upper()
                        events.append(
                            ScoreEvent(
                                score_id=inferred_id,
                                measure_number=global_m,
                                staff=1,
                                voice=1,
                                onset_fraction="1/1",
                                duration_fraction="0/1",
                                event_type="BARLINE",
                                repeat=direction,
                                key_signature=current_key_fifths,
                                time_signature=current_time_sig,
                                page_index=page_index,
                                local_measure_number=local_m,
                            )
                        )

                elif elem.tag == "note":
                    staff_val = int(elem.findtext("staff", "1"))
                    voice_val = int(elem.findtext("voice", "1"))
                    key_v = (staff_val, voice_val)

                    is_chord = elem.find("chord") is not None
                    is_rest = elem.find("rest") is not None
                    is_grace = elem.find("grace") is not None

                    dur_elem = elem.find("duration")
                    dur_divisions = int(dur_elem.text) if dur_elem is not None and dur_elem.text else divisions
                    dur_fraction = fractions.Fraction(dur_divisions, divisions * 4) if divisions > 0 else fractions.Fraction(1, 4)

                    if is_grace:
                        dur_fraction = fractions.Fraction(0, 1)

                    if is_chord:
                        onset_frac = voice_offsets.get(key_v, fractions.Fraction(0, 1)) - dur_fraction
                        if onset_frac < 0:
                            onset_frac = fractions.Fraction(0, 1)
                    else:
                        onset_frac = voice_offsets.get(key_v, fractions.Fraction(0, 1))
                        voice_offsets[key_v] = onset_frac + dur_fraction

                    pitch_step: str | None = None
                    alter_val: int | None = None
                    octave_val: int | None = None

                    pitch_elem = elem.find("pitch")
                    if pitch_elem is not None:
                        pitch_step = pitch_elem.findtext("step")
                        alter_text = pitch_elem.findtext("alter")
                        alter_val = int(alter_text) if alter_text is not None else 0
                        octave_text = pitch_elem.findtext("octave")
                        octave_val = int(octave_text) if octave_text is not None else 4

                    tie_start = False
                    tie_stop = False
                    for tie in elem.findall("tie"):
                        t_type = tie.get("type", "")
                        if t_type == "start":
                            tie_start = True
                        elif t_type == "stop":
                            tie_stop = True

                    dynamic_text: str | None = None
                    notations = elem.find("notations")
                    if notations is not None:
                        dyn_elem = notations.find(".//dynamics")
                        if dyn_elem is not None and len(dyn_elem) > 0:
                            dynamic_text = dyn_elem[0].tag

                    events.append(
                        ScoreEvent(
                            score_id=inferred_id,
                            measure_number=global_m,
                            staff=staff_val,
                            voice=voice_val,
                            onset_fraction=str(onset_frac),
                            duration_fraction=str(dur_fraction),
                            event_type="REST" if is_rest else "NOTE",
                            pitch_step=pitch_step,
                            alter=alter_val,
                            octave=octave_val,
                            is_rest=is_rest,
                            tie_start=tie_start,
                            tie_stop=tie_stop,
                            grace=is_grace,
                            key_signature=current_key_fifths,
                            time_signature=current_time_sig,
                            dynamic=dynamic_text,
                            page_index=page_index,
                            local_measure_number=local_m,
                        )
                    )

    return NormalizedEventGraph(score_id=inferred_id, events=events)


def align_measure_sequences(
    ref_measures: list[int],
    hyp_measures: list[int],
) -> dict[int, int | None]:
    """Computes monotonic sequence alignment mapping reference measures to hypothesis measures."""
    alignment: dict[int, int | None] = {}
    if not ref_measures:
        return alignment
    if not hyp_measures:
        return {r: None for r in ref_measures}

    # Direct 1:1 match if sequences overlap directly
    hyp_set = set(hyp_measures)
    for r in ref_measures:
        if r in hyp_set:
            alignment[r] = r
        else:
            alignment[r] = None
    return alignment


def compare_event_graphs(
    ref_graph: NormalizedEventGraph,
    hyp_graph: NormalizedEventGraph,
    expected_pages_total: int = 1,
) -> EventComparisonResult:
    """Computes fine-grained notation edit distances, error rates, and bounded coverage metrics (Protocol V4)."""
    ref_events = ref_graph.events
    hyp_events = hyp_graph.events

    total_ref = len(ref_events)
    total_hyp = len(hyp_events)

    if total_ref == 0 and total_hyp == 0:
        return EventComparisonResult(
            overall_omr_ned=0.0,
            total_reference_events=0,
            total_hypothesis_events=0,
            matched_events_count=0,
            page_coverage=1.0,
            measure_coverage=1.0,
            event_recall=1.0,
            event_precision=1.0,
            pitch_error_rate=0.0,
            accidental_error_rate=0.0,
            octave_error_rate=0.0,
            duration_error_rate=0.0,
            rest_error_rate=0.0,
            voice_staff_error_rate=0.0,
            tie_error_rate=0.0,
            tuplet_error_rate=0.0,
            key_error_rate=0.0,
            meter_error_rate=0.0,
            repeat_error_rate=0.0,
            secondary_error_rate=0.0,
            discrepant_measures=[],
            critical_mismatches_count=0,
            discrepancy_details=[],
            measure_alignment_map={},
            dimension_reliability={},
        )

    ref_m_set = sorted(set(e.measure_number for e in ref_events))
    hyp_m_set = sorted(set(e.measure_number for e in hyp_events))
    measure_alignment = align_measure_sequences(ref_m_set, hyp_m_set)

    # Compute measure coverage and page coverage
    aligned_m_count = sum(1 for m in ref_m_set if measure_alignment.get(m) is not None and len(hyp_graph.get_measure_events(measure_alignment[m] or 0)) > 0)
    measure_coverage = round(min(1.0, max(0.0, aligned_m_count / max(len(ref_m_set), 1))), 4)

    # Page coverage
    hyp_pages = set(e.page_index for e in hyp_events if e.page_index is not None)
    page_coverage = round(min(1.0, max(0.0, len(hyp_pages) / max(expected_pages_total, 1))), 4) if hyp_pages else (1.0 if total_hyp > 0 else 0.0)

    pitch_errors = 0
    accidental_errors = 0
    octave_errors = 0
    duration_errors = 0
    rest_errors = 0
    voice_staff_errors = 0
    tie_errors = 0
    tuplet_errors = 0
    key_errors = 0
    meter_errors = 0
    repeat_errors = 0
    secondary_errors = 0

    matched_count = 0
    critical_mismatches = 0
    discrepant_measures: set[int] = set()
    discrepancy_details: list[dict[str, Any]] = []

    # Iterate over reference measures
    for r_m in ref_m_set:
        r_m_events = ref_graph.get_measure_events(r_m)
        h_m = measure_alignment.get(r_m)
        h_m_events = hyp_graph.get_measure_events(h_m) if h_m is not None else []

        matched_hyp_indices: set[int] = set()

        for r_evt in r_m_events:
            best_match_idx: int | None = None
            for h_idx, h_evt in enumerate(h_m_events):
                if h_idx in matched_hyp_indices:
                    continue
                if (
                    r_evt.onset_fraction == h_evt.onset_fraction
                    and r_evt.staff == h_evt.staff
                    and r_evt.voice == h_evt.voice
                ):
                    best_match_idx = h_idx
                    break

            if best_match_idx is not None:
                matched_hyp_indices.add(best_match_idx)
                h_match = h_m_events[best_match_idx]

                mismatch_reasons: list[str] = []
                if r_evt.pitch_step != h_match.pitch_step:
                    pitch_errors += 1
                    mismatch_reasons.append(f"pitch({r_evt.pitch_step}!={h_match.pitch_step})")
                if r_evt.alter != h_match.alter:
                    accidental_errors += 1
                    mismatch_reasons.append(f"alter({r_evt.alter}!={h_match.alter})")
                if r_evt.octave != h_match.octave:
                    octave_errors += 1
                    mismatch_reasons.append(f"octave({r_evt.octave}!={h_match.octave})")
                if r_evt.duration_fraction != h_match.duration_fraction:
                    duration_errors += 1
                    mismatch_reasons.append(f"duration({r_evt.duration_fraction}!={h_match.duration_fraction})")
                if r_evt.is_rest != h_match.is_rest:
                    rest_errors += 1
                    mismatch_reasons.append(f"rest({r_evt.is_rest}!={h_match.is_rest})")
                if r_evt.tie_start != h_match.tie_start or r_evt.tie_stop != h_match.tie_stop:
                    tie_errors += 1
                    mismatch_reasons.append("tie_mismatch")
                if r_evt.tuplet_ratio != h_match.tuplet_ratio:
                    tuplet_errors += 1
                    mismatch_reasons.append(f"tuplet_ratio({r_evt.tuplet_ratio}!={h_match.tuplet_ratio})")
                if r_evt.voice != h_match.voice or r_evt.staff != h_match.staff:
                    voice_staff_errors += 1
                    mismatch_reasons.append(f"voice_staff({r_evt.staff}.{r_evt.voice}!={h_match.staff}.{h_match.voice})")
                if r_evt.key_signature != h_match.key_signature:
                    key_errors += 1
                    mismatch_reasons.append("key_mismatch")
                if r_evt.time_signature != h_match.time_signature:
                    meter_errors += 1
                    mismatch_reasons.append("time_sig_mismatch")
                if r_evt.repeat != h_match.repeat or r_evt.ending != h_match.ending:
                    repeat_errors += 1
                    mismatch_reasons.append("repeat_or_ending_mismatch")

                if mismatch_reasons:
                    critical_mismatches += 1
                    discrepant_measures.add(r_m)
                    discrepancy_details.append({
                        "measure": r_m,
                        "ref_onset": r_evt.onset_fraction,
                        "reasons": mismatch_reasons,
                    })
                else:
                    matched_count += 1
            else:
                # Missing in hypothesis (deletion)
                critical_mismatches += 1
                discrepant_measures.add(r_m)
                pitch_errors += 1
                duration_errors += 1
                discrepancy_details.append({
                    "measure": r_m,
                    "ref_onset": r_evt.onset_fraction,
                    "reasons": ["event_missing_in_hypothesis"],
                })

        # Insertions in hypothesis measure
        unmatched_hyp_count = len(h_m_events) - len(matched_hyp_indices)
        if unmatched_hyp_count > 0:
            critical_mismatches += unmatched_hyp_count
            discrepant_measures.add(r_m)
            pitch_errors += unmatched_hyp_count
            duration_errors += unmatched_hyp_count
            discrepancy_details.append({
                "measure": r_m,
                "reasons": [f"{unmatched_hyp_count}_unmatched_extra_events_in_hypothesis"],
            })

    # Unaligned hypothesis measures (spurious measures)
    unaligned_hyp_measures = [m for m in hyp_m_set if m not in measure_alignment.values()]
    for uh_m in unaligned_hyp_measures:
        extra_evts = hyp_graph.get_measure_events(uh_m)
        critical_mismatches += len(extra_evts)
        discrepant_measures.add(uh_m)
        discrepancy_details.append({
            "measure": uh_m,
            "reasons": [f"{len(extra_evts)}_events_in_unaligned_hypothesis_measure"],
        })

    norm_base = max(total_ref, 1)
    event_recall = round(min(1.0, max(0.0, matched_count / norm_base)), 4)
    event_precision = round(min(1.0, max(0.0, matched_count / max(total_hyp, 1))), 4)

    # Per-dimension empirical reliability metrics
    dim_reliability = {
        "pitch": {"recall": round(max(0.0, 1.0 - (pitch_errors / norm_base)), 4), "error_rate": round(pitch_errors / norm_base, 4)},
        "accidental": {"recall": round(max(0.0, 1.0 - (accidental_errors / norm_base)), 4), "error_rate": round(accidental_errors / norm_base, 4)},
        "octave": {"recall": round(max(0.0, 1.0 - (octave_errors / norm_base)), 4), "error_rate": round(octave_errors / norm_base, 4)},
        "duration": {"recall": round(max(0.0, 1.0 - (duration_errors / norm_base)), 4), "error_rate": round(duration_errors / norm_base, 4)},
        "rest": {"recall": round(max(0.0, 1.0 - (rest_errors / norm_base)), 4), "error_rate": round(rest_errors / norm_base, 4)},
        "voice_staff": {"recall": round(max(0.0, 1.0 - (voice_staff_errors / norm_base)), 4), "error_rate": round(voice_staff_errors / norm_base, 4)},
        "time_signature": {"recall": round(max(0.0, 1.0 - (meter_errors / norm_base)), 4), "error_rate": round(meter_errors / norm_base, 4)},
        "key_signature": {"recall": round(max(0.0, 1.0 - (key_errors / norm_base)), 4), "error_rate": round(key_errors / norm_base, 4)},
    }

    return EventComparisonResult(
        overall_omr_ned=round(critical_mismatches / norm_base, 4),
        total_reference_events=total_ref,
        total_hypothesis_events=total_hyp,
        matched_events_count=matched_count,
        page_coverage=page_coverage,
        measure_coverage=measure_coverage,
        event_recall=event_recall,
        event_precision=event_precision,
        pitch_error_rate=round(pitch_errors / norm_base, 4),
        accidental_error_rate=round(accidental_errors / norm_base, 4),
        octave_error_rate=round(octave_errors / norm_base, 4),
        duration_error_rate=round(duration_errors / norm_base, 4),
        rest_error_rate=round(rest_errors / norm_base, 4),
        voice_staff_error_rate=round(voice_staff_errors / norm_base, 4),
        tie_error_rate=round(tie_errors / norm_base, 4),
        tuplet_error_rate=round(tuplet_errors / norm_base, 4),
        key_error_rate=round(key_errors / norm_base, 4),
        meter_error_rate=round(meter_errors / norm_base, 4),
        repeat_error_rate=round(repeat_errors / norm_base, 4),
        secondary_error_rate=round(secondary_errors / norm_base, 4),
        discrepant_measures=sorted(discrepant_measures),
        critical_mismatches_count=critical_mismatches,
        discrepancy_details=discrepancy_details,
        measure_alignment_map=measure_alignment,
        dimension_reliability=dim_reliability,
    )
