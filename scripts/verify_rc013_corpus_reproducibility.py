"""Two-process independent reproducibility verifier for RC-013 milestone."""

from __future__ import annotations

import subprocess
import sys

from scripts.compute_rc013_hashes import get_all_rc013_hashes


def run_process_hashes() -> dict[str, str]:
    res = subprocess.run(
        [sys.executable, "-m", "scripts.compute_rc013_hashes"],
        capture_output=True,
        text=True,
        check=True,
    )
    hashes: dict[str, str] = {}
    for line in res.stdout.splitlines():
        if ":" in line and line.strip().startswith("RC013_"):
            parts = line.split(":", 1)
            hashes[parts[0].strip()] = parts[1].strip()
    return hashes


def main() -> int:
    print("Executing Two-Process Reproducibility Verification for RC-013...")

    # Process A (Direct in-process evaluation)
    print("\n[Process A] In-process calculation...")
    hashes_a = get_all_rc013_hashes()
    for k, v in hashes_a.items():
        print(f"  {k}: {v}")

    # Process B (Subprocess isolated execution)
    print("\n[Process B] Fresh isolated subprocess calculation...")
    hashes_b = run_process_hashes()
    for k, v in hashes_b.items():
        print(f"  {k}: {v}")

    print("\nComparing Process A and Process B...")
    mismatches = []
    for k in sorted(hashes_a.keys()):
        val_a = hashes_a.get(k)
        val_b = hashes_b.get(k)
        if val_a != val_b:
            mismatches.append((k, val_a, val_b))

    if mismatches:
        print("FAIL: Mismatches detected between Process A and Process B!")
        for k, va, vb in mismatches:
            print(f"  {k}: Process A = {va}, Process B = {vb}")
        return 1

    print("PASS: Process A == Process B (100% Cryptographic Reproducibility across all 7 hashes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
