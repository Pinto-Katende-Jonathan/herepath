# herepath

<p align="center">
  <em>A simpler way to find your files.</em>
</p>

<p align="center">
  <a href="https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml"><img src="https://github.com/Pinto-Katende-Jonathan/herepath/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://pypi.org/project/herepath/"><img src="https://img.shields.io/pypi/v/herepath.svg" alt="PyPI"></a>
  <a href="https://pypi.org/project/herepath/"><img src="https://img.shields.io/pypi/pyversions/herepath.svg" alt="Python versions"></a>
  <a href="https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

Source code: <a href="https://github.com/Pinto-Katende-Jonathan/herepath" target="_blank">github.com/Pinto-Katende-Jonathan/herepath</a>

`herepath` builds file paths relative to your project's root, no matter which
folder you run your code from. It is a Python port of the R
[`here`](https://here.r-lib.org/) package.

A relative path like `../../data/sales.csv` breaks the moment you run a script
from a different folder, a notebook, or your editor. Write this instead:

```python
from herepath import here

here("data", "sales.csv")
# -> /home/me/my-project/data/sales.csv   (always, from anywhere)
```

## Why herepath?

The problem it solves is small but constant. A relative path like
`../data/sales.csv` does not point to a file. It points to a file relative to
wherever you happen to be standing, so it breaks as soon as you move.

`herepath` finds the root of your project once, then anchors every path to that
root. The result no longer depends on your current working directory.

A few things it gives you:

- **Works from anywhere.** Run the same script from the project root, a subfolder,
  a notebook, or your IDE. `here()` returns the same absolute path every time.
- **No dependencies.** Pure standard library. `herepath` adds nothing to your
  dependency tree.
- **A small API.** Four core functions: `here()`, `i_am()`, `set_here()`,
  `dr_here()`. You can learn the essentials in a few minutes.
- **A shell command too.** Installing the package also gives you a `herepath`
  command for scripts and Makefiles.

## Installation

```bash
pip install herepath
```

One name everywhere: you install `herepath`, you import `herepath`, and you get a
`herepath` command. See [Installation](installation.md) for more.

## A short example

Suppose your project looks like this:

```
my-project/
├── pyproject.toml
├── data/
│   └── sales.csv
└── analysis/
    └── report.py
```

In `analysis/report.py`:

```python
from herepath import i_am, here   # (1)!
import pandas as pd

i_am("analysis/report.py")        # (2)!

df = pd.read_csv(here("data", "sales.csv"))  # (3)!
```

1. Import the two functions you need.
2. Declare where this file lives, relative to the project root. `herepath` now
   knows where the root is.
3. Build a path from the root. This works whether you run the script from
   `my-project/`, from `analysis/`, or from a notebook three folders away.

No more `../`, and no more "it works on my machine".

## Where to go next

- New here? Start with the [Tutorial](tutorial.md), a step-by-step walkthrough.
- Need more control? The [Advanced guide](advanced.md) covers custom markers,
  tests, and deployment.
- Scripting? See the [Command line](command-line.md) page.
- Looking something up? The [API reference](api-reference.md) lists every function.
- Want to help? Read [Contributing](contributing.md).

## License

[MIT](https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/LICENSE), Jonathan
Katende Pinto. Inspired by the R [`here`](https://here.r-lib.org/) package by
Kirill Müller and Jennifer Bryan.
