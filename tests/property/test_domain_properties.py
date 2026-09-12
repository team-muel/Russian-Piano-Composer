from fractions import Fraction
from hypothesis import given, strategies as st
from russian_piano_composer.domain import ThemeEvent, ThemeDNA, ThemeScores

@given(st.integers(min_value=0, max_value=127))
def test_valid_midi_values(midi_val: int):
    event = ThemeEvent(
        midi=midi_val,
        onset=Fraction(0),
        duration=Fraction(1),
        metric_position=Fraction(0),
        metric_strength=1.0,
        accent=False
    )
    assert event.midi == midi_val

@given(
    st.integers(min_value=1, max_value=100),
    st.integers(min_value=1, max_value=100)
)
def test_positive_rational_durations(num: int, den: int):
    dur = Fraction(num, den)
    event = ThemeEvent(
        midi=60,
        onset=Fraction(0),
        duration=dur,
        metric_position=Fraction(0),
        metric_strength=1.0,
        accent=False
    )
    assert event.duration == dur

@given(
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=1.0)
)
def test_valid_scores(v1: float, v2: float, v3: float):
    scores = ThemeScores(
        russian_style=v1,
        developability=v2,
        memorability=v3,
        harmonic_affordance=0.5,
        novelty=0.5,
        coherence=0.5,
        copy_risk=0.5,
        constraint_penalty=0.0
    )
    assert scores.russian_style == v1

@given(
    st.floats(min_value=0.0, max_value=1.0),
    st.floats(min_value=0.0, max_value=1.0)
)
def test_composer_weights(w1: float, w2: float):
    # Ensure they sum to <= 1.0
    if w1 + w2 > 1.0:
        w1, w2 = w1 / (w1 + w2), w2 / (w1 + w2)
    w3 = 1.0 - (w1 + w2)
    
    dna = ThemeDNA(
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        12, 16, w1, w2, w3, "test"
    )
    assert abs((dna.medtner + dna.rachmaninoff + dna.scriabin) - 1.0) < 1e-5
