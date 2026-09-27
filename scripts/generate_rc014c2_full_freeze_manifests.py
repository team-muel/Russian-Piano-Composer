"""Master RC-014C.2 Complete Confirmatory Corpus Freeze and Real Feature Cache Manifest Generator.

Generates:
1. data/manifests/rc014c2_complete_confirmatory_membership.json
2. data/manifests/rc014c2_complete_source_freeze.json (483/483 bound with zero missing hashes)
3. data/manifests/rc014c2_complete_role_blind_feature_cache.json (483 real extracted rows, zero placeholders)
4. data/reviews/rc014/rc014c2_preunblinding_integrity_audit.json

Reconciles full 9-composer confirmatory corpus (483 total pieces):
- Russian (4 composers, 246 pieces):
  - Alexander Scriabin: 207 pieces (craigsapp/scriabin)
  - Modest Mussorgsky: 18 pieces (SyMuPe/PERiScoPe)
  - Anton Rubinstein: 11 pieces (Tonal-Piano-Corpus)
  - Sergei Prokofiev: 10 pieces (8 TPC + 2 Humdrum supplements)
- Control (5 composers, 237 pieces):
  - Edvard Grieg: 66 pieces (DCMLab/grieg_lyric_pieces)
  - Claude Debussy: 54 pieces (7 DCMLab collections)
  - Ludwig van Beethoven: 91 pieces (DCMLab/beethoven_piano_sonatas)
  - Béla Bartók: 14 pieces (DCMLab/bartok_bagatelles)
  - Antonín Dvořák: 12 pieces (DCMLab/dvorak_silhouettes)

Computes master RC014C2_CONFIRMATORY_CORPUS_FREEZE_HASH and role-blind feature cache matrix SHA-256.
Explicitly supersedes invalid placeholder freeze hashes.
Enforces fail-closed preregistration gate: live N_Russian remains 2, RC-012 resumption remains BLOCKED.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from fractions import Fraction
from pathlib import Path
from typing import Any

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import music21 as m21
from scripts.materialize_rc014_external_corpus import parse_xml_to_canonical
from scripts.materialize_rc014_prokofiev_supplements import (
    m21_pitch_to_spelled,
    parse_humdrum_to_canonical,
)

from russian_piano_composer.corpus.adapters.dcml_ms3 import (
    ingest_score_entry_from_ms3,
    resolve_score_file,
)
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.domain.score import (
    CanonicalMeasure,
    CanonicalScore,
    CanonicalScoreEvent,
    EventKind,
    TieState,
)
from russian_piano_composer.structure_analysis import compute_structural_schema_hash
from russian_piano_composer.structure_analysis.extractor import (
    extract_structural_representation,
)
from russian_piano_composer.theory.meter import TimeSignature

SUPERSEDED_INVALID_PLACEHOLDER_FREEZE_HASH_RC014C1 = "06173918554380617153cadd4de66443733c33d52dbbe54813a10846b24e6330"
SUPERSEDED_INVALID_PLACEHOLDER_FEATURE_CACHE_SHA256_RC014C1 = "093d262da6ee7decce2026966be4b251d843c2c5836a2c4359d7609fefd8b28b"
SUPERSEDED_INCOMPLETE_FREEZE_HASH_RC014C = "782f0cbd26e252985ba28d7cdd8bc69486ed2c3f933c2333711c435d4c40d9a8"


def parse_m21_mxl_to_canonical(
    score: m21.stream.Score,
    corpus_id: str,
    score_entry_id: str,
    composer: str,
    title: str,
    source_repo: str,
    source_commit: str,
    source_rel_path: str,
    source_sha256: str,
    manifest_hash: str = "rc014c2_freeze",
) -> CanonicalScore:
    """Parse a music21 Score object (e.g. from MXL) into a validated CanonicalScore."""
    piece_id = f"{corpus_id}:{score_entry_id}"
    measures: list[CanonicalMeasure] = []
    p0 = score.parts[0]
    p0_m = list(p0.getElementsByClass(m21.stream.Measure))
    measure_onsets: dict[int, Fraction] = {}
    curr_ts = TimeSignature(4, 4)

    for m_idx, m in enumerate(p0_m):
        ts_l = m.getElementsByClass(m21.meter.TimeSignature)
        if ts_l:
            curr_ts = TimeSignature(ts_l[0].numerator, ts_l[0].denominator)
        g_onset = Fraction(str(m.offset)).limit_denominator(1920)
        measure_onsets[m_idx] = g_onset
        bar_dur = curr_ts.bar_duration
        measures.append(
            CanonicalMeasure(
                piece_id=piece_id,
                measure_index=m_idx,
                source_measure_label=str(m.number),
                global_onset=g_onset,
                actual_duration=bar_dur,
                time_signature=curr_ts,
                expected_duration=bar_dur,
                is_pickup=False,
            )
        )

    raw_events: list[tuple[Any, ...]] = []
    for p_idx, part in enumerate(score.parts):
        staff_num = p_idx + 1
        p_measures = list(part.getElementsByClass(m21.stream.Measure))
        for m_idx, m in enumerate(p_measures):
            m_label = str(m.number)
            m_onset = measure_onsets.get(m_idx, Fraction(str(m.offset)).limit_denominator(1920))
            for el in m.recurse():
                if not isinstance(el, (m21.note.Note, m21.chord.Chord, m21.note.Rest)):
                    continue
                offset_in_m = Fraction(str(el.getOffsetInHierarchy(m))).limit_denominator(1920)
                g_onset = m_onset + offset_in_m
                dur = Fraction(str(el.duration.quarterLength)).limit_denominator(1920)
                is_grace = bool(el.duration.isGrace)
                if is_grace and dur == 0:
                    dur = Fraction(0, 1)
                elif dur <= 0:
                    dur = Fraction(1, 4)
                voice_num = 1
                if getattr(el, "voice", None) is not None and str(el.voice).isdigit():
                    voice_num = int(el.voice)

                if isinstance(el, m21.note.Note):
                    pitch = m21_pitch_to_spelled(el.pitch)
                    raw_events.append((
                        g_onset, m_idx, staff_num, voice_num, EventKind.NOTE,
                        m_label, offset_in_m, dur, pitch, pitch.midi, is_grace, TieState.NONE
                    ))
                elif isinstance(el, m21.chord.Chord):
                    for n in el.notes:
                        pitch = m21_pitch_to_spelled(n.pitch)
                        raw_events.append((
                            g_onset, m_idx, staff_num, voice_num, EventKind.NOTE,
                            m_label, offset_in_m, dur, pitch, pitch.midi, is_grace, TieState.NONE
                        ))
                elif isinstance(el, m21.note.Rest):
                    raw_events.append((
                        g_onset, m_idx, staff_num, voice_num, EventKind.REST,
                        m_label, offset_in_m, dur, None, None, is_grace, TieState.NONE
                    ))

    raw_events.sort(key=lambda e: (e[0], e[1], e[2], e[3], e[4].value, e[9] if e[9] is not None else -1))
    events: list[CanonicalScoreEvent] = []
    for evt_idx, e in enumerate(raw_events):
        events.append(
            CanonicalScoreEvent(
                piece_id=piece_id,
                event_id=f"{piece_id}:evt_{evt_idx:06d}",
                event_index=evt_idx,
                event_kind=e[4],
                measure_index=e[1],
                source_measure_label=e[5],
                staff=e[2],
                voice=e[3],
                global_onset=e[0],
                offset_in_measure=e[6],
                duration=e[7],
                pitch=e[8],
                midi=e[9],
                is_grace=e[10],
                tie_state=e[11],
            )
        )

    return CanonicalScore(
        piece_id=piece_id,
        corpus_id=corpus_id,
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN if composer in {"Alexander Scriabin", "Modest Mussorgsky", "Anton Rubinstein", "Sergei Prokofiev"} else CorpusRole.CONTROL_NON_RUSSIAN,
        score_entry_id=score_entry_id,
        composer=composer,
        title=title,
        source_repository=source_repo,
        source_commit=source_commit,
        source_relative_path=source_rel_path,
        source_sha256=source_sha256,
        manifest_hash=manifest_hash,
        parser_name="music21",
        parser_version="10.5.0",
        measures=tuple(measures),
        events=tuple(events),
    )


def generate_rc014c2_manifests() -> dict[str, Any]:
    schema_hash = compute_structural_schema_hash()

    # ==============================================================================
    # 1. Complete Confirmatory Membership Manifest (9 composers, 483 pieces)
    # ==============================================================================
    membership_manifest = {
        "milestone": "RC-014C.2",
        "status": "TRUE_FULL_CONFIRMATORY_CORPUS_FROZEN_AWAITING_HUMAN_APPROVAL",
        "governance_model": "FAIL_CLOSED_IMMUTABLE_PREREGISTRATION",
        "preregistration_contract": {
            "min_russian_composers": 4,
            "min_control_composers": 4,
            "min_pieces_per_counted_composer": 10,
            "repertoire_sampling_rule": "USE_ALL_ELIGIBLE_PIECES",
            "composer_count_relaxation_permitted": False,
        },
        "live_production_pool": {
            "N_Russian": 2,
            "qualified_composers": ["Alexander Scriabin", "Modest Mussorgsky"],
            "rc012_resumption_status": "BLOCKED",
            "block_reason": "N_Russian = 2 < 4 (Preregistered minimum 4 Russian composers required)",
        },
        "confirmatory_pool": {
            "N_Russian_confirmatory": 4,
            "N_Control_confirmatory": 5,
            "total_composers_count": 9,
            "total_pieces_count": 483,
            "russian_pieces_count": 246,
            "control_pieces_count": 237,
            "russian_composers": [
                {
                    "composer": "Alexander Scriabin",
                    "class": "Russian",
                    "status": "LIVE_QUALIFIED",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 207,
                    "source_authority": "Stanford CCARH Humdrum (craigsapp/scriabin commit 7daa1136)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Modest Mussorgsky",
                    "class": "Russian",
                    "status": "LIVE_QUALIFIED",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 18,
                    "source_authority": "SyMuPe/PERiScoPe v1.1 (15 Pictures at an Exhibition + 3 standalone pieces)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Anton Rubinstein",
                    "class": "Russian",
                    "status": "TECHNICALLY_READY_GOVERNANCE_PENDING",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 11,
                    "source_authority": "Tonal-Piano-Corpus (hectorbellmann-art/Tonal-Piano-Corpus commit 3f5a08e9)",
                    "license_authority": "GOVERNANCE_DECISION_PENDING",
                },
                {
                    "composer": "Sergei Prokofiev",
                    "class": "Russian",
                    "status": "TECHNICALLY_READY_GOVERNANCE_PENDING",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 10,
                    "source_authority": "8 pre-1929 pieces from Tonal-Piano-Corpus + 2 Craig/Humdrum supplements (Op. 22 Nos. 2 & 3)",
                    "license_authority": "GOVERNANCE_DECISION_PENDING",
                },
            ],
            "control_composers": [
                {
                    "composer": "Edvard Grieg",
                    "class": "Control",
                    "status": "QUALIFIED_BASELINE",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 66,
                    "source_authority": "DCMLab/grieg_lyric_pieces (commit 91a30456)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Claude Debussy",
                    "class": "Control",
                    "status": "QUALIFIED_BASELINE",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 54,
                    "source_authority": "7 DCMLab collections (suite_bergamasque, preludes, etudes, childrens_corner, estampes, deux_arabesques, pour_le_piano)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Ludwig van Beethoven",
                    "class": "Control",
                    "status": "QUALIFIED_BASELINE",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 91,
                    "source_authority": "DCMLab/beethoven_piano_sonatas (commit ea7181bf)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Béla Bartók",
                    "class": "Control",
                    "status": "QUALIFIED_BASELINE",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 14,
                    "source_authority": "DCMLab/bartok_bagatelles (commit c6221f6e)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
                {
                    "composer": "Antonín Dvořák",
                    "class": "Control",
                    "status": "QUALIFIED_BASELINE",
                    "minimum_threshold_Mc": 10,
                    "eligible_pieces_count": 12,
                    "source_authority": "DCMLab/dvorak_silhouettes (commit f228006f)",
                    "license_authority": "ACCEPTED_BASELINE (CC-BY-NC-SA-4.0)",
                },
            ],
        },
    }

    os.makedirs("data/manifests", exist_ok=True)
    with open("data/manifests/rc014c2_complete_confirmatory_membership.json", "w", encoding="utf-8") as f:
        json.dump(membership_manifest, f, indent=2)

    # ==============================================================================
    # 2. Materialize All Repositories into Temporary Scratch
    # ==============================================================================
    temp_dir = tempfile.mkdtemp(prefix="rc014c2_full_mat_")
    print(f"Materializing confirmatory corpus into isolated scratch: {temp_dir}...")

    all_source_works: list[dict[str, Any]] = []
    all_feature_cache_entries: list[dict[str, Any]] = []

    try:
        # Clone Git Repositories
        repos = [
            ("scriabin", "https://github.com/craigsapp/scriabin.git", "7daa1136a4edfaf8d2bfadee973c33f3b76b6760"),
            ("grieg", "https://github.com/DCMLab/grieg_lyric_pieces.git", "91a304563521f3f273b8c0aadec1ce2ede2d1384"),
            ("deb_bergamasque", "https://github.com/DCMLab/debussy_suite_bergamasque.git", "322ece590e536924308a551a69d9c1520248d3d5"),
            ("deb_preludes", "https://github.com/DCMLab/debussy_preludes.git", "1d3d5d2fad9bc80029bce10aa8af486efe983b7f"),
            ("deb_etudes", "https://github.com/DCMLab/debussy_etudes.git", "02e6b0610351a3687a652eb18195111f2fed57ca"),
            ("deb_children", "https://github.com/DCMLab/debussy_childrens_corner.git", "f4bf168540a369a360550c9136fe2954cc8402d5"),
            ("deb_estampes", "https://github.com/DCMLab/debussy_estampes.git", "7fff184fb6a24eaeb9923c69fe5ae058db92f29a"),
            ("deb_arabesques", "https://github.com/DCMLab/debussy_deux_arabesques.git", "acf40ce6ec0da1175c767bfaef4b5fde63f3d7e4"),
            ("deb_pour_le_piano", "https://github.com/DCMLab/debussy_pour_le_piano.git", "d288cbf3b5480a6b1f83ba279d6253fc5320de9b"),
            ("beethoven", "https://github.com/DCMLab/beethoven_piano_sonatas.git", "ea7181bff88abc8713257234f7ec4033178c57a9"),
            ("bartok", "https://github.com/DCMLab/bartok_bagatelles.git", "c6221f6ecb4dbcd476e827f6bf8705bdcb15c8a9"),
            ("dvorak", "https://github.com/DCMLab/dvorak_silhouettes.git", "f228006fcd8696c809cfc8e701ed215cec3d07f1"),
            ("tpc", "https://github.com/hectorbellmann-art/Tonal-Piano-Corpus.git", "3f5a08e9b2360c11aea5d6d384eb84e7845b793c"),
            ("supp", "https://github.com/automata/ana-music.git", "335cbdc617c919d29e9384c4e490cabca5736f73"),
        ]

        repo_paths: dict[str, str] = {}
        for name, url, commit in repos:
            dest = os.path.join(temp_dir, name)
            subprocess.run(["git", "clone", "--depth", "1", url, dest], check=True, capture_output=True)
            subprocess.run(["git", "checkout", commit], cwd=dest, check=True, capture_output=True)
            repo_key = url.replace("https://github.com/", "").replace(".git", "")
            repo_paths[repo_key] = dest

        # Stream Mussorgsky from Hugging Face PERiScoPe
        print("Streaming Mussorgsky PERiScoPe MXL files from Hugging Face...")
        mussorgsky_mxl_bytes: dict[str, bytes] = {}
        hf_url = "https://huggingface.co/datasets/SyMuPe/PERiScoPe/resolve/main/v1.1/periscope_raw_v1.1.tar.gz"
        req = urllib.request.Request(hf_url, headers={"User-Agent": "Mozilla/5.0"})
        with (
            urllib.request.urlopen(req, timeout=120) as resp,
            tarfile.open(fileobj=resp, mode="r|gz") as tar,
        ):
                for member in tar:
                    if "modest_mussorgsky" in member.name.lower() and member.name.endswith(".mxl"):
                        f_obj = tar.extractfile(member)
                        if f_obj is not None:
                            mussorgsky_mxl_bytes[member.name] = f_obj.read()

        print(f"Retrieved {len(mussorgsky_mxl_bytes)} Mussorgsky MXL files.")

        # ==============================================================================
        # 3. Process All 483 Pieces and Extract Real 56 RC-011 Features
        # ==============================================================================
        with open("data/manifests/rc012_source_inventory.csv", encoding="utf-8") as f:
            baseline_rows = [r for r in csv.DictReader(f) if r["eligible"] == "True" and r["composer"] in {
                "Alexander Scriabin", "Modest Mussorgsky", "Edvard Grieg", "Claude Debussy",
                "Ludwig van Beethoven", "Béla Bartók", "Antonín Dvořák"
            }]

        with open("data/manifests/rc014b_external_access_policy.json", encoding="utf-8") as f:
            policy = json.load(f)

        rubinstein_tpc = [e for e in policy["reference_manifest"] if e["composer"] == "Anton Rubinstein"]
        prokofiev_tpc = [e for e in policy["reference_manifest"] if e["composer"] == "Sergei Prokofiev" and e.get("us_copyright_status") == "PUBLIC_DOMAIN"]

        # --- A. Alexander Scriabin (207 pieces) ---
        scriabin_dest = repo_paths["craigsapp/scriabin"]
        for r in baseline_rows:
            if r["composer"] != "Alexander Scriabin":
                continue
            item_id = r["actual_source_item_id"]
            pid = f"craigsapp_scriabin:{item_id}"
            rel_p = r["actual_source_path_or_record_id"]
            full_p = os.path.join(scriabin_dest, rel_p)

            with open(full_p, "rb") as fp:
                file_bytes = fp.read()
            file_sha256 = hashlib.sha256(file_bytes).hexdigest()

            ls_out = subprocess.run(["git", "ls-tree", "HEAD", rel_p], cwd=scriabin_dest, check=True, capture_output=True, text=True).stdout.strip()
            blob_sha = ls_out.split()[2]

            cs = parse_humdrum_to_canonical(
                krn_path=full_p,
                score_entry_id=item_id,
                composer="Alexander Scriabin",
                title=r["actual_title"],
                corpus_id="craigsapp_scriabin",
                source_relative_path=rel_p,
                source_blob_sha256=file_sha256,
            )
            rep = extract_structural_representation(cs, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {pid}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            all_source_works.append({
                "piece_id": pid,
                "canonical_work_id": r["canonical_work_id"],
                "composer": "Alexander Scriabin",
                "class": "Russian",
                "work_title": r["actual_title"],
                "opus_or_catalogue": r["actual_opus_or_catalogue"],
                "movement": r["actual_movement"],
                "publication_year": None,
                "source_repository": r["source_repository_or_dataset"],
                "source_commit": r["source_version_or_commit"],
                "relative_path": rel_p,
                "git_blob_sha": blob_sha,
                "raw_format": "**kern",
                "parser": "music21",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "license_status": r["license_status"],
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": pid,
                "composer": "Alexander Scriabin",
                "work_title": r["actual_title"],
                "corpus": "craigsapp/scriabin",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # --- B. Modest Mussorgsky (18 pieces) ---
        for r in baseline_rows:
            if r["composer"] != "Modest Mussorgsky":
                continue
            item_id = r["actual_source_item_id"]
            pid = f"SyMuPe_PERiScoPe:{item_id}"
            rel_p = r["actual_source_path_or_record_id"]

            matching_tar_keys = [k for k in mussorgsky_mxl_bytes if item_id in k or k.endswith(item_id)]
            if not matching_tar_keys:
                raise ValueError(f"Could not find PERiScoPe tar entry for {item_id}")
            tar_key = matching_tar_keys[0]
            mxl_data = mussorgsky_mxl_bytes[tar_key]
            file_sha256 = hashlib.sha256(mxl_data).hexdigest()

            scratch_mxl = os.path.join(temp_dir, f"mussorgsky_{os.path.basename(item_id)}")
            with open(scratch_mxl, "wb") as mf:
                mf.write(mxl_data)

            score_m21 = m21.converter.parse(scratch_mxl)
            cs = parse_m21_mxl_to_canonical(
                score=score_m21,
                corpus_id="SyMuPe_PERiScoPe",
                score_entry_id=item_id,
                composer="Modest Mussorgsky",
                title=r["actual_title"],
                source_repo=r["source_repository_or_dataset"],
                source_commit=r["source_version_or_commit"],
                source_rel_path=rel_p,
                source_sha256=file_sha256,
                manifest_hash="rc014c2_freeze",
            )
            rep = extract_structural_representation(cs, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {pid}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            all_source_works.append({
                "piece_id": pid,
                "canonical_work_id": r["canonical_work_id"],
                "composer": "Modest Mussorgsky",
                "class": "Russian",
                "work_title": r["actual_title"],
                "opus_or_catalogue": r["actual_opus_or_catalogue"],
                "movement": r["actual_movement"],
                "publication_year": None,
                "source_repository": r["source_repository_or_dataset"],
                "source_commit": r["source_version_or_commit"],
                "relative_path": rel_p,
                "git_blob_sha": "PERiScoPe_v1.1_tar_entry",
                "raw_format": "MXL",
                "parser": "music21",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "license_status": r["license_status"],
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": pid,
                "composer": "Modest Mussorgsky",
                "work_title": r["actual_title"],
                "corpus": "SyMuPe/PERiScoPe",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # --- C. Control Composers (Grieg 66, Debussy 54, Beethoven 91, Bartók 14, Dvořák 12) ---
        for r in baseline_rows:
            comp = r["composer"]
            if comp in {"Alexander Scriabin", "Modest Mussorgsky"}:
                continue

            repo_key = r["source_repository_or_dataset"]
            repo_dir = repo_paths[repo_key]
            item_id = r["actual_source_item_id"]
            pid = f"{repo_key.replace('/', '_')}:{item_id}"

            score_file = resolve_score_file(Path(repo_dir), item_id)
            rel_in_repo = os.path.relpath(score_file, repo_dir).replace("\\", "/")

            with open(score_file, "rb") as fp:
                file_bytes = fp.read()
            file_sha256 = hashlib.sha256(file_bytes).hexdigest()

            ls_out = subprocess.run(["git", "ls-tree", "HEAD", rel_in_repo], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()
            blob_sha = ls_out.split()[2] if ls_out else "UNTRACKED_OR_SUBDIR"

            score = ingest_score_entry_from_ms3(
                corpus_id=repo_key.replace("DCMLab/", ""),
                corpus_role=CorpusRole.CONTROL_NON_RUSSIAN,
                score_entry_id=item_id,
                composer=comp,
                title=r["actual_title"],
                repo_dir=Path(repo_dir),
                source_repository=repo_key,
                source_commit=r["source_version_or_commit"],
                source_sha256=file_sha256,
                manifest_hash="rc014c2_freeze",
            )
            rep = extract_structural_representation(score, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {pid}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = score.compute_piece_hash()

            all_source_works.append({
                "piece_id": pid,
                "canonical_work_id": r["canonical_work_id"],
                "composer": comp,
                "class": "Control",
                "work_title": r["actual_title"],
                "opus_or_catalogue": r["actual_opus_or_catalogue"],
                "movement": r["actual_movement"],
                "publication_year": None,
                "source_repository": repo_key,
                "source_commit": r["source_version_or_commit"],
                "relative_path": rel_in_repo,
                "git_blob_sha": blob_sha,
                "raw_format": "MuseScore",
                "parser": "ms3",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(score.measures),
                "events_count": len(score.events),
                "license_status": r["license_status"],
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": pid,
                "composer": comp,
                "work_title": r["actual_title"],
                "corpus": repo_key,
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # --- D. Anton Rubinstein (11 pieces) ---
        tpc_dest = repo_paths["hectorbellmann-art/Tonal-Piano-Corpus"]
        for entry in rubinstein_tpc:
            score_id = os.path.splitext(os.path.basename(entry["relative_path"]))[0].replace(" ", "_").lower()
            piece_id = f"tonal_piano_corpus:{score_id}"
            blob_sha = entry["git_blob_sha"]
            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=tpc_dest, check=True, capture_output=True).stdout
            file_sha256 = hashlib.sha256(blob_bytes).hexdigest()

            scratch_p = os.path.join(temp_dir, f"{piece_id.replace(':', '_')}.xml")
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_xml_to_canonical(scratch_p, piece_id, entry["composer"], entry["work_title"])
            rep = extract_structural_representation(cs, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {piece_id}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()
            canon_id = score_id if score_id.startswith("rubinstein_") else f"rubinstein_{score_id}"

            all_source_works.append({
                "piece_id": piece_id,
                "canonical_work_id": canon_id,
                "composer": "Anton Rubinstein",
                "class": "Russian",
                "work_title": entry["work_title"],
                "opus_or_catalogue": entry["opus"],
                "movement": "1",
                "publication_year": entry["publication_year"],
                "source_repository": policy["corpus_repository"],
                "source_commit": policy["corpus_frozen_commit"],
                "relative_path": entry["relative_path"],
                "git_blob_sha": blob_sha,
                "raw_format": "MusicXML",
                "parser": "ElementTree/xml",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "license_status": "GOVERNANCE_PENDING",
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Anton Rubinstein",
                "work_title": entry["work_title"],
                "corpus": "Tonal-Piano-Corpus",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # --- E. Sergei Prokofiev (10 pieces: 8 TPC + 2 Humdrum supplements) ---
        for entry in prokofiev_tpc:
            score_id = os.path.splitext(os.path.basename(entry["relative_path"]))[0].replace(" ", "_").lower()
            piece_id = f"tonal_piano_corpus:{score_id}"
            blob_sha = entry["git_blob_sha"]
            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=tpc_dest, check=True, capture_output=True).stdout
            file_sha256 = hashlib.sha256(blob_bytes).hexdigest()

            scratch_p = os.path.join(temp_dir, f"{piece_id.replace(':', '_')}.xml")
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_xml_to_canonical(scratch_p, piece_id, entry["composer"], entry["work_title"])
            rep = extract_structural_representation(cs, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {piece_id}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()
            canon_id = score_id if score_id.startswith("prokofiev_") else f"prokofiev_{score_id}"

            all_source_works.append({
                "piece_id": piece_id,
                "canonical_work_id": canon_id,
                "composer": "Sergei Prokofiev",
                "class": "Russian",
                "work_title": entry["work_title"],
                "opus_or_catalogue": entry["opus"],
                "movement": "1",
                "publication_year": entry["publication_year"],
                "source_repository": policy["corpus_repository"],
                "source_commit": policy["corpus_frozen_commit"],
                "relative_path": entry["relative_path"],
                "git_blob_sha": blob_sha,
                "raw_format": "MusicXML",
                "parser": "ElementTree/xml",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "license_status": "GOVERNANCE_PENDING",
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": entry["work_title"],
                "corpus": "Tonal-Piano-Corpus",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

        # 2 Prokofiev Humdrum supplements
        supp_dest = repo_paths["automata/ana-music"]
        supp_entries = [
            {
                "piece_identifier": "prokofiev_op22_no02",
                "work_title": "Visions Fugitives Op. 22 No. 2 (Andante)",
                "opus": "Op. 22 No. 2",
                "publication_year": 1918,
                "relative_path": "corpus/classical/users/craig/classical/prokofiev/op22/visions22-2.krn",
                "git_blob_sha": "8ecec739bc4c7f561e2c7c141aff1cf40d9d3c0d",
            },
            {
                "piece_identifier": "prokofiev_op22_no03",
                "work_title": "Visions Fugitives Op. 22 No. 3 (Allegretto)",
                "opus": "Op. 22 No. 3",
                "publication_year": 1918,
                "relative_path": "corpus/classical/users/craig/classical/prokofiev/op22/visions22-3.krn",
                "git_blob_sha": "d7554373b3d67e4606f9f2f5f79b34608a000b12",
            },
        ]

        for s_entry in supp_entries:
            pid_supp = s_entry["piece_identifier"]
            piece_id = f"ana_music:{pid_supp}"
            blob_sha = s_entry["git_blob_sha"]
            blob_bytes = subprocess.run(["git", "cat-file", "blob", blob_sha], cwd=supp_dest, check=True, capture_output=True).stdout
            file_sha256 = hashlib.sha256(blob_bytes).hexdigest()

            scratch_p = os.path.join(temp_dir, f"{piece_id.replace(':', '_')}.krn")
            with open(scratch_p, "wb") as sf:
                sf.write(blob_bytes)

            cs = parse_humdrum_to_canonical(
                krn_path=scratch_p,
                score_entry_id=pid_supp,
                composer="Sergei Prokofiev",
                title=s_entry["work_title"],
                corpus_id="ana_music",
                source_relative_path=s_entry["relative_path"],
                source_blob_sha256=file_sha256,
            )
            rep = extract_structural_representation(cs, manifest_hash="rc014c2_freeze")
            f_dict = {k: f.value for k, f in sorted(rep.features.items())}
            if len(f_dict) != 56 or all(v == 0.0 for v in f_dict.values()):
                raise ValueError(f"Invalid all-zero feature extraction for {piece_id}")

            b_hash = hashlib.sha256(json.dumps(f_dict, sort_keys=True).encode("utf-8")).hexdigest()
            score_hash = cs.compute_piece_hash()

            all_source_works.append({
                "piece_id": piece_id,
                "canonical_work_id": pid_supp,
                "composer": "Sergei Prokofiev",
                "class": "Russian",
                "work_title": s_entry["work_title"],
                "opus_or_catalogue": s_entry["opus"],
                "movement": "1",
                "publication_year": s_entry["publication_year"],
                "source_repository": "automata/ana-music",
                "source_commit": "335cbdc617c919d29e9384c4e490cabca5736f73",
                "relative_path": s_entry["relative_path"],
                "git_blob_sha": blob_sha,
                "raw_format": "**kern",
                "parser": "music21",
                "source_file_hash_if_available": file_sha256,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "measures_count": len(cs.measures),
                "events_count": len(cs.events),
                "license_status": "GOVERNANCE_PENDING",
                "eligible": True,
            })
            all_feature_cache_entries.append({
                "piece_id": piece_id,
                "composer": "Sergei Prokofiev",
                "work_title": s_entry["work_title"],
                "corpus": "automata/ana-music",
                "schema_hash": schema_hash,
                "canonical_score_hash": score_hash,
                "derived_feature_bundle_hash": b_hash,
                "features_56": f_dict,
            })

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # Sort all 483 pieces deterministically
    all_source_works.sort(key=lambda x: (x["composer"], x["canonical_work_id"], x["piece_id"]))
    all_feature_cache_entries.sort(key=lambda x: (x["composer"], x["piece_id"]))

    if len(all_source_works) != 483:
        raise ValueError(f"Expected 483 source works, got {len(all_source_works)}")
    if len(all_feature_cache_entries) != 483:
        raise ValueError(f"Expected 483 feature cache entries, got {len(all_feature_cache_entries)}")

    # Verify zero missing hashes in source freeze
    missing_hashes = [w["piece_id"] for w in all_source_works if not w.get("source_file_hash_if_available") or not w.get("canonical_score_hash") or not w.get("derived_feature_bundle_hash")]
    if missing_hashes:
        raise ValueError(f"Found {len(missing_hashes)} works with missing cryptographic hashes: {missing_hashes[:5]}")

    # ==============================================================================
    # 4. Save Complete Source Freeze Manifest
    # ==============================================================================
    complete_source_freeze = {
        "milestone": "RC-014C.2",
        "status": "TRUE_FULL_CONFIRMATORY_SOURCE_FREEZE_FROZEN",
        "total_source_works": len(all_source_works),
        "russian_source_works_count": sum(1 for w in all_source_works if w["class"] == "Russian"),
        "control_source_works_count": sum(1 for w in all_source_works if w["class"] == "Control"),
        "source_works": all_source_works,
    }

    with open("data/manifests/rc014c2_complete_source_freeze.json", "w", encoding="utf-8") as f:
        json.dump(complete_source_freeze, f, indent=2)

    # ==============================================================================
    # 5. Save Complete Role-Blind Real Feature Cache Manifest
    # ==============================================================================
    cache_dump = json.dumps(all_feature_cache_entries, sort_keys=True).encode("utf-8")
    feature_cache_matrix_hash = hashlib.sha256(cache_dump).hexdigest()

    complete_feature_cache = {
        "milestone": "RC-014C.2",
        "status": "TRUE_FULL_CONFIRMATORY_ROLE_BLIND_FEATURE_CACHE_FROZEN",
        "schema_hash": schema_hash,
        "feature_catalog_descriptor_count": 56,
        "total_cached_pieces": len(all_feature_cache_entries),
        "russian_pieces_count": sum(1 for e in all_feature_cache_entries if e["composer"] in {"Alexander Scriabin", "Modest Mussorgsky", "Anton Rubinstein", "Sergei Prokofiev"}),
        "control_pieces_count": sum(1 for e in all_feature_cache_entries if e["composer"] in {"Edvard Grieg", "Claude Debussy", "Ludwig van Beethoven", "Béla Bartók", "Antonín Dvořák"}),
        "composer_counts": {
            "Alexander Scriabin": sum(1 for e in all_feature_cache_entries if e["composer"] == "Alexander Scriabin"),
            "Modest Mussorgsky": sum(1 for e in all_feature_cache_entries if e["composer"] == "Modest Mussorgsky"),
            "Anton Rubinstein": sum(1 for e in all_feature_cache_entries if e["composer"] == "Anton Rubinstein"),
            "Sergei Prokofiev": sum(1 for e in all_feature_cache_entries if e["composer"] == "Sergei Prokofiev"),
            "Edvard Grieg": sum(1 for e in all_feature_cache_entries if e["composer"] == "Edvard Grieg"),
            "Claude Debussy": sum(1 for e in all_feature_cache_entries if e["composer"] == "Claude Debussy"),
            "Ludwig van Beethoven": sum(1 for e in all_feature_cache_entries if e["composer"] == "Ludwig van Beethoven"),
            "Béla Bartók": sum(1 for e in all_feature_cache_entries if e["composer"] == "Béla Bartók"),
            "Antonín Dvořák": sum(1 for e in all_feature_cache_entries if e["composer"] == "Antonín Dvořák"),
        },
        "feature_cache_matrix_sha256": feature_cache_matrix_hash,
        "cached_pieces": all_feature_cache_entries,
    }

    with open("data/manifests/rc014c2_complete_role_blind_feature_cache.json", "w", encoding="utf-8") as f:
        json.dump(complete_feature_cache, f, indent=2)

    # ==============================================================================
    # 6. Master Pre-Unblinding Confirmatory Corpus Freeze Hash & Audit Record
    # ==============================================================================
    freeze_manifest_payload = {
        "membership_manifest": membership_manifest,
        "source_freeze_manifest": complete_source_freeze,
        "feature_cache_matrix_sha256": feature_cache_matrix_hash,
        "schema_hash": schema_hash,
    }
    master_freeze_hash = hashlib.sha256(json.dumps(freeze_manifest_payload, sort_keys=True).encode("utf-8")).hexdigest()

    audit_data = {
        "milestone": "RC-014C.2",
        "status": "RC014C2_TRUE_FULL_CORPUS_FROZEN_AWAITING_HUMAN_ACCESS_APPROVAL",
        "rc014c2_confirmatory_corpus_freeze_hash": master_freeze_hash,
        "superseded_freeze_hash_rc014c1": SUPERSEDED_INVALID_PLACEHOLDER_FREEZE_HASH_RC014C1,
        "superseded_feature_cache_sha256_rc014c1": SUPERSEDED_INVALID_PLACEHOLDER_FEATURE_CACHE_SHA256_RC014C1,
        "superseded_freeze_hash_rc014c": SUPERSEDED_INCOMPLETE_FREEZE_HASH_RC014C,
        "superseded_freeze_explanation": "SUPERSEDED_INVALID_PLACEHOLDER_FEATURE_FREEZE (RC-014C.1 contained 462 zero-valued placeholder rows; RC-014C contained only 21 pieces for Rubinstein + Prokofiev)",
        "feature_cache_matrix_sha256": feature_cache_matrix_hash,
        "schema_hash": schema_hash,
        "total_confirmatory_pieces": len(all_source_works),
        "total_composers_count": 9,
        "russian_composers_count": 4,
        "control_composers_count": 5,
        "russian_pieces_count": 246,
        "control_pieces_count": 237,
        "live_n_russian": 2,
        "rc012_resumption_gate": "BLOCKED",
        "gate_reason": "Live N_Russian = 2 < 4 until human governance approval is logged; predictor execution strictly prohibited",
        "invalidation_policy": {
            "trigger": "ANY_CHANGE_TO_EXTERNAL_BYTES_OR_PARSERS_OR_FEATURES",
            "effect": "INVALIDATES_CONFIRMATORY_CORPUS_FREEZE_AND_DOWNSTREAM_STATISTICS",
        },
    }

    os.makedirs("data/reviews/rc014", exist_ok=True)
    with open("data/reviews/rc014/rc014c2_preunblinding_integrity_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)

    return {
        "master_freeze_hash": master_freeze_hash,
        "feature_cache_matrix_sha256": feature_cache_matrix_hash,
        "total_pieces": len(all_source_works),
        "russian_pieces": 246,
        "control_pieces": 237,
    }


if __name__ == "__main__":
    print("Generating RC-014C.2 Complete Confirmatory Corpus Freeze Manifests with REAL Features...")
    res = generate_rc014c2_manifests()
    print("Completed RC-014C.2 Manifest Generation:")
    print(f"  Master Freeze Hash: {res['master_freeze_hash']}")
    print(f"  Feature Cache Hash: {res['feature_cache_matrix_sha256']}")
    print(f"  Total Confirmatory Works: {res['total_pieces']}")
    print(f"  Russian Works: {res['russian_pieces']}")
    print(f"  Control Works: {res['control_pieces']}")
