from hypothesis import given
from hypothesis import strategies as st

from russian_piano_composer.corpus.manifest import (
    MANIFEST_SCHEMA_VERSION,
    CorpusManifest,
)
from russian_piano_composer.domain.corpus import (
    CorpusRole,
    CorpusSource,
)

roles_strategy = st.sampled_from(list(CorpusRole))
valid_ids = st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789_", min_size=3, max_size=10)


@st.composite
def corpus_source_strategy(draw, c_id: str | None = None) -> CorpusSource:
    cid = c_id if c_id is not None else draw(valid_ids)
    role = draw(roles_strategy)
    return CorpusSource(
        corpus_id=cid,
        title=f"Title {cid}",
        role=role,
        composer="Composer Name",
        source_provider="Provider",
        source_repository="https://example.com/repo",
        source_version="1.0",
        repertoire_scope="Scope",
        license="CC-BY-4.0",
        verified_at="2026-09-13",
    )


@given(
    st.lists(valid_ids, min_size=1, max_size=5, unique=True).flatmap(
        lambda ids: st.tuples(*[corpus_source_strategy(c_id=cid) for cid in ids])
    )
)
def test_manifest_role_filtering_properties(sources_tuple: tuple[CorpusSource, ...]) -> None:
    manifest = CorpusManifest(
        manifest_version=MANIFEST_SCHEMA_VERSION,
        sources=sources_tuple,
    )

    gen_sources = manifest.generative_sources()
    ctrl_sources = manifest.control_sources()

    for s in gen_sources:
        assert s.role == CorpusRole.GENERATIVE_RUSSIAN

    for s in ctrl_sources:
        assert s.role == CorpusRole.CONTROL_NON_RUSSIAN

    gen_ids = {s.corpus_id for s in gen_sources}
    ctrl_ids = {s.corpus_id for s in ctrl_sources}
    assert gen_ids.isdisjoint(ctrl_ids)


@given(
    st.lists(valid_ids, min_size=1, max_size=4, unique=True).flatmap(
        lambda ids: st.tuples(*[corpus_source_strategy(c_id=cid) for cid in ids])
    )
)
def test_manifest_hash_order_invariance_property(sources_tuple: tuple[CorpusSource, ...]) -> None:
    manifest1 = CorpusManifest(
        manifest_version=MANIFEST_SCHEMA_VERSION,
        sources=sources_tuple,
    )
    # Reverse sources list
    manifest2 = CorpusManifest(
        manifest_version=MANIFEST_SCHEMA_VERSION,
        sources=tuple(reversed(sources_tuple)),
    )

    assert manifest1.compute_manifest_hash() == manifest2.compute_manifest_hash()
