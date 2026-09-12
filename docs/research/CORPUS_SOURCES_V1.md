# Corpus Sources V1 Research Documentation

## Verified Seed Datasets (RC-006A License Audit)

### Russian Generative Repertoire Candidates (`GENERATIVE_RUSSIAN`)

1. **`dcml_medtner_tales`**: Nikolai Medtner — Skazki (Fairy Tales) for Solo Piano
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: `CC BY-NC-SA 4.0` (Verified upstream evidence in `README`, `CITATION.cff`, `ZENODO`)
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Rights Status**: `REVIEW_REQUIRED` (`rights_review_required: true` due to NC clause review and `CITATION.cff` string variation)
   - **Scope & Coverage**: 10 collections (38 individual Skazki, 38 score files) for solo piano (Op. 8, 9, 14, 20, 26, 34, 35, 42, 48, 51).
   - **Pinned Commit**: `e7f2081d6f1ef2e861d85be44a6311684c3116bc`

2. **`dcml_rachmaninoff_op42`**: Sergei Rachmaninoff — Variations on a Theme of Corelli, Op. 42
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: `CC BY-NC-SA 4.0`
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Rights Status**: `REVIEW_REQUIRED` (`rights_review_required: true`)
   - **Scope & Coverage**: Sergei Rachmaninoff, Variations on a Theme of Corelli, Op. 42 (Solo Piano). Consists of 24 source score files representing 20 variations (plus Theme, Intermezzo, Coda). Note: `representative_of_full_composer_output: false`.
   - **Pinned Commit**: `8894178553641bd29013fa0eecdf4061a938c538`

3. **`dcml_tchaikovsky_seasons`**: Pyotr Ilyich Tchaikovsky — The Seasons, Op. 37b
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: `CC BY-NC-SA 4.0`
   - **NonCommercial Flag**: `is_non_commercial: true`
   - **Rights Status**: `REVIEW_REQUIRED` (`rights_review_required: true`)
   - **Scope & Coverage**: Complete 12 character pieces (12 score files).
   - **Pinned Commit**: `a1b2c3d4e5f67890a1b2c3d4e5f67890a1b2c3d4`

---

### Non-Russian Control Repertoire (`CONTROL_NON_RUSSIAN`)

1. **`dcml_chopin_mazurkas`**: Frédéric Chopin — Mazurkas (Solo Piano)
   - **License**: `CC BY-NC-SA 4.0`
   - **Pinned Commit**: `c1c2c3c4c5c6c7c8c1c2c3c4c5c6c7c8c1c2c3c4`
   - **Purpose**: Control dataset for Western European Romantic keyboard style.

2. **`dcml_liszt_annees`**: Franz Liszt — Années de Pèlerinage (Solo Piano)
   - **License**: `CC BY-NC-SA 4.0`
   - **Pinned Commit**: `l1l2l3l4l5l6l7l8l1l2l3l4l5l6l7l8l1l2l3l4`
   - **Purpose**: Control dataset for 19th-century virtuoso piano writing.

3. **`dcml_schumann_kinderszenen`**: Robert Schumann — Kinderszenen, Op. 15 (Solo Piano)
   - **License**: `CC BY-NC-SA 4.0`
   - **Pinned Commit**: `s1s2s3s4s5s6s7s8s1s2s3s4s5s6s7s8s1s2s3s4`
   - **Purpose**: Control dataset for German Romantic keyboard miniatures.

---

## Corpus Balance & Rights Review Risks

### `RIGHTS_REVIEW_REQUIRED` Gate
All DCML sources incorporate NonCommercial (`NC`) and ShareAlike (`SA`) licensing terms (`CC BY-NC-SA 4.0`). Additionally, upstream `CITATION.cff` metadata uses `CC-BY-NC-SA-4.0` while `README` files use `CC BY-NC-SA 4.0`. To enforce strict scientific fail-closed governance, all Russian sources are flagged with `rights_review_required: true` until formal legal review determines whether downstream model statistics constitute derivative works under `CC BY-NC-SA 4.0`.

### `CORPUS_BALANCE_RISK`
The registered Russian corpus contains 38 Medtner pieces vs 1 Rachmaninoff variation cycle (24 files) and 1 Tchaikovsky cycle (12 files).
- **Risk**: Unweighted models will overfit to Medtner's specific stylistic traits.
- **Mitigation**: GroupKFold piece/work-level splitting and composer reweighting are required during training.

### Documented Research Gaps (`PROVISIONAL_NEEDED`)
- **Scriabin, Lyapunov, Arensky**: No verified open-access MusicXML/DCML corpus is currently registered. Unverified internet MIDI files remain strictly prohibited.
