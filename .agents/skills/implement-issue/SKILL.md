---
name: implement-issue
description: Structured workflow for implementing a project issue from inspection through verification.
---

1. **Inspect Issue Dependencies** — Check which other issues/modules this depends on. Verify dependencies are complete.
2. **Inspect Existing Contracts** — Review interfaces, schemas, and type signatures of modules this issue touches.
3. **Produce Implementation Plan** — Create a plan listing approach, affected files, and risks.
4. **List Files Affected** — Enumerate every file that will be created, modified, or deleted.
5. **Identify Mathematical/Scientific Definitions Affected** — Flag any changes to formulas, metrics, thresholds, or features. If any, invoke `review-scientific-change`.
6. **Implement Smallest Coherent Change** — Write the implementation. Do not bundle unrelated changes.
7. **Add Tests** — Write unit tests, property-based tests, and regression tests as appropriate.
8. **Run Verification** — Execute: ruff check, mypy, pytest. All must pass.
9. **Report Regressions and Limitations** — Document any test failures, known limitations, or edge cases.
10. **Stop** — Never silently continue to another issue. Report completion and await next assignment.
