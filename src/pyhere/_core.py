"""Core implementation of :mod:`pyhere`.

A Python port of the R `here` package (https://here.r-lib.org/).

The project root is discovered by walking the directory tree upwards from the
current working directory until a directory matching one of a set of
*criteria* is found (a ``.here`` file, a ``pyproject.toml``, a ``.git``
directory, ...). Once found, :func:`here` builds paths relative to that root,
acting as a drop-in replacement for :func:`os.path.join`.

The root can also be declared explicitly and robustly with :func:`i_am`, forced
via the ``PYHERE_ROOT`` environment variable, or searched for with arbitrary
criteria via :func:`find_root`.

.. note::
   ``pyhere`` is meant for scripts, notebooks and analyses -- code run from
   within a project tree. It is **not** meant for use inside an *installed*
   library: there, the source layout no longer exists, so use
   :mod:`importlib.resources` to access packaged data instead.
"""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator, Union

__all__ = [
    "here",
    "i_am",
    "set_here",
    "dr_here",
    "reset",
    "find_root",
    "has_file",
    "has_dir",
    "has_glob",
    "Criterion",
    "set_criteria",
    "reset_criteria",
    "using_root",
]

#: Environment variable that, when set to an existing directory, forces the
#: project root used by auto-detection (Docker / CI / deployment escape hatch).
ENV_VAR = "PYHERE_ROOT"

PathLike = Union[str, Path]

# Guards the module-global root/criteria state. An RLock (re-entrant) is used
# because some public functions call others that re-acquire it (e.g. i_am ->
# dr_here -> _ensure_root). pyhere is built for scripts and notebooks, not heavy
# concurrency, but this prevents torn reads if reset()/i_am() race with here().
_lock = threading.RLock()


class Criterion:
    """A single rule that decides whether a directory is the project root."""

    def __init__(self, description: str, testfun: Callable[[Path], bool]):
        self.description = description
        self._testfun = testfun

    def test(self, directory: Path) -> bool:
        try:
            return bool(self._testfun(directory))
        except OSError:
            return False

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Criterion({self.description!r})"


def has_file(name: str) -> Criterion:
    """A criterion that matches a directory containing a file named ``name``."""
    return Criterion(
        f"contains a file `{name}`",
        lambda d: (d / name).is_file(),
    )


def has_dir(name: str) -> Criterion:
    """A criterion that matches a directory containing a subdirectory ``name``."""
    return Criterion(
        f"contains a directory `{name}`",
        lambda d: (d / name).is_dir(),
    )


def has_glob(pattern: str) -> Criterion:
    """A criterion that matches a directory containing a file matching ``pattern``."""
    return Criterion(
        f"contains a file matching `{pattern}`",
        lambda d: any(d.glob(pattern)),
    )


def _has_entry(name: str, description: str) -> Criterion:
    return Criterion(description, lambda d: (d / name).exists())


# Ordered list of default criteria, mirroring (and Pythonising) the R package.
# Note: deliberately *no* `requirements.txt` -- it is commonly duplicated in
# subdirectories (docs/, tests/, requirements/), which would falsely anchor the
# root there. Project/lock files and VCS roots are reliable; loose dep lists are
# not.
DEFAULT_CRITERIA: list[Criterion] = [
    has_file(".here"),
    # Python project markers
    has_file("pyproject.toml"),
    has_file("setup.py"),
    has_file("setup.cfg"),
    has_file("Pipfile"),
    has_file("poetry.lock"),
    has_file("environment.yml"),
    # Editors / IDEs / other project systems
    has_dir(".vscode"),
    has_dir(".idea"),
    has_glob("*.Rproj"),
    has_file("_quarto.yml"),
    # Version control roots (a `.git` worktree may be a file, not a directory)
    _has_entry(".git", "contains a `.git` directory or file (Git root)"),
    has_dir(".hg"),
    has_dir(".svn"),
]

# The criteria actually used by auto-detection; swappable via set_criteria().
_active_criteria: list[Criterion] = list(DEFAULT_CRITERIA)


def set_criteria(*criteria: Criterion) -> None:
    """Replace the criteria used by auto-detection for this session.

    Useful for organisations with their own root markers, e.g.::

        from pyhere import set_criteria, has_file, has_dir
        set_criteria(has_file("company_project.json"), has_dir("src"))

    This clears any cached root so the new criteria take effect immediately.
    Built-in markers are not kept unless you include them. Call
    :func:`reset_criteria` to restore the defaults.
    """
    global _active_criteria
    with _lock:
        if not criteria:
            raise ValueError("set_criteria() requires at least one criterion.")
        _active_criteria = list(criteria)
        reset()


def reset_criteria() -> None:
    """Restore the default auto-detection criteria and clear the cached root."""
    global _active_criteria
    with _lock:
        _active_criteria = list(DEFAULT_CRITERIA)
        reset()


class _RootState:
    """Holds the resolved project root for the running session."""

    def __init__(self) -> None:
        self.root: Path | None = None
        self.wd: Path | None = None
        self.reason: str | None = None
        self.declared: bool = False  # True once i_am() pinned the root

    def set(self, root: Path, reason: str, declared: bool) -> None:
        self.root = Path(root).resolve()
        self.wd = Path.cwd()
        self.reason = reason
        self.declared = declared


_state = _RootState()


def _ancestors(start: Path) -> Iterator[Path]:
    start = start.resolve()
    yield start
    yield from start.parents


def _find_root(start: Path, criteria: list[Criterion]) -> tuple[Path | None, str | None]:
    """Return ``(root, reason)`` for the first ancestor matching a criterion."""
    for directory in _ancestors(start):
        for crit in criteria:
            if crit.test(directory):
                return directory, crit.description
    return None, None


def _root_from_env() -> Path | None:
    """Return the root forced via ``PYHERE_ROOT``, validating it if set."""
    value = os.environ.get(ENV_VAR)
    if not value:
        return None
    path = Path(value).expanduser()
    if not path.is_dir():
        raise ValueError(f"{ENV_VAR} is set to {value!r}, which is not an existing directory.")
    return path


def _ensure_root() -> None:
    with _lock:
        if _state.root is not None:
            return

        env_root = _root_from_env()
        if env_root is not None:
            _state.set(env_root, f"is set via the {ENV_VAR} environment variable", declared=False)
            return

        start = Path.cwd()
        root, reason = _find_root(start, _active_criteria)
        if root is None:
            _state.set(
                start,
                "is the initial working directory (no root criteria matched)",
                declared=False,
            )
        else:
            assert reason is not None  # found together with root
            _state.set(root, reason, declared=False)


def reset() -> None:
    """Forget the cached project root so it is re-detected on the next call.

    Useful in long-lived sessions such as Jupyter notebooks (e.g. after moving
    files or changing the working directory) and in tests. The next call to
    :func:`here` re-runs detection from scratch.
    """
    with _lock:
        _state.root = None
        _state.wd = None
        _state.reason = None
        _state.declared = False


@contextmanager
def using_root(path: PathLike) -> Iterator[Path]:
    """Temporarily pin the project root to ``path``, restoring it on exit.

    Primarily for tests and notebooks::

        with using_root(tmp_path):
            assert here("data") == tmp_path / "data"
        # previous root (or auto-detection) restored here

    Parameters
    ----------
    path:
        Directory to use as the project root for the duration of the block.

    Yields
    ------
    pathlib.Path
        The resolved root in effect inside the block.
    """
    with _lock:
        saved = (_state.root, _state.wd, _state.reason, _state.declared)
        _state.set(Path(path), "was set via a `using_root()` block", declared=True)
        current = _state.root
    try:
        assert current is not None
        yield current
    finally:
        with _lock:
            _state.root, _state.wd, _state.reason, _state.declared = saved


def _file_contains(path: Path, needle: str, n: int = 100) -> bool:
    """Return True if ``needle`` appears in the first ``n`` lines of ``path``."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for i, line in enumerate(handle):
                if i >= n:
                    break
                if needle in line:
                    return True
    except OSError:
        return False
    return False


def here(*args: PathLike) -> Path:
    """Build a path relative to the project root.

    Use as a drop-in replacement for :func:`os.path.join`; the result is
    always an absolute path anchored at the project root, regardless of the
    current working directory.

    Each argument may itself contain ``/``-separated components. Absolute
    paths are returned unchanged, so it is safe to pass either project-relative
    or absolute paths::

        here()                       # the project root
        here("data", "x.csv")        # root/data/x.csv
        here("data/x.csv")           # same -- components may contain "/"
        data = here("data")          # absolute
        here(data, "x.csv")          # data/x.csv -- absolute anchor kept

    Parameters
    ----------
    *args:
        Path components below the project root. Can be empty, in which case
        the project root itself is returned.

    Returns
    -------
    pathlib.Path
        The absolute path to the requested location.
    """
    _ensure_root()
    assert _state.root is not None
    if not args:
        return _state.root
    # joinpath() resets to the last absolute component, which gives exactly the
    # documented "absolute paths are returned unchanged" behaviour.
    return _state.root.joinpath(*(str(a) for a in args))


def i_am(path: PathLike, *, uuid: str | None = None, quiet: bool = False) -> Path:
    """Declare the location of the current script relative to the project root.

    Call this near the top of a script or notebook. It walks up from the
    current working directory until it finds a directory that contains
    ``path``, and pins that directory as the project root. This protects
    against running a script from an unexpected directory.

    On success it prints a one-line situation report (``here() starts at ...``),
    mirroring the R package; pass ``quiet=True`` to suppress it.

    Parameters
    ----------
    path:
        The project-relative path to the current script. Must be relative.
    uuid:
        Optional. If given, a unique string that must appear within the first
        100 lines of the file, for extra safety against moved/renamed files.
    quiet:
        Suppress the informative message. Defaults to False.

    Returns
    -------
    pathlib.Path
        The resolved project root.

    Raises
    ------
    ValueError
        If ``path`` is absolute.
    FileNotFoundError
        If no matching project directory is found.
    """
    rel = Path(path)
    if rel.is_absolute():
        raise ValueError(f"`path` must be relative to the project root, not absolute: {path}")

    start = Path.cwd()
    for directory in _ancestors(start):
        candidate = directory / rel
        if candidate.is_file() and (uuid is None or _file_contains(candidate, uuid)):
            reason = f"contains the file `{rel.as_posix()}`"
            if uuid is not None:
                reason += " with the matching identifier"
            _state.set(directory, reason, declared=True)
            if not quiet:
                dr_here(show_reason=False)
            return _state.root  # type: ignore[return-value]

    lines = [
        "Could not find associated project in working directory or any parent directory.",
        f"- Path in project: {rel.as_posix()}",
    ]
    if uuid is not None:
        lines.append(f"- File must contain: {uuid}")
    lines.append(f"- Current working directory: {start.resolve()}")
    lines.append("Please run from within the project associated with this file and try again.")
    raise FileNotFoundError("\n".join(lines))


def set_here(path: PathLike = ".", verbose: bool = True) -> Path:
    """Create an empty ``.here`` marker file.

    When :func:`here` encounters such a file it uses the containing directory
    as the project root. Useful when none of the default criteria apply.

    Parameters
    ----------
    path:
        Directory in which to create the ``.here`` file. Defaults to the
        current directory.
    verbose:
        Print a message about what happened. Defaults to True.

    Returns
    -------
    pathlib.Path
        The path to the ``.here`` file.
    """
    directory = Path(path).resolve()
    file_path = directory / ".here"

    if file_path.exists():
        if verbose:
            print(f"File .here already exists in {directory}")
    else:
        file_path.write_text("", encoding="utf-8")
        if verbose:
            print(f"Created file .here in {directory} .")

    return file_path


def _format_trace(start: Path) -> str:
    """Render the upward search, showing which directory matched (debugging)."""
    lines = [f"Searching from:\n  {start.resolve()}", "Checking:"]
    matched: str | None = None
    for directory in _ancestors(start):
        hit = next((c for c in _active_criteria if c.test(directory)), None)
        marker = f"  {directory}"
        if hit is not None:
            lines.append(f"{marker}   <- {hit.description}")
            matched = str(directory)
            break
        lines.append(marker)
    if matched is None:
        lines.append("Matched:\n  (nothing -- fell back to the working directory)")
    else:
        lines.append(f"Matched:\n  {matched}")
    return "\n".join(lines)


def dr_here(show_reason: bool = True, trace: bool = False) -> None:
    """Print a situation report explaining where the project root is and why.

    Parameters
    ----------
    show_reason:
        Include the reason and working-directory details. Defaults to True.
    trace:
        Also print the full upward search (every directory checked and what
        matched). Invaluable when auto-detection picks an unexpected root.
        Defaults to False.
    """
    _ensure_root()
    assert _state.root is not None
    if show_reason:
        message = (
            f"here() starts at {_state.root}."
            f"\n- This directory {_state.reason}"
            f"\n- Initial working directory: {_state.wd}"
            f"\n- Current working directory: {Path.cwd()}"
        )
    else:
        message = f"here() starts at {_state.root}"
    if trace:
        message += "\n\n" + _format_trace(_state.wd or Path.cwd())
    print(message)


def find_root(*criteria: Criterion, start: PathLike = ".") -> Path:
    """Search upwards for a directory matching any of the given criteria.

    A lower-level escape hatch for power users who need custom root markers,
    in the spirit of R's ``rprojroot::find_root``. Unlike :func:`here`, this
    does not cache anything and does not affect the session root.

    Parameters
    ----------
    *criteria:
        One or more :class:`Criterion` objects (build them with
        :func:`has_file`, :func:`has_dir`, :func:`has_glob`). A directory
        matches if it satisfies *any* of them. If none are given, the default
        criteria are used.
    start:
        Directory to start searching from. Defaults to the current directory.

    Returns
    -------
    pathlib.Path
        The first matching ancestor directory.

    Raises
    ------
    FileNotFoundError
        If no ancestor satisfies any criterion.

    Examples
    --------
    >>> from pyhere import find_root, has_file, has_dir
    >>> find_root(has_file("Makefile"), has_dir(".git"))  # doctest: +SKIP
    PosixPath('/home/me/myproject')
    """
    crits = list(criteria) if criteria else _active_criteria
    start_path = Path(start)
    root, _ = _find_root(start_path, crits)
    if root is None:
        descriptions = "\n".join(f"  - {c.description}" for c in crits)
        raise FileNotFoundError(
            f"No root directory found above {start_path.resolve()} matching any of:\n{descriptions}"
        )
    return root
