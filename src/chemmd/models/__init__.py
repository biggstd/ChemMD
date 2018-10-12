"""

"""

# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
from typing import Union, Tuple, Callable, NamedTuple


# ----------------------------------------------------------------------------
# Local package imports.
# ----------------------------------------------------------------------------
from .nodal import Node, Experiment, Sample, Source
from .core import Factor, SpeciesFactor, Comment, QueryGroup, DerivedGroup


# ----------------------------------------------------------------------------
# Define Type Hints.
# ----------------------------------------------------------------------------
# Define Nodal Types.
NodeTypes = Union[Node, Sample, Experiment, Source]

# Define Elemental Types.
ElementalTypes = Union[Factor, SpeciesFactor, Comment]

GroupTypes = Union[QueryGroup, DerivedGroup]
