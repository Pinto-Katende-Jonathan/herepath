# Advanced guide

You don't need any of this for everyday use. Reach for these tools when you need
custom project markers, test helpers, deployment overrides, or deeper debugging.

## Custom markers: `find_root()`

`find_root()` searches for a root using **your own criteria**, without caching
anything and without touching the session root. Build the criteria with
`has_file`, `has_dir`, or `has_glob`. A folder matches if it satisfies **any** of
them.

```python
from herepath import find_root, has_file, has_dir, has_glob

find_root(has_file("Makefile"))                    # look for a Makefile
find_root(has_file("Makefile"), has_dir(".git"))   # Makefile OR a .git folder
find_root(has_glob("*.toml"), start="sub/folder")  # start elsewhere
```

This is the equivalent of `rprojroot::find_root` in R, for users who want
control without changing how `here()` behaves.

!!! info "The three criteria builders"
    | Builder | Matches a folder that contains... |
    |---------|-----------------------------------|
    | `has_file("name")` | a file named `name` |
    | `has_dir("name")`  | a subfolder named `name` |
    | `has_glob("*.ext")`| at least one file matching the glob |

## Changing the default markers: `set_criteria()`

If your organisation uses a custom marker (say `company_project.json`), you can
replace the detection criteria for the **whole session**:

```python
from herepath import set_criteria, reset_criteria, has_file, has_dir

set_criteria(has_file("company_project.json"), has_dir("src"))
here()   # now uses these markers

reset_criteria()   # back to the default markers
```

!!! warning "set_criteria replaces, it does not add"
    `set_criteria` **replaces** the defaults; it does not append to them. If you
    want to keep `.here` or `.git`, include them in your call:

    ```python
    set_criteria(has_file("company_project.json"), has_file(".here"), has_dir(".git"))
    ```

    Both `set_criteria()` and `reset_criteria()` clear the cached root, so the
    change takes effect on the next `here()` call.

## In tests: `using_root()`

This context manager pins the root for the duration of a block, then restores the
previous state on exit. Ideal for tests.

```python
from herepath import using_root, here

def test_reading(tmp_path):
    with using_root(tmp_path):
        assert here("data") == tmp_path / "data"
    # the previous root is restored here
```

!!! warning "Single-threaded only"
    `using_root` saves and restores **process-global** state. It is meant for
    single-threaded use (tests, notebooks). Do not mutate the root from another
    thread (`reset()`, `i_am()`, another `using_root()`) while a block is active:
    the restore on exit would overwrite the concurrent change. If you need a
    per-thread or per-task root, manage it yourself.

## Forcing the root: `HEREPATH_ROOT`

In Docker, CI, or deployment, auto-detection may not apply. You can force the
root with an environment variable:

```bash
HEREPATH_ROOT=/app python analysis/report.py
```

If the value is not an existing directory, `here()` raises a `ValueError`
immediately, so a misconfiguration fails loudly. An explicit `i_am()` call still
takes precedence.

!!! note "Precedence order"
    When `here()` resolves the root, it checks, in order:

    1. An explicit `i_am()` / `using_root()` / `set_here()` declaration.
    2. The `HEREPATH_ROOT` environment variable.
    3. Auto-detection via the active criteria.
    4. Fallback to the current working directory.

## Debugging detection: `dr_here(trace=True)`

When `herepath` picks the wrong root, ask for the full search trace:

```python
from herepath import dr_here
dr_here(trace=True)
```

```
here() starts at /project.
- This directory contains a file `pyproject.toml`
...

Searching from:
  /project/notebooks
Checking:
  /project/notebooks
  /project   <- contains a file `pyproject.toml`
Matched:
  /project
```

You see exactly which folders were examined and which one won. Handy to paste
into a GitHub issue.

## When *not* to use herepath

`herepath` is for code you run from inside a project: scripts, notebooks,
analyses. It is **not** for an installed library, because once a package is
installed, the source tree no longer exists. To read data shipped with an
installed package, use
[`importlib.resources`](https://docs.python.org/3/library/importlib.resources.html)
instead.

## Bonus: a file picker with pyfilechoose

`pyfilechoose` is another small package (same author) that ports R's
`file.choose()` to Python: it opens a window to pick a file and returns its path.
It pairs nicely with `herepath`, because its `initialdir` parameter accepts a
starting folder, and `here()` provides exactly that: a stable project folder.

```bash
pip install pyfilechoose
```

```python
from herepath import here
from pyfilechoose import file_choose, files_choose

# the window opens directly inside the project's data/ folder
path = file_choose(initialdir=here("data"))

# multiple files, starting from the project root
paths = files_choose(initialdir=here())
```

The idea: `herepath` decides *where to look* (a reliable project folder), and
`pyfilechoose` lets the user *choose what* inside it.

!!! warning
    `pyfilechoose` opens a graphical window (via tkinter). Use it interactively
    (scripts, notebooks), not on a server or in CI.

## Differences from the R package

`herepath` is a faithful port of R's `here`: same philosophy, same four core
functions (`here`, `i_am`, `set_here`, `dr_here`). If you know R, you're on
familiar ground. But there are differences. Some are forced by Python, some
`herepath` adds on purpose.

| Aspect | R `here` | `herepath` |
|--------|----------|------------|
| Return type | string | `pathlib.Path` object |
| Replaces | `file.path()` | `os.path.join()` |
| When the root is resolved | at package load (`library(here)`) | on the first `here()` call (lazy) |
| Detection engine | delegates to `rprojroot` | its own `Criterion` system, dependency-free |
| Startup message | yes (printed on attach) | no (silent import), but `i_am()` confirms |

The three differences that matter most:

1. **Return type.** R returns strings; `herepath` returns `Path` objects. Handier
   with `open()`, `pandas`, etc. Call `str()` if you need a string.
2. **Resolution timing.** In R the root is fixed at package load. Python has no
   such hook, so `herepath` resolves on the first call.
3. **Root markers.** `herepath` replaces R markers with Python ones:

| | R `here` | `herepath` |
|---|----------|------------|
| Common | `.here`, `.vscode`, `_quarto.yml`, `.git`/`.svn` | same, plus `.idea`, `.hg`, `*.Rproj` (compat) |
| Specific | `DESCRIPTION`, `renv.lock`, `remake.yml`, `.projectile` | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |

!!! note
    `herepath` deliberately excludes `requirements.txt`, which is too often
    duplicated in `docs/` or `tests/` and would anchor the root in the wrong
    place.

What `herepath` adds that R's `here` doesn't have:

- `reset()`, and `find_root()` with `has_file` / `has_dir` / `has_glob` (in R
  these live in `rprojroot`, not `here`).
- `set_criteria()` / `reset_criteria()` to change the markers.
- `using_root()` for tests.
- The `HEREPATH_ROOT` environment variable.
- A `herepath` CLI command.
- The `dr_here(trace=True)` mode.
- Thread-safety (a lock).

So: the same core API as R, adapted to Python (`Path` return, Python markers,
lazy resolution), with fewer dependencies and a few extra conveniences.
