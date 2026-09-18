# Russian Piano Composer

An interpretable symbolic composition system for autonomous generation of original Russian late-Romantic / early-modern piano music.

## Project Goals

- Generate original piano music that belongs to the Russian piano tradition
- Ensure all output is physically playable by a human pianist
- Maintain scientific rigor with corpus-driven style analysis
- Export valid MusicXML and MIDI

## Status

**Current milestone**: RC-009B (Unsupervised Candidate Thematic Unit Discovery & Held-Out Future-Reuse Validation)

## Quick Start

```powershell
# Create virtual environment (requires Python 3.12)
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1

# Install in development mode
pip install -e ".[dev]"

# Run verification
powershell -File ci.ps1
```

## Development

```powershell
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test
pytest tests/ -v
```

## Project Structure

```
src/russian_piano_composer/
├── domain/      # Core domain models
├── theory/      # Music theory representations
├── corpus/      # Corpus ingestion and management
├── models/      # Statistical and generative models
├── generation/  # Theme and music generation
├── critics/     # Evaluation critics
├── search/      # Search and optimization
├── piano/       # Piano-specific constraints
├── export/      # MusicXML/MIDI export
└── runtime/     # Runtime configuration
```

## License

TBD
