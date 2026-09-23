# RC-013 Scientific Decision Record: Machine-Triangulated Validation Path

## Problem Statement
Full independent human measure-by-measure source-fidelity verification for all pilot material is currently operationally constrained. Without an alternative verifiable path, candidate scores cannot achieve validated source fidelity.

## Decision
Develop, calibrate, and freeze a machine-triangulated source-fidelity validation protocol using three independent verification channels (Classical Staff-Graph OMR, Neural Visual Feature OMR, and Structural Image Alignment).

## Important Scientific Boundaries
1. **No Human Reviewer Impersonation**: Machine-triangulated outputs will be designated as `MACHINE_TRIANGULATED_SOURCE_FIDELITY_PASS` and will never claim `INDEPENDENT_HUMAN_REVIEWER` or `HUMAN_MUSICOLOGIST`.
2. **Distinct Evidence Receipts**: Machine receipts reside in `data/reviews/rc013/machine_accepted/` separate from human review receipts in `data/reviews/rc013/accepted/`.
3. **Pre-Registered Calibration**: Measuring instruments are calibrated on non-RC-013 ground-truth piano material to determine empirical false negative/positive rates prior to any pilot evaluation.
4. **Current Scientific Posture**:
   * Machine Triangulation Status: `PROTOCOL_CALIBRATION`
   * Effect on RC-013 Pilot Scores: `NONE (PENDING_INDEPENDENT_HUMAN_REVIEW)`
   * Russian Composer Pool: $N_{\text{Russian}} = 2$ (Alexander Scriabin, Modest Mussorgsky)
   * RC-012 Resumption: `BLOCKED`
