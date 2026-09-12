import pytest
from russian_piano_composer.domain import ThemeDNA

def test_themedna_valid_construction():
    dna = ThemeDNA(
        darkness=0.5, lyricism=0.8, mystery=0.2, agitation=0.1,
        chromaticism=0.4, modal_strength=0.7,
        interval_complexity=0.3, rhythmic_complexity=0.6,
        repetition=0.5, asymmetry=0.5, hook_strength=0.9,
        desired_events=12, desired_range=16,
        medtner=0.3, rachmaninoff=0.5, scriabin=0.2,
        archetype_id="heroic"
    )
    assert dna.darkness == 0.5
    assert dna.desired_events == 12

def test_themedna_invalid_continuous_field():
    with pytest.raises(ValueError, match="darkness must be in \\[0, 1\\]"):
        ThemeDNA(
            darkness=1.5, lyricism=0.8, mystery=0.2, agitation=0.1,
            chromaticism=0.4, modal_strength=0.7,
            interval_complexity=0.3, rhythmic_complexity=0.6,
            repetition=0.5, asymmetry=0.5, hook_strength=0.9,
            desired_events=12, desired_range=16,
            medtner=0.3, rachmaninoff=0.5, scriabin=0.2,
            archetype_id="heroic"
        )

def test_themedna_invalid_composer_weights():
    with pytest.raises(ValueError, match="Composer weights must sum to 1.0"):
        ThemeDNA(
            darkness=0.5, lyricism=0.8, mystery=0.2, agitation=0.1,
            chromaticism=0.4, modal_strength=0.7,
            interval_complexity=0.3, rhythmic_complexity=0.6,
            repetition=0.5, asymmetry=0.5, hook_strength=0.9,
            desired_events=12, desired_range=16,
            medtner=0.5, rachmaninoff=0.5, scriabin=0.5,
            archetype_id="heroic"
        )

def test_themedna_invalid_desired_events():
    with pytest.raises(ValueError, match="desired_events must be positive"):
        ThemeDNA(
            darkness=0.5, lyricism=0.8, mystery=0.2, agitation=0.1,
            chromaticism=0.4, modal_strength=0.7,
            interval_complexity=0.3, rhythmic_complexity=0.6,
            repetition=0.5, asymmetry=0.5, hook_strength=0.9,
            desired_events=0, desired_range=16,
            medtner=0.3, rachmaninoff=0.5, scriabin=0.2,
            archetype_id="heroic"
        )

def test_themedna_invalid_desired_range():
    with pytest.raises(ValueError, match="desired_range must be positive"):
        ThemeDNA(
            darkness=0.5, lyricism=0.8, mystery=0.2, agitation=0.1,
            chromaticism=0.4, modal_strength=0.7,
            interval_complexity=0.3, rhythmic_complexity=0.6,
            repetition=0.5, asymmetry=0.5, hook_strength=0.9,
            desired_events=12, desired_range=0,
            medtner=0.3, rachmaninoff=0.5, scriabin=0.2,
            archetype_id="heroic"
        )
