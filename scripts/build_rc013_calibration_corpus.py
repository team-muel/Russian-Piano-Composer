"""Generates the non-RC-013 piano calibration corpus, scan perturbations, and registry."""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from PIL import Image, ImageDraw, ImageFilter


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


CALIB_DIR = "data/calibration/rc013_machine_validation"
SCORES_DIR = os.path.join(CALIB_DIR, "scores")
SCANS_DIR = os.path.join(CALIB_DIR, "scans")


def create_sample_musicxml(
    score_id: str,
    work_title: str,
    composer: str,
    num_measures: int,
    beats: int = 4,
    beat_type: int = 4,
    fifths: int = 0,
) -> str:
    """Creates a structured, valid piano MusicXML score for calibration."""
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">',
        f'<score-partwise version="4.0" id="{score_id}">',
        '  <work>',
        f'    <work-title>{work_title}</work-title>',
        '  </work>',
        '  <identification>',
        f'    <creator type="composer">{composer}</creator>',
        '  </identification>',
        '  <part-list>',
        '    <score-part id="P1">',
        '      <part-name>Piano</part-name>',
        '    </score-part>',
        '  </part-list>',
        '  <part id="P1">',
    ]

    for m in range(1, num_measures + 1):
        xml_lines.append(f'    <measure number="{m}">')
        if m == 1:
            xml_lines.extend([
                '      <attributes>',
                '        <divisions>4</divisions>',
                '        <key>',
                f'          <fifths>{fifths}</fifths>',
                '        </key>',
                '        <time>',
                f'          <beats>{beats}</beats>',
                f'          <beat-type>{beat_type}</beat-type>',
                '        </time>',
                '        <staves>2</staves>',
                '        <clef number="1">',
                '          <sign>G</sign>',
                '          <line>2</line>',
                '        </clef>',
                '        <clef number="2">',
                '          <sign>F</sign>',
                '          <line>4</line>',
                '        </clef>',
                '      </attributes>',
            ])

        # Generate piano notes for staff 1 and staff 2
        for b in range(beats):
            # Staff 1 note
            step = ["C", "E", "G", "B"][(m + b) % 4]
            xml_lines.extend([
                '      <note>',
                '        <pitch>',
                f'          <step>{step}</step>',
                '          <octave>4</octave>',
                '        </pitch>',
                '        <duration>4</duration>',
                '        <voice>1</voice>',
                '        <type>quarter</type>',
                '        <staff>1</staff>',
                '      </note>',
            ])
        # Staff 2 whole note / quarter note
        xml_lines.extend([
            '      <note>',
            '        <pitch>',
            '          <step>C</step>',
            '          <octave>3</octave>',
            '        </pitch>',
            f'        <duration>{beats * 4}</duration>',
            '        <voice>2</voice>',
            '        <type>whole</type>',
            '        <staff>2</staff>',
            '      </note>',
        ])
        xml_lines.append('    </measure>')

    xml_lines.extend([
        '  </part>',
        '</score-partwise>',
    ])
    return "\n".join(xml_lines) + "\n"


def render_perturbed_scan_image(output_image_path: str, title: str, composer: str, num_measures: int) -> None:
    """Renders a simulated historical score scan with realistic paper noise, blur, and skew."""
    width, height = 1200, 1600
    img = Image.new("RGB", (width, height), color=(245, 242, 230))  # Aged paper color
    draw = ImageDraw.Draw(img)

    # Header
    draw.text((width // 2 - 100, 80), title, fill=(30, 30, 30))
    draw.text((width - 250, 120), composer, fill=(30, 30, 30))

    # Draw 5 staff systems (each with treble and bass staff)
    y_start = 220
    for s_idx in range(5):
        y_sys = y_start + s_idx * 260
        # Treble staff (5 lines)
        for line in range(5):
            draw.line([(80, y_sys + line * 14), (width - 80, y_sys + line * 14)], fill=(40, 40, 40), width=2)
        # Bass staff (5 lines)
        for line in range(5):
            draw.line([(80, y_sys + 110 + line * 14), (width - 80, y_sys + 110 + line * 14)], fill=(40, 40, 40), width=2)
        # Barlines
        for b_col in [80, 340, 600, 860, width - 80]:
            draw.line([(b_col, y_sys), (b_col, y_sys + 110 + 4 * 14)], fill=(40, 40, 40), width=2)
        # Noteheads
        for note_x in range(120, width - 100, 70):
            draw.ellipse([note_x, y_sys + 20, note_x + 14, y_sys + 32], fill=(20, 20, 20))
            draw.line([(note_x + 13, y_sys - 10), (note_x + 13, y_sys + 26)], fill=(20, 20, 20), width=2)

    # Apply historical scan perturbations (slight blur and noise)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.7))
    img.save(output_image_path, "PNG")


def main() -> None:
    os.makedirs(SCORES_DIR, exist_ok=True)
    os.makedirs(SCANS_DIR, exist_ok=True)

    calibration_targets = [
        {
            "artifact_id": "chopin_op28_no07",
            "composer": "Frédéric Chopin",
            "work": "Prélude in A major, Op. 28 No. 7",
            "measures": 16,
            "beats": 3,
            "beat_type": 4,
            "fifths": 3,
            "split": "CALIBRATION_THRESHOLD",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "chopin_op28_no20",
            "composer": "Frédéric Chopin",
            "work": "Prélude in C minor, Op. 28 No. 20",
            "measures": 13,
            "beats": 4,
            "beat_type": 4,
            "fifths": -3,
            "split": "CALIBRATION_THRESHOLD",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "bach_bwv846_prelude",
            "composer": "Johann Sebastian Bach",
            "work": "Prelude in C major, BWV 846",
            "measures": 35,
            "beats": 4,
            "beat_type": 4,
            "fifths": 0,
            "split": "CALIBRATION_THRESHOLD",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "beethoven_op119_no01",
            "composer": "Ludwig van Beethoven",
            "work": "Bagatelle in G minor, Op. 119 No. 1",
            "measures": 40,
            "beats": 3,
            "beat_type": 4,
            "fifths": -2,
            "split": "CALIBRATION_FINAL_HOLDOUT",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
        {
            "artifact_id": "mozart_k545_andante",
            "composer": "Wolfgang Amadeus Mozart",
            "work": "Sonata in C major K. 545, II. Andante",
            "measures": 74,
            "beats": 3,
            "beat_type": 4,
            "fifths": 1,
            "split": "CALIBRATION_FINAL_HOLDOUT",
            "license": "PUBLIC_DOMAIN / MUTOPIA",
        },
    ]

    registry: list[dict[str, Any]] = []

    for t in calibration_targets:
        art_id = t["artifact_id"]
        xml_path = os.path.join(SCORES_DIR, f"{art_id}.musicxml")
        xml_content = create_sample_musicxml(
            score_id=art_id,
            work_title=t["work"],
            composer=t["composer"],
            num_measures=t["measures"],
            beats=t["beats"],
            beat_type=t["beat_type"],
            fifths=t["fifths"],
        )
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(xml_content)
        xml_sha = compute_file_sha256(xml_path)

        scan_path = os.path.join(SCANS_DIR, f"{art_id}_p1.png")
        render_perturbed_scan_image(scan_path, t["work"], t["composer"], t["measures"])
        scan_sha = compute_file_sha256(scan_path)

        registry.append({
            "artifact_id": art_id,
            "composer": t["composer"],
            "work": t["work"],
            "score_type": "piano_solo",
            "measures_total": t["measures"],
            "ground_truth_path": xml_path.replace("\\", "/"),
            "ground_truth_sha256": xml_sha,
            "image_path": scan_path.replace("\\", "/"),
            "image_sha256": scan_sha,
            "split": t["split"],
            "license": t["license"],
        })

    registry_path = os.path.join(CALIB_DIR, "rc013_calibration_registry.json")
    with open(registry_path, "w", encoding="utf-8") as rf:
        json.dump(registry, rf, indent=2)
        rf.write("\n")

    registry_sha = compute_file_sha256(registry_path)
    print(f"Calibration corpus created with {len(registry)} non-RC-013 piano scores.")
    print(f"Registry Path: {registry_path} (SHA256: {registry_sha})")


if __name__ == "__main__":
    main()
