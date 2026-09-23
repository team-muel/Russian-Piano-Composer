"""RC-013 Russian Composer Qualification and Eligibility Authority.

Provides single, immutable, authoritative machine-readable derivation of:
- Russian Composer Pool qualification status
- Control Composer Pool qualification status
- Derived N_Russian count
- Pre-review vs Post-review scientific state

Enforces fail-closed rules:
- N_Russian = 2 corresponds to Alexander Scriabin + Modest Mussorgsky (RC-012 confirmatory baseline).
- Anton Arensky, Sergei Lyapunov, Anatoly Lyadov are UNQUALIFIED until valid independent human source-fidelity receipts exist.
- Composer qualification for pilot composers requires exactly 3/3 verified frozen pilot target scores.
- N_Russian cannot be stated as 2 with wrong composer membership (e.g. Lyadov + Lyapunov).
- RC-012 Resumption remains BLOCKED while N_Russian < 4 or other data contract gates fail.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from russian_piano_composer.corpus.rc013_review_ingestion import (
    validate_human_review_receipt,
)


@dataclass(frozen=True)
class ComposerQualificationRecord:
    composer: str
    composer_class: str  # "Russian" | "Control"
    qualified_score_count: int
    source_fidelity_authority: str
    qualification_status: str  # "QUALIFIED" | "UNQUALIFIED"
    qualification_reason: str
    evidence_artifact: str
    evidence_sha: str


@dataclass(frozen=True)
class RussianPoolDerivationResult:
    n_russian: int
    n_control: int
    qualified_russian_composers: list[str]
    unqualified_russian_composers: list[str]
    qualified_control_composers: list[str]
    rc012_resumption_status: str  # "BLOCKED" | "UNBLOCKED"
    rc012_resumption_reason: str
    composer_records: dict[str, ComposerQualificationRecord] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_russian": self.n_russian,
            "n_control": self.n_control,
            "qualified_russian_composers": self.qualified_russian_composers,
            "unqualified_russian_composers": self.unqualified_russian_composers,
            "qualified_control_composers": self.qualified_control_composers,
            "rc012_resumption_status": self.rc012_resumption_status,
            "rc012_resumption_reason": self.rc012_resumption_reason,
            "composer_records": {
                k: {
                    "composer": v.composer,
                    "composer_class": v.composer_class,
                    "qualified_score_count": v.qualified_score_count,
                    "source_fidelity_authority": v.source_fidelity_authority,
                    "qualification_status": v.qualification_status,
                    "qualification_reason": v.qualification_reason,
                    "evidence_artifact": v.evidence_artifact,
                    "evidence_sha": v.evidence_sha,
                }
                for k, v in self.composer_records.items()
            },
        }


# Authoritative baseline evidence hashes
RC012_INVENTORY_SHA: str = "4813102a193c38fc61ef4815a25895243c819b2527803f82e7020ac766627eb7"
RC012_GATE_RESULT_SHA: str = "85398969b0abbc2873544cc4b4dbdffbe1d4db6d665fa99aa4de237e4222d4ab"

FROZEN_PILOT_TARGET_SCORES: dict[str, list[str]] = {
    "Anton Arensky": [
        "anton_arensky_op36_no01",
        "anton_arensky_op36_no02",
        "anton_arensky_op36_no13",
    ],
    "Anatoly Lyadov": [
        "anatoly_lyadov_op40_no02",
        "anatoly_lyadov_op40_no03",
        "anatoly_lyadov_op46_no04",
    ],
    "Sergei Lyapunov": [
        "sergei_lyapunov_op11_no01",
        "sergei_lyapunov_op11_no02",
        "sergei_lyapunov_op11_no03",
    ],
}


def derive_russian_composer_pool_from_evidence(
    receipts_dir: str = "data/reviews/rc013/accepted",
    scores_dir: str = "data/scores/rc013/canonical",
    scans_dir: str = "data/scans/rc013",
    packets_dir: str = "data/reviews/rc013/packets",
    source_manifest_csv: str = "data/manifests/rc013_source_candidates.csv",
) -> RussianPoolDerivationResult:
    """Derives Russian Composer Pool qualification exclusively from live validated human review receipts.

    Production path: discovers verified scores by checking valid receipts for each frozen target score.
    """
    from russian_piano_composer.corpus.rc013_fidelity import (
        compute_sha256_file,
        load_canonical_source_manifest,
    )

    source_sha_map = (
        load_canonical_source_manifest(source_manifest_csv)
        if os.path.exists(source_manifest_csv)
        else {}
    )

    verified_counts: dict[str, int] = {
        "Anton Arensky": 0,
        "Anatoly Lyadov": 0,
        "Sergei Lyapunov": 0,
    }

    for comp, target_scores in FROZEN_PILOT_TARGET_SCORES.items():
        comp_verified = 0
        for sid in target_scores:
            receipt_path = os.path.join(receipts_dir, f"{sid}.human_review_receipt.json")
            xml_path = os.path.join(scores_dir, f"{sid}.musicxml")

            if not os.path.exists(receipt_path) or not os.path.exists(xml_path):
                continue

            live_sym_sha = compute_sha256_file(xml_path)
            canonical_src_sha = source_sha_map.get(sid, "")

            res = validate_human_review_receipt(
                receipt_path=receipt_path,
                live_symbolic_sha=live_sym_sha,
                actual_source_sha=canonical_src_sha,
                packets_dir=packets_dir,
            )
            if res.valid:
                comp_verified += 1
        verified_counts[comp] = comp_verified

    return derive_russian_composer_pool(
        arensky_verified_count=verified_counts["Anton Arensky"],
        lyapunov_verified_count=verified_counts["Sergei Lyapunov"],
        lyadov_verified_count=verified_counts["Anatoly Lyadov"],
    )


def derive_russian_composer_pool(
    arensky_verified_count: int = 0,
    lyapunov_verified_count: int = 0,
    lyadov_verified_count: int = 0,
) -> RussianPoolDerivationResult:
    """Derives Russian Composer Pool qualification and N_Russian strictly from verified score evidence.

    Threshold requirement for RC-012/RC-013 qualification:
    - Scriabin: 207 verified scores (>= 10) -> QUALIFIED
    - Mussorgsky: 18 verified scores (>= 10) -> QUALIFIED
    - Arensky: requires exactly 3 verified pilot movements (3/3) -> QUALIFIED if verified, else UNQUALIFIED
    - Lyapunov: requires exactly 3 verified pilot movements (3/3) -> QUALIFIED if verified, else UNQUALIFIED
    - Lyadov: requires exactly 3 verified pilot movements (3/3) -> QUALIFIED if verified, else UNQUALIFIED
    """
    records: dict[str, ComposerQualificationRecord] = {}

    # 1. Alexander Scriabin (Baseline Qualified)
    records["Alexander Scriabin"] = ComposerQualificationRecord(
        composer="Alexander Scriabin",
        composer_class="Russian",
        qualified_score_count=207,
        source_fidelity_authority="RC-011 / RC-012 Canonical Confirmatory Corpus",
        qualification_status="QUALIFIED",
        qualification_reason="207 deduplicated canonical works meeting full data contract",
        evidence_artifact="data/manifests/rc012_source_inventory.csv",
        evidence_sha=RC012_INVENTORY_SHA,
    )

    # 2. Modest Mussorgsky (Baseline Qualified)
    records["Modest Mussorgsky"] = ComposerQualificationRecord(
        composer="Modest Mussorgsky",
        composer_class="Russian",
        qualified_score_count=18,
        source_fidelity_authority="RC-011 / RC-012 Canonical Confirmatory Corpus",
        qualification_status="QUALIFIED",
        qualification_reason="18 deduplicated canonical works meeting full data contract",
        evidence_artifact="data/manifests/rc012_source_inventory.csv",
        evidence_sha=RC012_INVENTORY_SHA,
    )

    # 3. Anton Arensky (RC-013 Pilot)
    arensky_status = "QUALIFIED" if arensky_verified_count >= 3 else "UNQUALIFIED"
    arensky_reason = (
        f"{arensky_verified_count}/3 source-fidelity verified movements (3/3 required for pilot qualification)"
        if arensky_verified_count >= 3
        else f"{arensky_verified_count}/3 source-fidelity verified movements (requires independent human review)"
    )
    records["Anton Arensky"] = ComposerQualificationRecord(
        composer="Anton Arensky",
        composer_class="Russian",
        qualified_score_count=arensky_verified_count,
        source_fidelity_authority="RC-013 Canonical Pilot Manifest",
        qualification_status=arensky_status,
        qualification_reason=arensky_reason,
        evidence_artifact="data/manifests/rc013_digitization_manifest.yaml",
        evidence_sha="",
    )

    # 4. Sergei Lyapunov (RC-013 Pilot)
    lyapunov_status = "QUALIFIED" if lyapunov_verified_count >= 3 else "UNQUALIFIED"
    lyapunov_reason = (
        f"{lyapunov_verified_count}/3 source-fidelity verified movements (3/3 required for pilot qualification)"
        if lyapunov_verified_count >= 3
        else f"{lyapunov_verified_count}/3 source-fidelity verified movements (requires independent human review)"
    )
    records["Sergei Lyapunov"] = ComposerQualificationRecord(
        composer="Sergei Lyapunov",
        composer_class="Russian",
        qualified_score_count=lyapunov_verified_count,
        source_fidelity_authority="RC-013 Canonical Pilot Manifest",
        qualification_status=lyapunov_status,
        qualification_reason=lyapunov_reason,
        evidence_artifact="data/manifests/rc013_digitization_manifest.yaml",
        evidence_sha="",
    )

    # 5. Anatoly Lyadov (RC-013 Pilot)
    lyadov_status = "QUALIFIED" if lyadov_verified_count >= 3 else "UNQUALIFIED"
    lyadov_reason = (
        f"{lyadov_verified_count}/3 source-fidelity verified movements (3/3 required for pilot qualification)"
        if lyadov_verified_count >= 3
        else f"{lyadov_verified_count}/3 source-fidelity verified movements (requires independent human review)"
    )
    records["Anatoly Lyadov"] = ComposerQualificationRecord(
        composer="Anatoly Lyadov",
        composer_class="Russian",
        qualified_score_count=lyadov_verified_count,
        source_fidelity_authority="RC-013 Canonical Pilot Manifest",
        qualification_status=lyadov_status,
        qualification_reason=lyadov_reason,
        evidence_artifact="data/manifests/rc013_digitization_manifest.yaml",
        evidence_sha="",
    )

    # Control Composers (from RC-012 baseline)
    for ctrl_comp in [
        "Antonín Dvořák",
        "Béla Bartók",
        "Claude Debussy",
        "Edvard Grieg",
        "Ludwig van Beethoven",
    ]:
        records[ctrl_comp] = ComposerQualificationRecord(
            composer=ctrl_comp,
            composer_class="Control",
            qualified_score_count=10,
            source_fidelity_authority="RC-012 Confirmatory Baseline",
            qualification_status="QUALIFIED",
            qualification_reason="M_c >= 10 canonical works meeting data contract",
            evidence_artifact="data/manifests/rc012_source_inventory.csv",
            evidence_sha=RC012_INVENTORY_SHA,
        )

    qualified_russian = sorted([
        r.composer for r in records.values()
        if r.composer_class == "Russian" and r.qualification_status == "QUALIFIED"
    ])
    unqualified_russian = sorted([
        r.composer for r in records.values()
        if r.composer_class == "Russian" and r.qualification_status == "UNQUALIFIED"
    ])
    qualified_control = sorted([
        r.composer for r in records.values()
        if r.composer_class == "Control" and r.qualification_status == "QUALIFIED"
    ])

    n_russian = len(qualified_russian)
    n_control = len(qualified_control)

    rc012_unblocked = (n_russian >= 4) and (n_control >= 4)
    resumption_status = "UNBLOCKED" if rc012_unblocked else "BLOCKED"
    resumption_reason = (
        "CONFIRMATORY_DATA_CONTRACT_SATISFIED"
        if rc012_unblocked
        else f"N_Russian = {n_russian} < 4 (requires at least 4 qualified Russian composers)"
    )

    return RussianPoolDerivationResult(
        n_russian=n_russian,
        n_control=n_control,
        qualified_russian_composers=qualified_russian,
        unqualified_russian_composers=unqualified_russian,
        qualified_control_composers=qualified_control,
        rc012_resumption_status=resumption_status,
        rc012_resumption_reason=resumption_reason,
        composer_records=records,
    )
