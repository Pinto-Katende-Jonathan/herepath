# herepath

[![CI](https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml/badge.svg)](https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/herepath.svg)](https://pypi.org/project/herepath/)
[![Python versions](https://img.shields.io/pypi/pyversions/herepath.svg)](https://pypi.org/project/herepath/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A simpler way to find your files. A Python port of the R [`here`](https://here.r-lib.org/) package.

`herepath` builds paths relative to your project's root, no matter what the
current working directory is. Stop writing brittle `../../data/x.csv` paths or
relying on where a script happens to be launched from.

```python
from herepath import here

here("data", "penguins.csv")
# -> /home/me/myproject/data/penguins.csv   (always, from anywhere)
```

## Installation

```bash
pip install herepath
```

One name everywhere: `pip install herepath`, `import herepath`, and a `herepath`
command. (An unrelated `pyhere` package by another author exists on PyPI;
`herepath` is deliberately named to avoid any confusion with it.)

For local development, from the project directory:

```bash
pip install -e ".[dev]"
```

## How it works

On the first call to `here()`, `herepath` walks up the directory tree from the
current working directory until it finds a directory matching one of these
criteria (in order):

| Category      | Markers |
|---------------|---------|
| Explicit      | `.here` |
| Python        | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Editors       | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Version control | `.git`, `.hg/`, `.svn/` |

The closest matching ancestor wins, so a sub-package in a monorepo resolves to
its own directory. If nothing matches, the current working directory is used as
a fallback. `requirements.txt` is deliberately not a marker: it is too often
duplicated in subdirectories (`docs/`, `tests/`), which would anchor the root in
the wrong place. Override the criteria with
[`set_criteria()`](#set_criteriacriteria--reset_criteria) if you need to.

## API

### `here(*args) -> Path`

Drop-in replacement for `os.path.join`, anchored at the project root.

```python
here()                       # the project root
here("data", "raw", "x.csv") # root/data/raw/x.csv
here("data/raw/x.csv")       # same: components may contain "/"

data = here("data")          # absolute
here(data)                   # returned unchanged
here(data, "x.csv")          # absolute anchor kept -> data/x.csv
```

The result is always an absolute `Path`, so it stays valid even if the working
directory changes later.

### `i_am(path, *, uuid=None) -> Path`

Declare where the current script lives, relative to the project root. This is the
recommended and most robust way to fix the root. Put it near the top of a script
or notebook:

```python
from herepath import i_am, here
i_am("analysis/report.py")

here("data", "penguins.csv")
```

It walks up from the working directory until it finds a directory containing
`path`, and pins that as the root. On success it prints a one-line report
(`here() starts at ...`); pass `quiet=True` to suppress it. If the file can't be
found, it raises `FileNotFoundError` with a descriptive message, which protects
you from running a script in the wrong place. Pass `uuid="..."` to also require a
unique marker string within the first 100 lines of the file, for extra safety.

### `set_here(path=".", verbose=True) -> Path`

Create an empty `.here` marker file to pin a root when no other criterion
applies.

### `reset()`

Forget the cached root so it is re-detected on the next call. Handy in
long-lived sessions like Jupyter notebooks (after moving files or changing
directory) and in tests.

### `find_root(*criteria, start=".") -> Path`

Lower-level escape hatch for custom root markers, in the spirit of R's
`rprojroot::find_root`. Does not cache anything or touch the session root.
Build criteria with `has_file`, `has_dir`, `has_glob`; a directory matches if it
satisfies any of them:

```python
from herepath import find_root, has_file, has_dir

find_root(has_file("Makefile"), has_dir(".git"))
```

### `set_criteria(*criteria)` / `reset_criteria()`

Customise what counts as a project root for the whole session. Useful for
organisations with their own markers:

```python
from herepath import set_criteria, has_file, has_dir

set_criteria(has_file("company_project.json"), has_dir("src"))
# ... here() now uses these markers
reset_criteria()  # back to the built-in defaults
```

### `using_root(path)` context manager

Temporarily pin the root, restoring the previous state on exit. Ideal in tests:

```python
from herepath import using_root, here

with using_root(tmp_path):
    assert here("data") == tmp_path / "data"
# previous root (or auto-detection) restored here
```

### Debugging detection: `dr_here(trace=True)`

When the wrong root is picked, `trace=True` prints the full upward search:

```
Searching from:
  /project/notebooks
Checking:
  /project/notebooks
  /project   <- contains a file `pyproject.toml`
Matched:
  /project
```

### Forcing the root with `HEREPATH_ROOT`

Set the `HEREPATH_ROOT` environment variable to an existing directory to override
auto-detection entirely. This is the recommended escape hatch for Docker, CI,
and deployment, where the heuristics may not apply:

```bash
HEREPATH_ROOT=/app python analysis/report.py
```

If it points to a path that isn't a directory, `here()` raises `ValueError` so
misconfiguration fails loudly. An explicit `i_am()` call still takes precedence.

### `dr_here(show_reason=True)`

Print a situation report explaining where the root is and why, which is useful
when `here()` gives unexpected results.

```
here() starts at /home/me/myproject
- This directory contains a file `pyproject.toml`
- Initial working directory: /home/me/myproject/analysis
- Current working directory: /home/me/myproject/analysis
```

## When not to use herepath

`herepath` is for scripts, notebooks and analyses: code run from within a project
tree. It is not meant for use inside an installed library, because once a package
is installed the source layout no longer exists. To access data bundled with an
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

Installing the package also provides a `herepath` command, handy in shell scripts
and Makefiles:

```bash
herepath                      # print the project root
herepath data penguins.csv    # print root/data/penguins.csv
herepath --report             # situation report (why this root?)
herepath --version

# e.g. anchor a command at the project root from any subdirectory:
cat "$(herepath data/penguins.csv)"
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
on CPython 3.8 to 3.13 across Linux, macOS and Windows.

## License

[MIT](LICENSE), Jonathan Katende Pinto. Inspired by the R
[`here`](https://here.r-lib.org/) package by Kirill Müller and Jennifer Bryan.
