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

# Define Query Groups Types
# These are implemented as generics so that these classes need not be
# created.

# QueryGroupType = Tuple[str, Tuple[str, ...], Tuple[str, ...]]
# DerivedGroupType = Tuple[str, Tuple[str, ...], Callable]
# GroupTypes = Union[QueryGroupType, DerivedGroupType]
