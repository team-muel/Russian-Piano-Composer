from fractions import Fraction

from hypothesis import given
from hypothesis import strategies as st

from russian_piano_composer.theory import (
    Duration,
    TimeSignature,
    dotted,
    get_metric_position,
    subdivide,
)

# Fraction strategy producing valid positive Fraction values
positive_fractions = st.builds(
    Fraction,
    st.integers(min_value=1, max_value=1000),
    st.integers(min_value=1, max_value=1000),
)

non_negative_fractions = st.builds(
    Fraction,
    st.integers(min_value=0, max_value=1000),
    st.integers(min_value=1, max_value=1000),
)

power_of_two_denominators = st.sampled_from([1, 2, 4, 8, 16, 32, 64])


@given(d=positive_fractions, n=st.integers(min_value=1, max_value=64))
def test_subdivide_sum_invariant(d: Fraction, n: int) -> None:
    subs = subdivide(d, n)
    assert len(subs) == n
    assert sum(subs) == d
    for s in subs:
        assert isinstance(s, Fraction)


@given(n=st.integers(min_value=1, max_value=32), d=power_of_two_denominators)
def test_time_signature_bar_duration_invariant(n: int, d: int) -> None:
    ts = TimeSignature(n, d)
    expected_bar_dur = Fraction(n * 4, d)
    assert ts.bar_duration == expected_bar_dur
    assert isinstance(ts.bar_duration, Fraction)


@given(d=positive_fractions)
def test_dotted_zero_dots_invariant(d: Fraction) -> None:
    assert dotted(d, 0) == d


@given(
    d=positive_fractions,
    dots=st.integers(min_value=1, max_value=5),
)
def test_dotted_exact_formula_invariant(d: Fraction, dots: int) -> None:
    result = dotted(d, dots)
    expected = d * Fraction(2 * (2**dots) - 1, 2**dots)
    assert result == expected
    assert isinstance(result, Fraction)


@given(
    onset=non_negative_fractions,
    num=st.integers(min_value=1, max_value=16),
    den=power_of_two_denominators,
)
def test_metric_position_bounds_invariant(onset: Fraction, num: int, den: int) -> None:
    meter = TimeSignature(num, den)
    mp = get_metric_position(onset, meter)
    assert mp.bar_index >= 0
    assert Fraction(0) <= mp.offset < meter.bar_duration
    assert isinstance(mp.offset, Fraction)
    # Exact reconstruction check: onset == bar_index * bar_duration + offset
    reconstructed_onset = mp.bar_index * meter.bar_duration + mp.offset
    assert reconstructed_onset == onset


@given(
    d1=positive_fractions,
    d2=positive_fractions,
)
def test_duration_arithmetic_invariant(d1: Fraction, d2: Fraction) -> None:
    dur1 = Duration(d1)
    dur2 = Duration(d2)
    sum_dur = dur1 + dur2
    assert isinstance(sum_dur.value, Fraction)
    assert sum_dur.value == d1 + d2
