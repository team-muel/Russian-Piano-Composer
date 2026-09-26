# RC-013 Machine Validation Protocol V4 Provenance & Calibration Record

## 1. Upstream Dataset & Historical Scan Provenance

All calibration scores and historical plate images in Protocol V4 originate from independently published, openly licensed musicological datasets and public domain historical first editions.

### A. Digital Datasets & Modern Symbolic References
- **DCMLab (Digital and Cognitive Musicology Lab, EPFL)**
  - Repository: `https://github.com/DCMLab/chopin_mazurkas` (License: CC BY-NC-SA 4.0)
  - Repository: `https://github.com/DCMLab/grieg_lyric_pieces` (License: CC BY-NC-SA 4.0)
  - Repository: `https://github.com/DCMLab/chopin_preludes` (License: CC BY-NC-SA 4.0)
  - Repository: `https://github.com/DCMLab/bach_wtc` (License: CC BY-NC-SA 4.0)

### B. Historical Plate Image Sources
- **Chopin Mazurka Op. 6 No. 1 in F-sharp minor**
  - Historical Plate Source: Breitkopf & Härtel Complete Edition (Leipzig, 1878-1880, ed. Bargiel, Brahms, Franchomme, Liszt, Reinecke, Rudorff). Plate C.XIV.6.
  - Scan Licensing: Public Domain / Unrestricted Historical Scan.
  - Extracted Page Range: Pages 2 to 4 (Complete Movement, 75 measures).
- **Chopin Mazurka Op. 7 No. 1 in B-flat major**
  - Historical Plate Source: Breitkopf & Härtel Complete Edition (Leipzig, 1878-1880). Plate C.XIV.7.
  - Scan Licensing: Public Domain / Unrestricted Historical Scan.
  - Extracted Page Range: Pages 6 to 7 (Complete Movement, 67 measures).
- **Chopin Mazurka Op. 17 No. 1 in B-flat major**
  - Historical Plate Source: Breitkopf & Härtel Complete Edition (Leipzig, 1878-1880). Plate C.XIV.17.
  - Scan Licensing: Public Domain / Unrestricted Historical Scan.
  - Extracted Page Range: Pages 24 to 25 (Complete Movement, 61 measures).
- **Grieg Lyric Pieces Op. 12 No. 1 (Arietta)**
  - Historical Plate Source: C. F. Peters (Leipzig, 1867). Plate 5025.
  - Scan Licensing: Public Domain / Unrestricted Historical Scan.
  - Extracted Page Range: Page 3 (Complete Movement, 23 measures).

---

## 2. External Engine Executables & Neural Models

Protocol V4 completely rejects mock or synthetic placeholder OMR logic and strictly utilizes production external engines:

1. **Audiveris Optical Music Recognition (Channel A)**
   - Version: Audiveris v5.11.0 (Java runtime 21.0.6)
   - Executable Path: `tools/audiveris/Audiveris/Audiveris.exe`
   - Invocation: CLI batch mode with deterministic XML export (`-batch -export -output <tempdir> <image>`)
2. **homr Neural Optical Music Recognition (Channel B)**
   - Version: homr v0.7.0 CLI
   - Engine Core: OnnxRuntime with SegNet (staff segmentation) + TrOMR (Vision Transformer sequence decoder)
   - Neural Model Checkpoints:
     - `tools/homr_onnx_models/segmentation/model.onnx`
     - `tools/homr_onnx_models/transformer/encoder.onnx`
     - `tools/homr_onnx_models/transformer/decoder.onnx`
3. **MuseScore Notation Renderer (Channel C)**
   - Version: MuseScore 4 CLI (v4.6.5)
   - Executable Path: `C:\Program Files\MuseScore 4\bin\MuseScore4.exe`
   - Invocation: Headless render to PNG (`-o <tempdir>/page-%d.png <musicxml>`)

---

## 3. Blind OMR Sandbox Architecture (`BlindOMRFirewall`)

The verification pipeline executes within strict physical isolation to prevent ground-truth data leakage:
- OMR engines are provided **only** the rendered or scanned image file.
- Temporary sandbox directories are generated with unique unguessable names (`rc013_blind_omr_*`).
- No candidate MusicXML, MEI, MIDI, or event data is accessible to the OMR execution context.
- Outputs are parsed directly from disk by standard XML parsers (`music21`) before being converted to `ScoreEventGraph`.

---

## 4. Multi-Page Global Measure Coordinate Alignment

In 19th-century historical plate prints, measure numbers are often omitted or restart per system. Protocol V4 enforces deterministic global measure offset accumulation:
- For each page $k \in [1, K]$, the adapter detects local measure count $M_k$.
- The global measure index for measure $m$ on page $k$ is calculated as:
  $$\text{global\_measure}(k, m) = m + \sum_{j=1}^{k-1} M_j$$
- This guarantees no measure collision occurs across multi-page movements.

---

## 5. Frozen Cryptographic Hash Bindings (Protocol V4)

- **`RC013_MACHINE_PROTOCOL_V4_HASH`**: `ef9edd06e3383de1df27cd6b4cb6eb5d96a73fcf435fbc9e76998844fbf521cc`
- **`RC013_CALIBRATION_V4_CORPUS_BUNDLE_HASH`**: `f03f23723e08af74df91e3255c346a99151013a4a1ec4d7ec4c0852935882e1d`
- **`RC013_EXTERNAL_ENGINE_BUNDLE_V4_HASH`**: `e696e41ea25329bd2f5c8642421c085a2c8d71fbfa0aa40ddb8956f7e196b51f`
- **`RC013_REAL_SCAN_BENCHMARK_V4_HASH`**: `5e732f103b9ba9c06b6f64d3d4701f502707d3de19f040ae92c0220334a51946`
- **`RC013_MUTATION_V4_HASH`**: `1a537f324b69daf230f74520bc03a6d1fc10af9f2fabc3eb5fb8540b52a03eee`
- **`RC013_CALIBRATION_V4_RESULT_HASH`**: `df75babd348df2715f9d79b9f749303d8f5dc25827a8c46d0e37252663181835`
