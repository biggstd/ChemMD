"""Tests

"""

# ----------------------------------------------------------------------------
# Imports for Testing
# ----------------------------------------------------------------------------

from chemmd.models.core import Factor, SpeciesFactor, Comment
from chemmd.models.nodal import DrupalNode, SampleNode, SourceNode, AssayNode


# ----------------------------------------------------------------------------
# Test core model initialization.
# ----------------------------------------------------------------------------

def test_factor_creation(factor_kwargs):
    for kwargs in factor_kwargs:
        factor = Factor(**kwargs)
        assert factor.factor_type == kwargs["factor_type"]
        assert factor.label == (kwargs["factor_type"],
                                kwargs.get("reference_value", ""),
                                kwargs.get("unit_reference"))


def test_species_factor_creation(species_factor_kwargs):
    for kwargs in species_factor_kwargs:
        species_factor = SpeciesFactor(**kwargs)
        assert species_factor.species_reference == kwargs["species_reference"]
        assert species_factor.stoichiometry == kwargs["stoichiometry"]


def test_comment_creation(comment_kwargs):
    for kwargs in comment_kwargs:
        comment = Comment(**kwargs)
        assert comment.name == kwargs["name"]
        assert comment.body == kwargs["body"]


# ----------------------------------------------------------------------------
# Test nodal model initialization.
# ----------------------------------------------------------------------------


def test_source_node_creation(source_node_fixtures):
    for source_node in source_node_fixtures:
        assert isinstance(source_node, SourceNode)


def test_sample_node_creation(sample_node_fixtures):
    for sample_node in sample_node_fixtures:
        assert isinstance(sample_node, SampleNode)


def test_assay_node_creation(assay_node_fixtures):
    for assay_node in assay_node_fixtures:
        assert isinstance(assay_node, AssayNode)


def test_drupal_node_creation(drupal_node_fixture_a):
    assert isinstance(drupal_node_fixture_a, DrupalNode)
