# herepath

<p align="center">
  <em>Une façon plus simple de retrouver tes fichiers.</em>
</p>

<p align="center">
  <a href="https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml"><img src="https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/herepath/"><img src="https://img.shields.io/pypi/v/herepath.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/herepath/"><img src="https://img.shields.io/pypi/pyversions/herepath.svg" alt="Versions de Python"></a>
  <a href="https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="Licence : MIT"></a>
</p>

Code source : <a href="https://github.com/Pinto-Katende-Jonathan/herepath" target="_blank">github.com/Pinto-Katende-Jonathan/herepath</a>

`herepath` construit des chemins de fichiers relatifs à la racine de ton projet,
peu importe le dossier depuis lequel tu lances ton code. C'est un portage en
Python du paquet R [`here`](https://here.r-lib.org/).

Un chemin relatif comme `../../data/ventes.csv` casse dès que tu lances un script
depuis un autre dossier, un notebook ou ton éditeur. Écris plutôt ceci :

```python
from herepath import here

here("data", "ventes.csv")
# -> /home/moi/mon-projet/data/ventes.csv   (toujours, depuis n'importe où)
```

## Pourquoi herepath ?

Le problème qu'il règle est petit mais constant. Un chemin relatif comme
`../data/ventes.csv` ne pointe pas vers un fichier. Il pointe vers un fichier
relatif à l'endroit où tu te trouves, donc il casse dès que tu te déplaces.

`herepath` trouve la racine de ton projet une fois, puis ancre chaque chemin à
cette racine. Le résultat ne dépend plus de ton répertoire de travail.

Ce qu'il t'apporte :

- **Marche depuis n'importe où.** Lance le même script depuis la racine, un
  sous-dossier, un notebook ou ton IDE. `here()` renvoie le même chemin absolu à
  chaque fois.
- **Aucune dépendance.** Bibliothèque standard uniquement. `herepath` n'ajoute
  rien à ton arbre de dépendances.
- **Une petite API.** Quatre fonctions de base : `here()`, `i_am()`, `set_here()`,
  `dr_here()`. L'essentiel s'apprend en quelques minutes.
- **Une commande shell aussi.** Installer le paquet te donne une commande
  `herepath` pour les scripts et les Makefiles.

## Installation

```bash
pip install herepath
```

Un seul nom partout : tu installes `herepath`, tu importes `herepath`, et tu
obtiens une commande `herepath`. Voir [Installation](installation.md) pour plus de
détails.

## Un petit exemple

Suppose que ton projet ressemble à ça :

```
mon-projet/
├── pyproject.toml
├── data/
│   └── ventes.csv
└── analyse/
    └── rapport.py
```

Dans `analyse/rapport.py` :

```python
from herepath import i_am, here   # (1)!
import pandas as pd

i_am("analyse/rapport.py")        # (2)!

df = pd.read_csv(here("data", "ventes.csv"))  # (3)!
```

1. Importe les deux fonctions dont tu as besoin.
2. Déclare où vit ce fichier, par rapport à la racine du projet. `herepath` sait
   désormais où se trouve la racine.
3. Construis un chemin depuis la racine. Ça marche que tu lances le script depuis
   `mon-projet/`, depuis `analyse/`, ou depuis un notebook trois dossiers plus
   loin.

Plus de `../`, et plus de « ça marche sur ma machine ».

## Par où continuer

- Tu débutes ? Commence par le [Tutoriel](tutorial.md), un parcours pas à pas.
- Besoin de plus de contrôle ? Le [Guide avancé](advanced.md) couvre les marqueurs
  sur mesure, les tests et le déploiement.
- Tu fais du scripting ? Voir la page [Ligne de commande](command-line.md).
- Tu cherches une fonction ? La [Référence de l'API](api-reference.md) liste tout.
- Tu veux aider ? Lis [Contribuer](contributing.md).

## Licence

[MIT](https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/LICENSE), Jonathan
Katende Pinto. Inspiré du paquet R [`here`](https://here.r-lib.org/) de Kirill
Müller et Jennifer Bryan.
