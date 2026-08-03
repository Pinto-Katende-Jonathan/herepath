# Installation

## Requirements

`herepath` runs on **Python 3.8 and newer** and has **no dependencies**. It is
tested on CPython 3.8 through 3.13 across Linux, macOS, and Windows.

## Install from PyPI

```bash
pip install herepath
```

!!! tip "One name everywhere"
    You install `herepath`, you `import herepath`, and you get a `herepath`
    command in your terminal. There is nothing else to remember.

    An unrelated `pyhere` package by another author exists on PyPI. `herepath`
    is deliberately named to avoid any confusion with it.

### Verify the installation

```bash
herepath --version
```

Or from Python:

```python
import herepath
print(herepath.__version__)
```

## Install in a virtual environment (recommended)

Keeping each project's dependencies isolated is good practice. Create a virtual
environment first, then install:

=== "Linux / macOS"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install herepath
    ```

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install herepath
    ```

## Install for development

If you want to work on `herepath` itself (and become a
[contributor](contributing.md)!), clone the repository and install it in
editable mode with the development extras:

```bash
git clone https://github.com/Pinto-Katende-Jonathan/herepath
cd herepath
pip install -e ".[dev]"
```

To build this documentation site locally, install the `docs` extras instead:

```bash
pip install -e ".[docs]"
mkdocs serve
```

Then open <http://127.0.0.1:8000> in your browser.

## Next step

You're installed and ready. Head to the [Tutorial](tutorial.md) to learn the
core ideas one at a time.
