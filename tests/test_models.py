"""Tests

"""

# ----------------------------------------------------------------------------
# Imports for Testing
# ----------------------------------------------------------------------------
import logging

from chemmd.models.core import Factor, SpeciesFactor, Comment
from chemmd.models.nodal import Node, Sample, Source, Experiment

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------
# Test core model initialization.
# ----------------------------------------------------------------------------

def test_factor_creation(factor_kwargs):
    for kwargs in factor_kwargs:
        factor = Factor(**kwargs)
        assert factor.factor_type == kwargs["factor_type"]
        assert factor.label == (kwargs["factor_type"],
                                kwargs.get("unit_reference"))


def test_species_factor_creation(species_factor_kwargs):
    for kwargs in species_factor_kwargs:
        species_factor = SpeciesFactor(**kwargs)
        assert species_factor.species_reference == kwargs["species_reference"]
        assert species_factor.stoichiometry == kwargs["stoichiometry"]


def test_comment_creation(comment_kwargs):
    for kwargs in comment_kwargs:
        comment = Comment(**kwargs)
        assert comment.comment_title == kwargs["comment_title"]
        assert comment.comment_body == kwargs["comment_body"]


# ----------------------------------------------------------------------------
# Test nodal model initialization.
# ----------------------------------------------------------------------------
def test_source_node_creation(source_node_fixtures):
    for source_node in source_node_fixtures:
        assert isinstance(source_node, Source)


def test_sample_node_creation(sample_node_fixtures):
    for sample_node in sample_node_fixtures:
        assert isinstance(sample_node, Sample)


def test_assay_node_creation(experiment_node_fixtures):
    for experiment in experiment_node_fixtures:
        assert isinstance(experiment, Experiment)


def test_drupal_node_creation(drupal_node_fixture_a):
    assert isinstance(drupal_node_fixture_a, Node)


# ----------------------------------------------------------------------------
# Test Experiment functions.
# ----------------------------------------------------------------------------
def test_build_factor_map(sipos_drupal_node):
    experiments = sipos_drupal_node.experiments
    for exp in experiments:
        mapping = exp.species_factor_mapping(sipos_drupal_node)
        if not mapping:
            logger.debug(f"Failed to generated mapping for: {exp}")
