"""Tests for the pyhere command-line interface."""

import pytest

from pyhere import __main__ as cli
from pyhere import _core


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


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "pyhere" in out
