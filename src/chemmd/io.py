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
import itertools
import csv
import json
import logging
import os
import uuid
# import pprint
import re
# from textwrap import dedent
from typing import List, Tuple, Union

import pandas as pd
# import numpy as np

from . import config

# from .models import util
from .models.core import Comment, Factor, SpeciesFactor, DataFile
from .models.core import QueryGroupType
from .models.nodal import (Experiment, Node, Sample,
                           Source, NodeTypes)
from .transforms import apply_transform

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


def node_from_path(json_path: str) -> Node:
    return parse_node_json(read_idream_json(json_path))


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
    groups = x_groups + y_groups

    for node in nodes:
        for exp in node.experiments:
            mapping = exp.species_factor_mapping(node)
            group_mapping = create_group_mapping(mapping, groups)
            data, metadata = group_mapping_as_df(group_mapping)
            cds_frames.append(pd.DataFrame(data))
            metadata_dict = {**metadata_dict, **metadata}

    # Concatenate all the data frames together and reset the index.
    main_df = pd.concat(cds_frames, sort=False)
    main_df = main_df.reset_index(drop=True)

    # The main_data_frame comes with metadata - data column pairs. Split
    # these columns and return two different data frames.
    # TODO: Re-examine this code. Should I need to swap levels here?
    # Perhaps this arrangement should be set as the default.
    metadata_df = main_df.xs("metadata", axis=1)
    main_df = main_df.xs("data", axis=1)

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


def parse_sources(json_dict: dict) -> Source:
    """Parse a source dictionary and create a Source object.
    """
    source_name = json_dict.get("source_name")
    factors = build_elemental_model(json_dict, Factor, "source_factors")
    species = build_elemental_model(json_dict, SpeciesFactor, "source_species")
    comments = build_elemental_model(json_dict, Comment, "source_comments")
    return Source(name=source_name, species=species, factors=factors,
                  comments=comments)


def parse_samples(json_dict: dict) -> Sample:
    """Parse a sample dictionary and create a Sample object.
    """
    sample_name = json_dict.get("sample_name")
    factors = build_elemental_model(json_dict, Factor, "sample_factors")
    species = build_elemental_model(json_dict, SpeciesFactor, "sample_species")
    comments = build_elemental_model(json_dict, Comment, "sample_comments")
    sources = build_nodal_model(json_dict, parse_sources, "sample_sources")
    return Sample(name=sample_name, factors=factors, species=species,
                  sources=sources, comments=comments)


def parse_experiments(json_dict: dict) -> Experiment:
    """Parse an assay dictionary and create an Experiment object.
    """
    title = json_dict.get("experiment_name")
    datafile = json_dict.get("experiment_datafile")
    comments = build_elemental_model(json_dict, Comment, "experiment_comments")
    factors = build_elemental_model(json_dict, Factor, "experiment_factors")
    samples = build_nodal_model(json_dict, parse_samples, "experiment_samples")
    return Experiment(name=title, datafile=datafile,
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
    experiments = build_nodal_model(json_dict, parse_experiments, "node_experiments")

    for experiment in experiments:
        experiment.parental_factors = factors
        experiment.parental_samples = samples
        experiment.parental_info = node_information
        experiment.parental_comments = comments

    return Node(node_information=node_information, experiments=experiments,
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
#
# ----------------------------------------------------------------------------
def create_uuid(metadata_node):
    """Create a uuid to label a metadata node.

    uuid.uuid3() generates a universally unique identifier based
    on a given namespace dns and a string. This is done so that
    the same node objects return the same uuid.
    """
    return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(metadata_node)))


def create_group_mapping(mapping, groups: List):
    group_mapping = {}

    def get_matching_species(species_list, group):
        g_label, g_unit_filter, g_species_filter = group

        for s, sf in itertools.product(species_list, g_species_filter):
            if re.match(sf, s):
                yield s

    # species_tuples = list(zip(*list(mapping.keys())))[0]
    # species = list(set(itertools.chain.from_iterable(species_tuples)))

    # logger.debug(f"Mapping species: {species}")

    for group in groups:
        logger.debug(f"Examining group:\n\t{group}")
        g_label, g_unit_filter, g_species_filter = group

        # matching_species = list(get_matching_species(species, group))
        # logger.debug(f"Found matching species:\n\t{matching_species}")
        # if not matching_species:
        #     continue

        if g_unit_filter != ("Species",):
            for keys, metadata in mapping.items():

                species, factor_label = keys
                group_species_matches = list(get_matching_species(species, group))
                if group_species_matches:
                    logger.debug(f"Species ----- {group_species_matches}")

                if group_species_matches and metadata["factor"].query(g_unit_filter):
                    metadata["species_keys"] = list(group_species_matches)
                    group_mapping[group] = metadata
                    logger.debug(f"Match found: {metadata['factor'].label}")
                    # The mappings are priority-ordered, so if a match is found
                    # we must break out of the loop to prevent the desired value
                    # from being overwritten with a lower-priority one.
                    break
        else:

            species_tuples = list(zip(*list(mapping.keys())))[0]
            species = list(set(itertools.chain.from_iterable(species_tuples)))
            matching_species = list(get_matching_species(species, group))
            group_mapping[group] = {"species_data": [matching_species, ]}

    return group_mapping


def group_mapping_as_df(group_mapping):
    data_dict = {}
    metadata_dict = {}

    # grouping_dict = apply_transform(group_mapping)

    for group, grouping_dict in group_mapping.items():

        g_label, g_unit_filter, g_species_filter = group

        metadata_keys = []

        for nodal in ("experiment", "sample", "source"):
            try:
                nodal_object = grouping_dict[nodal]
                nodal_uuid = create_uuid(nodal_object)
                metadata_dict[nodal_uuid] = nodal_object
                metadata_keys.append(nodal_uuid)
            except KeyError:
                nodal_uuid = None
                metadata_keys.append(nodal_uuid)

        try:
            factor_data = grouping_dict["factor_data"]
            data_dict[("data", g_label)] = factor_data
            metadata_keys = [tuple(metadata_keys), ] * len(factor_data)
            data_dict[("metadata", g_label)] = metadata_keys

        except KeyError:
            data_dict[("data", g_label)] = grouping_dict["species_data"]
            metadata_keys = [tuple(metadata_keys), ]
            data_dict[("metadata", g_label)] = metadata_keys

    try:
        factor_size = max(len(values) for values in data_dict.values())
        for key, value in data_dict.items():
            if len(value) == 1:
                data_dict[key] = value * factor_size
    except ValueError:
        pass

    logger.debug(data_dict)
    df = pd.DataFrame(data_dict)
    # logger.debug(f"Columns: {df.columns}, shape: {df.shape}")
    return df, metadata_dict
