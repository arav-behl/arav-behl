"""Hero, activity, section-title and repo cards for the profile README."""

from __future__ import annotations

import textwrap
from collections import OrderedDict
from datetime import date
from xml.sax.saxutils import escape

from svg_kit import (ACCENT, FAINT, GAP, HEAT, INK, LINE, MUTED, PAPER, RADIUS, WIDTH, kicker,
                     panel, svg_doc, text)

PAD = 40
ALL_FONTS = ("serif", "serif-italic", "sans", "mono")

HERO_STATS = (("2", "startups co-founded"), ("1", "building right now"), ("Point72", "quant work, global macro"))

REPOS = (
    ("PaperShield", "ai_safety", "Python",
     "Prompt-injection eval: attack success 0% to 19.4%, and what a defense really costs."),
    ("Quant Research", "Quant_Research_Strategies", "Python",
     "16 portfolio strategies (Ridge, LSTM, PPO, LLM) tested on the Nifty 50."),
    ("Crypto Order Book", "rust_new", "Rust",
     "Limit order book in Rust, matching against live Binance market data."),
    ("C++ Market Data", "cpp_project", "C++",
     "Low-latency market data handler written in modern C++20."),
    ("Transcript Clustering", "clustering_project", "Python",
     "Hierarchical NLP clustering of customer discovery meetings."),
    ("Pulsefield", "pulsefield", "JavaScript",
     "Local-first Apple Health analytics; every number traces to its source."),
)
REPO_W = (WIDTH - 2 * GAP) / 3
REPO_H = 190
BOLD = ' font-weight="600"'


# ---------- hero ----------

def render_hero() -> str:
    height = 340
    name = (f'<text x="{PAD}" y="168" class="serif rise" font-size="112" fill="{INK}" '
            f'style="animation-delay:.1s">Arav <tspan class="italic" fill="{ACCENT}">Behl</tspan></text>')
    lines = ("Co-founded two startups, now building at a third.",
             "Previously quant work at Point72 Global Macro.",
             "I build AI agents and measure whether they work.")
    tagline = "".join(text(PAD, 220 + i * 25, escape(line), "sans rise", 17, INK, delay=0.25 + i * 0.05)
                      for i, line in enumerate(lines))
    link = (f'<a href="https://aravbehl.com" target="_blank">'
            f'{text(PAD, 300, "aravbehl.com  ↗", "mono rise", 13, INK, delay=0.45)}</a>')

    col_x, row_h = 620, 92
    stats = []
    for i, (value, label) in enumerate(HERO_STATS):
        y = 40 + i * row_h
        delay = 0.35 + i * 0.12
        if i:
            stats.append(f'<line class="fade" style="animation-delay:{delay:.2f}s" x1="{col_x}" '
                         f'y1="{y}" x2="{WIDTH - PAD}" y2="{y}" stroke="{LINE}"/>')
        stats.append(text(col_x, y + 54, value, "serif italic rise", 52, INK, delay=delay))
        stats.append(text(col_x, y + 76, escape(label), "sans rise", 13.5, MUTED, delay=delay + 0.05))
    body = (panel(WIDTH, height - GAP) + kicker(PAD, 46, "Building at a stealth AI startup · Singapore")
            + name + tagline + link + "".join(stats))
    label = ("Arav Behl. Co-founded two startups, now building at a third. Previously quant work at "
             "Point72 Global Macro. Builds AI agents and measures whether they work.")
    return svg_doc(height, label, body, ALL_FONTS)


# ---------- activity ----------

def _streaks(days: list[dict]) -> tuple[int, int]:
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    tail = days[:-1] if days and days[-1]["count"] == 0 else days  # today may still be empty
    for d in reversed(tail):
        if not d["count"]:
            break
        current += 1
    return current, longest


def render_activity(days: list[dict], start: date) -> str:
    days = [d for d in days if date.fromisoformat(d["date"]) >= start]
    height = 330
    total = sum(d["count"] for d in days)
    active = sum(1 for d in days if d["count"])
    busiest = max(days, key=lambda d: d["count"])
    current, longest = _streaks(days)

    months: OrderedDict[str, int] = OrderedDict()
    for d in days:
        key = date.fromisoformat(d["date"]).strftime("%b")
        months[key] = months.get(key, 0) + d["count"]

    chart_left, chart_right, base, chart_h = PAD + 4, 540, 282, 120
    slot = (chart_right - chart_left) / len(months)
    peak = max(months.values()) or 1
    bars = []
    for i, (month, count) in enumerate(months.items()):
        h = max(3, count / peak * chart_h)
        x = chart_left + i * slot + slot * 0.18
        w = slot * 0.64
        is_peak = count == peak
        fill = ACCENT if is_peak else HEAT[2]
        delay = 0.35 + i * 0.07
        bars.append(f'<rect class="grow" style="animation-delay:{delay:.2f}s" x="{x:.1f}" '
                    f'y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{fill}"/>')
        bars.append(text(x + w / 2, base + 22, month.upper(), "mono", 10.5, MUTED, "middle"))
        if is_peak:
            bars.append(text(x + w / 2, base - h - 8, f"{count:,}", "mono pop", 11, ACCENT, "middle",
                             delay=delay + 0.6))

    col_x = 620
    stat_rows = (
        (f"{current}", " days", "current streak"),
        (f"{active}", f" / {len(days)}", "days with a contribution"),
        (f"{busiest['count']}", "", f"on the busiest day, {date.fromisoformat(busiest['date']):%d %b}"),
    )
    stats = []
    for i, (big, small, label) in enumerate(stat_rows):
        y = 46 + i * 92
        delay = 0.4 + i * 0.12
        if i:
            stats.append(f'<line class="fade" x1="{col_x}" y1="{y - 8}" x2="{WIDTH - PAD}" '
                         f'y2="{y - 8}" stroke="{LINE}"/>')
        stats.append(f'<text x="{col_x}" y="{y + 42}" class="serif rise" font-size="46" fill="{INK}" '
                     f'style="animation-delay:{delay:.2f}s">{big}<tspan class="italic" fill="{FAINT}" '
                     f'font-size="34">{escape(small)}</tspan></text>')
        stats.append(text(col_x, y + 64, escape(label), "sans rise", 13, MUTED, delay=delay + 0.05))

    headline = (f'<text x="{PAD}" y="118" class="serif rise" font-size="64" fill="{INK}" '
                f'style="animation-delay:.15s">{total:,} <tspan class="italic">contributions</tspan></text>')
    body = (panel(WIDTH, height - GAP) + kicker(PAD, 46, f"Since {start:%B} on GitHub")
            + headline + "".join(bars) + "".join(stats))
    label = (f"{total:,} contributions since {start:%B %Y}; current streak {current} days, longest "
             f"{longest}; {active} of {len(days)} days active.")
    return svg_doc(height, label, body, ALL_FONTS)


# ---------- section title (adapts to light/dark page) ----------

def render_title(lead: str, italic: str) -> str:
    css = (".t{fill:#16150f}.i{fill:%s}@media (prefers-color-scheme:dark){.t{fill:#f0eee8}}" % ACCENT)
    body = (f'<text x="4" y="58" class="serif rise t" font-size="44">{escape(lead)} '
            f'<tspan class="italic i">{escape(italic)}</tspan></text>')
    return svg_doc(84, f"{lead} {italic}", body, ("serif", "serif-italic"), css)


# ---------- repo cards ----------

def render_repo(index: int, name: str, language: str, blurb: str) -> str:
    column = index % 3
    x = column * GAP / 3  # keeps outer edges flush and inner gaps equal across a row of three
    w = REPO_W
    total_w = WIDTH / 3
    lines = textwrap.wrap(blurb, 34)
    delay = 0.1 + index * 0.08
    desc = "".join(text(x + 24, 80 + i * 21, escape(line), "sans", 14, MUTED) for i, line in enumerate(lines))
    body = (
        f'<g class="rise" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="0" width="{w:.2f}" height="{REPO_H - GAP}" rx="{RADIUS}" fill="{PAPER}"/>'
        f'<rect x="{x + 24}" y="34" width="8" height="8" rx="1.5" fill="{ACCENT}"/>'
        f'{text(x + 40, 43, escape(name), "sans", 17, INK, extra=BOLD)}'
        f"{desc}"
        f'{text(x + 24, REPO_H - GAP - 24, escape(language.upper()), "mono", 10.5, FAINT)}'
        f'{text(x + w - 24, REPO_H - GAP - 24, "VIEW  ↗", "mono", 10.5, INK, "end")}'
        f"</g>"
    )
    return svg_doc(REPO_H, f"{name}: {blurb}", body, ("sans", "mono"), width=round(total_w, 3))
