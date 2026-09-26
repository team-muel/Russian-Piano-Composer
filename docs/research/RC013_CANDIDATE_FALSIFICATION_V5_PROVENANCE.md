# RC-013 Candidate-Conditioned Falsification Protocol V5 Provenance Record

## 1. Upstream Scholarly Reference & Historical Scan Datasets

All calibration works, ground-truth symbolic files, and historical print scans originate from open, independently published academic and public-domain resources:

### A. Digital Symbolic Datasets (DCMLab, EPFL)
- **Chopin Mazurkas Dataset:** `https://github.com/DCMLab/chopin_mazurkas` (License: `CC BY-NC-SA 4.0`)
- **Grieg Lyric Pieces Dataset:** `https://github.com/DCMLab/grieg_lyric_pieces` (License: `CC BY-NC-SA 4.0`)
- **Schumann Kinderszenen Dataset:** `https://github.com/DCMLab/schumann_kinderszenen` (License: `CC BY-NC-SA 4.0`)
- **Chopin Preludes & Bach WTC:** `https://github.com/DCMLab/chopin_preludes`, `https://github.com/DCMLab/bach_wtc` (License: `CC BY-NC-SA 4.0`)

### B. Historical Plate Image Sources
1. **Chopin Mazurka Op. 6 No. 1 in F-sharp minor (75 mm., 3 pages)**
   - Historical Edition: Rafael Joseffy Edition / Breitkopf Complete Edition (Leipzig, Plate C.XIV.6).
   - License: Public Domain historical print scan.
2. **Chopin Mazurka Op. 7 No. 1 in B-flat major (67 mm., 2 pages)**
   - Historical Edition: Rafael Joseffy Edition / Breitkopf Complete Edition (Leipzig, Plate C.XIV.7).
   - License: Public Domain historical print scan.
3. **Chopin Mazurka Op. 17 No. 1 in B-flat major (61 mm., 2 pages)**
   - Historical Edition: Rafael Joseffy Edition / Breitkopf Complete Edition (Leipzig, Plate C.XIV.17).
   - License: Public Domain historical print scan.
4. **Grieg Lyric Pieces Op. 12 No. 1 - Arietta (23 mm., 1 page)**
   - Historical Edition: C. F. Peters Gesamtausgabe (Leipzig, 1867, Plate 5025).
   - License: Public Domain historical print scan.
5. **Schumann Kinderszenen Op. 15 No. 1 - Von fremden Ländern und Menschen (22 mm., 1 page)**
   - Historical Edition: Clara Schumann Complete Edition (Breitkopf & Härtel, Leipzig, 1879, Plate R.S.49).
   - License: Public Domain historical print scan.
   - Status: Untouched one-shot final holdout split (`CALIBRATION_V5_FINAL_HOLDOUT`).

---

## 2. Rendering and Local Alignment Invariants

- **Production Renderer:** MuseScore 4 CLI (`C:\Program Files\MuseScore 4\bin\MuseScore4.exe`, version 4.6.5).
- **System and Measure Alignment Engine:** `SystemAndMeasureAligner` (`src/russian_piano_composer/corpus/rc013_alignment.py`), establishing staff-projection grand-staff pair detection and proportional measure-slice coordinates.
- **Candidate Conditioning Boundary:** Verification explicitly takes candidate MusicXML ($H_0$) and compares local region distance against counterfactual variations ($H_i$) on the source scan ($S$). It is explicitly **not** represented as independent blind retranscription.

---

## 3. Frozen Cryptographic Hash Bindings (Protocol V5)

- **`RC013_CANDIDATE_FALSIFICATION_PROTOCOL_V5_HASH`**: `3f362056f29575161631176a982937f9b45bc4d04c5c5ee0574afde30ecb2df1`
- **`RC013_CANDIDATE_FALSIFICATION_CALIBRATION_CORPUS_HASH`**: `5f0866c09f3526e58866b63f3d9a86bf3276bcfac25acd84ebd121a75a421aff`
- **`RC013_REAL_SCAN_COUNTERFACTUAL_BENCHMARK_HASH`**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- **`RC013_V5_ALIGNMENT_ENGINE_HASH`**: `e7de857e492e9baf75fcaf644771e0fdc0bc0d573a2589b06921784cda4c2d72`
- **`RC013_V5_COUNTERFACTUAL_SUITE_HASH`**: `60b84bddd1ae66840ab9eef27b1b7ac9ddf913aab580061b86a41da870aaceb6`
- **`RC013_V5_CALIBRATION_RESULT_HASH`**: `01c1488dbfb818aea95a02f788af6f4410079b421f83ef15113eae30f258c461`
