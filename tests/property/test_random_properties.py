from hypothesis import given
from hypothesis import strategies as st

from russian_piano_composer.runtime import (
    RNG_DERIVATION_VERSION,
    RandomContext,
)

root_seeds = st.integers(min_value=0, max_value=2**63 - 1)
str_components = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=1, max_size=20)
int_components = st.integers(min_value=0, max_value=1000)
path_components = st.one_of(str_components, int_components)
paths = st.tuples(path_components, path_components)


@given(seed=root_seeds)
def test_random_context_deterministic_equality_property(seed: int) -> None:
    ctx1 = RandomContext(seed)
    ctx2 = RandomContext(seed)
    assert ctx1.derived_seed == ctx2.derived_seed
    assert ctx1.python_rng().random() == ctx2.python_rng().random()


@given(seed=root_seeds, comp1=str_components, comp2=str_components)
def test_random_context_immutability_property(seed: int, comp1: str, comp2: str) -> None:
    parent = RandomContext(seed, (comp1,))
    initial_parent_path = parent.path
    child = parent.child(comp2)

    assert parent.path == initial_parent_path
    assert child.path == (comp1, comp2)
    assert child.root_seed == seed


@given(seed=root_seeds, comp1=str_components, comp2=str_components)
def test_random_context_distinct_child_streams_property(seed: int, comp1: str, comp2: str) -> None:
    if comp1 == comp2:
        return
    ctx = RandomContext(seed)
    child1 = ctx.child(comp1)
    child2 = ctx.child(comp2)

    assert child1.derived_seed != child2.derived_seed


@given(seed=root_seeds, comp=path_components)
def test_random_context_metadata_property(seed: int, comp: str | int) -> None:
    ctx = RandomContext(seed).child(comp)
    meta = ctx.metadata()

    assert meta["root_seed"] == seed
    assert meta["path"] == [comp]
    assert meta["derived_seed"] == ctx.derived_seed
    assert meta["derivation_version"] == RNG_DERIVATION_VERSION
    assert meta["numpy_bit_generator"] == "PCG64"
