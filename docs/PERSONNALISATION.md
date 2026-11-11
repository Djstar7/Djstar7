# Maintenance du profil

## Principe

Le README est construit avec des éléments natifs de GitHub : titres, tableaux, texte et liens. Il ne contient aucun grand panneau en image. Il utilise le logo officiel Djstar7 et quatre petites icônes produits dessinées par script.

| Élément | Rôle |
| --- | --- |
| `README.md` | Contenu du profil, modifiable directement. |
| `assets/brand/djstar7.png` | Logo officiel Djstar7 (480 px, coins transparents). |
| `assets/pieces/` | Icônes produits (`kpay`, `formcam`, `estuaire`, `dsie`). |
| `scripts/artwork.py` | Couleurs et dessin des pièces. |
| `scripts/build_artwork.py` | Régénère les pièces. |
| `scripts/generate_activity.py` | Réécrit le bloc « Activité GitHub » du README. |
| `scripts/validate_profile.py` | Contrôles hors ligne : sections, pièces, liens, snapshot et actions épinglées. |
| `profile.json` | Identité et liens vérifiés. Seul `username` est lu par le générateur. |

## Couleurs

- Fond des pièces : noir `#000000`.
- Surfaces : bleu nuit `#0A1128`.
- Tracés : bleu `#3D6BFF`, détails en bleu clair `#A9BCFF`.

Les pièces ont leur propre fond noir et restent donc identiques en thème clair et en thème sombre de GitHub.

## Modifier le contenu

Les textes, produits, technologies et principes se modifient directement dans `README.md`. Il ne faut pas toucher au bloc compris entre `<!-- activity:start -->` et `<!-- activity:end -->` : il est réécrit automatiquement.

Après une modification des couleurs ou des icônes :

```sh
python3 scripts/build_artwork.py
```

## Snapshot GitHub

Le workflow `Refresh GitHub snapshot` s'exécute chaque lundi, sur demande, et à chaque modification des scripts sur `main`. Il compte les dépôts publics détenus par le compte, sans les forks. Il réécrit uniquement le bloc d'activité du README et `assets/generated/`. En cas d'échec, le contenu précédent est conservé.

Pour l'exécuter en local :

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/generate_activity.py
```

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_profile.py
```

## Règles éditoriales

- Ne lier que des dépôts publics vérifiés. Aujourd'hui, seul `kpay-php-sdk` est lié.
- Images externes autorisées (vérifiées le 2026-11-11) : capsule-render, readme-typing-svg, skillicons, shields.io, streak-stats. `github-readme-stats` et `activity-graph` étaient hors service et sont exclus.
- Les indicateurs d'usage (400+, 150+, 1 750+) sont déclarés. Il faut les mettre à jour quand ils évoluent.
- Une technologie en cours d'apprentissage reste sur la ligne *En cours*.
