"""Tests for pyhere."""

import os
from pathlib import Path

import pytest

import pyhere
from pyhere import _core


@pytest.fixture(autouse=True)
def reset_state(monkeypatch, tmp_path):
    """Reset the cached root and run each test inside an isolated tmp dir."""
    monkeypatch.delenv(_core.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    pyhere.reset()
    yield


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
    assert pyhere.here() == tmp_path.resolve()
    assert pyhere.here("data", "x.csv") == (tmp_path / "data" / "x.csv").resolve()


def test_here_joins_slash_components(tmp_path):
    _touch(tmp_path / ".here")
    assert pyhere.here("data/sub/x.csv") == (tmp_path / "data" / "sub" / "x.csv").resolve()


def test_here_returns_absolute_paths_unchanged(tmp_path):
    _touch(tmp_path / ".here")
    data = pyhere.here("data")  # absolute
    assert data.is_absolute()
    # an absolute single arg comes back unchanged
    assert pyhere.here(data) == data
    # an absolute anchor is kept, with further components appended
    assert pyhere.here(data, "penguins.csv") == data / "penguins.csv"


def test_here_dot_here_marker(tmp_path):
    _touch(tmp_path / ".here")
    deep = tmp_path / "x" / "y" / "z"
    deep.mkdir(parents=True)
    os.chdir(deep)
    assert pyhere.here() == tmp_path.resolve()


def test_here_falls_back_to_cwd_when_no_marker(tmp_path, monkeypatch):
    # Force "no criterion matches anywhere" to exercise the fallback path,
    # independent of whatever markers may exist in real ancestor dirs.
    monkeypatch.setattr(_core, "DEFAULT_CRITERIA", [])
    assert pyhere.here() == tmp_path.resolve()
    assert "no root criteria matched" in _core._state.reason


def test_git_marker_as_directory(tmp_path):
    (tmp_path / ".git").mkdir()
    sub = tmp_path / "src"
    sub.mkdir()
    os.chdir(sub)
    assert pyhere.here() == tmp_path.resolve()


def test_git_marker_as_file_worktree(tmp_path):
    (tmp_path / ".git").write_text("gitdir: /elsewhere", encoding="utf-8")
    assert pyhere.here() == tmp_path.resolve()


# --- i_am() ---------------------------------------------------------------


def test_i_am_pins_root(tmp_path):
    _touch(tmp_path / "analysis" / "report.py")
    sub = tmp_path / "analysis"
    os.chdir(sub)
    root = pyhere.i_am("analysis/report.py", quiet=True)
    assert root == tmp_path.resolve()
    assert _core._state.declared is True
    assert pyhere.here("data") == (tmp_path / "data").resolve()


def test_i_am_prints_message_by_default(tmp_path, capsys):
    _touch(tmp_path / "run.py")
    pyhere.i_am("run.py")
    out = capsys.readouterr().out
    assert out.startswith("here() starts at")
    # one-line report (no reason details)
    assert "Current working directory" not in out


def test_i_am_absolute_path_raises(tmp_path):
    with pytest.raises(ValueError):
        pyhere.i_am(str(tmp_path / "x.py"))


def test_i_am_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pyhere.i_am("does/not/exist.py")


def test_i_am_uuid_match(tmp_path):
    f = tmp_path / "scripts" / "run.py"
    f.parent.mkdir(parents=True)
    f.write_text("# id: abc-123-unique\nprint('hi')\n", encoding="utf-8")
    root = pyhere.i_am("scripts/run.py", uuid="abc-123-unique")
    assert root == tmp_path.resolve()


def test_i_am_uuid_mismatch_raises(tmp_path):
    f = tmp_path / "scripts" / "run.py"
    f.parent.mkdir(parents=True)
    f.write_text("print('hi')\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        pyhere.i_am("scripts/run.py", uuid="missing-id")


# --- set_here() -----------------------------------------------------------


def test_set_here_creates_marker(tmp_path):
    result = pyhere.set_here(tmp_path, verbose=False)
    assert result == (tmp_path / ".here").resolve()
    assert (tmp_path / ".here").is_file()


def test_set_here_idempotent(tmp_path):
    pyhere.set_here(tmp_path, verbose=False)
    # second call should not raise and should report existing file
    result = pyhere.set_here(tmp_path, verbose=False)
    assert result.is_file()


# --- dr_here() ------------------------------------------------------------


def test_dr_here_prints_report(tmp_path, capsys):
    _touch(tmp_path / ".here")
    pyhere.here()
    pyhere.dr_here()
    out = capsys.readouterr().out
    assert "here() starts at" in out
    assert "Current working directory" in out


# --- PYHERE_ROOT env var --------------------------------------------------


def test_env_var_overrides_detection(tmp_path, monkeypatch):
    forced = tmp_path / "forced"
    forced.mkdir()
    _touch(tmp_path / ".here")  # would otherwise win
    monkeypatch.setenv(_core.ENV_VAR, str(forced))
    assert pyhere.here() == forced.resolve()
    assert _core.ENV_VAR in _core._state.reason


def test_env_var_invalid_raises(tmp_path, monkeypatch):
    monkeypatch.setenv(_core.ENV_VAR, str(tmp_path / "does-not-exist"))
    with pytest.raises(ValueError):
        pyhere.here()


# --- reset() --------------------------------------------------------------


def test_reset_redetects_root(tmp_path):
    _touch(tmp_path / ".here")
    assert pyhere.here() == tmp_path.resolve()
    # create a deeper project and move into it; without reset the old root sticks
    deep = tmp_path / "sub"
    deep.mkdir()
    _touch(deep / ".here")
    os.chdir(deep)
    assert pyhere.here() == tmp_path.resolve()  # still cached
    pyhere.reset()
    assert pyhere.here() == deep.resolve()  # re-detected


# --- find_root() ----------------------------------------------------------


def test_find_root_custom_criterion(tmp_path):
    _touch(tmp_path / "Makefile")
    deep = tmp_path / "a" / "b"
    deep.mkdir(parents=True)
    root = pyhere.find_root(pyhere.has_file("Makefile"), start=deep)
    assert root == tmp_path.resolve()


def test_find_root_any_of_multiple(tmp_path):
    (tmp_path / ".git").mkdir()
    root = pyhere.find_root(pyhere.has_file("Makefile"), pyhere.has_dir(".git"), start=tmp_path)
    assert root == tmp_path.resolve()


def test_find_root_glob(tmp_path):
    _touch(tmp_path / "project.toml")
    root = pyhere.find_root(pyhere.has_glob("*.toml"), start=tmp_path)
    assert root == tmp_path.resolve()


def test_find_root_not_found_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        pyhere.find_root(pyhere.has_file("definitely-absent.xyz"), start=tmp_path)


def test_find_root_does_not_affect_session(tmp_path):
    _touch(tmp_path / ".here")
    pyhere.find_root(pyhere.has_file(".here"), start=tmp_path)
    # session root remains uninitialised until here() is called
    assert _core._state.root is None
