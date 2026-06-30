"""
Exports all dysonsphere palettes as Illustrator swatch files to scripts/illustrator/:
  - import_dysonsphere_palettes_to_illustrator.jsx  (run in Illustrator to load into active doc)
  - dysonsphere.ase  (persistent swatch library; auto-installed to Illustrator User Defined folder)

Usage (from project root):
    uv run python scripts/illustrator/export_swatches_to_illustrator.py
"""

from pathlib import Path

from dysonsphere.palettes import export_swatches

export_swatches(Path(__file__).resolve().parent)
