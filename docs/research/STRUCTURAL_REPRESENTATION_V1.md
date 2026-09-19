# Structural Representation V1 — RC-011 Scientific Report

## 1. Executive Summary
RC-011 establishes the theory-grounded symbolic structural music representation foundation for the Russian Piano Composer research project. Operating strictly under label-blind protocols (zero composer nationality, zero style conditioning, zero AUC optimization), RC-011 extracts 56 frozen symbolic music descriptors across all 141 canonical scores in the corpus.

- **Empirical Status**: `STRUCTURAL_REPRESENTATION_VALIDATED`
- **Corpus Coverage**: 141 / 141 canonical scores (100.0%)
- **Synthetic Metamorphic Invariance**: 504 / 504 checks passed across 20 synthetic fixtures (100.0%)
- **Directional Fixture Assertions**: 20 / 20 assertions passed across all 7 families (100.0%)
- **Ground-Truth & Style Leakage Audit**: PASS (0 forbidden tokens, 0 metadata predictors)
- **True Two-Process Reproducibility**: PASS (Byte-for-byte exact payload equality)

---

## 2. Lineage & Provenance Registry

| Lineage Artifact | Value / SHA-256 Hash |
| :--- | :--- |
| **Master Baseline Commit** | `53fcecef76598c50e62d7f6cac6c86d9730cedbf` |
| **Preregistration Commit** | `ad3299e0f36f4fb028a2f5125a88b19361504d27` |
| **Preregistration Amendment 1** | `d9881562a9a206629544681a96b13d99a819cf56` |
| **Canonical Manifest Hash** | `cc94004e6003e60e0af1162eb046fce537c9de0c8274b7564c225364d2b34212` |
| **RC-009A Feature Schema Hash** | `55a388b490dda3089d3073463818edcbc60abf0bcbc9dd114cd5a28032976516` |
| **RC-009A Feature Policy Hash** | `46ac0709d3b34b8e930b6f2d09723ca658cd7f29c204f235b0814f8c2a86150e` |
| **RC-009B Discovery Policy Hash** | `df0810aa9601131df59e1341d6281ce339e1d97b8c993d0baf453fa4a31f0367` |
| **RC-009B Candidate Set Hash** | `43fda7ba9503df0650fa4e2fb03ff897452a90adf225650d2d785d71a6f6ba8d` |
| **RC-009B CTU Schema Semantic Hash** | `03e8103ae9d7d534ded951b781ee6d43269a046fc787c543029c5f9ce3dd0ec1` |
| **RC-009B Representation Semantic Hash** | `967c42a2f47e16dbc6ce3b160ff56284298c73524b46133b6df116ef06db3539` |
| **RC-009B Similarity Semantic Hash** | `9cdd0387050e9c4aa7025f333da975ed02e453b345ebda3622266343fdb475e2` |
| **Structural Schema Hash** | `547406a0836da4182310dfb6f2049481fe134ecfff58894d2f7c2beef19db189` |
| **Tonal Policy Hash** | `54b691ba47362f1a8155beb1b04f35e00904a2a10c6c2cdd1bfef8d5be88366a` |
| **Sonority Policy Hash** | `d9753514573bd2b65b7da0f09b7316eb72a97f19b55fb7b1c193622533bf708a` |
| **Cadence Policy Hash** | `0707085b69e7fd2646be30fe4efa5187f5b7f082ae7ec49af231739d5a68d27f` |
| **Form Policy Hash** | `50e05a5e3212037f56a2611d96d960aa1a74f033a583b42c10e9e918c255b353` |
| **Voice-Leading Policy Hash** | `1b05bbb24043839fae1c771954bfa7a8bed1f72af395c2d0d66dd932e4293324` |
| **Texture Policy Hash** | `356996d524279b1c5d53f7e817922640e0564440a75b4b72760b26099729de9c` |
| **Trajectory Policy Hash** | `3635098aae8631d2dc93acdb7be6885509bc54d32bb8dd55333e2037f39e347f` |
| **Synthetic Fixture Suite Hash** | `258dcceb677f183b14d8015dc9e51b558c090f381f27c8375031a98f0616ec43` |
| **Invariance Contract Hash** | `a21ed9cf21f2df3e75414f06556f0b69ab98694bd201733b90f46389832f58b4` |
| **Preregistration Amendment Hash** | `50f8ffa67cb01b9521b73d3588c4e4d0210d8b744137541a38f6515b24ba56eb` |
| **Exclusion Ledger Hash** | `28b142e1bbef5eeff65ee3a62a94b55e55f88841c3b5954d763d098579eac9b3` |
| **Full Corpus Structural Matrix Hash** | `fab23da25a0c41baad5f1cd76f6bb3f927cd3592543ba7e5a5e3050d50554f2d` |
| **Validation Result Hash** | `74e5710615d27522dd028ebae2bac545a327e51018a467e86ef9114cf38d5925` |
| **Process A Payload Hash** | `3cac2db7aa463635cf25e380b2517e6f4906229d67894efa28f55c958919b1a8` |
| **Process B Payload Hash** | `3cac2db7aa463635cf25e380b2517e6f4906229d67894efa28f55c958919b1a8` |
| **Lineage Bundle Hash** | `85158c5b0f511f44296be5b833a52feee0b248c8bdd99772fb6a4700706c00b3` |

---

## 3. Structural Summary across 7 Musical Families

```
Families Validated:
  [PASS] Family A: Tonal / Harmonic Center Proxies (8 features: 3/3 assertions, 72/72 metamorphic)
  [PASS] Family B: Sonority & Harmonic Motion (8 features: 2/2 assertions, 72/72 metamorphic)
  [PASS] Family C: Cadential & Boundary Proxies (6 features: 2/2 assertions, 54/54 metamorphic)
  [PASS] Family D: Formal Recurrence & Sectional Architecture (8 features: 1/1 assertions, 72/72 metamorphic)
  [PASS] Family E: Voice-Leading Geometry (8 features: 3/3 assertions, 72/72 metamorphic)
  [PASS] Family F: Piano Texture & Registral Architecture (10 features: 4/4 assertions, 90/90 metamorphic)
  [PASS] Family G: Normalized Temporal Trajectories (8 features: 5/5 assertions, 72/72 metamorphic)
```

### Representation Properties:
- **Tonal Stability**: Global Krumhansl-Kessler correlation provides robust tonal profiles across late 19th and early 20th-century piano literature.
- **Sonority Diversity**: Explicit sounding note tracking at each unique onset captures harmonic density and dissonance shares (IC1 semitone, IC6 tritone) across homophonic and polyphonic textures.
- **Voice Leading**: Outer-voice motion and symmetric minimal voice-leading assignment capture stepwise motion, common-tone retention, and voice displacement geometry without requiring ad-hoc voice streaming.
- **Formal Recurrence**: 12-dimensional pitch-class SSM recurrence, novelty peak rate, late recapitulatory return strength, and unsupervised CTU first-occurrence/dispersion provide multi-scale formal architecture.
- **Registral Trajectories**: The normalized 8-bin trajectory features capture macro-level registral trends, attack density slopes/curvatures, and chromaticity trajectories.

---

## 4. Scientific Limitations & Boundaries
1. **Label-Free Representation Only**: RC-011 represents musical structure objectively. It does **not** evaluate stylistic separability or classification accuracy (pre-registered constraint).
2. **Key Estimation Heuristic**: Tonal center tracking uses Krumhansl-Kessler profiles, which assume 12-TET pitch classes and may underestimate stability in highly chromatic passages.
3. **No Direct Polyphonic Voice Streaming**: Staves and onsets serve as structural boundaries; polyphonic voice leading is evaluated via outer voices and optimal bipartite pitch-class assignment.
