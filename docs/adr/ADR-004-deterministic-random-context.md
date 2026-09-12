### Title: ADR-004: Deterministic Hierarchical RandomContext

### Status: Accepted
### Date: 2026-09-13

### Context
The Russian Piano Composer system relies on stochastic generation across multiple independent modules (DNA, rhythm, contour, pitch, hook, candidate sampling, evolutionary search). Using uncontrolled global RNG state (`random.random()`, `np.random.seed()`) or a single shared mutable RNG causes unrelated code modifications and execution ordering variations to perturb downstream random streams, making scientific reproduction impossible.

### Decision
1. **Explicit Root Seed**: All production stochastic generation must begin from an explicit `RandomContext(root_seed)` where `root_seed >= 0`. Global random state and timestamp-based auto-seeding are prohibited.
2. **Cryptographic Seed Derivation**: Child stream seeds are derived using SHA-256 (`hashlib.sha256`) over length-prefixed, type-tagged path components to prevent path collision ambiguities.
3. **Derivation Versioning**: Derivation algorithm includes an explicit version constant (`RNG_DERIVATION_VERSION = 1`).
4. **Child Order Independence**: Derived child streams depend solely on path identity (`root.child("dna")`), not on execution order or which child was derived first.
5. **Fresh Local RNG Adapters**:
   - `python_rng()` returns a fresh `random.Random` instance seeded from adapter sub-path `(*path, "adapter:python")`.
   - `numpy_rng()` returns a fresh `np.random.Generator` using explicit `np.random.PCG64` bit generator seeded from adapter sub-path `(*path, "adapter:numpy")`.
6. **Golden Seed Vectors**: Derivation identity is locked using regression golden seed vectors in tests.

### Rejected Alternatives
- **Global `random` / `np.random` state**: Rejected because global state is non-reproducible and thread-unsafe.
- **Python built-in `hash()`**: Rejected because `hash()` is randomized between process invocations (`PYTHONHASHSEED`).
- **Single shared mutable RNG**: Rejected because consuming random values in one module alters the sequence for all downstream modules.

### Consequences
- **Pros**:
  - Full scientific reproducibility: `(code, config, data, seed) -> identical output`.
  - Child order independence and stream isolation across generation modules.
  - Parallel-safe candidate generation.
  - Traceable experiment lineage.
- **Cons**:
  - Requires explicit `RandomContext` parameter plumbing across generative modules.
