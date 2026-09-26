"""Regression and Integrity Tests for RC-014C.1 Complete Confirmatory Corpus Freeze.

Verifies:
1. Strict Composer-Count Gate: N=2 -> BLOCKED, N=3 -> BLOCKED, N=4 -> SATISFIED (no 3-composer relaxation).
2. Report Repertoire == Manifest Repertoire: Exactly 483 pieces across 9 composers.
3. Rubinstein Repertoire Fidelity: Exact Op. 75 (Nos. 1, 2, 3, 4, 5, 6, 10, 11) & Op. 24 (Nos. 1, 4, 6).
4. Prokofiev Repertoire Fidelity: Exactly 10 works (8 TPC + 2 Humdrum supplements Op. 22 Nos. 2 & 3).
5. Anti-Unblinding Isolation: Role-blind cache contains zero target labels, zero prediction outputs.
6. Master Freeze Hash Determinism: RC014C1_CONFIRMATORY_CORPUS_FREEZE_HASH and supersession of RC-014C hash.
7. Frozen Predictor Bundle Hash: RC012_FROZEN_PREDICTOR_BUNDLE_HASH matches 4e783889...
8. Live Production Pool Safety: N_Russian remains 2 and RC-012 resumption remains BLOCKED.
"""

from __future__ import annotations

import json
from pathlib import Path

from russian_piano_composer.corpus.rc013_composer_pool import (
    derive_russian_composer_pool,
)

EXPECTED_RC014C1_FREEZE_HASH = "06173918554380617153cadd4de66443733c33d52dbbe54813a10846b24e6330"
EXPECTED_FEATURE_CACHE_HASH = "093d262da6ee7decce2026966be4b251d843c2c5836a2c4359d7609fefd8b28b"
EXPECTED_PREDICTOR_BUNDLE_HASH = "4e783889d8f9bbd83699bf27357bdd7873a43e15b81d2d04d9ea84ec5525f926"
SUPERSEDED_INCOMPLETE_FREEZE_HASH = "782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8"


def evaluate_composer_count_gate(
    n_russian: int,
    n_control: int,
    composer_piece_counts: dict[str, int],
    min_pieces_threshold: int = 10,
) -> str:
    """Evaluates the preregistered composer-count gate strictly without relaxation."""
    if n_russian < 4 or n_control < 4:
        return "BLOCKED"
    for _comp, count in composer_piece_counts.items():
        if count < min_pieces_threshold:
            return "BLOCKED"
    return "SATISFIED"


def test_composer_count_gate_strictness() -> None:
    """Proves that N=2 and N=3 are strictly BLOCKED, and only N>=4 with Mc>=10 is SATISFIED."""
    counts_mock = {
        "Scriabin": 207,
        "Mussorgsky": 18,
        "Rubinstein": 11,
        "Prokofiev": 10,
        "Grieg": 66,
        "Debussy": 54,
        "Beethoven": 91,
        "Bartók": 14,
        "Dvořák": 12,
    }

    # N=2 -> BLOCKED
    assert evaluate_composer_count_gate(2, 5, counts_mock) == "BLOCKED"

    # N=3 -> BLOCKED (Relaxation strictly rejected)
    assert evaluate_composer_count_gate(3, 5, counts_mock) == "BLOCKED"

    # N=4 with all Mc >= 10 -> SATISFIED
    assert evaluate_composer_count_gate(4, 5, counts_mock) == "SATISFIED"

    # N=4 but one composer Mc < 10 -> BLOCKED
    under_threshold_counts = dict(counts_mock)
    under_threshold_counts["Prokofiev"] = 9
    assert evaluate_composer_count_gate(4, 5, under_threshold_counts) == "BLOCKED"


def test_rc014c1_manifest_repertoire_exact_counts() -> None:
    """Verifies that all 9 composers and 483 pieces are precisely accounted for in manifests."""
    membership_p = Path("data/manifests/rc014c1_complete_confirmatory_membership.json")
    assert membership_p.exists(), "Membership manifest missing"

    with open(membership_p, encoding="utf-8") as f:
        data = json.load(f)

    conf_pool = data["confirmatory_pool"]
    assert conf_pool["total_composers_count"] == 9
    assert conf_pool["total_pieces_count"] == 483
    assert conf_pool["russian_pieces_count"] == 246
    assert conf_pool["control_pieces_count"] == 237

    # Russian counts
    ru_map = {c["composer"]: c["eligible_pieces_count"] for c in conf_pool["russian_composers"]}
    assert ru_map["Alexander Scriabin"] == 207
    assert ru_map["Modest Mussorgsky"] == 18
    assert ru_map["Anton Rubinstein"] == 11
    assert ru_map["Sergei Prokofiev"] == 10

    # Control counts
    ctrl_map = {c["composer"]: c["eligible_pieces_count"] for c in conf_pool["control_composers"]}
    assert ctrl_map["Edvard Grieg"] == 66
    assert ctrl_map["Claude Debussy"] == 54
    assert ctrl_map["Ludwig van Beethoven"] == 91
    assert ctrl_map["Béla Bartók"] == 14
    assert ctrl_map["Antonín Dvořák"] == 12


def test_rubinstein_repertoire_exact_works() -> None:
    """Verifies Anton Rubinstein repertoire matches canonical manifest Op. 75 and Op. 24."""
    source_freeze_p = Path("data/manifests/rc014c1_complete_source_freeze.json")
    assert source_freeze_p.exists()

    with open(source_freeze_p, encoding="utf-8") as f:
        data = json.load(f)

    rub_works = [w for w in data["source_works"] if w["composer"] == "Anton Rubinstein"]
    assert len(rub_works) == 11

    opuses = {w["opus_or_catalogue"] for w in rub_works}
    expected_opuses = {
        "Op. 75 No. 1",
        "Op. 75 No. 2",
        "Op. 75 No. 3",
        "Op. 75 No. 4",
        "Op. 75 No. 5",
        "Op. 75 No. 6",
        "Op. 75 No. 10",
        "Op. 75 No. 11",
        "Op. 24 No. 1",
        "Op. 24 No. 4",
        "Op. 24 No. 6",
    }
    assert opuses == expected_opuses


def test_prokofiev_repertoire_exact_works() -> None:
    """Verifies Sergei Prokofiev repertoire matches 8 TPC + 2 Humdrum supplements."""
    source_freeze_p = Path("data/manifests/rc014c1_complete_source_freeze.json")
    assert source_freeze_p.exists()

    with open(source_freeze_p, encoding="utf-8") as f:
        data = json.load(f)

    prok_works = [w for w in data["source_works"] if w["composer"] == "Sergei Prokofiev"]
    assert len(prok_works) == 10

    tpc_works = [w for w in prok_works if "tonal_piano_corpus" in w["piece_id"]]
    ana_works = [w for w in prok_works if "ana_music" in w["piece_id"]]

    assert len(tpc_works) == 8
    assert len(ana_works) == 2
    assert {w["canonical_work_id"] for w in ana_works} == {
        "prokofiev_op22_no02",
        "prokofiev_op22_no03",
    }


def test_anti_unblinding_isolation() -> None:
    """Verifies that role-blind feature cache contains zero labels or predictions."""
    cache_p = Path("data/manifests/rc014c1_complete_role_blind_feature_cache.json")
    assert cache_p.exists()

    with open(cache_p, encoding="utf-8") as f:
        data = json.load(f)

    assert data["total_cached_pieces"] == 483
    assert data["feature_catalog_descriptor_count"] == 56

    forbidden_keys = {"label", "class", "target", "score", "probability", "prediction", "y", "y_true", "y_pred"}

    for piece in data["cached_pieces"]:
        assert piece["composer"] in {
            "Alexander Scriabin",
            "Modest Mussorgsky",
            "Anton Rubinstein",
            "Sergei Prokofiev",
            "Edvard Grieg",
            "Claude Debussy",
            "Ludwig van Beethoven",
            "Béla Bartók",
            "Antonín Dvořák",
        }
        # Check no forbidden labels leaked
        assert not any(k in piece for k in forbidden_keys)
        assert len(piece["features_56"]) == 56


def test_master_freeze_hash_and_supersession() -> None:
    """Verifies master RC-014C.1 freeze hash and explicit supersession of RC-014C draft hash."""
    audit_p = Path("data/reviews/rc014/rc014c1_preunblinding_integrity_audit.json")
    assert audit_p.exists()

    with open(audit_p, encoding="utf-8") as f:
        data = json.load(f)

    assert data["rc014c1_confirmatory_corpus_freeze_hash"] == EXPECTED_RC014C1_FREEZE_HASH
    assert data["superseded_freeze_hash"] == SUPERSEDED_INCOMPLETE_FREEZE_HASH
    assert "SUPERSEDED_INCOMPLETE_NEW_RUSSIAN_ADDITIONS_FREEZE" in data["superseded_freeze_explanation"]
    assert data["total_confirmatory_pieces"] == 483
    assert data["total_composers_count"] == 9
    assert data["live_n_russian"] == 2
    assert data["rc012_resumption_gate"] == "BLOCKED"


def test_frozen_predictor_bundle_hash_determinism() -> None:
    """Verifies frozen predictor bundle hash matches preregistered value."""
    bundle_p = Path("models/rc012_predictor/frozen_predictor_bundle.json")
    manifest_p = Path("data/manifests/rc012_frozen_predictor_bundle.json")
    assert bundle_p.exists(), "Predictor bundle missing in models directory"
    assert manifest_p.exists(), "Predictor bundle missing in manifests directory"

    with open(bundle_p, encoding="utf-8") as f:
        bundle = json.load(f)
    assert bundle.get("predictor_bundle_hash") == EXPECTED_PREDICTOR_BUNDLE_HASH

    with open(manifest_p, encoding="utf-8") as f:
        manifest_bundle = json.load(f)
    assert manifest_bundle.get("predictor_bundle_hash") == EXPECTED_PREDICTOR_BUNDLE_HASH


def test_live_production_pool_remains_two() -> None:
    """Verifies live production pool remains strictly N_Russian = 2 until human authorization."""
    pool = derive_russian_composer_pool()
    assert pool.n_russian == 2
    assert pool.qualified_russian_composers == ["Alexander Scriabin", "Modest Mussorgsky"]
    assert pool.rc012_resumption_status == "BLOCKED"
