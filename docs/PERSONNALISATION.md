# Maintenance du profil

## Organisation

| Élément | Rôle |
| --- | --- |
| `README.md` | Contenu du profil, modifiable directement. |
| `assets/brand/djstar7.png` | Logo officiel Djstar7 (480 px, coins transparents). |
| `assets/projects/` | Logos officiels des produits (`kpay`, `formcam`, `estuaire`, `dsie`), en tuiles de 256 px aux coins arrondis. |
| `scripts/generate_activity.py` | Réécrit le bloc « Activité GitHub » du README. |
| `scripts/validate_profile.py` | Contrôles hors ligne : sections, images, liens, snapshot et actions épinglées. |
| `profile.json` | Identité et liens vérifiés. Seul `username` est lu par le générateur. |

## Couleurs

- Fond : noir `#000000`.
- Surfaces : bleu nuit `#0A1128`, puis `#1E3A8A` dans les dégradés de bannière.
- Accents : bleu `#3D6BFF` et bleu clair `#A9BCFF`.

Les images externes (bannières, texte animé, carte de série) reçoivent ces couleurs par leurs paramètres d'URL dans `README.md`.

## Remplacer un logo

Chaque logo de produit est une tuile carrée de 256 px aux coins arrondis, affichée en 64 px. Le fond de la tuile reprend celui du logo d'origine : noir pour KPay et FormCam, blanc pour Estuaire Emploi et DSIE. Pour remplacer un logo, il suffit de garder le même nom de fichier dans `assets/projects/`.

## Modifier le contenu

Tout le contenu se modifie directement dans `README.md`. Il ne faut pas toucher au bloc compris entre `<!-- activity:start -->` et `<!-- activity:end -->` : il est réécrit automatiquement.

## Snapshot GitHub

Le workflow `Refresh GitHub snapshot` s'exécute chaque jour à 04:17 UTC, sur demande, et à chaque modification des scripts sur `main`. Il compte les dépôts publics détenus par le compte, sans les forks. Il réécrit uniquement le bloc d'activité du README et `assets/generated/`.

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
