"""RC-013 Score Notation Validator and Quality Control Audit Engine.

Enforces strict notation-level syntax, metric bar integrity, pitch spelling,
rest completeness, staff distribution, and polyphonic voice consistency
for digitized Russian piano works, with anti-synthetic guard rails.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import music21 as m21


@dataclass
class NotationValidationError:
    code: str
    measure: int
    staff: int | None
    voice: int | None
    message: str
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "measure": self.measure,
            "staff": self.staff,
            "voice": self.voice,
            "message": self.message,
            "context": self.context,
        }


@dataclass
class ValidationReport:
    file_path: str
    valid: bool
    num_measures: int
    num_notes: int
    num_rests: int
    num_parts_or_staves: int
    time_signatures: list[str]
    key_signatures: list[str]
    errors: list[NotationValidationError] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "valid": self.valid,
            "num_measures": self.num_measures,
            "num_notes": self.num_notes,
            "num_rests": self.num_rests,
            "num_parts_or_staves": self.num_parts_or_staves,
            "time_signatures": self.time_signatures,
            "key_signatures": self.key_signatures,
            "error_count": len(self.errors),
            "errors": [e.to_dict() for e in self.errors],
        }


class RC013ScoreValidator:
    """Validates MusicXML scores against RC-013 notation preservation criteria."""

    def __init__(self, tolerance_quarter: float = 0.001) -> None:
        self.tolerance = tolerance_quarter

    def validate_file(self, file_path: str, enforce_anti_synthetic: bool = True) -> ValidationReport:
        if not os.path.exists(file_path):
            return ValidationReport(
                file_path=file_path,
                valid=False,
                num_measures=0,
                num_notes=0,
                num_rests=0,
                num_parts_or_staves=0,
                time_signatures=[],
                key_signatures=[],
                errors=[
                    NotationValidationError(
                        code="FILE_NOT_FOUND",
                        measure=0,
                        staff=None,
                        voice=None,
                        message=f"File not found: {file_path}",
                    )
                ],
            )

        try:
            score = m21.converter.parse(file_path)
        except Exception as e:
            return ValidationReport(
                file_path=file_path,
                valid=False,
                num_measures=0,
                num_notes=0,
                num_rests=0,
                num_parts_or_staves=0,
                time_signatures=[],
                key_signatures=[],
                errors=[
                    NotationValidationError(
                        code="PARSING_SYNTAX_ERROR",
                        measure=0,
                        staff=None,
                        voice=None,
                        message=f"XML/music21 parsing failure: {e!s}",
                    )
                ],
            )

        errors: list[NotationValidationError] = []

        # 1. Structural parts / staves check
        if isinstance(score, m21.stream.Score):
            parts = list(score.parts)
        else:
            parts = list(score.getElementsByClass(m21.stream.Part))

        num_parts = len(parts)
        if num_parts == 0:
            errors.append(
                NotationValidationError(
                    code="STRUCTURAL_NO_PARTS",
                    measure=0,
                    staff=0,
                    voice=0,
                    message="Score contains no parts or staves.",
                )
            )

        # 2. Extract global metadata and signatures
        time_sigs = [ts.ratioString for ts in score.recurse().getElementsByClass(m21.meter.TimeSignature)]
        key_sigs = [str(ks) for ks in score.recurse().getElementsByClass(m21.key.KeySignature)]

        # 3. Measures count & iteration
        measures = list(parts[0].getElementsByClass(m21.stream.Measure)) if num_parts > 0 else []
        num_measures = len(measures)
        if num_measures < 4:
            errors.append(
                NotationValidationError(
                    code="MEASURE_COUNT_DEFICIENT",
                    measure=num_measures,
                    staff=1,
                    voice=1,
                    message=f"Score has fewer than 4 measures ({num_measures}).",
                )
            )

        # Check part measure-count alignment
        if num_parts > 1:
            for p_idx, part in enumerate(parts[1:], start=2):
                p_m_count = len(list(part.getElementsByClass(m21.stream.Measure)))
                if p_m_count != num_measures:
                    errors.append(
                        NotationValidationError(
                            code="STAFF_MEASURE_COUNT_MISMATCH",
                            measure=0,
                            staff=p_idx,
                            voice=1,
                            message=f"Staff {p_idx} measure count ({p_m_count}) differs from Staff 1 ({num_measures}).",
                        )
                    )

        # 4. Detailed Measure-level duration, voice, underflow/overflow checks
        current_ts = m21.meter.TimeSignature("4/4")
        measure_patterns: list[tuple[str, ...]] = []

        for p_idx, part in enumerate(parts):
            staff_num = p_idx + 1
            part_measures = list(part.getElementsByClass(m21.stream.Measure))
            for m in part_measures:
                m_num = m.number
                if m.timeSignature is not None:
                    current_ts = m.timeSignature

                expected_bar_length = current_ts.barDuration.quarterLength
                is_pickup = (m_num == 0)

                # Collect measure note pattern for staff 1 to test anti-synthetic repetition
                if staff_num == 1:
                    m_notes = tuple(n.nameWithOctave for n in m.notes)
                    measure_patterns.append(m_notes)

                # Check voices in measure
                voices = list(m.voices)
                if not voices:
                    total_dur = float(m.duration.quarterLength)
                    # Check overflow
                    if not is_pickup and total_dur > expected_bar_length + self.tolerance:
                        errors.append(
                            NotationValidationError(
                                code="NOTE_DURATION_OVERFLOW",
                                measure=m_num,
                                staff=staff_num,
                                voice=1,
                                message=(
                                    f"Measure duration {total_dur} exceeds "
                                    f"time signature {current_ts.ratioString} ({expected_bar_length})"
                                ),
                            )
                        )
                    # Check underflow (except for pickup or final measure)
                    elif not is_pickup and m_num < num_measures and total_dur < expected_bar_length - self.tolerance and total_dur > 0:
                        errors.append(
                            NotationValidationError(
                                code="NOTE_DURATION_UNDERFLOW",
                                measure=m_num,
                                staff=staff_num,
                                voice=1,
                                message=(
                                    f"Measure duration {total_dur} is less than "
                                    f"time signature {current_ts.ratioString} ({expected_bar_length})"
                                ),
                            )
                        )
                else:
                    for v_idx, voice in enumerate(voices):
                        v_dur = float(voice.duration.quarterLength)
                        if not is_pickup and v_dur > expected_bar_length + self.tolerance:
                            errors.append(
                                NotationValidationError(
                                    code="VOICE_DURATION_OVERFLOW",
                                    measure=m_num,
                                    staff=staff_num,
                                    voice=v_idx + 1,
                                    message=(
                                        f"Voice {v_idx+1} duration {v_dur} exceeds "
                                        f"bar duration {expected_bar_length}"
                                    ),
                                )
                            )

        # 5. Anti-Synthetic Pattern Guard: reject scores where identical patterns repeat uniformly
        if enforce_anti_synthetic and num_measures >= 10:
            unique_patterns = len(set(measure_patterns))
            if unique_patterns <= 1:
                errors.append(
                    NotationValidationError(
                        code="SYNTHETIC_REPETITIVE_PATTERN_DETECTED",
                        measure=0,
                        staff=1,
                        voice=1,
                        message=(
                            f"Suspicious synthetic pattern: entire score of {num_measures} measures "
                            f"contains only {unique_patterns} unique measure pattern(s)."
                        ),
                    )
                )

        # 6. Note, Rest, and Pitch Integrity
        notes = list(score.recurse().notes)
        rests = list(score.recurse().getElementsByClass(m21.note.Rest))
        num_notes = len(notes)
        num_rests = len(rests)

        if num_notes == 0:
            errors.append(
                NotationValidationError(
                    code="NOTE_EMPTY_SCORE",
                    measure=0,
                    staff=1,
                    voice=1,
                    message="Score has zero notes.",
                )
            )

        # Check pitch spelling validity
        for n in notes:
            if n.isChord:
                for p in n.pitches:
                    if p.name == "" or p.octave is None:
                        errors.append(
                            NotationValidationError(
                                code="NOTE_PITCH_MALFORMED",
                                measure=n.measureNumber or 0,
                                staff=None,
                                voice=None,
                                message=f"Chord pitch lacks name or octave: {p}",
                            )
                        )
            elif n.isNote and (n.pitch.name == "" or n.pitch.octave is None):
                errors.append(
                    NotationValidationError(
                        code="NOTE_PITCH_MALFORMED",
                        measure=n.measureNumber or 0,
                        staff=None,
                        voice=None,
                        message=f"Note pitch lacks name or octave: {n.pitch}",
                    )
                )

        valid = (len(errors) == 0)
        return ValidationReport(
            file_path=file_path,
            valid=valid,
            num_measures=num_measures,
            num_notes=num_notes,
            num_rests=num_rests,
            num_parts_or_staves=num_parts,
            time_signatures=time_sigs,
            key_signatures=key_sigs,
            errors=errors,
        )
