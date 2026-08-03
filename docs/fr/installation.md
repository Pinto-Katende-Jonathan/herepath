# Installation

## Prérequis

`herepath` fonctionne sur **Python 3.8 et plus récent** et n'a **aucune
dépendance**. Il est testé sur CPython 3.8 à 3.13 sous Linux, macOS et Windows.

## Installer depuis PyPI

```bash
pip install herepath
```

!!! tip "Un seul nom partout"
    Tu installes `herepath`, tu fais `import herepath`, et tu obtiens une commande
    `herepath` dans ton terminal. Il n'y a rien d'autre à retenir.

    Un paquet `pyhere` sans rapport, d'un autre auteur, existe sur PyPI.
    `herepath` est nommé exprès pour éviter toute confusion avec lui.

### Vérifier l'installation

```bash
herepath --version
```

Ou depuis Python :

```python
import herepath
print(herepath.__version__)
```

## Installer dans un environnement virtuel (recommandé)

Isoler les dépendances de chaque projet est une bonne pratique. Crée d'abord un
environnement virtuel, puis installe :

=== "Linux / macOS"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install herepath
    ```

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install herepath
    ```

## Installer pour le développement

Si tu veux travailler sur `herepath` lui-même (et devenir
[contributeur·rice](contributing.md) !), clone le dépôt et installe-le en mode
éditable avec les extras de développement :

```bash
git clone https://github.com/Pinto-Katende-Jonathan/herepath
cd herepath
pip install -e ".[dev]"
```

Pour construire ce site de documentation en local, installe plutôt les extras
`docs` :

```bash
pip install -e ".[docs]"
mkdocs serve
```

Ouvre ensuite <http://127.0.0.1:8000> dans ton navigateur.

## Étape suivante

Te voilà installé·e et prêt·e. Direction le [Tutoriel](tutorial.md) pour
apprendre les idées de base une par une.
