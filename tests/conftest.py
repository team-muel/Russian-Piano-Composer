"""Shared pytest configuration and fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture()
def deterministic_seed() -> int:
    """Provide a fixed seed for deterministic test reproducibility.

    All stochastic tests should use this fixture to ensure
    reproducible results across runs.
    """
    return 42
