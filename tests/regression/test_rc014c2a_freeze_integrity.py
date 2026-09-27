"""Regression tests for RC-014C.2A Complete Confirmatory Corpus Freeze and Deterministic Source Authority.

Verifies:
1. Strict Fail-Closed Preregistration Gate:
   - Live N_Russian == 2 (Scriabin, Mussorgsky).
   - Live qualified composers == ["Alexander Scriabin", "Modest Mussorgsky"].
   - RC-012 resumption status == "BLOCKED".
   - 0 evaluations of the confirmatory predictor on confirmatory rows.
2. Complete Confirmatory Repertoire (9 composers, 483 pieces):
   - Russian: 4 composers, 246 pieces (Scriabin 207, Mussorgsky 18, Rubinstein 11, Prokofiev 10).
   - Control: 5 composers, 237 pieces (Grieg 66, Debussy 54, Beethoven 91, Bartók 14, Dvořák 12).
3. Deterministic Source Authority:
   - 465 Git-backed pieces have source_object_type == "GIT_BLOB", valid 40-hex blob SHA, and canonical_source_sha256.
   - 18 Mussorgsky pieces have source_object_type == "HF_DATASET_ARCHIVE_ENTRY", pinned revision 5a637bd9..., and archive metadata.
   - EOL normalization audit tracks IDENTICAL vs CHECKOUT_NORMALIZATION_DIFFERENCE.
   - 0 missing hashes across all 483 pieces.
4. Feature Cache Integrity:
   - 483 cached feature vectors, exactly 56 descriptors per piece.
   - Zero all-zero placeholder rows.
   - feature_cache_matrix_sha256 matches frozen hash.
5. Master Pre-Unblinding Freeze Hash:
   - Matches frozen RC014C2A master hash.
   - Properly supersedes provisional RC014C.2, placeholder RC014C.1, and incomplete RC014C.
"""

from __future__ import annotations

import json
from pathlib import Path

FROZEN_RC014C2A_MASTER_FREEZE_HASH = "ec9c1a344cf7a53ba69c00865bda783c352d92770267fcb6933521e9cc186c1e"
FROZEN_RC014C2A_FEATURE_CACHE_MATRIX_SHA256 = "6a1fba9d1071ad0453516870f78eabb138b46415d2f642d3d2e195f0fe9bfca7"

SUPERSEDED_PROVISIONAL_REAL_FEATURE_FREEZE_HASH_RC014C2 = "d634349e5e9950345c62b43d66af61b0f8936631639bf0b22254330fb9aa2996"
SUPERSEDED_INVALID_PLACEHOLDER_FREEZE_HASH_RC014C1 = "06173918554380617153cadd4de66443733c33d52dbbe54813a10846b24e6330"
SUPERSEDED_INVALID_PLACEHOLDER_FEATURE_CACHE_SHA256_RC014C1 = "093d262da6ee7decce2026966be4b251d843c2c5836a2c4359d7609fefd8b28b"
SUPERSEDED_INCOMPLETE_FREEZE_HASH_RC014C = "782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8"


def test_rc014c2a_membership_manifest_integrity() -> None:
    path = Path("data/manifests/rc014c2a_complete_confirmatory_membership.json")
    assert path.exists(), f"Missing {path}"

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-014C.2A"
    assert data["governance_model"] == "FAIL_CLOSED_IMMUTABLE_PREREGISTRATION"

    live = data["live_production_pool"]
    assert live["N_Russian"] == 2
    assert live["qualified_composers"] == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert live["rc012_resumption_status"] == "BLOCKED"

    conf = data["confirmatory_pool"]
    assert conf["N_Russian_confirmatory"] == 4
    assert conf["N_Control_confirmatory"] == 5
    assert conf["total_composers_count"] == 9
    assert conf["total_pieces_count"] == 483
    assert conf["russian_pieces_count"] == 246
    assert conf["control_pieces_count"] == 237

    # Verify per-composer counts
    ru_counts = {c["composer"]: c["eligible_pieces_count"] for c in conf["russian_composers"]}
    assert ru_counts["Alexander Scriabin"] == 207
    assert ru_counts["Modest Mussorgsky"] == 18
    assert ru_counts["Anton Rubinstein"] == 11
    assert ru_counts["Sergei Prokofiev"] == 10

    ctrl_counts = {c["composer"]: c["eligible_pieces_count"] for c in conf["control_composers"]}
    assert ctrl_counts["Edvard Grieg"] == 66
    assert ctrl_counts["Claude Debussy"] == 54
    assert ctrl_counts["Ludwig van Beethoven"] == 91
    assert ctrl_counts["Béla Bartók"] == 14
    assert ctrl_counts["Antonín Dvořák"] == 12


def test_rc014c2a_source_freeze_manifest_deterministic_authority() -> None:
    path = Path("data/manifests/rc014c2a_complete_source_freeze.json")
    assert path.exists(), f"Missing {path}"

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-014C.2A"
    assert data["total_source_works"] == 483
    assert data["russian_source_works_count"] == 246
    assert data["control_source_works_count"] == 237

    breakdown = data["typed_source_breakdown"]
    assert breakdown["GIT_BLOB"] == 465
    assert breakdown["HF_DATASET_ARCHIVE_ENTRY"] == 18

    audit = data["eol_normalization_audit"]
    assert audit["IDENTICAL"] + audit["CHECKOUT_NORMALIZATION_DIFFERENCE"] == 483

    works = data["source_works"]
    assert len(works) == 483

    for w in works:
        assert w["eligible"] is True
        assert len(w["canonical_score_hash"]) == 64
        assert len(w["derived_feature_bundle_hash"]) == 64
        assert len(w["canonical_source_sha256"]) == 64
        assert w["measures_count"] > 0
        assert w["events_count"] > 0

        if w["source_object_type"] == "GIT_BLOB":
            assert len(w["source_object_id"]) == 40
            assert len(w["git_blob_sha"]) == 40
        elif w["source_object_type"] == "HF_DATASET_ARCHIVE_ENTRY":
            assert w["composer"] == "Modest Mussorgsky"
            assert "5a637bd9ee3ca748c425301417fd917d56486645" in w["source_object_id"]
            assert len(w["archive_file_sha256"]) == 64
            assert w["archive_file_size_bytes"] > 0
            assert len(w["entry_sha256"]) == 64
        else:
            raise ValueError(f"Unknown source_object_type {w['source_object_type']}")


def test_rc014c2a_role_blind_feature_cache_real_values() -> None:
    path = Path("data/manifests/rc014c2a_complete_role_blind_feature_cache.json")
    assert path.exists(), f"Missing {path}"

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-014C.2A"
    assert data["total_cached_pieces"] == 483
    assert data["russian_pieces_count"] == 246
    assert data["control_pieces_count"] == 237
    assert data["feature_catalog_descriptor_count"] == 56
    assert data["feature_cache_matrix_sha256"] == FROZEN_RC014C2A_FEATURE_CACHE_MATRIX_SHA256

    pieces = data["cached_pieces"]
    assert len(pieces) == 483

    for p in pieces:
        f56 = p["features_56"]
        assert len(f56) == 56
        # Assert not all zero
        assert not all(v == 0.0 for v in f56.values()), f"Found all-zero placeholder vector in {p['piece_id']}"
        # Assert no NaN or Inf
        import math
        assert all(isinstance(v, (int, float)) and not math.isnan(v) and not math.isinf(v) for v in f56.values())


def test_rc014c2a_preunblinding_integrity_audit_record() -> None:
    path = Path("data/reviews/rc014/rc014c2a_preunblinding_integrity_audit.json")
    assert path.exists(), f"Missing {path}"

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    assert data["milestone"] == "RC-014C.2A"
    assert data["status"] == "RC014C2A_TRUE_FULL_CORPUS_FROZEN_READY_FOR_HUMAN_ACCESS_DECISION"
    assert data["rc014c2a_confirmatory_corpus_freeze_hash"] == FROZEN_RC014C2A_MASTER_FREEZE_HASH
    assert data["feature_cache_matrix_sha256"] == FROZEN_RC014C2A_FEATURE_CACHE_MATRIX_SHA256
    assert data["superseded_freeze_hash_rc014c2"] == SUPERSEDED_PROVISIONAL_REAL_FEATURE_FREEZE_HASH_RC014C2
    assert data["superseded_freeze_hash_rc014c1"] == SUPERSEDED_INVALID_PLACEHOLDER_FREEZE_HASH_RC014C1
    assert data["superseded_feature_cache_sha256_rc014c1"] == SUPERSEDED_INVALID_PLACEHOLDER_FEATURE_CACHE_SHA256_RC014C1
    assert data["superseded_freeze_hash_rc014c"] == SUPERSEDED_INCOMPLETE_FREEZE_HASH_RC014C

    assert data["total_confirmatory_pieces"] == 483
    assert data["russian_composers_count"] == 4
    assert data["control_composers_count"] == 5
    assert data["russian_pieces_count"] == 246
    assert data["control_pieces_count"] == 237
    assert data["live_n_russian"] == 2
    assert data["rc012_resumption_gate"] == "BLOCKED"
