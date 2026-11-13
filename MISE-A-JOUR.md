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

Le CV français est servi à l'adresse <https://apeneranda.github.io/files/cv.pdf>
(lien « CV » de la version française).

**CV anglais** : même opération avec `static/files/cv-en.pdf` (lien « CV » de la version
anglaise, <https://apeneranda.github.io/files/cv-en.pdf>).

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
- **Version anglaise** : `publications-en.json` (racine du dépôt) donne, pour chaque clé
  BibTeX, la traduction du titre, affichée entre crochets après le titre original :
  `"peneranda2017aristote": "Aristotle, Moral Action and Management"`.
  Pour une nouvelle publication, ajouter une ligne de ce type (sinon le titre reste seul,
  sans traduction ; le journal de l'onglet *Actions* liste les clés sans traduction).
  Pour remplacer tout le titre (recensions, entretiens) :
  `"cle": {"title": "Review of …"}`. Une valeur vide `""` convient aux titres déjà en anglais.
- Les publications mises en avant sont listées par clé BibTeX dans `hugo.toml`
  (ligne `featured = [...]`).
- Une rubrique inconnue ou une clé en double fait échouer la publication : le site en
  ligne reste alors inchangé et l'onglet *Actions* affiche l'erreur.

## Recherche

La loupe en haut à droite (raccourci clavier : touche `/`) cherche dans toutes les pages et
publications de la langue affichée. Son index est recalculé automatiquement à chaque
publication : rien à faire.

## Modifier les textes

Le site existe en anglais (langue par défaut, à la racine : <https://apeneranda.github.io/>)
et en français (sous `/fr/` : <https://apeneranda.github.io/fr/>). Un petit drapeau, à
droite du menu, mène à la même page dans l'autre langue. Chaque page a deux fichiers :
`nom.en.md` pour l'anglais, `nom.fr.md` pour le français. Penser à modifier les deux.

| Contenu | Anglais | Français |
|---|---|---|
| Bio courte et vidéo (accueil) | `content/_index.en.md` | `content/_index.fr.md` |
| Bio longue, fonctions, parcours, conférences | `content/bio.en.md` | `content/bio.fr.md` |
| Enseignement et encadrement | `content/enseignement.en.md` | `content/enseignement.fr.md` |
| Mentions légales | `content/mentions-legales.en.md` | `content/mentions-legales.fr.md` |

| Autres réglages | Fichier |
|---|---|
| Accueil : nom, fonction, lignes « Research Fellow / Laboratoire », domaines, formation (blocs `fr` et `en`), coordonnées, liens | `data/profil.yaml` |
| Menus des deux langues, descriptions, publications mises en avant | `hugo.toml` |
| Petits libellés de l'interface (boutons, titres de rubriques) | `i18n/fr.yaml`, `i18n/en.yaml` |

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

## Changer la vidéo de l'accueil

La vidéo affichée sous la biographie est décrite par le bloc `video:` placé en tête de
`content/_index.fr.md` et de `content/_index.en.md` (penser aux deux fichiers) :

- `id` : l'identifiant YouTube, c'est-à-dire ce qui suit `v=` dans l'adresse de la vidéo ;
- `vignette` : l'image affichée avant la lecture, au format 16:9, déposée dans `assets/img/` ;
- `titre` et `description` : le texte affiché sous la vidéo.

Pour retirer la vidéo, supprimer le bloc `video:` dans les deux fichiers. Rien n'est chargé
depuis YouTube tant que le visiteur ne clique pas sur la vignette.

## Changer la photo

Remplacer `assets/img/portrait.jpg` par un portrait **vertical au format 4:5**
(par exemple 640 × 800 px), visage dans le tiers supérieur, sous le même nom.

## Prévisualiser en local (facultatif)

Avec [Hugo](https://gohugo.io/installation/) (version *extended* 0.162.0) et Python 3 :

```bash
python3 scripts/import_publications.py
hugo server
```

puis ouvrir <http://localhost:1313>.
