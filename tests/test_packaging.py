"""Checks that hold from day one, before any feature exists.

The runtime-dependency test is not busywork: zero third-party runtime dependencies is a
stated design goal, and the cheapest way to keep it true is to fail a test the moment
someone adds one.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from magiterm import __version__
from magiterm.__main__ import build_parser, main

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def load_pyproject() -> dict[str, object]:
    with PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)


def test_runtime_dependencies_stay_empty() -> None:
    project = load_pyproject()["project"]
    assert isinstance(project, dict)
    assert project["dependencies"] == [], (
        "MagiTerminalManager must keep zero third-party runtime dependencies "
        "(see 'Zero runtime dependencies is a design goal' in README.md). "
        "If that has to change, change the decision first, then this test."
    )


def test_version_matches_pyproject() -> None:
    project = load_pyproject()["project"]
    assert isinstance(project, dict)
    assert project["version"] == __version__


def test_tkinter_is_importable() -> None:
    """The GUI is stdlib tkinter; a Python build without Tk would be unusable here."""
    pytest.importorskip("tkinter")


def test_version_flag_exits_zero() -> None:
    with pytest.raises(SystemExit) as excinfo:
        build_parser().parse_args(["--version"])
    assert excinfo.value.code == 0


def test_main_reports_not_implemented() -> None:
    assert main([]) == 1
