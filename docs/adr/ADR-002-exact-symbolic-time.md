### Title: ADR-002: Exact Fraction-Based Symbolic Time Representation

### Status: Accepted
### Date: 2026-09-13

### Context
Future theme generation, rhythmic tuplets, corpus alignment, meter analysis, bar validation, and deterministic output require exact rational arithmetic. Floating-point timing values introduce cumulative rounding errors, non-deterministic equality checks, and floating-point drift across rhythmic subdivisions and bar boundaries.

### Decision
Canonical symbolic timing and duration representations across the domain and theory layers use standard Python `fractions.Fraction`.

Key conventions:
1. **Canonical Unit**: Quarter note duration = `1` (`Fraction(1)`).
2. **Standard Durations**: Whole note = `4`, Half note = `2`, Eighth note = `1/2`, Sixteenth note = `1/4`, Thirty-second note = `1/8`.
3. **Bar Durations**: Calculated exactly as $B = N \times (4 / D)$ (e.g. `3/4` = `3`, `6/8` = `3`, `12/8` = `6`).
4. **Input Policy**: Accept `Fraction` and `int` for onset and duration parameters, normalizing immediately to `Fraction`. Reject floating-point canonical timing.

### Rejected Alternatives
- **Floating-point canonical timing**: Rejected due to cumulative rounding errors and non-deterministic comparisons.
- **MIDI Ticks as canonical representation**: Rejected because tick resolutions (e.g. 480 or 960 TPQ) hardcode resolution limits and belong strictly to export/import serialization.

### Consequences
- **Pros**:
  - Exact mathematical equality comparisons (`Fraction(1, 2) == Fraction(2, 4)`).
  - Deterministic generation and exact tuplet/subdivision calculations without drift.
  - Bar duration validation without epsilon tolerances (`abs(total - bar_duration) < 1e-9` is eliminated).
- **Cons**:
  - Slight execution overhead relative to primitive floats (negligible for symbolic music generation).
  - External format exporters (e.g. MIDI, audio rendering) must explicitly convert exact fractions to ticks or seconds at boundary interfaces.
