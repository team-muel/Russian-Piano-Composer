# RC-013 Protocol V3 Provenance & External Component Manifest

This document records the exact provenance, licensing, upstream sources, cryptographic hashes, and execution isolation architecture for all external components utilized in the **RC-013 Machine-Triangulated Source-Fidelity Validation Protocol (Version 3)**.

---

## 1. Scope and Scientific Objective

Protocol V3 completely replaces all prior placeholder/pseudo-OMR components and approximate renderers with **real, independently maintained external software systems** and **genuine external real-scan historical piano benchmark datasets**.

No pilot composer scores (Anton Arensky, Anatoly Lyadov, Sergei Lyapunov) are included in this calibration dataset. The calibration corpus is strictly partitioned to prevent data leakage and ensure objective error detection performance on historical piano notation.

---

## 2. External Software Engines & Runtimes

### 2.1 Runtime: OpenJDK 17 (Eclipse Temurin)
* **Component**: OpenJDK 17.0.14+7 (HotSpot 64-bit Server VM)
* **Vendor / Distribution**: Eclipse Adoptium (Temurin)
* **Upstream URL**: `https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.14%2B7/OpenJDK17U-jdk_x64_windows_hotspot_17.0.14_7.zip`
* **License**: GPL v2 with Classpath Exception (GPLv2+CE)
* **Binary Path**: `tools/jdk-17.0.14+7/bin/java.exe`
* **Version**: `openjdk 17.0.14 2025-01-21`

### 2.2 Channel A OMR Engine: Audiveris
* **Component**: Audiveris Optical Music Recognition CLI
* **Version**: `5.11.0`
* **Upstream URL**: `https://github.com/Audiveris/audiveris/releases/download/v5.11.0/Audiveris-5.11.0-windows-x86_64.zip`
* **License**: GNU Affero General Public License v3.0 (AGPL-3.0)
* **Binary Path**: `tools/audiveris/Audiveris/Audiveris.exe`
* **Architecture**: Rule-based musical symbol classification, staff line extraction, and embedded Tesseract OCR for text/expression symbols.
* **Execution Interface**: Standard CLI invocation in isolated sub-process:
  `Audiveris.exe -batch -export -output <temp_dir> <input_image>`
* **SHA256**: Calculated dynamically within `RC013_EXTERNAL_ENGINE_BUNDLE_HASH`.

### 2.3 Channel B Neural OMR Engine: homr
* **Component**: `homr` (Holistic Optical Music Recognition)
* **Version**: `0.7.0`
* **Upstream Repository**: `https://github.com/steinbergmedia/homr` (PyPI package `homr==0.7.0`)
* **License**: MIT License
* **Model Checkpoints**:
  - `segnet_308-0.08985.onnx`: SegNet-based staff line and measure segmentation model.
  - `encoder_pytorch_model_396-0.34771.onnx`: Vision transformer encoder for musical sequence representation.
  - `decoder_pytorch_model_396-0.34771.onnx`: Autoregressive sequence decoder generating standard Humdrum **kern format.
* **Conversion Toolchain**: `hum2xml` converter producing valid MusicXML output from neural **kern tokens.

### 2.4 Channel C Notation Renderer: MuseScore 4
* **Component**: MuseScore 4 Production Notation Engine CLI
* **Version**: `4.4.4.243461245`
* **Upstream Distribution**: Muse Group (`https://musescore.org`)
* **License**: GPL v3.0
* **Binary Path**: `C:\Program Files\MuseScore 4\bin\MuseScore4.exe`
* **Role**: Renders candidate MusicXML into canonical notation images at 300 DPI for geometric and visual correlation analysis against historical scan plates.

---

### 2.5 Combined External Engine Bundle Hash

The combined SHA-256 hash representing the exact configuration, versions, and architectures of the external execution engines is:

$$\text{RC013\_EXTERNAL\_ENGINE\_BUNDLE\_HASH} = \texttt{96fa5f29f01b2d8915ca438a36944f5b9e059b74f55e43352dae8cf32846160e}$$

---

## 3. External Real-Scan Benchmark Datasets

All calibration real-scan benchmarks were sourced from independent external research initiatives and public-domain historical first editions.

### 3.1 DCMLab Chopin Mazurkas Dataset
* **Source Organization**: Digital and Cognitive Musicology Lab (DCML), École Polytechnique Fédérale de Lausanne (EPFL).
* **Upstream Repository**: `https://github.com/DCMLab/chopin_mazurkas`
* **License**: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).
* **Ground Truth Authority**: Independent scholarly digital musicology transcriptions (MuseScore MSCX / MusicXML).
* **Paired Historical Source**: IMSLP / S.B. & Co. 1915 Joseffy Edition high-resolution plate scans (300 DPI PNG).

#### Works Included:
1. **`chopin_mazurka_op06_no01`** (Op. 6 No. 1 in F# minor, 72 measures)
   - Split: `REAL_SCAN_THRESHOLD_SET`
   - Role: Real-scan baseline calibration and noise profile benchmarking.
2. **`chopin_mazurka_op07_no01`** (Op. 7 No. 1 in Bb major, 64 measures)
   - Split: `REAL_SCAN_THRESHOLD_SET`
   - Role: Real-scan cross-validation and rhythmic complexity benchmarking.
3. **`chopin_mazurka_op17_no01`** (Op. 17 No. 1 in Bb major, 60 measures)
   - Split: `CALIBRATION_V3_FINAL_HOLDOUT`
   - Role: Strict untouched holdout; evaluated only once during frozen verification.

### 3.2 Real Scan Benchmark Hash

$$\text{RC013\_REAL\_SCAN\_BENCHMARK\_HASH} = \texttt{3d07697894f19e2a5ee9eab690f95755d0c17b8139f3f3205383e15d6ec02ae1}$$

---

## 4. Execution Sandbox & Blindness Architecture

To guarantee total independence and prevent data leakage:

1. **`BlindOMRFirewall`**:
   - Executes OMR processes inside completely isolated scratch directories.
   - Forbids passing symbolic MusicXML, ground-truth metadata, or work IDs to the recognition processes.
   - Only raw raster image bytes (`.png`, `.tif`) are provided as input.
2. **Channel C Anti-Self-Comparison Guard**:
   - `SELF_COMPARISON_DISALLOWED`: Raises a fatal error if the candidate rendering is compared against its own rendered image.
3. **Downstream Feature Dependency Mapping**:
   - All 5 core RC-011/RC-012 descriptors (pitch-class entropy, voice-leading cross-entropy, harmonic root motion, metric accent syncopation, phrase boundary density) depend upon verified dimensions (`pitch`, `duration`, `onset`, `accidental`, `measure_sequence`, `staff`, `voice`).
   - The protocol enforces strict dimensional coverage verification.

---

## 5. Frozen Cryptographic Manifest Hashes (Protocol V3)

| Protocol Artifact | Canonical SHA-256 Hash |
| :--- | :--- |
| **`RC013_MACHINE_PROTOCOL_V3_HASH`** | `f78dbf70ecf32b44c39b39b9b9a42fc4666041ad4eaf29cce68352a8e2a74bb8` |
| **`RC013_CALIBRATION_V3_CORPUS_HASH`** | `607aad434b43d2bf23b1cc24278fe758572e702bf7080a237ebe3719b5136345` |
| **`RC013_EXTERNAL_ENGINE_BUNDLE_HASH`** | `96fa5f29f01b2d8915ca438a36944f5b9e059b74f55e43352dae8cf32846160e` |
| **`RC013_REAL_SCAN_BENCHMARK_HASH`** | `3d07697894f19e2a5ee9eab690f95755d0c17b8139f3f3205383e15d6ec02ae1` |
| **`RC013_END_TO_END_MUTATION_V3_HASH`** | `1a537f324b69daf230f74520bc03a6d1fc10af9f2fabc3eb5fb8540b52a03eee` |
| **`RC013_CALIBRATION_V3_RESULT_HASH`** | `8dde9ad7c93b9ecb9c4a9bc465853539d55aaf0247f7ec014add691f19c0baa3` |
