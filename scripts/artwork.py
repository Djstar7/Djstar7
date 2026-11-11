"""DJSTAR7 product icons: black background, blue drawing.

The README is built from native GitHub elements. Only small pieces are drawn
here: one icon per product. The DJSTAR7 logo itself lives in assets/brand/. Standard library only.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = "assets/pieces"

COLORS = dict(
    bg="#000000",       # fond : noir
    night="#0A1128",    # bleu nuit : surfaces et anneaux
    line="#1B2A5E",     # bleu nuit éclairci : contours discrets
    blue="#3D6BFF",     # bleu : tracés principaux
    light="#A9BCFF",    # bleu clair : points et détails
)


class Piece:
    def __init__(self, size, title):
        self.size = size
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}" role="img" aria-labelledby="title">',
            f'<title id="title">{escape(title)}</title>',
            f'<rect width="{size}" height="{size}" rx="{size * 0.22:.0f}" fill="{COLORS["bg"]}"/>',
        ]

    def path(self, d, color="blue", width=2):
        self.parts.append(f'<path d="{d}" fill="none" stroke="{COLORS[color]}" stroke-width="{width}" '
                          'stroke-linecap="round" stroke-linejoin="round"/>')

    def circle(self, x, y, r, fill="none", stroke=None, width=1):
        border = f' stroke="{COLORS[stroke]}" stroke-width="{width}"' if stroke else ""
        color = COLORS.get(fill, fill)
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"{border}/>')

    def save(self, name):
        path = ROOT / OUTPUT / f"{name}.svg"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]) + "\n", encoding="utf-8")
        return path


GLYPHS = {
    "kpay": ("KPay", "M0 0H16V16H0ZM40 0H56V16H40ZM0 40H16V56H0ZM28 0V22M28 34V56M40 28H56M0 28H22M40 40H56V56H40"),
    "formcam": ("FormCam", "M28 4L54 16L28 28L2 16ZM2 29L28 41L54 29M2 42L28 54L54 42"),
    "estuaire": ("Estuaire Emploi", "M2 28A10 10 0 1 0 22 28A10 10 0 1 0 2 28M34 28A10 10 0 1 0 54 28A10 10 0 1 0 34 28M22 28H34M12 8V18M44 38V48"),
    "dsie": ("DSIE", "M0 0H22V22H0ZM34 0H56V22H34ZM0 34H22V56H0ZM34 34H56V56H34ZM22 11H34M11 22V34M45 22V34M22 45H34"),
}


def glyph(key):
    title, d = GLYPHS[key]
    s = Piece(96, title)
    s.circle(48, 48, 38, "night", "line", 1)
    s.parts.append('<g transform="translate(26 26) scale(0.786)">')
    s.path(d, "blue", 2.6)
    s.parts.append("</g>")
    return s.save(key)


def main():
    built = [glyph(key) for key in GLYPHS]
    print(f"Built {len(built)} pieces in {OUTPUT}/")
