"""Provides utility functions for ChemMD models.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# Generic Python imports.
import csv
import itertools
import os
import uuid
import collections
from typing import Any, List

from .. import config


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


def create_uuid(metadata_node):
    """Create a uuid to label a metadata node.

    uuid.uuid3() generates a universally unique identifier based
    on a given namespace dns and a string. This is done so that
    the same node objects return the same uuid.
    """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(metadata_node)))


def load_csv_as_dict(path: str, base_path: str = config["BASE_PATH"]
                     ) -> dict:
    """Load a CSV file as a Python dictionary.

    The header in each file will be skipped.

    :param path: The path to the .csv in question.
    :param base_path: The path to prepend to the path given above.
    :return: A dictionary object with integer keys representing the csv
        column index the data was found in.

    """
    csv_path = os.path.join(base_path, path)
    data = collections.defaultdict(list)

    # Open the file and create a reader (an object that when iterated
    # on gives the values of each row.
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)

        # Pop the header and get its length.
        field_int_index = range(len(next(reader)))
        field_int_index = [str(x) for x in field_int_index]

        # Iterate over the remaining rows and append the data.
        for row in reader:
            for idx, header in zip(field_int_index, reader.fieldnames):
                data[idx].append(float(row[header]))

    return dict(data)