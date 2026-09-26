# RC-014C.1 Confirmatory Corpus Grain & Count Reconciliation

## 1. Executive Summary & Inferential Unit Definition

This document establishes the authoritative repertoire census, grain definition, and count reconciliation for the 9 confirmatory composers in the Russian Piano Composer project.

### 1.1 Inferential Unit Standard
In the preregistered RC-012 protocol, the inferential unit for confirmatory hypothesis testing is defined as an **individual standalone musical movement or discrete piece for solo piano** possessing its own complete metric, tonal, and formal boundary structure. 
- For multi-movement cycles where movements are independent musical entities (e.g. *Pictures at an Exhibition*, Beethoven Sonatas, Grieg Lyric Pieces, Bartók Bagatelles, Dvořák Silhouettes, Visions Fugitives, Album de Peterhof), each movement is evaluated as an individual inferential unit.
- For standalone pieces (e.g. Toccata Op. 11, Islamey, standalone Preludes/Etudes), the entire work constitutes a single inferential unit.

### 1.2 Repertoire Policy: Minimum Threshold ($M_c \ge 10$) vs. Exhaustive Sampling
The preregistration specifies $M_c \ge 10$ as an immutable **minimum eligibility threshold per counted composer**, not a truncation cap:
- Under the default preregistered policy `repertoire_sampling_rule: "USE_ALL_ELIGIBLE_PIECES"`, all verified, deduplicated, solo-piano pieces meeting the RC-011 structural compatibility criteria are included in the confirmatory evaluation.
- Previous informal shorthands stating $M_c = 10$ for composers with larger available corpuses (such as Mussorgsky or Scriabin) represented the minimum qualification gate, not a random or arbitrary subsampling.

---

## 2. Complete 9-Composer Census & Reconciliation

Across the 9 confirmatory composers (4 Russian, 5 Control), the complete confirmatory corpus comprises exactly **483 pieces**:

| Composer | Class | Status | Minimum Threshold ($M_c$) | Total Available / Eligible Pieces | Primary Source Repository & Authority | Encoding Format |
|---|---|---|---|---|---|---|
| **Alexander Scriabin** | Russian | `LIVE_QUALIFIED` | 10 | **207** | Stanford CCARH (`craigsapp/scriabin` commit `7daa1136`) | `**kern` |
| **Modest Mussorgsky** | Russian | `LIVE_QUALIFIED` | 10 | **18** | `SyMuPe/PERiScoPe` v1.1 (15 *Pictures* + 3 standalone works) | `MusicXML` |
| **Anton Rubinstein** | Russian | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 10 | **11** | `hectorbellmann-art/Tonal-Piano-Corpus` (commit `3f5a08e9`) | `MusicXML` |
| **Sergei Prokofiev** | Russian | `TECHNICALLY_READY_GOVERNANCE_PENDING` | 10 | **10** | 8 TPC (commit `3f5a08e9`) + 2 Humdrum (`automata/ana-music` commit `335cbdc6`) | `MusicXML` / `**kern` |
| **Edvard Grieg** | Control | `QUALIFIED_BASELINE` | 10 | **66** | `DCMLab/grieg_lyric_pieces` (commit `91a30456`) | `MuseScore` |
| **Claude Debussy** | Control | `QUALIFIED_BASELINE` | 10 | **54** | 7 DCMLab collections (`suite_bergamasque`, `preludes`, `etudes`, `childrens_corner`, `estampes`, `deux_arabesques`, `pour_le_piano`) | `MuseScore` |
| **Ludwig van Beethoven** | Control | `QUALIFIED_BASELINE` | 10 | **91** | `DCMLab/beethoven_piano_sonatas` (commit `ea7181bf`) | `MuseScore` |
| **Béla Bartók** | Control | `QUALIFIED_BASELINE` | 10 | **14** | `DCMLab/bartok_bagatelles` (commit `c6221f6e`) | `MuseScore` |
| **Antonín Dvořák** | Control | `QUALIFIED_BASELINE` | 10 | **12** | `DCMLab/dvorak_silhouettes` (commit `f228006f`) | `MuseScore` |

### Subtotals:
- **Russian Confirmatory Subtotal**: $207 + 18 + 11 + 10 = \mathbf{246}$ pieces across 4 composers.
- **Control Confirmatory Subtotal**: $66 + 54 + 91 + 14 + 12 = \mathbf{237}$ pieces across 5 composers.
- **Grand Total Confirmatory Corpus**: $\mathbf{483}$ pieces across 9 composers.

---

## 3. Composer-by-Composer Repertoire Details

### 3.1 Alexander Scriabin (207 pieces)
Exhaustive collection of Scriabin's solo piano works from CCARH KernScores:
- Preludes (Op. 11 [24], Op. 13 [6], Op. 15 [5], Op. 16 [5], Op. 17 [7], Op. 22 [4], Op. 27 [2], Op. 31 [4], Op. 33 [4], Op. 35 [3], Op. 37 [4], Op. 38, Op. 39 [4], Op. 48 [4], Op. 56 No. 1, Op. 67 [2], Op. 74 [5])
- Etudes (Op. 8 [12], Op. 42 [8], Op. 65 [3])
- Mazurkas (Op. 3 [10], Op. 25 [9], Op. 40 [2])
- Piano Sonatas Nos. 1–10 (multi-movement sonata movements and single-movement sonatas)
- Poèmes (Op. 32 [2], Op. 44 [2], Op. 52 [3], Op. 63 [2], Op. 69 [2], Op. 71 [2], *Vers la flamme* Op. 72)
- Morceaux, Impromptus, Waltzes, and Feuillet d'album.

### 3.2 Modest Mussorgsky (18 pieces)
18 authentic solo piano inferential units:
1. *Pictures at an Exhibition* (15 movements):
   - Promenade 1, Gnomus, Promenade 2, Il vecchio castello, Promenade 3, Tuileries, Bydlo, Promenade 4, Ballet of the Unhatched Chicks, Samuel Goldenberg und Schmuÿle, Promenade 5, Limoges (The Market Place), Catacombae (Sepulcrum romanum), Con mortuis in lingua mortua, The Hut on Hen's Legs (Baba-Yaga), The Great Gate of Kiev.
2. Standalone solo piano pieces (3 pieces):
   - *Impromptu passionné*
   - *Memories of Childhood* (*Souvenir d'enfance*)
   - *The Seamstress* (*La couturière*)

### 3.3 Anton Rubinstein (11 pieces)
11 authentic public-domain works from Tonal-Piano-Corpus:
- *Album de Peterhof*, Op. 75 (8 pieces):
  - No. 1 *Souvenir*
  - No. 2 *Torche-Dance*
  - No. 3 *Nocturne*
  - No. 4 *Barcarolle*
  - No. 5 *Valse-Caprice*
  - No. 6 *Romance*
  - No. 10 *Mazurka*
  - No. 11 *Romance*
- *6 Préludes*, Op. 24 (3 pieces):
  - No. 1 in E major
  - No. 4 in B minor
  - No. 6 in E-flat minor

### 3.4 Sergei Prokofiev (10 pieces)
10 authentic public-domain (pre-1929) works from TPC + Humdrum supplements:
- Tonal-Piano-Corpus (8 pieces):
  - Toccata in D minor, Op. 11 (1912)
  - 10 Pieces, Op. 12: No. 2 *Legend* (1913)
  - 10 Pieces, Op. 12: No. 7 *Prelude (Harp)* (1913)
  - 4 Pieces, Op. 3: No. 3 *March* (1907)
  - 4 Pieces, Op. 2: No. 4 *Étude* (1909)
  - *Visions Fugitives*, Op. 22: No. 1 *Lentamente* (1917, pub. 1918)
  - *Visions Fugitives*, Op. 22: No. 5 *Molto giocoso* (1917, pub. 1918)
  - *Visions Fugitives*, Op. 22: No. 10 *Ridicolosamente* (1917, pub. 1918)
- Humdrum Supplements from `automata/ana-music` (2 pieces):
  - *Visions Fugitives*, Op. 22: No. 2 *Andante* (1917, pub. 1918)
  - *Visions Fugitives*, Op. 22: No. 3 *Allegretto* (1917, pub. 1918)

### 3.5 Edvard Grieg (66 pieces)
Complete *Lyric Pieces* (*Lyriske stykker*) across Books I–X (Op. 12 [8], Op. 38 [8], Op. 43 [6], Op. 47 [7], Op. 54 [6], Op. 57 [6], Op. 62 [6], Op. 65 [6], Op. 68 [6], Op. 71 [7]).

### 3.6 Claude Debussy (54 pieces)
54 solo piano pieces across 7 DCML collections:
- *Suite Bergamasque* (4 pieces: Prélude, Menuet, Clair de lune, Passepied)
- *Préludes* Books I & II (24 pieces)
- *Études* Books I & II (12 pieces)
- *Children's Corner* (6 pieces)
- *Estampes* (3 pieces: Pagodes, La soirée dans Grenade, Jardins sous la pluie)
- *Deux Arabesques* (2 pieces: No. 1, No. 2)
- *Pour le piano* (3 pieces: Prélude, Sarabande, Toccata)

### 3.7 Ludwig van Beethoven (91 pieces)
91 sonata movements from the 32 Piano Sonatas (Op. 2 No. 1 through Op. 111).

### 3.8 Béla Bartók (14 pieces)
*14 Bagatelles*, Op. 6 (Bagatelles I–XIV).

### 3.9 Antonín Dvořák (12 pieces)
*Silhouettes*, Op. 8 (Silhouettes Nos. 1–12).

---

## 4. Governance & Blinding Invariants

1. **Zero Prediction Execution**: No confirmatory piece (from any of the 9 composers) has been evaluated by the frozen predictor.
2. **Immutable Preregistration Gate**: Live status remains $N_{\text{Russian}} = 2$ and `RC012_RESUMPTION_STATUS = BLOCKED` pending human authorization of the external Russian additions.
3. **Role Blindness**: All 483 feature cache entries are stored without class labels or predictive scores.
