"""Command-line interface for py_here.

Examples
--------
Print the project root::

    $ py-here
    /home/me/myproject

Build a project-relative path (handy in shell scripts)::

    $ cat "$(py-here data penguins.csv)"

Show the situation report explaining where the root is and why::

    $ py-here --report
"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from ._core import dr_here, here


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="py-here",
        description="Print paths relative to your project root.",
    )
    parser.add_argument(
        "components",
        nargs="*",
        help="Path components below the project root. With none, prints the root.",
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Print a situation report explaining the chosen root, then exit.",
    )
    parser.add_argument(
        "-q",
        "--quiet-report",
        action="store_true",
        help="With --report, omit the reason details (one line only).",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    # Top-level guard: a CLI should print a clean one-line error and exit 1
    # (e.g. a misconfigured PYHERE_ROOT), not dump a traceback -- important for
    # shell capture like `ROOT="$(py-here)"`.
    try:
        if args.report:
            dr_here(show_reason=not args.quiet_report)
        else:
            print(here(*args.components))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
