"""CLI entry point.

The GUI is not implemented yet (v0.1.0 ticket 07). Until the mechanism spike (ticket 01)
settles how `split-pane -s` and `move-focus` actually behave, there is nothing to render.
"""

from __future__ import annotations

import argparse
import sys

from magiterm import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="magiterm",
        description="MagiTerminalManager - generate Windows Terminal workspace artifacts.",
    )
    parser.add_argument("--version", action="version", version=f"magiterm {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    print(
        f"magiterm {__version__}: the GUI is not implemented yet.\n"
        "Current work is the mechanism spike (v0.1.0 ticket 01).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
