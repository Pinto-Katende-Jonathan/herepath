"""Tests for the py_here command-line interface."""

import pytest

from py_here import __main__ as cli
from py_here import _core


@pytest.fixture(autouse=True)
def reset_state(monkeypatch, tmp_path):
    monkeypatch.delenv(_core.ENV_VAR, raising=False)
    monkeypatch.chdir(tmp_path)
    _core.reset_criteria()
    yield


def test_cli_prints_root(tmp_path, capsys):
    (tmp_path / ".here").write_text("", encoding="utf-8")
    rc = cli.main([])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == str(tmp_path.resolve())


def test_cli_builds_path(tmp_path, capsys):
    (tmp_path / ".here").write_text("", encoding="utf-8")
    rc = cli.main(["data", "penguins.csv"])
    assert rc == 0
    out = capsys.readouterr().out.strip()
    assert out == str((tmp_path / "data" / "penguins.csv").resolve())


def test_cli_report(tmp_path, capsys):
    (tmp_path / ".here").write_text("", encoding="utf-8")
    rc = cli.main(["--report"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "here() starts at" in out
    assert "Current working directory" in out


def test_cli_report_quiet(tmp_path, capsys):
    (tmp_path / ".here").write_text("", encoding="utf-8")
    rc = cli.main(["--report", "--quiet-report"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "here() starts at" in out
    assert "Current working directory" not in out


def test_cli_reports_error_cleanly(tmp_path, capsys, monkeypatch):
    # A misconfigured PYHERE_ROOT must yield a clean error + exit 1, not a
    # traceback (so `ROOT="$(py-here)"` fails predictably).
    monkeypatch.setenv(_core.ENV_VAR, str(tmp_path / "missing"))
    rc = cli.main([])
    assert rc == 1
    captured = capsys.readouterr()
    assert captured.out == ""  # nothing on stdout to capture
    assert "Error:" in captured.err


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "py-here" in out
