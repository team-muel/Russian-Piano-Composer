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
    Outer fold specification holding out exactly 1 class-1 composer and 1 class-0 composer.
    """

    fold_index: int
    held_out_class_1: str
    held_out_class_0: str
    training_class_1: tuple[str, ...]
    training_class_0: tuple[str, ...]

    @property
    def held_out_russian(self) -> str:
        return self.held_out_class_1

    @property
    def held_out_control(self) -> str:
        return self.held_out_class_0

    @property
    def training_russian(self) -> tuple[str, ...]:
        return self.training_class_1

    @property
    def training_control(self) -> tuple[str, ...]:
        return self.training_class_0

    @property
    def name(self) -> str:
        return f"Fold_{self.fold_index:02d}_HeldOut_{self.held_out_class_1}_vs_{self.held_out_class_0}"

    @property
    def training_composers(self) -> tuple[str, ...]:
        return (*self.training_class_1, *self.training_class_0)

    @property
    def test_composers(self) -> tuple[str, ...]:
        return (self.held_out_class_1, self.held_out_class_0)


@dataclass(frozen=True, slots=True)
class ComposerSplitPlan:
    """
    Immutable specification of all 9 outer composer-pair held-out folds.
    """

    folds: tuple[ComposerFold, ...]
    class_1_composers: tuple[str, ...] = RUSSIAN_COMPOSERS
    class_0_composers: tuple[str, ...] = CONTROL_COMPOSERS

    @property
    def russian_composers(self) -> tuple[str, ...]:
        return self.class_1_composers

    @property
    def control_composers(self) -> tuple[str, ...]:
        return self.class_0_composers

    def compute_plan_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the composer split plan.
        """
        canonical = {
            "class_1_composers": list(self.class_1_composers),
            "class_0_composers": list(self.class_0_composers),
            "folds": [
                {
                    "fold_index": f.fold_index,
                    "held_out_class_1": f.held_out_class_1,
                    "held_out_class_0": f.held_out_class_0,
                    "training_class_1": list(f.training_class_1),
                    "training_class_0": list(f.training_class_0),
                }
                for f in self.folds
            ],
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def build_pair_holdout_plan(
    class_1_composers: tuple[str, ...],
    class_0_composers: tuple[str, ...],
) -> ComposerSplitPlan:
    """
    Construct an exact 3 x 3 = 9 outer fold split plan holding out each (class-1, class-0) composer pair.

    Guarantees:
      - Exactly 9 outer folds.
      - Each fold holds out exactly 1 class-1 composer and 1 class-0 composer.
      - Training set contains exactly the remaining 2 class-1 and 2 class-0 composers.
      - Zero train/test composer overlap.
    """
    if len(class_1_composers) != 3 or len(class_0_composers) != 3:
        raise ValueError("Both class_1_composers and class_0_composers must contain exactly 3 composers.")
    if set(class_1_composers).intersection(set(class_0_composers)):
        raise ValueError("class_1_composers and class_0_composers must be disjoint.")

    c1_sorted = tuple(sorted(class_1_composers))
    c0_sorted = tuple(sorted(class_0_composers))

    folds: list[ComposerFold] = []
    idx = 0
    for c1 in c1_sorted:
        for c0 in c0_sorted:
            train_c1 = tuple(c for c in c1_sorted if c != c1)
            train_c0 = tuple(c for c in c0_sorted if c != c0)
            folds.append(
                ComposerFold(
                    fold_index=idx,
                    held_out_class_1=c1,
                    held_out_class_0=c0,
                    training_class_1=train_c1,
                    training_class_0=train_c0,
                )
            )
            idx += 1

    return ComposerSplitPlan(
        folds=tuple(folds),
        class_1_composers=c1_sorted,
        class_0_composers=c0_sorted,
    )


def build_composer_split_plan() -> ComposerSplitPlan:
    """
    Construct the canonical 9 outer Leave-One-Russian + One-Control Composer Pair Out folds.
    """
    return build_pair_holdout_plan(
        class_1_composers=RUSSIAN_COMPOSERS,
        class_0_composers=CONTROL_COMPOSERS,
    )


def compute_composer_split_plan_hash() -> str:
    """Convenience function returning SHA-256 hash of the canonical 9-fold split plan."""
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
