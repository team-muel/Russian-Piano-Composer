# Corpus Manifest Schema Specification

## Overview
This document specifies the canonical schema, role semantics, rights requirements, and validation rules for `data/manifests/corpus_manifest.yaml` in the **Russian Piano Composer** project.

## Schema Version
Current schema version: `manifest_version: 1`.

## Corpus Roles
Every registered corpus entry must explicitly declare a `role`:

| Role | Meaning | Generative Pipeline Eligible |
| :--- | :--- | :--- |
| `GENERATIVE_RUSSIAN` | Target Russian late-Romantic / early-modern solo piano repertoire | **YES** (if rights verified) |
| `CONTROL_NON_RUSSIAN` | Non-Russian evaluation data for style discrimination & controls | **NO** (Strictly excluded) |
| `PROVISIONAL` | Repertoire under study; pending rights or scope verification | **NO** |
| `EXCLUDED` | Documented source deliberately excluded from research pipeline | **NO** |

## Fail-Closed Principles
1. **No Defaulting**: Missing or unknown roles raise immediate validation errors. An unknown source NEVER defaults to `GENERATIVE_RUSSIAN`.
2. **Unique Identifiers**: `corpus_id` must be non-empty, lowercase ASCII, and unique across the manifest.
3. **Strict Top-Level Key Validation**: Unknown top-level keys in `corpus_manifest.yaml` trigger validation failures.

## Fields Reference

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `corpus_id` | `str` | Yes | Unique lowercase ASCII identifier (e.g. `dcml_medtner_tales`) |
| `title` | `str` | Yes | Human-readable dataset title |
| `role` | `enum` | Yes | One of `GENERATIVE_RUSSIAN`, `CONTROL_NON_RUSSIAN`, `PROVISIONAL`, `EXCLUDED` |
| `composer` | `str` | Yes | Primary composer name |
| `composer_authority_ids` | `dict` | No | Authority IDs (`viaf`, `wikidata`, `musicbrainz`) |
| `piano_medium` | `enum` | Yes | `SOLO_PIANO`, `PIANO_FOUR_HANDS`, `TWO_PIANOS`, `CONCERTO_ORCHESTRA`, etc. |
| `repertoire_scope` | `str` | Yes | Explicit description of exact works contained |
| `coverage_notes` | `str` | No | Additional notes on completeness or missing pieces |
| `is_complete_for_claimed_scope` | `bool` | Yes | Whether dataset complete for declared scope |
| `work_count` | `int` | No | Number of distinct opus/work cycles |
| `piece_count` | `int` | No | Number of distinct movement/piece files |
| `source_provider` | `str` | Yes | Institution/organization publishing dataset |
| `source_repository` | `str` | Yes | URL to source repository or archive |
| `source_version` | `str` | Yes | Pinned release tag or version string |
| `source_commit` | `str` | No | Pinned Git commit SHA |
| `source_documentation` | `str` | No | URL to upstream README or documentation |
| `doi` | `str` | No | Persistent DOI identifier |
| `citation` | `str` | No | Recommended academic citation string |
| `license` | `str` | Yes | License identifier (e.g. `CC-BY-4.0`, `Public Domain`) |
| `license_url` | `str` | No | URL to official license terms |
| `rights_notes` | `str` | No | Specific notes on usage terms |
| `rights_status` | `enum` | Yes | `VERIFIED`, `REVIEW_REQUIRED`, `UNKNOWN`, `INCOMPATIBLE` |
| `rights_review_required` | `bool` | Yes | Flag indicating pending legal review |
| `provenance_status` | `enum` | Yes | `VERIFIED_SOURCE`, `PARTIALLY_VERIFIED`, `UNVERIFIED` |
| `formats_available` | `list` | Yes | List of `MUSESCORE_MSCX`, `MUSICXML`, `TSV_NOTES`, `MIDI`, etc. |
| `retrieval_method` | `str` | Yes | Method string (e.g. `git_clone`) |
| `verified_at` | `str` | Yes | ISO 8601 verification date (`YYYY-MM-DD`) |

## Logical Manifest Hash
The logical manifest hash is computed deterministically:
$$\text{Hash} = \text{SHA256}(\text{CanonicalJSON}(\text{ManifestData}))$$
This fingerprint is recorded in experiment lineage to detect dataset definition changes regardless of YAML formatting/whitespace modifications.
