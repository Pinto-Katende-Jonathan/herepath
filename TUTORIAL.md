# Tutoriel herepath : du débutant à l'avancé

Ce guide explique `herepath` pas à pas. Commence par le début et avance à ton
rythme. Chaque section ajoute une seule idée.

## 1. Le problème que ça résout

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

Ça marche... tant que tu lances le script depuis le dossier `analyse/`. Si tu le
lances depuis la racine du projet, ou depuis un notebook, ou depuis ton éditeur,
le chemin `../data/ventes.csv` pointe ailleurs et tu obtiens une erreur.

Le vrai souci : le chemin dépend de l'endroit d'où tu lances le code (le
"répertoire de travail"), pas de l'endroit où vit le fichier.

`herepath` règle ça. Il trouve la racine de ton projet une fois, puis construit
tous les chemins à partir de cette racine. Peu importe d'où tu lances le code.

## 2. Installation

```bash
pip install herepath
```

Un seul nom : tu installes `herepath`, tu importes `herepath`, et tu obtiens une
commande `herepath`.

## 3. Premier pas : `here()`

`here()` construit un chemin à partir de la racine du projet.

```python
from herepath import here

here()                          # la racine du projet
here("data", "ventes.csv")      # racine/data/ventes.csv
here("data/ventes.csv")         # pareil, le "/" marche aussi
```

Le résultat est toujours un chemin absolu (un objet `pathlib.Path`). Tu peux le
passer directement à `open()`, `pandas`, etc :

```python
import pandas as pd
df = pd.read_csv(here("data", "ventes.csv"))
```

Ce code marche depuis n'importe quel dossier. C'est tout l'intérêt.

### Comment herepath trouve-t-il la racine ?

Au premier appel à `here()`, il part du répertoire courant et remonte les
dossiers parents jusqu'à en trouver un qui contient un marqueur de projet. Les
marqueurs par défaut, dans l'ordre :

| Catégorie | Marqueurs |
|-----------|-----------|
| Explicite | `.here` |
| Python | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Éditeurs | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Gestion de versions | `.git`, `.hg/`, `.svn/` |

Le dossier le plus proche qui contient un de ces marqueurs gagne. Si rien n'est
trouvé, herepath utilise le répertoire courant.

## 4. Comprendre la décision : `dr_here()`

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

Ça te dit où est la racine et pourquoi (ici, à cause de `pyproject.toml`).

## 5. La bonne pratique : `i_am()`

C'est la façon recommandée de fixer la racine. Mets cet appel tout en haut de ton
script ou dans la première cellule de ton notebook :

```python
from herepath import i_am, here

i_am("analyse/rapport.py")

df = pd.read_csv(here("data", "ventes.csv"))
```

Tu déclares : "ce fichier est `analyse/rapport.py` par rapport à la racine".
herepath remonte les dossiers jusqu'à en trouver un qui contient bien
`analyse/rapport.py`, et fixe ce dossier comme racine.

L'avantage, c'est la sécurité. Si tu lances le script depuis le mauvais endroit,
ou si quelqu'un a déplacé le fichier, tu obtiens une erreur claire au lieu d'un
bug silencieux :

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

herepath vérifiera que le fichier trouvé contient bien cette chaîne.

## 6. Quand aucun marqueur n'existe : `set_here()`

Parfois ton projet n'a aucun des marqueurs par défaut. Tu peux en créer un
toi-même : un fichier vide nommé `.here`.

```python
from herepath import set_here
set_here()           # crée .here dans le dossier courant
```

Ou en ligne de commande :

```bash
touch .here
```

À partir de là, le dossier qui contient `.here` est reconnu comme racine.

## 7. Dans un notebook : `reset()`

Un notebook reste ouvert longtemps. Si tu déplaces des fichiers ou changes de
dossier en cours de route, herepath garde en mémoire la racine du premier appel.
Pour le forcer à chercher de nouveau :

```python
from herepath import reset
reset()
here()   # re-détecte la racine
```

C'est aussi pratique dans les tests.

## 8. En ligne de commande

Installer le paquet fournit aussi une commande `herepath`. Utile dans les scripts
shell et les Makefiles.

```bash
herepath                      # affiche la racine du projet
herepath data ventes.csv      # affiche racine/data/ventes.csv
herepath --report             # explique le choix de la racine
herepath --version
```

Exemple concret : ancrer une commande sur la racine depuis n'importe quel
sous-dossier.

```bash
cat "$(herepath data/ventes.csv)"
```

Si quelque chose échoue, la commande affiche `Error: ...` et renvoie le code 1,
sans pile d'appels illisible. Ton script shell peut donc réagir proprement.

## Bonus : ouvrir un sélecteur de fichiers avec pyfilechoose

`pyfilechoose` est un autre petit paquet (même auteur) qui porte le
`file.choose()` de R en Python : il ouvre une fenêtre pour choisir un fichier et
renvoie son chemin. Il se marie bien avec herepath, parce que son paramètre
`initialdir` accepte un dossier de départ, et `here()` fournit justement un
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

Ensuite tu lis le fichier choisi comme d'habitude :

```python
import pandas as pd
df = pd.read_csv(file_choose(initialdir=here("data")))
```

L'idée : herepath décide *où regarder* (un dossier fiable du projet),
pyfilechoose laisse l'utilisateur *choisir quoi* dans ce dossier. C'est utile
pour des scripts interactifs ou des notebooks. Comme `pyfilechoose` ouvre une
fenêtre graphique (via tkinter), réserve-le à un usage interactif, pas à un
serveur ou à la CI.

---

À partir d'ici, on passe aux fonctions avancées. Tu n'en as pas besoin pour un
usage normal.

## 9. Des marqueurs sur mesure : `find_root()`

`find_root()` cherche une racine selon tes propres critères, sans rien mettre en
cache et sans toucher à la racine de la session. Construis les critères avec
`has_file`, `has_dir` ou `has_glob`. Un dossier correspond s'il satisfait l'un
d'eux.

```python
from herepath import find_root, has_file, has_dir, has_glob

find_root(has_file("Makefile"))                 # cherche un Makefile
find_root(has_file("Makefile"), has_dir(".git"))  # Makefile OU dossier .git
find_root(has_glob("*.toml"), start="sous/dossier")
```

C'est l'équivalent du `find_root` de `rprojroot` en R. Pour les utilisateurs qui
veulent du contrôle, sans changer le comportement de `here()`.

## 10. Changer les marqueurs par défaut : `set_criteria()`

Si ton organisation utilise un marqueur maison (par exemple
`company_project.json`), tu peux remplacer les critères de détection pour toute
la session :

```python
from herepath import set_criteria, reset_criteria, has_file, has_dir

set_criteria(has_file("company_project.json"), has_dir("src"))
here()   # utilise maintenant ces marqueurs

reset_criteria()   # revient aux marqueurs par défaut
```

Attention : `set_criteria` remplace les défauts, il ne s'ajoute pas. Si tu veux
garder `.here` ou `.git`, inclus-les dans ton appel.

## 11. Dans les tests : `using_root()`

Ce gestionnaire de contexte fixe la racine le temps d'un bloc, puis remet l'état
précédent en sortie. Idéal pour les tests.

```python
from herepath import using_root, here

def test_lecture(tmp_path):
    with using_root(tmp_path):
        assert here("data") == tmp_path / "data"
    # la racine d'avant est rétablie ici
```

Petit avertissement : `using_root` modifie un état global au processus. C'est
prévu pour du code mono-thread (tests, notebooks), pas pour plusieurs threads qui
changeraient la racine en même temps.

## 12. Forcer la racine : `HEREPATH_ROOT`

En Docker, en CI, ou en déploiement, la détection automatique peut ne pas
s'appliquer. Tu peux alors imposer la racine avec une variable d'environnement :

```bash
HEREPATH_ROOT=/app python analyse/rapport.py
```

Si la valeur n'est pas un dossier existant, `here()` lève une `ValueError` tout
de suite, pour que la mauvaise configuration se voie. Un appel explicite à
`i_am()` reste prioritaire.

## 13. Déboguer une détection : `dr_here(trace=True)`

Quand herepath choisit la mauvaise racine, demande la trace complète de la
recherche :

```python
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

## 14. Quand ne pas utiliser herepath

`herepath` est fait pour le code que tu lances depuis un projet : scripts,
notebooks, analyses. Il n'est pas fait pour une bibliothèque installée, car une
fois le paquet installé, l'arborescence des sources n'existe plus. Pour lire des
données livrées avec un paquet installé, utilise `importlib.resources`.

## 15. Différences avec le `here` de R

`herepath` est un portage fidèle du `here` de R : même philosophie, mêmes quatre
fonctions de base (`here`, `i_am`, `set_here`, `dr_here`). Si tu connais le R, tu
es en terrain connu. Mais il y a des différences, certaines imposées par Python,
d'autres que herepath ajoute.

| Aspect | R `here` | `herepath` |
|---|---|---|
| Type de retour | chaîne de caractères | objet `pathlib.Path` |
| Remplace | `file.path()` | `os.path.join()` |
| Quand la racine est résolue | au chargement du package (`library(here)`) | au premier appel à `here()` (paresseux) |
| Moteur de détection | délègue à `rprojroot` | son propre système `Criterion`, sans dépendance |
| Message au démarrage | oui (affiché à l'attache) | non (import silencieux), mais `i_am()` confirme |

Les trois différences qui comptent vraiment :

1. Type de retour. R renvoie des chaînes, herepath renvoie des `Path`. Plus
   pratique avec `open()`, `pandas`, etc. Fais `str()` si tu veux une chaîne.
2. Moment de la résolution. En R, la racine est fixée au chargement du package,
   d'après le répertoire courant à cet instant. Python n'a pas ce point
   d'accroche, donc herepath résout au premier appel.
3. Les marqueurs de racine. herepath remplace les marqueurs R par des marqueurs
   Python :

| | R `here` | `herepath` |
|---|---|---|
| Communs | `.here`, `.vscode`, `_quarto.yml`, `.git`/`.svn` | idem, plus `.idea`, `.hg`, `*.Rproj` (compat) |
| Spécifiques | DESCRIPTION, `renv.lock`, `remake.yml`, `.projectile` | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |

À noter : herepath exclut volontairement `requirements.txt`, trop souvent
dupliqué dans `docs/` ou `tests/`.

Ce que herepath ajoute et que le `here` de R n'a pas :

- `reset()`, `find_root()` avec `has_file`/`has_dir`/`has_glob` (en R, ça vit
  dans `rprojroot`, pas dans `here`).
- `set_criteria()` / `reset_criteria()` pour changer les marqueurs.
- `using_root()` pour les tests.
- La variable d'environnement `HEREPATH_ROOT`.
- Une commande CLI `herepath`.
- Le mode `dr_here(trace=True)`.
- La sécurité multi-thread (verrou).

Ce que R gère autrement :

- Le moteur `rprojroot` (puissant) côté R ; herepath a un petit système maison,
  plus léger et sans dépendance.
- Les conflits de noms : en R, charger `plyr` après `here` masque `here()` (il
  faut écrire `here::here()`). En Python, l'espace de noms est explicite, donc ce
  problème n'existe pas.

En une phrase : même esprit et même API de base que le R, adapté à Python
(retour `Path`, marqueurs Python, résolution paresseuse), plus minimal côté
dépendances et plus riche côté ergonomie.

## 16. Aide-mémoire

| Tu veux... | Utilise |
|------------|---------|
| Un chemin depuis la racine | `here("data", "x.csv")` |
| Fixer la racine proprement | `i_am("chemin/du/script.py")` |
| Comprendre la racine choisie | `dr_here()` ou `dr_here(trace=True)` |
| Créer un marqueur de racine | `set_here()` ou un fichier `.here` |
| Re-détecter (notebook, test) | `reset()` |
| Chercher avec tes critères | `find_root(has_file("..."))` |
| Changer les marqueurs | `set_criteria(...)` / `reset_criteria()` |
| Fixer la racine dans un test | `with using_root(chemin):` |
| Forcer en prod | variable `HEREPATH_ROOT` |
| Depuis le shell | `herepath`, `herepath --report` |

Voilà. Tu connais tout `herepath`, du premier `here()` aux critères sur mesure.
