# apeneranda.github.io

Site académique d'Adrien Peneranda, maître de conférences en sciences de gestion à
Sciences Po Toulouse (LEREPS) : <https://apeneranda.github.io> (anglais, langue par défaut)
et <https://apeneranda.github.io/fr/> (français).

- Générateur : [Hugo](https://gohugo.io/) 0.162.0, gabarits propres au dépôt (aucun thème ni
  module externe), mise en page inspirée du thème Academic.
- Publications : `publications.bib` (+ `publications-en.json` pour les titres traduits) →
  `scripts/import_publications.py` (bibliothèque standard Python) → une page par référence
  et par langue, régénérées à chaque publication.
- Recherche : index JSON par langue (`layouts/home.searchindex.json` → `/search.json`,
  `/fr/search.json`) interrogé dans le navigateur par `assets/js/search.js`, sans service extérieur.
- Déploiement : GitHub Actions → GitHub Pages (`.github/workflows/deploy.yml`).
- Aucun cookie, aucune mesure d'audience, aucune ressource tierce chargée par les pages.

Pour toute mise à jour (CV, publications, textes, photo) : voir [MISE-A-JOUR.md](MISE-A-JOUR.md).
