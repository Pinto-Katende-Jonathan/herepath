# Tutoriel : guide de l'utilisateur

Ce guide t'apprend `herepath` une idée à la fois. Commence par le début et avance
à ton rythme. À la fin, tu connaîtras tout ce qu'il faut pour un usage quotidien.

!!! note "Pour suivre"
    Chaque bloc de code est autonome. Tu peux les coller dans un script ou un
    notebook à l'intérieur de n'importe quel projet et regarder ce qui se passe.

## 1. Le problème que herepath résout

Imagine ce projet :

```
mon-projet/
├── pyproject.toml
├── data/
│   └── ventes.csv
└── analyse/
    └── rapport.py
```

Dans `rapport.py`, tu veux lire `data/ventes.csv`. La méthode naïve :

```python
import pandas as pd
df = pd.read_csv("../data/ventes.csv")
```

Ça marche... *tant que* tu lances le script depuis le dossier `analyse/`. Si tu le
lances depuis la racine du projet, ou depuis un notebook, ou depuis ton éditeur,
le chemin `../data/ventes.csv` pointe ailleurs et tu obtiens une erreur.

Le vrai souci : le chemin dépend de **l'endroit d'où tu lances le code** (le
« répertoire de travail »), pas de **l'endroit où vit le fichier**.

!!! success "Ce que fait herepath"
    `herepath` trouve la racine de ton projet une fois, puis construit tous les
    chemins à partir de cette racine. Peu importe d'où tu lances le code.

## 2. Premier pas : `here()`

`here()` construit un chemin à partir de la racine du projet.

```python
from herepath import here

here()                          # la racine du projet
here("data", "ventes.csv")      # racine/data/ventes.csv
here("data/ventes.csv")         # pareil, le "/" marche aussi
```

Le résultat est toujours un **chemin absolu** (un objet `pathlib.Path`). Tu peux
le passer directement à `open()`, `pandas`, etc. :

```python
import pandas as pd
df = pd.read_csv(here("data", "ventes.csv"))
```

Ce code marche depuis **n'importe quel** dossier. C'est tout l'intérêt.

!!! tip
    Comme `here()` renvoie un `Path`, tu peux faire des opérations de chemin :
    `here("data").exists()`, `here("data") / "sous" / "fichier.csv"`, etc. Tu veux
    une simple chaîne ? Enveloppe : `str(here("data"))`.

### Comment herepath trouve-t-il la racine ?

Au premier appel à `here()`, il part du dossier courant et remonte les dossiers
parents jusqu'à en trouver un qui contient un **marqueur de projet**. Les
marqueurs par défaut, dans l'ordre :

| Catégorie | Marqueurs |
|-----------|-----------|
| Explicite | `.here` |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Éditeurs | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Gestion de versions | `.git`, `.hg/`, `.svn/` |

Le dossier **le plus proche** qui contient un de ces marqueurs gagne. Si rien
n'est trouvé, `herepath` utilise le répertoire courant.

## 3. Comprendre la décision : `dr_here()`

Si `here()` ne pointe pas où tu crois, demande-lui de s'expliquer :

```python
from herepath import dr_here
dr_here()
```

Sortie typique :

```
here() starts at /home/moi/mon-projet.
- This directory contains a file `pyproject.toml`
- Initial working directory: /home/moi/mon-projet/analyse
- Current working directory: /home/moi/mon-projet/analyse
```

Ça te dit **où** est la racine et **pourquoi** (ici, à cause de `pyproject.toml`).

## 4. La bonne pratique : `i_am()`

C'est la façon recommandée de fixer la racine. Mets cet appel tout en haut de ton
script, ou dans la première cellule de ton notebook :

```python
from herepath import i_am, here

i_am("analyse/rapport.py")

df = pd.read_csv(here("data", "ventes.csv"))
```

Tu déclares : *« ce fichier est `analyse/rapport.py` par rapport à la racine ».*
`herepath` remonte les dossiers jusqu'à en trouver un qui contient bien
`analyse/rapport.py`, et fixe ce dossier comme racine.

!!! success "Pourquoi c'est plus sûr"
    Si tu lances le script depuis le mauvais endroit, ou si quelqu'un a déplacé le
    fichier, tu obtiens une **erreur claire** au lieu d'un bug silencieux :

    ```
    Could not find associated project in working directory or any parent directory.
    - Path in project: analyse/rapport.py
    - Current working directory: /tmp
    Please run from within the project associated with this file and try again.
    ```

Au passage, `i_am()` affiche une petite ligne de confirmation. Pour la couper :

```python
i_am("analyse/rapport.py", quiet=True)
```

### Sécurité supplémentaire : `uuid`

Si deux projets ont un fichier au même chemin (par exemple `scripts/run.py`), tu
peux les distinguer avec un identifiant unique présent dans le fichier :

```python
# en haut de scripts/run.py, dans les 100 premières lignes :
# id: 7f3a1c2e-...
i_am("scripts/run.py", uuid="7f3a1c2e-...")
```

`herepath` vérifiera que le fichier trouvé contient bien cette chaîne.

## 5. Quand aucun marqueur n'existe : `set_here()`

Parfois ton projet n'a aucun des marqueurs par défaut. Tu peux en créer un
toi-même : un fichier vide nommé `.here`.

```python
from herepath import set_here
set_here()           # crée .here dans le dossier courant
```

Ou en ligne de commande :

=== "Linux / macOS"

    ```bash
    touch .here
    ```

=== "Windows (PowerShell)"

    ```powershell
    New-Item .here -ItemType File
    ```

À partir de là, le dossier qui contient `.here` est reconnu comme racine.

## 6. Dans un notebook : `reset()`

Un notebook reste ouvert longtemps. Si tu déplaces des fichiers ou changes de
dossier en cours de route, `herepath` garde en mémoire la racine du premier appel.
Pour le forcer à chercher de nouveau :

```python
from herepath import reset
reset()
here()   # re-détecte la racine
```

C'est aussi pratique dans les tests.

## 7. En ligne de commande

Installer le paquet fournit aussi une commande `herepath`, utile dans les scripts
shell et les Makefiles.

```bash
herepath                      # affiche la racine du projet
herepath data ventes.csv      # affiche racine/data/ventes.csv
herepath --report             # explique le choix de la racine
herepath --version
```

Un exemple concret : ancrer une commande sur la racine depuis n'importe quel
sous-dossier.

```bash
cat "$(herepath data/ventes.csv)"
```

Si quelque chose échoue, la commande affiche `Error: ...` et renvoie le code 1,
sans pile d'appels illisible, donc ton script shell peut réagir proprement.

Voir la page [Ligne de commande](command-line.md) pour la référence complète.

## Récapitulatif

Tu connais maintenant tout pour un usage quotidien :

| Tu veux... | Utilise |
|------------|---------|
| Un chemin depuis la racine | `here("data", "x.csv")` |
| Fixer la racine proprement | `i_am("chemin/du/script.py")` |
| Comprendre la racine choisie | `dr_here()` |
| Créer un marqueur de racine | `set_here()` ou un fichier `.here` |
| Re-détecter (notebook, test) | `reset()` |
| Travailler depuis le shell | `herepath`, `herepath --report` |

## Étape suivante

Voilà pour l'essentiel. Quand tu auras besoin de marqueurs sur mesure, d'aides
pour les tests ou de réglages pour le déploiement, continue avec le
[Guide avancé](advanced.md).
