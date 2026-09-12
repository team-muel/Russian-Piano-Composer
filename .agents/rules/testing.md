# Testing

### Unit Tests
- All modules must have corresponding unit tests
- Use pytest as the test framework
- Tests must be fast and isolated
- Mock external dependencies

### Property-Based Tests
- Use Hypothesis for property-based testing
- Especially important for: interval arithmetic, rhythm operations, pitch representations, transposition invariants
- Properties should express musical invariants (e.g., transposing up then down returns original pitch)

### Golden Regression Tests
- Key outputs must have golden reference files
- Changes to golden outputs require explicit review
- Golden tests protect against silent behavioral drift

### Deterministic Seed Tests
- Any stochastic component must be testable with a fixed seed
- Same seed + same code + same data = same output
- Seed tests verify reproducibility

### No Issue Completion Without Verification
- An issue is not complete until:
  - All new code has tests
  - All tests pass
  - Lint passes (ruff)
  - Type checking passes (mypy)
  - No regressions in existing tests
  - Limitations are documented
