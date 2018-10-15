# ----------------------------------------------------------------------------
# Imports -- Standard Python Library
# ----------------------------------------------------------------------------
import itertools
import logging
import re
from typing import List, Tuple, Dict

# ----------------------------------------------------------------------------
# Imports -- Data science imports.
# ----------------------------------------------------------------------------
import pandas as pd

# ----------------------------------------------------------------------------
# Local package imports.
# ----------------------------------------------------------------------------
from ..models import Node, QueryGroup
from ..models.util import create_uuid

logger = logging.getLogger(__name__)


def prepare_nodes_for_bokeh(x_groups: List[QueryGroup],
                            y_groups: List[QueryGroup],
                            nodes: List[Node]
                            ) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Prepare a main pd.DataFrame and a metadata ChainMap from a
    list of ``Node`` objects.

    :param x_groups: A user-given grouping query for X-axis values.
    :param y_groups: A user-given grouping query for Y-axis values.
    :param nodes: A list of Node objects to apply the group queries to.
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
    metadata_df = main_df.xs("metadata", axis=1)
    main_df = main_df.xs("data", axis=1)

    return main_df, metadata_df, metadata_dict


def create_group_mapping(mapping: Dict, groups: List[QueryGroup]) -> Dict:
    """Create a dictionary mapping based on the given mapping and query
    group.

    :param mapping: A dictionary from `chemmd.models.Experiment.species_factor_mapping`.
    :param groups: A list of query group objects.
    :returns: A QueryGroup based dictionary mapping of the original
        mapping provided.

    """
    group_mapping = {}

    def get_matching_species(species_list, group):
        """Helper function for checking species matches."""
        for s, sf in itertools.product(species_list, group.species_filters):
            if re.match(sf, s):
                yield s

    for group in groups:
        logger.debug(f"Examining group: {group}")

        # Ensure that this is not the special case of a species column.
        if group.factor_filters != ("Species",):

            # Examine each key: value set in the experiments mapping.
            for keys, metadata in mapping.items():

                species, factor_label = keys  # Extract the keys.
                # Find those species which match this QueryGroup.
                group_species_matches = list(get_matching_species(species, group))

                # If the species and unit filters match, add the data to the output
                # and break out of this loop.
                if group_species_matches and metadata["factor"].query(group.factor_filters):
                    metadata["species_keys"] = list(group_species_matches)
                    group_mapping[group] = metadata
                    logger.debug(f"Match found: {metadata['factor'].label}")
                    # The mappings are priority-ordered, so if a match is found
                    # we must break out of the loop to prevent the desired value
                    # from being overwritten with a lower-priority one.
                    break
        else:
            # Only return the first matching species for now.
            species_tuples = list(zip(*list(mapping.keys())))[0]
            species = list(set(itertools.chain.from_iterable(species_tuples)))
            matching_species = list(get_matching_species(species, group))
            group_mapping[group] = {"species_data": [matching_species, ]}
            logger.debug(f"Match found: {matching_species}")
            break

    return group_mapping


def group_mapping_as_df(group_mapping: Dict) -> Tuple[pd.DataFrame, Dict]:
    """Convert a given group_mapping to a pandas data frame object.

    :param group_mapping:
    :returns:

    """
    data_dict = {}
    metadata_dict = {}

    # grouping_dict = apply_transform(group_mapping)

    # For each group and its matches.
    for group, grouping_dict in group_mapping.items():

        metadata_keys = []

        # Get each of the nodal objects associated with this group
        # mapping match, get their UUIDs and add them to the metadata
        # dictionary.
        for nodal in ("experiment", "sample", "source"):
            try:
                nodal_object = grouping_dict[nodal]
                nodal_uuid = create_uuid(nodal_object)
                metadata_dict[nodal_uuid] = nodal_object
                metadata_keys.append(nodal_uuid)
            except KeyError:
                nodal_uuid = None  # Ensuring all key tuples are the
                # same length.
                metadata_keys.append(nodal_uuid)

        try:
            # Load this factors data into the data_dict.
            factor_data = grouping_dict["factor_data"]
            data_dict[("data", group.column_name)] = factor_data
            # Add an array of metadata keys of matching length.
            metadata_keys = [tuple(metadata_keys), ] * len(factor_data)
            data_dict[("metadata", group.column_name)] = metadata_keys

        except KeyError:
            # A KeyError here means that there is no factor data, in this
            # case that means there should be species data to extract instead.
            data_dict[("data", group.column_name)] = grouping_dict["species_data"]
            metadata_keys = [tuple(metadata_keys), ]
            data_dict[("metadata", group.column_name)] = metadata_keys

    try:
        # Ensure all the data sets are of the same (longest) length.
        factor_size = max(len(values) for values in data_dict.values())
        for key, value in data_dict.items():
            if len(value) == 1:
                data_dict[key] = value * factor_size
    except ValueError:
        pass

    # Convert the data dict into a data frame and return it.
    df = pd.DataFrame(data_dict)
    return df, metadata_dict
