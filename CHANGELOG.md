# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-06-13

Initial release — a Python port of the R [`here`](https://here.r-lib.org/)
package.

### Added
- `here(*args)` — build absolute, project-root-relative paths. Drop-in for
  `os.path.join`. Absolute paths are returned unchanged.
- `i_am(path, *, uuid=None, quiet=False)` — declare the current script's
  project-relative location, robustly pinning the project root. Emits a
  one-line situation report on success. Optional `uuid` for extra safety.
- `set_here(path=".", verbose=True)` — create a `.here` marker file.
- `dr_here(show_reason=True)` — print a situation report explaining the root.
- Root detection via ordered criteria: `.here`, Python project files
  (`pyproject.toml`, `setup.py`/`.cfg`, `requirements.txt`, `Pipfile`,
  `poetry.lock`, `environment.yml`), editors (`.vscode`, `.idea`, `*.Rproj`,
  `_quarto.yml`), and VCS roots (`.git`, `.hg`, `.svn`).
- PEP 561 typing support (`py.typed`).
