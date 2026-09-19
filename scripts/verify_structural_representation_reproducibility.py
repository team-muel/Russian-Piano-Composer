"""
True Two-Process Structural Representation Reproducibility Verification for RC-011.

Launches two independent Python subprocesses to execute full structural extraction,
synthetic fixture validation, and matrix generation, requiring byte-for-byte payload equality.
"""

import hashlib
import json
import subprocess
import sys

WORKER_SCRIPT = """
import json
import sys
from pathlib import Path
from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest
from russian_piano_composer.structure_analysis.extractor import StructuralExtractionPolicy, extract_structural_representation
from russian_piano_composer.structure_analysis.matrix import build_structural_representation_matrix
from russian_piano_composer.structure_analysis.validation import run_synthetic_validation_suite
from russian_piano_composer.structure_analysis.lineage import compute_structural_representation_lineage

manifest_path = Path("data/manifests/corpus_manifest.yaml")
manifest = load_manifest(manifest_path)
manifest_hash = manifest.compute_manifest_hash()
interim_base = Path("data/interim/canonical") / manifest_hash

val_result = run_synthetic_validation_suite()

scores_by_id = {}
for source in manifest.sources:
    corpus_dir = interim_base / source.corpus_id
    for entry_id in source.score_entry_ids:
        piece_id = f"{source.corpus_id}:{entry_id}"
        scores_by_id[piece_id] = load_canonical_score_from_parquet(corpus_dir, piece_id)

policy = StructuralExtractionPolicy()
piece_representations = {}
for pid, score in sorted(scores_by_id.items()):
    rep = extract_structural_representation(score, manifest_hash=manifest_hash, policy=policy)
    piece_representations[pid] = rep.features

matrix = build_structural_representation_matrix(piece_representations, manifest_hash=manifest_hash)
lineage = compute_structural_representation_lineage(manifest_hash, matrix, val_result, policy)

payload = {
    "manifest_hash": manifest_hash,
    "structural_schema_hash": lineage.structural_schema_hash,
    "structural_matrix_hash": lineage.structural_matrix_hash,
    "validation_result_hash": lineage.validation_result_hash,
    "lineage_bundle_hash": lineage.compute_bundle_hash(),
    "matrix_data": [list(row) for row in matrix.data],
    "matrix_availability": [[st.value for st in r] for r in matrix.availability_matrix],
    "assertions_passed": val_result.passed_assertions,
    "overall_status": val_result.overall_status,
}

print("JSON_START")
print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
print("JSON_END")
"""


def _run_worker(name: str) -> dict:
    print(f"Launching Worker Process {name}...")
    proc = subprocess.run(
        [sys.executable, "-c", WORKER_SCRIPT],
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = proc.stdout
    if "JSON_START" not in stdout or "JSON_END" not in stdout:
        raise RuntimeError(f"Worker {name} output missing JSON delimiters:\n{stdout}\nSTDERR:\n{proc.stderr}")
    json_text = stdout.split("JSON_START")[1].split("JSON_END")[0].strip()
    return json.loads(json_text)


def main() -> None:
    print("--- Running True Two-Process Structural Representation Reproducibility Audit ---")

    payload_a = _run_worker("A")
    payload_b = _run_worker("B")

    # 1. Direct Structural Comparison
    is_structurally_equal = (payload_a == payload_b)
    print(f"  Process A Complete Payload == Process B Complete Payload: {str(is_structurally_equal).upper()}")
    if not is_structurally_equal:
        raise RuntimeError("True two-process payload inequality detected!")

    # 2. SHA-256 Payload Hash Comparison
    hash_a = hashlib.sha256(json.dumps(payload_a, sort_keys=True).encode("utf-8")).hexdigest()
    hash_b = hashlib.sha256(json.dumps(payload_b, sort_keys=True).encode("utf-8")).hexdigest()

    print("\n--- Payload Hash Comparison ---")
    print(f"  Process A Payload Hash: {hash_a}")
    print(f"  Process B Payload Hash: {hash_b}")

    if hash_a != hash_b:
        raise RuntimeError(f"Payload hash mismatch! A: {hash_a} != B: {hash_b}")

    print("\n--- TRUE TWO-PROCESS STRUCTURAL REPRODUCIBILITY AUDIT: PASS ---")
    print(f"  Structural Schema Hash: {payload_a['structural_schema_hash']}")
    print(f"  Structural Matrix Hash: {payload_a['structural_matrix_hash']}")
    print(f"  Validation Result Hash: {payload_a['validation_result_hash']}")
    print(f"  Lineage Bundle Hash:    {payload_a['lineage_bundle_hash']}")
    print(f"  Overall Status:         {payload_a['overall_status']}")


if __name__ == "__main__":
    main()
