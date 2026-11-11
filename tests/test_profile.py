import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from scripts import artwork
from scripts import generate_activity as generator
from scripts.generate_activity import (END, START, UNCLASSIFIED, bar, inject,
                                       public_repositories, render_block, summarize)

OWNER = "Djstar7"


def repository(identifier, **changes):
    result = {"id": identifier, "name": f"repo-{identifier}", "private": False,
              "fork": False, "owner": {"login": OWNER}, "language": "PHP"}
    result.update(changes)
    return result


class SnapshotTests(unittest.TestCase):
    def test_refresh_rewrites_only_the_marked_readme_block(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "profile.json").write_text(json.dumps({"username": OWNER}))
            (root / "README.md").write_text(f"# Avant\n\n{START}\nancien\n{END}\n\n## Après\n")
            with patch.object(generator, "ROOT", root), \
                    patch.object(generator, "OUTPUT", root / "assets/generated"), \
                    patch.object(generator, "public_repositories",
                                 return_value=[{"name": "a", "language": "PHP"}]):
                generator.main()
            readme = (root / "README.md").read_text()
            self.assertTrue(readme.startswith("# Avant"))
            self.assertTrue(readme.endswith("## Après\n"))
            self.assertNotIn("ancien", readme)
            self.assertIn("| PHP | 1 |", readme)
            snapshot = json.loads((root / "assets/generated/activity.json").read_text())
            self.assertEqual(snapshot["repositories"], 1)

    def test_missing_markers_fail_instead_of_losing_content(self):
        with self.assertRaises(ValueError):
            inject("# README sans marqueurs\n", f"{START}\n{END}")

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

    def test_unclassified_is_listed_last_and_is_not_a_language(self):
        result = summarize([{"language": None}, {"language": None}, {"language": "PHP"}], "2026-11-11")
        self.assertEqual(result["primary_languages"], 1)
        self.assertEqual(list(result["language_counts"]), ["PHP", UNCLASSIFIED])

    def test_bars_and_table_escaping(self):
        self.assertEqual(bar(4, 4), "█" * 20)
        self.assertEqual(bar(1, 100), "█" + "░" * 19)
        block = render_block(summarize([{"language": "A|B"}], "2026-11-11"), OWNER)
        self.assertIn("A\\|B", block)
        self.assertEqual(render_block(summarize([], "2026-11-11"), OWNER).count(START), 1)

    def test_api_error_is_not_treated_as_zero_repositories(self):
        def unavailable(_):
            raise RuntimeError("Service unavailable")
        with self.assertRaises(RuntimeError):
            public_repositories(OWNER, unavailable)


class PieceTests(unittest.TestCase):
    def test_pieces_use_black_background_and_blue_drawing(self):
        with tempfile.TemporaryDirectory() as temporary:
            with patch.object(artwork, "ROOT", Path(temporary)):
                artwork.main()
            files = list(Path(temporary).rglob("*.svg"))
            self.assertEqual(len(files), 5)
            for path in files:
                source = path.read_text()
                ET.fromstring(source)
                self.assertIn('fill="#000000"', source)
                self.assertIn(artwork.COLORS["blue"], source)
