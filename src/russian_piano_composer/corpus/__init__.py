"""Corpus ingestion and provenance management.
"""
from russian_piano_composer.corpus.hashing import sha256_file
from russian_piano_composer.corpus.manifest import (
    MANIFEST_SCHEMA_VERSION,
    CorpusManifest,
    load_manifest,
)

__all__ = [
    "MANIFEST_SCHEMA_VERSION",
    "CorpusManifest",
    "load_manifest",
    "sha256_file",
]
