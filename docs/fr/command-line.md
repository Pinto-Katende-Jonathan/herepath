# Ligne de commande

Installer le paquet te donne une commande `herepath`. Elle est pratique dans les
scripts shell, les Makefiles et les pipelines de CI où tu veux un chemin ancré sur
la racine du projet sans écrire de Python.

## Utilisation

```bash
herepath [composants ...] [options]
```

## Exemples

```bash
herepath                      # affiche la racine du projet
herepath data ventes.csv      # affiche racine/data/ventes.csv
herepath data/ventes.csv      # pareil, les composants peuvent contenir "/"
herepath --report             # rapport de situation : quelle racine, et pourquoi ?
herepath --version            # affiche la version
```

Un motif courant, pour ancrer une commande sur la racine depuis n'importe quel
sous-dossier :

```bash
cat "$(herepath data/ventes.csv)"
```

Dans un Makefile :

```makefile
DATA := $(shell herepath data)

train:
	python train.py --input $(DATA)/ventes.csv
```

## Options

| Option | Court | Description |
|--------|-------|-------------|
| `--report` | `-r` | Affiche un rapport expliquant la racine choisie, puis quitte. |
| `--quiet-report` | `-q` | Avec `--report`, affiche une seule ligne (sans les détails). |
| `--version` | `-V` | Affiche la version et quitte. |
| `--help` | `-h` | Affiche l'aide. |

## Codes de sortie et gestion d'erreur

La CLI est conçue pour bien se comporter dans les scripts shell :

- En cas de succès, elle affiche le chemin (ou le rapport) sur **stdout** et
  renvoie `0`.
- En cas d'échec (par exemple un `HEREPATH_ROOT` mal configuré), elle affiche une
  ligne `Error: ...` propre sur **stderr** et renvoie `1`, sans pile d'appels.

Ça rend la capture shell sûre et prévisible :

```bash
if ROOT="$(herepath)"; then
    echo "La racine du projet est $ROOT"
else
    echo "herepath n'a pas trouvé de racine de projet" >&2
fi
```

!!! tip "Forcer la racine en CI"
    En CI ou en Docker, où la détection automatique peut ne pas s'appliquer, fixe
    la variable d'environnement
    [`HEREPATH_ROOT`](advanced.md#forcer-la-racine-herepath_root) :

    ```bash
    HEREPATH_ROOT=/app herepath data/ventes.csv
    ```
