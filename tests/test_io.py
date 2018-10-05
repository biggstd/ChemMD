"""Test the input / output (io) module.

"""

# ----------------------------------------------------------------------------
# Imports for Testing
# ----------------------------------------------------------------------------
from chemmd import io
from chemmd.models.nodal import Node


# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
def test_node_creation(sipos_drupal_node):
    assert isinstance(sipos_drupal_node, Node)


def test_node_subgraph(sipos_drupal_node):
    sub_nodes = io.prepare_sub_graphs(sipos_drupal_node)
    print(sub_nodes)
