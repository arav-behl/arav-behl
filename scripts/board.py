"""Snakes-and-ladders board: one tile per day, a mouse walks from the first day to today.

Ladders climb from my busiest days, snakes slide down from quiet ones. Layout is
boustrophedon like a real board: row 0 runs left to right along the bottom, row 1
runs right to left above it, and so on.
"""

from __future__ import annotations

import math
from datetime import date

from svg_kit import (ACCENT, ACCENT_DEEP, FAINT, GAP, HEAT, INK, LINE, MUTED, WIDTH, kicker,
                     panel, svg_doc, text)

COLS = 28
PAD_X = 40
PITCH = (WIDTH - 2 * PAD_X) / COLS
TILE = PITCH - 4
HEADER_H = 138
FOOTER_H = 58
MAX_LADDERS = 4
MAX_SNAKES = 3
WALK_SECONDS = 16
HOLD_FRACTION = 0.86  # share of the loop spent walking; the rest the mouse rests on today


def _cell_xy(index: int, board_top: float, rows: int) -> tuple[float, float]:
    row, col = divmod(index, COLS)
    visual_col = col if row % 2 == 0 else COLS - 1 - col
    x = PAD_X + visual_col * PITCH + PITCH / 2
    y = board_top + (rows - 1 - row) * PITCH + PITCH / 2
    return x, y


def _index_at(row: int, visual_col: int) -> int:
    col = visual_col if row % 2 == 0 else COLS - 1 - visual_col
    return row * COLS + col


def _visual_col(index: int) -> int:
    row, col = divmod(index, COLS)
    return col if row % 2 == 0 else COLS - 1 - col


def _collides(start: int, end: int, placed: list[tuple[int, int]]) -> bool:
    """True if a new jump would sit within 3 columns of an existing one over shared rows."""
    rows = {start // COLS, end // COLS}
    cols = {_visual_col(start), _visual_col(end)}
    for a, b in placed:
        other_rows = range(min(a, b) // COLS, max(a, b) // COLS + 1)
        near = any(abs(c - _visual_col(x)) <= 3 for c in cols for x in (a, b))
        if near and any(r in other_rows for r in range(min(rows), max(rows) + 1)):
            return True
    return False


def _pick_jumps(days: list[dict], ranked: list[int], direction: int, limit: int,
                taken: set[int], placed: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Pick start->end jumps of 1-2 rows (up for ladders, down for snakes) that don't collide."""
    jumps: list[tuple[int, int]] = []
    for start in ranked:
        row = start // COLS
        if start in taken:
            continue
        for span in (2, 1):
            target_row = row + direction * span
            shift = 1 if _visual_col(start) < COLS - 2 else -1
            end = _index_at(target_row, _visual_col(start) + shift) if target_row >= 0 else -1
            if 0 <= end < len(days) and end not in taken and not _collides(start, end, placed):
                jumps.append((start, end))
                placed.append((start, end))
                taken.update({start, end})
                break
        if len(jumps) == limit:
            break
    return jumps


def _ladder(x1: float, y1: float, x2: float, y2: float) -> str:
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * 5.5, dx / length * 5.5
    rails = "".join(
        f'<line x1="{x1 + s * nx:.1f}" y1="{y1 + s * ny:.1f}" x2="{x2 + s * nx:.1f}" '
        f'y2="{y2 + s * ny:.1f}"/>' for s in (-1, 1)
    )
    rungs = []
    steps = int(length // 9)
    for k in range(1, steps):
        t = k / steps
        cx, cy = x1 + dx * t, y1 + dy * t
        rungs.append(f'<line x1="{cx - nx:.1f}" y1="{cy - ny:.1f}" x2="{cx + nx:.1f}" y2="{cy + ny:.1f}"/>')
    return (f'<g stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity=".72">'
            f'{rails}{"".join(rungs)}</g>')


def _snake(x1: float, y1: float, x2: float, y2: float) -> str:
    """Head at (x1, y1) on the quiet day, tail at (x2, y2) lower down."""
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    nx, ny = -dy / length * 14, dx / length * 14
    c1 = (x1 + dx * 0.33 + nx, y1 + dy * 0.33 + ny)
    c2 = (x1 + dx * 0.66 - nx, y1 + dy * 0.66 - ny)
    d = f"M{x1:.1f},{y1:.1f} C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {x2:.1f},{y2:.1f}"
    angle = math.degrees(math.atan2(-dy, -dx))
    return (
        f'<path d="{d}" fill="none" stroke="{ACCENT_DEEP}" stroke-width="7" stroke-linecap="round"/>'
        f'<path d="{d}" fill="none" stroke="#f0b9a6" stroke-width="2.4" stroke-linecap="round" '
        f'stroke-dasharray="3 7"/>'
        f'<g transform="translate({x1:.1f},{y1:.1f}) rotate({angle:.1f})">'
        f'<ellipse cx="2" cy="0" rx="7" ry="5.5" fill="{ACCENT_DEEP}"/>'
        f'<circle cx="5" cy="-2.2" r="1.2" fill="#fff"/><circle cx="5" cy="2.2" r="1.2" fill="#fff"/>'
        f'<path d="M9,0 l4,-1.6 M9,0 l4,1.6" stroke="{ACCENT}" stroke-width="1"/></g>'
    )


MOUSE = (
    f'<path d="M-8,0 C-14,0 -16,6 -22,5" fill="none" stroke="{MUTED}" stroke-width="1.6" '
    f'stroke-linecap="round"/>'
    f'<ellipse cx="0" cy="0" rx="8.5" ry="6" fill="#8d877c"/>'
    f'<circle cx="4.5" cy="-5" r="3.4" fill="#d8b4a6" stroke="#8d877c" stroke-width="1.4"/>'
    f'<circle cx="4.5" cy="5" r="3.4" fill="#d8b4a6" stroke="#8d877c" stroke-width="1.4"/>'
    f'<ellipse cx="8" cy="0" rx="5" ry="4.2" fill="#8d877c"/>'
    f'<circle cx="9.6" cy="-1.9" r="1" fill="{INK}"/><circle cx="9.6" cy="1.9" r="1" fill="{INK}"/>'
    f'<circle cx="13" cy="0" r="1.4" fill="{ACCENT}"/>'
)


def _tiles(days: list[dict], rows: int, board_top: float) -> str:
    parts = []
    for i in range(rows * COLS):
        x, y = _cell_xy(i, board_top, rows)
        left, top = x - TILE / 2, y - TILE / 2
        delay = 0.25 + i * 0.004
        if i >= len(days):
            parts.append(f'<rect class="fade" style="animation-delay:{delay:.2f}s" x="{left:.1f}" '
                         f'y="{top:.1f}" width="{TILE:.1f}" height="{TILE:.1f}" rx="5" fill="none" '
                         f'stroke="{LINE}" stroke-width="1.2" stroke-dasharray="3 3"/>')
            continue
        level = days[i]["level"]
        parts.append(f'<rect class="fade" style="animation-delay:{delay:.2f}s" x="{left:.1f}" '
                     f'y="{top:.1f}" width="{TILE:.1f}" height="{TILE:.1f}" rx="5" fill="{HEAT[level]}"/>')
        day = date.fromisoformat(days[i]["date"])
        if day.day == 1:
            colour = "#fff" if level >= 3 else INK
            parts.append(text(x, y + 3.5, day.strftime("%b").upper(), "mono", 8, colour, "middle"))
    return "".join(parts)


def _walk(days: list[dict], rows: int, board_top: float) -> str:
    points = [_cell_xy(i, board_top, rows) for i in range(len(days))]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    length = PITCH * (len(points) - 1)
    timing = (f'dur="{WALK_SECONDS}s" repeatCount="indefinite" calcMode="linear" '
              f'keyTimes="0;{HOLD_FRACTION};1"')
    end_x, end_y = points[-1]
    return (
        f'<path d="{path}" fill="none" stroke="{INK}" stroke-opacity=".28" stroke-width="2" '
        f'stroke-linejoin="round" stroke-dasharray="{length:.1f}" stroke-dashoffset="{length:.1f}">'
        f'<animate attributeName="stroke-dashoffset" values="{length:.1f};0;0" {timing}/></path>'
        f'<circle class="pulse" cx="{end_x:.1f}" cy="{end_y:.1f}" r="{TILE / 2 + 3:.1f}" fill="none" '
        f'stroke="{ACCENT}" stroke-width="2"/>'
        f'<g><animateMotion path="{path}" rotate="auto" keyPoints="0;1;1" {timing}/>{MOUSE}</g>'
    )


def render_board(days: list[dict], start: date) -> str:
    days = [d for d in days if date.fromisoformat(d["date"]) >= start]
    rows = math.ceil(len(days) / COLS)
    board_top = HEADER_H
    height = HEADER_H + rows * PITCH + FOOTER_H
    total = sum(d["count"] for d in days)

    taken: set[int] = {0, len(days) - 1}
    busiest = sorted(range(len(days)), key=lambda i: -days[i]["count"])
    quiet = [i for i in range(len(days)) if days[i]["count"] == 0][::-1]
    placed: list[tuple[int, int]] = []
    ladders = _pick_jumps(days, busiest, +1, MAX_LADDERS, taken, placed)
    snakes = _pick_jumps(days, quiet, -1, MAX_SNAKES, taken, placed)

    xy = lambda i: _cell_xy(i, board_top, rows)  # noqa: E731
    jumps = "".join(_ladder(*xy(a), *xy(b)) for a, b in ladders)
    jumps += "".join(_snake(*xy(a), *xy(b)) for a, b in snakes)

    title = (f'<text x="{PAD_X}" y="82" class="serif rise" font-size="40" fill="{INK}" '
             f'style="animation-delay:.1s">Every day since {start:%B}, '
             f'<tspan class="italic" fill="{ACCENT}">as a board game</tspan></text>')
    sub = text(PAD_X, 108, f"{total:,} contributions across {len(days)} days. Ladders climb from my "
               "busiest days; snakes slide from the quiet ones.", "sans rise", 13.5, MUTED, delay=0.2)
    foot_y = height - GAP - 22
    legend = (
        text(PAD_X, foot_y, f"START · {start:%d %b %Y}".upper(), "mono", 10.5, FAINT)
        + text(WIDTH - PAD_X, foot_y, f"TODAY · {days[-1]['date']}".upper(), "mono", 10.5, FAINT, "end")
    )
    body = (
        panel(WIDTH, height - GAP)
        + kicker(PAD_X, 42, "Refreshed daily")
        + title + sub
        + f'<g>{_tiles(days, rows, board_top)}</g>'
        + f'<g class="fade" style="animation-delay:1.1s">{jumps}</g>'
        + _walk(days, rows, board_top)
        + legend
    )
    label = (f"Snakes and ladders board of {len(days)} days of GitHub contributions since "
             f"{start:%B %Y}; a mouse walks from the first day to today.")
    return svg_doc(round(height), label, body, ("serif", "serif-italic", "sans", "mono"))
