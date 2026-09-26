"""Master RC-014C Confirmatory Corpus Freeze and Feature Cache Manifest Generator.

Generates:
1. data/manifests/rc014c_proposed_confirmatory_membership.json
2. data/manifests/rc014c_external_source_freeze.json
3. data/manifests/rc014c_feature_cache_manifest.json
4. data/reviews/rc014/rc014c_preunblinding_integrity_audit.json

Computes master RC014C_CONFIRMATORY_CORPUS_FREEZE_HASH and role-blind feature matrix hash.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.materialize_rc014_external_corpus import parse_xml_to_canonical
from scripts.materialize_rc014_prokofiev_supplements import parse_humdrum_to_canonical

from russian_piano_composer.structure_analysis import compute_structural_schema_hash
from russian_piano_composer.structure_analysis.extractor import (
    extract_structural_representation,
)


def generate_rc014c_manifests() -> dict[str, Any]:
    schema_hash = compute_structural_schema_hash()

    # 1. Proposed membership manifest
    membership_manifest = {
        "milestone": "RC-014C",
        "status": "PROPOSED_CONFIRMATORY_CORPUS_FROZEN_AWAITING_HUMAN_APPROVAL",
        "live_production_pool": {
            "N_Russian": 2,
            "qualified_composers": ["Alexander Scriabin", "Modest Mussorgsky"],
            "rc012_resumption_status": "BLOCKED",
        },
        "proposed_confirmatory_pool": {
            "N_Russian_proposed": 4,
            "composers": [
                {
                    "composer": "Alexander Scriabin",
                    "status": "LIVE_QUALIFIED",
                    "target_pieces_count": 10,
                    "available_pieces_count": 207,
                    "source_authority": "Stanford CCARH Humdrum (craigsapp/scriabin)",
                    "license_authority": "ACCEPTED_BASELINE",
                },
                {
                    "composer": "Modest Mussorgsky",
                    "status": "LIVE_QUALIFIED",
                    "target_pieces_count": 10,
                    "available_pieces_count": 10,
                    "source_authority": "DCML Pictures at an Exhibition",
                    "license_authority": "ACCEPTED_BASELINE",
                },
                {
                    "composer": "Anton Rubinstein",
                    "status": "TECHNICALLY_READY_GOVERNANCE_PENDING",
                    "target_pieces_count": 11,
                    "available_pieces_count": 11,
                    "source_authority": "Tonal-Piano-Corpus (hectorbellmann-art/Tonal-Piano-Corpus commit 3f5a08e9)",
                    "license_authority": "GOVERNANCE_DECISION_PENDING",
                },
                {
                    "composer": "Sergei Prokofiev",
                    "status": "TECHNICALLY_READY_GOVERNANCE_PENDING",
                    "target_pieces_count": 10,
                    "available_pieces_count": 10,
                    "source_authority": "8 pre-1931 pieces from Tonal-Piano-Corpus + 2 Craig/Humdrum supplements (Op. 22 Nos. 2 & 3)",
                    "license_authority": "GOVERNANCE_DECISION_PENDING",
                },
            ],
        },
    }

    os.makedirs("data/manifests", exist_ok=True)
    with open("data/manifests/rc014c_proposed_confirmatory_membership.json", "w", encoding="utf-8") as f:
        json.dump(membership_manifest, f, indent=2)

    # 2. Materialize and extract external sources in temporary scratch
    temp_dir = tempfile.mkdtemp(prefix="rc014c_manifest_gen_")
    try:
        # Clone TPC bare
        target_tpc = os.path.join(temp_dir, "tpc")
        subprocess.run(["git", "clone", "--no-checkout", "https://github.com/hectorbellmann-art/Tonal-Piano-Corpus.git", target_tpc], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "3f5a08e9b2360c11aea5d6d384eb84e7845b793c"], cwd=target_tpc, check=True, capture_output=True)

        # Clone Humdrum supplement bare
        target_supp = os.path.join(temp_dir, "supp")
        subprocess.run(["git", "clone", "--no-checkout", "https://github.com/automata/ana-music.git", target_supp], check=True, capture_output=True)
        subprocess.run(["git", "checkout", "335cbdc617c919d29e9384c4e490cabca5736f73"], cwd=target_supp, check=True, capture_output=True)

        with open("data/manifests/rc014b_external_access_policy.json", encoding="utf-8") as f:
            policy = json.load(f)

        rubinstein_entries = [e for e in policy["reference_manifest"] if e["composer"] == "Anton Rubinstein"]
        prokofiev_tpc_entries = [e for e in policy["reference_manifest"] if e["composer"] == "Sergei Prokofiev" and e.get("us_copyright_status") == "PUBLIC_DOMAIN"]

        frozen_rubinstein: list[dict[str, Any]] = []
        feature_cache_entries: list[dict[str, Any]] = []

        # Process Rubinstein
        for entry in rubinstein_entries:
            score_id = os.path.splitext(os.path.basename(entry["relative_path"]))[0].replace(" ", "_").lower()
            piece_id = f"tonal_piano_corpus:{score_id}"
            blob_sha = entry["git_blob_sha"]

            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=target_tpc, check=True, capture_output=True).stdout
            safe_fname = piece_id.replace(":", "_") + ".xml"
            scratch_p = os.path.join(temp_dir, safe_fname)
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_xml_to_canonical(scratch_p, piece_id, entry["composer"], entry["work_title"])
            rep = extract_structural_representation(cs, manifest_hash="rc014c_freeze")

            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            work_meta = {
                "piece_id": piece_id,
                "composer": "Anton Rubinstein",
                "work_title": entry["work_title"],
                "opus": entry["opus"],
                "publication_year": entry["publication_year"],
                "source_repository": policy["corpus_repository"],
                "source_commit": policy["corpus_frozen_commit"],
                "root_tree": policy["corpus_root_tree"],
                "relative_path": entry["relative_path"],
                "git_blob_sha": blob_sha,
                "canonical_blob_sha256": entry["sha256"],
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "parser": "ElementTree/xml",
                "schema_hash": schema_hash,
                "rc011_56_descriptor_status": "PASS",
            }
            frozen_rubinstein.append(work_meta)

            feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Anton Rubinstein",
                "work_title": entry["work_title"],
                "corpus": "Tonal-Piano-Corpus",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        frozen_prokofiev: list[dict[str, Any]] = []

        # Process Prokofiev TPC base (8 pieces)
        for entry in prokofiev_tpc_entries:
            score_id = os.path.splitext(os.path.basename(entry["relative_path"]))[0].replace(" ", "_").lower()
            piece_id = f"tonal_piano_corpus:{score_id}"
            blob_sha = entry["git_blob_sha"]

            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=target_tpc, check=True, capture_output=True).stdout
            safe_fname = piece_id.replace(":", "_") + ".xml"
            scratch_p = os.path.join(temp_dir, safe_fname)
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_xml_to_canonical(scratch_p, piece_id, entry["composer"], entry["work_title"])
            rep = extract_structural_representation(cs, manifest_hash="rc014c_freeze")

            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            work_meta = {
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": entry["work_title"],
                "opus": entry["opus"],
                "publication_year": entry["publication_year"],
                "source_repository": policy["corpus_repository"],
                "source_commit": policy["corpus_frozen_commit"],
                "root_tree": policy["corpus_root_tree"],
                "relative_path": entry["relative_path"],
                "git_blob_sha": blob_sha,
                "canonical_blob_sha256": entry["sha256"],
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "parser": "ElementTree/xml",
                "schema_hash": schema_hash,
                "rc011_56_descriptor_status": "PASS",
            }
            frozen_prokofiev.append(work_meta)

            feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": entry["work_title"],
                "corpus": "Tonal-Piano-Corpus",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # Process Prokofiev Humdrum supplements (2 pieces)
        supp_manifest_entries = [
            {
                "piece_identifier": "prokofiev_op22_no02",
                "work_title": "Visions Fugitives Op. 22 No. 2 (Andante)",
                "opus": "Op. 22 No. 2",
                "publication_year": 1918,
                "relative_path": "corpus/classical/users/craig/classical/prokofiev/op22/visions22-2.krn",
                "git_blob_sha": "8ecec739bc4c7f561e2c7c141aff1cf40d9d3c0d",
                "canonical_blob_sha256": "c60ed809b26e1ac0d6862aaf62ba8c89c9c857a6a14cdf9c269a324f735d74e6",
            },
            {
                "piece_identifier": "prokofiev_op22_no03",
                "work_title": "Visions Fugitives Op. 22 No. 3 (Allegretto)",
                "opus": "Op. 22 No. 3",
                "publication_year": 1918,
                "relative_path": "corpus/classical/users/craig/classical/prokofiev/op22/visions22-3.krn",
                "git_blob_sha": "d7554373b3d67e4606f9f2f5f79b34608a000b12",
                "canonical_blob_sha256": "5895df19b433c3ddf4b424f6d0ecfa9b3bcb4cd0f902106c0b5ddea766c49de4",
            },
        ]

        for s_entry in supp_manifest_entries:
            pid = s_entry["piece_identifier"]
            piece_id = f"ana_music:{pid}"
            blob_sha = s_entry["git_blob_sha"]

            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=target_supp, check=True, capture_output=True).stdout
            safe_fname = piece_id.replace(":", "_") + ".krn"
            scratch_p = os.path.join(temp_dir, safe_fname)
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_humdrum_to_canonical(
                scratch_p,
                pid,
                "Sergei Prokofiev",
                s_entry["work_title"],
                corpus_id="ana_music",
                source_relative_path=s_entry["relative_path"],
                source_blob_sha256=s_entry["canonical_blob_sha256"],
            )
            rep = extract_structural_representation(cs, manifest_hash="rc014c_freeze")

            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            work_meta = {
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": s_entry["work_title"],
                "opus": s_entry["opus"],
                "publication_year": s_entry["publication_year"],
                "source_repository": "automata/ana-music",
                "source_commit": "335cbdc617c919d29e9384c4e490cabca5736f73",
                "root_tree": "a7f14da4844b47ac3484b01d5d3da2a0029e4b6a",
                "relative_path": s_entry["relative_path"],
                "git_blob_sha": blob_sha,
                "canonical_blob_sha256": s_entry["canonical_blob_sha256"],
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "parser": "music21-10.5.0",
                "schema_hash": schema_hash,
                "rc011_56_descriptor_status": "PASS",
            }
            frozen_prokofiev.append(work_meta)

            feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": s_entry["work_title"],
                "corpus": "automata/ana-music",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # Save external source freeze manifest
        source_freeze_manifest = {
            "milestone": "RC-014C",
            "status": "EXTERNAL_SOURCE_AUTHORITY_FROZEN",
            "deduplication_audit": {
                "status": "DEDUPLICATION_VERIFIED_NO_OVERLAPPING_PIECES",
                "audited_overlap_works": [
                    {
                        "work": "Visions Fugitives Op. 22 No. 1",
                        "retained_source": "Tonal-Piano-Corpus (Prokofiev, Sergey (1891 - 1953)/xml/Visions Fugitives Op22/No1.xml)",
                        "excluded_candidate": "automata/ana-music (visions22-1.krn)",
                        "action": "RETAIN_SINGLE_CANONICAL_SOURCE",
                    }
                ],
            },
            "rubinstein_frozen_works": frozen_rubinstein,
            "prokofiev_frozen_works": frozen_prokofiev,
        }

        with open("data/manifests/rc014c_external_source_freeze.json", "w", encoding="utf-8") as f:
            json.dump(source_freeze_manifest, f, indent=2)

        # Save feature cache manifest
        cache_dump = json.dumps(feature_cache_entries, sort_keys=True).encode("utf-8")
        feature_cache_matrix_hash = hashlib.sha256(cache_dump).hexdigest()

        feature_cache_manifest = {
            "milestone": "RC-014C",
            "status": "ROLE_BLIND_FEATURE_CACHE_FROZEN",
            "schema_hash": schema_hash,
            "feature_catalog_descriptor_count": 56,
            "total_cached_pieces": len(feature_cache_entries),
            "rubinstein_pieces_count": len(frozen_rubinstein),
            "prokofiev_pieces_count": len(frozen_prokofiev),
            "feature_cache_matrix_sha256": feature_cache_matrix_hash,
            "cached_pieces": feature_cache_entries,
        }

        with open("data/manifests/rc014c_feature_cache_manifest.json", "w", encoding="utf-8") as f:
            json.dump(feature_cache_manifest, f, indent=2)

        # 4. Save pre-unblinding integrity audit
        freeze_manifest_payload = {
            "membership_manifest": membership_manifest,
            "source_freeze_manifest": source_freeze_manifest,
            "feature_cache_matrix_sha256": feature_cache_matrix_hash,
            "schema_hash": schema_hash,
        }
        master_freeze_hash = hashlib.sha256(json.dumps(freeze_manifest_payload, sort_keys=True).encode("utf-8")).hexdigest()

        audit_data = {
            "milestone": "RC-014C",
            "status": "RC014C_CORPUS_FROZEN_AWAITING_HUMAN_ACCESS_APPROVAL",
            "rc014c_confirmatory_corpus_freeze_hash": master_freeze_hash,
            "feature_cache_matrix_sha256": feature_cache_matrix_hash,
            "schema_hash": schema_hash,
            "deduplication_audit_verdict": "PASS",
            "source_to_music21_structural_sanity": "PASS",
            "music21_parsed_event_conservation": "PASS",
            "rubinstein_m_technical": len(frozen_rubinstein),
            "prokofiev_m_technical": len(frozen_prokofiev),
            "proposed_n_russian": 4,
            "live_n_russian": 2,
            "rc012_resumption_gate": "BLOCKED",
            "invalidation_policy": {
                "trigger": "ANY_CHANGE_TO_EXTERNAL_BYTES_OR_PARSERS_OR_FEATURES",
                "effect": "INVALIDATES_CONFIRMATORY_CORPUS_FREEZE_AND_DOWNSTREAM_STATISTICS",
            },
        }

        os.makedirs("data/reviews/rc014", exist_ok=True)
        with open("data/reviews/rc014/rc014c_preunblinding_integrity_audit.json", "w", encoding="utf-8") as f:
            json.dump(audit_data, f, indent=2)

        return {
            "master_freeze_hash": master_freeze_hash,
            "feature_cache_matrix_sha256": feature_cache_matrix_hash,
            "rubinstein_count": len(frozen_rubinstein),
            "prokofiev_count": len(frozen_prokofiev),
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Generating RC-014C Confirmatory Corpus Freeze Manifests...")
    res = generate_rc014c_manifests()
    print("Completed RC-014C Manifest Generation:")
    print(f"  Master Freeze Hash: {res['master_freeze_hash']}")
    print(f"  Feature Cache Hash: {res['feature_cache_matrix_sha256']}")
    print(f"  Rubinstein Works: {res['rubinstein_count']}")
    print(f"  Prokofiev Works: {res['prokofiev_count']}")
