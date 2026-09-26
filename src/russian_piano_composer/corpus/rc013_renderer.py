"""Production Notation Score Renderer and Test Fixture Renderer for RC-013 Channel C.

Provides:
1. MuseScoreProductionScoreRenderer: Production-grade notation engraver utilizing MuseScore 4 CLI.
   Fully renders pitch, accidentals, duration glyphs, beams, rests, ties, tuplets, key signatures,
   time signatures, clefs, multi-voice counterpoint, dynamics, and repeats.
2. MatplotlibDiagnosticRenderer: Diagnostic/test fixture renderer for fast isolated testing.
"""

from __future__ import annotations

import glob
import hashlib
import os
import subprocess

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from russian_piano_composer.corpus.rc013_event_graph import (
    extract_event_graph_from_musicxml,
)


def compute_file_sha256(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class MuseScoreProductionScoreRenderer:
    """Production-grade notation rendering engine utilizing MuseScore 4 CLI for Channel C verification."""

    RENDERER_NAME = "MuseScoreProductionScoreRenderer"
    RENDERER_VERSION = "4.0.0-rc013"
    DEFAULT_MUSESCORE_PATH = r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe"

    def __init__(self, musescore_path: str | None = None, dpi: int = 300, target_dpi: int | None = None) -> None:
        self.musescore_path = musescore_path or self.DEFAULT_MUSESCORE_PATH
        self.dpi = target_dpi if target_dpi is not None else dpi

    def is_available(self) -> bool:
        return os.path.exists(self.musescore_path)

    def render_musicxml_to_images(
        self,
        musicxml_path: str,
        output_dir: str,
        score_id: str | None = None,
    ) -> list[str]:
        """Renders canonical MusicXML into a sequence of production PNG page images."""
        if not os.path.exists(musicxml_path):
            raise FileNotFoundError(f"MusicXML file not found: {musicxml_path}")
        if not self.is_available():
            raise RuntimeError(f"MUSESCORE_NOT_AVAILABLE: MuseScore executable not found at {self.musescore_path}")

        os.makedirs(output_dir, exist_ok=True)
        inferred_id = score_id or os.path.basename(musicxml_path).replace(".musicxml", "")
        base_out_png = os.path.join(output_dir, f"{inferred_id}.png")

        cmd = [self.musescore_path, os.path.abspath(musicxml_path), "-o", os.path.abspath(base_out_png)]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"MuseScore rendering execution failed: {res.stderr}")

        # MuseScore multi-page files are named {inferred_id}-1.png, {inferred_id}-2.png etc.
        # or {inferred_id}.png if single page.
        rendered_pages: list[str] = []
        if os.path.exists(base_out_png):
            rendered_pages.append(base_out_png)
        else:
            page_pattern = os.path.join(output_dir, f"{inferred_id}-*.png")
            found_pages = sorted(glob.glob(page_pattern))
            rendered_pages.extend(found_pages)

        if not rendered_pages:
            raise RuntimeError(f"MuseScore finished with exit code 0 but no output PNG files were generated for {musicxml_path}")

        return rendered_pages


class MatplotlibDiagnosticRenderer:
    """Non-authoritative diagnostic / test fixture renderer for lightweight isolated unit testing."""

    RENDERER_NAME = "MatplotlibDiagnosticRenderer"
    RENDERER_VERSION = "2.0.0-rc013"

    def __init__(self, target_dpi: int = 150) -> None:
        self.target_dpi = target_dpi

    def render_musicxml_to_images(
        self,
        musicxml_path: str,
        output_dir: str,
        score_id: str | None = None,
    ) -> list[str]:
        """Renders MusicXML into an approximate sequence of score sketch pages for test fixtures."""
        if not os.path.exists(musicxml_path):
            raise FileNotFoundError(f"MusicXML file not found: {musicxml_path}")

        os.makedirs(output_dir, exist_ok=True)
        inferred_id = score_id or os.path.basename(musicxml_path).replace(".musicxml", "")

        graph = extract_event_graph_from_musicxml(musicxml_path, score_id=inferred_id)
        total_m = max(graph.total_measures, 1)

        measures_per_system = 4
        systems_per_page = 5
        measures_per_page = measures_per_system * systems_per_page
        num_pages = max(1, (total_m + measures_per_page - 1) // measures_per_page)

        output_paths: list[str] = []

        for p_idx in range(num_pages):
            fig = plt.figure(figsize=(8.27, 11.69), dpi=self.target_dpi)
            ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
            ax.set_xlim(0, 1000)
            ax.set_ylim(1400, 0)
            ax.axis("off")
            ax.fill_between([0, 1000], 0, 1400, color="white")

            start_m = p_idx * measures_per_page + 1

            for s_idx in range(systems_per_page):
                sys_start_m = start_m + s_idx * measures_per_system
                if sys_start_m > total_m:
                    break
                sys_end_m = min(sys_start_m + measures_per_system - 1, total_m)
                y_top = 180 + s_idx * 230

                for l_idx in range(5):
                    ax.plot([80, 920], [y_top + l_idx * 12, y_top + l_idx * 12], color="black", lw=1.2)
                    ax.plot([80, 920], [y_top + 90 + l_idx * 12, y_top + 90 + l_idx * 12], color="black", lw=1.2)

                num_bars_sys = sys_end_m - sys_start_m + 1
                bar_width = (920 - 80) / max(num_bars_sys, 1)

                for b in range(num_bars_sys + 1):
                    x_b = 80 + b * bar_width
                    ax.plot([x_b, x_b], [y_top, y_top + 90 + 4 * 12], color="black", lw=1.2)

                for m_offset, m_num in enumerate(range(sys_start_m, sys_end_m + 1)):
                    m_events = graph.get_measure_events(m_num)
                    m_x_start = 80 + m_offset * bar_width

                    for evt in m_events:
                        if evt.event_type == "BARLINE":
                            continue
                        import fractions
                        onset_f = float(fractions.Fraction(evt.onset_fraction))
                        x_note = m_x_start + 25 + onset_f * (bar_width - 40)

                        if evt.is_rest:
                            y_rest = y_top + (24 if evt.staff == 1 else 114)
                            ax.plot([x_note - 4, x_note + 4], [y_rest, y_rest], color="black", lw=3.0)
                        else:
                            base_y = y_top if evt.staff == 1 else y_top + 90
                            step_idx = ["C", "D", "E", "F", "G", "A", "B"].index(evt.pitch_step or "C")
                            octave = evt.octave or 4
                            pitch_semi = (octave - 4) * 7 + step_idx
                            y_note = base_y + 48 - pitch_semi * 6

                            circle = mpatches.Circle((x_note, y_note), 5.5, color="black")
                            ax.add_patch(circle)
                            ax.plot([x_note + 5.0, x_note + 5.0], [y_note, y_note - 32], color="black", lw=1.4)

            out_p = os.path.join(output_dir, f"{inferred_id}_rendered_p{p_idx + 1}.png")
            fig.savefig(out_p, dpi=self.target_dpi, bbox_inches="tight", pad_inches=0)
            plt.close(fig)
            output_paths.append(out_p)

        return output_paths


# Backward compatibility alias
DeterministicScoreRenderer = MuseScoreProductionScoreRenderer
