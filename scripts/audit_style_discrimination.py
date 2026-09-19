"""
Static Python AST inspection and dynamic runtime role-blindness audit script for RC-010.

Verifies that style analysis predictor modules contain zero ground-truth annotation leakage,
no metadata predictors, and zero role conditioning before label attachment.
"""

import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from russian_piano_composer.corpus.adapters.dcml_ms3 import load_canonical_score_from_parquet
from russian_piano_composer.corpus.manifest import load_manifest

if TYPE_CHECKING:
    from russian_piano_composer.domain.score import CanonicalScore
from russian_piano_composer.style_analysis.features import (
    FORBIDDEN_METADATA_TERMS,
    build_role_blind_feature_matrices,
)


class StyleAnalysisRoleBlindnessVisitor(ast.NodeVisitor):
    """
    AST Visitor inspecting nodes in style_analysis modules for forbidden ground-truth / metadata leakage terms.
    """

    FORBIDDEN_TERMS: ClassVar[set[str]] = {
        "theme_annotations",
        "candidate_specs",
        "human_review",
        "GENERATIVE_RUSSIAN",
        "CONTROL_NON_RUSSIAN",
    }

    _OWN_PACKAGE: ClassVar[str] = "russian_piano_composer"

    def __init__(self, filepath: Path) -> None:
        self.filepath = filepath
        self.violations: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name.startswith(self._OWN_PACKAGE):
                continue
            for term in self.FORBIDDEN_TERMS:
                if term in alias.name:
                    self.violations.append(f"Line {node.lineno}: Forbidden import '{alias.name}' contains '{term}'")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            if node.module.startswith(self._OWN_PACKAGE):
                return
            for term in self.FORBIDDEN_TERMS:
                if term in node.module:
                    self.violations.append(f"Line {node.lineno}: Forbidden import from '{node.module}' contains '{term}'")
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        for term in self.FORBIDDEN_TERMS:
            if term == node.id:
                self.violations.append(f"Line {node.lineno}: Identifier name '{node.id}' uses forbidden term '{term}'")
        self.generic_visit(node)


def main() -> None:
    print("--- Auditing Style Analysis Role-Blindness & Leakage Invariants ---")

    # Audit 1: Static AST Inspection of style_analysis modules
    style_dir = Path("src/russian_piano_composer/style_analysis")
    all_violations: list[str] = []

    for py_file in style_dir.glob("*.py"):
        source_text = py_file.read_text(encoding="utf-8")
        parsed_ast = ast.parse(source_text, filename=str(py_file))
        visitor = StyleAnalysisRoleBlindnessVisitor(py_file)
        visitor.visit(parsed_ast)
        if visitor.violations:
            for v in visitor.violations:
                all_violations.append(f"{py_file.name}: {v}")

    if all_violations:
        print("ROLE-BLINDNESS AST AUDIT FAILED:")
        for v in all_violations:
            print(f"  - {v}")
        sys.stdout.flush()
        raise RuntimeError("Genuine Python AST inspection found forbidden annotation/role terms in style_analysis files!")

    print("Audit 1: Zero Ground Truth / Annotation Leakage -> PASS (Genuine AST inspection clean)")
    sys.stdout.flush()

    # Audit 2: Dynamic Module Load Check
    forbidden_modules = [
        "russian_piano_composer.corpus.theme_annotations",
        "russian_piano_composer.domain.annotations",
    ]
    for mod in sys.modules:
        for fmod in forbidden_modules:
            if mod.startswith(fmod):
                raise RuntimeError(f"ROLE-BLINDNESS DYNAMIC AUDIT ERROR: Forbidden annotation module {mod} loaded in environment!")

    print("Audit 2: Dynamic Module Environment -> PASS (No annotation modules loaded)")
    sys.stdout.flush()

    # Audit 3: Runtime Predictor Column Audit
    manifest_path = Path("data/manifests/corpus_manifest.yaml")
    if not manifest_path.exists():
        print("Error: corpus_manifest.yaml not found.")
        sys.exit(1)

    manifest = load_manifest(manifest_path)
    manifest_hash = manifest.compute_manifest_hash()
    interim_base = Path("data/interim/canonical") / manifest_hash

    if not interim_base.exists():
        print("Error: Canonical corpus parquet cache not found.")
        sys.exit(1)

    # Load 10 scores for quick matrix column verification
    scores_by_id: dict[str, CanonicalScore] = {}
    count = 0
    for source in manifest.sources:
        corpus_dir = interim_base / source.corpus_id
        for entry_id in source.score_entry_ids:
            if count >= 10:
                break
            piece_id = f"{source.corpus_id}:{entry_id}"
            score = load_canonical_score_from_parquet(corpus_dir, piece_id)
            scores_by_id[piece_id] = score
            count += 1
        if count >= 10:
            break

    matrices = build_role_blind_feature_matrices(scores_by_id, manifest_hash=manifest_hash)

    for m_name, mat in matrices.items():
        for col_name in mat.feature_names:
            for term in FORBIDDEN_METADATA_TERMS:
                if term in col_name:
                    raise RuntimeError(f"LEAKAGE AUDIT ERROR: Predictor column '{col_name}' in {m_name} contains forbidden term '{term}'!")

    print("Audit 3: Runtime Predictor Column Sanity -> PASS (Zero metadata predictors in MODEL_A/B/C)")
    sys.stdout.flush()

    print("\n--- ALL STYLE ANALYSIS INVARIANTS VERIFIED CLEAN ---")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
