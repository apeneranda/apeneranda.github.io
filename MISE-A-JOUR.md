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
| Bio courte (accueil) | `content/_index.en.md` | `content/_index.fr.md` |
| Bio longue, fonctions, parcours, conférences | `content/bio.en.md` | `content/bio.fr.md` |
| Enseignement et encadrement | `content/enseignement.en.md` | `content/enseignement.fr.md` |
| Phrase d'introduction de la page Conférences | `content/conferences.en.md` | `content/conferences.fr.md` |
| Mentions légales | `content/mentions-legales.en.md` | `content/mentions-legales.fr.md` |

| Autres réglages | Fichier |
|---|---|
| Accueil : nom, fonction, lignes « Research Fellow / Laboratoire », domaines, formation (blocs `fr` et `en`), coordonnées, liens | `data/profil.yaml` |
| Conférences filmées ou enregistrées (page Conférences et accueil) | `data/conferences.yaml` |
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

## Conférences (vidéos, enregistrements, affiches)

La page « Conférences » (« Talks » en anglais) et la rubrique « Interventions récentes »
de l'accueil sont alimentées par un seul fichier, `data/conferences.yaml`. La page affiche
toutes les interventions, l'accueil les deux plus récentes ; le tri par date est automatique.

Chaque intervention est une entrée introduite par un tiret :

```yaml
- date: 2026-11-14                         # jour de l'intervention (AAAA-MM-JJ)
  youtube: xV4M7LzXj3U                     # identifiant de la vidéo
  debut: 5547                              # seconde où commence l'intervention (facultatif)
  vignette: img/bolzano-2026.jpg           # image 16:9 affichée avant la lecture
  affiche: img/bolzano-2026-affiche.jpg    # affiche ou image du colloque (facultatif)
  fr:
    evenement: "Nom du colloque"
    lieu: "Lieu, ville"
    titre: "Titre de l'intervention"
    description: "Quelques lignes de présentation."
  en:
    evenement: "…"
    lieu: "…"
    titre: "…"
    description: "…"
```

- `youtube` : ce qui suit `v=` (ou `/live/`) dans l'adresse de la vidéo. Dans
  `https://www.youtube.com/live/xV4M7LzXj3U?t=5547`, l'identifiant est `xV4M7LzXj3U`
  et `debut` vaut `5547`.
- Pour un enregistrement hébergé ailleurs (audio, autre site), remplacer `youtube` par
  `url: https://…` : la vignette mène alors à cette adresse.
- `vignette` et `affiche` : déposer les images dans `assets/img/` (**Add file → Upload
  files**), puis indiquer leur nom précédé de `img/`. La vignette est recadrée en 16:9 ;
  l'affiche garde ses proportions et s'agrandit au clic. Elle n'apparaît que sur la page
  « Conférences ».

Pour ajouter une intervention, copier une entrée, l'adapter et la coller n'importe où dans
la liste. Rien n'est chargé depuis YouTube tant que le visiteur ne clique pas sur une vignette.

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
