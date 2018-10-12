"""Shared test fixtures.

"""

# ----------------------------------------------------------------------------
# General Imports
# ----------------------------------------------------------------------------
import chemmd.io.input
import pytest

# ----------------------------------------------------------------------------
# Imports for Testing
# ----------------------------------------------------------------------------
from chemmd.demos import loaders

from chemmd.models.core import Factor, SpeciesFactor, Comment, QueryGroup
from chemmd.models.nodal import Source, Sample, Experiment, Node


# ----------------- -----------------------------------------------------------
# Globals and constants
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Key-value Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture
def factor_kwargs():
    return [
        {
            "factor_type": "Measurement Condition",
            "decimal_value": 18.0,
            "unit_reference": "Molar"
        },
        {
            "factor_type": "Measurement Condition",
            "unit_reference": "Molar",
            "csv_column_index": 0
        },
        {
            "factor_type": "Measurement Condition",
            "unit_reference": "Integrated Intensity",
            "csv_column_index": 1
        },
        {
            "factor_type": "Measurement Condition",
            "unit_reference": "cm-1",
            "csv_column_index": 2
        }
    ]


@pytest.fixture
def species_factor_kwargs():
    return [
        {
            "species_reference": "Na+",
            "stoichiometry": 1.0
        },
        {
            "species_reference": "OH-",
            "stoichiometry": 1.0
        }
    ]


@pytest.fixture
def comment_kwargs():
    return [
        {
            "comment_title": "Test comment number 1.",
            "comment_body": "Test comment 1 body."
        }
    ]


# ----------------------------------------------------------------------------
# Elemental Model Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture
def factor_fixtures(factor_kwargs):
    return [Factor(**kwargs) for kwargs in factor_kwargs]


@pytest.fixture
def species_factor_fixtures(species_factor_kwargs):
    return [SpeciesFactor(**kwargs) for kwargs in species_factor_kwargs]


@pytest.fixture
def comment_factor_fixtures(comment_kwargs):
    return [Comment(**kwargs) for kwargs in comment_kwargs]


# ----------------------------------------------------------------------------
# Nodal Model Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture
def source_node_fixtures(factor_fixtures, species_factor_fixtures,
                         comment_factor_fixtures):
    return [Source(**dict(source_name="Test Source",
                          species=species_factor_fixtures,
                          factors=factor_fixtures,
                          comments=comment_factor_fixtures))]


@pytest.fixture
def sample_node_fixtures(factor_fixtures, species_factor_fixtures,
                         comment_factor_fixtures, source_node_fixtures):
    return [Sample(**dict(name="Test Sample",
                          species=species_factor_fixtures,
                          factors=factor_fixtures,
                          sources=source_node_fixtures,
                          comments=comment_factor_fixtures))]


@pytest.fixture
def experiment_node_fixtures(factor_fixtures, sample_node_fixtures,
                             comment_factor_fixtures):
    return [Experiment(**dict(datafile="some_datafile.csv",
                              name="Some assay title.",
                              factors=factor_fixtures,
                              samples=sample_node_fixtures,
                              comments=comment_factor_fixtures))]


@pytest.fixture
def drupal_node_fixture_a(experiment_node_fixtures, factor_fixtures,
                          sample_node_fixtures, comment_factor_fixtures):
    return Node(**dict(name="Drupal Node A",
                       experiments=experiment_node_fixtures,
                       factors=factor_fixtures,
                       samples=sample_node_fixtures,
                       comments=comment_factor_fixtures))


@pytest.fixture
def sipos_drupal_node():
    return loaders.node_demo_by_key("SIPOS_NMR")


# ----------------------------------------------------------------------------
# JSON Data Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture
def sipos_nmr_json():
    path = loaders.json_demo_path(loaders.JSON_DEMOS["SIPOS_NMR"])
    return chemmd.io.input.read_idream_json(path)


@pytest.fixture
def sipos_nmr2_json():
    path = loaders.json_demo_path(loaders.JSON_DEMOS["SIPOS_NMR_2"])
    return chemmd.io.input.read_idream_json(path)


@pytest.fixture
def ernesto_nmr():
    path = loaders.json_demo_path(loaders.JSON_DEMOS["ERNESTO_NMR_1"])
    return chemmd.io.input.read_idream_json(path)


# ----------------------------------------------------------------------------
# QueryGroup Fixtures
# ----------------------------------------------------------------------------

@pytest.fixture
def nmr_groups():
    x_groups = (('Total Aluminate Concentration', ('Molar', ), ("Al",)),
                ('Counter Ion Concentration', ('Molar', ), ("Na+", "Li+", "Cs+", "K+")),
                ('Counter Ion', ('Species',), ("Na+", "Li+", "Cs+", "K+",)),
                ('Base Concentration', ('Molar', ), ("OH-",)))

    x_query_groups = [QueryGroup(
        **{"column_name": cn, "factor_filters": ff, "species_filters": sf}
    ) for cn, ff, sf in x_groups]

    y_groups = (('27 Al ppm', 'ppm', ("Al",)),)

    y_query_groups = [QueryGroup(
        **{"column_name": cn, "factor_filters": ff, "species_filters": sf}
    ) for cn, ff, sf in y_groups]

    return x_query_groups, y_query_groups


@pytest.fixture
def raman_groups():
    x_groups = (('Total Aluminate Concentration', ('Molar',), ("Al",)),
                ('Counter Ion Concentration', ('Molar', ), ("Na+", "Li+", "Cs+", "K+")),
                ('Counter Ion', ('Species',), ("Na+", "Li+", "Cs+", "K+",)),
                ('Base Concentration', ('Molar', ), ("OH-",)))
    y_groups = (('Integrated Raman Intensity', ('Integrated Intensity', ), ("Al",)),)
    return x_groups, y_groups
