---
name: review-scientific-change
description: Mandatory review protocol when a change affects mathematical definitions, metrics, thresholds, dataset splits, or style features.
---

This skill MUST be invoked when a change modifies any of:
- A mathematical definition or formula
- A critic score or evaluation metric
- A threshold or decision boundary
- A dataset split strategy
- A style feature definition
- A public research claim or conclusion

Review protocol:
1. **Identify What Changed** — Precisely describe the before and after.
2. **Justify the Change** — Provide scientific rationale. Reference OBSERVED/LITERATURE/HYPOTHESIS/ENGINEERING HEURISTIC classification.
3. **Impact Assessment** — Which downstream components are affected? Which experiments need re-running?
4. **Regression Risk** — Could this change invalidate previous results?
5. **Approval** — Changes to scientific definitions require explicit review before merging.
