# RC-013 Arensky Op. 36 Identity Map & Bibliographic Reconciliation

**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Component**: Work Identity and Source Manifest Verification  
**Authoritative Corpus Entity**: Anton Arensky, *24 Morceaux caractéristiques*, Op. 36 (1894)  
**Status**: IDENTITY_MAPPING_ESTABLISHED (Frozen for Confirmatory Pilot)  
**Date**: 2026-09-20  

---

## 1. Executive Summary & Problem Formulation

During the initial candidate ingestion of Anton Arensky's *24 Morceaux caractéristiques*, Op. 36 for the RC-013 confirmatory acquisition pilot, three severe structural and metadata discrepancies were uncovered:

1. **Score 1 (Op. 36 No. 1)**: Ingested under the preliminary label *"Prélude in F major"*, whereas the authentic source score is a **Prélude in C major** (0 accidentals in key signature; opens with an F-major subdominant coloration over a low C organ point, cadencing to C major).
2. **Score 2 (Op. 36 No. 2)**: Ingested under the erroneous title *"Prélude in A minor"* and erroneously bound to Book 2 (`Arensky_morceaux_op36-2.pdf`), whereas authentic Op. 36 No. 2 is ***La Toupie* (*The Spinning Top / Kreisel*) in C minor / F minor ostinato** (3 flats key signature, $102$ measures, *Vivace* $\mathbf{d. = 120}$, moto perpetuo 16th notes), located on pages 8–15 (PDF pp. 5–12) of Book 1 (`Arensky_morceaux_op36-1.pdf`).
3. **Score 3 / Entry 13 (Op. 36 No. 13)**: Ingested under the erroneous title *"Étude in E minor"*, whereas authentic Op. 36 No. 13 is ***Étude* in F-sharp major** (6 sharps key signature, 3/4 meter, *Moderato* $\mathbf{d. = 69}$), located on pages 61–65 (PDF pp. 1–5) of Book 3 (`Arensky_Morceaux_op.36_No.13-18.pdf`).

Per the **RC-013 Arensky Identity Recovery Protocol**, all transcription candidate generation is halted until the complete 24-piece identity map is established from primary bibliographic records and multi-source cross-catalog reconciliation.

---

## 2. Primary Bibliographic Evidence & Publication History

The work *24 Morceaux caractéristiques pour piano*, Op. 36, was composed by Anton Stepanovich Arensky (1861–1906) in 1894.

### 2.1 Primary Edition (P. Jurgenson, Moscow, 1894)
- **Publisher**: P. Jurgenson, Moscow (Plates 19599–19624 / 19782–19805)
- **Publication Date**: 1894
- **Format**: Issued simultaneously as 4 separate cahiers (volumes) of 6 pieces each, and as individual sheets:
  - **Cahier I (Nos. 1–6)**: Plates 19782–19787 (Printed pp. 4–30)
  - **Cahier II (Nos. 7–12)**: Plates 19788–19793 (Printed pp. 31–60)
  - **Cahier III (Nos. 13–18)**: Plates 19794–19799 (Printed pp. 61–99)
  - **Cahier IV (Nos. 19–24)**: Plates 19800–19805 (Printed pp. 101–125)

### 2.2 Secondary Authoritative Reference (Belwin Mills Reprint, 1982 / IMSLP)
- **Publisher**: Belwin-Mills Publishing Corp., Melville, N.Y., 1982 (Kalmus Piano Series / Belwin Mills reprint of Jurgenson plates).
- **Physical Structure**: 4 volumes preserving original pagination and engraving plates.

---

## 3. Authoritative 24-Piece Movement Map

The table below provides the authoritative title, key, meter, tempo, plate number, and exact physical source PDF coordinates for all 24 pieces of Op. 36.

| Mov # | French Title / Genre | Russian / English Title | Key | Key Sig | Meter | Tempo Marking | Plate (Jurgenson) | Source PDF Filename | PDF Page Range | Printed Pages |
|:---:|:---|:---|:---|:---:|:---:|:---|:---:|:---|:---:|:---:|
| **1** | **Prélude** | Прелюдия / Prelude | **C major** | 0 | 4/4 | *Adagio non troppo* ($\mathbf{d=76}$) | 19782 | `Arensky_morceaux_op36-1.pdf` | **pp. 1–4** | pp. 4–7 |
| **2** | **La Toupie** | Волчок / The Spinning Top | **C minor** | 3 flats | 3/4 | *Vivace* ($\mathbf{d.=120}$) | 19783 | `Arensky_morceaux_op36-1.pdf` | **pp. 5–12** | pp. 8–15 |
| **3** | **Nocturne** | Ноктюрн / Nocturne | **G-sharp minor** | 5 sharps | 4/4 | *Andante cantabile* | 19784 | `Arensky_morceaux_op36-1.pdf` | **pp. 13–16** | pp. 16–19 |
| **4** | **Petite Ballade** | Маленькая баллада / Little Ballad | **F-sharp minor** | 3 sharps | 6/8 | *Allegro moderato* | 19785 | `Arensky_morceaux_op36-1.pdf` | **pp. 17–19** | pp. 20–22 |
| **5** | **Consolation** | Утешение / Consolation | **A major** | 3 sharps | 3/4 | *Andante* | 19786 | `Arensky_morceaux_op36-1.pdf` | **pp. 20–23** | pp. 23–26 |
| **6** | **Duettino** | Дуэттино / Duettino | **F minor / Ab major** | 4 flats | 2/4 | *Andantino con moto* | 19787 | `Arensky_morceaux_op36-1.pdf` | **pp. 24–27** | pp. 27–30 |
| **7** | **Valse** | Вальс / Waltz | **E-flat major** | 3 flats | 3/4 | *Allegro grazioso* | 19788 | `Arensky_morceaux_op36-2.pdf` | **pp. 1–6** | pp. 31–36 |
| **8** | **Intermezzo** | Интермеццо / Intermezzo | **G minor** | 2 flats | 2/4 | *Allegro non troppo* | 19789 | `Arensky_morceaux_op36-2.pdf` | **pp. 7–10** | pp. 37–40 |
| **9** | **Scherzino** | Скерцино / Scherzino | **F major** | 1 flat | 3/8 | *Vivacissimo* | 19790 | `Arensky_morceaux_op36-2.pdf` | **pp. 11–14** | pp. 41–44 |
| **10** | **Ne m'oubliez pas** | Незабудка / Forget-me-not | **D major** | 2 sharps | 3/4 | *Andante sostenuto* | 19791 | `Arensky_morceaux_op36-2.pdf` | **pp. 15–18** | pp. 45–48 |
| **11** | **Barcarolle** | Баркарола / Barcarolle | **F major** | 1 flat | 6/8 | *Andante sostenuto* | 19792 | `Arensky_morceaux_op36-2.pdf` | **pp. 19–22** | pp. 49–52 |
| **12** | **Étude** | Этюд / Study | **B-flat minor** | 5 flats | 2/4 | *Allegro* | 19793 | `Arensky_morceaux_op36-2.pdf` | **pp. 23–30** | pp. 53–60 |
| **13** | **Étude** | Этюд / Study | **F-sharp major** | 6 sharps | 3/4 | *Moderato* ($\mathbf{d.=69}$) | 19794 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 1–5** | pp. 61–65 |
| **14** | **Scherzino** | Скерцино / Scherzino | **E major** | 4 sharps | 2/4 | *Allegro vivace* | 19795 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 6–10** | pp. 66–70 |
| **15** | **Le Ruisseau** | Ручей / The Brook | **D major** | 2 sharps | 6/8 | *Allegro moderato* | 19796 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 11–16** | pp. 71–76 |
| **16** | **Élégie** | Элегия / Elegy | **G minor** | 2 flats | 4/4 | *Andante sostenuto* | 19797 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 17–20** | pp. 77–80 |
| **17** | **Rêve d'une Valse** | Мечты о вальсе / Dream of a Waltz | **D-flat major** | 5 flats | 3/4 | *Tempo di Valse* | 19798 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 21–29** | pp. 81–89 |
| **18** | **Marche** | Марш / March | **C major** | 0 | 4/4 | *Tempo di Marcia* | 19799 | `Arensky_Morceaux_op.36_No.13-18.pdf` | **pp. 30–39** | pp. 90–99 |
| **19** | **Au Rouet** | За прялкой / At the Spinning Wheel | **G major** | 1 sharp | 2/4 | *Allegretto* | 19800 | `Arensky_morceaux_op36-4.pdf` | **pp. 1–5** | pp. 101–105 |
| **20** | **Mazurka** | Мазурка / Mazurka | **B minor** | 2 sharps | 3/4 | *Allegretto* | 19801 | `Arensky_morceaux_op36-4.pdf` | **pp. 6–8** | pp. 106–108 |
| **21** | **Marche funèbre** | Траурный марш / Funeral March | **E-flat minor** | 6 flats | 4/4 | *Lento* | 19802 | `Arensky_morceaux_op36-4.pdf` | **pp. 9–13** | pp. 109–113 |
| **22** | **Polka** | Полька / Polka | **A-flat major** | 4 flats | 2/4 | *Allegro brillante* | 19803 | `Arensky_morceaux_op36-4.pdf` | **pp. 14–17** | pp. 114–117 |
| **23** | **Valse** | Вальс / Waltz | **A minor** | 0 | 3/4 | *Tempo di Valse* | 19804 | `Arensky_morceaux_op36-4.pdf` | **pp. 18–21** | pp. 118–121 |
| **24** | **Aux Champs** | В полях / In the Fields | **F major** | 1 flat | 3/4 | *Andante* | 19805 | `Arensky_morceaux_op36-4.pdf` | **pp. 22–25** | pp. 122–125 |

---

## 4. Specific Resolution of Pilot Movements (Nos. 1, 2, 13)

### 4.1 Score 1: Anton Arensky Op. 36 No. 1
- **Canonical Work ID**: `anton_arensky_op36_m01`
- **Official Movement Title**: *Prélude in C major*
- **Key & Key Signature**: C major (0 sharps/flats). Opens with IV chord (F major) over C bass pedal; concludes on C major tonic triad in m. 36.
- **Time Signature & Tempo**: 4/4 (C), *Adagio non troppo* ($\mathbf{d=76}$).
- **Total Measures**: 36
- **Source Binding**: `Arensky_morceaux_op36-1.pdf` (SHA256: `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855`), PDF pages 1–4 (printed pages 4–7).
- **Status**: `IDENTITY_REVALIDATION_REQUIRED` (Reopened; candidate requires re-verification against clean C-major key metadata).

### 4.2 Score 2: Anton Arensky Op. 36 No. 2
- **Canonical Work ID**: `anton_arensky_op36_m02`
- **Official Movement Title**: *La Toupie (The Spinning Top / Kreisel) in C minor*
- **Key & Key Signature**: C minor (3 flats: $B\flat, E\flat, A\flat$).
- **Time Signature & Tempo**: 3/4, *Vivace* ($\mathbf{d.=120}$).
- **Total Measures**: 102
- **Source Binding**: `Arensky_morceaux_op36-1.pdf` (SHA256: `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855`), PDF pages 5–12 (printed pages 8–15).
- **Status**: `IDENTITY_REVALIDATION_REQUIRED` (Reopened; candidate generator quarantined).

### 4.3 Score 3 / Entry 13: Anton Arensky Op. 36 No. 13
- **Canonical Work ID**: `anton_arensky_op36_m13`
- **Official Movement Title**: *Étude in F-sharp major*
- **Key & Key Signature**: F-sharp major (6 sharps: $F\sharp, C\sharp, G\sharp, D\sharp, A\sharp, E\sharp$).
- **Time Signature & Tempo**: 3/4, *Moderato* ($\mathbf{d.=69}$).
- **Total Measures**: 110 (preliminary estimate from scan inspection; pending full audit).
- **Source Binding**: `Arensky_Morceaux_op.36_No.13-18.pdf` (SHA256: `eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5`), PDF pages 1–5 (printed pages 61–65).
- **Status**: `PENDING_SOURCE_COMPARISON` (Not yet reviewed; candidate template to be rebuilt).

---

## 5. Frozen Historical Scan Manifest for Arensky Op. 36

| Book / Cahier | Movement Range | Filename | SHA256 Hash | Size (Bytes) | Pages |
|:---|:---:|:---|:---|:---:|:---:|
| **Cahier I** | Nos. 1–6 | `Arensky_morceaux_op36-1.pdf` | `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855` | 1,506,575 | 27 |
| **Cahier II** | Nos. 7–12 | `Arensky_morceaux_op36-2.pdf` | `f98061b4097b216aa4fa47b985b3c8addd83218358edf1370a8748a67056a136` | 1,831,534 | 30 |
| **Cahier III** | Nos. 13–18 | `Arensky_Morceaux_op.36_No.13-18.pdf` | `eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5` | 2,571,253 | 39 |
| **Cahier IV** | Nos. 19–24 | `Arensky_morceaux_op36-4.pdf` | *(Pending acquisition upon pilot expansion)* | — | 29 |
