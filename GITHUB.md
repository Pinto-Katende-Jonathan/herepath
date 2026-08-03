# Le dossier `.github/` expliqué

Ce document explique à quoi sert le dossier `.github/`, chacun de ses
sous-dossiers et fichiers, puis détaille les deux workflows YAML
(`ci.yml` et `publish.yml`).

> Ce fichier est une documentation interne pour les mainteneurs. Pour publier une
> version, voir [`RELEASING.md`](RELEASING.md).

---

## À quoi sert le dossier `.github/` ?

`.github/` est un dossier **spécial reconnu par GitHub**. GitHub y cherche
automatiquement de la configuration : les workflows d'automatisation
(*GitHub Actions*), les modèles d'issues et de pull requests, etc. Tu n'as rien à
activer — il suffit que les fichiers soient au bon endroit avec le bon nom.

```
.github/
├── workflows/              ← automatisations GitHub Actions
│   ├── ci.yml              ← tests + lint à chaque push / PR
│   └── publish.yml         ← publication sur PyPI à chaque release
├── ISSUE_TEMPLATE/         ← formulaires proposés à l'ouverture d'une issue
│   ├── bug_report.yml      ← modèle « rapport de bug »
│   ├── feature_request.yml ← modèle « demande de fonctionnalité »
│   └── config.yml          ← réglages du sélecteur d'issues
└── PULL_REQUEST_TEMPLATE.md ← texte pré-rempli à l'ouverture d'une PR
```

---

## Les sous-dossiers et fichiers

### `workflows/` — les automatisations

Chaque fichier `.yml` ici est un **workflow** : une suite d'étapes que GitHub
exécute automatiquement sur ses serveurs quand un évènement se produit (un push,
une pull request, une release…). Détaillé plus bas.

### `ISSUE_TEMPLATE/` — les modèles d'issues

Quand quelqu'un clique sur « New issue », GitHub propose les modèles définis ici
plutôt qu'une zone de texte vide. Cela structure les retours et fait gagner du
temps au mainteneur.

- **`bug_report.yml`** — formulaire de rapport de bug. Les champs `validations:
  required: true` obligent l'utilisateur à remplir l'essentiel (ce qui s'est
  passé, la reproduction, les versions). Le champ « Output of `herepath
  --report` » aide à diagnostiquer un mauvais *root* détecté. Label automatique :
  `bug`.
- **`feature_request.yml`** — formulaire de demande de fonctionnalité. Rappelle
  que `herepath` garde volontairement une petite surface d'API. Label
  automatique : `enhancement`.
- **`config.yml`** — règle le comportement du sélecteur :
  - `blank_issues_enabled: false` → interdit les issues vides, force l'usage des
    modèles.
  - `contact_links` → ajoute un lien « Question / discussion » qui renvoie vers
    les *Discussions* plutôt que vers une issue (les questions ne sont pas des
    bugs).

> Le format `.yml` (et non `.md`) active les **formulaires d'issue** de GitHub
> (champs structurés). C'est plus riche qu'un simple modèle Markdown.

### `PULL_REQUEST_TEMPLATE.md` — le modèle de pull request

Quand quelqu'un ouvre une PR, sa description est pré-remplie avec ce texte : un
résumé à compléter, une *checklist* (tests, `pytest`/`ruff`/`mypy`, mise à jour
du `CHANGELOG`, docs) et une section « issues liées ». Cela uniformise les
contributions et rappelle les vérifications à faire.

---

## Les workflows YAML en détail

Un workflow se lit en trois blocs : **quand** il se déclenche (`on:`), **où** il
tourne (`runs-on:`), et **quoi** il exécute (`jobs:` → `steps:`).

### Notions de base

- **`on:`** — les évènements déclencheurs (push, pull_request, release…).
- **`jobs:`** — un workflow contient un ou plusieurs *jobs*, qui tournent en
  parallèle par défaut. `needs:` force un ordre entre eux.
- **`runs-on:`** — la machine virtuelle (ex. `ubuntu-latest`).
- **`steps:`** — les étapes d'un job, exécutées dans l'ordre.
- **`uses:`** — réutilise une *action* toute faite (ex. `actions/checkout`).
- **`run:`** — exécute une commande shell.
- **`matrix:`** — répète un job sur plusieurs combinaisons (versions, OS).

---

### `ci.yml` — intégration continue (tests + qualité)

**But :** vérifier automatiquement que le code marche et respecte le style, à
chaque modification. C'est le filet de sécurité du projet.

**Quand ça tourne :**

```yaml
on:
  push:
    branches: [main]   # à chaque push sur main
  pull_request:        # à chaque PR
  workflow_dispatch:   # déclenchement manuel (bouton dans l'onglet Actions)
```

**`concurrency:`** — si tu pushes deux fois de suite, l'ancien run est annulé
(`cancel-in-progress: true`) pour ne pas gaspiller de temps machine.

**Job `test` :** lance la suite de tests sur **toutes** les combinaisons
supportées grâce à la `matrix` :

```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
  python-version: ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
```

Soit 3 OS × 6 versions de Python = 18 environnements testés. `fail-fast: false`
fait tourner tous les jobs même si l'un échoue (utile pour voir *quelle*
combinaison casse). Les étapes : récupérer le code, installer Python, installer
le projet en mode dev (`pip install -e ".[dev]"`), lancer `pytest --cov`, puis
envoyer la couverture à Codecov (uniquement depuis un seul environnement, et sans
faire échouer le build si Codecov est indisponible).

**Job `lint` :** vérifie la qualité du code sur un seul environnement :
`ruff check` (lint), `ruff format --check` (formatage), `mypy` (typage strict).

> C'est ce job qui produit les « 2 required status checks » mentionnés par la
> protection de branche : une PR ne peut être fusionnée que si `test` et `lint`
> passent.

---

### `publish.yml` — publication sur PyPI

**But :** construire le paquet et l'envoyer sur PyPI, automatiquement, à chaque
nouvelle release GitHub.

**Quand ça tourne :**

```yaml
on:
  release:
    types: [published]  # quand tu publies une release GitHub
  workflow_dispatch:    # ou manuellement
```

**Job `build` :** récupère le code, installe Python, lance `python -m build` (qui
crée le `.whl` et le `.tar.gz` dans `dist/`), puis **téléverse ces fichiers comme
artefact** pour les passer au job suivant.

**Job `publish` :** `needs: build` → il attend que `build` réussisse. Points
clés :

```yaml
environment: pypi          # l'environnement GitHub « pypi »
permissions:
  id-token: write          # autorise l'authentification OIDC
```

- **`environment: pypi`** — relie ce job à l'environnement GitHub nommé `pypi`
  (Settings → Environments). C'est aussi ce nom qui est déclaré côté PyPI dans le
  *trusted publisher*. Permet d'ajouter des protections (ex. approbation manuelle
  avant publication).
- **`id-token: write`** — c'est le cœur du **Trusted Publishing (OIDC)**. GitHub
  génère un jeton d'identité éphémère que PyPI vérifie. **Aucun token API n'est
  stocké** dans le dépôt : plus sûr et rien à faire tourner manuellement.

Les étapes : télécharger l'artefact `dist/` produit par `build`, puis lancer
l'action officielle `pypa/gh-action-pypi-publish`, qui envoie le contenu de
`dist/` sur PyPI via OIDC.

> Le lien entre les trois éléments — `workflow_name: publish.yml`,
> `environment: pypi`, et le *trusted publisher* configuré sur PyPI — doit être
> **exactement** cohérent, sinon PyPI refuse la publication.

---

## Pour aller plus loin

- Documentation GitHub Actions : <https://docs.github.com/actions>
- Trusted Publishing PyPI : <https://docs.pypi.org/trusted-publishers/>
- Formulaires d'issue : <https://docs.github.com/communities/using-templates-to-encourage-useful-issues-and-pull-requests>
