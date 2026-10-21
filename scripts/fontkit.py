"""Subset and inline fonts into a finished SVG.

Each SVG only carries the glyphs it actually draws, as base64 WOFF2 inside
@font-face rules, so it renders the same everywhere with no network access.
"""
import base64
import html
import io
import re
from functools import lru_cache
from pathlib import Path

from fontTools import subset

FONT_DIR = Path(__file__).parent / "fonts"

# css class -> (family name used in CSS, file, weight, style)
FACES = {
    "fw": ("AWide", "archivo-wide-800.ttf", 800, "normal"),
    "fh": ("AHead", "archivo-112-620.ttf", 620, "normal"),
    "fs": ("ISerif", "instrument-serif-italic.ttf", 400, "italic"),
    "fm": ("GMono", "geist-mono-500.ttf", 500, "normal"),
    "fc": ("GCode", "geist-mono-400.ttf", 400, "normal"),
    "fb": ("IText", "inter-400.ttf", 400, "normal"),
    "fbm": ("ITextM", "inter-500.ttf", 500, "normal"),
}

TEXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.S)
TAG_RE = re.compile(r"<[^>]+>")


def used_text(svg: str) -> str:
    chars = set(" ")
    for inner in TEXT_RE.findall(svg):
        chars.update(html.unescape(TAG_RE.sub("", inner)))
    return "".join(sorted(chars))


@lru_cache(maxsize=None)
def woff2_b64(filename: str, text: str) -> str:
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.hinting = False
    opts.desubroutinize = True
    opts.layout_features = ["kern", "liga", "calt", "case"]
    opts.name_IDs = [1, 2]
    opts.recalc_timestamp = False
    opts.drop_tables += ["meta", "DSIG"]
    font = subset.load_font(str(FONT_DIR / filename), opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    subset.save_font(font, buf, opts)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def embed(svg: str) -> str:
    """Replace the /*FONTS*/ marker with @font-face rules for the classes in use."""
    text = used_text(svg)
    rules = []
    for cls, (family, filename, weight, style) in FACES.items():
        if not re.search(rf'class="(?:[^"]*\s)?{cls}(?:\s[^"]*)?"', svg):
            continue
        data = woff2_b64(filename, text)
        rules.append(
            f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{data}) format('woff2');"
            f"font-weight:{weight};font-style:{style};font-display:block}}"
        )
    return svg.replace("/*FONTS*/", "".join(rules), 1)
