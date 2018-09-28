"""Input and Output Operations

This module provides functions for transforming to and from ChemMD models.

ChemMD ``models`` can be created from:

+ .json source files

ChemMD ``models`` can be output to data frame, metadata dictionary pairs
with the use of ``query groups``.


"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import collections
import csv
# import itertools
import json
import logging
import os
import uuid
from typing import List, Tuple, Union

import pandas as pd
import numpy as np

from . import config

# from .models import util
from .models.core import Comment, Factor, SpeciesFactor, DataFile
from .models.core import QueryGroupType
from .models.nodal import (AssayNode, Node, SampleNode,
                           SourceNode, NodeTypes)
from .display.transforms import TRANSFORMS

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Top level API functions.
# ----------------------------------------------------------------------------
ElementalTypes = Union[Factor, SpeciesFactor, Comment, DataFile]


def create_nodes_from_files(json_files: List[str]) -> List[Node]:
    """Create multiple Node models from a list of json files.

    :param json_files: A list of json file paths as strings.
    :returns: A list of Node objects.

    """

    return [parse_node_json(read_idream_json(json_file))
            for json_file in json_files]


def prepare_nodes_for_bokeh(x_groups: QueryGroupType,
                            y_groups: QueryGroupType,
                            nodes: List[Node]
                            ) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Prepare a main pd.DataFrame and a metadata ChainMap from a
    list of `Node`s.

    :param x_groups: A user-given grouping query for X-axis values.
    :param y_groups: A user-given grouping query for Y-axis values.
    :param nodes: A list of Node objects to apply the
        group queries to.

    :returns: A populated pd.DataFrame and a ChainMap with all the
        data and metadata requested by the given  groups from the
        given nodes.

    """
    cds_frames = []
    metadata_dict = {}

    for node in nodes:
        data, metadata = collate_node(node, x_groups + y_groups)
        cds_frames.append(pd.DataFrame(data))
        metadata_dict = {**metadata_dict, **metadata}

    # Concatenate all the data frames together and reset the index.
    main_df = pd.concat(cds_frames, sort=False)
    main_df = main_df.reset_index(drop=True)

    # The main_data_frame comes with metadata - data column pairs. Split
    # these columns and return two different data frames.
    # TODO: Re-examine this code. Should I need to swap levels here?
    # Perhaps this arrangement should be set as the default.
    main_df = main_df.swaplevel(0, 1, axis=1).xs("data", axis=1)
    metadata_df = main_df.swaplevel(0, 1, axis=1).xs("metadata", axis=1)

    return main_df, metadata_df, metadata_dict


# ----------------------------------------------------------------------------
# JSON Input Functions.
#
# These should never need be used directly. Consider appending "__" to the
# front of these function names.
# ----------------------------------------------------------------------------

def read_idream_json(json_path: str) -> dict:
    """Read a json from a path and return as a python dictionary.

    """

    with open(json_path) as json_file:
        data = json.load(json_file)
    return data


def build_elemental_model(json_dict: dict, model: ElementalTypes,
                          key: str) -> List[ElementalTypes]:
    """Construct an 'elemental' metadata object.

    """
    # Many entries are optional, ensure the entry exists.
    if json_dict.get(key):
        model_list = json_dict.get(key)
        return [model(**kwargs) for kwargs in model_list]
    return []


def build_nodal_model(json_dict: dict, model: NodeTypes,
                      key: str) -> List[NodeTypes]:
    """Construct a 'nodal' metadata object.
    """
    # Many entries are optional, ensure the entry exists.
    if json_dict.get(key):
        model_list = json_dict.get(key)
        return [model(item) for item in model_list]
    return []


def parse_sources(json_dict: dict) -> SourceNode:
    """Parse a source dictionary and create a SourceNode object.
    """
    source_name = json_dict.get("source_name")
    factors = build_elemental_model(json_dict, Factor, "source_factors")
    species = build_elemental_model(json_dict, SpeciesFactor, "source_species")
    comments = build_elemental_model(json_dict, Comment, "source_comments")
    return SourceNode(source_name=source_name, species=species, factors=factors,
                      comments=comments)


def parse_samples(json_dict: dict) -> SampleNode:
    """Parse a sample dictionary and create a SampleNode object.
    """
    sample_name = json_dict.get("sample_name")
    factors = build_elemental_model(json_dict, Factor, "sample_factors")
    species = build_elemental_model(json_dict, SpeciesFactor, "sample_species")
    comments = build_elemental_model(json_dict, Comment, "sample_comments")
    sources = build_nodal_model(json_dict, parse_sources, "sample_sources")
    return SampleNode(sample_name=sample_name, factors=factors, species=species,
                      sources=sources, comments=comments)


def parse_assays(json_dict: dict) -> AssayNode:
    """Parse an assay dictionary and create an AssayNode object.
    """
    assay_title = json_dict.get("assay_title")
    assay_datafile = json_dict.get("assay_datafile")
    comments = build_elemental_model(json_dict, Comment, "assay_comments")
    factors = build_elemental_model(json_dict, Factor, "assay_factors")
    samples = build_nodal_model(json_dict, parse_samples, "assay_samples")
    return AssayNode(assay_title=assay_title, assay_datafile=assay_datafile,
                     comments=comments, factors=factors, samples=samples)


def parse_node_json(json_dict: dict) -> Node:
    """Convert a dictionary to a Node object.
    """
    # Info, factors and comments can be directly created from the json.
    node_information = json_dict.get("node_information")
    factors = build_elemental_model(json_dict, Factor, "node_factors")
    comments = build_elemental_model(json_dict, Comment, "node_comments")
    # Samples and assays have nested items, and require more processing.
    samples = build_nodal_model(json_dict, parse_samples, "node_samples")
    assays = build_nodal_model(json_dict, parse_assays, "node_assays")

    for assay in assays:
        assay.parental_factors = factors
        assay.parental_samples = samples
        assay.parental_info = node_information
        assay.parental_comments = comments

    return Node(node_information=node_information, assays=assays,
                factors=factors, samples=samples, comments=comments)


# ----------------------------------------------------------------------------
# CSV Data Input.
# ----------------------------------------------------------------------------


def load_csv_as_dict(path: str, base_path: str = config["BASE_PATH"]
                     ) -> dict:
    """Load a CSV file as a Python dictionary.

    The header in each file will be skipped.

    :param path:
    :param base_path:
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


# ----------------------------------------------------------------------------
# Model to Pandas DataFrame Functions
# ----------------------------------------------------------------------------


def filter_matching_factors(factors: List[Factor],
                            group: QueryGroupType
                            ) -> List[Factor]:
    """Filter given list of factors and return only those which match
    the given query group.
    """
    __g_label, g_unit_filter, __g_species_filter = group
    return [factor for factor in factors
            if factor.query(g_unit_filter)
            or g_unit_filter == ("Species",)]


def filter_matching_samples(samples: List[SampleNode],
                            group: QueryGroupType) -> List[SampleNode]:
    """Filter given list of samples and return only those which match
    the given query group.
    """
    __g_label, __g_unit_filter, g_species_filter = group
    return [sample for sample in samples
            if sample.query(g_species_filter)]


def collate_group_matches(node_samples: List[SampleNode],
                          node_factors: List[Factor],
                          group: QueryGroupType
                          ) -> Tuple[Factor, SampleNode]:
    """Iterate over the samples and factors provided, and
    return (Factor, Sample) tuple pairs of those which match
    the given group.
    """
    # Find matching factors and samples of the top-level node.
    matching_samples = filter_matching_samples(node_samples, group)
    matching_factors = filter_matching_factors(node_factors, group)

    # Samples are the next highest level node.
    for m_sample in matching_samples:

        # Get those factors specific to this sample.
        m_sample_factors = filter_matching_factors(m_sample.factors, group)
        # The factors which apply to this sample node are all of the
        # parental factors, combined with its private factors.
        m_factors = matching_factors + m_sample_factors

        # Provide the requested data.
        for factor in m_factors:
            yield factor, m_sample


def parse_species_factor_match(sample: SampleNode,
                               group: QueryGroupType,
                               experiment: Node
                               ) -> List[str]:
    """Parse a matching SpeciesFactor. 

    Return a list of the string representation of the matching 
    species. The length of the list is determined by the length of
    the csv data associated with the species factor.
    """
    # Unpack the group, load the csv data and determine its length.
    __g_label, __g_unit_filter, g_species_filter = group
    data_dict = load_csv_as_dict(experiment.assay_datafile)
    factor_size = max(len(values) for values in data_dict.values())

    # Find the actual matching species in this sample set, as a sample
    # can have more than one species and not all of them must be matches.
    matching_species = [species
                        for species in sample.all_species
                        if species.species_reference in g_species_filter]

    # Return the first of these species found.
    # TODO: Consider what should be done with multiple matches?
    return [matching_species[0].species_reference] * factor_size


def parse_group_match(factor: Factor,
                      sample: SampleNode,
                      group: QueryGroupType,
                      experiment: Node
                      ) -> List:
    """Pares a matching group. Handles normal and csv index factors.
    """
    # Unpack the group object.
    __g_label, g_unit_filter, g_species_filter = group

    # Get the size of this retrieved data array.
    data_dict = load_csv_as_dict(experiment.assay_datafile)
    factor_size = max(len(values) for values in data_dict.values())

    # Find the matching species.
    matching_species = [species
                        for species in sample.all_species
                        if species.species_reference in g_species_filter]

    if factor.is_csv_index:
        data = np.array(data_dict[str(factor.csv_column_index)])
        # TODO: Consider the location of this call to transforms.
        # Apply transforms.
        for key, func in TRANSFORMS.items():
            if any(unit in key for unit in g_unit_filter) and matching_species:
                logger.info(f"Transform {func} called for {key}.")
                data = func(data, matching_species[0])
        return data
    else:
        return [factor.value] * factor_size


def create_uuid(metadata_node):
    """Create a uuid to label a metadata node.

    uuid.uuid3() generates a universally unique identifier based
    on a given namespace dns and a string. This is done so that
    the same node objects return the same uuid.
    """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(metadata_node)))


def collate_node(drupal_node: Node,
                 groups: QueryGroupType
                 ) -> Tuple[pd.DataFrame, dict]:
    """Collate the matching data and metadata from a given drupal node
    by the given groups.

    TODO: Convert to a graph-based solution. Use either ChainMap or NetworkX.
    """
    # Create the uuid for the Node, and add it to the metadata dictionary.
    drupal_node_uuid = create_uuid(drupal_node)
    metadata = {drupal_node_uuid: drupal_node}

    node_frames = []  # Holds all the created dataframes.

    for group in groups:

        # Unpack the group object.
        g_label, g_unit_filter, __g_species_filter = group
        group_matches = []  # Holds all the dataframes for this group.

        for experiment in drupal_node.assays:

            # Create the uuid for the experiment object,
            # and add it to the metadata dictionary.
            experiment_node_uuid = create_uuid(experiment)
            metadata[experiment_node_uuid] = experiment

            # Find the matching sample and factors of this experiment.
            # This includes all those samples and factors from the parent node.
            matches = collate_group_matches(
                experiment.samples + drupal_node.samples,
                experiment.factors + drupal_node.factors,
                group)

            # Examine each unique sample match for a species factor column.
            # The `matches` variable cannot be used again as it is a generator.
            factors, samples = zip(*matches)

            # Check for the special case of a species column.
            if g_unit_filter == ("Species",):

                # Samples are duplicated as they are paired with factors.
                # Ensure each sample is considered once by creating a set.
                for sample in set(samples):

                    # Create the species data for this sample.
                    species_data = parse_species_factor_match(
                        sample, group, experiment)

                    # Create the uuid for the sample object, and add
                    # it to the metadata dictionary.
                    sample_node_uuid = create_uuid(sample)
                    metadata[sample_node_uuid] = sample

                    # The three metadata keys are stored in a tuple and
                    # converted to a list with the same length of the csv data.
                    metadata_keys = [(drupal_node_uuid, experiment_node_uuid,
                                      sample_node_uuid)] * len(species_data)

                    # Create the data frame from an intermediary dictionary
                    # and append it to the group matches list.
                    species_data_dict = {(g_label, "data"):     species_data,
                                         (g_label, "metadata"): metadata_keys}
                    df = pd.DataFrame(species_data_dict)
                    group_matches.append(df)

            # To ensure that we skip any groups that where handled above.
            # if g_unit_filter != ("Species",):
            else:

                # Iterate through the sample factor pairs.
                for factor, sample in zip(factors, samples):

                    # Create the sample node uuid and add it to
                    # the metadata dictionary.
                    sample_node_uuid = create_uuid(sample)
                    metadata[sample_node_uuid] = sample

                    # Get the data array for this match.
                    matching_data = parse_group_match(
                        factor, sample, group, experiment)

                    # Create the metadata key tuple with the same length
                    # as the data.
                    metadata_keys = [(drupal_node_uuid,
                                      experiment_node_uuid,
                                      sample_node_uuid)] * len(matching_data)

                    # Convert the data to a pandas dataframe.
                    df = pd.DataFrame({(g_label, "data"):     matching_data,
                                       (g_label, "metadata"): metadata_keys})
                    group_matches.append(df)

        # Stack the created dataframes along the index axis, each matching
        # group is returned in a pair of data, metadata columns.
        group_df = pd.concat(group_matches, sort=False).reset_index(drop=True)
        node_frames.append(group_df)

    # Concatenate the group columns along the column axis.
    main_df = pd.concat(node_frames, axis=1, sort=False)

    return main_df, metadata
