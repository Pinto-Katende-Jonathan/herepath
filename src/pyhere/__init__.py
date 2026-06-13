"""pyhere -- A simpler way to find your files.

A Python port of the R `here` package. Construct paths relative to your
project's root, no matter the current working directory.

    >>> from pyhere import here, i_am
    >>> i_am("analysis/report.py")        # declare where this script lives
    >>> here("data", "penguins.csv")      # -> <project root>/data/penguins.csv
"""

from ._core import (
    Criterion,
    dr_here,
    find_root,
    has_dir,
    has_file,
    has_glob,
    here,
    i_am,
    reset,
    set_here,
)

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
]
__version__ = "0.1.0"
