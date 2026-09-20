# RC-013 Verified Upstream Source Inventory & Source-Byte Freeze

**Milestone**: RC-013 Russian Confirmatory Corpus Acquisition & Digitization  
**Status**: ACTIVE & VERIFIED  
**Date**: 2026-09-20  

---

## 1. Upstream Evidence Principles

Under RC-013 Amendment 1, no source scan is accepted without:
1. **Persistent Upstream URL & Repository**: Verifiable Internet Archive / IMSLP collections.
2. **Immutable Identifier**: Permanent archive collection ID and document identifier.
3. **Exact Historic Edition**: Documented publisher, plate number, publication year, and editor.
4. **Actual Downloaded Byte Checksum**: 64-character SHA256 computed on the downloaded source file bytes (not local metadata text).
5. **Verified Page Ranges**: Exact score page references within the digitized historical document.

---

## 2. Verified 9-Score Pilot Source Manifest

| Composer | Opus / Movement | Title | Historic Edition & Plate | Archive / Library | Source File SHA256 (Actual Bytes) | File Size (Bytes) | Page Range |
|---|---|---|---|---|---|---|---|
| **Sergei Lyapunov** | Op. 11, No. 1 | *Berceuse* in F-sharp major | J.H. Zimmermann (1897), Plate Z. 2883 | Internet Archive / IMSLP (`imslp-tudes-dexcution-transcendante-op11-lyapunov-sergey`) | `1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0` | 17,210,082 | pp. 1–8 |
| **Sergei Lyapunov** | Op. 11, No. 2 | *Ronde des Fantômes* in D-sharp minor | J.H. Zimmermann (1898), Plate Z. 3060 | Internet Archive / IMSLP (`imslp-tudes-dexcution-transcendante-op11-lyapunov-sergey`) | `1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0` | 17,210,082 | pp. 9–20 |
| **Sergei Lyapunov** | Op. 11, No. 3 | *Carillon* in B major | J.H. Zimmermann (1899), Plate Z. 3060 | Internet Archive / IMSLP (`imslp-tudes-dexcution-transcendante-op11-lyapunov-sergey`) | `1083b34ad2e8a972877d8f3da7458d265976ced42377ad33efe14ad11157beb0` | 17,210,082 | pp. 21–30 |
| **Anton Arensky** | Op. 36, No. 1 | *Prélude* in F major | P. Jurgenson (1894), Plate 19782 | Internet Archive / IMSLP (`imslp-morceaux-caractristiques-op36-arensky-anton`) | `d14e77d7af646671c7ddf267b0ba7bebd4f176a6b2fb6e3a7e9cce114919f855` | 1,506,575 | pp. 1–3 |
| **Anton Arensky** | Op. 36, No. 2 | *Prélude* in A minor | P. Jurgenson (1894), Plate 19783 | Internet Archive / IMSLP (`imslp-morceaux-caractristiques-op36-arensky-anton`) | `f98061b4097b216aa4fa47b985b3c8addd83218358edf1370a8748a67056a136` | 1,831,534 | pp. 1–4 |
| **Anton Arensky** | Op. 36, No. 13 | *Étude* in E minor | P. Jurgenson (1894), Plate 19794 | Internet Archive / IMSLP (`imslp-morceaux-caractristiques-op36-arensky-anton`) | `eaf21776599c1069a78cce881a518a40badb604b9061d4ff6d60537dcb3b87f5` | 2,571,253 | pp. 1–5 |
| **Anatoly Lyadov** | Op. 40, No. 2 | *Prelude* in D minor | M.P. Belaieff (1897), Plate 1450 | University of Toronto Music Library / IA (`31761108768078`) | `8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5` | 3,641,671 | pp. 1–3 |
| **Anatoly Lyadov** | Op. 40, No. 3 | *Prelude* in B-flat major | M.P. Belaieff (1897), Plate 1450 | University of Toronto Music Library / IA (`31761108768078`) | `8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5` | 3,641,671 | pp. 4–6 |
| **Anatoly Lyadov** | Op. 46, No. 4 | *Prelude* in E minor | M.P. Belaieff (1899), Plate 2045 | University of Toronto Music Library / IA (`31761108768078`) | `8484f2d6e88df70001935921964ed6c805f3df069d02cd4d0cd466d8f6cdc8f5` | 3,641,671 | pp. 7–9 |

---

## 3. Cryptographic Verification

- **Source Image Bundle Hash**: `81076d05a28b6a5fbf367ec2128381d26ce99f8ec5347d17bc4d86b098cc35d6` (computed strictly over verified upstream source file bytes and metadata).
- **Rights Verification**: All compositions are public domain worldwide ($p_{\text{death}} \le 1924$). All print editions were published between 1894 and 1899 (pre-1928, public domain in the United States and internationally).
