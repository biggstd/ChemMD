"""Provides demo `chemmd` objects for testing.

"""
# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
import os
from typing import Dict

# ----------------------------------------------------------------------------
# Local package imports.
# ----------------------------------------------------------------------------
from ..models import Node, QueryGroup
from ..io import node_from_path

# ----------------------------------------------------------------------------
# Constant definitions.
# ----------------------------------------------------------------------------
JSON_DEMOS = {
    "SIPOS_NMR": "sipos_2006_nmr_1.json",
    "SIPOS_NMR_2": "sipos_2006_nmr_2.json",
    "ERNESTO_NMR_1": "ernesto_nmr_1.json"
}
demo_keys = tuple(JSON_DEMOS.keys())

NMR_GROUPS = dict(
    x_groups=(QueryGroup('Total Aluminate Concentration', ('Molar',), ("Al",)),
              QueryGroup('Counter Ion Concentration', ('Molar',),
                         ("Na+", "Li+", "Cs+", "K+")),
              QueryGroup('Counter Ion', ('Species',),
                         ("Na+", "Li+", "Cs+", "K+",)),
              QueryGroup('Base Concentration', ('Molar',), ("OH-",))),
    y_groups=(QueryGroup('27 Al ppm', ('ppm',), ("Al",)),)
)


# ----------------------------------------------------------------------------
# Demo loading functions.
# ----------------------------------------------------------------------------
def json_demo_path(file: str) -> str:
    """Loads the absolute directory path to the given .json demo `file`.

    :param file: The name of a .json demo file.
    :returns: The absolute path of the given .json demo file name.

    """
    # Get the directory of this Python file.
    demos_dir = os.path.dirname(__file__)
    # Create the paths to the data folder.
    data_dir = os.path.join(demos_dir, "demo_json", file)
    # Return the absolute path of that directory.
    return os.path.abspath(data_dir)


def node_demo_by_key(key: str) -> Node:
    """Loads a demo `chemmd.models.node` object based on a given key.

    :param key: The key, see `demo_keys`.
    :returns: A `chemmd.models.node` object.

    """

    path = json_demo_path(JSON_DEMOS[key])
    return node_from_path(path)


def load_demo_nodes() -> Dict[str, Node]:
    """Load all demo nodes.

    :returns: A list of all demo nodes.
    """
    return {key: node_demo_by_key(key)
            for key in JSON_DEMOS.keys()}
