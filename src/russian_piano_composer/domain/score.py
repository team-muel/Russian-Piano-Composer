"""
Canonical symbolic score domain models for Russian Piano Composer.

Provides notation-preserving canonical score, measure, and event representations
supporting exact rational timing, spelled pitch preservation, and polyphonic staff/voice tracking.
"""

import hashlib
from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.theory.meter import TimeSignature
from russian_piano_composer.theory.pitch import SpelledPitch


class EventKind(StrEnum):
    """Classification of score events."""

    NOTE = "NOTE"
    REST = "REST"


class TieState(StrEnum):
    """Tie notation state for a score event."""

    NONE = "NONE"
    START = "START"
    CONTINUE = "CONTINUE"
    STOP = "STOP"


CANONICAL_SCORE_SCHEMA_VERSION: int = 1


@dataclass(frozen=True, slots=True)
class CanonicalScoreEvent:
    """
    Immutable representation of an individual musical notation event in a canonical score.
    """

    piece_id: str
    event_id: str
    event_index: int
    event_kind: EventKind
    measure_index: int
    source_measure_label: str
    staff: int
    voice: int
    global_onset: Fraction
    offset_in_measure: Fraction
    duration: Fraction
    pitch: SpelledPitch | None = None
    midi: int | None = None
    is_grace: bool = False
    tie_state: TieState = TieState.NONE
    source_relative_path: str = ""
    source_event_locator: str = ""

    def __post_init__(self) -> None:
        if self.event_index < 0:
            raise ValueError(f"event_index must be >= 0, got {self.event_index}")
        if self.measure_index < 0:
            raise ValueError(f"measure_index must be >= 0, got {self.measure_index}")
        if self.staff < 1:
            raise ValueError(f"staff must be >= 1, got {self.staff}")
        if self.voice < 1:
            raise ValueError(f"voice must be >= 1, got {self.voice}")
        if self.global_onset < 0:
            raise ValueError(f"global_onset must be >= 0, got {self.global_onset}")
        if self.offset_in_measure < 0:
            raise ValueError(f"offset_in_measure must be >= 0, got {self.offset_in_measure}")

        if self.is_grace:
            if self.duration < 0:
                raise ValueError(f"Grace event duration must be >= 0, got {self.duration}")
        else:
            if self.duration <= 0:
                raise ValueError(f"Non-grace event duration must be > 0, got {self.duration}")

        if self.event_kind == EventKind.NOTE:
            if self.pitch is None:
                raise ValueError("NOTE event must specify a pitch")
            if self.midi is None:
                raise ValueError("NOTE event must specify MIDI number")
            if not (0 <= self.midi <= 127):
                raise ValueError(f"MIDI out of range [0, 127]: {self.midi}")
            if self.midi != self.pitch.midi:
                raise ValueError(
                    f"MIDI number mismatch: provided {self.midi}, pitch.midi {self.pitch.midi}"
                )
        elif self.event_kind == EventKind.REST:
            if self.pitch is not None:
                raise ValueError("REST event must not specify pitch")
            if self.midi is not None:
                raise ValueError("REST event must not specify MIDI")


@dataclass(frozen=True, slots=True)
class CanonicalMeasure:
    """
    Immutable representation of a measure within a canonical score.
    """

    piece_id: str
    measure_index: int
    source_measure_label: str
    global_onset: Fraction
    actual_duration: Fraction
    time_signature: TimeSignature
    expected_duration: Fraction
    is_pickup: bool = False

    def __post_init__(self) -> None:
        if self.measure_index < 0:
            raise ValueError(f"measure_index must be >= 0, got {self.measure_index}")
        if self.global_onset < 0:
            raise ValueError(f"global_onset must be >= 0, got {self.global_onset}")
        if self.actual_duration <= 0:
            raise ValueError(f"actual_duration must be > 0, got {self.actual_duration}")
        if self.expected_duration <= 0:
            raise ValueError(f"expected_duration must be > 0, got {self.expected_duration}")


@dataclass(frozen=True, slots=True)
class CanonicalScore:
    """
    Complete canonical symbolic score for a single musical piece.
    """

    piece_id: str
    corpus_id: str
    corpus_role: CorpusRole
    score_entry_id: str
    composer: str
    title: str
    source_repository: str
    source_commit: str
    source_relative_path: str
    source_sha256: str
    manifest_hash: str
    parser_version: str
    measures: tuple[CanonicalMeasure, ...]
    events: tuple[CanonicalScoreEvent, ...]
    canonical_schema_version: int = CANONICAL_SCORE_SCHEMA_VERSION
    parser_name: str = "ms3"

    def __post_init__(self) -> None:
        expected_piece_id = f"{self.corpus_id}:{self.score_entry_id}"
        if self.piece_id != expected_piece_id:
            raise ValueError(
                f"piece_id must be '{expected_piece_id}', got '{self.piece_id}'"
            )

        # Validate measure contiguity
        for idx, m in enumerate(self.measures):
            if m.piece_id != self.piece_id:
                raise ValueError(
                    f"Measure piece_id '{m.piece_id}' does not match score piece_id '{self.piece_id}'"
                )
            if m.measure_index != idx:
                raise ValueError(
                    f"Measures must have contiguous zero-based indices: expected {idx}, got {m.measure_index}"
                )

        # Validate events
        prev_key = None
        for evt in self.events:
            if evt.piece_id != self.piece_id:
                raise ValueError(
                    f"Event piece_id '{evt.piece_id}' does not match score piece_id '{self.piece_id}'"
                )
            # Deterministic sorting check
            current_key = (
                evt.global_onset,
                evt.measure_index,
                evt.staff,
                evt.voice,
                evt.event_kind.value,
                evt.event_index,
            )
            if prev_key is not None and current_key < prev_key:
                raise ValueError(
                    f"Events are not deterministically sorted: {current_key} < {prev_key}"
                )
            prev_key = current_key

    def compute_piece_hash(self) -> str:
        """
        Compute a deterministic semantic SHA-256 hash of the canonical score.
        """
        hasher = hashlib.sha256()
        # Header info
        hasher.update(
            f"{self.piece_id}|{self.corpus_id}|{self.corpus_role.value}|{self.manifest_hash}\n".encode()
        )

        # Measures
        for m in self.measures:
            hasher.update(
                f"M|{m.measure_index}|{m.source_measure_label}|{m.global_onset.numerator}/{m.global_onset.denominator}|"
                f"{m.actual_duration.numerator}/{m.actual_duration.denominator}|"
                f"{m.time_signature.numerator}/{m.time_signature.denominator}|{m.is_pickup}\n".encode()
            )

        # Events
        for e in self.events:
            pitch_str = str(e.pitch) if e.pitch is not None else "NONE"
            hasher.update(
                f"E|{e.event_index}|{e.event_kind.value}|{e.measure_index}|{e.staff}|{e.voice}|"
                f"{e.global_onset.numerator}/{e.global_onset.denominator}|"
                f"{e.offset_in_measure.numerator}/{e.offset_in_measure.denominator}|"
                f"{e.duration.numerator}/{e.duration.denominator}|"
                f"{pitch_str}|{e.midi}|{e.is_grace}|{e.tie_state.value}\n".encode()
            )

        return hasher.hexdigest()
