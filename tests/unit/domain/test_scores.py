import pytest

from russian_piano_composer.domain import ThemeScores


def test_themescores_valid_construction():
    scores = ThemeScores(
        russian_style=0.9,
        developability=0.8,
        memorability=0.7,
        harmonic_affordance=0.6,
        novelty=0.5,
        coherence=0.4,
        copy_risk=0.1,
        constraint_penalty=0.0
    )
    assert scores.russian_style == 0.9

def test_themescores_invalid_normalized():
    with pytest.raises(ValueError, match="Score russian_style must be in \\[0, 1\\]"):
        ThemeScores(
            russian_style=1.5,
            developability=0.8,
            memorability=0.7,
            harmonic_affordance=0.6,
            novelty=0.5,
            coherence=0.4,
            copy_risk=0.1,
            constraint_penalty=0.0
        )

def test_themescores_invalid_penalty():
    with pytest.raises(ValueError, match="Constraint penalty must be non-negative"):
        ThemeScores(
            russian_style=0.9,
            developability=0.8,
            memorability=0.7,
            harmonic_affordance=0.6,
            novelty=0.5,
            coherence=0.4,
            copy_risk=0.1,
            constraint_penalty=-1.0
        )
