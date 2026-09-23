"""Deterministic Symbolic MusicXML Score Renderer for RC-013 Channel C Alignment.

Renders MusicXML files into high-resolution, normalized score page images for structural
cross-correlation against historical source scans.
"""

from __future__ import annotations

import hashlib
import os

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


class DeterministicScoreRenderer:
    """Renders canonical MusicXML into standardized raster images for image alignment."""

    RENDERER_NAME = "DeterministicMatplotlibNotationRenderer"
    RENDERER_VERSION = "2.0.0-rc013"

    def __init__(self, target_dpi: int = 300, page_width: int = 2480, page_height: int = 3508) -> None:
        self.target_dpi = target_dpi
        self.page_width = page_width
        self.page_height = page_height

    def render_musicxml_to_images(
        self,
        musicxml_path: str,
        output_dir: str,
        score_id: str | None = None,
    ) -> list[str]:
        """Renders MusicXML into a sequence of normalized PNG score pages."""
        if not os.path.exists(musicxml_path):
            raise FileNotFoundError(f"MusicXML file not found: {musicxml_path}")

        os.makedirs(output_dir, exist_ok=True)
        inferred_id = score_id or os.path.basename(musicxml_path).replace(".musicxml", "")

        # Extract event graph to guide deterministic layout
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
            ax.set_ylim(1400, 0)  # Inverted Y for sheet music
            ax.axis("off")

            # Background: pure white for rendered symbolic score
            ax.fill_between([0, 1000], 0, 1400, color="white")

            start_m = p_idx * measures_per_page + 1

            for s_idx in range(systems_per_page):
                sys_start_m = start_m + s_idx * measures_per_system
                if sys_start_m > total_m:
                    break
                sys_end_m = min(sys_start_m + measures_per_system - 1, total_m)

                y_top = 180 + s_idx * 230
                # Draw 5 lines for Treble staff
                for l_idx in range(5):
                    y_l = y_top + l_idx * 12
                    ax.plot([80, 920], [y_l, y_l], color="black", lw=1.2)

                # Draw 5 lines for Bass staff
                for l_idx in range(5):
                    y_l = y_top + 90 + l_idx * 12
                    ax.plot([80, 920], [y_l, y_l], color="black", lw=1.2)

                # Barlines
                num_bars_sys = sys_end_m - sys_start_m + 1
                bar_width = (920 - 80) / max(num_bars_sys, 1)

                for b in range(num_bars_sys + 1):
                    x_b = 80 + b * bar_width
                    ax.plot([x_b, x_b], [y_top, y_top + 90 + 4 * 12], color="black", lw=1.2)

                # Render events in this system
                for m_offset, m_num in enumerate(range(sys_start_m, sys_end_m + 1)):
                    m_events = graph.get_measure_events(m_num)
                    m_x_start = 80 + m_offset * bar_width

                    for evt in m_events:
                        if evt.event_type == "BARLINE":
                            continue

                        # Approximate note position
                        import fractions
                        onset_f = float(fractions.Fraction(evt.onset_fraction))
                        x_note = m_x_start + 25 + onset_f * (bar_width - 40)

                        if evt.is_rest:
                            # Draw rest symbol
                            y_rest = y_top + (24 if evt.staff == 1 else 114)
                            ax.plot([x_note - 4, x_note + 4], [y_rest, y_rest], color="black", lw=3.0)
                        else:
                            # Calculate Y based on pitch step and octave
                            base_y = y_top if evt.staff == 1 else y_top + 90
                            # Octave/step offset
                            step_idx = ["C", "D", "E", "F", "G", "A", "B"].index(evt.pitch_step or "C")
                            octave = evt.octave or 4
                            pitch_semi = (octave - 4) * 7 + step_idx
                            y_note = base_y + 48 - pitch_semi * 6

                            # Notehead ellipse
                            circle = mpatches.Circle((x_note, y_note), 5.5, color="black")
                            ax.add_patch(circle)
                            # Stem
                            ax.plot([x_note + 5.0, x_note + 5.0], [y_note, y_note - 32], color="black", lw=1.4)

            out_p = os.path.join(output_dir, f"{inferred_id}_rendered_p{p_idx + 1}.png")
            fig.savefig(out_p, dpi=self.target_dpi, bbox_inches="tight", pad_inches=0)
            plt.close(fig)
            output_paths.append(out_p)

        return output_paths
