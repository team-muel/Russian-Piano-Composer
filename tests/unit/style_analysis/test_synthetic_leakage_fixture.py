"""
Unit test for synthetic leakage fixture demonstrating random piece splits vs composer-held-out splits.
"""

from russian_piano_composer.style_analysis.splits import (
    ALL_COMPOSERS,
    RUSSIAN_COMPOSERS,
    make_synthetic_leakage_fixture,
)


def test_synthetic_leakage_fixture_generation() -> None:
    """
    Verify synthetic leakage fixture generates 60 synthetic pieces (10 per composer).
    """
    data = make_synthetic_leakage_fixture()
    assert "piece_ids" in data
    assert "composer_labels" in data
    assert "class_labels" in data
    assert "features" in data

    assert len(data["piece_ids"]) == 60
    assert len(data["composer_labels"]) == 60
    assert len(data["class_labels"]) == 60
    assert len(data["features"]) == 60

    # Verify each composer has 10 pieces
    from collections import Counter
    counts = Counter(data["composer_labels"])
    for comp in ALL_COMPOSERS:
        assert counts[comp] == 10

    # Verify Russian composers have class label 1, Control 0
    for comp, label in zip(data["composer_labels"], data["class_labels"], strict=True):
        if comp in RUSSIAN_COMPOSERS:
            assert label == 1
        else:
            assert label == 0
