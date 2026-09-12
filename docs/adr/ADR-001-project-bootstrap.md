### Title: ADR-001: Project Bootstrap Decisions

### Status: Accepted
### Date: 2026-09-13

### Context
The Russian Piano Composer project requires a clean, reproducible Python research repository foundation.

### Decisions

1. **Python Version**: Python 3.12 (pinned `>=3.12,<3.13`) for compatibility with music21, ms3, and scientific libraries.
2. **Build System**: hatchling — lightweight, modern PEP 621 compliant, no setup.py needed.
3. **Package Manager**: venv + pip — conventional and well-supported. uv deferred.
4. **Project Layout**: `src/` layout following Python packaging best practices.
5. **Linting**: ruff — fast, comprehensive Python linter.
6. **Type Checking**: mypy — standard Python type checker.
7. **Testing**: pytest + hypothesis — unit tests and property-based testing.
8. **CI**: GitHub Actions (Python 3.12) + local PowerShell script.
9. **Directory Structure**: Follows the specification with .agents/, configs/, data/, docs/, models/, src/, scripts/, tests/, outputs/ top-level directories.

### Consequences
- All development must use Python 3.12 virtual environment
- All subpackages created as stubs — no speculative implementations
- CI runs lint, type-check, and tests — no expensive corpus operations
