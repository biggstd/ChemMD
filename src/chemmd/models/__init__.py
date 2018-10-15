"""

"""

# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
from typing import Union


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

# Define Group Types.
GroupTypes = Union[QueryGroup, DerivedGroup]
