# herepath tutorial: from beginner to advanced

This guide explains `herepath` step by step. Start at the top and go at your own
pace. Each section adds a single idea.

## 1. The problem it solves

Imagine this project:

```
my-project/
├── pyproject.toml
├── data/
│   └── sales.csv
└── analysis/
    └── report.py
```

Inside `report.py`, you want to read `data/sales.csv`. The naïve way:

```python
import pandas as pd
df = pd.read_csv("../data/sales.csv")
```

This works... as long as you launch the script from the `analysis/` folder. If you
launch it from the project root, or from a notebook, or from your editor, the path
`../data/sales.csv` points somewhere else and you get an error.

The real issue: the path depends on where you launch the code (the "working
directory"), not on where the file lives.

`herepath` fixes this. It finds your project root once, then builds every path
from that root. It no longer matters where you launch the code.

## 2. Installation

```bash
pip install herepath
```

One name throughout: you install `herepath`, you import `herepath`, and you get a
`herepath` command.

## 3. First step: `here()`

`here()` builds a path starting from the project root.

```python
from herepath import here

here()                          # the project root
here("data", "sales.csv")       # root/data/sales.csv
here("data/sales.csv")          # same, "/" works too
```

The result is always an absolute path (a `pathlib.Path` object). You can pass it
straight to `open()`, `pandas`, etc:

```python
import pandas as pd
df = pd.read_csv(here("data", "sales.csv"))
```

This code runs from any folder. That's the whole point.

### How does herepath find the root?

On the first call to `here()`, it starts in the current directory and walks up
through the parent directories until it finds one that contains a project marker.
The default markers, in order:

| Category        | Markers |
|-----------------|---------|
| Explicit        | `.here` |
| Python          | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Editors         | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Version control | `.git`, `.hg/`, `.svn/` |

The closest directory containing one of these markers wins. If nothing is found,
herepath uses the current working directory.

## 4. Understanding the decision: `dr_here()`

If `here()` doesn't point where you expect, ask it to explain itself:

```python
from herepath import dr_here
dr_here()
```

Typical output:

```
here() starts at /home/me/my-project.
- This directory contains a file `pyproject.toml`
- Initial working directory: /home/me/my-project/analysis
- Current working directory: /home/me/my-project/analysis
```

It tells you where the root is and why (here, because of `pyproject.toml`).

## 5. The best practice: `i_am()`

This is the recommended way to fix the root. Put this call at the very top of your
script, or in the first cell of your notebook:

```python
from herepath import i_am, here

i_am("analysis/report.py")

df = pd.read_csv(here("data", "sales.csv"))
```

You declare: "this file is `analysis/report.py` relative to the root." herepath
walks up the directories until it finds one that really contains
`analysis/report.py`, and pins that directory as the root.

The benefit is safety. If you run the script from the wrong place, or someone moved
the file, you get a clear error instead of a silent bug:

```
Could not find associated project in working directory or any parent directory.
- Path in project: analysis/report.py
- Current working directory: /tmp
Please run from within the project associated with this file and try again.
```

By the way, `i_am()` prints a small confirmation line. To silence it:

```python
i_am("analysis/report.py", quiet=True)
```

### Extra safety: `uuid`

If two projects have a file at the same path (for example `scripts/run.py`), you
can tell them apart with a unique identifier present in the file:

```python
# at the top of scripts/run.py, within the first 100 lines:
# id: 7f3a1c2e-...
i_am("scripts/run.py", uuid="7f3a1c2e-...")
```

herepath will check that the file it found really contains that string.

## 6. When no marker exists: `set_here()`

Sometimes your project has none of the default markers. You can create one
yourself: an empty file named `.here`.

```python
from herepath import set_here
set_here()           # creates .here in the current directory
```

Or from the command line:

```bash
touch .here
```

From then on, the directory containing `.here` is recognised as the root.

## 7. In a notebook: `reset()`

A notebook stays open for a long time. If you move files or change directory along
the way, herepath keeps the root from the first call in memory. To force it to look
again:

```python
from herepath import reset
reset()
here()   # re-detects the root
```

This is also handy in tests.

## 8. From the command line

Installing the package also provides a `herepath` command. Useful in shell scripts
and Makefiles.

```bash
herepath                      # print the project root
herepath data sales.csv       # print root/data/sales.csv
herepath --report             # explain the chosen root
herepath --version
```

A concrete example: anchor a command at the root from any subfolder.

```bash
cat "$(herepath data/sales.csv)"
```

If anything fails, the command prints `Error: ...` and returns exit code 1, with no
unreadable traceback. Your shell script can therefore react cleanly.

## Bonus: open a file picker with pyfilechoose

`pyfilechoose` is another small package (same author) that ports R's `file.choose()`
to Python: it opens a window to pick a file and returns its path. It pairs nicely
with herepath, because its `initialdir` parameter accepts a starting folder, and
`here()` provides exactly that: a stable project folder.

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

Then you read the chosen file as usual:

```python
import pandas as pd
df = pd.read_csv(file_choose(initialdir=here("data")))
```

The idea: herepath decides *where to look* (a reliable project folder),
pyfilechoose lets the user *choose what* in that folder. It's useful for
interactive scripts or notebooks. Since `pyfilechoose` opens a graphical window
(via tkinter), keep it for interactive use, not a server or CI.

---

From here on, we move to the advanced functions. You don't need them for normal
use.

## 9. Custom markers: `find_root()`

`find_root()` searches for a root using your own criteria, without caching anything
and without touching the session root. Build the criteria with `has_file`,
`has_dir`, or `has_glob`. A directory matches if it satisfies any of them.

```python
from herepath import find_root, has_file, has_dir, has_glob

find_root(has_file("Makefile"))                 # look for a Makefile
find_root(has_file("Makefile"), has_dir(".git"))  # Makefile OR a .git directory
find_root(has_glob("*.toml"), start="sub/folder")
```

This is the equivalent of R's `rprojroot::find_root`. For users who want control,
without changing the behaviour of `here()`.

## 10. Changing the default markers: `set_criteria()`

If your organisation uses a custom marker (for example `company_project.json`), you
can replace the detection criteria for the whole session:

```python
from herepath import set_criteria, reset_criteria, has_file, has_dir

set_criteria(has_file("company_project.json"), has_dir("src"))
here()   # now uses these markers

reset_criteria()   # back to the default markers
```

Careful: `set_criteria` replaces the defaults, it does not append. If you want to
keep `.here` or `.git`, include them in your call.

## 11. In tests: `using_root()`

This context manager pins the root for the duration of a block, then restores the
previous state on exit. Ideal for tests.

```python
from herepath import using_root, here

def test_reading(tmp_path):
    with using_root(tmp_path):
        assert here("data") == tmp_path / "data"
    # the previous root is restored here
```

A small warning: `using_root` mutates process-global state. It is meant for
single-threaded code (tests, notebooks), not for multiple threads changing the root
at the same time.

## 12. Forcing the root: `HEREPATH_ROOT`

In Docker, CI, or deployment, auto-detection may not apply. You can then force the
root with an environment variable:

```bash
HEREPATH_ROOT=/app python analysis/report.py
```

If the value is not an existing directory, `here()` raises a `ValueError` right
away, so the misconfiguration is visible. An explicit `i_am()` call still takes
precedence.

## 13. Debugging detection: `dr_here(trace=True)`

When herepath picks the wrong root, ask for the full search trace:

```python
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

You see exactly which directories were examined and which one won. Handy to paste
into a GitHub issue.

## 14. When not to use herepath

`herepath` is for code you run from within a project: scripts, notebooks, analyses.
It is not for an installed library, because once a package is installed the source
tree no longer exists. To read data shipped with an installed package, use
`importlib.resources`.

## 15. Differences from R's `here`

`herepath` is a faithful port of R's `here`: same philosophy, same four core
functions (`here`, `i_am`, `set_here`, `dr_here`). If you know R, you're on familiar
ground. But there are differences, some forced by Python, others that herepath adds.

| Aspect | R `here` | `herepath` |
|---|---|---|
| Return type | string | `pathlib.Path` object |
| Replaces | `file.path()` | `os.path.join()` |
| When the root is resolved | at package load (`library(here)`) | on the first `here()` call (lazy) |
| Detection engine | delegates to `rprojroot` | its own `Criterion` system, dependency-free |
| Startup message | yes (printed on attach) | no (silent import), but `i_am()` confirms |

The three differences that matter most:

1. Return type. R returns strings, herepath returns `Path`. Handier with `open()`,
   `pandas`, etc. Call `str()` if you want a string.
2. Resolution timing. In R, the root is fixed at package load, based on the current
   directory at that moment. Python has no such hook, so herepath resolves on the
   first call.
3. The root markers. herepath replaces R markers with Python ones:

| | R `here` | `herepath` |
|---|---|---|
| Common | `.here`, `.vscode`, `_quarto.yml`, `.git`/`.svn` | same, plus `.idea`, `.hg`, `*.Rproj` (compat) |
| Specific | DESCRIPTION, `renv.lock`, `remake.yml`, `.projectile` | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |

Note: herepath deliberately excludes `requirements.txt`, too often duplicated in
`docs/` or `tests/`.

What herepath adds that R's `here` doesn't have:

- `reset()`, `find_root()` with `has_file`/`has_dir`/`has_glob` (in R, this lives in
  `rprojroot`, not `here`).
- `set_criteria()` / `reset_criteria()` to change the markers.
- `using_root()` for tests.
- The `HEREPATH_ROOT` environment variable.
- A `herepath` CLI command.
- The `dr_here(trace=True)` mode.
- Thread-safety (a lock).

What R handles differently:

- The (powerful) `rprojroot` engine on the R side; herepath has a small in-house
  system, lighter and dependency-free.
- Name clashes: in R, loading `plyr` after `here` masks `here()` (you have to write
  `here::here()`). In Python, the namespace is explicit, so this problem doesn't
  exist.

In one sentence: same spirit and same core API as R, adapted to Python (`Path`
return, Python markers, lazy resolution), more minimal on dependencies and richer on
ergonomics.

## 16. Cheat sheet

| You want to... | Use |
|------------|---------|
| A path from the root | `here("data", "x.csv")` |
| Pin the root cleanly | `i_am("path/to/script.py")` |
| Understand the chosen root | `dr_here()` or `dr_here(trace=True)` |
| Create a root marker | `set_here()` or a `.here` file |
| Re-detect (notebook, test) | `reset()` |
| Search with your criteria | `find_root(has_file("..."))` |
| Change the markers | `set_criteria(...)` / `reset_criteria()` |
| Pin the root in a test | `with using_root(path):` |
| Force in production | the `HEREPATH_ROOT` variable |
| From the shell | `herepath`, `herepath --report` |

There you go. You know all of `herepath`, from the first `here()` to custom
criteria.
