"""Tests for py_here."""

import os
from pathlib import Path

import pytest

import py_here
from py_here import _core


@pytest.fixture(autouse=True)
def reset_state(monkeypatch, tmp_path):
    """Reset the cached root and run each test inside an isolated tmp dir."""
    monkeypatch.delenv(_core.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    py_here.reset_criteria()  # also clears the cached root
    yield
    py_here.reset_criteria()


def _touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    return path


# --- here() ---------------------------------------------------------------


def test_here_finds_pyproject_root(tmp_path):
    _touch(tmp_path / "pyproject.toml")
    sub = tmp_path / "a" / "b"
    sub.mkdir(parents=True)
    os.chdir(sub)
    assert py_here.here() == tmp_path.resolve()
    assert py_here.here("data", "x.csv") == (tmp_path / "data" / "x.csv").resolve()


def test_here_joins_slash_components(tmp_path):
    _touch(tmp_path / ".here")
    assert py_here.here("data/sub/x.csv") == (tmp_path / "data" / "sub" / "x.csv").resolve()


def test_here_returns_absolute_paths_unchanged(tmp_path):
    _touch(tmp_path / ".here")
    data = py_here.here("data")  # absolute
    assert data.is_absolute()
    # an absolute single arg comes back unchanged
    assert py_here.here(data) == data
    # an absolute anchor is kept, with further components appended
    assert py_here.here(data, "penguins.csv") == data / "penguins.csv"


def test_here_dot_here_marker(tmp_path):
    _touch(tmp_path / ".here")
    deep = tmp_path / "x" / "y" / "z"
    deep.mkdir(parents=True)
    os.chdir(deep)
    assert py_here.here() == tmp_path.resolve()


def test_here_falls_back_to_cwd_when_no_marker(tmp_path, monkeypatch):
    # Force "no criterion matches anywhere" to exercise the fallback path,
    # independent of whatever markers may exist in real ancestor dirs.
    monkeypatch.setattr(_core, "_active_criteria", [])
    assert py_here.here() == tmp_path.resolve()
    assert "no root criteria matched" in _core._state.reason


def test_git_marker_as_directory(tmp_path):
    (tmp_path / ".git").mkdir()
    sub = tmp_path / "src"
    sub.mkdir()
    os.chdir(sub)
    assert py_here.here() == tmp_path.resolve()


def test_git_marker_as_file_worktree(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /elsewhere", encoding="utf-8")
    assert py_here.here() == tmp_path.resolve()


def test_symlinked_subdir_not_resolved_in_result(tmp_path):
    # Regression: only the root is resolve()d; a symlinked component in the
    # result (e.g. `data -> /mnt/shared/data`) must be kept as project/data,
    # not rewritten to its target. (Skips where symlinks aren't permitted.)
    _touch(tmp_path / ".here")
    external = tmp_path / "external_target"
    external.mkdir()
    link = tmp_path / "data"
    try:
        link.symlink_to(external, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not permitted on this platform")
    assert py_here.here("data") == tmp_path.resolve() / "data"
    assert py_here.here("data") != external.resolve()


# --- i_am() ---------------------------------------------------------------


def test_i_am_pins_root(tmp_path):
    _touch(tmp_path / "analysis" / "report.py")
    sub = tmp_path / "analysis"
    os.chdir(sub)
    root = py_here.i_am("analysis/report.py", quiet=True)
    assert root == tmp_path.resolve()
    assert _core._state.declared is True
    assert py_here.here("data") == (tmp_path / "data").resolve()


def test_i_am_prints_message_by_default(tmp_path, capsys):
    _touch(tmp_path / "run.py")
    py_here.i_am("run.py")
    out = capsys.readouterr().out
    assert out.startswith("here() starts at")
    # one-line report (no reason details)
    assert "Current working directory" not in out


def test_i_am_acquires_lock(tmp_path, monkeypatch):
    # Regression: i_am() must pin the root under the lock, like reset().
    _touch(tmp_path / "run.py")
    acquired = []
    real_lock = _core._lock

    class _SpyLock:
        def __enter__(self):
            acquired.append(True)
            return real_lock.__enter__()

        def __exit__(self, *exc):
            return real_lock.__exit__(*exc)

    monkeypatch.setattr(_core, "_lock", _SpyLock())
    py_here.i_am("run.py", quiet=True)
    assert acquired, "i_am() should acquire the lock before mutating state"


def test_i_am_absolute_path_raises(tmp_path):
    with pytest.raises(ValueError):
        py_here.i_am(str(tmp_path / "x.py"))


def test_i_am_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        py_here.i_am("does/not/exist.py")


def test_i_am_uuid_match(tmp_path):
    f = tmp_path / "scripts" / "run.py"
    f.parent.mkdir(parents=True)
    f.write_text("# id: abc-123-unique\nprint('hi')\n", encoding="utf-8")
    root = py_here.i_am("scripts/run.py", uuid="abc-123-unique")
    assert root == tmp_path.resolve()


def test_i_am_uuid_mismatch_raises(tmp_path):
    f = tmp_path / "scripts" / "run.py"
    f.parent.mkdir(parents=True)
    f.write_text("print('hi')\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        py_here.i_am("scripts/run.py", uuid="missing-id")


# --- set_here() -----------------------------------------------------------


def test_set_here_creates_marker(tmp_path):
    result = py_here.set_here(tmp_path, verbose=False)
    assert result == (tmp_path / ".here").resolve()
    assert (tmp_path / ".here").is_file()


def test_set_here_idempotent(tmp_path):
    py_here.set_here(tmp_path, verbose=False)
    # second call should not raise and should report existing file
    result = py_here.set_here(tmp_path, verbose=False)
    assert result.is_file()


# --- dr_here() ------------------------------------------------------------


def test_dr_here_prints_report(tmp_path, capsys):
    _touch(tmp_path / ".here")
    py_here.here()
    py_here.dr_here()
    out = capsys.readouterr().out
    assert "here() starts at" in out
    assert "Current working directory" in out


# --- PYHERE_ROOT env var --------------------------------------------------


def test_env_var_overrides_detection(tmp_path, monkeypatch):
    forced = tmp_path / "forced"
    forced.mkdir()
    _touch(tmp_path / ".here")  # would otherwise win
    monkeypatch.setenv(_core.ENV_VAR, str(forced))
    assert py_here.here() == forced.resolve()
    assert _core.ENV_VAR in _core._state.reason


def test_env_var_invalid_raises(tmp_path, monkeypatch):
    monkeypatch.setenv(_core.ENV_VAR, str(tmp_path / "does-not-exist"))
    with pytest.raises(ValueError):
        py_here.here()


# --- reset() --------------------------------------------------------------


def test_reset_redetects_root(tmp_path):
    _touch(tmp_path / ".here")
    assert py_here.here() == tmp_path.resolve()
    # create a deeper project and move into it; without reset the old root sticks
    deep = tmp_path / "sub"
    deep.mkdir()
    _touch(deep / ".here")
    os.chdir(deep)
    assert py_here.here() == tmp_path.resolve()  # still cached
    py_here.reset()
    assert py_here.here() == deep.resolve()  # re-detected


# --- find_root() ----------------------------------------------------------


def test_find_root_custom_criterion(tmp_path):
    _touch(tmp_path / "Makefile")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    root = py_here.find_root(py_here.has_file("Makefile"), start=deep)
    assert root == tmp_path.resolve()


def test_find_root_any_of_multiple(tmp_path):
    (tmp_path / ".git").mkdir()
    root = py_here.find_root(py_here.has_file("Makefile"), py_here.has_dir(".git"), start=tmp_path)
    assert root == tmp_path.resolve()


def test_find_root_glob(tmp_path):
    _touch(tmp_path / "project.toml")
    root = py_here.find_root(py_here.has_glob("*.toml"), start=tmp_path)
    assert root == tmp_path.resolve()


def test_find_root_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        py_here.find_root(py_here.has_file("definitely-absent.xyz"), start=tmp_path)


def test_find_root_does_not_affect_session(tmp_path):
    _touch(tmp_path / ".here")
    py_here.find_root(py_here.has_file(".here"), start=tmp_path)
    # session root remains uninitialised until here() is called
    assert _core._state.root is None


# --- requirements.txt is NOT a root marker (subdir false-positive) --------


def test_requirements_txt_is_not_a_root_marker(tmp_path):
    # The real root has pyproject.toml; docs/ has its own requirements.txt.
    _touch(tmp_path / "pyproject.toml")
    docs = tmp_path / "docs"
    docs.mkdir()
    _touch(docs / "requirements.txt")
    os.chdir(docs)
    # Must walk past docs/ up to the project root, not stop at docs/.
    assert py_here.here() == tmp_path.resolve()


# --- set_criteria() / reset_criteria() ------------------------------------


def test_set_criteria_custom_marker(tmp_path):
    _touch(tmp_path / "company_project.json")
    sub = tmp_path / "a"
    sub.mkdir()
    os.chdir(sub)
    py_here.set_criteria(py_here.has_file("company_project.json"))
    assert py_here.here() == tmp_path.resolve()


def test_set_criteria_replaces_defaults(tmp_path):
    # .here would normally win, but custom criteria replace the defaults
    _touch(tmp_path / ".here")
    py_here.set_criteria(py_here.has_file("never-present.marker"))
    # nothing matches -> falls back to cwd
    assert py_here.here() == tmp_path.resolve()
    assert "no root criteria matched" in _core._state.reason


def test_set_criteria_requires_argument():
    with pytest.raises(ValueError):
        py_here.set_criteria()


def test_reset_criteria_restores_defaults(tmp_path):
    _touch(tmp_path / ".here")
    py_here.set_criteria(py_here.has_file("nope.marker"))
    py_here.reset_criteria()
    assert py_here.here() == tmp_path.resolve()


# --- using_root() context manager -----------------------------------------


def test_using_root_temporary_override(tmp_path):
    _touch(tmp_path / ".here")
    assert py_here.here() == tmp_path.resolve()
    other = tmp_path / "other"
    other.mkdir()
    with py_here.using_root(other) as root:
        assert root == other.resolve()
        assert py_here.here("data") == (other / "data").resolve()
    # restored to the previous root
    assert py_here.here() == tmp_path.resolve()


def test_using_root_restores_uninitialised_state(tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    with py_here.using_root(other):
        assert py_here.here() == other.resolve()
    # root was uninitialised before the block; it should be again
    assert _core._state.root is None


# --- dr_here(trace=True) --------------------------------------------------


def test_dr_here_trace(tmp_path, capsys):
    _touch(tmp_path / "pyproject.toml")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    os.chdir(deep)
    py_here.here()
    py_here.dr_here(trace=True)
    out = capsys.readouterr().out
    assert "Searching from:" in out
    assert "Checking:" in out
    assert "pyproject.toml" in out
    assert "Matched:" in out
