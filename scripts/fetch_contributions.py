"""Fetch a user's public contribution calendar and save it as JSON.

Uses the same HTML fragment github.com renders on the profile page, so it
needs no token. Fails loudly (exit 1) instead of writing partial data.

Usage: python scripts/fetch_contributions.py LDATuan data/contributions.json
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

DAY_RE = re.compile(r"<td\b[^>]*?\bdata-date=\"(\d{4}-\d\d-\d\d)\"[^>]*>")
ID_RE = re.compile(r'\bid="(contribution-day-component-\d+-\d+)"')
LEVEL_RE = re.compile(r'\bdata-level="(\d)"')
TIP_RE = re.compile(r'<tool-tip\b[^>]*\bfor="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>')
COUNT_RE = re.compile(r"([\d,]+) contributions?\b")


def fetch(user: str) -> str:
    req = urllib.request.Request(
        f"https://github.com/users/{user}/contributions",
        headers={"User-Agent": "profile-readme-renderer", "Accept": "text/html"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(html: str) -> list[dict]:
    cells = {}
    for m in DAY_RE.finditer(html):
        tag = m.group(0)
        cid, lvl = ID_RE.search(tag), LEVEL_RE.search(tag)
        if cid:
            cells[cid.group(1)] = {"date": m.group(1), "count": 0, "level": int(lvl.group(1)) if lvl else 0}
    for m in TIP_RE.finditer(html):
        if m.group(1) in cells:
            n = COUNT_RE.match(m.group(2).strip())
            cells[m.group(1)]["count"] = int(n.group(1).replace(",", "")) if n else 0
    return sorted(cells.values(), key=lambda d: d["date"])


def main():
    user, out = sys.argv[1], Path(sys.argv[2])
    days = parse(fetch(user))
    if len(days) < 300:
        sys.exit(f"expected about a year of days, got {len(days)}; GitHub may have changed the markup")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"user": user, "days": days}, indent=1) + "\n")
    print(f"{len(days)} days, {sum(d['count'] for d in days):,} contributions, {days[0]['date']} to {days[-1]['date']}")


if __name__ == "__main__":
    main()
