import numpy as np
import pytest

from russian_piano_composer.runtime.random_context import (
    RNG_DERIVATION_VERSION,
    RandomContext,
)


def test_root_seed_validation():
    ctx = RandomContext(0)
    assert ctx.root_seed == 0

    ctx_42 = RandomContext(42)
    assert ctx_42.root_seed == 42

    with pytest.raises(ValueError, match="root_seed must be non-negative"):
        RandomContext(-1)

    with pytest.raises(TypeError, match="root_seed must be an integer"):
        RandomContext(42.0)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="root_seed must be an integer"):
        RandomContext(True)  # type: ignore[arg-type]


def test_path_validation():
    root = RandomContext(10)
    c1 = root.child("dna", 0)
    assert c1.path == ("dna", 0)

    with pytest.raises(ValueError, match="Child path string component cannot be empty"):
        root.child("")

    with pytest.raises(ValueError, match="Child path integer component must be non-negative"):
        root.child("candidate", -1)

    with pytest.raises(TypeError, match="Child path components must be str or int"):
        root.child(3.14)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Child path components must be str or int"):
        root.child(True)  # type: ignore[arg-type]


def test_child_order_independence():
    root = RandomContext(20260913)

    # Order 1: dna first, then rhythm
    dna1 = root.child("dna")
    rhythm1 = root.child("rhythm")

    # Order 2: rhythm first, then dna
    rhythm2 = root.child("rhythm")
    dna2 = root.child("dna")

    assert dna1 == dna2
    assert dna1.derived_seed == dna2.derived_seed
    assert rhythm1 == rhythm2
    assert rhythm1.derived_seed == rhythm2.derived_seed
    assert dna1.derived_seed != rhythm1.derived_seed


def test_collision_safe_encoding():
    root = RandomContext(42)

    # Collision test: ("ab", "c") vs ("a", "bc")
    c_ab_c = root.child("ab", "c")
    c_a_bc = root.child("a", "bc")
    assert c_ab_c.derived_seed != c_a_bc.derived_seed

    # Collision test: ("1",) vs (1,)
    c_str1 = root.child("1")
    c_int1 = root.child(1)
    assert c_str1.derived_seed != c_int1.derived_seed


def test_python_rng_reproducibility():
    ctx = RandomContext(100).child("rhythm")

    rng1 = ctx.python_rng()
    seq1 = [rng1.random() for _ in range(50)]

    rng2 = ctx.python_rng()
    seq2 = [rng2.random() for _ in range(50)]

    assert seq1 == seq2


def test_numpy_rng_reproducibility():
    ctx = RandomContext(100).child("pitch")

    rng1 = ctx.numpy_rng()
    arr1 = rng1.normal(size=50)

    rng2 = ctx.numpy_rng()
    arr2 = rng2.normal(size=50)

    assert np.array_equal(arr1, arr2)


def test_stream_isolation():
    root = RandomContext(777)

    # Rhythms generated directly
    rhythm_seq1 = [root.child("rhythm").python_rng().random() for _ in range(20)]

    # Interleave heavy consumption from hook stream
    hook_rng = root.child("hook").python_rng()
    for _ in range(10000):
        hook_rng.random()

    # Rhythms generated afterwards
    rhythm_seq2 = [root.child("rhythm").python_rng().random() for _ in range(20)]

    assert rhythm_seq1 == rhythm_seq2


def test_indexed_candidate_contexts():
    root = RandomContext(123)

    c0 = root.child("candidate", 0)
    c1 = root.child("candidate", 1)
    c100 = root.child("candidate", 100)

    assert len({c0.derived_seed, c1.derived_seed, c100.derived_seed}) == 3

    # Candidate 100 derived independently without evaluating 0..99
    c100_direct = RandomContext(123).child("candidate", 100)
    assert c100.derived_seed == c100_direct.derived_seed


def test_metadata_output():
    ctx = RandomContext(42).child("theme", 5)
    meta = ctx.metadata()

    assert meta["root_seed"] == 42
    assert meta["path"] == ["theme", 5]
    assert meta["derived_seed"] == ctx.derived_seed
    assert meta["derivation_version"] == RNG_DERIVATION_VERSION
    assert meta["numpy_bit_generator"] == "PCG64"
    assert isinstance(meta["python_adapter_seed"], int)
    assert isinstance(meta["numpy_adapter_seed"], int)


def test_golden_seed_vectors():
    """
    Golden seed vectors locking the derivation algorithm.
    If these fail, the RNG derivation implementation was changed.
    """
    ctx1 = RandomContext(0)
    assert ctx1.derived_seed == 151923723709505763851425407690297020074

    ctx2 = RandomContext(1).child("dna")
    assert ctx2.derived_seed == 260468588729295644858293100831619570112

    ctx3 = RandomContext(42).child("theme", "rhythm")
    assert ctx3.derived_seed == 31726086548442648357876062923779197587

    ctx4 = RandomContext(20260913).child("generation", "candidate", 17)
    assert ctx4.derived_seed == 91967140764262623101690783266205589971
