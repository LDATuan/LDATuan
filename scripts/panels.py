"""Panel builders for the profile README.

Every function returns SVG markup drawn with the active theme (see `use`).
Motion is CSS keyframes only; GitHub strips scripts from images.
"""
import datetime as dt
import random
import textwrap

LIGHT = dict(
    name="light", bg="#f2f1ee", raised="#faf9f7", sunk="#e9e8e4", paper="#ffffff", concrete="#ebe9e3",
    ink="#101014", strong="#000000", muted="rgba(16,16,20,.62)", faint="rgba(16,16,20,.42)",
    line="rgba(16,16,20,.16)", acc="#2d81ff", screen="#101014", shadow=".16",
)
DARK = dict(
    name="dark", bg="#101014", raised="#16161b", sunk="#1c1c22", paper="#24242b", concrete="#2a2a31",
    ink="#f2f1ee", strong="#ffffff", muted="rgba(242,241,238,.64)", faint="rgba(242,241,238,.42)",
    line="rgba(242,241,238,.14)", acc="#5aa0ff", screen="#1c1c23", shadow=".55",
)
T = dict(LIGHT)
FIX_ACC = "#2d81ff"  # accent inside scenes that look the same in both themes


def use(theme):
    T.clear()
    T.update(theme)


BASE_CSS = """/*FONTS*/
.fw{font-family:AWide,Archivo,system-ui,sans-serif;font-weight:800}
.fh{font-family:AHead,Archivo,system-ui,sans-serif;font-weight:620}
.fs{font-family:ISerif,'Instrument Serif',Georgia,serif;font-style:italic;font-weight:400}
.fm{font-family:GMono,'Geist Mono',ui-monospace,Menlo,monospace;font-weight:500;letter-spacing:.15em}
.fc{font-family:GCode,'Geist Mono',ui-monospace,Menlo,monospace;font-weight:400;letter-spacing:0}
.fb{font-family:IText,Inter,system-ui,-apple-system,sans-serif;font-weight:400}
.fbm{font-family:ITextM,Inter,system-ui,-apple-system,sans-serif;font-weight:500}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

SECTIONS = ["WORK", "JOURNEY", "WRITING", "ACTIVITY", "CONTACT"]


# ------------------------------------------------------------------ helpers
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(s, p):
    """Swap the § placeholder for a prefix, so ids and keyframes stay unique."""
    return s.replace("§", p + "-")


def svg(w, h, body, css="", label="", viewbox=None):
    vb = viewbox or f"0 0 {w} {h}"
    x, y, vw, vh = vb.split()
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title><style>{BASE_CSS}{css}</style>"
        f'<clipPath id="root-clip"><rect x="{x}" y="{y}" width="{vw}" height="{vh}"/></clipPath>'
        f'<g clip-path="url(#root-clip)">{body}</g></svg>'
    )


def mono(x, y, s, size=9.5, fill=None, anchor="start", cls="fm", extra=""):
    fill = fill or T["faint"]
    return (
        f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{esc(s)}</text>'
    )


# The "T" monogram from ldatuan.com, drawn in a 104 x 132 box starting at (44, 30).
T_MARK = (
    "M94.31,35.49v121a1.08,1.08,0,0,1-.9,1.18H66.52a1.07,1.07,0,0,1-.9-1.18v-3.88a1.07,1.07,0,0,1,.9-1.18H76.3a1.07,1.07,0,0,0,.9-1.18V41.07c0-.76-.54-1.330-1.11-1.15A30.22,30.22,0,0,0,62,49.62C53.63,59.55,52,72.32,51.62,77a1,1,0,0,1-.9,1.06H49.43a1.08,1.08,0,0,1-.9-1.18V35.49a1.08,1.08,0,0,1,.9-1.18h44A1.08,1.08,0,0,1,94.31,35.49Z",
    "M97.69,35.49v121a1.08,1.08,0,0,0,.9,1.18h26.89a1.07,1.07,0,0,0,.9-1.18v-3.88a1.07,1.07,0,0,0-.9-1.18H115.7a1.07,1.07,0,0,1-.9-1.18V41.07c0-.76.54-1.33,1.11-1.15A30.22,30.22,0,0,1,130,49.62c8.34,9.93,10,22.7,10.35,27.42a1,1,0,0,0,.9,1.06h1.29a1.08,1.08,0,0,0,.9-1.18V35.49a1.08,1.08,0,0,0-.9-1.18h-44A1.08,1.08,0,0,0,97.69,35.49Z",
)
MOON = "M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"  # 24 x 24, stroked


def mark(x, y, h=22.0, fill=None):
    """The T monogram, h pixels tall, top-left corner at (x, y)."""
    k = h / 132
    d = "".join(f'<path d="{p}"/>' for p in T_MARK)
    return f'<g transform="translate({x},{y}) scale({k:.5f}) translate(-44,-30)" fill="{fill or T["ink"]}">{d}</g>'


def moon(cx, cy, size=15.0, stroke=None):
    k = size / 24
    return (f'<path transform="translate({cx - size / 2},{cy - size / 2}) scale({k:.4f})" d="{MOON}" fill="none" '
            f'stroke="{stroke or T["ink"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>')


def stack(blocks):
    """Stack (body, css, height) blocks vertically into one body."""
    out, css, y = [], [], 0
    for body, c, h in blocks:
        out.append(f'<g transform="translate(0,{y})">{body}</g>')
        css.append(c)
        y += h
    return "".join(out), "".join(css), y


# ------------------------------------------------------------------ hero
def _iso_box(fx, fy, a, b, h, top, left, right, edge="#dbeeff"):
    """Isometric box standing on ground corner (fx, fy): a along the right axis, b along the left."""
    ux, uy = (0.866, -0.5), (-0.866, -0.5)
    F = (fx, fy)
    Rr = (fx + a * ux[0], fy + a * ux[1])
    L = (fx + b * uy[0], fy + b * uy[1])
    B = (Rr[0] + b * uy[0], Rr[1] + b * uy[1])
    up = lambda p: (p[0], p[1] - h)
    pts = lambda *ps: " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)
    out = (
        f'<polygon points="{pts(F, L, up(L), up(F))}" fill="{left}"/>'
        f'<polygon points="{pts(F, Rr, up(Rr), up(F))}" fill="{right}"/>'
        f'<polygon points="{pts(up(F), up(Rr), up(B), up(L))}" fill="{top}"/>'
        f'<path d="M{L[0]:.1f} {L[1]-h:.1f} L{fx:.1f} {fy-h:.1f} L{Rr[0]:.1f} {Rr[1]-h:.1f} M{fx:.1f} {fy:.1f} V{fy-h:.1f}" '
        f'fill="none" stroke="{edge}" stroke-opacity=".5" stroke-width=".5"/>'
    )
    return out, F, Rr, L


def _cloud(x0, y0, x1, y1, step=4.6, r=2.5):
    """Revision cloud: scalloped rectangle, clockwise so the bumps face out."""
    pts = []
    for (ax, ay, bx, by) in [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]:
        n = max(1, round(((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5 / step))
        for i in range(1, n + 1):
            pts.append((ax + (bx - ax) * i / n, ay + (by - ay) * i / n))
    d = f"M{x0} {y0}" + "".join(f" A{r} {r} 0 0 1 {x:.1f} {y:.1f}" for x, y in pts)
    return d


def hero_cards():
    A, ink, paper = FIX_ACC, "#101014", "#fbfaf7"
    defs = (
        '<clipPath id="h-cc"><rect x="-60" y="-39" width="120" height="78" rx="10"/></clipPath>'
        '<pattern id="h-hatch" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        '<path d="M0 0 V3" stroke="#101014" stroke-opacity=".2" stroke-width=".6"/></pattern>'
        '<linearGradient id="h-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1230"/><stop offset="1" stop-color="#1c2b66"/></linearGradient>'
        '<linearGradient id="h-dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1d2540"/><stop offset=".6" stop-color="#6a5674"/><stop offset="1" stop-color="#eaa77a"/></linearGradient>'
        '<linearGradient id="h-asph" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6e6871"/><stop offset="1" stop-color="#26262b"/></linearGradient>'
        '<radialGradient id="h-sun"><stop offset="0" stop-color="#ffdcae" stop-opacity=".95"/><stop offset="1" stop-color="#ffdcae" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="h-av" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#8cc0ff"/><stop offset="1" stop-color="{A}"/></linearGradient>'
    )

    def card(bg, inner, dark=False):
        border = "rgba(255,255,255,.10)" if dark else "rgba(16,16,20,.13)"
        return (f'<rect x="-60" y="-39" width="120" height="78" rx="10" fill="{bg}"/>'
                f'<g clip-path="url(#h-cc)">{inner}</g>'
                f'<rect x="-59.5" y="-38.5" width="119" height="77" rx="9.5" fill="none" stroke="{border}"/>')

    def sparkle(cx, cy, s, fill):
        return (f'<path transform="translate({cx},{cy}) scale({s})" fill="{fill}" '
                'd="M0 -4 L1 -1 L4 0 L1 1 L0 4 L-1 1 L-4 0 L-1 -1 Z"/>')

    c = {}

    # ---- floor plan with grid, poché walls, doors, a selected room
    p = []
    for gx, lab in [(-48, "A"), (-6, "B"), (48, "C")]:
        p.append(f'<path d="M{gx} -27 V31" stroke="{ink}" stroke-opacity=".14" stroke-width=".5" stroke-dasharray="1.6 1.6"/>')
        p.append(f'<circle cx="{gx}" cy="-31" r="3.4" fill="{paper}" stroke="{ink}" stroke-opacity=".45" stroke-width=".5"/>')
        p.append(mono(gx, -29.7, lab, 3.6, "rgba(16,16,20,.6)", "middle", cls="fc"))
    p.append(f'<rect x="-5" y="-21" width="52" height="24" fill="{A}" fill-opacity=".13"/>')
    p.append(f'<rect x="-42" y="16" width="24" height="7" rx="2" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width=".5"/>')
    p.append(f'<circle cx="-27" cy="-3" r="5" fill="none" stroke="{ink}" stroke-opacity=".3" stroke-width=".5"/>')
    p.append(f'<rect x="10" y="-17" width="18" height="12" rx="1.5" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width=".5"/>'
             f'<path d="M10 -13.5 H28" stroke="{ink}" stroke-opacity=".3" stroke-width=".4"/>')
    p.append(f'<rect x="-48" y="-22" width="96" height="50" fill="none" stroke="{ink}" stroke-width="2.2"/>')
    p.append(f'<path d="M-6 -22 V-4 M-6 7 V28 M-6 4 H20 M30 4 H48" fill="none" stroke="{ink}" stroke-width="1.4"/>')
    for wx in (-38, 14, 32):
        p.append(f'<rect x="{wx}" y="-23.4" width="10" height="2.8" fill="{paper}"/>'
                 f'<path d="M{wx} -22.6 H{wx+10} M{wx} -21.4 H{wx+10}" stroke="{ink}" stroke-opacity=".7" stroke-width=".4"/>')
    p.append(f'<path d="M-6 -4 H5 A11 11 0 0 1 -6 7 M20 4 V14 A10 10 0 0 0 30 4" fill="none" stroke="{ink}" stroke-opacity=".45" stroke-width=".5"/>')
    p.append(mono(44, -16, "BED 2", 3.4, A, "end"))
    p.append(f'<path d="M-48 34 H48 M-48 32 V36 M48 32 V36" stroke="{ink}" stroke-opacity=".45" stroke-width=".5"/>'
             f'<rect x="-9" y="31.6" width="18" height="4.8" fill="{paper}"/>' + mono(0, 35.4, "9 600", 3.6, "rgba(16,16,20,.6)", "middle", cls="fc"))
    c["plan"] = card(paper, "".join(p))

    # ---- isometric tower at night
    p = [f'<rect x="-60" y="-39" width="120" height="78" fill="url(#h-night)"/>']
    for x, y in [(-50, -30), (-36, -20), (40, -32), (52, -18), (24, -26), (-20, -34)]:
        p.append(f'<circle cx="{x}" cy="{y}" r=".6" fill="#fff" fill-opacity=".7"/>')
    for k in range(-6, 7):
        p.append(f'<path d="M{-70 + k*12} 40 l60 -34" stroke="#7fa6ff" stroke-opacity=".10" stroke-width=".5"/>'
                 f'<path d="M{70 + k*12} 40 l-60 -34" stroke="#7fa6ff" stroke-opacity=".10" stroke-width=".5"/>')
    p.append('<ellipse cx="-2" cy="31" rx="40" ry="7" fill="#000" fill-opacity=".3"/>')
    tower, F, Rr, L = _iso_box(-4, 32, 24, 20, 44, "#a9dcff", "#3b82f6", "#1e4fd0")
    p.append(tower)
    lit = {(1, 2), (2, 4), (3, 1), (4, 3), (5, 2), (1, 5), (6, 4)}
    for row in range(1, 7):
        z = row * 6 + 2
        for col in range(4):
            t0 = 0.1 + col * 0.21
            for face, corner, n in (("l", L, 0), ("r", Rr, 1)):
                fill = "#ffd28a" if (row, col + 3 * n) in lit else "#bfe0ff"
                op = ".95" if fill == "#ffd28a" else ".35"
                q = []
                for (t, dz) in ((t0, 0), (t0 + .13, 0), (t0 + .13, 3), (t0, 3)):
                    x = F[0] + (corner[0] - F[0]) * t
                    y = F[1] + (corner[1] - F[1]) * t - z - dz
                    q.append(f"{x:.1f},{y:.1f}")
                p.append(f'<polygon points="{" ".join(q)}" fill="{fill}" fill-opacity="{op}"/>')
    wing, *_ = _iso_box(20, 35, 20, 14, 12, "#c7e6ff", "#5b9bff", "#2a5fe0")
    p.append(wing)
    c["iso"] = card("#0a1230", "".join(p), dark=True)

    # ---- code editor
    p = ['<rect x="-60" y="-39" width="120" height="12" fill="#1d1e27"/>']
    for x, col in [(-51, "#ff5f57"), (-45.5, "#febc2e"), (-40, "#28c840")]:
        p.append(f'<circle cx="{x}" cy="-33" r="1.8" fill="{col}"/>')
    p.append('<rect x="-33" y="-37" width="34" height="10" rx="2" fill="#15161d"/>')
    p.append('<text class="fb" x="-29" y="-30.4" font-size="4" fill="#c0c3d0">Command.cs</text>')
    lines = [
        (0, [(10, "#bb9af7"), (18, "#e0e0e6"), (14, "#7dcfff")]),
        (0, [(12, "#bb9af7"), (22, "#7aa2f7")]),
        (6, [(8, "#bb9af7"), (16, "#e0e0e6"), (20, "#9ece6a")]),
        (6, [(14, "#7aa2f7"), (10, "#e0af68"), (8, "#e0e0e6")]),
        (12, [(18, "#7aa2f7"), (12, "#ff9e64")]),
        (6, [(10, "#bb9af7"), (16, "#7dcfff")]),
        (0, [(4, "#e0e0e6")]),
    ]
    for i, (ind, segs) in enumerate(lines):
        y = -19 + i * 7.6
        if i == 3:
            p.append(f'<rect x="-60" y="{y-4.2}" width="120" height="6.6" fill="#fff" fill-opacity=".05"/>')
        p.append(mono(-48, y + 1.1, str(i + 1), 3.4, "#454756", "end", cls="fc"))
        x = -43 + ind
        for w, col in segs:
            p.append(f'<rect x="{x}" y="{y-1.3}" width="{w}" height="2.6" rx="1.3" fill="{col}" fill-opacity=".92"/>')
            x += w + 2
        if i == 3:
            p.append(f'<rect x="{x}" y="{y-2.6}" width=".9" height="5.2" fill="{A}"/>')
    for i in range(10):
        p.append(f'<rect x="49" y="{-24 + i*5.6}" width="{[6,8,5,7,4,8,6,3,7,5][i]}" height="1.6" fill="#fff" fill-opacity=".14"/>')
    c["code"] = card("#15161d", "".join(p), dark=True)

    # ---- agent chat
    p = [f'<circle cx="-48" cy="-28" r="5" fill="url(#h-av)"/>' + sparkle(-48, -28, .7, "#fff")]
    p.append('<text class="fb" x="-40" y="-26.4" font-size="4.6" fill="#e4e4e7">Revit agent</text>')
    p.append('<circle cx="-13" cy="-28" r="1.4" fill="#34d399"/>')
    p.append('<path d="M-60 -19.5 H60" stroke="#fff" stroke-opacity=".07"/>')
    p.append(f'<rect x="2" y="-15" width="52" height="14" rx="6" fill="{A}"/>'
             '<rect x="8" y="-10.8" width="34" height="2.4" rx="1.2" fill="#fff" fill-opacity=".92"/>'
             '<rect x="8" y="-6.2" width="22" height="2.4" rx="1.2" fill="#fff" fill-opacity=".7"/>')
    p.append('<rect x="-54" y="3" width="66" height="22" rx="6" fill="#23232d"/>' + sparkle(-48.5, 8.5, .55, "#9cc2ff"))
    p.append('<rect x="-43" y="7.3" width="44" height="2.4" rx="1.2" fill="#d4d4d8"/>'
             '<rect x="-43" y="12" width="34" height="2.4" rx="1.2" fill="#8b8b96"/>')
    p.append(f'<rect x="-43" y="16.6" width="24" height="6" rx="3" fill="none" stroke="{A}" stroke-width=".7"/>'
             + mono(-31, 20.8, "37 WALLS", 3, "#9cc2ff", "middle"))
    p.append('<rect x="-54" y="28.5" width="96" height="7" rx="3.5" fill="#1b1b23" stroke="#2e2e38" stroke-width=".5"/>'
             '<rect x="-49" y="31.3" width="28" height="1.6" rx=".8" fill="#4a4a56"/>')
    p.append(f'<circle cx="49" cy="32" r="4.2" fill="{A}"/><path d="M47 32 h4 m-1.6 -1.6 l1.6 1.6 l-1.6 1.6" fill="none" stroke="#fff" stroke-width=".7"/>')
    c["chat"] = card("#121219", "".join(p), dark=True)

    # ---- beam section with rebar
    p = ['<rect x="-30" y="-30" width="40" height="62" fill="#ebe9e3"/><rect x="-30" y="-30" width="40" height="62" fill="url(#h-hatch)"/>']
    p.append(f'<rect x="-30" y="-30" width="40" height="62" fill="none" stroke="{ink}" stroke-opacity=".8" stroke-width="1"/>')
    p.append(f'<rect x="-25.5" y="-25.5" width="31" height="53" rx="3" fill="none" stroke="{A}" stroke-width="1.1"/>'
             f'<path d="M-21.5 -25.5 l4 4 M-25.5 -21.5 l4 4" stroke="{A}" stroke-width=".9"/>')
    for x in (-19, -10, -1):
        p.append(f'<circle cx="{x}" cy="-19.5" r="2.8" fill="{ink}"/><circle cx="{x-.8}" cy="-20.3" r=".8" fill="#fff" fill-opacity=".45"/>')
    for x in (-20.5, -13.2, -5.9, 1.4):
        p.append(f'<circle cx="{x}" cy="22.5" r="3.1" fill="{ink}"/><circle cx="{x-.9}" cy="21.6" r=".9" fill="#fff" fill-opacity=".45"/>')
    p.append(f'<path d="M16 -30 V32 M13.5 -30 H18.5 M13.5 32 H18.5" stroke="{ink}" stroke-opacity=".45" stroke-width=".5"/>'
             f'<rect x="13.6" y="-1" width="4.8" height="9" fill="{paper}"/>' + mono(16, 1.4, "600", 3.4, "rgba(16,16,20,.6)", "middle", cls="fc",
                                                                                      extra='transform="rotate(90 16 1.4)"'))
    p.append(f'<path d="M-1 -19.5 L26 -27 H54 M1.4 22.5 L26 30 H54 M5.5 2 H54" fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width=".5"/>')
    p.append(mono(27, -28.6, "3Ø20", 4, ink, cls="fc") + mono(27, 28.4, "4Ø25", 4, ink, cls="fc") + mono(27, .6, "Ø10@150", 3.6, A, cls="fc"))
    c["rebar"] = card(paper, "".join(p))

    # ---- wall schedule with fire ratings
    p = [f'<text class="fb" x="-52" y="-26.6" font-size="4.8" fill="{ink}">Wall schedule</text>']
    p.append(f'<rect x="26" y="-31.4" width="26" height="7" rx="3.5" fill="{A}" fill-opacity=".14"/>' + mono(39, -26.8, "1 240", 3.4, A, "middle", cls="fc"))
    p.append('<rect x="-54" y="-21" width="108" height="8" rx="2" fill="#ecebe6"/>')
    for x, lab in [(-50, "MARK"), (-28, "TYPE"), (6, "LEVEL"), (30, "FIRE")]:
        p.append(mono(x, -15.8, lab, 3.1, "rgba(16,16,20,.55)"))
    status = ["2H", "2H", None, "1H", None]
    widths = [24, 30, 20, 28, 22]
    for i in range(5):
        y = -7.5 + i * 8.4
        p.append(mono(-50, y + 1.3, f"W-0{i+1}", 3.5, "rgba(16,16,20,.75)", cls="fc"))
        p.append(f'<rect x="-28" y="{y-1.2}" width="{widths[i]}" height="2.4" rx="1.2" fill="{ink}" fill-opacity=".2"/>')
        p.append(mono(6, y + 1.3, "L2", 3.5, "rgba(16,16,20,.75)", cls="fc"))
        if status[i]:
            p.append(f'<rect x="30" y="{y-2.6}" width="14" height="5.2" rx="2.6" fill="#16a34a" fill-opacity=".14"/>'
                     + mono(37, y + 1.1, status[i], 3.2, "#15803d", "middle", cls="fc"))
        else:
            p.append(f'<rect x="30" y="{y-2.6}" width="18" height="5.2" rx="2.6" fill="#f59e0b" fill-opacity=".18"/>'
                     + mono(39, y + 1.1, "NONE", 3, "#b45309", "middle"))
        p.append(f'<path d="M-54 {y+4.2} H54" stroke="{ink}" stroke-opacity=".08" stroke-width=".5"/>')
    c["table"] = card(paper, "".join(p))

    # ---- dashcam frame with a detected pothole
    p = ['<rect x="-60" y="-39" width="120" height="29" fill="url(#h-dusk)"/>',
         '<circle cx="4" cy="-11" r="17" fill="url(#h-sun)"/><circle cx="4" cy="-12" r="3.2" fill="#ffe8c8"/>']
    for x, w, h in [(-60, 10, 10), (-50, 8, 15), (-42, 12, 8), (-30, 7, 13), (-23, 10, 6), (14, 9, 9), (23, 7, 16), (30, 12, 11), (42, 8, 7), (50, 12, 13)]:
        p.append(f'<rect x="{x}" y="{-10-h}" width="{w}" height="{h}" fill="#262a3b"/>')
    p.append('<rect x="-60" y="-10" width="120" height="49" fill="#3a3440"/>')
    p.append('<polygon points="2,-10 6,-10 72,39 -64,39" fill="url(#h-asph)"/>')
    p.append('<path d="M2.5 -10 L-60 39 M5.5 -10 L68 39" stroke="#efe7dc" stroke-opacity=".55" stroke-width=".6"/>')
    for q in ["3.6,-6 4.4,-6 4.9,-2 3.1,-2", "2.9,2 5.1,2 5.8,9 2.2,9", "1.6,15 6.4,15 7.6,27 .4,27"]:
        p.append(f'<polygon points="{q}" fill="#f2ece2" fill-opacity=".85"/>')
    p.append('<ellipse cx="-16" cy="20" rx="13" ry="4" fill="#141417"/><ellipse cx="-17" cy="19.4" rx="8" ry="2" fill="#3a3f55" fill-opacity=".7"/>')
    p.append(f'<rect x="-32" y="13" width="32" height="13" fill="{A}" fill-opacity=".1"/>'
             f'<path d="M-32 17 v-4 h4 M-4 13 h4 v4 M-32 22 v4 h4 M-4 26 h4 v-4" fill="none" stroke="{A}" stroke-width="1.1"/>'
             f'<rect x="-32" y="6.6" width="33" height="6" fill="{A}"/>' + mono(-30.6, 10.9, "POTHOLE .94", 3.3, "#fff"))
    p.append('<path d="M-54 -27 v-6 h6 M48 -33 h6 v6 M-54 27 v6 h6 M48 33 h6 v-6" fill="none" stroke="#fff" stroke-opacity=".6" stroke-width=".7"/>')
    p.append('<circle cx="-47" cy="-28.6" r="1.5" fill="#ff5a5a"/>' + mono(-44, -27.4, "REC", 3.3, "rgba(255,255,255,.85)"))
    c["pot"] = card("#3a3440", "".join(p), dark=True)

    # ---- drawing sheet with title block and revision cloud
    p = [f'<rect x="-55" y="-34" width="110" height="68" fill="none" stroke="{ink}" stroke-opacity=".45" stroke-width=".6"/>',
         f'<rect x="-52" y="-31" width="104" height="62" fill="none" stroke="{ink}" stroke-opacity=".22" stroke-width=".4"/>']
    p.append(f'<rect x="-46" y="-24" width="58" height="40" fill="none" stroke="{ink}" stroke-opacity=".8" stroke-width="1.6"/>')
    p.append(f'<path d="M-20 -24 V-6 M-20 3 V16 M-20 -2 H12 M-46 4 H-34" fill="none" stroke="{ink}" stroke-opacity=".75" stroke-width=".9"/>')
    p.append(f'<path d="M-20 -6 H-12 A8 8 0 0 1 -20 3" fill="none" stroke="{ink}" stroke-opacity=".4" stroke-width=".4"/>')
    p.append(f'<path d="{_cloud(-6, -21, 9, -5)}" fill="none" stroke="{A}" stroke-width=".7"/>')
    p.append(f'<path d="M15 -26 l4 7 h-8 z" fill="#fff" stroke="{A}" stroke-width=".7"/>' + mono(15, -20.4, "1", 3.4, A, "middle", cls="fc"))
    p.append(f'<circle cx="35" cy="-17" r="5" fill="none" stroke="{ink}" stroke-opacity=".4" stroke-width=".5"/>'
             f'<path d="M35 -21.5 l2 7 l-2 -1.6 l-2 1.6 z" fill="{ink}" fill-opacity=".7"/>' + mono(35, -23.4, "N", 2.8, "rgba(16,16,20,.6)", "middle", cls="fc"))
    p.append(f'<rect x="18" y="8" width="34" height="23" fill="none" stroke="{ink}" stroke-opacity=".45" stroke-width=".5"/>'
             f'<path d="M18 16 H52 M18 23 H52 M35 23 V31" stroke="{ink}" stroke-opacity=".3" stroke-width=".4"/>')
    p.append(mono(20, 13.6, "PROJECT", 2.8, "rgba(16,16,20,.5)") +
             f'<text class="fh" x="20" y="21.4" font-size="4.4" fill="{ink}">A-201</text>' +
             mono(20, 28.6, "1:100", 3, "rgba(16,16,20,.6)", cls="fc") + mono(37, 28.6, "REV 1", 3, A, cls="fc"))
    c["sheet"] = card("#ffffff", "".join(p))

    return defs + "".join(f'<g id="h-{k}">{v}</g>' for k, v in c.items())


def ticker():
    items = ["REVIT API", "C# / WPF", "AUTODESK PLATFORM SERVICES", "DYNAMO", "MCP", "AI AGENTS",
             "NEXT.JS", "PYTHON", "YOLOV6", "SPECKLE", "IFC"]
    cw = 10 * 0.75
    x, parts = 0, []
    for it in items:
        parts.append(f'<circle cx="{x+3}" cy="18" r="2" fill="{T["acc"]}"/>')
        x += 18
        parts.append(mono(x, 21.5, it, 10, T["muted"]))
        x += len(it) * cw + 30
    W = int(x)
    seq = "".join(parts)
    css = ".t-run{animation:t-run 48s linear infinite}@keyframes t-run{to{transform:translateX(-%dpx)}}" % W
    body = (
        f'<rect width="880" height="36" fill="{T["bg"]}"/>'
        f'<g class="t-run"><g transform="translate(14,0)">{seq}</g><g transform="translate({14+W},0)">{seq}</g></g>'
        f'<path d="M0 .5 H880 M0 35.5 H880" stroke="{T["line"]}"/>'
    )
    return body, css, 36


def hero():
    W, H = 880, 600
    css = """
.h-o1{offset-path:path('M440,0 A400,300 0 1,1 440,600 A400,300 0 1,1 440,0');offset-rotate:0deg;animation:h-orb 84s linear infinite}
.h-o2{offset-path:path('M440,-72 A470,372 0 1,1 440,672 A470,372 0 1,1 440,-72');offset-rotate:0deg;animation:h-orb 126s linear infinite reverse}
@keyframes h-orb{from{offset-distance:0%}to{offset-distance:100%}}
.h-dash{animation:h-dash 22s linear infinite}
@keyframes h-dash{to{stroke-dashoffset:-512}}
.h-rise{animation:h-rise 1.1s cubic-bezier(.2,.8,.2,1) .15s both}
@keyframes h-rise{from{transform:translateY(100px)}}
.h-up{animation:h-up .9s cubic-bezier(.2,.8,.2,1) both}
@keyframes h-up{from{opacity:0;transform:translateY(12px)}}
.h-mk{animation:h-mk 24s ease-in-out infinite alternate}
@keyframes h-mk{from{transform:translateY(0)}to{transform:translateY(460px)}}
.h-cards{animation:h-fade 1.6s ease .9s both}
@keyframes h-fade{from{opacity:0}}
"""
    bg, ink, line = T["bg"], T["ink"], T["line"]
    b = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    b.append(
        "<defs>"
        f'<filter id="h-sh" x="-40%" y="-40%" width="180%" height="200%"><feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" flood-opacity="{T["shadow"]}"/></filter>'
        f'<filter id="h-sh2" x="-40%" y="-40%" width="180%" height="200%"><feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#000" flood-opacity="{float(T["shadow"]) * .7:.2f}"/></filter>'
        ''
        f'<linearGradient id="h-fr" x1="0" x2="1"><stop offset="0" stop-color="{bg}" stop-opacity="0"/><stop offset="1" stop-color="{bg}" stop-opacity=".92"/></linearGradient>'
        '<clipPath id="h-wm"><rect x="0" y="104" width="880" height="106"/></clipPath>'
        + hero_cards() + "</defs>"
    )
    for rx, ry in [(250, 197), (400, 300), (470, 372), (600, 474), (740, 585)]:
        b.append(f'<ellipse cx="440" cy="300" rx="{rx}" ry="{ry}" fill="none" stroke="{ink}" stroke-opacity=".08"/>')
    b.append(f'<ellipse class="h-dash" cx="440" cy="300" rx="400" ry="300" fill="none" stroke="{T["acc"]}" stroke-opacity=".35" stroke-dasharray="2 14"/>')

    b.append('<g class="h-cards">')
    for i, k in enumerate(["sheet", "pot", "table", "plan", "chat", "rebar"]):
        b.append(f'<g class="h-o2" style="offset-distance:{(1 - i / 6) * 100:.2f}%;animation-delay:-{i*21}s"><use href="#h-{k}" transform="scale(.78)" filter="url(#h-sh2)"/></g>')
    for i, k in enumerate(["plan", "code", "rebar", "chat", "iso", "table", "pot"]):
        b.append(f'<g class="h-o1" style="offset-distance:{i*100/7:.2f}%;animation-delay:-{i*12}s"><use href="#h-{k}" filter="url(#h-sh)"/></g>')
    b.append("</g>")
    b.append(f'<rect x="812" y="0" width="34" height="600" fill="url(#h-fr)"/><rect x="846" y="0" width="34" height="600" fill="{bg}" fill-opacity=".92"/>')

    b.append(
        '<g clip-path="url(#h-wm)"><g class="h-rise">'
        f'<text class="fw" x="440" y="196" font-size="92" text-anchor="middle" fill="{T["strong"]}" letter-spacing="-2">LDATUAN</text>'
        "</g></g>"
    )
    b.append(
        '<g class="h-up" style="animation-delay:.55s"><text x="440" y="262" text-anchor="middle">'
        f'<tspan class="fh" font-size="32" fill="{T["strong"]}" letter-spacing="-1">Software </tspan>'
        f'<tspan class="fs" font-size="36" fill="{T["muted"]}">for buildings.</tspan></text></g>'
    )
    b.append(
        f'<g class="h-up" style="animation-delay:.7s"><text class="fb" x="440" y="300" font-size="15" fill="{T["muted"]}" text-anchor="middle">'
        "Civil engineer turned software engineer. I build Revit add-ins,</text>"
        f'<text class="fb" x="440" y="322" font-size="15" fill="{T["muted"]}" text-anchor="middle">'
        "move model data onto the web, and teach agents the boring parts.</text></g>"
    )
    b.append(
        '<g class="h-up" style="animation-delay:.85s">'
        f'<rect x="365" y="346" width="150" height="38" fill="{ink}"/>'
        f'<g fill="none" stroke="{bg}" stroke-width="1.1"><rect x="382" y="358" width="9" height="12" rx="1"/><path d="M384.5 362 H388.5 M384.5 365 H388.5"/></g>'
        + mono(400, 368.5, "LDATUAN.COM", 10, bg)
        + "</g>"
    )
    b.append(
        '<g class="h-up" style="animation-delay:1s">'
        + mono(197, 424, "OPEN SOURCE ON GITHUB", 9) + mono(386, 424, "REVIT · AUTOCAD · WEB", 9) + mono(575, 424, "SINGAPORE · UTC+8", 9)
        + "</g>"
    )
    r = []
    for y in range(60, 600, 10):
        long_ = (y - 60) % 50 == 0
        r.append(f'<path d="M{870 if long_ else 875} {y} H880" stroke="{ink}" stroke-opacity="{.45 if long_ else .25}"/>')
        if long_:
            r.append(mono(864, y + 2.5, str((y - 60) // 10), 7, T["faint"], "end", "fc"))
    b.append("".join(r))
    b.append(f'<g class="h-mk"><path d="M838 88 H880" stroke="{T["acc"]}"/>' + mono(866, 84, "012 %", 6.5, T["acc"], "end", "fc") + "</g>")

    n = [f'<rect width="{W}" height="44" fill="{bg}"/><path d="M0 44.5 H880" stroke="{line}"/>', mark(26 - 104 * 22 / 132 / 2, 11, 22)]
    n.append(f'<path d="M52.5 0 V44" stroke="{line}"/>')
    n.append(f'<rect x="62" y="13" width="44" height="18" fill="{ink}"/>' + mono(68, 25.5, "HOME", 9.5, bg))
    for x, s in [(124, "WORK"), (176, "JOURNEY"), (250, "WRITING"), (324, "ACTIVITY"), (405, "CONTACT")]:
        n.append(mono(x, 25.5, s, 9.5, T["muted"]))
    n.append(f'<path d="M548.5 0 V44 M710.5 0 V44 M756.5 0 V44" stroke="{line}"/>')
    n.append(mono(566, 25.5, "GITHUB", 9.5, T["muted"]) + mono(633, 25.5, "LINKEDIN", 9.5, T["muted"]))
    n.append(moon(733.5, 22, 15, ink))
    n.append(f'<rect x="756" y="0" width="124" height="44" fill="{ink}"/>' + mono(818, 25.5, "VISIT BLOG", 9.5, bg, "middle"))
    b.append("".join(n))

    tb, tcss, th = ticker()
    body, allcss, total = stack([("".join(b), css, H), (tb, tcss, th)])
    return svg(W, total, body, allcss, "LDATUAN. Software for buildings. Civil engineer turned software engineer: Revit add-ins, model data on the web, and AI agents.")


# ------------------------------------------------------------------ section headers
def header_block(idx, left, right):
    body = (
        f'<rect width="880" height="36" fill="{T["bg"]}"/><path d="M0 .5 H880 M0 35.5 H880" stroke="{T["line"]}"/>'
        + mono(32, 22.5, f"{idx} / {left}", 9.5) + mono(848, 22.5, right, 9.5, T["faint"], "end")
    )
    return body, "", 36


def headline_block(p, lines, body_text, active, size=52):
    css = P("""
.§rise{animation:§rise 1s cubic-bezier(.2,.8,.2,1) both}
@keyframes §rise{from{transform:translateY(70px)}}
.§up{animation:§up .9s cubic-bezier(.2,.8,.2,1) .45s both}
@keyframes §up{from{opacity:0;transform:translateY(10px)}}
""", p)
    wrapped = textwrap.wrap(body_text, 62)
    h = 96 + (len(lines) - 1) * (size + 8) + 46 + (len(wrapped) - 1) * 25 + 44
    b, defs, y = [f'<rect width="880" height="{h}" fill="{T["bg"]}"/>'], [], 96
    for i, segs in enumerate(lines):
        defs.append(f'<clipPath id="{p}-cl{i}"><rect x="0" y="{y-size}" width="880" height="{size+16}"/></clipPath>')
        ts = []
        for txt, sty in segs:
            if sty == "s":
                ts.append(f'<tspan class="fs" font-size="{size*1.1:.0f}" fill="{T["strong"]}" letter-spacing="-1">{esc(txt)}</tspan>')
            else:
                ts.append(f'<tspan class="fh" font-size="{size}" fill="{T["strong"]}" letter-spacing="-1.8">{esc(txt)}</tspan>')
        b.append(f'<g clip-path="url(#{p}-cl{i})"><g class="{p}-rise" style="animation-delay:{.05+i*.12:.2f}s"><text x="32" y="{y}">{"".join(ts)}</text></g></g>')
        y += size + 8
    y += 46 - (size + 8)
    b.append(f'<g class="{p}-up">')
    for ln in wrapped:
        b.append(f'<text class="fb" x="32" y="{y}" font-size="16" fill="{T["muted"]}">{esc(ln)}</text>')
        y += 25
    b.append("</g>")
    adv = [30 if i == active else 17 for i in range(len(SECTIONS))]
    cy = h - 26 - sum(adv)
    for i, s in enumerate(SECTIONS):
        cy += adv[i]
        if i == active:
            b.append(f'<text class="fw" x="836" y="{cy}" font-size="25" fill="{T["strong"]}" text-anchor="end">{s}</text>')
        else:
            b.append(f'<text class="fw" x="836" y="{cy}" font-size="12.5" fill="{T["faint"]}" text-anchor="end">{s}</text>')
    b.append(
        f'<text class="fw" font-size="19" fill="none" stroke="{T["ink"]}" stroke-opacity=".3" stroke-width=".8" '
        f'text-anchor="middle" transform="translate(868,{h/2-30}) rotate(-90)">{SECTIONS[active]}</text>'
    )
    return f"<defs>{''.join(defs)}</defs>" + "".join(b), css, h


def section(p, idx, left, right, lines, body_text, active, extra=None):
    blocks = [header_block(idx, left, right), headline_block(p, lines, body_text, active)]
    if extra:
        blocks.append(extra)
    body, css, h = stack(blocks)
    label = f"{idx} {left.title()}. " + " ".join(t for seg in lines for t, _ in seg) + " " + body_text
    return svg(880, h, body, css, label)


# ------------------------------------------------------------------ work illustrations (440 x 190)
def ill_crop(p):
    css = P("""
.§crop{transform-box:view-box;transform-origin:70px 46px;animation:§crop 7s ease-in-out infinite}
@keyframes §crop{0%,12%{transform:scale(1)}45%,70%{transform:scale(.7,.78)}100%{transform:scale(1)}}
.§grip{animation:§grip 7s ease-in-out infinite}
@keyframes §grip{0%,12%{transform:translate(0,0)}45%,70%{transform:translate(-60px,-22px)}100%{transform:translate(0,0)}}
""", p)
    ink, line = T["ink"], T["line"]
    b = P(f"""
<rect width="440" height="190" fill="{T['raised']}"/>
<g fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width="1"><rect x="40" y="30" width="250" height="130"/>
<path d="M130 30 V96 H290 M40 96 H82 M210 96 V160 M130 160 V128"/></g>
<path d="M82 96 a24 24 0 0 1 24 -24 M210 128 a18 18 0 0 0 -18 18" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width=".8"/>
<mask id="§m"><rect width="440" height="190" fill="#fff"/><rect class="§crop" x="70" y="46" width="200" height="100" fill="#000"/></mask>
<rect width="310" height="190" fill="{ink}" fill-opacity=".07" mask="url(#§m)"/>
<rect class="§crop" x="70" y="46" width="200" height="100" fill="none" stroke="{T['acc']}" stroke-width="1.3" stroke-dasharray="5 4" vector-effect="non-scaling-stroke"/>
<g class="§grip"><rect x="266" y="142" width="8" height="8" fill="{T['acc']}"/><path d="M276 150 l0 14 l4 -4 l3 6 l2 -1 l-3 -6 l5 0 z" fill="{ink}"/></g>
<rect x="318" y="36" width="104" height="118" rx="6" fill="{T['paper']}" stroke="{line}"/>
<path d="M318 56 V42 a6 6 0 0 1 6 -6 H416 a6 6 0 0 1 6 6 V56 Z" fill="{T['sunk']}"/>
<text class="fb" x="328" y="50" font-size="9" fill="{ink}">Crop View</text>
""", p) + mono(328, 74, "OFFSET", 6.5) + f"""
<rect x="328" y="79" width="84" height="14" rx="3" fill="{T['bg']}" stroke="{line}"/><text class="fb" x="333" y="89" font-size="8" fill="{ink}">300 mm</text>
""" + mono(328, 107, "VIEW", 6.5) + f"""
<rect x="328" y="112" width="84" height="14" rx="3" fill="{T['bg']}" stroke="{line}"/><text class="fb" x="333" y="122" font-size="8" fill="{ink}">Level 2</text>
<rect x="370" y="134" width="42" height="14" rx="3" fill="{ink}"/>
""" + mono(391, 143.5, "APPLY", 6.5, T["bg"], "middle") + mono(20, 178, "CROPVIEWCOMMAND.CS", 7.5)
    return b, css


def ill_rebar(p):
    css = P("""
.§loop{animation:§loop 8s linear infinite}
@keyframes §loop{0%,92%{opacity:1}97%,100%{opacity:0}}
.§st{stroke-dasharray:404;animation:§st 8s ease-out infinite both}
@keyframes §st{0%{stroke-dashoffset:404}14%,100%{stroke-dashoffset:0}}
.§b{transform-box:fill-box;transform-origin:center;animation:§b 8s cubic-bezier(.2,1.4,.4,1) infinite both}
@keyframes §b{0%,16%{transform:scale(0)}22%,100%{transform:scale(1)}}
.§dim{stroke-dasharray:420;animation:§dim 8s ease-out infinite both}
@keyframes §dim{0%,28%{stroke-dashoffset:420}38%,100%{stroke-dashoffset:0}}
.§tag{animation:§tag 8s ease infinite both}
@keyframes §tag{0%,40%{opacity:0}46%,100%{opacity:1}}
.§flow{animation:§flow 1s linear infinite}
@keyframes §flow{to{stroke-dashoffset:-9}}
""", p)
    ink, acc = T["ink"], T["acc"]
    bars = "".join(f'<circle class="§b" style="animation-delay:{i*.12:.2f}s" cx="{x}" cy="44" r="5.5" fill="{ink}"/>' for i, x in enumerate((94, 118, 142)))
    bars += "".join(f'<circle class="§b" style="animation-delay:{.36+i*.12:.2f}s" cx="{x}" cy="145" r="6.5" fill="{ink}"/>' for i, x in enumerate((93, 109, 127, 143)))
    json_lines = [
        ('<tspan fill="#a1a1aa">{</tspan>', 0),
        ('<tspan fill="#9cc2ff">"b"</tspan><tspan fill="#a1a1aa">: </tspan><tspan fill="#fff">300,</tspan>', 1),
        ('<tspan fill="#9cc2ff">"h"</tspan><tspan fill="#a1a1aa">: </tspan><tspan fill="#fff">600,</tspan>', 1),
        ('<tspan fill="#9cc2ff">"top"</tspan><tspan fill="#a1a1aa">: </tspan><tspan fill="#fff">"3Ø20",</tspan>', 1),
        ('<tspan fill="#9cc2ff">"bot"</tspan><tspan fill="#a1a1aa">: </tspan><tspan fill="#fff">"4Ø25"</tspan>', 1),
        ('<tspan fill="#a1a1aa">}</tspan>', 0),
    ]
    js = "".join(f'<text class="fc" x="{298+ind*10}" y="{62+i*16}" font-size="8.5">{t}</text>' for i, (t, ind) in enumerate(json_lines))
    b = P(f"""
<rect width="440" height="190" fill="{T['raised']}"/>
<pattern id="§dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r=".7" fill="{ink}" fill-opacity=".18"/></pattern>
<rect x="70" y="22" width="96" height="146" fill="{T['concrete']}"/><rect x="70" y="22" width="96" height="146" fill="url(#§dots)"/>
<rect x="70" y="22" width="96" height="146" fill="none" stroke="{ink}" stroke-opacity=".75" stroke-width="1.2"/>
<g class="§loop">
<rect class="§st" x="80" y="32" width="76" height="126" rx="6" fill="none" stroke="{acc}" stroke-width="1.6"/>
{bars}
<path class="§dim" d="M188 22 V168 M183 22 H193 M183 168 H193 M70 178 H166 M70 174 V182 M166 174 V182" fill="none" stroke="{ink}" stroke-opacity=".5" stroke-width=".8"/>
<g class="§tag">
<path d="M142 44 L222 26 H254 M143 145 L222 164 H254" fill="none" stroke="{ink}" stroke-opacity=".55" stroke-width=".8"/>
""", p) + mono(196, 98, "600", 8, T["muted"], cls="fc") + mono(172, 181, "300", 8, T["muted"], cls="fc") \
        + mono(226, 22, "3Ø20", 9, ink, cls="fc") + mono(226, 160, "4Ø25", 9, ink, cls="fc") + P(f"""
</g></g>
<path class="§flow" d="M286 95 H200" stroke="{acc}" stroke-width="1.2" stroke-dasharray="4 5"/>
<path d="M204 91 L198 95 L204 99" fill="none" stroke="{acc}" stroke-width="1.2"/>
<rect x="286" y="34" width="136" height="122" rx="8" fill="{T['screen']}"/>
{js}
""", p) + mono(298, 148, "BEAM.JSON", 6.5, "#71717a") + mono(20, 178, "BEAMSECTIONVIEW.CS", 7.5)
    return b, css


def ill_multi(p):
    css = P("""
.§dot{animation:§dot 2.6s linear infinite;offset-rotate:0deg}
@keyframes §dot{0%{offset-distance:0%;opacity:0}15%{opacity:1}85%{opacity:1}100%{offset-distance:100%;opacity:0}}
.§ok{transform-box:fill-box;transform-origin:center;animation:§ok 5.2s cubic-bezier(.2,1.4,.4,1) infinite both}
@keyframes §ok{0%,40%{transform:scale(0)}48%,92%{transform:scale(1)}100%{transform:scale(0)}}
""", p)
    ink, line = T["ink"], T["line"]
    b = [f'<rect width="440" height="190" fill="{T["raised"]}"/>']
    for i, ver in enumerate(["1.0.0.0", "1.1.0.0", "2.0.0.0"]):
        y = 34 + i * 44
        b.append(f'<rect x="22" y="{y}" width="112" height="30" rx="5" fill="{T["bg"]}" stroke="{line}"/>')
        b.append(f'<text class="fb" x="32" y="{y+13}" font-size="9.5" fill="{ink}">MyLibrary.dll</text>')
        b.append(mono(32, y + 24, "v" + ver, 7.5, T["faint"], cls="fc"))
    paths = ["M134 49 C150 49,150 95,166 95", "M134 93 H166", "M134 137 C150 137,150 95,166 95",
             "M290 95 C304 95,304 75,326 75", "M290 95 C304 95,304 121,326 121"]
    for d in paths:
        b.append(f'<path d="{d}" fill="none" stroke="{ink}" stroke-opacity=".22"/>')
    for i, d in enumerate(paths):
        delay = (i % 3) * .5 + (1.3 if i >= 3 else 0)
        b.append(P(f'<circle class="§dot" style="offset-path:path(\'{d}\');animation-delay:{delay:.2f}s" r="2.6" fill="{T["acc"]}"/>', p))
    b.append(f'<rect x="166" y="50" width="124" height="90" rx="8" fill="{T["screen"]}"/>')
    b.append(mono(176, 64, "MYLIBRARY.DLL.CONFIG", 5.8, "#71717a"))
    cfg = [("&lt;bindingRedirect", "#9cc2ff", 0), ("oldVersion=", "#a1a1aa", 6), ('"1.0.0.0-1.1.0.0"', "#c8f7a6", 12),
           ("newVersion=", "#a1a1aa", 6), ('"2.0.0.0" /&gt;', "#c8f7a6", 12)]
    for i, (t, col, ind) in enumerate(cfg):
        b.append(f'<text class="fc" x="{176+ind}" y="{80+i*12}" font-size="7.5" fill="{col}">{t}</text>')
    b.append(f'<rect x="316" y="30" width="108" height="130" rx="6" fill="{T["bg"]}" stroke="{line}"/>')
    b.append(mono(326, 46, "HOST APP", 7))
    for i, (name, y) in enumerate([("TestLoadAddin", 58), ("TestLoadAddin2", 104)]):
        b.append(f'<rect x="326" y="{y}" width="90" height="34" rx="5" fill="{T["paper"]}" stroke="{line}"/>')
        b.append(f'<text class="fb" x="334" y="{y+15}" font-size="8" fill="{ink}">{name}</text>')
        b.append(mono(334, y + 26, "→ 2.0.0.0", 6.5, T["faint"], cls="fc"))
        b.append(P(f'<g class="§ok" style="animation-delay:{i*.3:.1f}s"><circle cx="406" cy="{y+17}" r="5.5" fill="{T["acc"]}"/>'
                   f'<path d="M403.5 {y+17} l2 2 l3.5 -4" fill="none" stroke="#fff" stroke-width="1.2"/></g>', p))
    b.append(mono(20, 178, "STRONG NAME + BINDING REDIRECT", 7.5))
    return "".join(b), css


def ill_agent(p):
    css = P("""
.§u{animation:§u 9s cubic-bezier(.2,.8,.2,1) infinite both}
@keyframes §u{0%,3%{opacity:0;transform:translateY(8px)}9%,92%{opacity:1;transform:none}98%,100%{opacity:0}}
.§a{animation:§a 9s cubic-bezier(.2,.8,.2,1) infinite both}
@keyframes §a{0%,24%{opacity:0;transform:translateY(8px)}30%,92%{opacity:1;transform:none}98%,100%{opacity:0}}
.§hl{stroke-dasharray:494;animation:§hl 9s ease-out infinite both}
@keyframes §hl{0%,32%{stroke-dashoffset:494}52%,92%{stroke-dashoffset:0;opacity:1}98%,100%{opacity:0}}
.§dot{animation:§dot 1.4s ease-in-out infinite}
@keyframes §dot{50%{opacity:.25}}
""", p)
    b = P(f"""
<rect width="440" height="190" fill="{T['screen']}"/>
<g class="§u"><rect x="54" y="24" width="160" height="30" rx="12" fill="{FIX_ACC}"/>
<text class="fb" x="68" y="43" font-size="10" fill="#fff">Walls with no fire rating?</text></g>
<g class="§a"><rect x="20" y="66" width="194" height="56" rx="12" fill="#25252d" stroke="#34343e"/>
<path d="M36 81 l1.4 -3.4 l1.4 3.4 l3.4 1.4 l-3.4 1.4 l-1.4 3.4 l-1.4 -3.4 l-3.4 -1.4 z" fill="#9cc2ff"/>
""", p) + mono(46, 85, "AGENT", 7, "#9cc2ff") + P(f"""
<text class="fb" x="34" y="101" font-size="10" fill="#e4e4e7">Found 37 walls on Level 2.</text>
<text class="fb" x="34" y="115" font-size="10" fill="#a1a1aa">Highlighted in the 3D view.</text></g>
<rect x="20" y="138" width="194" height="28" rx="14" fill="#202027" stroke="#34343e"/>
<text class="fb" x="34" y="156" font-size="9" fill="#62626d">Ask the model…</text>
<circle cx="200" cy="152" r="9" fill="{FIX_ACC}"/><path d="M196 152 h7 m-3 -3 l3 3 l-3 3" fill="none" stroke="#fff" stroke-width="1.2"/>
<g fill="none" stroke="#44444e" stroke-width="1"><rect x="236" y="24" width="184" height="144"/>
<path d="M236 96 H330 V168 M330 96 V60 H420 M380 96 V168 M290 24 V60"/></g>
<path class="§hl" d="M236 24 H420 M420 24 V168 M330 96 V168 M236 96 H330" fill="none" stroke="{FIX_ACC}" stroke-width="2.4"/>
<circle class="§dot" cx="240" cy="180" r="2.5" fill="{FIX_ACC}"/>
""", p) + mono(248, 182.5, "LIVE · LEVEL 2", 6.5, "#71717a")
    return b, css


def ill_doc(p):
    css = P("""
.§scan{animation:§scan 5s ease-in-out infinite}
@keyframes §scan{0%{transform:translateY(16px)}100%{transform:translateY(174px)}}
.§hb{animation:§hb 5s ease infinite both}
@keyframes §hb{0%,4%{opacity:0}10%,94%{opacity:1}100%{opacity:0}}
.§chip{animation:§chip 5s cubic-bezier(.2,.8,.2,1) infinite both}
@keyframes §chip{0%,4%{opacity:0;transform:translateX(10px)}12%,94%{opacity:1;transform:none}100%{opacity:0}}
""", p)
    ink, line, acc = T["ink"], T["line"], T["acc"]
    b = [P(f"""
<rect width="440" height="190" fill="{T['sunk']}"/>
<defs><linearGradient id="§sg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{acc}" stop-opacity="0"/><stop offset="1" stop-color="{acc}" stop-opacity=".18"/></linearGradient>
<clipPath id="§sc"><rect x="28" y="16" width="226" height="158"/></clipPath></defs>
<rect x="28" y="16" width="226" height="158" fill="{T['paper']}" stroke="{line}"/>
<rect x="36" y="24" width="210" height="142" fill="none" stroke="{ink}" stroke-opacity=".3" stroke-width=".6"/>
<path d="M48 36 H170 V120 H48 Z M100 36 V80 H170 M48 92 H80 M130 120 V96 H170" fill="none" stroke="{ink}" stroke-opacity=".45" stroke-width=".8"/>
<g fill="{ink}" fill-opacity=".18"><rect x="180" y="40" width="56" height="3"/><rect x="180" y="48" width="48" height="3"/><rect x="180" y="56" width="52" height="3"/><rect x="180" y="64" width="34" height="3"/></g>
<rect x="178" y="124" width="64" height="38" fill="none" stroke="{ink}" stroke-opacity=".35" stroke-width=".6"/>
<path d="M178 136 H242 M178 148 H242 M210 148 V162" stroke="{ink}" stroke-opacity=".3" stroke-width=".5"/>
""", p), mono(182, 133, "A-201", 5), mono(182, 145, "1:100", 5), mono(182, 158, "REV C", 5),
        P(f"""
<g clip-path="url(#§sc)"><g class="§scan"><rect x="28" y="-26" width="226" height="26" fill="url(#§sg)"/><rect x="28" y="0" width="226" height="1.5" fill="{acc}"/></g></g>
<rect class="§hb" style="animation-delay:.6s" x="176" y="36" width="66" height="34" fill="none" stroke="{acc}" stroke-width="1.2"/>
<rect class="§hb" style="animation-delay:3.4s" x="175" y="121" width="70" height="44" fill="none" stroke="{acc}" stroke-width="1.2"/>
""", p)]
    rows = [("SHEET", "A-201", 3.5), ("SCALE", "1:100", 3.7), ("TITLE", "Level 2 plan", 0.8), ("REVISION", "C", 3.9)]
    for i, (k, v, d) in enumerate(rows):
        y = 30 + i * 36
        b.append(P(f'<g class="§chip" style="animation-delay:{d}s"><rect x="272" y="{y}" width="150" height="28" rx="5" fill="{T["bg"]}" stroke="{line}"/>', p)
                 + mono(282, y + 11, k, 6.5) + f'<text class="fb" x="282" y="{y+23}" font-size="10.5" fill="{ink}">{v}</text></g>')
    return "".join(b), css


def ill_pothole(p):
    """Dashcam at dusk: lane marks and potholes roll toward the viewer, boxes track them."""
    rnd = random.Random(11)
    VX, VY = 226, 76
    css = P("""
.§mv{animation:§mv 2.4s cubic-bezier(.55,0,1,.6) infinite}
@keyframes §mv{from{transform:translateY(0) scale(.03)}to{transform:translateY(150px) scale(1.15)}}
.§ph{animation:§mv 6s cubic-bezier(.55,0,1,.6) infinite}
.§lp{animation:§mv 3.6s cubic-bezier(.55,0,1,.6) infinite}
.§bx{animation:§bx 6s linear infinite both}
@keyframes §bx{0%,46%{opacity:0}52%,100%{opacity:1}}
.§rec{animation:§rec 1.2s steps(1) infinite}
@keyframes §rec{50%{opacity:.15}}
.§tw{animation:§tw 3.2s ease-in-out infinite}
@keyframes §tw{50%{opacity:.25}}
""", p)
    b = [P(f"""
<defs>
<linearGradient id="§sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2338"/><stop offset=".55" stop-color="#5d4f6c"/><stop offset="1" stop-color="#e8a47a"/></linearGradient>
<radialGradient id="§sun" cx="{VX}" cy="{VY}" r="150" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#ffd7a3" stop-opacity=".95"/><stop offset=".35" stop-color="#f0a878" stop-opacity=".35"/><stop offset="1" stop-color="#f0a878" stop-opacity="0"/></radialGradient>
<linearGradient id="§road" x1="0" y1="{VY}" x2="0" y2="190" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#77707a"/><stop offset=".35" stop-color="#47454c"/><stop offset="1" stop-color="#26262b"/></linearGradient>
<linearGradient id="§gr" x1="0" y1="{VY}" x2="0" y2="190" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#5b4d57"/><stop offset="1" stop-color="#1d1b22"/></linearGradient>
<radialGradient id="§vig" cx="220" cy="100" r="270" gradientUnits="userSpaceOnUse"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<pattern id="§scan" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity=".035"/></pattern>
<radialGradient id="§glow"><stop offset="0" stop-color="#ffd9a6" stop-opacity=".9"/><stop offset="1" stop-color="#ffd9a6" stop-opacity="0"/></radialGradient>
<radialGradient id="§refl" cx="{VX}" cy="{VY+26}" r="64" gradientUnits="userSpaceOnUse" gradientTransform="translate({VX} {VY+26}) scale(.32 1) translate(-{VX} -{VY+26})"><stop offset="0" stop-color="#ffd7a3" stop-opacity=".32"/><stop offset="1" stop-color="#ffd7a3" stop-opacity="0"/></radialGradient>
</defs>
<rect width="440" height="{VY}" fill="url(#§sky)"/>
<rect width="440" height="190" fill="url(#§sun)"/>
<circle cx="{VX}" cy="{VY-4}" r="8" fill="#ffe8c8" fill-opacity=".9"/>
""", p)]
    # skyline silhouettes on the horizon
    sil, win = [], []
    for side in (0, 1):
        x = 0 if side == 0 else 250
        end = 202 if side == 0 else 440
        while x < end:
            w = rnd.randint(14, 30)
            h = rnd.randint(10, 34) if abs(x + w / 2 - VX) > 40 else rnd.randint(6, 14)
            sil.append(f'<rect x="{x}" y="{VY-h}" width="{w}" height="{h}" fill="#262a3b"/>')
            for _ in range(rnd.randint(0, 3)):
                wx, wy = x + rnd.randint(2, max(3, w - 4)), VY - rnd.randint(3, max(4, h - 3))
                delay = rnd.uniform(0, 3)
                win.append(P(f'<rect class="§tw" style="animation-delay:-{delay:.1f}s" x="{wx}" y="{wy}" width="2" height="2" fill="#ffd28a" fill-opacity=".8"/>', p))
            x += w + rnd.randint(0, 4)
    b.append("".join(sil) + "".join(win))
    b.append(P(f'<rect x="0" y="{VY}" width="440" height="{190-VY}" fill="url(#§gr)"/>', p))
    b.append(P(f'<polygon points="{VX-5},{VY} {VX+5},{VY} 500,190 -48,190" fill="url(#§road)"/>', p))
    b.append(f'<path d="M{VX-4} {VY} L-30 190 M{VX+4} {VY} L482 190" stroke="#efe7dc" stroke-opacity=".55" stroke-width="1.3"/>')
    b.append(P(f'<rect x="{VX-40}" y="{VY}" width="80" height="120" fill="url(#§refl)"/>', p))
    # lane dashes rolling toward the camera
    for i in range(5):
        b.append(P(f'<g transform="translate({VX},{VY})"><g class="§mv" style="animation-delay:-{i*.48:.2f}s">'
                   '<polygon points="-3,-26 3,-26 6,0 -6,0" fill="#f2ece2" fill-opacity=".85"/></g></g>', p))
    # potholes, each with a detection box that grows with it
    for off, conf, delay in [(-84, "0.94", 0), (74, "0.88", 2), (-14, "0.71", 4)]:
        lab = f"POTHOLE {conf}"
        lw = 8 * 0.75 * len(lab) + 10
        bx, by, bw, bh = off - 44, -22, 88, 30
        corners = (f"M{bx} {by+9} v-9 h9 M{bx+bw-9} {by} h9 v9 M{bx} {by+bh-9} v9 h9 M{bx+bw-9} {by+bh} h9 v-9")
        b.append(P(
            f'<g transform="translate({VX},{VY})"><g class="§ph" style="animation-delay:-{delay}s">'
            f'<ellipse cx="{off}" cy="-6" rx="36" ry="10" fill="#141417"/>'
            f'<ellipse cx="{off-4}" cy="-7" rx="22" ry="5" fill="#3a3f55" fill-opacity=".7"/>'
            f'<ellipse cx="{off}" cy="-6" rx="36" ry="10" fill="none" stroke="#5b5a62" stroke-width=".9"/>'
            f'<path d="M{off-36} -6 l-10 4 M{off+34} -9 l12 -3 l6 3" fill="none" stroke="#141417" stroke-width="1.3"/>'
            f'<g class="§bx" style="animation-delay:-{delay}s">'
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{FIX_ACC}" fill-opacity=".1"/>'
            f'<path d="{corners}" fill="none" stroke="{FIX_ACC}" stroke-width="2"/>'
            f'<rect x="{bx}" y="{by-14}" width="{lw:.0f}" height="13" fill="{FIX_ACC}"/>', p)
            + mono(bx + 5, by - 4, lab, 8, "#ffffff") + "</g></g></g>")
    # street lights sweeping past on both sides
    for side in (-1, 1):
        for i in range(3):
            x = 372 * side
            arm = x - 30 * side
            b.append(P(
                f'<g transform="translate({VX},{VY})"><g class="§lp" style="animation-delay:-{i*1.2 + (0.6 if side > 0 else 0):.1f}s">'
                f'<circle cx="{arm}" cy="-146" r="22" fill="url(#§glow)" opacity=".55"/>'
                f'<path d="M{x} 0 V-150 H{arm}" fill="none" stroke="#1e2130" stroke-width="5"/>'
                f'<rect x="{arm - 9 if side > 0 else arm - 3}" y="-152" width="12" height="5" rx="2" fill="#ffe3b8"/>'
                "</g></g>", p))
    # HUD
    b.append(P(f'<rect width="440" height="190" fill="url(#§scan)"/><rect width="440" height="190" fill="url(#§vig)"/>', p))
    b.append('<path d="M14 26 V14 H26 M414 14 H426 V26 M14 164 V176 H26 M414 176 H426 V164" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="1.2"/>')
    b.append(P('<circle class="§rec" cx="38" cy="26" r="3.2" fill="#ff5a5a"/>', p) + mono(46, 29, "REC", 7.5, "rgba(255,255,255,.9)"))
    b.append(mono(76, 29, "CAM 01", 7.5, "rgba(255,255,255,.55)"))
    b.append(mono(404, 29, "YOLOV6", 7.5, "rgba(255,255,255,.9)", "end"))
    b.append(mono(404, 40, "LIVE DETECTION", 6.2, "rgba(255,255,255,.55)", "end"))
    return "".join(b), css


def work_card(p, label, idx, title, body_text, ill):
    W, H = 440, 344
    inner, icss = ill(p)
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>']
    b.append(mono(20, 21.5, label, 9) + mono(420, 21.5, idx, 9, T["faint"], "end"))
    b.append(f'<svg x="0" y="34" width="440" height="190" viewBox="0 0 440 190" overflow="hidden">{inner}</svg>')
    b.append(f'<path d="M0 34.5 H440 M0 224.5 H440 M0 {H-.5} H440" stroke="{T["line"]}"/>')
    b.append(f'<text class="fh" x="24" y="262" font-size="21" fill="{T["strong"]}" letter-spacing="-.6">{esc(title)}</text>')
    y = 290
    for ln in textwrap.wrap(body_text, 56):
        b.append(f'<text class="fb" x="24" y="{y}" font-size="13.5" fill="{T["muted"]}">{esc(ln)}</text>')
        y += 19
    return svg(W, H, "".join(b), icss, f"{title}. {body_text}")


# ------------------------------------------------------------------ journey
def timeline_block():
    css = """
.tl-prog{stroke-dasharray:708;animation:tl-prog 2.6s cubic-bezier(.5,0,.2,1) .3s both}
@keyframes tl-prog{from{stroke-dashoffset:708}}
.tl-n{transform-box:fill-box;transform-origin:center;animation:tl-n .5s cubic-bezier(.2,1.4,.4,1) both}
@keyframes tl-n{from{transform:scale(0)}}
.tl-pulse{transform-box:fill-box;transform-origin:center;animation:tl-pulse 1.8s ease-out 3s infinite}
@keyframes tl-pulse{0%{transform:scale(.6);opacity:.6}100%{transform:scale(2.2);opacity:0}}
.tl-up{animation:tl-up .7s cubic-bezier(.2,.8,.2,1) both}
@keyframes tl-up{from{opacity:0;transform:translateY(8px)}}
"""
    cells = [
        ("2015 — 2020", "HCMUT", ["Civil engineering,", "PFIEV programme."]),
        ("2020", "BIM Factory", ["BIM technologist.", "Revit, Dynamo, Forge."]),
        ("2023", "Arent, Tokyo", ["C# and WPF add-ins", "for MEP automation."]),
        ("2026", "Tiong Seng", ["Revit add-ins and", "Platform Services."]),
        ("NOW", "Agents for AEC", ["A Revit agent and", "Agent Drawing."]),
    ]
    acc, ink, line = T["acc"], T["ink"], T["line"]
    b = [f'<rect width="880" height="176" fill="{T["bg"]}"/><path d="M0 .5 H880 M0 175.5 H880" stroke="{line}"/>']
    b.append(f'<path d="M24 56 H856" stroke="{ink}" stroke-opacity=".14" stroke-width="2"/>')
    b.append(f'<path d="M732 56 H856" stroke="{acc}" stroke-opacity=".5" stroke-width="2" stroke-dasharray="3 5"/>')
    b.append(f'<path class="tl-prog" d="M24 56 H732" stroke="{acc}" stroke-width="2"/>')
    for i, (yr, title, desc) in enumerate(cells):
        x0, last = i * 176, i == len(cells) - 1
        nx = x0 + 28
        t = .3 + (nx - 24) / 708 * 2.6
        if i:
            b.append(f'<path d="M{x0+.5} 0 V176" stroke="{line}"/>')
        b.append(f'<g class="tl-up" style="animation-delay:{t:.2f}s">' + mono(x0 + 24, 34, yr, 9.5, acc if last else T["faint"]))
        b.append(f'<text class="fh" x="{x0+24}" y="94" font-size="17" fill="{T["strong"]}" letter-spacing="-.4">{esc(title)}</text>')
        for j, d in enumerate(desc):
            b.append(f'<text class="fb" x="{x0+24}" y="{118+j*18}" font-size="12.5" fill="{T["muted"]}">{esc(d)}</text>')
        b.append("</g>")
        if last:
            b.append(f'<circle class="tl-pulse" cx="{nx}" cy="56" r="6" fill="{acc}"/>')
        b.append(f'<circle class="tl-n" style="animation-delay:{t:.2f}s" cx="{nx}" cy="56" r="5" fill="{acc if last else T["bg"]}" stroke="{acc if last else ink}" stroke-width="1.5"/>')
    return "".join(b), css, 176


# ------------------------------------------------------------------ writing thumbs (293 x 150)
def th_rlhf(p):
    css = P("""
.§cv{stroke-dasharray:320;animation:§cv 6s ease-out infinite both}
@keyframes §cv{0%{stroke-dashoffset:320}55%,92%{stroke-dashoffset:0;opacity:1}100%{opacity:0}}
""", p)
    b = [f'<rect width="293" height="150" fill="{T["screen"]}"/>']
    b.append("".join(f'<path d="M0 {y} H293" stroke="#2a2a33"/>' for y in (30, 60, 90, 120)))
    b.append(f'<rect x="0" y="52" width="293" height="36" fill="{FIX_ACC}" fill-opacity=".1"/>')
    b.append('<path d="M0 52 H293 M0 88 H293" stroke="#44444f" stroke-dasharray="3 3"/>')
    b.append(mono(282, 48, "1+ε", 7, "#8b8b96", "end", "fc") + mono(282, 100, "1−ε", 7, "#8b8b96", "end", "fc"))
    b.append(P(f'<path class="§cv" d="M14 120 C40 118,52 104,70 108 S100 86,118 92 S150 70,170 74 S206 56,224 60 S262 44,280 46" fill="none" stroke="#5aa0ff" stroke-width="2"/>', p))
    b.append('<text class="fs" x="16" y="40" font-size="28" fill="#fff">PPO</text>')
    return "".join(b), css


def th_math(p):
    css = P("""
.§gd{offset-path:path('M118 28 L170 118 L186 52 L200 104 L203 72 L206 86');offset-rotate:0deg;animation:§gd 5s cubic-bezier(.4,0,.2,1) infinite}
@keyframes §gd{0%{offset-distance:0%}70%,100%{offset-distance:100%}}
.§pl{stroke-dasharray:300;animation:§pl 5s cubic-bezier(.4,0,.2,1) infinite}
@keyframes §pl{0%{stroke-dashoffset:300}70%,100%{stroke-dashoffset:0}}
""", p)
    ink = T["ink"]
    b = [f'<rect width="293" height="150" fill="{T["sunk"]}"/>']
    for i, (rx, ry) in enumerate([(84, 56), (64, 42), (44, 29), (24, 16), (10, 7)]):
        b.append(f'<ellipse cx="206" cy="84" rx="{rx}" ry="{ry}" fill="none" stroke="{ink}" stroke-opacity="{.12+i*.06:.2f}"/>')
    b.append(P(f'<path class="§pl" d="M118 28 L170 118 L186 52 L200 104 L203 72 L206 86" fill="none" stroke="{T["acc"]}" stroke-width="1.2"/>', p))
    b.append(P(f'<circle class="§gd" r="3.5" fill="{T["acc"]}"/>', p))
    b.append(f'<text class="fs" x="16" y="46" font-size="30" fill="{ink}">∇J(θ)</text>')
    b.append(mono(16, 134, "θ ← θ − η∇J", 8, T["faint"], cls="fc"))
    return "".join(b), css


def th_crop(p):
    inner, css = ill_crop(p)
    return f'<svg width="293" height="150" viewBox="20 12 294 150" preserveAspectRatio="xMidYMid slice">{inner}</svg>', css


def writing_card(p, meta, title, thumb, idx):
    W, H = 880 / 3, 274
    inner, tcss = thumb(p)
    b = [f'<rect width="{W:.3f}" height="{H}" fill="{T["bg"]}"/>']
    b.append(mono(18, 21.5, "ARTICLE", 9) + mono(275, 21.5, idx, 9, T["faint"], "end"))
    b.append(f'<svg x="0" y="34" width="293.333" height="150" viewBox="0 0 293 150" preserveAspectRatio="none" overflow="hidden">{inner}</svg>')
    b.append(f'<path d="M0 34.5 H{W:.3f} M0 184.5 H{W:.3f} M0 {H-.5} H{W:.3f}" stroke="{T["line"]}"/>')
    b.append(f'<rect x="10" y="152" width="62" height="22" fill="#101014" fill-opacity=".88"/><path d="M20 158.5 l7 4.5 l-7 4.5 z" fill="none" stroke="#fff" stroke-width="1"/>' + mono(33, 166.5, "READ", 8, "#fff"))
    y = 212
    for ln in textwrap.wrap(title, 32):
        b.append(f'<text class="fbm" x="18" y="{y}" font-size="14.5" fill="{T["ink"]}">{esc(ln)}</text>')
        y += 20
    b.append(mono(18, 256, meta, 8))
    return svg(W, H, "".join(b), tcss, f"Article: {title}", viewbox=f"0 0 {W:.3f} {H}")


# ------------------------------------------------------------------ closing: CTA + footer, cut into windows
CTA_H = 330
FOOT_H = 280
BTN_Y0, BTN_Y1 = 206, 262            # band holding the two buttons
BTN_COLS = [(0, 312), (312, 440), (440, 568), (568, 880)]


def closing_scene():
    css = """
.c-rise{animation:c-rise 1.1s cubic-bezier(.2,.8,.2,1) .1s both}
@keyframes c-rise{from{transform:translateY(100px)}}
.c-dash{animation:c-dash 20s linear infinite}
@keyframes c-dash{to{stroke-dashoffset:-400}}
"""
    ink, bg, line = T["ink"], T["bg"], T["line"]
    b = [f'<rect width="880" height="{CTA_H+FOOT_H}" fill="{bg}"/><path d="M0 .5 H880" stroke="{line}"/>']
    b.append(f'<defs><clipPath id="c-cl"><rect x="0" y="96" width="880" height="100"/></clipPath><clipPath id="c-top"><rect width="880" height="{CTA_H}"/></clipPath></defs>')
    b.append('<g clip-path="url(#c-top)">')
    for rx in range(200, 800, 100):
        b.append(f'<ellipse cx="440" cy="430" rx="{rx}" ry="{rx*.62:.0f}" fill="none" stroke="{ink}" stroke-opacity=".07"/>')
    b.append(f'<ellipse class="c-dash" cx="440" cy="430" rx="400" ry="248" fill="none" stroke="{T["acc"]}" stroke-opacity=".35" stroke-dasharray="2 14"/>')
    b.append("</g>")
    b.append(mono(440, 86, "OPEN TO COLLABORATION · REVIT · APS · AGENTS", 9.5, T["faint"], "middle"))
    b.append(
        '<g clip-path="url(#c-cl)"><g class="c-rise"><text x="440" y="180" text-anchor="middle">'
        f'<tspan class="fh" font-size="84" fill="{T["strong"]}" letter-spacing="-3">Start </tspan>'
        f'<tspan class="fs" font-size="92" fill="{T["strong"]}" letter-spacing="-1">building.</tspan></text></g></g>'
    )
    b.append(f'<rect x="316" y="214" width="120" height="40" fill="{ink}"/>' + mono(376, 237.5, "VISIT BLOG", 10, bg, "middle"))
    b.append(f'<rect x="444.5" y="214.5" width="119" height="39" fill="none" stroke="{ink}" stroke-opacity=".28"/>' + mono(504, 237.5, "LINKEDIN", 10, ink, "middle"))

    # footer
    f = [f'<path d="M0 .5 H880 M0 232.5 H880" stroke="{line}"/>', mark(32, 28, 32)]
    f.append(f'<text class="fb" x="32" y="96" font-size="14" fill="{T["muted"]}">Software for buildings,</text>')
    f.append(f'<text class="fb" x="32" y="116" font-size="14" fill="{T["muted"]}">from a civil engineer.</text>')
    f.append(mono(32, 148, "LDATUAN.COM", 7.5))
    cols = [
        ("STACK", ["C# · WPF", "Revit API", "Platform Services", "Python", "Next.js"]),
        ("WORK", ["RevitAPI-Learning", "AutoCadRebar", "multiversion", "pothole"]),
        ("WRITING", ["Blog", "About", "Tiếng Việt"]),
        ("ELSEWHERE", ["GitHub", "LinkedIn"]),
    ]
    for i, (h, items) in enumerate(cols):
        x = 300 + i * 145
        f.append(f'<path d="M{x+.5} 0 V232" stroke="{line}"/>')
        f.append(mono(x + 24, 42, h, 8.5))
        for j, it in enumerate(items):
            f.append(f'<text class="fb" x="{x+24}" y="{74+j*24}" font-size="13.5" fill="{ink}">{esc(it)}</text>')
    f.append(mono(32, 260, f"© {dt.date.today().year} LDATUAN", 8.5) + mono(848, 260, "MADE BY AN ENGINEER, FOR ENGINEERS", 8.5, T["faint"], "end"))
    b.append(f'<g transform="translate(0,{CTA_H})">{"".join(f)}</g>')
    return "".join(b), css


def closing_windows():
    """The closing scene cut into windows, so each button can be its own link."""
    body, css = closing_scene()
    H = CTA_H + FOOT_H
    out = {"cta-top": svg(880, BTN_Y0, body, css, "Start building. Open to collaboration on Revit, Autodesk Platform Services and agents.",
                          viewbox=f"0 0 880 {BTN_Y0}")}
    names = ["cta-left", "cta-blog", "cta-linkedin", "cta-right"]
    labels = ["", "Visit the blog", "LinkedIn", ""]
    for name, lab, (x0, x1) in zip(names, labels, BTN_COLS):
        out[name] = svg(x1 - x0, BTN_Y1 - BTN_Y0, body, css, lab or " ", viewbox=f"{x0} {BTN_Y0} {x1-x0} {BTN_Y1-BTN_Y0}")
    out["cta-bottom"] = svg(880, H - BTN_Y1, body, css, "Footer: stack, work, writing and links. Made by an engineer, for engineers.",
                            viewbox=f"0 {BTN_Y1} 880 {H-BTN_Y1}")
    return out
