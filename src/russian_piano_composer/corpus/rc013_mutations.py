"""Adversarial Symbolic Mutation Engine for RC-013 Machine Verification Calibration.

Injects controlled, deterministic notation corruptions across 19 critical and structural
mutation families into canonical MusicXML / Event Graphs to empirically measure verifier recall.
"""

from __future__ import annotations

import fractions
from dataclasses import asdict, dataclass
from typing import ClassVar

from russian_piano_composer.corpus.rc013_event_graph import (
    NormalizedEventGraph,
    ScoreEvent,
)


@dataclass(frozen=True)
class MutationSpecimen:
    """A mutated score specimen with full provenance of injected mutation."""

    specimen_id: str
    original_score_id: str
    mutation_family: str
    target_measure: int
    mutation_description: str
    mutated_event_graph: NormalizedEventGraph
    specimen_sha256: str


class RC013MutationEngine:
    """Generates deterministic adversarial corruptions to test machine verifier sensitivity."""

    MUTATION_FAMILIES: ClassVar[list[str]] = [
        "pitch_semitone_shift",
        "wrong_accidental",
        "octave_displacement",
        "duration_halving_doubling",
        "rest_insertion",
        "rest_deletion",
        "note_deletion",
        "chord_tone_deletion",
        "extra_note_insertion",
        "tie_removal",
        "tie_insertion",
        "voice_swap",
        "staff_swap",
        "tuplet_corruption",
        "key_signature_mutation",
        "time_signature_mutation",
        "measure_deletion",
        "measure_duplication",
        "repeat_corruption",
    ]

    def generate_mutations(
        self,
        base_graph: NormalizedEventGraph,
        max_per_family: int = 2,
    ) -> list[MutationSpecimen]:
        """Generates a suite of mutated specimens across all 19 mutation families."""
        specimens: list[MutationSpecimen] = []
        events = base_graph.events
        if not events:
            return specimens

        score_id = base_graph.score_id
        target_m = max(1, base_graph.total_measures // 2)

        # 1. pitch_semitone_shift
        for idx in range(min(max_per_family, len(events))):
            mutated = list(events)
            target_evt = mutated[idx]
            if not target_evt.is_rest and target_evt.pitch_step:
                new_alter = (target_evt.alter or 0) + 1
                mutated[idx] = ScoreEvent(
                    **{**asdict(target_evt), "alter": new_alter}
                )
                specimens.append(self._create_specimen(score_id, "pitch_semitone_shift", target_evt.measure_number, f"Shifted pitch {target_evt.pitch_step} alter to {new_alter}", mutated))
                break

        # 2. wrong_accidental
        for idx, evt in enumerate(events):
            if not evt.is_rest and evt.pitch_step:
                mutated = list(events)
                new_alter = -1 if (evt.alter or 0) >= 0 else 1
                mutated[idx] = ScoreEvent(**{**asdict(evt), "alter": new_alter})
                specimens.append(self._create_specimen(score_id, "wrong_accidental", evt.measure_number, f"Altered accidental from {evt.alter} to {new_alter}", mutated))
                break

        # 3. octave_displacement
        for idx, evt in enumerate(events):
            if not evt.is_rest and evt.octave is not None:
                mutated = list(events)
                new_oct = evt.octave + 1 if evt.octave < 7 else evt.octave - 1
                mutated[idx] = ScoreEvent(**{**asdict(evt), "octave": new_oct})
                specimens.append(self._create_specimen(score_id, "octave_displacement", evt.measure_number, f"Displaced octave from {evt.octave} to {new_oct}", mutated))
                break

        # 4. duration_halving_doubling
        for idx, evt in enumerate(events):
            if not evt.is_rest:
                mutated = list(events)
                dur_frac = fractions.Fraction(evt.duration_fraction)
                new_dur = str(dur_frac / 2 if dur_frac >= fractions.Fraction(1, 4) else dur_frac * 2)
                mutated[idx] = ScoreEvent(**{**asdict(evt), "duration_fraction": new_dur})
                specimens.append(self._create_specimen(score_id, "duration_halving_doubling", evt.measure_number, f"Mutated duration from {evt.duration_fraction} to {new_dur}", mutated))
                break

        # 5. rest_insertion
        mutated = list(events)
        mutated.append(ScoreEvent(score_id=score_id, measure_number=target_m, staff=1, voice=1, onset_fraction="1/2", duration_fraction="1/4", event_type="REST", is_rest=True))
        specimens.append(self._create_specimen(score_id, "rest_insertion", target_m, "Inserted extraneous rest in measure", mutated))

        # 6. rest_deletion
        for idx, evt in enumerate(events):
            if evt.is_rest:
                mutated = list(events)
                mutated.pop(idx)
                specimens.append(self._create_specimen(score_id, "rest_deletion", evt.measure_number, f"Deleted rest at measure {evt.measure_number}", mutated))
                break
        else:
            # If no rest in score, convert first note to rest in mutated
            mutated = list(events)
            mutated[0] = ScoreEvent(**{**asdict(mutated[0]), "is_rest": True, "event_type": "REST", "pitch_step": None})
            specimens.append(self._create_specimen(score_id, "rest_deletion", target_m, "Converted note to rest (rest mismatch)", mutated))

        # 7. note_deletion
        for idx, evt in enumerate(events):
            if not evt.is_rest:
                mutated = list(events)
                mutated.pop(idx)
                specimens.append(self._create_specimen(score_id, "note_deletion", evt.measure_number, f"Deleted note at measure {evt.measure_number}", mutated))
                break

        # 8. chord_tone_deletion
        # Find note sharing same onset
        onsets: dict[str, list[int]] = {}
        for idx, evt in enumerate(events):
            onsets.setdefault(f"{evt.measure_number}:{evt.onset_fraction}", []).append(idx)
        chord_indices = next((idxs for idxs in onsets.values() if len(idxs) > 1), None)
        if chord_indices:
            mutated = list(events)
            mutated.pop(chord_indices[0])
            specimens.append(self._create_specimen(score_id, "chord_tone_deletion", target_m, "Removed one chord tone", mutated))
        else:
            mutated = list(events)
            mutated.pop(0)
            specimens.append(self._create_specimen(score_id, "chord_tone_deletion", 1, "Simulated chord tone deletion", mutated))

        # 9. extra_note_insertion
        mutated = list(events)
        mutated.append(ScoreEvent(score_id=score_id, measure_number=target_m, staff=1, voice=1, onset_fraction="3/8", duration_fraction="1/8", event_type="NOTE", pitch_step="G", alter=0, octave=5))
        specimens.append(self._create_specimen(score_id, "extra_note_insertion", target_m, "Inserted extra note G5", mutated))

        # 10. tie_removal
        for idx, evt in enumerate(events):
            if evt.tie_start or evt.tie_stop:
                mutated = list(events)
                mutated[idx] = ScoreEvent(**{**asdict(evt), "tie_start": False, "tie_stop": False})
                specimens.append(self._create_specimen(score_id, "tie_removal", evt.measure_number, "Removed tie", mutated))
                break
        else:
            mutated = list(events)
            mutated[0] = ScoreEvent(**{**asdict(mutated[0]), "tie_stop": True})
            specimens.append(self._create_specimen(score_id, "tie_removal", 1, "Simulated tie mismatch (injected dangling tie stop)", mutated))

        # 11. tie_insertion
        mutated = list(events)
        mutated[0] = ScoreEvent(**{**asdict(mutated[0]), "tie_start": True})
        specimens.append(self._create_specimen(score_id, "tie_insertion", 1, "Inserted unreferenced tie", mutated))

        # 12. voice_swap
        for idx, evt in enumerate(events):
            mutated = list(events)
            new_voice = 2 if evt.voice == 1 else 1
            mutated[idx] = ScoreEvent(**{**asdict(evt), "voice": new_voice})
            specimens.append(self._create_specimen(score_id, "voice_swap", evt.measure_number, f"Swapped voice to {new_voice}", mutated))
            break

        # 13. staff_swap
        for idx, evt in enumerate(events):
            mutated = list(events)
            new_staff = 2 if evt.staff == 1 else 1
            mutated[idx] = ScoreEvent(**{**asdict(evt), "staff": new_staff})
            specimens.append(self._create_specimen(score_id, "staff_swap", evt.measure_number, f"Swapped staff to {new_staff}", mutated))
            break

        # 14. tuplet_corruption
        mutated = list(events)
        mutated[0] = ScoreEvent(**{**asdict(mutated[0]), "tuplet_ratio": "5/4"})
        specimens.append(self._create_specimen(score_id, "tuplet_corruption", 1, "Corrupted tuplet ratio to 5/4", mutated))

        # 15. key_signature_mutation
        mutated = [ScoreEvent(**{**asdict(e), "key_signature": ((e.key_signature or 0) + 1)}) for e in events]
        specimens.append(self._create_specimen(score_id, "key_signature_mutation", 1, "Mutated key signature fifths by +1", mutated))

        # 16. time_signature_mutation
        mutated = [ScoreEvent(**{**asdict(e), "time_signature": "3/4" if e.time_signature != "3/4" else "4/4"}) for e in events]
        specimens.append(self._create_specimen(score_id, "time_signature_mutation", 1, "Mutated time signature", mutated))

        # 17. measure_deletion
        mutated = [e for e in events if e.measure_number != target_m]
        specimens.append(self._create_specimen(score_id, "measure_deletion", target_m, f"Deleted entire measure {target_m}", mutated))

        # 18. measure_duplication
        duped_events: list[ScoreEvent] = []
        for e in events:
            duped_events.append(e)
            if e.measure_number == target_m:
                duped_events.append(ScoreEvent(**{**asdict(e), "measure_number": target_m + 1000}))
        specimens.append(self._create_specimen(score_id, "measure_duplication", target_m, f"Duplicated measure {target_m}", duped_events))

        # 19. repeat_corruption
        mutated = list(events)
        mutated[0] = ScoreEvent(**{**asdict(mutated[0]), "repeat": "FORWARD"})
        specimens.append(self._create_specimen(score_id, "repeat_corruption", 1, "Injected invalid repeat direction", mutated))

        return specimens

    def _create_specimen(
        self,
        original_score_id: str,
        family: str,
        target_m: int,
        desc: str,
        events: list[ScoreEvent],
    ) -> MutationSpecimen:
        graph = NormalizedEventGraph(score_id=f"{original_score_id}_mut_{family}", events=events)
        sha = graph.compute_sha256()
        specimen_id = f"{original_score_id}_{family}_{sha[:8]}"
        return MutationSpecimen(
            specimen_id=specimen_id,
            original_score_id=original_score_id,
            mutation_family=family,
            target_measure=target_m,
            mutation_description=desc,
            mutated_event_graph=graph,
            specimen_sha256=sha,
        )
