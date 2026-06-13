"""pyhere -- A simpler way to find your files.

A Python port of the R `here` package. Construct paths relative to your
project's root, no matter the current working directory.

    >>> from pyhere import here, i_am
    >>> i_am("analysis/report.py")        # declare where this script lives
    >>> here("data", "penguins.csv")      # -> <project root>/data/penguins.csv
"""

from ._core import dr_here, here, i_am, set_here

__all__ = ["here", "i_am", "set_here", "dr_here"]
__version__ = "0.1.0"
