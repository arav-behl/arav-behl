"""Render every profile card from data/contributions.json into cards/."""

from __future__ import annotations

import json
import sys
from datetime import date

from board import render_board
from cards import REPOS, render_activity, render_hero, render_repo, render_title
from svg_kit import ROOT, write

START = date(2026, 5, 1)
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "cards"


def main() -> int:
    days = json.loads(DATA.read_text())["days"]
    write(OUT / "hero.svg", render_hero())
    write(OUT / "board.svg", render_board(days, START))
    write(OUT / "activity.svg", render_activity(days, START))
    write(OUT / "title-built.svg", render_title("What I've", "built"))
    for i, (name, slug, language, blurb) in enumerate(REPOS):
        write(OUT / f"repo-{slug.lower().replace('_', '-')}.svg", render_repo(i, name, language, blurb))
    print(f"rendered cards into {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
