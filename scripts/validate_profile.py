#!/usr/bin/env python3
"""Offline checks for the README structure, graphic pieces, links, snapshot and action pins."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

try:
    from .generate_activity import END, START, UNCLASSIFIED
except ImportError:
    from generate_activity import END, START, UNCLASSIFIED

ROOT = Path(__file__).resolve().parents[1]
NS = "{http://www.w3.org/2000/svg}"
# Services checked as reachable on 2026-11-11. github-readme-stats (503) and
# github-readme-activity-graph (402) were unavailable and are deliberately excluded.
IMAGE_HOSTS = {"capsule-render.vercel.app", "readme-typing-svg.demolab.com", "skillicons.dev",
               "img.shields.io", "streak-stats.demolab.com"}


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "img":
            assert attrs.get("alt"), "Every README image needs meaningful alt text"
            if attrs["src"].startswith("assets/pieces/"):
                assert int(attrs.get("width", "0")) <= 96, "Product icons stay small"
            self.paths.append(attrs["src"])


def validate():
    readme = (ROOT / "README.md").read_text()
    sections = re.findall(r"^## (.+)$", readme, re.MULTILINE)
    assert sections == ["À propos", "Produits", "Stack technique", "Activité GitHub", "Contact"], \
        "The profile must keep its banner and five sections"
    assert readme.count(START) == 1 and readme.count(END) == 1, "Activity markers missing"
    images = Images()
    images.feed(readme)
    assert len([p for p in images.paths if not urlsplit(p).scheme]) == 5, "Expected the Djstar7 logo and four product icons"
    links = re.findall(r"\]\(([^)]+)\)", readme) + re.findall(r'href="([^"]+)"', readme)
    for path in images.paths + links:
        parsed = urlsplit(path)
        if parsed.scheme or not parsed.path:
            continue
        target = (ROOT / unquote(parsed.path)).resolve()
        assert target.is_relative_to(ROOT) and target.is_file(), f"Missing local resource: {path}"
    for path in images.paths:
        parsed = urlsplit(path)
        if parsed.scheme:
            assert parsed.scheme == "https" and parsed.hostname in IMAGE_HOSTS, f"Unverified image service: {path}"
    svgs = list((ROOT / "assets").rglob("*.svg"))
    assert len(svgs) == 4, "Only the four product icons are kept"
    assert (ROOT / "assets/brand/djstar7.png").stat().st_size < 400_000, "Keep the logo light"
    for path in svgs:
        source = path.read_text()
        assert "<!ENTITY" not in source and "<!DOCTYPE" not in source
        root = ET.fromstring(source)
        assert root.tag == NS + "svg" and root.get("viewBox"), str(path)
        assert root.find(NS + "title") is not None, f"Missing SVG title: {path}"
        for element in root.iter():
            assert element.tag.split("}")[-1] not in {"script", "foreignObject", "image"}, str(path)
            for name, value in element.attrib.items():
                assert not name.lower().startswith("on"), str(path)
                if name.endswith("href"):
                    assert value.startswith("#"), str(path)
        assert not re.search(r"@import|url\(\s*['\"]?https?://", source), str(path)
        assert "@keyframes" not in source and "<animate" not in source, f"No animation: {path}"
    snapshot = json.loads((ROOT / "assets/generated/activity.json").read_text())
    assert sum(snapshot["language_counts"].values()) == snapshot["repositories"]
    assert snapshot["primary_languages"] == len(
        [language for language in snapshot["language_counts"] if language != UNCLASSIFIED])
    for path in (ROOT / ".github/workflows").glob("*.yml"):
        workflow = path.read_text()
        for action in re.findall(r"uses:\s*(\S+)", workflow):
            assert re.fullmatch(r"[\w/-]+@[0-9a-f]{40}", action), f"Unpinned action: {action}"
        assert "pull_request_target" not in workflow
        assert "write-all" not in workflow
    print(f"Validated README structure, {len(svgs)} graphic pieces, local links, snapshot and action pins")


if __name__ == "__main__":
    validate()
