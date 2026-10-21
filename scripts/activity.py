"""The contribution calendar, redrawn as an isometric city.

Each day is a block on a 53 x 7 grid. Height and colour follow the day's
count on a square-root scale, so a handful of huge days does not flatten the
rest. Data comes from data/contributions.json (see fetch_contributions.py).
"""
import datetime as dt
import math

import panels
from panels import T, esc, mono, svg

PALETTES = {
    "light": dict(z=("#e4e2dc", "#d8d5ce", "#cdc9c1"), lo="#d3e2fb", mid="#5d9cff", hi="#0b3fa8",
                  shade=(0.13, 0.25), edge="rgba(255,255,255,.55)", shadow=("#101014", .10)),
    "dark": dict(z=("#1e1e25", "#18181e", "#131318"), lo="#1a2a47", mid="#2f6fe0", hi="#9fd0ff",
                 shade=(0.28, 0.45), edge="rgba(255,255,255,.08)", shadow=("#000000", .45)),
}

CSS = """
.k-b{transform-box:view-box;animation:k-rise .8s cubic-bezier(.2,1.25,.4,1) both}
@keyframes k-rise{from{transform:scaleY(0)}}
.k-up{animation:k-up .8s cubic-bezier(.2,.8,.2,1) both}
@keyframes k-up{from{opacity:0;transform:translateY(10px)}}
.k-odo{animation:k-odo 1.8s cubic-bezier(.15,.85,.25,1) .2s both}
@keyframes k-odo{from{transform:translateY(var(--n))}}
.k-pin{stroke-dasharray:80;animation:k-pin .6s ease-out 2.6s both}
@keyframes k-pin{from{stroke-dashoffset:80}}
.k-pulse{transform-box:fill-box;transform-origin:center;animation:k-pulse 1.8s ease-out 2.4s infinite}
@keyframes k-pulse{0%{transform:scale(.5);opacity:.8}100%{transform:scale(2.6);opacity:0}}
.k-sec{opacity:0;animation:k-sec 10s cubic-bezier(.45,0,.55,1) 3.2s infinite both}
@keyframes k-sec{0%{transform:translate(0,0);opacity:0}6%{opacity:1}68%{opacity:1}74%{transform:translate(var(--dx),var(--dy));opacity:0}100%{transform:translate(var(--dx),var(--dy));opacity:0}}
.k-sh{animation:k-shf 1s ease 2.2s both}
@keyframes k-shf{from{opacity:0}}
"""

AX, AY = 13.0, 2.0      # one week step on screen
BX, BY = -6.0, 9.0      # one day step on screen
X0, Y0 = 96.0, 266.0    # week 0, Sunday (back-left corner)
MAXH = 112.0
F = 0.80                # block footprint inside its cell
G = (1 - F) / 2


def _hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _mix(a, b, t):
    a, b = _hexrgb(a), _hexrgb(b)
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x + (y - x) * t))) for x, y in zip(a, b))


def _pt(w, d, h=0.0):
    return (X0 + w * AX + d * BX, Y0 + w * AY + d * BY - h)


def _pts(*ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def _hull(points):
    pts = sorted(set(points))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lo, up = [], []
    for q in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def _day(date):
    return f"{date:%b} {date.day}".upper()


def render(data):
    pal = PALETTES[T["name"]]
    days = [dict(d) for d in data["days"]]
    total = sum(d["count"] for d in days)
    start = dt.date.fromisoformat(days[0]["date"])
    for d in days:
        off = (dt.date.fromisoformat(d["date"]) - start).days
        d["w"], d["d"] = off // 7, off % 7  # d: 0 = Sunday, GitHub's row order
    nw = max(d["w"] for d in days) + 1
    maxc = max(1, max(d["count"] for d in days))
    best = max(days, key=lambda d: d["count"])
    best_date = dt.date.fromisoformat(best["date"])

    streak, s_from, s_to, run, run_start = 0, days[0], days[0], 0, None
    for d in days:
        if d["count"]:
            run += 1
            run_start = run_start or d
            if run > streak:
                streak, s_from, s_to = run, run_start, d
        else:
            run, run_start = 0, None
    active = sum(1 for d in days if d["count"])
    weekend = sum(d["count"] for d in days if d["d"] in (0, 6))
    weekend_pct = round(weekend * 100 / total) if total else 0

    def height(c):
        return 1.6 if c == 0 else 4 + (MAXH - 4) * (c / maxc) ** 0.5

    def tone(c):
        t = (c / maxc) ** 0.42
        if t < 0.55:
            return _mix(pal["lo"], pal["mid"], t / 0.55)
        return _mix(pal["mid"], pal["hi"], (t - 0.55) / 0.45)

    acc, faint, line, strong = T["acc"], T["faint"], T["line"], T["strong"]
    W, H = 880, 500
    b = [f'<rect width="{W}" height="{H}" fill="{T["bg"]}"/>']
    b.append(f'<path d="M0 .5 H880 M0 35.5 H880 M0 {H-.5} H880" stroke="{line}"/>')
    b.append(mono(32, 22.5, "04 / ACTIVITY", 9.5) + mono(848, 22.5, "REAL DATA — REDRAWN NIGHTLY", 9.5, faint, "end"))

    # rolling odometer for the total
    base = 132
    b.append(f'<defs><clipPath id="k-clip"><rect x="0" y="{base-60}" width="560" height="66"/></clipPath></defs>')
    x, col = 32, []
    for ch in f"{total:,}":
        if ch == ",":
            col.append(f'<text class="fw" x="{x}" y="{base}" font-size="72" fill="{strong}">,</text>')
            x += 24
            continue
        t = int(ch)
        rows = "".join(
            f'<text class="fw" x="{x+26}" y="{base + (k - (10 + t)) * 72}" font-size="72" fill="{strong}" text-anchor="middle">{k % 10}</text>'
            for k in range(20))
        col.append(f'<g class="k-odo" style="--n:{(10 + t) * 72}px">{rows}</g>')
        x += 54
    b.append(f'<g clip-path="url(#k-clip)">{"".join(col)}</g>')
    tail = "mostly on weekends." if weekend_pct >= 50 else "in the last year."
    b.append(
        f'<g class="k-up" style="animation-delay:.6s"><text x="32" y="{base+40}">'
        f'<tspan class="fh" font-size="28" fill="{strong}" letter-spacing="-.8">contributions, </tspan>'
        f'<tspan class="fs" font-size="31" fill="{T["muted"]}">{tail}</tspan></text></g>')

    # stats grid
    gx, gy, cw, chh = 556, 60, 146, 70
    stats = [
        ("LONGEST STREAK", str(streak), " days" if streak != 1 else " day",
         f"{_day(dt.date.fromisoformat(s_from['date']))} – {_day(dt.date.fromisoformat(s_to['date']))}"),
        ("BUSIEST DAY", str(best["count"]), "", f"{best_date:%a}".upper() + f" · {_day(best_date)}, {best_date.year}"),
        ("ACTIVE DAYS", str(active), "", f"OF {len(days)} DAYS"),
        ("ON WEEKENDS", f"{weekend_pct}%", "", f"{weekend:,} OF {total:,}"),
    ]
    g = ['<g class="k-up" style="animation-delay:.9s">',
         f'<rect x="{gx+.5}" y="{gy+.5}" width="{cw*2-1}" height="{chh*2-1}" fill="none" stroke="{line}"/>',
         f'<path d="M{gx+cw+.5} {gy} V{gy+chh*2} M{gx} {gy+chh+.5} H{gx+cw*2}" stroke="{line}"/>']
    for i, (lab, val, unit, sub) in enumerate(stats):
        cx, cy = gx + (i % 2) * cw, gy + (i // 2) * chh
        g.append(mono(cx + 14, cy + 19, lab, 7.5))
        g.append(f'<text x="{cx+14}" y="{cy+48}"><tspan class="fh" font-size="27" fill="{strong}" letter-spacing="-.6">{val}</tspan>'
                 + (f'<tspan class="fs" font-size="19" fill="{T["muted"]}">{unit}</tspan>' if unit else "") + "</text>")
        g.append(mono(cx + 14, cy + 62, sub, 6.8))
    g.append("</g>")
    b.extend(g)

    # ground plate, cast shadows, blocks
    b.append(f'<polygon points="{_pts(_pt(0, 0), _pt(nw, 0), _pt(nw, 7), _pt(0, 7))}" fill="none" stroke="{line}" stroke-dasharray="2 4"/>')
    sh = []
    for d in days:
        if not d["count"]:
            continue
        w, r, h = d["w"], d["d"], height(d["count"])
        foot = [_pt(w + G, r + G), _pt(w + G + F, r + G), _pt(w + G + F, r + G + F), _pt(w + G, r + G + F)]
        cast = [(px + h * .42, py + h * .16) for px, py in foot]
        sh.append(f'<polygon points="{_pts(*_hull([(round(px, 1), round(py, 1)) for px, py in foot + cast]))}"/>')
    b.append(f'<g class="k-sh" fill="{pal["shadow"][0]}" fill-opacity="{pal["shadow"][1]}">{"".join(sh)}</g>')

    blocks = []
    for d in sorted(days, key=lambda d: (d["d"], d["w"])):
        w, r, c = d["w"], d["d"], d["count"]
        h = height(c)
        w0, w1, r0, r1 = w + G, w + G + F, r + G, r + G + F
        if c == 0:
            top, front, right = pal["z"]
        else:
            top = tone(c)
            front, right = _mix(top, "#000000", pal["shade"][0]), _mix(top, "#000000", pal["shade"][1])
        a, bb, cc, dd = _pt(w0, r0), _pt(w1, r0), _pt(w1, r1), _pt(w0, r1)
        at, bt, ct, dtp = _pt(w0, r0, h), _pt(w1, r0, h), _pt(w1, r1, h), _pt(w0, r1, h)
        ox, oy = _pt(w + .5, r + .5)
        blocks.append(
            f'<g class="k-b" style="transform-origin:{ox:.1f}px {oy:.1f}px;animation-delay:{0.35 + w * 0.032 + r * 0.012:.2f}s">'
            f'<polygon points="{_pts(dd, cc, ct, dtp)}" fill="{front}"/>'
            f'<polygon points="{_pts(bb, cc, ct, bt)}" fill="{right}"/>'
            f'<polygon points="{_pts(at, bt, ct, dtp)}" fill="{top}" stroke="{pal["edge"]}" stroke-width=".4"/></g>')
    b.append("".join(blocks))

    # section plane sweeping along the weeks, like a Revit section box
    hgt = 78
    pa, pb = _pt(0, -0.2), _pt(0, 7.2)
    b.append(
        f'<g class="k-sec" style="--dx:{AX*nw:.1f}px;--dy:{AY*nw:.1f}px">'
        f'<polygon points="{_pts(pa, pb, (pb[0], pb[1]-hgt), (pa[0], pa[1]-hgt))}" fill="{acc}" fill-opacity=".09" stroke="{acc}" stroke-opacity=".7" stroke-width=".9"/>'
        f'<path d="M{pb[0]:.1f} {pb[1]:.1f} l-10 3" fill="none" stroke="{acc}" stroke-width=".9"/>'
        f'<circle cx="{pb[0]-14:.1f}" cy="{pb[1]+4:.1f}" r="4" fill="{T["bg"]}" stroke="{acc}" stroke-width=".9"/>'
        f'<path d="M{pb[0]-14:.1f} {pb[1]:.1f} l3 4 h-6 z" fill="{acc}"/></g>')

    for r, lab in [(1, "MON"), (3, "WED"), (5, "FRI")]:
        px, py = _pt(0, r + .5)
        b.append(mono(px - 12, py + 3, lab, 7.5, faint, "end"))
    seen = set()
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        if (date.year, date.month) in seen or date.day > 7:
            continue
        seen.add((date.year, date.month))
        px, py = _pt(d["w"] + .5, 7)
        b.append(mono(px, py + 17, f"{date:%b}".upper(), 7.5, faint, "middle"))

    if streak > 1:
        (x0, y0), (x1, y1) = _pt(s_from["w"], 7), _pt(s_to["w"] + 1, 7)
        off = 30
        b.append(f'<g class="k-up" style="animation-delay:2.4s"><path d="M{x0:.1f} {y0+off-4:.1f} L{x0:.1f} {y0+off:.1f} L{x1:.1f} {y1+off:.1f} L{x1:.1f} {y1+off-4:.1f}" fill="none" stroke="{acc}" stroke-width="1.2"/>'
                 + mono((x0 + x1) / 2, (y0 + y1) / 2 + off + 13, f"{streak}-DAY STREAK", 7, acc, "middle") + "</g>")

    if best["count"]:
        bx, by = _pt(best["w"] + .5, best["d"] + .5, height(best["count"]))
        tx, ty = bx - 70, by - 34
        b.append(f'<path class="k-pin" d="M{bx:.1f} {by:.1f} L{bx:.1f} {ty:.1f} L{tx:.1f} {ty:.1f}" fill="none" stroke="{T["ink"]}" stroke-opacity=".55" stroke-width=".8"/>')
        b.append(f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="2.2" fill="{T["ink"]}"/>')
        b.append('<g class="k-up" style="animation-delay:3s">' + mono(tx - 4, ty + 3, f"{best['count']} ON {_day(best_date)}", 7.5, T["ink"], "end") + "</g>")

    today = days[-1]
    tx, ty = _pt(today["w"] + .5, today["d"] + .5, height(today["count"]))
    b.append(f'<circle class="k-pulse" cx="{tx:.1f}" cy="{ty:.1f}" r="4" fill="none" stroke="{acc}" stroke-width="1.2"/>')
    b.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="2.2" fill="{acc}"/>')

    lx, ly = 848, 474
    sw = []
    for i, c in enumerate(reversed([0, 2, 12, 50, maxc])):
        top = pal["z"][0] if c == 0 else tone(min(c, maxc))
        sw.append(f'<rect x="{lx-44-i*16}" y="{ly-9}" width="10" height="10" rx="1.5" fill="{top}"/>')
    b.append(mono(lx, ly, "MORE", 7.5, faint, "end") + "".join(sw) + mono(lx - 34 - 5 * 16 - 4, ly, "LESS", 7.5, faint, "end"))
    end = dt.date.fromisoformat(days[-1]["date"])
    b.append(mono(32, ly, f"{_day(start)}, {start.year} — {_day(end)}, {end.year}", 7.5))

    label = (f"{total:,} contributions in the last year, {weekend_pct}% on weekends. Longest streak {streak} days. "
             f"Busiest day: {best['count']} on {best_date:%B} {best_date.day}, {best_date.year}.")
    return svg(W, H, "".join(b), CSS, label)
