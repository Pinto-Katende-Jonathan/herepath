# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `set_criteria(*criteria)` / `reset_criteria()` — customise the auto-detection
  markers for the session (e.g. company-specific root files).
- `using_root(path)` — context manager that temporarily pins the root and
  restores it on exit (great for tests and notebooks).
- `dr_here(trace=True)` — print the full upward search (every directory checked
  and what matched) to debug unexpected roots.
- Thread-safety: state mutations are guarded by a re-entrant lock.

### Changed
- `requirements.txt` is no longer a default root marker — it is commonly
  duplicated in subdirectories and caused false-positive roots. Add it back with
  `set_criteria(...)` if you rely on it.

### Fixed
- `i_am()` now pins the root under the shared lock (atomic search-and-set),
  consistent with `reset()` and auto-detection.
- `using_root()` documents that it saves/restores the process-global root and is
  intended for single-threaded use; mutating the root from another thread during
  an active block is unsupported.

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
- `reset()` — forget the cached root so it is re-detected on next use
  (notebooks, tests).
- `find_root(*criteria, start=".")` plus `has_file`, `has_dir`, `has_glob`
  criterion builders and the `Criterion` class — a lower-level escape hatch for
  custom root markers, in the spirit of `rprojroot::find_root`.
- `PYHERE_ROOT` environment variable to force the project root (Docker / CI /
  deployment). Raises `ValueError` if it does not point to a directory.
- Root detection via ordered criteria: `.here`, Python project files
  (`pyproject.toml`, `setup.py`/`.cfg`, `requirements.txt`, `Pipfile`,
  `poetry.lock`, `environment.yml`), editors (`.vscode`, `.idea`, `*.Rproj`,
  `_quarto.yml`), and VCS roots (`.git`, `.hg`, `.svn`).
- `pyhere` command-line interface (`pyhere`, `pyhere <paths>`, `--report`,
  `--version`).
- PEP 561 typing support (`py.typed`).
