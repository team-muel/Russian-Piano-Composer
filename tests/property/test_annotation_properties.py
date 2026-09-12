"""
Property-based tests for theme annotation hashing, deterministic IDs, and half-open metric span invariants.
"""
from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from russian_piano_composer.domain.annotations import (
    ScorePosition,
    ThemeRole,
    ThemeSpan,
    compute_annotation_id,
)


@given(
    measure1=st.integers(min_value=0, max_value=100),
    measure2=st.integers(min_value=0, max_value=100),
    offset1_num=st.integers(min_value=0, max_value=16),
    offset2_num=st.integers(min_value=0, max_value=16),
)
def test_property_theme_span_ordering(
    measure1: int, measure2: int, offset1_num: int, offset2_num: int
) -> None:
    off1 = Fraction(offset1_num, 4)
    off2 = Fraction(offset2_num, 4)

    pos1 = ScorePosition(measure1, off1)
    pos2 = ScorePosition(measure2, off2)

    is_valid = (measure2 > measure1) or (measure2 == measure1 and off2 > off1)

    if is_valid:
        span = ThemeSpan(pos1, pos2)
        assert span.start == pos1
        assert span.end == pos2
    else:
        with pytest.raises(ValueError):
            ThemeSpan(pos1, pos2)


@given(
    piece_id=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz0123456789_"),
    measure_idx=st.integers(min_value=0, max_value=50),
)
def test_property_deterministic_id_uniqueness(piece_id: str, measure_idx: int) -> None:
    pos1 = ScorePosition(measure_idx, Fraction(0))
    pos2 = ScorePosition(measure_idx, Fraction(1, 2))
    span = ThemeSpan(pos1, pos2)

    id_a = compute_annotation_id(piece_id, span, ThemeRole.PRIMARY_THEME)
    id_b = compute_annotation_id(piece_id, span, ThemeRole.PRIMARY_THEME)
    assert id_a == id_b

    id_other_role = compute_annotation_id(piece_id, span, ThemeRole.SECONDARY_THEME)
    assert id_a != id_other_role
