"""Test the input / output (io) module.

"""

# ----------------------------------------------------------------------------
# Imports for Testing
# ----------------------------------------------------------------------------
import logging

from chemmd import io
from chemmd.models.nodal import Node

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
def test_node_creation(sipos_drupal_node):
    assert isinstance(sipos_drupal_node, Node)


def test_export_by_groups(sipos_drupal_node, nmr_groups):
    x_groups, y_groups = nmr_groups
    groups = x_groups + y_groups

    for exp in sipos_drupal_node.experiments:
        mapping = exp.species_factor_mapping(sipos_drupal_node)
        # print(mapping)
        group_mapping = io.create_group_mapping(mapping, groups)
        df, metadata = io.group_mapping_as_df(group_mapping)
        # logger.debug(df.columns)
        # logger.debug(metadata.keys())