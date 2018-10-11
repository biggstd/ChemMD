# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import csv
import json

import logging
import os
import collections
from typing import List

from .. import config
from ..models.core import Factor, SpeciesFactor, Comment, ElementalTypes
from ..models.nodal import NodeTypes, Source, Sample, Experiment, Node

logger = logging.getLogger(__name__)


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


def create_nodes_from_files(json_files: List[str]) -> List[Node]:
    """Create multiple Node models from a list of json files.

    :param json_files: A list of json file paths as strings.
    :returns: A list of Node objects.

    """

    return [parse_node_json(read_idream_json(json_file))
            for json_file in json_files]


def node_from_path(json_path: str) -> Node:
    return parse_node_json(read_idream_json(json_path))