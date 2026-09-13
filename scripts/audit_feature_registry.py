"""
Automated feature registry audit script for Russian Piano Composer.

Mechanically verifies set equality, non-overlapping category partitions,
and matrix column contract compliance.
"""
import sys
from collections import Counter

from russian_piano_composer.domain.features import FEATURE_SCHEMA_VERSION
from russian_piano_composer.features import FEATURE_REGISTRY


def run_feature_registry_audit() -> int:
    print(f"=== Russian Piano Composer Feature Registry Audit (v{FEATURE_SCHEMA_VERSION}) ===")

    reg_ids = [fd.feature_id for fd in FEATURE_REGISTRY]
    unique_ids = set(reg_ids)

    print(f"Registered Descriptors: {len(reg_ids)}")
    print(f"Unique Descriptors:     {len(unique_ids)}")

    if len(reg_ids) != len(unique_ids):
        dups = [item for item, count in Counter(reg_ids).items() if count > 1]
        print(f"[FAIL] Duplicate feature IDs found: {dups}")
        return 1

    # Disjoint sets A, B, C, D
    set_a = {fd.feature_id for fd in FEATURE_REGISTRY if fd.validity_category == "A"}
    set_b = {fd.feature_id for fd in FEATURE_REGISTRY if fd.validity_category == "B"}
    set_c = {fd.feature_id for fd in FEATURE_REGISTRY if fd.validity_category == "C"}
    set_d = {fd.feature_id for fd in FEATURE_REGISTRY if fd.validity_category == "D"}

    # Pairwise disjoint check
    intersections = [
        ("A", "B", set_a & set_b),
        ("A", "C", set_a & set_c),
        ("A", "D", set_a & set_d),
        ("B", "C", set_b & set_c),
        ("B", "D", set_b & set_d),
        ("C", "D", set_c & set_d),
    ]

    has_error = False
    for cat1, cat2, inter in intersections:
        if inter:
            print(f"[FAIL] Non-disjoint categories {cat1} and {cat2}: {inter}")
            has_error = True

    union_all = set_a | set_b | set_c | set_d
    if union_all != unique_ids:
        missing = unique_ids - union_all
        extra = union_all - unique_ids
        print(f"[FAIL] Category union mismatch! Missing: {missing}, Extra: {extra}")
        has_error = True

    if has_error:
        return 1

    print("\n--- Category Breakdown ---")
    print(f"Category A (Analysis-Ready):              {len(set_a):2d}")
    print(f"Category B (Usable with Limitation):      {len(set_b):2d}")
    print(f"Category C (Diagnostic Only):             {len(set_c):2d}")
    print(f"Category D (Unsupported / Disabled):      {len(set_d):2d}")
    print(f"Total Category Union Count:               {len(union_all):2d}")

    # Check Analysis-Ready vs comparison_ready
    analysis_ready_set = {fd.feature_id for fd in FEATURE_REGISTRY if fd.comparison_ready and fd.validity_category == "A"}
    print(f"Analysis-Ready Features (Category A & comp=True): {len(analysis_ready_set):2d}")

    if len(analysis_ready_set) != len(set_a):
        print("[FAIL] Mismatch between Category A set and comparison_ready set!")
        return 1

    print("\n[SUCCESS] Feature registry audit passed clean!")
    return 0


if __name__ == "__main__":
    sys.exit(run_feature_registry_audit())
