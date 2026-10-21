"""One-off: turn the upstream variable fonts into the static instances used by render.py.

Sources (SIL Open Font License, see OFL-*.txt next to this file), from github.com/google/fonts:
  ofl/archivo/Archivo[wdth,wght].ttf
  ofl/instrumentserif/InstrumentSerif-Italic.ttf
  ofl/geistmono/GeistMono[wght].ttf
  ofl/inter/Inter[opsz,wght].ttf

Usage: python build_fonts.py <dir with the downloaded files>
"""
import shutil
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

SRC = Path(sys.argv[1])
OUT = Path(__file__).parent

INSTANCES = {
    "archivo-wide-800.ttf": ("Archivo[wdth,wght].ttf", {"wght": 800, "wdth": 125}),
    "archivo-112-620.ttf": ("Archivo[wdth,wght].ttf", {"wght": 620, "wdth": 112}),
    "geist-mono-500.ttf": ("GeistMono[wght].ttf", {"wght": 500}),
    "geist-mono-400.ttf": ("GeistMono[wght].ttf", {"wght": 400}),
    "inter-400.ttf": ("Inter[opsz,wght].ttf", {"wght": 400, "opsz": 14}),
    "inter-500.ttf": ("Inter[opsz,wght].ttf", {"wght": 500, "opsz": 14}),
}

for name, (src, axes) in INSTANCES.items():
    font = instancer.instantiateVariableFont(TTFont(SRC / src), axes)
    font.save(OUT / name)
    print("wrote", name)

shutil.copy(SRC / "InstrumentSerif-Italic.ttf", OUT / "instrument-serif-italic.ttf")
print("wrote instrument-serif-italic.ttf")
