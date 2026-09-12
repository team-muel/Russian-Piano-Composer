"""
Deterministic RandomContext for reproducible stochastic composition generation.
"""
import hashlib
import random
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np

RNG_DERIVATION_VERSION: int = 1
RandomPathComponent = str | int


def _encode_path_component(comp: RandomPathComponent) -> bytes:
    if isinstance(comp, bool) or not isinstance(comp, (str, int)):
        raise TypeError(
            f"Child path components must be str or int, got {type(comp).__name__} ({comp!r})."
        )
    if isinstance(comp, str):
        if not comp:
            raise ValueError("Child path string component cannot be empty.")
        encoded_val = comp.encode("utf-8")
        return f"S:{len(encoded_val)}:".encode() + encoded_val + b";"
    else:
        # int
        if comp < 0:
            raise ValueError(f"Child path integer component must be non-negative, got {comp}.")
        encoded_val = str(comp).encode("utf-8")
        return f"I:{len(encoded_val)}:".encode() + encoded_val + b";"


def _derive_seed(root_seed: int, path: Sequence[RandomPathComponent]) -> int:
    hasher = hashlib.sha256()
    prefix = f"russian-piano-composer|rng-v1|root={root_seed}|path=".encode()
    hasher.update(prefix)
    for comp in path:
        hasher.update(_encode_path_component(comp))
    digest = hasher.digest()
    return int.from_bytes(digest[:16], byteorder="big")


@dataclass(frozen=True, slots=True)
class RandomContext:
    """
    Immutable, hierarchical deterministic random context.
    """
    root_seed: int
    path: tuple[RandomPathComponent, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.root_seed, int) or isinstance(self.root_seed, bool):
            raise TypeError(f"root_seed must be an integer, got {type(self.root_seed).__name__}.")
        if self.root_seed < 0:
            raise ValueError(f"root_seed must be non-negative, got {self.root_seed}.")
        if not isinstance(self.path, tuple):
            raise TypeError(f"path must be a tuple, got {type(self.path).__name__}.")
        for comp in self.path:
            _encode_path_component(comp)

    @property
    def derived_seed(self) -> int:
        """
        Calculates the derived 128-bit integer seed for this context.
        """
        return _derive_seed(self.root_seed, self.path)

    def child(self, *components: RandomPathComponent) -> "RandomContext":
        """
        Derive an independent child context by extending the stream path.
        """
        if not components:
            raise ValueError("child() requires at least one path component.")
        validated: list[RandomPathComponent] = []
        for comp in components:
            _encode_path_component(comp)
            validated.append(comp)
        return RandomContext(self.root_seed, self.path + tuple(validated))

    def python_rng(self) -> random.Random:
        """
        Returns a fresh, seeded Python standard library random.Random instance.
        """
        sub_seed = _derive_seed(self.root_seed, (*self.path, "adapter:python"))
        return random.Random(sub_seed)

    def numpy_rng(self) -> np.random.Generator:
        """
        Returns a fresh, seeded NumPy Generator using explicit PCG64 bit generator.
        """
        sub_seed = _derive_seed(self.root_seed, (*self.path, "adapter:numpy"))
        bit_gen = np.random.PCG64(sub_seed)
        return np.random.Generator(bit_gen)

    def metadata(self) -> dict[str, Any]:
        """
        Exposes serializable metadata for experiment lineage and reproducibility.
        """
        py_sub = _derive_seed(self.root_seed, (*self.path, "adapter:python"))
        np_sub = _derive_seed(self.root_seed, (*self.path, "adapter:numpy"))
        return {
            "root_seed": self.root_seed,
            "path": list(self.path),
            "derived_seed": self.derived_seed,
            "derivation_version": RNG_DERIVATION_VERSION,
            "python_adapter_seed": py_sub,
            "numpy_adapter_seed": np_sub,
            "numpy_bit_generator": "PCG64",
        }
