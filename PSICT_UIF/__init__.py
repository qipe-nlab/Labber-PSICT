## This file provides the initialisation for the PSICT-UIF module
##  by Sam Wolski

from sys import version_info

## verify python version
if version_info >= (3,6):
    ## version info
    from ._include36._version import version as __version__
    ## classes (only top-level required)
    from ._include36.psictUIFInterface import psictUIFInterface


## PSICT_UIF does not currently support Python <= 3.5, or Python 2
else:
    raise ImportError("PSICT-UIF requires Python 3.6 or later; current version is {}.{}.{}".format(version_info[0], version_info[1], version_info[2]))
