# Piano Playability

### Human Playability as Hard Final Gate
- Every final piece must be physically playable by a real human pianist
- Playable(piece) == False → REJECT
- Playability is a hard gate, not merely a weighted style score

### Target Performer
- Default: advanced classical pianist / conservatory undergraduate level or stronger
- Difficulty may be high
- Physical impossibility is forbidden

### Ordinary Hand-Size Assumptions
- Do NOT assume unusually large hands
- Do NOT use Rachmaninoff's own hand size as the default ergonomic model
- Use standard concert pianist hand spans as reference

### Tempo-Aware Difficulty
- Difficulty assessment must account for tempo
- A passage that is easy at Adagio may be impossible at Presto

### Constraint Categories
The playability system must eventually consider at minimum:
1. Simultaneous hand span
2. Hand assignment
3. Chord size
4. Chord repetition speed
5. Octave passages
6. Repeated notes
7. Rapid leaps
8. Available movement time
9. Note density
10. Polyphonic voices per hand
11. Hand crossing
12. Redistribution between hands
13. Rolled chords
14. Awkward fingering
15. Tempo-dependent difficulty
16. Endurance
17. Coordination between hands

### Repair Before Rejection
- A musically strong passage that fails playability must be REPAIR or REGENERATE, not silently accepted
- Repair is preferred over rejection when reasonable

### Physical Impossibility Never Accepted
- No exception to this rule
- A piece that contains physically impossible passages is never a valid output
