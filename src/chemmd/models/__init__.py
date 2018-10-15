"""

#############
ChemMD Models
#############

**Overview**

These models are combined to create a nested metadata structure. The top-most
level being the ``Node``, which contains the contents of one Drupal content
node.


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
