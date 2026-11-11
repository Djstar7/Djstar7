#!/usr/bin/env python3
"""Generate dated public-repository statistics using only Python's standard library."""
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

try:
    from .artwork import UNCLASSIFIED, activity
except ImportError:
    from artwork import UNCLASSIFIED, activity

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets/generated"


def api_get(path):
    headers = {"Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "github-profile-snapshot"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            with urlopen(Request(f"https://api.github.com/{path}", headers=headers),
                         timeout=30) as response:
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
    repositories = {}
    page = 1
    while True:
        batch = fetch(f"users/{username}/repos?type=owner&per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("Expected a repository list")
        for repo in batch:
            if (repo["private"] is False and not repo["fork"]
                    and repo["owner"]["login"].lower() == username.lower()):
                repositories[repo["id"]] = {
                    "name": repo["name"],
                    "language": repo["language"],
                }
        if len(batch) < 100:
            break
        page += 1
    return sorted(repositories.values(), key=lambda repo: repo["name"].lower())


def summarize(repositories, updated):
    counts = Counter(repo["language"] or UNCLASSIFIED for repo in repositories)
    return {
        "updated": updated,
        "scope": "Dépôts publics détenus par le compte, forks exclus, dépôts archivés inclus.",
        "repositories": len(repositories),
        "primary_languages": len({r["language"] for r in repositories if r["language"]}),
        "language_counts": dict(sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))),
    }


def render_svg(snapshot, dark, mobile=False):
    return activity(snapshot, dark, mobile)


def main():
    config = json.loads((ROOT / "profile.json").read_text())
    repos = public_repositories(config["username"])
    snapshot = summarize(repos, datetime.now(timezone.utc).date().isoformat())
    # Fetching and rendering finish before any existing snapshot is replaced.
    files = {
        f"activity-{'mobile-' if mobile else ''}{theme}.svg": render_svg(snapshot, theme == "dark", mobile)
        for theme in ("light", "dark") for mobile in (False, True)
    }
    files["activity.json"] = json.dumps(snapshot, indent=2) + "\n"
    lines = [
        "# Snapshot des dépôts publics", "",
        f'Mis à jour le **{snapshot["updated"]} UTC** depuis l\'API REST de GitHub.', "",
        f'- Dépôts publics originaux : **{snapshot["repositories"]}**.',
        f'- Langages principaux distincts : **{snapshot["primary_languages"]}**.', "",
        "| Langage principal | Dépôts |", "| --- | ---: |",
        *[f"| {language} | {count} |" for language, count in snapshot["language_counts"].items()],
        "", snapshot["scope"], "",
        "GitHub attribue un seul langage principal par dépôt ; les dépôts sans langage détecté "
        f"apparaissent comme « {UNCLASSIFIED} ». Ces chiffres ne mesurent ni un niveau de maîtrise, "
        "ni le volume de code, ni l'état d'avancement des projets.", "",
        f'[Source](https://api.github.com/users/{config["username"]}/repos?type=owner&per_page=100). '
        "Le générateur parcourt toutes les pages. Un échec conserve le snapshot précédent.", "",
    ]
    files["activity.md"] = "\n".join(lines)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        temporary = OUTPUT / f".{name}.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(OUTPUT / name)
    print(f'Updated public snapshot: {snapshot["repositories"]} repositories')


if __name__ == "__main__":
    main()
