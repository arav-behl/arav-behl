"""Calendar board: one tile per day, a mouse walks from the first day to today.

The mouse pauses on the busiest days. Layout is boustrophedon like a board game: row 0
runs left to right along the bottom, row 1 runs right to left above it, and so on.
"""

from __future__ import annotations

import math
from datetime import date

from svg_kit import ACCENT, FAINT, GAP, HEAT, INK, LINE, MUTED, WIDTH, kicker, panel, svg_doc, text

COLS = 28
PAD_X = 40
PITCH = (WIDTH - 2 * PAD_X) / COLS
TILE = PITCH - 4
HEADER_H = 138
FOOTER_H = 58
WALK_SECONDS = 18
BUSY_LEVEL = 4  # heat level at which the mouse stops for a moment
PAUSE_STEPS = 3  # a pause lasts as long as walking this many tiles
HOLD_FRACTION = 0.86  # share of the loop spent walking; the rest the mouse rests on today


def _cell_xy(index: int, board_top: float, rows: int) -> tuple[float, float]:
    row, col = divmod(index, COLS)
    visual_col = col if row % 2 == 0 else COLS - 1 - col
    x = PAD_X + visual_col * PITCH + PITCH / 2
    y = board_top + (rows - 1 - row) * PITCH + PITCH / 2
    return x, y


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


def _schedule(days: list[dict]) -> tuple[str, str]:
    """keyTimes / keyPoints for the walk: steady steps, a short stop on each busiest day,
    then a rest on today for the remainder of the loop."""
    last = len(days) - 1
    stops = [i for i, d in enumerate(days) if d["level"] >= BUSY_LEVEL and 0 < i < last]
    total_steps = last + PAUSE_STEPS * len(stops)
    points, times, elapsed = [0.0], [0.0], 0
    for i in range(1, last + 1):
        elapsed += 1
        points.append(i / last)
        times.append(elapsed / total_steps * HOLD_FRACTION)
        if i in stops:
            elapsed += PAUSE_STEPS
            points.append(i / last)
            times.append(elapsed / total_steps * HOLD_FRACTION)
    points.append(1.0)
    times.append(1.0)
    fmt = lambda values: ";".join(f"{v:.4f}" for v in values)  # noqa: E731
    return fmt(times), fmt(points)


def _walk(days: list[dict], rows: int, board_top: float) -> str:
    points = [_cell_xy(i, board_top, rows) for i in range(len(days))]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    length = PITCH * (len(points) - 1)
    key_times, key_points = _schedule(days)
    timing = (f'dur="{WALK_SECONDS}s" repeatCount="indefinite" calcMode="linear" '
              f'keyTimes="{key_times}"')
    offsets = ";".join(f"{length * (1 - float(k)):.1f}" for k in key_points.split(";"))
    end_x, end_y = points[-1]
    return (
        f'<path d="{path}" fill="none" stroke="{INK}" stroke-opacity=".28" stroke-width="2" '
        f'stroke-linejoin="round" stroke-dasharray="{length:.1f}" stroke-dashoffset="{length:.1f}">'
        f'<animate attributeName="stroke-dashoffset" values="{offsets}" {timing}/></path>'
        f'<circle class="pulse" cx="{end_x:.1f}" cy="{end_y:.1f}" r="{TILE / 2 + 3:.1f}" fill="none" '
        f'stroke="{ACCENT}" stroke-width="2"/>'
        f'<g><animateMotion path="{path}" rotate="auto" keyPoints="{key_points}" {timing}/>{MOUSE}</g>'
    )


def render_board(days: list[dict], start: date) -> str:
    days = [d for d in days if date.fromisoformat(d["date"]) >= start]
    rows = math.ceil(len(days) / COLS)
    board_top = HEADER_H
    height = HEADER_H + rows * PITCH + FOOTER_H
    total = sum(d["count"] for d in days)

    title = (f'<text x="{PAD_X}" y="82" class="serif rise" font-size="40" fill="{INK}" '
             f'style="animation-delay:.1s">Every day since {start:%B}, '
             f'<tspan class="italic" fill="{ACCENT}">one tile at a time</tspan></text>')
    sub = text(PAD_X, 108, f"{total:,} contributions across {len(days)} days. Darker tiles are busier "
               "days; the mouse stops on the busiest.", "sans rise", 13.5, MUTED, delay=0.2)
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
        + _walk(days, rows, board_top)
        + legend
    )
    label = (f"Calendar board of {len(days)} days of GitHub contributions since {start:%B %Y}; "
             "a mouse walks from the first day to today, stopping on the busiest days.")
    return svg_doc(round(height), label, body, ("serif", "serif-italic", "sans", "mono"))
