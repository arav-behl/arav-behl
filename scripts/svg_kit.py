"""Shared palette, fonts and helpers for the profile SVG cards."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"

WIDTH = 880
GAP = 12  # vertical gap baked into the bottom of each card
RADIUS = 18

PAPER = "#f3f1ec"
INK = "#16150f"
MUTED = "#6b6860"
FAINT = "#a8a49a"
LINE = "#e2ded5"
ACCENT = "#d9472b"
ACCENT_DEEP = "#9e2c16"
HEAT = ("#e4e0d6", "#f5cbbb", "#ec9979", "#df6340", "#b3341b")

FONTS = {
    "serif": ("Instrument Serif", "normal", "InstrumentSerif-Regular.woff2"),
    "serif-italic": ("Instrument Serif", "italic", "InstrumentSerif-Italic.woff2"),
    "sans": ("Geist", "normal", "Geist.woff2"),
    "mono": ("Geist Mono", "normal", "GeistMono.woff2"),
}

ANIMATIONS = """
@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.4)}70%{transform:scale(1.08)}100%{opacity:1;transform:scale(1)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.35}}
.rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.fade{animation:fade 1.2s ease both}
.grow{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.7,.2,1) both}
.pop{transform-box:fill-box;transform-origin:center;animation:pop .5s cubic-bezier(.2,.7,.2,1) both}
.pulse{animation:pulse 2.4s ease-in-out infinite}
.serif{font-family:'Instrument Serif',Georgia,serif}
.italic{font-style:italic}
.sans{font-family:'Geist',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'Geist Mono',ui-monospace,Menlo,monospace;letter-spacing:.08em}
"""


@lru_cache(maxsize=None)
def _font_face(key: str) -> str:
    family, style, filename = FONTS[key]
    data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode("ascii")
    return (
        f"@font-face{{font-family:'{family}';font-style:{style};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def style_block(fonts: tuple[str, ...], extra: str = "") -> str:
    faces = "".join(_font_face(k) for k in fonts)
    return f"<style>{faces}{ANIMATIONS}{extra}</style>"


def svg_doc(height: int, label: str, body: str, fonts: tuple[str, ...], extra_css: str = "",
            width: float = WIDTH) -> str:
    safe = escape(label)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{safe}">'
        f"<title>{safe}</title>{style_block(fonts, extra_css)}{body}</svg>"
    )


def panel(width: float, height: float, x: float = 0, fill: str = PAPER) -> str:
    return f'<rect x="{x}" y="0" width="{width}" height="{height}" rx="{RADIUS}" fill="{fill}"/>'


def text(x: float, y: float, content: str, cls: str, size: float, fill: str = INK,
         anchor: str = "start", delay: float | None = None, extra: str = "") -> str:
    style = f' style="animation-delay:{delay:.2f}s"' if delay is not None else ""
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}"{style}{extra}>{content}</text>'
    )


def kicker(x: float, y: float, label: str, delay: float = 0.0) -> str:
    """Small mono caps label with an accent square, like a section eyebrow."""
    return (
        f'<g class="rise" style="animation-delay:{delay:.2f}s">'
        f'<rect x="{x}" y="{y - 9}" width="8" height="8" rx="1.5" fill="{ACCENT}"/>'
        f'{text(x + 18, y, escape(label.upper()), "mono", 12, MUTED)}</g>'
    )


def write(path: Path, svg: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(svg)
