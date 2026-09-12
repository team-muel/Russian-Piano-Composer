# Corpus Sources V1 Research Documentation

## Verified Seed Datasets

### Russian Generative Repertoire (`GENERATIVE_RUSSIAN`)

1. **`dcml_medtner_tales`**: Nikolai Medtner — Skazki (Fairy Tales) for Solo Piano
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: CC-BY 4.0
   - **Scope**: 10 collections (38 individual Skazki) for solo piano (Op. 8, 9, 14, 20, 26, 34, 35, 42, 48, 51).
   - **Role Rationale**: Central corpus for Medtnerian thematic development, polymetric rhythms, and complex counterpoint.

2. **`dcml_rachmaninoff_op42`**: Sergei Rachmaninoff — Variations on a Theme of Corelli, Op. 42
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: CC-BY 4.0
   - **Scope**: Corelli Variations Op. 42 (Solo Piano).
   - **Role Rationale**: Represents Rachmaninoff's late-period variation techniques, chromatic voice leading, and pianistic textures.

3. **`dcml_tchaikovsky_seasons`**: Pyotr Ilyich Tchaikovsky — The Seasons, Op. 37b
   - **Provider**: EPFL Digital and Cognitive Musicology Lab (DCML)
   - **License**: CC-BY 4.0
   - **Scope**: Complete 12 character pieces.
   - **Role Rationale**: Standard 19th-century Russian lyrical melodic style and homophonic piano textures.

---

### Non-Russian Control Repertoire (`CONTROL_NON_RUSSIAN`)

1. **`dcml_chopin_mazurkas`**: Frédéric Chopin — Mazurkas (Solo Piano)
   - **License**: CC-BY 4.0
   - **Purpose**: Control dataset for Western European Romantic keyboard rhythm and harmony.

2. **`dcml_liszt_annees`**: Franz Liszt — Années de Pèlerinage (Solo Piano)
   - **License**: CC-BY 4.0
   - **Purpose**: Control dataset for 19th-century virtuoso piano writing.

3. **`dcml_schumann_kinderszenen`**: Robert Schumann — Kinderszenen, Op. 15 (Solo Piano)
   - **License**: CC-BY 4.0
   - **Purpose**: Control dataset for German Romantic keyboard miniatures.

---

## Corpus Balance & Provenance Risks

### `CORPUS_BALANCE_RISK`
The initial verified Russian generative corpus contains 38 Medtner pieces vs 1 Rachmaninoff variation cycle and 1 Tchaikovsky cycle.
- **Risk**: Statistical models trained directly without composer re-weighting will overfit to Medtner's specific stylistic quirks (e.g. 5/4 meter, dense polyrhythms).
- **Mitigation Strategy**: Corpus-balancing strategies and composer-level GroupKFold splitting will be introduced during model training in later issues.

### Documented Research Gaps (`PROVISIONAL_NEEDED`)
- **Scriabin**: No verified open-access DCML/MusicXML corpus for Alexander Scriabin (Op. 8 Etudes, Sonatas, Preludes) is currently registered.
- **Lyapunov & Arensky**: Additional late-Romantic Russian repertoire required before final model evaluation.
- **Policy**: Unverified third-party internet MIDI files are strictly excluded from the generative pipeline until independently transcribed and rights-verified.
