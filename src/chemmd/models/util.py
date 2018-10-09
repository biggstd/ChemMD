"""Provides utility functions for ChemMD models.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Generic Python imports.
import itertools
from typing import Any, List


def ensure_list(val_or_values: Any) -> List:
    """Examine a value and ensure that it is returned as a list.

    """
    if hasattr(val_or_values, '__iter__') and not isinstance(val_or_values, str):
        return val_or_values
    elif val_or_values is None:
        return []
    else:
        return [val_or_values]


def get_all_elements(node,
                     elemental_cls: str,
                     children=('experiments', 'samples', 'sources')) -> List:
    """

    :param node:
    :param elemental_cls:
    :param children:
    :return:
    """

    # Construct the list to be output.
    element_list = list()

    # Examine the current node for the desired elemental.
    if hasattr(node, elemental_cls):
        element_container = getattr(node, elemental_cls)
        if element_container:
            element_list.extend(getattr(node, elemental_cls))

    # Now examine the containers on the node that may contain the desired element.
    for attr in children:

        # Check if the node has a given container attribute.
        # This method allows us to access the container regardless of what type it is.
        if hasattr(node, attr):

            # Get the value of that container.
            element_containers = getattr(node, attr)

            # Since the container can empty, check it here.
            # This does not work when combined with the if statement above. Why?
            if not element_containers:
                # If this is empty simply go on to the next loop iteration.
                continue

            # Each item this container is examined recursively with this function.
            children_elements = [get_all_elements(container, elemental_cls, children=children)
                                 for container in element_containers]

            # Flatten the list returned, and extend the output list with the new values.
            element_list.extend(itertools.chain.from_iterable(children_elements))

    return element_list
