# Référence de l'API

Tous les noms publics de `herepath`, avec leur signature et leur comportement.
Importe-les directement depuis le paquet de plus haut niveau :

```python
from herepath import (
    here, i_am, set_here, dr_here, reset,
    find_root, has_file, has_dir, has_glob, Criterion,
    set_criteria, reset_criteria, using_root,
)
```

## Fonctions de base

### `here(*args) -> Path`

Construit un chemin relatif à la racine du projet. Remplaçant direct de
`os.path.join`, renvoyant toujours un `pathlib.Path` absolu.

```python
here()                       # la racine du projet
here("data", "x.csv")        # racine/data/x.csv
here("data/x.csv")           # pareil, les composants peuvent contenir "/"

data = here("data")          # absolu
here(data, "x.csv")          # ancre absolue conservée -> data/x.csv
```

Paramètres :

- `*args` : les composants de chemin sous la racine. Vide, la racine elle-même est
  renvoyée.

Renvoie le `Path` absolu vers l'emplacement demandé.

La racine est résolue paresseusement au premier appel et mise en cache pour la
session. Passe un chemin absolu comme composant et il est renvoyé tel quel.

### `i_am(path, *, uuid=None, quiet=False) -> Path`

Déclare où vit le script courant, par rapport à la racine du projet, et fixe cette
racine. C'est la façon recommandée de fixer la racine. Appelle-la tout en haut
d'un script ou dans la première cellule d'un notebook.

```python
i_am("analyse/rapport.py")
i_am("analyse/rapport.py", quiet=True)            # pas de ligne de confirmation
i_am("scripts/run.py", uuid="7f3a1c2e-...")       # sécurité supplémentaire
```

Paramètres :

- `path` : le chemin du script courant relatif à la racine. Doit être relatif.
- `uuid` (nommé) : optionnel. Une chaîne unique qui doit apparaître dans les 100
  premières lignes du fichier, pour plus de sécurité contre les fichiers déplacés
  ou renommés.
- `quiet` (nommé) : supprime la ligne de confirmation. Défaut `False`.

Renvoie la racine du projet résolue.

Lève :

- `ValueError` si `path` est absolu.
- `FileNotFoundError` si aucun dossier de projet correspondant n'est trouvé.

### `set_here(path=".", verbose=True) -> Path`

Crée un fichier marqueur `.here` vide, fixant une racine là où aucun autre critère
ne s'applique.

```python
set_here()             # crée .here dans le dossier courant
set_here("un/dossier") # crée .here là-bas
```

Paramètres :

- `path` : dossier où créer `.here`. Défaut : dossier courant.
- `verbose` : affiche un message sur ce qui s'est passé. Défaut `True`.

Renvoie le `Path` vers le fichier `.here`.

### `dr_here(show_reason=True, trace=False) -> None`

Affiche un rapport de situation expliquant où est la racine et pourquoi.

```python
dr_here()             # où, et pourquoi
dr_here(trace=True)   # affiche aussi la recherche complète vers le haut
```

Paramètres :

- `show_reason` : inclut la raison et les détails du répertoire de travail. Défaut
  `True`.
- `trace` : affiche aussi chaque dossier examiné et ce qui a correspondu, ce qui
  aide à déboguer une racine inattendue. Défaut `False`.

### `reset() -> None`

Oublie la racine en cache pour qu'elle soit re-détectée au prochain appel. Utile
dans les sessions longues (notebooks Jupyter après avoir déplacé des fichiers ou
changé de dossier) et dans les tests.

## Critères sur mesure

### `find_root(*criteria, start=".") -> Path`

Cherche vers le haut un dossier correspondant à l'un des critères donnés. Une
échappatoire de plus bas niveau qui ne met rien en cache et n'affecte pas la
racine de session.

```python
find_root(has_file("Makefile"), has_dir(".git"))
find_root(has_glob("*.toml"), start="sous/dossier")
```

Paramètres :

- `*criteria` : un ou plusieurs objets `Criterion`. Si aucun n'est donné, les
  critères par défaut actifs sont utilisés.
- `start` (nommé) : dossier de départ. Défaut : dossier courant.

Renvoie le premier dossier ancêtre correspondant. Lève `FileNotFoundError` si
aucun ancêtre ne satisfait un critère.

### `has_file(name) -> Criterion`

Un critère correspondant à un dossier qui contient un fichier nommé `name`.

### `has_dir(name) -> Criterion`

Un critère correspondant à un dossier qui contient un sous-dossier nommé `name`.

### `has_glob(pattern) -> Criterion`

Un critère correspondant à un dossier qui contient au moins un fichier
correspondant au motif glob `pattern` (par exemple `"*.Rproj"`).

### `class Criterion`

Une règle unique décidant si un dossier est la racine du projet. Tu en construis
rarement directement ; utilise `has_file`, `has_dir` ou `has_glob`. Chacun a un
`.description` (utilisé dans les rapports) et une méthode `.test(dossier) -> bool`.

### `set_criteria(*criteria) -> None`

Remplace les critères de détection pour toute la session. Vide la racine en cache.
Exige au moins un critère (lève `ValueError` sinon).

!!! warning
    Ça remplace les défauts. Inclus `.here` / `.git` toi-même si tu veux les
    garder.

### `reset_criteria() -> None`

Restaure les critères de détection par défaut et vide la racine en cache.

## Gestionnaire de contexte

### `using_root(path)`

Fixe temporairement la racine à `path`, restaurant l'état précédent en sortie.
Produit la racine résolue.

```python
with using_root(tmp_path):
    assert here("data") == tmp_path / "data"
# racine précédente rétablie ici
```

!!! warning
    Sauvegarde et restaure un état global au processus, à utiliser en mono-thread
    uniquement (tests, notebooks). Voir le
    [Guide avancé](advanced.md#dans-les-tests-using_root).

## Variable d'environnement

### `HEREPATH_ROOT`

Quand elle est fixée à un dossier existant, force la racine de projet utilisée par
la détection automatique. Si la valeur n'est pas un dossier existant, `here()`
lève `ValueError`. Un appel explicite à `i_am()` reste prioritaire.

```bash
HEREPATH_ROOT=/app python analyse/rapport.py
```

## Attributs du module

### `herepath.__version__`

Une chaîne avec la version installée, par exemple `"0.1.0"`.
