# Tutorial: User guide

This guide teaches `herepath` one idea at a time. Start at the top and go at
your own pace. By the end you'll know everything you need for everyday use.

!!! note "Following along"
    Every code block is self-contained. You can paste them into a script or a
    notebook inside any project and watch what happens.

## 1. The problem herepath solves

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

This works... *as long as* you launch the script from the `analysis/` folder. If
you run it from the project root, or from a notebook, or from your editor, the
path `../data/sales.csv` points somewhere else and you get an error.

The real issue: the path depends on **where you launch the code** (the "working
directory"), not on **where the file lives**.

!!! success "What herepath does"
    `herepath` finds your project root once, then builds every path from that
    root. It no longer matters where you launch your code.

## 2. Your first step: `here()`

`here()` builds a path starting from the project root.

```python
from herepath import here

here()                          # the project root
here("data", "sales.csv")       # root/data/sales.csv
here("data/sales.csv")          # same, "/" works too
```

The result is always an **absolute path** (a `pathlib.Path` object). You can pass
it straight to `open()`, `pandas`, and friends:

```python
import pandas as pd
df = pd.read_csv(here("data", "sales.csv"))
```

This code runs correctly from **any** folder. That's the whole point.

!!! tip
    Because `here()` returns a `Path`, you can do path things with it:
    `here("data").exists()`, `here("data") / "sub" / "file.csv"`, and so on. Need
    a plain string? Wrap it: `str(here("data"))`.

### How does herepath find the root?

On the first call to `here()`, it starts in the current folder and walks up
through the parent folders until it finds one that contains a **project marker**.
The default markers, in order:

| Category        | Markers |
|-----------------|---------|
| Explicit        | `.here` |
| Python          | `pyproject.toml`, `setup.py`, `setup.cfg`, `Pipfile`, `poetry.lock`, `environment.yml` |
| Editors         | `.vscode/`, `.idea/`, `*.Rproj`, `_quarto.yml` |
| Version control | `.git`, `.hg/`, `.svn/` |

The **closest** folder containing one of these markers wins. If nothing is found,
`herepath` falls back to the current working directory.

## 3. Understanding the decision: `dr_here()`

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

It tells you **where** the root is and **why** (here, because of
`pyproject.toml`).

## 4. The best practice: `i_am()`

This is the recommended way to fix the root. Put this call at the very top of
your script, or in the first cell of your notebook:

```python
from herepath import i_am, here

i_am("analysis/report.py")

df = pd.read_csv(here("data", "sales.csv"))
```

You are declaring: *"this file is `analysis/report.py` relative to the root."*
`herepath` walks up the folders until it finds one that really does contain
`analysis/report.py`, and pins that folder as the root.

!!! success "Why this is safer"
    If you run the script from the wrong place, or someone moved the file, you
    get a **clear error** instead of a silent bug:

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

If two projects have a file at the same path (say `scripts/run.py`), you can tell
them apart with a unique marker inside the file:

```python
# at the top of scripts/run.py, within the first 100 lines:
# id: 7f3a1c2e-...
i_am("scripts/run.py", uuid="7f3a1c2e-...")
```

`herepath` will check that the file it found really contains that string.

## 5. When no marker exists: `set_here()`

Sometimes your project has none of the default markers. You can create one
yourself: an empty file called `.here`.

```python
from herepath import set_here
set_here()           # creates .here in the current folder
```

Or from the command line:

=== "Linux / macOS"

    ```bash
    touch .here
    ```

=== "Windows (PowerShell)"

    ```powershell
    New-Item .here -ItemType File
    ```

From then on, the folder containing `.here` is recognised as the root.

## 6. In a notebook: `reset()`

A notebook stays open for a long time. If you move files or change folders along
the way, `herepath` keeps the root it found on the first call in memory. To force
it to look again:

```python
from herepath import reset
reset()
here()   # re-detects the root
```

This is also handy in tests.

## 7. From the command line

Installing the package also gives you a `herepath` command, useful in shell
scripts and Makefiles.

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

If anything fails, the command prints `Error: ...` and returns exit code 1, with
no unreadable traceback, so your shell script can react cleanly.

See the [Command line](command-line.md) page for the full reference.

## Recap

You now know everything for everyday use:

| You want to...                  | Use |
|---------------------------------|-----|
| A path from the root            | `here("data", "x.csv")` |
| Pin the root cleanly            | `i_am("path/to/script.py")` |
| Understand the chosen root      | `dr_here()` |
| Create a root marker            | `set_here()` or a `.here` file |
| Re-detect (notebook, test)      | `reset()` |
| Work from the shell             | `herepath`, `herepath --report` |

## Next step

That covers the essentials. When you need custom markers, test helpers, or
deployment overrides, continue to the [Advanced guide](advanced.md).
