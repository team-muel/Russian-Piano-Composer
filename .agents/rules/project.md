# Project Rules

### Russian-Only Generative Corpus
- The generative musical grammar must be learned ONLY from the selected Russian piano corpus
- Central stylistic references: Medtner, Rachmaninoff, early/middle Scriabin, Lyapunov, Arensky, Balakirev, Tchaikovsky piano works, and other justified Russian repertoire
- Non-Russian composers (Chopin, Brahms, Schumann, Liszt, Fauré, Debussy, etc.) may ONLY be used as control corpora for scientific comparison and style discrimination
- They must NEVER be used to train melody, harmonic, rhythmic, formal, theme, texture, or voice-leading generation
- Architecture must explicitly distinguish GENERATION CORPUS (Russian only) from CONTROL CORPUS (non-Russian, evaluation only)
- This separation is a HARD project rule

### Target Period and Style
- Russian late-Romantic / early-modern classical piano music
- The goal is NOT composer mimicry — not "generate another Medtner piece"
- The result should be music that convincingly belongs to the Russian piano tradition while representing a hypothetical new composer
- Distinguish Russian tradition affinity from individual-composer similarity
- High Russian-tradition affinity is desirable; extremely high similarity to one historical composer triggers review

### Originality Requirement
- System must not reproduce source melodies after transposition or superficial rhythmic modification
- Copy analysis must consider: interval n-grams, rhythm n-grams, joint interval/rhythm sequences, melodic contour, approximate sequence similarity, transposition-invariant similarity, transformed motif similarity, nearest source theme
- Novelty and Copy Risk are SEPARATE concepts — never collapse them

### Interpretability
- The system follows: Generate → Explain → Evaluate → Verify → Reject or Improve
- Results are never accepted merely because they sound plausible
- System must remain scientifically inspectable
- Prefer interpretable symbolic methods before black-box neural generation
- Do NOT introduce Transformer, LLM music generator, diffusion model, or end-to-end neural composer during v1 unless explicitly authorized

### Deterministic Generation
- Scientific reproducibility is mandatory
- Every stochastic process must derive randomness from a central deterministic RandomContext
- Do NOT use uncontrolled global random.random() or numpy.random.* in generation logic
- Same git commit + dataset version + model version + configuration + seed must reproduce the same canonical theme

### V1 Scope
- V1 focuses on autonomous Russian piano theme generation (2-4 bar thematic seed)
- V1 may contain: corpus ingestion, symbolic representations, theme annotations, interval/rhythm statistics, contour models, tonal/mode representations, Piece/Theme DNA, Russian-style analysis, theme generation, developability evaluation, memorability proxies, harmonic affordance, novelty evaluation, copy-risk detection, beam search, evolutionary refinement, Pareto selection, MusicXML/MIDI output
- V1 must NOT implement: full-length compositions, full accompaniment, full piano texture engine, full sonata form, orchestration, Transformer generation, end-to-end deep learning

### Architecture Boundaries
- Do not build the generator before understanding the corpus
- Required research order: Russian Corpus → Control Corpus → Descriptive Feature Analysis → Russian vs Control Statistical Validation → Robust Feature Set → Theme Generator → Critics → Search

### No Silent API/Scientific-Definition Changes
- Any change to a mathematical definition, critic score, threshold, dataset split, style feature, or public research claim must trigger the review-scientific-change skill
- Silent changes are forbidden

### Issue Completion Definition
- An issue is complete only when: implementation is done, tests pass, lint passes, type-check passes, regressions are checked, and limitations are documented
- Never silently continue to another issue
