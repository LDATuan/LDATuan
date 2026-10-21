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
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{esc(label)}">'
        f"<title>{esc(label)}</title><style>{BASE_CSS}{css}</style>{body}</svg>"
    )


def mono(x, y, s, size=9.5, fill=None, anchor="start", cls="fm", extra=""):
    fill = fill or T["faint"]
    return (
        f'<text class="{cls}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" {extra}>{esc(s)}</text>'
    )


def mark(x, y, s=1.0, fill=None):
    """I-beam cross-section, used as the monogram."""
    return (
        f'<path transform="translate({x},{y}) scale({s})" fill="{fill or T["ink"]}" '
        'd="M0 0 H22 V5 H14 V15 H22 V20 H0 V15 H8 V5 H0 Z"/>'
    )


def stack(blocks):
    """Stack (body, css, height) blocks vertically into one body."""
    out, css, y = [], [], 0
    for body, c, h in blocks:
        out.append(f'<g transform="translate(0,{y})">{body}</g>')
        css.append(c)
        y += h
    return "".join(out), "".join(css), y


# ------------------------------------------------------------------ hero
def hero_cards():
    clip = '<clipPath id="h-cc"><rect x="-55" y="-36" width="110" height="72" rx="9"/></clipPath>'

    def card(bg, inner, border="rgba(16,16,20,.12)"):
        return (
            f'<rect x="-55" y="-36" width="110" height="72" rx="9" fill="{bg}"/>'
            f'<g clip-path="url(#h-cc)">{inner}</g>'
            f'<rect x="-55" y="-36" width="110" height="72" rx="9" fill="none" stroke="{border}"/>'
        )

    lines = [(0, 40, "#bb9af7"), (8, 56, "#7aa2f7"), (8, 34, "#9ece6a"), (16, 44, "#e0af68"), (8, 50, "#7dcfff"), (0, 22, "#bb9af7")]
    c = {
        "plan": card("#fbfaf7",
            '<g fill="none" stroke="#101014" stroke-opacity=".6" stroke-width=".9">'
            '<rect x="-42" y="-26" width="84" height="46"/><path d="M-10 -26 V2 H42 M-42 2 H-26 M14 2 V20"/></g>'
            f'<path d="M-26 2 a12 12 0 0 1 12 -12" fill="none" stroke="{FIX_ACC}" stroke-width=".9"/>'
            + mono(-42, 30, "PLAN · L2", 4.6, "rgba(16,16,20,.45)")),
        "iso": card("#0f1733",
            '<g transform="translate(0,2)"><polygon points="0,-24 28,-10 0,4 -28,-10" fill="#a5dcff"/>'
            '<polygon points="-28,-10 0,4 0,28 -28,14" fill="#3b82f6" fill-opacity=".85"/>'
            '<polygon points="28,-10 0,4 0,28 28,14" fill="#1d4ed8"/>'
            '<path d="M-28 -10 L0 4 L28 -10 M0 4 V28 M-28 2 L0 16 L28 2" fill="none" stroke="#dbeeff" stroke-opacity=".55" stroke-width=".6"/></g>',
            "rgba(255,255,255,.08)"),
        "code": card("#16161e",
            '<circle cx="-46" cy="-28" r="2" fill="#ff5f57"/><circle cx="-40" cy="-28" r="2" fill="#febc2e"/><circle cx="-34" cy="-28" r="2" fill="#28c840"/>'
            + "".join(f'<rect x="{-46+i0}" y="{-18+i*8.5}" width="{w}" height="3.6" rx="1.8" fill="{col}" fill-opacity=".9"/>'
                      for i, (i0, w, col) in enumerate(lines)),
            "rgba(255,255,255,.08)"),
        "chat": card("#15151c",
            f'<rect x="-14" y="-27" width="60" height="18" rx="7" fill="{FIX_ACC}"/><rect x="-8" y="-20" width="40" height="3.4" rx="1.7" fill="#fff" fill-opacity=".9"/>'
            '<rect x="-46" y="-3" width="72" height="30" rx="7" fill="#26262f"/>'
            '<path d="M-40 6 l1.2 -3 l1.2 3 l3 1.2 l-3 1.2 l-1.2 3 l-1.2 -3 l-3 -1.2 z" fill="#9cc2ff"/>'
            '<rect x="-31" y="3" width="48" height="3.4" rx="1.7" fill="#d4d4d8"/><rect x="-31" y="12" width="34" height="3.4" rx="1.7" fill="#71717a"/>',
            "rgba(255,255,255,.08)"),
        "rebar": card("#fbfaf7",
            '<rect x="-18" y="-28" width="36" height="56" fill="#ebe9e3" stroke="#101014" stroke-opacity=".7" stroke-width=".9"/>'
            f'<rect x="-13" y="-23" width="26" height="46" rx="3" fill="none" stroke="{FIX_ACC}" stroke-width=".9"/>'
            + "".join(f'<circle cx="{x}" cy="-17" r="2.3" fill="#101014"/>' for x in (-7, 0, 7))
            + "".join(f'<circle cx="{x}" cy="17" r="2.8" fill="#101014"/>' for x in (-7, 0, 7))
            + '<path d="M28 -28 V28 M25 -28 H31 M25 28 H31" stroke="#101014" stroke-opacity=".5" stroke-width=".6"/>'
            + mono(33, 2, "600", 4.6, "rgba(16,16,20,.45)")),
        "table": card("#fbfaf7",
            '<rect x="-46" y="-27" width="92" height="10" rx="2" fill="#e9e8e4"/>'
            + mono(-42, -20, "ID   CAT    LVL", 4.4, "rgba(16,16,20,.6)")
            + "".join(f'<path d="M-46 {y} H46" stroke="rgba(16,16,20,.12)"/>' for y in (-7, 3, 13, 23))
            + "".join(
                f'<rect x="-42" y="{y-7}" width="10" height="3" fill="#101014" fill-opacity=".5"/>'
                f'<rect x="-24" y="{y-7}" width="22" height="3" fill="#101014" fill-opacity=".3"/>'
                f'<rect x="8" y="{y-7}" width="12" height="3" fill="{FIX_ACC}" fill-opacity=".75"/>'
                for y in (3, 13, 23, 33))),
        "pot": card("#3a3a3e",
            '<rect x="-55" y="-36" width="110" height="26" fill="#d99d77"/>'
            '<rect x="-55" y="-36" width="110" height="14" fill="#5e5470"/>'
            '<polygon points="-3,-10 3,-10 70,36 -70,36" fill="#323137"/>'
            '<polygon points="-.6,-6 .6,-6 1.6,4 -1.6,4" fill="#f2f1ee" fill-opacity=".8"/>'
            '<polygon points="-2,10 2,10 3.4,24 -3.4,24" fill="#f2f1ee" fill-opacity=".8"/>'
            '<ellipse cx="-20" cy="18" rx="13" ry="4" fill="#17171a"/>'
            f'<path d="M-36 9 v-4 h4 M-4 9 v-4 h-4 M-36 25 v4 h4 M-4 25 v4 h-4" fill="none" stroke="{FIX_ACC}" stroke-width="1.1"/>'
            f'<rect x="-36" y="-2" width="36" height="7" fill="{FIX_ACC}"/>'
            + mono(-34, 3.4, "POTHOLE .94", 3.8, "#fff"),
            "rgba(255,255,255,.08)"),
        "sheet": card("#ffffff",
            '<rect x="-48" y="-30" width="96" height="60" fill="none" stroke="#101014" stroke-opacity=".35" stroke-width=".6"/>'
            '<path d="M-40 -22 H4 V8 H-40 Z M-18 -22 V-4 H4" fill="none" stroke="#101014" stroke-opacity=".5" stroke-width=".7"/>'
            '<rect x="14" y="12" width="30" height="14" fill="none" stroke="#101014" stroke-opacity=".35" stroke-width=".6"/>'
            '<path d="M14 19 H44 M29 19 V26" stroke="#101014" stroke-opacity=".3" stroke-width=".5"/>'
            f'<path d="M30 -24 l6 10 h-12 z" fill="none" stroke="{FIX_ACC}" stroke-width=".8"/>'),
    }
    return clip + "".join(f'<g id="h-{k}">{v}</g>' for k, v in c.items())


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
.h-o1{offset-path:path('M440,0 A380,300 0 1,1 440,600 A380,300 0 1,1 440,0');offset-rotate:0deg;animation:h-orb 84s linear infinite}
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
        f'<filter id="h-sh" x="-40%" y="-40%" width="180%" height="190%"><feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity="{T["shadow"]}"/></filter>'
        f'<linearGradient id="h-fl" x1="0" x2="1"><stop offset="0" stop-color="{bg}"/><stop offset="1" stop-color="{bg}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="h-fr" x1="0" x2="1"><stop offset="0" stop-color="{bg}" stop-opacity="0"/><stop offset="1" stop-color="{bg}" stop-opacity=".92"/></linearGradient>'
        '<clipPath id="h-wm"><rect x="0" y="104" width="880" height="106"/></clipPath>'
        + hero_cards() + "</defs>"
    )
    for rx, ry in [(250, 197), (380, 300), (470, 372), (600, 474), (740, 585)]:
        b.append(f'<ellipse cx="440" cy="300" rx="{rx}" ry="{ry}" fill="none" stroke="{ink}" stroke-opacity=".08"/>')
    b.append(f'<ellipse class="h-dash" cx="440" cy="300" rx="380" ry="300" fill="none" stroke="{T["acc"]}" stroke-opacity=".35" stroke-dasharray="2 14"/>')

    b.append('<g class="h-cards">')
    for i, k in enumerate(["sheet", "iso", "code", "plan", "chat", "rebar"]):
        b.append(f'<g class="h-o2" style="offset-distance:{(1 - i / 6) * 100:.2f}%;animation-delay:-{i*21}s"><use href="#h-{k}" transform="scale(.76)" opacity=".72"/></g>')
    for i, k in enumerate(["plan", "code", "rebar", "chat", "iso", "table", "pot"]):
        b.append(f'<g class="h-o1" style="offset-distance:{i*100/7:.2f}%;animation-delay:-{i*12}s"><use href="#h-{k}" filter="url(#h-sh)"/></g>')
    b.append("</g>")
    b.append('<rect x="0" y="0" width="70" height="600" fill="url(#h-fl)"/><rect x="790" y="0" width="90" height="600" fill="url(#h-fr)"/>')

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

    n = [f'<rect width="{W}" height="44" fill="{bg}"/><path d="M0 44.5 H880" stroke="{line}"/>', mark(15, 12)]
    n.append(f'<path d="M52.5 0 V44" stroke="{line}"/>')
    n.append(f'<rect x="62" y="13" width="44" height="18" fill="{ink}"/>' + mono(68, 25.5, "HOME", 9.5, bg))
    for x, s in [(124, "WORK"), (176, "JOURNEY"), (250, "WRITING"), (324, "ACTIVITY"), (405, "CONTACT")]:
        n.append(mono(x, 25.5, s, 9.5, T["muted"]))
    n.append(f'<path d="M548.5 0 V44 M710.5 0 V44 M756.5 0 V44" stroke="{line}"/>')
    n.append(mono(566, 25.5, "GITHUB", 9.5, T["muted"]) + mono(633, 25.5, "LINKEDIN", 9.5, T["muted"]))
    n.append(f'<path d="M731 16 a7 7 0 1 0 6 10 a5.5 5.5 0 1 1 -6 -10 z" fill="none" stroke="{ink}" stroke-width="1.1"/>')
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
    f = [f'<path d="M0 .5 H880 M0 232.5 H880" stroke="{line}"/>', mark(32, 34, 1.3)]
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
