"""Draw every image in assets/ (light and dark) and write README.md.

Usage: python scripts/render.py
Needs data/contributions.json, written by fetch_contributions.py.
"""
import json
from pathlib import Path

import activity
import fontkit
import panels as pn

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
BLOG = "https://ldatuan.com"
GH = "https://github.com/LDATuan"
LINKEDIN = "https://www.linkedin.com/in/tuanle-97/"

WORK = [
    ("revitapi-learning", f"{GH}/RevitAPI-Learning", "REVIT ADD-IN", "01", "RevitAPI-Learning",
     "Crop views and rebar solids as WPF MVVM tools. Where the blog's first post came from.", pn.ill_crop),
    ("autocadrebar", f"{GH}/AutoCadRebar", "AUTOCAD ADD-IN", "02", "AutoCadRebar",
     "Beam sections, rebar, dimensions and tags, generated from data instead of drawn by hand.", pn.ill_rebar),
    ("multiversion", f"{GH}/multiversion-same-assembly", ".NET PLUMBING", "03", "multiversion-same-assembly",
     "One assembly, several versions, one host app. Strong naming and binding redirects so they stop colliding.", pn.ill_multi),
    ("revit-agent", f"{BLOG}/about", "AI AGENT · IN PROGRESS", "04", "Revit agent",
     "Operate the model by asking for things instead of clicking through dialogs.", pn.ill_agent),
    ("agent-drawing", f"{BLOG}/about", "DOCUMENTS · IN PROGRESS", "05", "Agent Drawing",
     "Pulls the key information out of drawings and project documents.", pn.ill_doc),
    ("pothole", f"{GH}/pothole", "COMPUTER VISION", "06", "pothole",
     "Pothole detection with YOLOv6, with a separate client and server.", pn.ill_pothole),
]

POSTS = [
    ("post-rlhf", f"{BLOG}/article/rlhf-and-ppo", "AUG 2026 · 12 MIN · ML", "How RLHF Works, and Why It Uses PPO", pn.th_rlhf),
    ("post-math", f"{BLOG}/article/math-foundations-for-machine-learning", "AUG 2026 · 12 MIN · ML",
     "The Math You Actually Need for Machine Learning", pn.th_math),
    ("post-crop-view", f"{BLOG}/article/how-to-crop-view-with-revitapi", "AUG 2022 · 2 MIN · REVIT API",
     "How To Crop View With RevitAPI", pn.th_crop),
]


def build(data):
    """Return {asset name: svg markup} for the active theme."""
    out = {"hero": pn.hero()}
    out["work"] = pn.section(
        "s1", "01", "SELECTED WORK", "REAL CODE — ON GITHUB",
        [[("Drawings in,", "h")], [("data", "s"), (" out.", "h")]],
        "I work where a building model stops being drawings and starts being data. "
        "Revit add-ins, model data on the web, and agents for the boring parts.", 0)
    for i, (name, _href, label, idx, title, body, ill) in enumerate(WORK):
        out[f"card-{name}"] = pn.work_card(f"w{i}", label, idx, title, body, ill)
    out["journey"] = pn.section(
        "s2", "02", "JOURNEY", "CIVIL ENGINEER — SOFTWARE ENGINEER",
        [[("From ", "h"), ("concrete", "s")], [("to code.", "h")]],
        "Five years studying civil engineering, then six writing software for the same industry, "
        "for teams in Saigon, Tokyo and Singapore.", 1, extra=pn.timeline_block())
    out["writing"] = pn.section(
        "s3", "03", "WRITING", "LDATUAN.COM — EN / VI",
        [[("Written ", "h"), ("down", "s"), (",", "h")], [("for the next person.", "h")]],
        "Mostly things I could not find written down anywhere else. Revit API, C#, and lately the maths behind LLMs.", 2)
    for i, (name, _href, meta, title, thumb) in enumerate(POSTS):
        out[name] = pn.writing_card(f"a{i}", meta, title, thumb, f"0{i+1}")
    out["activity"] = activity.render(data)
    out.update(pn.closing_windows())
    return out


def pct(px, total=880):
    # floor to 4 decimals so a row never adds up to more than 100%
    return f"{int(px / total * 1_000_000) / 10_000}%"


def picture(name, alt, width, href=None):
    img = (f'<picture><source media="(prefers-color-scheme: dark)" srcset="./assets/{name}-dark.svg">'
           f'<img src="./assets/{name}-light.svg" width="{width}" align="top" alt="{pn.esc(alt)}"></picture>')
    return f'<a href="{href}">{img}</a>' if href else img


def readme():
    rows = [
        [picture("hero", "LDATUAN. Software for buildings. Civil engineer turned software engineer.", "100%", BLOG)],
        [picture("work", "01 Selected work. Drawings in, data out.", "100%")],
    ]
    for i in range(0, len(WORK), 2):
        rows.append([picture(f"card-{w[0]}", f"{w[4]}: {w[5]}", "50%", w[1]) for w in WORK[i:i + 2]])
    rows.append([picture("journey", "02 Journey. From concrete to code: HCMUT, BIM Factory, Arent, Tiong Seng, agents for AEC.", "100%")])
    rows.append([picture("writing", "03 Writing. Written down, for the next person.", "100%")])
    rows.append([picture(p[0], f"Article: {p[3]}", "33.3333%", p[1]) for p in POSTS])
    rows.append([picture("activity", "04 Activity. Contribution calendar drawn as an isometric city.", "100%", f"{GH}?tab=overview")])
    rows.append([picture("cta-top", "Start building.", "100%", BLOG)])
    widths = [pct(x1 - x0) for x0, x1 in pn.BTN_COLS]
    rows.append([
        picture("cta-left", " ", widths[0], BLOG),
        picture("cta-blog", "Visit the blog", widths[1], BLOG),
        picture("cta-linkedin", "LinkedIn", widths[2], LINKEDIN),
        picture("cta-right", " ", widths[3], LINKEDIN),
    ])
    rows.append([picture("cta-bottom", "Footer: stack, work, writing and links.", "100%", BLOG)])

    body = "\n".join("".join(r) for r in rows)
    return f"""<!-- Generated by scripts/render.py. Edit the script, not this file. -->

<p>
{body}
</p>
"""


def main():
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    ASSETS.mkdir(exist_ok=True)
    sizes = {}
    for theme in (pn.LIGHT, pn.DARK):
        pn.use(theme)
        for name, markup in build(data).items():
            path = ASSETS / f"{name}-{theme['name']}.svg"
            path.write_text(fontkit.embed(markup), encoding="utf-8")
            sizes[path.name] = path.stat().st_size
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")
    total = sum(sizes.values())
    print(f"wrote {len(sizes)} images, {total/1024:.0f} KB, largest {max(sizes, key=sizes.get)} ({max(sizes.values())/1024:.0f} KB)")


if __name__ == "__main__":
    main()
