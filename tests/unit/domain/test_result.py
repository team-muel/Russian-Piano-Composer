from fractions import Fraction

import pytest

from russian_piano_composer.domain import (
    GenerationResult,
    ScoredTheme,
    Theme,
    ThemeDNA,
    ThemeEvent,
    ThemeScores,
)


def get_scored_theme() -> ScoredTheme:
    event = ThemeEvent(60, Fraction(0), Fraction(1), Fraction(0), 1.0, False)
    theme = Theme((event,), 0, "minor", 4, 4, 2, "lyrical", 42)
    scores = ThemeScores(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.1, 0.0)
    return ScoredTheme(theme, scores)

def get_dna() -> ThemeDNA:
    return ThemeDNA(
        0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,
        12, 16, 0.4, 0.4, 0.2, "test"
    )

def test_result_valid():
    scored = get_scored_theme()
    dna = get_dna()
    result = GenerationResult(
        best=scored,
        pareto_front=(scored,),
        candidates_evaluated=10,
        dna=dna,
        seed=42
    )
    assert result.candidates_evaluated == 10

def test_result_invalid_candidates():
    scored = get_scored_theme()
    dna = get_dna()
    with pytest.raises(ValueError, match="candidates_evaluated must be >= 1"):
        GenerationResult(scored, (scored,), 0, dna, 42)

def test_result_best_without_pareto():
    scored = get_scored_theme()
    dna = get_dna()
    with pytest.raises(ValueError, match="pareto_front cannot be empty if best is provided"):
        GenerationResult(scored, (), 10, dna, 42)

def test_result_best_not_in_pareto():
    scored1 = get_scored_theme()
    # Different theme instance for pareto front
    event = ThemeEvent(61, Fraction(0), Fraction(1), Fraction(0), 1.0, False)
    theme2 = Theme((event,), 0, "minor", 4, 4, 2, "lyrical", 42)
    scores2 = ThemeScores(0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.1, 0.0)
    scored2 = ScoredTheme(theme2, scores2)

    dna = get_dna()
    with pytest.raises(ValueError, match="best must belong to pareto_front"):
        GenerationResult(scored1, (scored2,), 10, dna, 42)
