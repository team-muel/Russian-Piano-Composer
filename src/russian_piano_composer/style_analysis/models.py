"""
Deterministic primary classifier specification and fold-level training scaler for RC-010.

Uses a simple, interpretable L2-regularized logistic regression classifier (C=1.0, lbfgs solver, random_state=42).
Enforces training-only scaling using StandardScaler fit strictly on training pieces per outer fold.
"""

import hashlib
import json
from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True, slots=True)
class ModelSpecification:
    """
    Immutable specification of the primary classifier semantics.
    """

    classifier_type: str = "LogisticRegression"
    penalty: str = "l2"
    C: float = 1.0
    solver: str = "lbfgs"
    max_iter: int = 1000
    random_state: int = 42
    fit_intercept: bool = True

    def compute_spec_hash(self) -> str:
        """
        Deterministic SHA-256 hash of the model specification.
        """
        canonical = {
            "classifier_type": self.classifier_type,
            "penalty": self.penalty,
            "C": float(self.C),
            "solver": self.solver,
            "max_iter": self.max_iter,
            "random_state": self.random_state,
            "fit_intercept": self.fit_intercept,
        }
        encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def create_classifier(self) -> LogisticRegression:
        """
        Instantiate a new deterministic LogisticRegression instance.
        """
        return LogisticRegression(
            penalty=self.penalty,
            C=self.C,
            solver=self.solver,
            max_iter=self.max_iter,
            random_state=self.random_state,
            fit_intercept=self.fit_intercept,
        )


def compute_model_spec_hash() -> str:
    """Convenience function returning SHA-256 hash of primary model spec."""
    return ModelSpecification().compute_spec_hash()


def fit_fold_scaler_and_classifier(
    x_train: tuple[tuple[float, ...], ...],
    y_train: tuple[int, ...],
    sample_weights_train: tuple[float, ...] | None = None,
    spec: ModelSpecification | None = None,
) -> tuple[StandardScaler, LogisticRegression]:
    """
    Fit a StandardScaler ONLY on x_train, then fit LogisticRegression on scaled x_train.

    Guarantees:
      - Held-out test pieces never influence scaler parameters (mean, std).
      - Sample weights are applied strictly during scaling and model fitting.
      - Fails closed if any NaNs or Infs are present.
    """
    if spec is None:
        spec = ModelSpecification()

    if not x_train or not y_train:
        raise ValueError("x_train and y_train cannot be empty.")
    if len(x_train) != len(y_train):
        raise ValueError("x_train and y_train row counts must match.")

    # Check missing/non-finite values
    for row in x_train:
        for val in row:
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                raise TypeError(f"Invalid non-numeric feature value {val}.")
            import math
            if math.isnan(val) or math.isinf(val):
                raise ValueError("Missing or non-finite feature value detected in training matrix.")

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(list(x_train), sample_weight=list(sample_weights_train) if sample_weights_train else None)

    clf = spec.create_classifier()
    clf.fit(x_train_scaled, list(y_train), sample_weight=list(sample_weights_train) if sample_weights_train else None)

    return scaler, clf
