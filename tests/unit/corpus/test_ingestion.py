"""
Unit tests for symbolic score ingestion and ms3 parser adapter (network-free).
"""

from fractions import Fraction
from pathlib import Path

from russian_piano_composer.corpus.adapters.dcml_ms3 import (
    ingest_score_entry_from_ms3,
    parse_rational,
    parse_spelled_pitch_from_name,
)
from russian_piano_composer.corpus.ingestion import EXPECTED_MANIFEST_HASH, export_canonical_parquet
from russian_piano_composer.domain.corpus import CorpusRole
from russian_piano_composer.theory.pitch import PitchLetter, SpelledPitch


def test_parse_spelled_pitch_from_name_enharmonics() -> None:
    c_sharp = parse_spelled_pitch_from_name("C#4")
    d_flat = parse_spelled_pitch_from_name("Db4")

    assert c_sharp.letter == PitchLetter.C
    assert c_sharp.alteration == 1
    assert c_sharp.octave == 4
    assert c_sharp.midi == 61

    assert d_flat.letter == PitchLetter.D
    assert d_flat.alteration == -1
    assert d_flat.octave == 4
    assert d_flat.midi == 61

    # Mandatory check: same MIDI, distinct SpelledPitch identity
    assert c_sharp.midi == d_flat.midi
    assert c_sharp != d_flat
    assert str(c_sharp) == "C#4"
    assert str(d_flat) == "Db4"


def test_parse_spelled_pitch_from_name_double_accidentals() -> None:
    f_double_sharp = parse_spelled_pitch_from_name("F##4")
    b_double_flat = parse_spelled_pitch_from_name("Ebb4")

    assert f_double_sharp.letter == PitchLetter.F
    assert f_double_sharp.alteration == 2
    assert f_double_sharp.midi == 67

    assert b_double_flat.letter == PitchLetter.E
    assert b_double_flat.alteration == -2
    assert b_double_flat.midi == 62


def test_parse_rational_exactness() -> None:
    assert parse_rational("1/4") == Fraction(1, 4)
    assert parse_rational("3/8") == Fraction(3, 8)
    assert parse_rational(1) == Fraction(1, 1)
    assert parse_rational(0.25) == Fraction(1, 4)


def test_ingest_score_entry_synthetic_mscx(tmp_path: Path) -> None:
    mscx_content = """<?xml version="1.0" encoding="UTF-8"?>
<museScore version="3.01">
  <programVersion>3.6.2</programVersion>
  <programRevision>3224f34</programRevision>
  <Score>
    <LayerTag id="0" tag="default"></LayerTag>
    <currentLayer>0</currentLayer>
    <Division>480</Division>
    <Part>
      <Staff id="1">
        <StaffType group="pitched">
          <name>stdNormal</name>
        </StaffType>
      </Staff>
      <trackName>Piano</trackName>
    </Part>
    <Staff id="1">
      <Measure>
        <voice>
          <TimeSig>
            <sigN>4</sigN>
            <sigD>4</sigD>
          </TimeSig>
          <Chord>
            <durationType>quarter</durationType>
            <Note>
              <pitch>61</pitch>
              <tpc>21</tpc>
            </Note>
          </Chord>
          <Chord>
            <durationType>quarter</durationType>
            <Note>
              <pitch>61</pitch>
              <tpc>9</tpc>
            </Note>
          </Chord>
          <Rest>
            <durationType>half</durationType>
          </Rest>
        </voice>
      </Measure>
    </Staff>
  </Score>
</museScore>"""

    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    score_path = repo_dir / "op08n01.mscx"
    score_path.write_text(mscx_content, encoding="utf-8")

    score = ingest_score_entry_from_ms3(
        corpus_id="dcml_medtner_tales",
        corpus_role=CorpusRole.GENERATIVE_RUSSIAN,
        score_entry_id="op08n01",
        composer="Nikolai Medtner",
        title="Medtner Op. 8 No. 1",
        repo_dir=repo_dir,
        source_repository="DCMLab/medtner_tales",
        source_commit="1d2e58ba8d329463829e45e75900af43be4256bf",
        source_sha256="1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        manifest_hash=EXPECTED_MANIFEST_HASH,
    )

    assert score.piece_id == "dcml_medtner_tales:op08n01"
    assert len(score.measures) == 1
    assert len(score.events) == 3

    e0 = score.events[0]
    e1 = score.events[1]

    # Check pitch spellings C#4 vs Db4
    assert e0.pitch == SpelledPitch(letter=PitchLetter.C, alteration=1, octave=4)
    assert e1.pitch == SpelledPitch(letter=PitchLetter.D, alteration=-1, octave=4)
    assert e0.midi == e1.midi == 61

    # Check Parquet export
    out_dir = tmp_path / "parquet_out"
    export_canonical_parquet(out_dir, [score])

    assert (out_dir / "pieces.parquet").exists()
    assert (out_dir / "measures.parquet").exists()
    assert (out_dir / "events.parquet").exists()
