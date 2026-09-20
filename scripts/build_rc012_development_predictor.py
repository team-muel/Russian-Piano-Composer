"""
Script to fit and freeze the primary RC-012 Development Predictor on the 141 development pieces.
Strictly role-blind feature extraction from RC-011 frozen structural matrix.
Weights each development composer equally (w_{c,i} = 1 / (6 * N_c)).
Fills and serializes the frozen predictor bundle, computing RC012_FROZEN_PREDICTOR_BUNDLE_HASH.
"""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from russian_piano_composer.structure_analysis.schema import STRUCTURAL_FEATURE_CATALOG

EXPECTED_CANONICAL_MANIFEST_HASH: str = "cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212"
EXPECTED_STRUCTURAL_MATRIX_HASH: str = "7e141a62bed72d10a894d7fa3123619aacce85797b1953423fd8de2b5b069bc0"
EXPECTED_SAMPLE_COUNT: int = 141
EXPECTED_COMPOSERS: list[str] = [
    "Franz Liszt",
    "Frédéric Chopin",
    "Nikolai Medtner",
    "Pyotr Ilyich Tchaikovsky",
    "Robert Schumann",
    "Sergei Rachmaninoff",
]


def build_and_freeze_development_predictor() -> dict:
    matrix_path = Path("data/features/structural_v1/structural_matrix.parquet")
    if not matrix_path.exists():
        print(f"Error: {matrix_path} not found.")
        sys.exit(1)

    df = pd.read_parquet(matrix_path)
    if len(df) != EXPECTED_SAMPLE_COUNT:
        raise ValueError(f"Expected {EXPECTED_SAMPLE_COUNT} rows, found {len(df)}")

    feature_cols = sorted([d.feature_id for d in STRUCTURAL_FEATURE_CATALOG])
    if len(feature_cols) != 56:
        raise ValueError(f"Expected 56 features, found {len(feature_cols)}")

    # Verify composers
    composers = df["composer"].values
    unique_composers = sorted(list(set(composers)))
    if unique_composers != EXPECTED_COMPOSERS:
        raise ValueError(f"Unexpected composers: {unique_composers}")

    x_features = df[feature_cols].values.astype(float)
    y = (df["corpus_role"] == "GENERATIVE_RUSSIAN").astype(int).values

    # Compute composer-balanced weights: w_{c, i} = 1 / (6 * N_c)
    unique_c, counts = np.unique(composers, return_counts=True)
    c_count_map = dict(zip(unique_c, counts, strict=True))
    weights = np.array([1.0 / (6.0 * c_count_map[c]) for c in composers], dtype=float)

    # Weighted mean and variance for explicit, reproducible standardization
    weighted_mean = np.average(x_features, axis=0, weights=weights)
    weighted_var = np.average((x_features - weighted_mean) ** 2, axis=0, weights=weights)
    weighted_scale = np.sqrt(weighted_var)

    # Standardize X using weighted moments
    x_scaled = (x_features - weighted_mean) / weighted_scale

    # Fit LogisticRegression
    clf = LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", random_state=42)
    clf.fit(x_scaled, y, sample_weight=weights)

    train_acc_weighted = float(clf.score(x_scaled, y, sample_weight=weights))
    train_acc_unweighted = float(clf.score(x_scaled, y))

    print("--- RC-012 Development Predictor Fitting Summary ---")
    print(f"  Training Pieces:            {len(x_features)}")
    print(f"  Training Composers:         {len(unique_composers)}")
    print(f"  Features Count:             {len(feature_cols)}")
    print(f"  Weighted Training Accuracy: {train_acc_weighted * 100:.2f}%")
    print(f"  Unweighted Accuracy:        {train_acc_unweighted * 100:.2f}%")
    print(f"  Intercept:                  {float(clf.intercept_[0]):.8f}")

    bundle = {
        "version": "RC012_FROZEN_PREDICTOR_V1",
        "parent_manifest_hash": EXPECTED_CANONICAL_MANIFEST_HASH,
        "parent_structural_matrix_hash": EXPECTED_STRUCTURAL_MATRIX_HASH,
        "model_family": "LOGISTIC_REGRESSION",
        "hyperparameters": {
            "C": 1.0,
            "penalty": "l2",
            "solver": "lbfgs",
            "random_state": 42,
        },
        "feature_names": feature_cols,
        "scaler": {
            "mean": [round(float(v), 10) for v in weighted_mean],
            "scale": [round(float(v), 10) for v in weighted_scale],
        },
        "coefficients": [round(float(v), 10) for v in clf.coef_[0]],
        "intercept": round(float(clf.intercept_[0]), 10),
        "training_sample_count": len(x_features),
        "training_composers": unique_composers,
        "training_weighted_accuracy": round(train_acc_weighted, 6),
        "training_unweighted_accuracy": round(train_acc_unweighted, 6),
    }

    bundle_encoded = json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    bundle_hash = hashlib.sha256(bundle_encoded).hexdigest()
    bundle["predictor_bundle_hash"] = bundle_hash

    output_dir = Path("models/rc012_predictor")
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / "frozen_predictor_bundle.json"
    with open(bundle_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2, sort_keys=True)

    print(f"\nSaved Frozen Predictor Bundle to: {bundle_path}")
    print(f"RC012_FROZEN_PREDICTOR_BUNDLE_HASH: {bundle_hash}")
    return bundle


if __name__ == "__main__":
    build_and_freeze_development_predictor()
