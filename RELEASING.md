# Guide de publication (release) de `herepath`

Ce guide explique comment publier une nouvelle version de `herepath` sur
[PyPI](https://pypi.org/project/herepath/) à l'aide de GitHub Actions.

La publication est **automatique** : tu crées une *release* sur GitHub, et le
workflow `.github/workflows/publish.yml` construit le paquet et l'envoie sur PyPI
tout seul. Aucun token API à gérer (on utilise le *Trusted Publishing* / OIDC).

---

## 1. Configuration unique (déjà faite)

Ces deux étapes ne se font **qu'une seule fois** pour le projet. Elles sont déjà
en place, mais voici comment les refaire si besoin (nouveau dépôt, etc.).

### a) Déclarer le « Trusted Publisher » sur PyPI

1. Connecte-toi sur <https://pypi.org> (2FA activée, obligatoire).
2. Va sur <https://pypi.org/manage/account/publishing/>.
3. Ajoute un *pending publisher* avec exactement :
   - **PyPI Project Name** : `herepath`
   - **Owner** : `Pinto-Katende-Jonathan`
   - **Repository name** : `herepath`
   - **Workflow name** : `publish.yml`
   - **Environment name** : `pypi`

### b) Créer l'environnement GitHub `pypi`

Dans le dépôt : **Settings → Environments → New environment** → nom : `pypi`.

> Le nom `pypi` doit correspondre exactement à `environment: pypi` dans
> `.github/workflows/publish.yml`.

---

## 2. Publier une nouvelle version (à chaque release)

Suppose qu'on passe de `0.1.0` à `0.2.0`. Remplace le numéro selon ton cas
(voir [versionnage](#versionnage-semver) plus bas).

### Étape 1 — Mettre à jour le numéro de version

Dans `pyproject.toml`, change la ligne :

```toml
version = "0.2.0"
```

Pense aussi à `CITATION.cff` (champs `version` et `date-released`) si tu veux que
la citation reste à jour.

### Étape 2 — Figer le CHANGELOG

Dans `CHANGELOG.md`, transforme la section `## [Unreleased]` en une section
datée, et recrée une section `[Unreleased]` vide au-dessus :

```markdown
## [Unreleased]

## [0.2.0] - 2026-07-15

### Added
- ...
```

### Étape 3 — Vérifier en local (recommandé)

```bash
python -m pytest          # les tests passent
python -m build           # construit le wheel + sdist dans dist/
python -m twine check dist/*   # valide les métadonnées
```

> `pip install build twine` si ces outils ne sont pas installés.

### Étape 4 — Commiter et pousser

```bash
git add pyproject.toml CHANGELOG.md CITATION.cff
git commit -m "Release 0.2.0"
git push origin main
```

### Étape 5 — Créer la release GitHub (déclenche la publication)

Avec le CLI GitHub :

```bash
gh release create v0.2.0 --title "v0.2.0" --notes "Voir CHANGELOG.md."
```

…ou via l'interface web : **Releases → Draft a new release**, tag `v0.2.0`,
puis **Publish release**.

> Le tag suit la convention `v` + numéro (ex. `v0.2.0`).

### Étape 6 — Vérifier

Le workflow se lance automatiquement. Suis-le :

```bash
gh run watch --exit-status        # suit le dernier run jusqu'au bout
```

Puis confirme que la version est en ligne :

```bash
pip index versions herepath       # ou ouvre https://pypi.org/project/herepath/
```

---

## Versionnage (SemVer)

Le projet suit le [versionnage sémantique](https://semver.org/lang/fr/) :
`MAJEUR.MINEUR.CORRECTIF`.

| Type de changement                          | Exemple         |
| ------------------------------------------- | --------------- |
| Correction de bug, rétro-compatible         | `0.1.0 → 0.1.1` |
| Nouvelle fonctionnalité, rétro-compatible   | `0.1.0 → 0.2.0` |
| Changement cassant (API modifiée/supprimée) | `0.1.0 → 1.0.0` |

---

## Points importants

- **Un numéro de version PyPI est définitif.** On ne peut jamais réutiliser ni
  réécraser une version publiée. En cas d'erreur, publie un correctif
  (`0.2.0 → 0.2.1`).
- **La page PyPI affiche le README figé au moment de la publication.** Modifier
  le README après coup n'actualise PyPI qu'à la release suivante.
- **Tester avant de publier** : une fois la release créée, c'est parti. En cas
  de doute, publie d'abord sur [TestPyPI](https://test.pypi.org/) (nécessite un
  *trusted publisher* séparé pointant vers TestPyPI).

---

## En cas d'échec du workflow

1. Ouvre l'onglet **Actions** du dépôt et lis les logs du run échoué
   (`gh run view --log-failed`).
2. Causes fréquentes :
   - Environnement `pypi` ou *trusted publisher* mal configurés (étape 1).
   - Version déjà existante sur PyPI → augmente le numéro.
   - Échec du build → reproduis avec `python -m build` en local.
3. Corrige, supprime la release ratée si besoin (`gh release delete v0.2.0`),
   puis recommence à partir de l'étape adéquate.
