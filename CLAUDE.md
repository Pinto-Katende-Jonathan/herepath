# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`herepath` is a Python port of the R [`here`](https://here.r-lib.org/) package: it
builds filesystem paths anchored at a project's root, regardless of the current
working directory. Zero runtime dependencies (standard library only) — this is a
deliberate constraint, do not add any. The package is published to PyPI as
`herepath` (the name avoids collision with an unrelated `pyhere` package).

## Commands

Install for development (from the project directory):

```bash
pip install -e ".[dev]"
pre-commit install        # optional: runs linters on commit
```

Test / lint / type-check:

```bash
pytest                                  # all tests
pytest --cov                            # tests + coverage
pytest tests/test_herepath.py           # a single file
pytest tests/test_herepath.py::test_x   # a single test
ruff check .                            # lint
ruff format .                           # format
mypy                                    # type-check (strict, src/ only)
```

CI runs all of the above on CPython 3.8–3.13 across Linux, macOS, and Windows, so
keep `target-version`/`requires-python` at 3.8 — no 3.9+ syntax in `src/`.

Docs (MkDocs Material, bilingual EN/FR):

```bash
pip install -e ".[docs]"
mkdocs serve                            # http://127.0.0.1:8000/herepath/
```

Publishing to PyPI is automated via GitHub Actions on each GitHub Release; see
`RELEASING.md` for the step-by-step release process and `GITHUB.md` for how the
`.github/` workflows (`ci.yml`, `publish.yml`) work.

## Architecture

- **`src/` layout.** The importable package is `src/herepath/`. `pyproject.toml`
  is the single source of config (build, pytest, coverage, ruff, mypy).
- **`_core.py` is the whole implementation.** Everything lives in this one module.
  `__init__.py` only re-exports the public API and `__version__`; `__main__.py` is
  the `herepath` CLI (an argparse wrapper over `here()` / `dr_here()`).
- **The public API is the contract.** It is the `__all__` list, duplicated in both
  `_core.py` and `__init__.py` — keep them in sync. `here`, `i_am`, `set_here`,
  `dr_here`, `reset`, `find_root`, `has_file`, `has_dir`, `has_glob`, `Criterion`,
  `set_criteria`, `reset_criteria`, `using_root`.

### How root resolution works (the core mental model)

Root detection is **lazy and cached in process-global state** (`_RootState`), all
guarded by a re-entrant `_lock` (an `RLock`, because public functions call each
other — e.g. `i_am` → `dr_here` → `_ensure_root`). `here()` calls `_ensure_root()`,
which resolves the root exactly once, in this precedence order:

1. `HEREPATH_ROOT` env var (validated; raises `ValueError` if not a directory).
2. The nearest ancestor of the cwd matching any active `Criterion`
   (`_active_criteria`, defaulting to `DEFAULT_CRITERIA`). Closest match wins.
3. Fallback: the initial working directory.

`i_am()` and `using_root()` bypass detection and pin the root directly (`declared`).
`reset()` clears the cache so the next call re-detects — essential for notebooks
and tests. Because the root is process-global, `using_root()` is single-threaded
by design (it saves/restores global state around a `yield`).

A `Criterion` is a description + a predicate over a directory; build them with
`has_file` / `has_dir` / `has_glob`. `DEFAULT_CRITERIA` is an **ordered** list
mirroring the R package. Note the deliberate omission of `requirements.txt` as a
marker (it's commonly duplicated in subdirs and would anchor the root wrong) — keep
that omission if editing the list.

## Conventions

- **Docs are bilingual and must stay in sync.** Pages live in `docs/en/` and
  `docs/fr/`, mirrored page-for-page; the root tutorials are `TUTORIAL.en.md`
  (English) and `TUTORIAL.md` (French). Editing one language means mirroring the
  change in the other. New languages are registered under `plugins > i18n >
  languages` in `mkdocs.yml`.
- **User-facing changes** require updating `README.md` and `CHANGELOG.md` (under an
  `## [Unreleased]` heading).
- `herepath` deliberately mirrors the small surface of the R package. Before adding
  a public function, consider whether it fits that minimal philosophy — more
  powerful root-finding belongs in user code or `find_root()`.
- Scope note: `herepath` is for scripts/notebooks/analyses run from within a
  project tree, **not** for use inside an installed library (the source layout no
  longer exists once installed — use `importlib.resources` there).
