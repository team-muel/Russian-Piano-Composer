# RC-014A New Symbolic Source Discovery Record

**Status**: COMPLETED & VERIFIED  
**Discovery Date**: 2026-09-26  
**Candidate External Repository**: `https://github.com/hectorbellmann-art/Tonal-Piano-Corpus`  
**Frozen Target Commit**: `3f5a08e9b2360c11aea5d6d384eb84e7845b793c`  
**Audit Script**: [`scripts/audit_tonal_piano_corpus_rc014a.py`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/scripts/audit_tonal_piano_corpus_rc014a.py)  
**Primary Manifest Artifact**: [`data/manifests/rc014a_tonal_piano_corpus_inventory.json`](file:///C:/Users/User/.gemini/antigravity/scratch/russian-piano-composer/data/manifests/rc014a_tonal_piano_corpus_inventory.json)

---

## 1. Discovery Overview & Provenance Context

Following the formal closure of the machine-verification research branch in RC-013 (`RC013_MACHINE_VALIDATION_EXIT_RECORD.md`), an exhaustive external survey was conducted to identify existing, high-fidelity, source-linked symbolic MusicXML repositories of Russian piano literature.

The public repository `hectorbellmann-art/Tonal-Piano-Corpus` (commit `3f5a08e9b2360c11aea5d6d384eb84e7845b793c`) was identified as containing substantial collections for two key Russian composers:
1. **Sergei Prokofiev (1891–1953)**: 12 candidate MusicXML files, 40 TIFF source scan pages, 12 Finale `.mus` source files.
2. **Anton Rubinstein (1829–1894)**: 11 candidate MusicXML files, 52 TIFF source scan pages, 11 Finale `.mus` source files.

---

## 2. Source-Linked Evidence Hierarchy & Editorial Architecture

The repository adheres to a rigorous, transparent editorial model documented in its root metadata:
* **`EditorialPrinciples.md` (SHA-256: `37a2101a...`)**: Explicitly mandates that all digital notation files reproduce printed historical library editions as closely as possible, preserving exact readings and accompanying every piece with high-resolution TIFF scans.
* **`EditorialNotes.md` (SHA-256: `c997fd27...`)**: Documents every editorial intervention across the entire corpus. In the Russian holdings (Prokofiev and Rubinstein), exactly **zero** editorial departures or unnotated revisions were introduced.
* **Format Completeness**: Every work is provided in three synchronized formats:
  - `.xml`: Clean, valid MusicXML notation.
  - `.mus`/`.musx`: Native Finale engraving files.
  - `.tif`/`.tiff`: Direct high-resolution bitmap scans of historical printed editions.

---

## 3. Inventory & Structural Parsing Summary

| Composer | Raw XML Count | Matched Source TIFFs | Matched Finale Files | Valid MusicXML Parse | RC-011 56-Descriptor Extraction |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sergei Prokofiev** | 12 | 40 | 12 | 12 / 12 (100%) | 12 / 12 (100% PASS) |
| **Anton Rubinstein** | 11 | 52 | 11 | 11 / 11 (100%) | 11 / 11 (100% PASS) |
| **Total** | **23** | **92** | **23** | **23 / 23 (100%)** | **23 / 23 (100% PASS)** |

### Prokofiev Repertoire Holdings:
1. `Legend.xml`: *Legend*, Op. 12 No. 2 (39 measures, 7 TIFFs)
2. `Prelude.xml`: *Prelude 'Harp'*, Op. 12 No. 7 (81 measures, 7 TIFFs)
3. `March.xml`: *March*, Op. 3 No. 3 (21 measures, 2 TIFFs)
4. `Etude.xml`: *Etude*, Op. 2 No. 4 (99 measures, 5 TIFFs)
5. `Montagues.xml`: *The Montagues and the Capulets*, Op. 75 No. 6 (95 measures, 40 TIFFs)
6. `Grasshoppers.xml`: *March of the Grasshoppers*, Op. 65 No. 7 (65 measures, 6 TIFFs)
7. `Moonlit.xml`: *Moonlit Meadows*, Op. 65 No. 12 (82 measures, 6 TIFFs)
8. `Morning.xml`: *Morning*, Op. 65 No. 1 (29 measures, 6 TIFFs)
9. `Toccata.xml`: *Toccata*, Op. 11 (226 measures, 40 TIFFs)
10. `Op22No1.xml`: *Visions Fugitives*, Op. 22 No. 1 (27 measures, 4 TIFFs)
11. `Op22No10.xml`: *Visions Fugitives*, Op. 22 No. 10 (39 measures, 4 TIFFs)
12. `Op22No5.xml`: *Visions Fugitives*, Op. 22 No. 5 (20 measures, 4 TIFFs)

### Rubinstein Repertoire Holdings:
1. `1 Souvenir.xml`: *Souvenir*, Op. 75 No. 1 (133 measures, 36 TIFFs)
2. `10 Mazurka.xml`: *Mazurka*, Op. 75 No. 10 (104 measures, 36 TIFFs)
3. `11 Romance.xml`: *Romance*, Op. 75 No. 11 (65 measures, 36 TIFFs)
4. `2 Aubade.xml`: *Aubade*, Op. 75 No. 2 (52 measures, 36 TIFFs)
5. `3 Marche funèbre.xml`: *Marche funèbre*, Op. 75 No. 3 (90 measures, 36 TIFFs)
6. `4 Impromptu.xml`: *Impromptu*, Op. 75 No. 4 (98 measures, 36 TIFFs)
7. `5 Rêverie.xml`: *Rêverie*, Op. 75 No. 5 (101 measures, 36 TIFFs)
8. `6 Caprice russe.xml`: *Caprice russe*, Op. 75 No. 6 (139 measures, 36 TIFFs)
9. `Prélude1.xml`: *Prélude*, Op. 24 No. 1 (97 measures, 16 TIFFs)
10. `Prélude4.xml`: *Prélude*, Op. 24 No. 4 (164 measures, 16 TIFFs)
11. `Prélude6.xml`: *Prélude*, Op. 24 No. 6 (47 measures, 16 TIFFs)

---

## 4. Discovery Conclusion

The candidate corpus provides authentic, source-linked digital notation for Russian piano works. All 23 scores parse cleanly and satisfy RC-011 structural feature extraction requirements. Full legal rights, jurisdiction analysis, and source-authority symmetry are evaluated in `docs/research/RC014A_TONAL_PIANO_CORPUS_QUALIFICATION_AUDIT.md`.
