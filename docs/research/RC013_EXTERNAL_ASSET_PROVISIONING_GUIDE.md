# RC-013 External Asset Provisioning Guide

## Overview

In accordance with repository provenance and licensing governance policies, third-party historical PDF scans and calibration corpora are not committed to Git. Instead, the test suite strictly separates:

1. **Semantic / Metadata / Protocol Tests** (Run in standard clean GitHub Actions CI via `pytest -m "not external_asset"`):
   - Verifies all schema, taxonomy, exclusion rules, cryptographic manifests, feature dependencies, and fail-closed security properties without requiring untracked physical source files.
2. **Physical Asset Integration Tests** (Marked with `@pytest.mark.external_asset`):
   - Verifies physical file integrity, bit-level image binding, and end-to-end multi-engine triangulation against real on-disk historical PDF bytes.

---

## Authoritative Physical PDF Inventory

To run tests marked with `@pytest.mark.external_asset`, download or copy the authoritative public domain source PDFs into `data/scans/rc013/` matching the exact SHA-256 hashes bound in `data/scans/rc013/rc013_scans_manifest.json`:

| File Name | Target Path | Expected SHA-256 | Description |
| :--- | :--- | :--- | :--- |
| `31761108768078.pdf` | `data/scans/rc013/31761108768078.pdf` | `7be339d10787e91eb360ba3cfdcf2da30cfcfcf4b91f1adfd6054f066b1d4410` | Lyadov Op. 40 & Op. 46 (Belaieff, Leipzig) |
| `Arensky_morceaux_op36-1.pdf` | `data/scans/rc013/Arensky_morceaux_op36-1.pdf` | `71dcab764f26830571d7c07b06fc8efda9036c0dbf83cff72f0dd8544d6786a3` | Arensky Op. 36 No. 1 (Jurgenson, Moscow) |
| `Arensky_morceaux_op36-2.pdf` | `data/scans/rc013/Arensky_morceaux_op36-2.pdf` | `e0d9b43db784eb821a719d20c56782ff7754f9a03eb3c4f74d6c6e7a2df25fba` | Arensky Op. 36 No. 2 (Jurgenson, Moscow) |
| `Arensky_Morceaux_op.36_No.13-18.pdf` | `data/scans/rc013/Arensky_Morceaux_op.36_No.13-18.pdf` | `f289cfeb3cb24e8e6e58cb35821fc003d154ee4a460b134dc232da1e7dc65582` | Arensky Op. 36 No. 13 (Jurgenson, Moscow) |
| `Lyapunov_-_Etudes,_Op.11.pdf` | `data/scans/rc013/Lyapunov_-_Etudes,_Op.11.pdf` | `a90d402fae80ea4cb0d82944b1c20e2ef64d7df6395ec1a0c7ec83fb67a07018` | Lyapunov 12 Études d'exécution transcendante Op. 11 (Zimmermann) |

---

## Test Execution Commands

### 1. Standard Clean CI (No Physical Assets Required)
```bash
pytest tests/ -v -m "not external_asset"
```

### 2. Physical Asset Integration Test Suite (Requires Downloaded Assets)
```bash
pytest tests/ -v -m "external_asset"
```

### 3. Full Comprehensive Test Suite (Requires Downloaded Assets)
```bash
pytest tests/ -v
```

---

## Fail-Closed Production Behavior

When `data/scans/rc013/*.pdf` are absent, production evaluation pipelines strictly fail closed with:
```text
FileNotFoundError: SOURCE_BYTES_MISSING: data/scans/rc013/<filename>.pdf
```
This ensures unverified or ungrounded scores can never claim production source fidelity or bypass qualification controls.
