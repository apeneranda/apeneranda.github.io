# Mettre à jour le site

Le site se republie **tout seul** à chaque modification enregistrée sur la branche `main`
(onglet *Actions* du dépôt : compter 1 à 2 minutes). Aucune commande n'est nécessaire :
tout peut se faire depuis l'interface web de GitHub.

## Remplacer le CV

1. Produire le nouveau `cv.pdf` (dans le coffre Dacom) :
   ```bash
   python3 x/Scripts/cv/cv.py --sans-notes --sortie "Claude outputs/Site web/cv"
   ```
2. Sur GitHub, ouvrir le dossier `static/files/`, cliquer sur **Add file → Upload files**,
   déposer le nouveau `cv.pdf` (même nom) et valider (**Commit changes**).

Le CV reste servi à l'adresse <https://apeneranda.github.io/files/cv.pdf>.

## Remplacer les publications

1. Produire le nouveau `publications.bib` (dans le coffre Dacom) :
   ```bash
   python3 x/Scripts/cv/bibtex.py --sortie "Claude outputs/Site web/publications"
   ```
2. Sur GitHub, à la **racine** du dépôt, **Add file → Upload files**, déposer
   `publications.bib` (même nom) et valider.

Il n'y a **pas d'import manuel** à relancer : à chaque publication, le script
`scripts/import_publications.py` relit `publications.bib` et régénère une page par référence.

Règles lues dans le `.bib` :

| champ `keywords` | rubrique du site |
|---|---|
| `acl` | Articles dans des revues à comité de lecture |
| `ouvrage`, `direction`, `numero` | Ouvrages, directions de collection et numéros thématiques |
| `chapitre` | Chapitres d'ouvrages |
| `communication` | Communications |
| `cahier` | Cahiers de recherche |
| `revue`, `diffusion` | Autres articles et diffusion |

- Le champ `hal` (et `url`) ajoute un bouton **HAL**.
- Les publications mises en avant sont listées par clé BibTeX dans `hugo.toml`
  (ligne `featured = [...]`).
- Une rubrique inconnue ou une clé en double fait échouer la publication : le site en
  ligne reste alors inchangé et l'onglet *Actions* affiche l'erreur.

## Modifier les textes

| Contenu | Fichier |
|---|---|
| Bio courte (accueil) | `content/_index.md` |
| Bio longue, fonctions, parcours, conférences | `content/bio.md` |
| Enseignement et encadrement | `content/enseignement.md` |
| Mentions légales | `content/mentions-legales.md` |
| Nom, fonction, intérêts, formation, contact, liens (icônes) | `data/profil.yaml` |
| Menu, description du site, publications mises en avant | `hugo.toml` |

Sur GitHub : ouvrir le fichier, cliquer sur le crayon (**Edit**), modifier, **Commit changes**.

### Ajouter un lien (idHAL…)

Dans `data/profil.yaml`, sous `liens`, ajouter par exemple :

```yaml
  - icone: orcid
    libelle: ORCID
    url: https://orcid.org/0000-0000-0000-0000
```

Icônes disponibles : `email`, `scholar`, `orcid`, `hal`, `cairn`, `linkedin`, `github`, `web` (toute autre
valeur affiche l'icône générique `web`).

## Changer la photo

Remplacer `assets/img/avatar.jpg` par un portrait **carré** (600 × 600 px minimum),
visage centré, sous le même nom.

## Prévisualiser en local (facultatif)

Avec [Hugo](https://gohugo.io/installation/) (version *extended* 0.162.0) et Python 3 :

```bash
python3 scripts/import_publications.py
hugo server
```

puis ouvrir <http://localhost:1313>.
