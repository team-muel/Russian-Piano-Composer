"""
Domain models and value objects for corpus provenance and rights management.
"""
import re
from dataclasses import dataclass, field
from enum import StrEnum


class CorpusRole(StrEnum):
    """
    Explicit project role assigned to a corpus source.
    """
    GENERATIVE_RUSSIAN = "GENERATIVE_RUSSIAN"
    CONTROL_NON_RUSSIAN = "CONTROL_NON_RUSSIAN"
    PROVISIONAL = "PROVISIONAL"
    EXCLUDED = "EXCLUDED"


class CorpusFormat(StrEnum):
    """
    Structured formats available for a corpus source.
    """
    MUSESCORE_MSCX = "MUSESCORE_MSCX"
    MUSICXML = "MUSICXML"
    MXL = "MXL"
    MIDI = "MIDI"
    TSV_NOTES = "TSV_NOTES"
    TSV_MEASURES = "TSV_MEASURES"
    TSV_CHORDS = "TSV_CHORDS"
    TSV_HARMONIES = "TSV_HARMONIES"
    PDF = "PDF"
    OTHER = "OTHER"


class RightsStatus(StrEnum):
    """
    Verification status of upstream rights and licensing facts.
    """
    VERIFIED = "VERIFIED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"
    INCOMPATIBLE = "INCOMPATIBLE"


class ProvenanceStatus(StrEnum):
    """
    Confidence status of source provenance documentation.
    """
    VERIFIED_SOURCE = "VERIFIED_SOURCE"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class PianoMedium(StrEnum):
    """
    Instrumental scoring classification for playability and texture filtering.
    """
    SOLO_PIANO = "SOLO_PIANO"
    PIANO_FOUR_HANDS = "PIANO_FOUR_HANDS"
    TWO_PIANOS = "TWO_PIANOS"
    CONCERTO_ORCHESTRA = "CONCERTO_ORCHESTRA"
    CHAMBER_WITH_PIANO = "CHAMBER_WITH_PIANO"
    SONG_WITH_PIANO = "SONG_WITH_PIANO"
    ARRANGEMENT = "ARRANGEMENT"
    TRANSCRIPTION = "TRANSCRIPTION"
    REDUCTION = "REDUCTION"
    UNKNOWN = "UNKNOWN"


class ReadinessStatus(StrEnum):
    """
    Acquisition/provenance readiness status of a corpus source.
    Separate from scientific role.
    """
    PROVENANCE_READY = "PROVENANCE_READY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNVERIFIED = "UNVERIFIED"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class LicenseClaim:
    """
    Evidence record of an observed upstream license claim.
    """
    source_type: str
    value: str
    source_url: str | None = None

    def __post_init__(self) -> None:
        if not self.source_type:
            raise ValueError("LicenseClaim source_type cannot be empty.")
        if not self.value:
            raise ValueError("LicenseClaim value cannot be empty.")


HEX_COMMIT_REGEX = re.compile(r"^[0-9a-f]{40}$")
DISALLOWED_COMMIT_PATTERNS = re.compile(r"(a1b2c3d4|c1c2c3c4|l1l2l3l4|s1s2s3s4|00000000000000000000|\.\.\.)")


@dataclass(frozen=True, slots=True)
class CorpusSource:
    """
    Metadata representation of a candidate score corpus source.
    Must be fully specified before any score acquisition occurs.
    """
    corpus_id: str
    title: str
    composer: str
    role: CorpusRole
    repertoire_scope: str
    license: str
    verified_at: str
    source_provider: str = ""
    source_repository: str = ""
    source_version: str = ""
    license_claims: tuple[LicenseClaim, ...] = ()
    is_non_commercial: bool = True
    readiness_status: ReadinessStatus = ReadinessStatus.REVIEW_REQUIRED
    composer_authority_ids: dict[str, str] = field(default_factory=dict)
    piano_medium: PianoMedium = PianoMedium.SOLO_PIANO
    coverage_notes: str | None = None
    is_complete_for_claimed_scope: bool = False
    representative_of_full_composer_output: bool = False
    work_count: int | None = None
    piece_count: int | None = None
    score_entry_count: int | None = None
    musical_piece_count: int | None = None
    work_cycle_count: int | None = None
    source_file_count: int | None = None
    source_commit: str | None = None
    meta_repository_commit: str | None = None
    source_documentation: str | None = None
    doi: str | None = None
    citation: str | None = None
    license_url: str | None = None
    rights_notes: str | None = None
    rights_status: RightsStatus = RightsStatus.VERIFIED
    rights_review_required: bool = False
    provenance_status: ProvenanceStatus = ProvenanceStatus.VERIFIED_SOURCE
    formats_available: tuple[CorpusFormat, ...] = ()
    retrieval_method: str = "git_clone"
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.corpus_id or not self.corpus_id.isascii() or self.corpus_id != self.corpus_id.lower():
            raise ValueError(f"corpus_id must be non-empty lowercase ASCII, got {self.corpus_id!r}.")
        if not isinstance(self.role, CorpusRole):
            raise TypeError(f"role must be a CorpusRole enum instance, got {type(self.role).__name__}.")
        if not isinstance(self.rights_status, RightsStatus):
            raise TypeError(f"rights_status must be a RightsStatus enum instance, got {type(self.rights_status).__name__}.")
        if not isinstance(self.provenance_status, ProvenanceStatus):
            raise TypeError(f"provenance_status must be a ProvenanceStatus enum instance, got {type(self.provenance_status).__name__}.")
        if not isinstance(self.piano_medium, PianoMedium):
            raise TypeError(f"piano_medium must be a PianoMedium enum instance, got {type(self.piano_medium).__name__}.")
        if not isinstance(self.readiness_status, ReadinessStatus):
            raise TypeError(f"readiness_status must be a ReadinessStatus enum instance, got {type(self.readiness_status).__name__}.")

        if self.source_commit is not None and (
            not HEX_COMMIT_REGEX.match(self.source_commit) or DISALLOWED_COMMIT_PATTERNS.search(self.source_commit)
        ):
            raise ValueError(
                f"source_commit for {self.corpus_id!r} must be a 40-character lowercase hex string without synthetic placeholder patterns, got {self.source_commit!r}"
            )
        if self.meta_repository_commit is not None and (
            not HEX_COMMIT_REGEX.match(self.meta_repository_commit) or DISALLOWED_COMMIT_PATTERNS.search(self.meta_repository_commit)
        ):
            raise ValueError(
                f"meta_repository_commit for {self.corpus_id!r} must be a 40-character lowercase hex string without synthetic placeholder patterns, got {self.meta_repository_commit!r}"
            )

    @property
    def generative_eligible(self) -> bool:
        """
        True iff source is GENERATIVE_RUSSIAN with VERIFIED rights and no pending review.
        """
        return (
            self.role == CorpusRole.GENERATIVE_RUSSIAN
            and self.rights_status == RightsStatus.VERIFIED
            and not self.rights_review_required
            and self.readiness_status == ReadinessStatus.PROVENANCE_READY
        )


@dataclass(frozen=True, slots=True)
class PieceProvenance:
    """
    Immutable metadata record for an individual piece within a corpus.
    """
    piece_id: str
    corpus_id: str
    upstream_id: str
    title: str
    composer: str
    role: CorpusRole
    piano_medium: PianoMedium
    opus: str | None = None
    movement: str | None = None
    year_or_period: str | None = None

    def __post_init__(self) -> None:
        if not self.piece_id:
            raise ValueError("piece_id cannot be empty.")
        if not self.corpus_id:
            raise ValueError("corpus_id cannot be empty.")
        if not isinstance(self.role, CorpusRole):
            raise TypeError(f"role must be a CorpusRole enum instance, got {type(self.role).__name__}.")
