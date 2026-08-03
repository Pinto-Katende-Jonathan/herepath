# Guide avancé

Tu n'as besoin de rien de tout ça pour un usage quotidien. Utilise ces outils
quand il te faut des marqueurs de projet sur mesure, des aides pour les tests, des
réglages de déploiement ou du débogage approfondi.

## Marqueurs sur mesure : `find_root()`

`find_root()` cherche une racine selon **tes propres critères**, sans rien mettre
en cache et sans toucher à la racine de la session. Construis les critères avec
`has_file`, `has_dir` ou `has_glob`. Un dossier correspond s'il satisfait **l'un**
d'eux.

```python
from herepath import find_root, has_file, has_dir, has_glob

find_root(has_file("Makefile"))                    # cherche un Makefile
find_root(has_file("Makefile"), has_dir(".git"))   # Makefile OU dossier .git
find_root(has_glob("*.toml"), start="sous/dossier")  # part d'ailleurs
```

C'est l'équivalent du `rprojroot::find_root` de R, pour les utilisateurs qui
veulent du contrôle sans changer le comportement de `here()`.

!!! info "Les trois constructeurs de critères"
    | Constructeur | Correspond à un dossier qui contient... |
    |--------------|------------------------------------------|
    | `has_file("nom")` | un fichier nommé `nom` |
    | `has_dir("nom")`  | un sous-dossier nommé `nom` |
    | `has_glob("*.ext")`| au moins un fichier correspondant au motif |

## Changer les marqueurs par défaut : `set_criteria()`

Si ton organisation utilise un marqueur maison (par exemple
`company_project.json`), tu peux remplacer les critères de détection pour **toute
la session** :

```python
from herepath import set_criteria, reset_criteria, has_file, has_dir

set_criteria(has_file("company_project.json"), has_dir("src"))
here()   # utilise maintenant ces marqueurs

reset_criteria()   # revient aux marqueurs par défaut
```

!!! warning "set_criteria remplace, il n'ajoute pas"
    `set_criteria` **remplace** les défauts ; il ne s'ajoute pas. Si tu veux
    garder `.here` ou `.git`, inclus-les dans ton appel :

    ```python
    set_criteria(has_file("company_project.json"), has_file(".here"), has_dir(".git"))
    ```

    `set_criteria()` et `reset_criteria()` vident la racine en cache, donc le
    changement prend effet au prochain appel à `here()`.

## Dans les tests : `using_root()`

Ce gestionnaire de contexte fixe la racine le temps d'un bloc, puis remet l'état
précédent en sortie. Idéal pour les tests.

```python
from herepath import using_root, here

def test_lecture(tmp_path):
    with using_root(tmp_path):
        assert here("data") == tmp_path / "data"
    # la racine d'avant est rétablie ici
```

!!! warning "Mono-thread uniquement"
    `using_root` sauvegarde et restaure un état **global au processus**. C'est
    prévu pour du code mono-thread (tests, notebooks). Ne modifie pas la racine
    depuis un autre thread (`reset()`, `i_am()`, un autre `using_root()`) pendant
    qu'un bloc est actif : la restauration en sortie écraserait le changement
    concurrent. Si tu as besoin d'une racine par thread ou par tâche, gère-la
    toi-même.

## Forcer la racine : `HEREPATH_ROOT`

En Docker, en CI ou en déploiement, la détection automatique peut ne pas
s'appliquer. Tu peux alors imposer la racine avec une variable d'environnement :

```bash
HEREPATH_ROOT=/app python analyse/rapport.py
```

Si la valeur n'est pas un dossier existant, `here()` lève une `ValueError` tout de
suite, pour que la mauvaise configuration se voie. Un appel explicite à `i_am()`
reste prioritaire.

!!! note "Ordre de priorité"
    Quand `here()` résout la racine, il vérifie, dans l'ordre :

    1. Une déclaration explicite `i_am()` / `using_root()` / `set_here()`.
    2. La variable d'environnement `HEREPATH_ROOT`.
    3. La détection automatique via les critères actifs.
    4. Le repli sur le répertoire de travail courant.

## Déboguer une détection : `dr_here(trace=True)`

Quand `herepath` choisit la mauvaise racine, demande la trace complète de la
recherche :

```python
from herepath import dr_here
dr_here(trace=True)
```

```
here() starts at /projet.
- This directory contains a file `pyproject.toml`
...

Searching from:
  /projet/notebooks
Checking:
  /projet/notebooks
  /projet   <- contains a file `pyproject.toml`
Matched:
  /projet
```

Tu vois exactement quels dossiers ont été examinés et lequel a gagné. Pratique à
coller dans un ticket GitHub.

## Quand ne *pas* utiliser herepath

`herepath` est fait pour le code que tu lances depuis un projet : scripts,
notebooks, analyses. Il n'est **pas** fait pour une bibliothèque installée, car
une fois le paquet installé, l'arborescence des sources n'existe plus. Pour lire
des données livrées avec un paquet installé, utilise
[`importlib.resources`](https://docs.python.org/3/library/importlib.resources.html)
à la place.

## Bonus : un sélecteur de fichiers avec pyfilechoose

`pyfilechoose` est un autre petit paquet (même auteur) qui porte le
`file.choose()` de R en Python : il ouvre une fenêtre pour choisir un fichier et
renvoie son chemin. Il se marie bien avec `herepath`, parce que son paramètre
`initialdir` accepte un dossier de départ, et `here()` fournit justement ça : un
dossier stable du projet.

```bash
pip install pyfilechoose
```

```python
from herepath import here
from pyfilechoose import file_choose, files_choose

# la fenêtre s'ouvre directement dans le dossier data/ du projet
chemin = file_choose(initialdir=here("data"))

# plusieurs fichiers, en partant de la racine du projet
chemins = files_choose(initialdir=here())
```

L'idée : `herepath` décide *où regarder* (un dossier fiable du projet), et
`pyfilechoose` laisse l'utilisateur *choisir quoi* dedans.

!!! warning
    `pyfilechoose` ouvre une fenêtre graphique (via tkinter). Réserve-le à un
    usage interactif (scripts, notebooks), pas à un serveur ou à la CI.

## Différences avec le paquet R

`herepath` est un portage fidèle du `here` de R : même philosophie, mêmes quatre
fonctions de base (`here`, `i_am`, `set_here`, `dr_here`). Si tu connais le R, tu
es en terrain connu. Mais il y a des différences : certaines imposées par Python,
d'autres que `herepath` ajoute volontairement.

| Aspect | R `here` | `herepath` |
|--------|----------|------------|
| Type de retour | chaîne de caractères | objet `pathlib.Path` |
| Remplace | `file.path()` | `os.path.join()` |
| Quand la racine est résolue | au chargement du paquet (`library(here)`) | au premier appel à `here()` (paresseux) |
| Moteur de détection | délègue à `rprojroot` | son propre système `Criterion`, sans dépendance |
| Message au démarrage | oui (affiché à l'attache) | non (import silencieux), mais `i_am()` confirme |

Les trois différences qui comptent vraiment :

1. **Type de retour.** R renvoie des chaînes, `herepath` renvoie des `Path`. Plus
   pratique avec `open()`, `pandas`, etc. Fais `str()` si tu veux une chaîne.
2. **Moment de la résolution.** En R, la racine est fixée au chargement du paquet.
   Python n'a pas ce point d'accroche, donc `herepath` résout au premier appel.
3. **Les marqueurs de racine.** `herepath` remplace les marqueurs R par des
   marqueurs Python :

| | R `here` | `herepath` |
|---|----------|------------|
| Communs | `.here`, `.vscode`, `_quarto.yml`, `.git`/`.svn` | idem, plus `.idea`, `.hg`, `*.Rproj` (compat) |
| Spécifiques | `DESCRIPTION`, `renv.lock`, `remake.yml`, `.projectile` | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |

!!! note
    `herepath` exclut volontairement `requirements.txt`, trop souvent dupliqué
    dans `docs/` ou `tests/`, ce qui ancrerait la racine au mauvais endroit.

Ce que `herepath` ajoute et que le `here` de R n'a pas :

- `reset()`, et `find_root()` avec `has_file` / `has_dir` / `has_glob` (en R, ça
  vit dans `rprojroot`, pas dans `here`).
- `set_criteria()` / `reset_criteria()` pour changer les marqueurs.
- `using_root()` pour les tests.
- La variable d'environnement `HEREPATH_ROOT`.
- Une commande CLI `herepath`.
- Le mode `dr_here(trace=True)`.
- La sécurité multi-thread (un verrou).

Donc : la même API de base que le R, adaptée à Python (retour `Path`, marqueurs
Python, résolution paresseuse), avec moins de dépendances et quelques commodités
en plus.
