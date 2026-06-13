# pyhere

[![CI](https://github.com/katendepinto/py-here/actions/workflows/ci.yml/badge.svg)](https://github.com/katendepinto/py-here/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/py-here.svg)](https://pypi.org/project/py-here/)
[![Python versions](https://img.shields.io/pypi/pyversions/py-here.svg)](https://pypi.org/project/py-here/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A simpler way to find your files — a Python port of the R [`here`](https://here.r-lib.org/) package.

`pyhere` builds paths relative to your project's **root**, no matter what the
current working directory is. Stop writing brittle `../../data/x.csv` paths or
relying on where a script happens to be launched from.

```python
from pyhere import here

here("data", "penguins.csv")
# -> /home/me/myproject/data/penguins.csv   (always, from anywhere)
```

## Installation

```bash
pip install py-here
```

The import name is `pyhere`; the distribution name on PyPI is `py-here`.

For local development, from the project directory:

```bash
pip install -e ".[dev]"
```

## How it works

On the first call to `here()`, `pyhere` walks **up** the directory tree from the
current working directory until it finds a directory matching one of these
criteria (in order):

| Category      | Markers |
|---------------|---------|
| Explicit      | `.here` |
| Python        | `pyproject.toml`, `setup.py`, `setup.cfg`, `requirements.txt`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Editors       | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Version control | `.git`, `.hg/`, `.svn/` |

That directory becomes the project root. If nothing matches, the current
working directory is used as a fallback.

## API

### `here(*args) -> Path`

Drop-in replacement for `os.path.join`, anchored at the project root.

```python
here()                       # the project root
here("data", "raw", "x.csv") # root/data/raw/x.csv
here("data/raw/x.csv")       # same — components may contain "/"

data = here("data")          # absolute
here(data)                   # returned unchanged
here(data, "x.csv")          # absolute anchor kept → data/x.csv
```

The result is always an absolute `Path`, so it stays valid even if the working
directory changes later.

### `i_am(path, *, uuid=None) -> Path`

Declare where the current script lives, relative to the project root. This is
the **recommended** and most robust way to fix the root. Put it near the top of
a script or notebook:

```python
from pyhere import i_am, here
i_am("analysis/report.py")

here("data", "penguins.csv")
```

It walks up from the working directory until it finds a directory containing
`path`, and pins that as the root. On success it prints a one-line report
(`here() starts at ...`); pass `quiet=True` to suppress it. If the file can't be
found, it raises `FileNotFoundError` with a descriptive message — protecting you
from running a script in the wrong place. Pass `uuid="..."` to also require a
unique marker string within the first 100 lines of the file, for extra safety.

### `set_here(path=".", verbose=True) -> Path`

Create an empty `.here` marker file to pin a root when no other criterion
applies.

### `reset()`

Forget the cached root so it is re-detected on the next call. Handy in
long-lived sessions like **Jupyter notebooks** (after moving files or changing
directory) and in tests.

### `find_root(*criteria, start=".") -> Path`

Lower-level escape hatch for custom root markers, in the spirit of R's
`rprojroot::find_root`. Does not cache anything or touch the session root.
Build criteria with `has_file`, `has_dir`, `has_glob`; a directory matches if it
satisfies **any** of them:

```python
from pyhere import find_root, has_file, has_dir

find_root(has_file("Makefile"), has_dir(".git"))
```

### Forcing the root with `PYHERE_ROOT`

Set the `PYHERE_ROOT` environment variable to an existing directory to override
auto-detection entirely. This is the recommended escape hatch for **Docker, CI,
and deployment**, where heuristics may not apply:

```bash
PYHERE_ROOT=/app python analysis/report.py
```

If it points to a path that isn't a directory, `here()` raises `ValueError` so
misconfiguration fails loudly. An explicit `i_am()` call still takes precedence.

### `dr_here(show_reason=True)`

Print a "situation report" explaining where the root is and **why** — useful
when `here()` gives unexpected results.

```
here() starts at /home/me/myproject
- This directory contains a file `pyproject.toml`
- Initial working directory: /home/me/myproject/analysis
- Current working directory: /home/me/myproject/analysis
```

## When *not* to use pyhere

`pyhere` is for scripts, notebooks and analyses — code run from within a project
tree. It is **not** meant for use inside an *installed* library: once a package
is installed, the source layout no longer exists. To access data bundled with an
installed package, use [`importlib.resources`](https://docs.python.org/3/library/importlib.resources.html)
instead.

## Differences from the R package

- Returns `pathlib.Path` objects instead of strings.
- The default root criteria are Python-flavoured (e.g. `pyproject.toml`)
  rather than R-flavoured (e.g. `DESCRIPTION`), while keeping the universal
  markers (`.here`, `.git`, editors).
- The root is resolved lazily on first use (Python has no package-load hook
  tied to a session the way R does).

## Command line

Installing the package also provides a `pyhere` command — handy in shell scripts
and Makefiles:

```bash
pyhere                      # print the project root
pyhere data penguins.csv    # print root/data/penguins.csv
pyhere --report             # situation report (why this root?)
pyhere --version

# e.g. anchor a command at the project root from any subdirectory:
cat "$(pyhere data/penguins.csv)"
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install   # optional: run linters on commit

pytest               # tests
pytest --cov         # tests + coverage
ruff check .         # lint
ruff format .        # format
mypy                 # type-check
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide. The project is tested
on CPython 3.8–3.13 across Linux, macOS and Windows.

## License

[MIT](LICENSE) © Jonathan Katende Pinto. Inspired by the R
[`here`](https://here.r-lib.org/) package by Kirill Müller and Jennifer Bryan.
