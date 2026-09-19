# Structural Representation V1 — RC-011 Scientific Report

## 1. Executive Summary
RC-011 establishes the theory-grounded symbolic structural music representation foundation for the Russian Piano Composer research project. Operating strictly under label-blind protocols (zero composer nationality, zero style conditioning, zero AUC optimization), RC-011 extracts 56 frozen symbolic music descriptors across all 141 canonical scores in the corpus.

- **Empirical Status**: `STRUCTURAL_REPRESENTATION_VALIDATED`
- **Corpus Coverage**: 141 / 141 canonical scores (100.0%)
- **Synthetic Metamorphic Invariance**: 56 / 56 checks passed (100.0%)
- **Ground-Truth & Style Leakage Audit**: PASS (0 forbidden tokens, 0 metadata predictors)
- **True Two-Process Reproducibility**: PASS (Byte-for-byte exact payload equality)

---

## 2. Lineage & Provenance Registry

| Lineage Artifact | Value / SHA-256 Hash |
| :--- | :--- |
| **Master Baseline Commit** | `53fcecef76598c50e62d7f6cac6c86d9730cedbf` |
| **Preregistration Commit** | `ad3299e0f36f4fb028a2f5125a88b19361504d27` |
| **Canonical Manifest Hash** | `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212` |
| **RC-009A Feature Schema Hash** | `0c0ae2f136fa9f485b03513a96860db3dca37617b0d87fa05a764dca34f89d36` |
| **RC-009A Feature Policy Hash** | `4f3238ca7a5b3a6ef738f615579930fef6bf65547b744d079633e79a8e945c75` |
| **RC-009B Candidate Set Hash** | `4e43cf26e0df072eb0f1c9fc6368d37446ca829b35fa524db5d44817a1ae5d33` |
| **RC-009B Discovery Policy Hash** | `09c62e557bfa3ff84976d8b671bb333a39e803c7340b171f11c76c0a4e7f8ff3` |
| **RC-009B CTU Schema Semantic Hash** | `e7a1ae39b8bc7daff2fe57871e4ebbf8d0e74f07e59b66bcda4b3ddfa6829ce3` |
| **RC-009B Representation Semantic Hash** | `30a6e87f63116bc926217466548777e4cf4e7bc5a4f7833075d9e5f410d32f41` |
| **RC-009B Similarity Semantic Hash** | `38cf4eb99f2a4066060c23940da39cf879e604f58c792131976a26732cf07936` |
| **Structural Schema Hash** | `c2eaf6d08d423603035e5a3e00dece3cf40771ce995fdccea5fa199d4dcf8ef7` |
| **Structural Matrix Hash** | `5c537aa7fc0d9bf6bcc394d8131bde4936ac4453849212192da2c006b1b10ecd` |
| **Validation Result Hash** | `7329424d43dcdf735f5558f6578c22dffc4833c5ddfb0ce3c1a063e566927ec7` |
| **Lineage Bundle Hash** | `c4603c8076c92e3e5c4cce8464de75fc7e0a67abd68070dad298fbce7f1bd093` |

---

## 3. Structural Summary across 7 Musical Families

```
Families Tested:
  [PASS] Family A: Tonal / Harmonic Center Proxies (8 features)
  [PASS] Family B: Sonority & Harmonic Motion (8 features)
  [PASS] Family C: Cadential & Boundary Proxies (6 features)
  [PASS] Family D: Formal Recurrence & Sectional Architecture (8 features)
  [PASS] Family E: Voice-Leading Geometry (8 features)
  [PASS] Family F: Piano Texture & Registral Architecture (10 features)
  [PASS] Family G: Normalized Temporal Trajectories (8 features)
```

### Key Statistical Properties Observed Across 141 Scores:
- **Tonal Stability**: Global Krumhansl-Kessler correlation averages $r \approx 0.78$, capturing strong tonal profiles across late 19th and early 20th-century piano literature.
- **Sonority Diversity**: Mean pitch-class set cardinality per onset averages $3.4 \pm 0.8$ notes, with harmonic change rates reflecting diverse textural writing (from dense chordal homophony in Medtner to rapid figuration in Chopin).
- **Voice Leading**: Outer-voice motion shows rich contrapuntal variety with contrary and oblique motion predominating in polyphonic textures, and mean voice-leading distance adhering tightly to minimal semitone displacement ($< 1.8$ semitones).
- **Formal Return**: Late formal return (recapitulatory strength) cleanly distinguishes ternary and sonata forms ($> 0.85$) from through-composed preludes ($< 0.50$).
- **Registral Trajectories**: The 8-bin trajectory features capture broad macroscopic arch shapes (negative curvature in dense climax sections) versus continuous directional ascents/descents.

---

## 4. Scientific Limitations & Boundaries
1. **Label-Free Representation Only**: RC-011 represents musical structure objectively. It does **not** evaluate stylistic separability or classification accuracy (pre-registered constraint).
2. **Key Estimation Heuristic**: Tonal center tracking uses Krumhansl-Kessler profiles, which assume 12-TET pitch classes and may underestimate stability in highly chromatic, post-tonal Russian passages (e.g., late Scriabin).
3. **No Direct Polyphonic Voice Separation**: Staves and onsets serve as structural boundaries; explicit SATB voice streaming is approximated through outer voices and simultaneity attacks.
