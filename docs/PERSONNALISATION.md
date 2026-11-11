# Maintenance du profil

## Organisation

| Élément | Rôle |
| --- | --- |
| `README.md` | Présentation publique, textes et liens. |
| `profile.json` | Identité, liens vérifiés et date de vérification. Seul `username` est lu par le générateur. |
| `scripts/artwork.py` | Système visuel : couleurs, typographie, étoile DJSTAR7 et compositions. |
| `scripts/build_artwork.py` | Régénère la couverture, les produits, la stack et la méthode. |
| `scripts/generate_activity.py` | Génère le snapshot des dépôts publics depuis l'API GitHub. |
| `scripts/validate_profile.py` | Contrôles hors ligne : sections, images, liens locaux, SVG et actions épinglées. |

## Modifier le contenu

Les textes des visuels se trouvent dans `scripts/artwork.py` : `PRODUCTS`, `STACK`, `LEARNING`, `CYCLE` et `PRINCIPLES` (garder des listes courtes). Après une modification :

```sh
python3 scripts/build_artwork.py
```

Chaque texte est contrôlé à partir d'une largeur estimée. Un libellé trop long fait échouer la génération au lieu de déborder du visuel. Il faut alors le raccourcir ou réduire sa taille.

Chaque composition existe en quatre variantes : clair et sombre, bureau (1200 px) et mobile (480 px). Le README choisit la bonne variante avec `<picture>`.

## Identité visuelle

- Couleur principale, le bleu nuit : fond `#0A1128` en thème sombre, texte `#0A1F44` en thème clair.
- Accent : étoile dorée `#E9B949` sur fond nuit en thème sombre, bleu `#1E3A8A` en thème clair.
- Les libellés de métadonnées utilisent une police monospace en majuscules. Le texte courant utilise une police sans-serif système.
- La marque est un heptagramme {7/3} : une étoile à sept branches, pour DJSTAR7.
- Aucune animation, aucun badge, aucun service d'images externe.

## Snapshot GitHub

Le workflow `Refresh GitHub snapshot` s'exécute chaque lundi, sur demande, et à chaque modification des scripts sur `main`. Il compte uniquement les dépôts publics détenus par le compte, sans les forks, et ne publie que `assets/generated/`. En cas d'échec, le snapshot précédent est conservé.

Pour l'exécuter en local :

```sh
GH_TOKEN="$(gh auth token)" python3 scripts/generate_activity.py
```

Le workflow ne s'exécute que dans le dépôt `Djstar7/Djstar7`. C'est le dépôt spécial que GitHub affiche sur la page de profil.

## Validation

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_profile.py
```

## Règles éditoriales

- Ne lier que des dépôts publics vérifiés. Aujourd'hui, seul `kpay-php-sdk` est lié.
- Les indicateurs d'usage (400+, 150+, 1 750+) sont déclarés. Il faut les mettre à jour quand ils évoluent.
- Une technologie en cours d'apprentissage reste sur la ligne « En apprentissage » jusqu'à ce qu'elle soit pratiquée en production.
