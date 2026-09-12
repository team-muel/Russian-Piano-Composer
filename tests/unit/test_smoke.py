"""Smoke tests for project bootstrap verification.

These tests verify that the package structure is intact
and all subpackages can be imported successfully.
"""

from __future__ import annotations


def test_package_imports() -> None:
    """Verify that the root package can be imported."""
    import russian_piano_composer

    assert russian_piano_composer is not None


def test_version_exists() -> None:
    """Verify that __version__ is set and non-empty."""
    from russian_piano_composer import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0
    assert __version__ == "0.1.0"


def test_version_format() -> None:
    """Verify that __version__ follows semantic versioning format."""
    from russian_piano_composer import __version__

    parts = __version__.split(".")
    assert len(parts) == 3, f"Expected 3 version parts, got {len(parts)}"
    for part in parts:
        assert part.isdigit(), f"Version part '{part}' is not numeric"


class TestSubpackageImports:
    """Verify all subpackages import without error."""

    def test_domain_imports(self) -> None:
        """Import domain subpackage."""
        import russian_piano_composer.domain

        assert russian_piano_composer.domain is not None

    def test_theory_imports(self) -> None:
        """Import theory subpackage."""
        import russian_piano_composer.theory

        assert russian_piano_composer.theory is not None

    def test_corpus_imports(self) -> None:
        """Import corpus subpackage."""
        import russian_piano_composer.corpus

        assert russian_piano_composer.corpus is not None

    def test_models_imports(self) -> None:
        """Import models subpackage."""
        import russian_piano_composer.models

        assert russian_piano_composer.models is not None

    def test_generation_imports(self) -> None:
        """Import generation subpackage."""
        import russian_piano_composer.generation

        assert russian_piano_composer.generation is not None

    def test_critics_imports(self) -> None:
        """Import critics subpackage."""
        import russian_piano_composer.critics

        assert russian_piano_composer.critics is not None

    def test_search_imports(self) -> None:
        """Import search subpackage."""
        import russian_piano_composer.search

        assert russian_piano_composer.search is not None

    def test_piano_imports(self) -> None:
        """Import piano subpackage."""
        import russian_piano_composer.piano

        assert russian_piano_composer.piano is not None

    def test_export_imports(self) -> None:
        """Import export subpackage."""
        import russian_piano_composer.export

        assert russian_piano_composer.export is not None

    def test_runtime_imports(self) -> None:
        """Import runtime subpackage."""
        import russian_piano_composer.runtime

        assert russian_piano_composer.runtime is not None
