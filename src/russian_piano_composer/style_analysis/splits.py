"""
Composer-held-out evaluation split design and synthetic leakage fixture for RC-010.

Defines 9 outer Leave-One-Russian + One-Control Composer Pair Out folds across 6 composers.
Provides a synthetic leakage fixture proving why random piece splits cause composer-identity
leakage and falsely inflated performance.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

RUSSIAN_COMPOSERS: tuple[str, ...] = ("Medtner", "Rachmaninoff", "Tchaikovsky")
CONTROL_COMPOSERS: tuple[str, ...] = ("Chopin", "Liszt", "Schumann")
ALL_COMPOSERS: tuple[str, ...] = (*RUSSIAN_COMPOSERS, *CONTROL_COMPOSERS)

RUSSIAN_CLASS_LABEL: int = 1
CONTROL_CLASS_LABEL: int = 0


def normalize_composer_name(raw_name: str) -> str:
    """
    Map raw composer string from score metadata to canonical composer key.
    """
    if "Medtner" in raw_name:
        return "Medtner"
    if "Rachmaninoff" in raw_name:
        return "Rachmaninoff"
    if "Tchaikovsky" in raw_name:
        return "Tchaikovsky"
    if "Chopin" in raw_name:
        return "Chopin"
    if "Liszt" in raw_name:
        return "Liszt"
    if "Schumann" in raw_name:
        return "Schumann"
    raise ValueError(f"Unrecognized composer string: '{raw_name}'")



@dataclass(frozen=True, slots=True)
class ComposerFold:
    """
    Outer fold specification holding out exactly 1 Russian composer and 1 Control composer.
    """

    fold_index: int
    held_out_russian: str
    held_out_control: str
    training_russian: tuple[str, ...]
    training_control: tuple[str, ...]

    @property
    def name(self) -> str:
        return f"Fold_{self.fold_index:02d}_HeldOut_{self.held_out_russian}_vs_{self.held_out_control}"

    @property
    def training_composers(self) -> tuple[str, ...]:
        return (*self.training_russian, *self.training_control)

    @property
    def test_composers(self) -> tuple[str, ...]:
        return (self.held_out_russian, self.held_out_control)


@dataclass(frozen=True, slots=True)
class ComposerSplitPlan:
    """
    Immutable specification of all 9 outer composer-pair held-out folds.
    """

    folds: tuple[ComposerFold, ...]
    russian_composers: tuple[str, ...] = RUSSIAN_COMPOSERS
    control_composers: tuple[str, ...] = CONTROL_COMPOSERS

    def compute_plan_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the composer split plan.
        """
        canonical = {
            "russian_composers": list(self.russian_composers),
            "control_composers": list(self.control_composers),
            "folds": [
                {
                    "fold_index": f.fold_index,
                    "held_out_russian": f.held_out_russian,
                    "held_out_control": f.held_out_control,
                    "training_russian": list(f.training_russian),
                    "training_control": list(f.training_control),
                }
                for f in self.folds
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def build_composer_split_plan() -> ComposerSplitPlan:
    """
    Construct the canonical 9 outer Leave-One-Russian + One-Control Composer Pair Out folds.
    """
    folds: list[ComposerFold] = []
    idx = 0
    for r_comp in RUSSIAN_COMPOSERS:
        for c_comp in CONTROL_COMPOSERS:
            train_r = tuple(c for c in RUSSIAN_COMPOSERS if c != r_comp)
            train_c = tuple(c for c in CONTROL_COMPOSERS if c != c_comp)
            folds.append(
                ComposerFold(
                    fold_index=idx,
                    held_out_russian=r_comp,
                    held_out_control=c_comp,
                    training_russian=train_r,
                    training_control=train_c,
                )
            )
            idx += 1

    return ComposerSplitPlan(folds=tuple(folds))


def compute_composer_split_plan_hash() -> str:
    """Convenience function returning SHA-256 hash of the 9-fold split plan."""
    return build_composer_split_plan().compute_plan_hash()


def make_synthetic_leakage_fixture() -> dict[str, tuple[Any, ...]]:
    """
    Generates a synthetic dataset demonstrating why random piece splits produce
    falsely high performance due to composer-identity leakage.

    Synthetic construction:
      - 6 composers (3 Russian, 3 Control), 10 pieces each.
      - Predictor 0 ('composer_signature'): strongly encodes composer ID (constant per composer),
        which happens to correlate with class in the training set.
      - Predictor 1 ('noise'): pure random gaussian noise.

    Returns dict with keys:
      'piece_ids', 'composer_labels', 'class_labels', 'features'
    """
    import random

    rng = random.Random(1337)

    piece_ids = []
    composer_labels = []
    class_labels = []
    features = []

    composer_signatures = {
        "Medtner": 1.0,
        "Rachmaninoff": 2.0,
        "Tchaikovsky": 3.0,
        "Chopin": -1.0,
        "Liszt": -2.0,
        "Schumann": -3.0,
    }

    for comp in ALL_COMPOSERS:
        is_rus = 1 if comp in RUSSIAN_COMPOSERS else 0
        sig = composer_signatures[comp]
        for i in range(10):
            pid = f"synthetic_{comp}_{i:02d}"
            noise = rng.gauss(0.0, 1.0)
            piece_ids.append(pid)
            composer_labels.append(comp)
            class_labels.append(is_rus)
            features.append((sig, noise))

    return {
        "piece_ids": tuple(piece_ids),
        "composer_labels": tuple(composer_labels),
        "class_labels": tuple(class_labels),
        "features": tuple(features),
    }
