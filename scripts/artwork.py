"""DJSTAR7 profile artwork: midnight blue system, gold star accent, seven-point mark.

Standard library only. Every composition exists in light/dark and desktop/mobile.
Text placement is checked against an estimated width so a long label fails the
build instead of silently overflowing an artboard.
"""
from html import escape
from math import cos, pi, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOKENS = {
    "dark": dict(bg="#0A1128", surface="#0F1A3A", raised="#18264D", border="#1F2F5C",
                 rule="#2E437A", fg="#F4F6FC", muted="#9AA6C8", accent="#E9B949"),
    "light": dict(bg="#F7F9FD", surface="#FFFFFF", raised="#E6ECF7", border="#D5DDEE",
                  rule="#B4C1DD", fg="#0A1F44", muted="#4A5878", accent="#1E3A8A"),
}
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"
SAFE = 20  # minimum distance between any text and the artboard edge


def estimate(text, size, weight=400, mono=False, spacing=0):
    factor = 0.61 if mono else (0.6 if weight >= 600 else 0.55)
    return len(str(text)) * (size * factor + spacing)


class Canvas:
    def __init__(self, width, height, theme, title, description):
        self.width, self.height, self.theme = width, height, theme
        self.c = TOKENS[theme]
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        ]
        self.rect(0.5, 0.5, width - 1, height - 1, "bg", "border", 12)

    def color(self, value):
        return self.c.get(value, value)

    def rect(self, x, y, w, h, fill="surface", stroke="border", radius=10, width=1, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
                          f'fill="{self.color(fill)}" stroke="{self.color(stroke)}" stroke-width="{width}"{extra}/>')

    def text(self, x, y, value, size=22, color="fg", weight=400, mono=False,
             anchor="start", spacing=0):
        width = estimate(value, size, weight, mono, spacing)
        left = {"start": x, "middle": x - width / 2, "end": x - width}[anchor]
        if left < SAFE or left + width > self.width - SAFE:
            raise ValueError(f"Text overflows {self.width}px artboard: {value!r}")
        family = MONO if mono else SANS
        extra = f' letter-spacing="{spacing}"' if spacing else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{self.color(color)}" text-anchor="{anchor}"{extra}>{escape(str(value))}</text>')

    def label(self, x, y, value, size=15, color="muted", anchor="start"):
        """Uppercase monospace metadata, the system's only typographic ornament."""
        self.text(x, y, value.upper(), size, color, 500, True, anchor, 1.5)

    def path(self, d, color="rule", width=1.5, fill="none", dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<path d="{d}" fill="{self.color(fill)}" stroke="{self.color(color)}" '
                          f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    def dot(self, x, y, r=3, color="accent"):
        self.parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{self.color(color)}"/>')

    def ring(self, x, y, r, color="border", width=1, dash=None):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{self.color(color)}" '
                          f'stroke-width="{width}"{extra}/>')

    def group(self, x, y, scale=1):
        self.parts.append(f'<g transform="translate({x} {y}) scale({scale})">')

    def end(self):
        self.parts.append("</g>")

    def finish(self):
        return "\n".join(self.parts + ["</svg>"]) + "\n"

    def save(self, filename):
        path = ROOT / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.finish(), encoding="utf-8")
        return path


def wrap(items, size, width, separator=" · "):
    """Greedy line breaking of an item list using the same width estimate."""
    lines, current = [], ""
    for item in items:
        candidate = f"{current}{separator}{item}" if current else item
        if current and estimate(candidate, size) > width:
            lines.append(current)
            current = item
        else:
            current = candidate
    return lines + ([current] if current else [])


def suffix(theme, mobile):
    return f"{'mobile-' if mobile else ''}{theme}"


# --------------------------------------------------------------------------- mark

def star(d, cx, cy, r, stroke=2, vertices=True, orbit=True):
    """{7/3} heptagram: seven vertices joined every third point."""
    points = [(cx + r * cos(-pi / 2 + i * 2 * pi / 7), cy + r * sin(-pi / 2 + i * 2 * pi / 7))
              for i in range(7)]
    order = [points[(i * 3) % 7] for i in range(8)]
    d.path("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in order), "accent", stroke)
    if orbit:
        d.ring(cx, cy, round(r * 1.32), "border", 1)
    if vertices:
        for x, y in points:
            d.dot(x, y, max(2, stroke + 0.5), "fg")


# -------------------------------------------------------------------------- cover

def cover(theme, mobile):
    d = Canvas(480 if mobile else 1200, 380 if mobile else 420, theme,
               "Staël Djune — DJSTAR7",
               "Full-Stack Engineer, Web, Mobile and Backend, based in Cameroon. "
               "A seven-point star forms the DJSTAR7 mark. Vision, Discipline, Impact.")
    if mobile:
        d.label(28, 46, "DJSTAR7 / Full-Stack")
        star(d, 412, 66, 34, 1.5)
        d.text(28, 156, "Staël Djune", 50, weight=700)
        for i, line in enumerate(["Applications Web et Mobile,", "orientées Backend, pensées",
                                  "pour la production."]):
            d.text(28, 204 + i * 32, line, 22, "muted")
        d.path("M28 318H452", "border", 1)
        d.label(28, 350, "Vision • Discipline • Impact", 14, "accent")
    else:
        d.label(64, 76, "DJSTAR7  /  Full-Stack Engineer  /  Cameroun")
        d.text(60, 196, "Staël Djune", 96, weight=700)
        d.text(64, 252, "Je conçois des applications Web et Mobile", 26, "muted")
        d.text(64, 288, "utiles, sécurisées et prêtes pour la production.", 26, "muted")
        d.path("M64 344H760", "border", 1)
        d.label(64, 378, "Vision • Discipline • Impact", 15, "accent")
        d.label(760, 378, "Web · Mobile · Backend", 15, anchor="end")
        for gx in range(860, 1161, 30):
            for gy in range(50, 371, 30):
                d.dot(gx, gy, 1, "border")
        star(d, 1010, 210, 118, 2.5)
    d.save(f"assets/branding/cover-{suffix(theme, mobile)}.svg")


# ----------------------------------------------------------------------- products

PRODUCTS = [
    dict(key="kpay", index="01", domain="FinTech", name="KPay",
         lines=["Paiements, transferts et tontines", "intégrés au Mobile Money."],
         stack="Next.js · NestJS · Prisma · PostgreSQL · Redis",
         metric="400+", metric_label="utilisateurs actifs · 23+ pays"),
    dict(key="formcam", index="02", domain="EdTech / SaaS", name="FormCam",
         lines=["Formations en ligne, formateurs,", "partenaires et abonnements."],
         stack="Laravel 12 · Vue 3 · Inertia.js 2 · Tailwind",
         metric="150+", metric_label="utilisateurs · projet fondé"),
    dict(key="estuaire", index="03", domain="Mobile", name="Estuaire Emploi",
         lines=["Mise en relation et accès aux", "offres d'emploi, en temps réel."],
         stack="Flutter · Laravel · temps réel",
         metric="1 750+", metric_label="utilisateurs"),
    dict(key="dsie", index="04", domain="Ingénierie", name="DSIE",
         lines=["Environnement d'ingénierie bâti", "sur des standards communs."],
         stack="DSIE Engineering Standard (DES)",
         metric=None, metric_label="Noyau commun + standards par techno"),
]

GLYPHS = {
    "kpay": "M0 0H16V16H0ZM40 0H56V16H40ZM0 40H16V56H0ZM28 0V22M28 34V56M40 28H56M0 28H22M40 40H56V56H40",
    "formcam": "M28 4L54 16L28 28L2 16ZM2 29L28 41L54 29M2 42L28 54L54 42",
    "estuaire": "M2 28A10 10 0 1 0 22 28A10 10 0 1 0 2 28M34 28A10 10 0 1 0 54 28A10 10 0 1 0 34 28M22 28H34M12 8V18M44 38V48",
    "dsie": "M0 0H22V22H0ZM34 0H56V22H34ZM0 34H22V56H0ZM34 34H56V56H34ZM22 11H34M11 22V34M45 22V34M22 45H34",
}


def product_tile(d, p, x, y, w, h, mobile):
    pad = 24 if mobile else 32
    d.rect(x, y, w, h, "surface", "border", 10)
    d.label(x + pad, y + pad + 12, f'{p["index"]}  {p["domain"]}', 13 if mobile else 14)
    d.group(x + w - pad - (34 if mobile else 42), y + pad - 2, 0.6 if mobile else 0.75)
    d.path(GLYPHS[p["key"]], "accent", 2)
    d.end()
    name_y = y + pad + (62 if mobile else 78)
    d.text(x + pad, name_y, p["name"], 34 if mobile else 42, weight=700)
    size = 18 if mobile else 21
    for i, line in enumerate(p["lines"]):
        d.text(x + pad, name_y + (34 if mobile else 42) + i * (size + 9), line, size, "muted")
    d.text(x + pad, y + h - (66 if mobile else 82), p["stack"], 13 if mobile else 15, "fg", 400, True)
    d.path(f"M{x + pad} {y + h - (50 if mobile else 62)}H{x + w - pad}", "border", 1)
    base = y + h - pad + (2 if mobile else 0)
    if p["metric"]:
        msize = 22 if mobile else 26
        d.text(x + pad, base, p["metric"], msize, "accent", 700)
        d.text(x + pad + estimate(p["metric"], msize, 700) + 12, base, p["metric_label"],
               14 if mobile else 16, "muted")
    else:
        d.label(x + pad, base - 2, p["metric_label"], 12 if mobile else 13, "accent")


def products(theme, mobile):
    desc = ("KPay, FinTech: payments, transfers and savings groups with Mobile Money, 400+ active users. "
            "FormCam, EdTech SaaS: online training platform, 150+ users. "
            "Estuaire Emploi, mobile: job matching with real-time features, 1,750+ users. "
            "DSIE: engineering environment built on shared standards (DES). "
            "Original illustrations, not screenshots.")
    if mobile:
        tile_h, gap = 270, 16
        d = Canvas(480, 64 + 4 * tile_h + 3 * gap + 28, theme, "Produits et initiatives", desc)
        d.label(28, 42, "Produits & initiatives")
        for i, p in enumerate(PRODUCTS):
            product_tile(d, p, 28, 64 + i * (tile_h + gap), 424, tile_h, True)
    else:
        tile_w, tile_h, gap = 552, 330, 24
        d = Canvas(1200, 96 + 2 * tile_h + gap + 36, theme, "Produits et initiatives", desc)
        d.label(36, 56, "Produits & initiatives")
        d.label(1164, 56, "04 projets", anchor="end")
        for i, p in enumerate(PRODUCTS):
            col, row = i % 2, i // 2
            product_tile(d, p, 36 + col * (tile_w + gap), 84 + row * (tile_h + gap), tile_w, tile_h, False)
    d.save(f"assets/branding/products-{suffix(theme, mobile)}.svg")


# -------------------------------------------------------------------------- stack

STACK = [
    ("Backend", ["PHP 8.2+ / Laravel 12", "Node.js / NestJS", "TypeScript"]),
    ("Interfaces", ["REST", "WebSockets", "gRPC", "Webhooks", "Sanctum", "Spatie Permission"]),
    ("Frontend", ["Vue 3", "Nuxt", "React", "Next.js", "Inertia.js", "Tailwind CSS"]),
    ("Mobile", ["Flutter", "Dart", "GetX", "Provider"]),
    ("Données", ["PostgreSQL", "MySQL", "MongoDB", "Redis", "Prisma"]),
    ("DevOps", ["Linux", "Docker", "Compose", "Nginx", "GitLab CI/CD", "VPS"]),
    ("Paiements", ["Orange Money", "MTN MoMo", "Stripe", "CinetPay", "NotchPay", "FreemoPay"]),
]
LEARNING = ("En cours", ["Go", "IA : LLM", "Tool calling", "Agents", "RAG"])


def stack(theme, mobile):
    desc = "; ".join(f"{k}: {', '.join(v)}" for k, v in STACK)
    desc += f". In progress, learning: {', '.join(LEARNING[1])}. Domains, not proficiency levels."
    if mobile:
        size, width = 18, 424
        blocks = [(k, wrap(v, size, width)) for k, v in STACK + [LEARNING]]
        height = 72 + sum(30 + 26 * len(lines) + 18 for _, lines in blocks) + 10
        d = Canvas(480, height, theme, "Stack technique", desc)
        d.label(28, 44, "Stack technique")
        y = 72
        for i, (title, lines) in enumerate(blocks):
            learning = title == LEARNING[0]
            d.path(f"M28 {y}H452", "border", 1, dash="4 4" if learning else None)
            d.label(28, y + 26, title + ("  — apprentissage" if learning else ""), 13,
                    "accent" if learning else "muted")
            for j, line in enumerate(lines):
                d.text(28, y + 54 + j * 26, line, size, "muted" if learning else "fg")
            y += 30 + 26 * len(lines) + 18
    else:
        row = 54
        d = Canvas(1200, 96 + row * (len(STACK) + 1) + 40, theme, "Stack technique", desc)
        d.label(36, 56, "Stack technique")
        d.label(1164, 56, "Domaines, pas des niveaux", anchor="end")
        for i, (title, items) in enumerate(STACK + [LEARNING]):
            y = 84 + i * row
            learning = title == LEARNING[0]
            d.path(f"M36 {y}H1164", "border", 1, dash="4 4" if learning else None)
            d.label(36, y + 34, title, 14, "accent" if learning else "muted")
            d.text(260, y + 35, " · ".join(items), 22, "muted" if learning else "fg")
            if learning:
                d.label(1164, y + 34, "En apprentissage", 13, "accent", "end")
        d.path(f"M36 {84 + row * (len(STACK) + 1)}H1164", "border", 1)
    d.save(f"assets/branding/stack-{suffix(theme, mobile)}.svg")


# ------------------------------------------------------------------------- method

CYCLE = ["Comprendre", "Concevoir", "Développer", "Tester", "Déployer", "Faire évoluer"]
PRINCIPLES = [
    "Security by Design",
    "Séparation des responsabilités",
    "Validation stricte des entrées",
    "Transactions maîtrisées",
    "Tests automatisés",
]


def cycle(d, cx, cy, r, size):
    d.ring(cx, cy, r, "rule", 1.5)
    star(d, cx, cy, r * 0.3, 1.5, vertices=False, orbit=False)
    for i, name in enumerate(CYCLE):
        angle = -pi / 2 + i * pi / 3
        x, y = cx + r * cos(angle), cy + r * sin(angle)
        d.dot(x, y, 9, "bg")
        d.ring(f"{x:.1f}", f"{y:.1f}", 9, "accent", 1.5)
        d.dot(x, y, 3, "accent")
        gap = 22
        lx, ly = cx + (r + gap) * cos(angle), cy + (r + gap) * sin(angle)
        anchor = "middle" if abs(cos(angle)) < 0.1 else ("start" if cos(angle) > 0 else "end")
        if abs(cos(angle)) < 0.1:
            ly += -6 if sin(angle) < 0 else size + 4
        else:
            ly += size / 3
        d.text(round(lx, 1), round(ly, 1), name, size, "fg", 600, anchor=anchor)
    d.text(cx, cy + r * 0.3 + size + 14, "↻", size, "muted", anchor="middle")


def method(theme, mobile):
    desc = ("Product cycle: " + " → ".join(CYCLE) + ", then back to understanding. Principles: "
            + "; ".join(PRINCIPLES) + ".")
    if mobile:
        rows = 36
        d = Canvas(480, 380 + rows * len(PRINCIPLES) + 56, theme, "Méthode et principes", desc)
        d.label(28, 44, "Cycle produit")
        cycle(d, 240, 200, 80, 16)
        top = 370
        d.path(f"M28 {top}H452", "border", 1)
        d.label(28, top + 32, "Principes")
        for i, item in enumerate(PRINCIPLES):
            y = top + 70 + i * rows
            d.path(f"M28 {y - 6}H40", "accent", 2)
            d.text(54, y, item, 17)
    else:
        d = Canvas(1200, 460, theme, "Méthode et principes", desc)
        d.label(36, 56, "Cycle produit")
        cycle(d, 322, 250, 130, 20)
        d.path("M600 40V420", "border", 1)
        d.label(648, 56, "Principes")
        for i, item in enumerate(PRINCIPLES):
            y = 140 + i * 56
            d.path(f"M648 {y - 7}H664", "accent", 2)
            d.text(684, y, item, 24)
    d.save(f"assets/branding/method-{suffix(theme, mobile)}.svg")


# ----------------------------------------------------------------------- activity

UNCLASSIFIED = "Non classé"


def activity(snapshot, dark, mobile=False):
    """Render one dated repository snapshot; no network access happens here."""
    theme = "dark" if dark else "light"
    rows = sorted(snapshot["language_counts"].items(),
                  key=lambda row: (row[0] == UNCLASSIFIED, -row[1], row[0]))
    maximum = max(snapshot["language_counts"].values(), default=1)
    desc = (f'Snapshot of {snapshot["updated"]} UTC: {snapshot["repositories"]} original public '
            f'repositories, forks excluded, {snapshot["primary_languages"]} primary languages. '
            "One primary language per repository; not a measure of proficiency or code volume.")
    if mobile:
        height = 250 + len(rows) * 30
        d = Canvas(480, height, theme, "Activité GitHub publique", desc)
        d.label(28, 44, "GitHub public / snapshot")
        d.text(28, 106, snapshot["repositories"], 46, weight=700)
        d.text(250, 106, snapshot["primary_languages"], 46, weight=700)
        d.text(28, 136, "dépôts originaux", 17, "muted")
        d.text(250, 136, "langages principaux", 17, "muted")
        d.path("M28 160H452", "border", 1)
        for i, (name, count) in enumerate(rows):
            y = 196 + i * 30
            d.text(28, y, name, 17)
            d.rect(196, y - 10, 210, 6, "raised", "raised", 3)
            d.rect(196, y - 10, max(6, 210 * count / maximum), 6, "accent", "accent", 3)
            d.text(452, y, count, 17, "muted", anchor="end", mono=True)
        d.label(28, height - 22, f'{snapshot["updated"]} UTC · forks exclus', 12)
    else:
        height = max(340, 128 + len(rows) * 34)
        d = Canvas(1200, height, theme, "Activité GitHub publique", desc)
        d.label(36, 56, "GitHub public / snapshot")
        d.text(36, 156, snapshot["repositories"], 72, weight=700)
        d.text(36, 192, "dépôts publics originaux", 20, "muted")
        d.text(300, 156, snapshot["primary_languages"], 72, weight=700)
        d.text(300, 192, "langages principaux", 20, "muted")
        d.label(36, height - 30, f'{snapshot["updated"]} UTC · forks exclus', 13)
        d.path(f"M560 36V{height - 36}", "border", 1)
        d.label(600, 56, "Dépôts par langage principal")
        for i, (name, count) in enumerate(rows):
            y = 104 + i * 34
            d.text(600, y, name, 20)
            d.rect(800, y - 11, 300, 7, "raised", "raised", 3.5)
            d.rect(800, y - 11, max(7, 300 * count / maximum), 7, "accent", "accent", 3.5)
            d.text(1164, y, count, 20, "muted", anchor="end", mono=True)
    return d.finish()


def main():
    built = []
    for theme in TOKENS:
        for mobile in (False, True):
            for compose in (cover, products, stack, method):
                compose(theme, mobile)
                built.append(compose.__name__)
    print(f"Built {len(built)} SVGs: cover, products, stack and method in light/dark, desktop/mobile")
