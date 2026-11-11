import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from scripts import artwork
from scripts import generate_activity as generator
from scripts.artwork import UNCLASSIFIED, Canvas
from scripts.generate_activity import public_repositories, render_svg, summarize

OWNER = "Djstar7"


def repository(identifier, **changes):
    result = {"id": identifier, "name": f"repo-{identifier}", "private": False,
              "fork": False, "owner": {"login": OWNER}, "language": "PHP"}
    result.update(changes)
    return result


class SnapshotTests(unittest.TestCase):
    def test_refresh_writes_matching_desktop_and_mobile_snapshots(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "assets/generated"
            (root / "profile.json").write_text(json.dumps({"username": OWNER}))
            with patch.object(generator, "ROOT", root), patch.object(generator, "OUTPUT", output), \
                    patch.object(generator, "public_repositories",
                                 return_value=[{"name": "sample", "language": "PHP"}]):
                generator.main()
            snapshot = json.loads((output / "activity.json").read_text())
            self.assertEqual(snapshot["repositories"], 1)
            for theme in ("light", "dark"):
                for mobile in (False, True):
                    source = (output / f'activity-{"mobile-" if mobile else ""}{theme}.svg').read_text()
                    self.assertEqual(ET.fromstring(source).get("width"), "480" if mobile else "1200")
                    self.assertIn(snapshot["updated"], source)
                    self.assertIn("PHP", source)

    def test_only_public_owned_original_repositories_are_counted(self):
        data = [repository(1), repository(2, private=True), repository(3, fork=True),
                repository(4, owner={"login": "someone-else"})]
        self.assertEqual(public_repositories(OWNER, lambda _: data),
                         [{"name": "repo-1", "language": "PHP"}])

    def test_pagination_and_duplicate_repository_ids(self):
        pages = [[repository(i) for i in range(100)], [repository(99), repository(100)]]
        calls = []

        def fetch(path):
            calls.append(path)
            return pages[len(calls) - 1]
        self.assertEqual(len(public_repositories(OWNER, fetch)), 101)
        self.assertIn("page=2", calls[1])

    def test_unclassified_is_not_a_language(self):
        result = summarize([{"language": "PHP"}, {"language": "PHP"}, {"language": None}], "2026-11-11")
        self.assertEqual(result["repositories"], 3)
        self.assertEqual(result["primary_languages"], 1)
        self.assertEqual(result["language_counts"], {"PHP": 2, UNCLASSIFIED: 1})

    def test_empty_account_and_xml_escaping(self):
        for repos in ([], [{"language": "A&B"}]):
            result = summarize(repos, "2026-11-11")
            for dark in (True, False):
                for mobile in (True, False):
                    ET.fromstring(render_svg(result, dark, mobile))

    def test_api_error_is_not_treated_as_zero_repositories(self):
        def unavailable(_):
            raise RuntimeError("Service unavailable")
        with self.assertRaises(RuntimeError):
            public_repositories(OWNER, unavailable)


class ArtworkTests(unittest.TestCase):
    def test_overflowing_text_fails_the_build(self):
        with self.assertRaises(ValueError):
            Canvas(480, 100, "dark", "t", "d").text(28, 50, "x" * 80, 22)

    def test_every_composition_builds_valid_svg(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(artwork, "ROOT", Path(temporary)):
                artwork.main()
            files = list(Path(temporary).rglob("*.svg"))
            self.assertEqual(len(files), 16)
            for path in files:
                root = ET.fromstring(path.read_text())
                self.assertIsNotNone(root.get("viewBox"))
