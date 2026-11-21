"""Fetch the public GitHub contribution calendar (no auth) into data/contributions.json."""

from __future__ import annotations

import json
import re
import sys
import urllib.request
from pathlib import Path

USER = "arav-behl"
URL = f"https://github.com/users/{USER}/contributions"
OUT = Path(__file__).resolve().parent.parent / "data" / "contributions.json"

CELL_RE = re.compile(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*id="([^"]+)"[^>]*data-level="(\d)"')
TIP_RE = re.compile(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>')
COUNT_RE = re.compile(r"^(\d[\d,]*) contribution")


def fetch_html(url: str = URL) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-cards"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse(html: str) -> list[dict]:
    tips = dict(TIP_RE.findall(html))
    days = []
    for date, cell_id, level in CELL_RE.findall(html):
        match = COUNT_RE.match(tips.get(cell_id, "").strip())
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": date, "count": count, "level": int(level)})
    if not days:
        raise ValueError("no contribution cells found; GitHub markup may have changed")
    return sorted(days, key=lambda d: d["date"])


def main() -> int:
    days = parse(fetch_html())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"user": USER, "days": days}, indent=1))
    print(f"wrote {len(days)} days to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
