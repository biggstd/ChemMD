# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import itertools
import logging
import re
from typing import List, Tuple

import pandas as pd


from ..models import Node, QueryGroup
from ..models.util import create_uuid

logger = logging.getLogger(__name__)


def prepare_nodes_for_bokeh(x_groups: List[QueryGroup],
                            y_groups: List[QueryGroup],
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


def create_group_mapping(mapping, groups: List):
    group_mapping = {}

    def get_matching_species(species_list, group):
        for s, sf in itertools.product(species_list, group.species_filters):
            if re.match(sf, s):
                yield s

    # logger.debug(f"Mapping species: {species}")

    for group in groups:
        # logger.debug(f"Examining group:\n\t{group}")

        if group.factor_filters != ("Species",):
            for keys, metadata in mapping.items():

                species, factor_label = keys
                group_species_matches = list(get_matching_species(species, group))

                if group_species_matches and metadata["factor"].query(group.factor_filters):
                    metadata["species_keys"] = list(group_species_matches)
                    group_mapping[group] = metadata
                    # logger.debug(f"Match found: {metadata['factor'].label}")
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
            data_dict[("data", group.column_name)] = factor_data
            metadata_keys = [tuple(metadata_keys), ] * len(factor_data)
            data_dict[("metadata", group.column_name)] = metadata_keys

        except KeyError:
            data_dict[("data", group.column_name)] = grouping_dict["species_data"]
            metadata_keys = [tuple(metadata_keys), ]
            data_dict[("metadata", group.column_name)] = metadata_keys

    try:
        factor_size = max(len(values) for values in data_dict.values())
        for key, value in data_dict.items():
            if len(value) == 1:
                data_dict[key] = value * factor_size
    except ValueError:
        pass

    df = pd.DataFrame(data_dict)
    return df, metadata_dict
