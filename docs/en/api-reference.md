# API reference

Every public name in `herepath`, with its signature and behaviour. Import them
all directly from the top-level package:

```python
from herepath import (
    here, i_am, set_here, dr_here, reset,
    find_root, has_file, has_dir, has_glob, Criterion,
    set_criteria, reset_criteria, using_root,
)
```

## Core functions

### `here(*args) -> Path`

Build a path relative to the project root. A drop-in replacement for
`os.path.join`, always returning an absolute `pathlib.Path`.

```python
here()                       # the project root
here("data", "x.csv")        # root/data/x.csv
here("data/x.csv")           # same, components may contain "/"

data = here("data")          # absolute
here(data, "x.csv")          # absolute anchor kept -> data/x.csv
```

Parameters:

- `*args`: path components below the project root. If empty, the root itself is
  returned.

Returns the absolute `Path` to the requested location.

The root is resolved lazily on the first call and cached for the session. Pass an
absolute path as a component and it is returned unchanged.

### `i_am(path, *, uuid=None, quiet=False) -> Path`

Declare where the current script lives, relative to the project root, and pin
that root. This is the recommended way to fix the root. Call it near the top of a
script or the first cell of a notebook.

```python
i_am("analysis/report.py")
i_am("analysis/report.py", quiet=True)            # no confirmation line
i_am("scripts/run.py", uuid="7f3a1c2e-...")       # extra safety
```

Parameters:

- `path`: the project-relative path to the current script. Must be relative.
- `uuid` (keyword-only): optional. A unique string that must appear within the
  first 100 lines of the file, for extra safety against moved or renamed files.
- `quiet` (keyword-only): suppress the one-line confirmation. Default `False`.

Returns the resolved project root.

Raises:

- `ValueError` if `path` is absolute.
- `FileNotFoundError` if no matching project directory is found.

### `set_here(path=".", verbose=True) -> Path`

Create an empty `.here` marker file, pinning a root where no other criterion
applies.

```python
set_here()             # creates .here in the current folder
set_here("some/dir")   # creates .here there
```

Parameters:

- `path`: directory in which to create `.here`. Default: current directory.
- `verbose`: print a message about what happened. Default `True`.

Returns the `Path` to the `.here` file.

### `dr_here(show_reason=True, trace=False) -> None`

Print a situation report explaining where the root is and why.

```python
dr_here()             # where, and why
dr_here(trace=True)   # also print the full upward search
```

Parameters:

- `show_reason`: include the reason and working-directory details. Default
  `True`.
- `trace`: also print every directory checked and what matched, which helps when
  debugging an unexpected root. Default `False`.

### `reset() -> None`

Forget the cached root so it is re-detected on the next call. Useful in
long-lived sessions (Jupyter notebooks after moving files or changing directory)
and in tests.

## Custom criteria

### `find_root(*criteria, start=".") -> Path`

Search upwards for a directory matching any of the given criteria. A lower-level
escape hatch that does not cache anything or affect the session root.

```python
find_root(has_file("Makefile"), has_dir(".git"))
find_root(has_glob("*.toml"), start="sub/folder")
```

Parameters:

- `*criteria`: one or more `Criterion` objects. If none are given, the active
  default criteria are used.
- `start` (keyword): directory to start from. Default: current directory.

Returns the first matching ancestor directory. Raises `FileNotFoundError` if no
ancestor satisfies any criterion.

### `has_file(name) -> Criterion`

A criterion matching a directory that contains a file named `name`.

### `has_dir(name) -> Criterion`

A criterion matching a directory that contains a subdirectory named `name`.

### `has_glob(pattern) -> Criterion`

A criterion matching a directory that contains at least one file matching the
glob `pattern` (for example `"*.Rproj"`).

### `class Criterion`

A single rule deciding whether a directory is the project root. You rarely build
one directly; use `has_file`, `has_dir`, or `has_glob`. Each has a `.description`
(used in reports) and a `.test(directory) -> bool` method.

### `set_criteria(*criteria) -> None`

Replace the auto-detection criteria for the whole session. Clears the cached
root. Requires at least one criterion (raises `ValueError` otherwise).

!!! warning
    This replaces the defaults. Include `.here` / `.git` yourself if you want to
    keep them.

### `reset_criteria() -> None`

Restore the default auto-detection criteria and clear the cached root.

## Context manager

### `using_root(path)`

Temporarily pin the root to `path`, restoring the previous state on exit. Yields
the resolved root.

```python
with using_root(tmp_path):
    assert here("data") == tmp_path / "data"
# previous root restored here
```

!!! warning
    Saves and restores process-global state, so use it single-threaded only
    (tests, notebooks). See the [Advanced guide](advanced.md#in-tests-using_root).

## Environment variable

### `HEREPATH_ROOT`

When set to an existing directory, forces the project root used by
auto-detection. If the value is not an existing directory, `here()` raises
`ValueError`. An explicit `i_am()` call takes precedence.

```bash
HEREPATH_ROOT=/app python analysis/report.py
```

## Module attributes

### `herepath.__version__`

A string with the installed version, for example `"0.1.0"`.
