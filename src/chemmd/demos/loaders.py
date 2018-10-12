"""Demo `chemmd.core.Node` objects for testing.

"""
import os

from ..io import node_from_path
from ..models import QueryGroup


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
              QueryGroup('Counter Ion', ('Species',), ("Na+", "Li+", "Cs+", "K+",)),
              QueryGroup('Base Concentration', ('Molar',), ("OH-",))),
    y_groups=(QueryGroup('27 Al ppm', ('ppm',), ("Al",)),)
)


def json_demo_path(file):
    # Get the directory of this Python file.
    demos_dir = os.path.dirname(__file__)
    # Create the paths to the data folder.
    data_dir = os.path.join(demos_dir, "demo_json", file)
    # Return the absolute path of that directory.
    return os.path.abspath(data_dir)


def node_demo_by_key(key):
    path = json_demo_path(JSON_DEMOS[key])
    return node_from_path(path)


def load_demo_nodes():
    return {key: node_demo_by_key(key)
            for key in JSON_DEMOS.keys()}

