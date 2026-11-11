#!/usr/bin/env python3
"""Write a dated public-repository snapshot as native Markdown inside the README."""
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/generated"
UNCLASSIFIED = "Non classé"
START, END = "<!-- activity:start -->", "<!-- activity:end -->"
BAR = 20


def api_get(path):
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "github-profile-snapshot"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            with urlopen(Request(f"https://api.github.com/{path}", headers=headers), timeout=30) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError(f"GitHub API returned HTTP {error.code}") from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError("GitHub API unavailable; previous snapshot kept") from None
        time.sleep(2 ** attempt)


def public_repositories(username, fetch=api_get):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", username):
        raise ValueError("Invalid GitHub username")
    repositories, page = {}, 1
    while True:
        batch = fetch(f"users/{username}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Expected a repository list")
        for repo in batch:
            if (repo["private"] is False and not repo["fork"]
                    and repo["owner"]["login"].lower() == username.lower()):
                repositories[repo["id"]] = {"name": repo["name"], "language": repo["language"]}
        if len(batch) < 100:
            break
        page += 1
    return sorted(repositories.values(), key=lambda repo: repo["name"].lower())


def summarize(repositories, updated):
    counts = Counter(repo["language"] or UNCLASSIFIED for repo in repositories)
    ordered = sorted(counts.items(), key=lambda pair: (pair[0] == UNCLASSIFIED, -pair[1], pair[0]))
    return {
        "updated": updated,
        "scope": "Dépôts publics détenus par le compte, forks exclus, dépôts archivés inclus.",
        "repositories": len(repositories),
        "primary_languages": len({r["language"] for r in repositories if r["language"]}),
        "language_counts": dict(ordered),
    }


def bar(count, maximum):
    filled = round(BAR * count / maximum) if maximum else 0
    return "█" * max(filled, 1 if count else 0) + "░" * (BAR - max(filled, 1 if count else 0))


def cell(text):
    return str(text).replace("|", "\\|").replace("<", "&lt;")


def render_block(snapshot, username):
    maximum = max(snapshot["language_counts"].values(), default=0)
    lines = [
        START,
        f'**{snapshot["repositories"]}** dépôts publics originaux · '
        f'**{snapshot["primary_languages"]}** langages principaux',
        "",
        "| Langage principal | Dépôts | Répartition |",
        "| :-- | --: | :-- |",
        *[f"| {cell(name)} | {count} | `{bar(count, maximum)}` |"
          for name, count in snapshot["language_counts"].items()],
        "",
        f'<sub>Snapshot du {snapshot["updated"]} UTC · forks exclus · un langage principal par dépôt, '
        "pas un niveau de maîtrise · "
        f'[définitions](assets/generated/activity.md) · '
        f'[tous les dépôts](https://github.com/{username}?tab=repositories)</sub>',
        END,
    ]
    return "\n".join(lines)


def inject(readme, block):
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(readme):
        raise ValueError("README has no activity markers")
    return pattern.sub(lambda _: block, readme, count=1)


def render_notes(snapshot, username):
    return "\n".join([
        "# Snapshot des dépôts publics", "",
        f'Mis à jour le **{snapshot["updated"]} UTC** depuis l\'API REST de GitHub.', "",
        snapshot["scope"], "",
        "GitHub attribue un seul langage principal par dépôt ; les dépôts sans langage détecté "
        f"apparaissent comme « {UNCLASSIFIED} ». Ces chiffres ne mesurent ni un niveau de maîtrise, "
        "ni le volume de code, ni l'état d'avancement des projets.", "",
        f"[Source](https://api.github.com/users/{username}/repos?type=owner&per_page=100). "
        "Le générateur parcourt toutes les pages. Un échec conserve le snapshot précédent.", "",
    ])


def write_atomic(path, content):
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main():
    username = json.loads((ROOT / "profile.json").read_text())["username"]
    repos = public_repositories(username)
    snapshot = summarize(repos, datetime.now(timezone.utc).date().isoformat())
    readme_path = ROOT / "README.md"
    # Everything is rendered before any file is replaced.
    readme = inject(readme_path.read_text(encoding="utf-8"), render_block(snapshot, username))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_atomic(OUTPUT / "activity.json", json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n")
    write_atomic(OUTPUT / "activity.md", render_notes(snapshot, username))
    write_atomic(readme_path, readme)
    print(f'Updated public snapshot: {snapshot["repositories"]} repositories')


if __name__ == "__main__":
    main()
