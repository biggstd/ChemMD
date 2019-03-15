"""Helper functions for creating Bokeh applications.


Helpers transform the pandas data frames and metadata dictionaries provided
by the ``io`` module.

"""

# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
import glob
import json
import itertools
import logging
import os
from typing import Dict, List, Tuple, Union

# Bokeh imports
import bokeh as bk
import bokeh.document
import bokeh.layouts
import bokeh.models
import bokeh.palettes

# External imports
import numpy as np
import pandas as pd
import markdown

# Local project imports.
from .. import config
from .. import io
from ..models import DerivedGroup, QueryGroup, GroupTypes

# ----------------------------------------------------------------------------
# Globals and constants
# ----------------------------------------------------------------------------

# Setup the error logger.
logger = logging.getLogger(__name__)

# Get the environment variable to find the base path for data files
# described in the loaded metadata.
HTTP_QUERY_STRING = config["HTTP_QUERY_STRING"]
GROUP_QUERY = config["HTTP_GROUP_QUERY"]
PALETTE = bk.palettes.Category10  # pylint: disable=maybe-no-member


# ----------------------------------------------------------------------------
# HTML Session API
# ----------------------------------------------------------------------------

def get_session_json_paths(current_document: bk.document.Document,
                           base_path: str = config["BASE_PATH"]) -> List[str]:
    """Get the HTTP request of an active bokeh document.

    The HTTP request points to the path where this document should load
    its .json metadata files.

    :param current_document: A bokeh Document instance. Usually provided by
        a call to `bk.io.curdoc()`.
    :param base_path: The base directory for reading json datafiles.

    :returns: A list of json file paths.

    """

    # Get the HTTP request and find the arguments being passed.
    arguments = current_document.session_context.request.arguments
    logger.info(f"Document HTTP context arguments: {arguments}")

    # Get the list of arguments (there should be only one).
    # TODO: Describe HTTP_QUERY_STRING better.
    file_path = arguments.get(HTTP_QUERY_STRING)[0].decode("utf-8")

    # The data should always be found in the "data" sub-directory.
    # It is placed there by the Drupal server.
    file_path = os.path.join(base_path, file_path)
    logger.info(f"Json file path found to be: {file_path}")

    return [json_file for json_file in
            glob.glob(f"{file_path}/*[!gq].json")]


def get_session_groups(current_document: bk.document.Document,
                       base_path: str = config["BASE_PATH"]) -> dict:
    """

    :param current_document:
    :param base_path:
    :return:
    """
    arguments = current_document.session_context.request.arguments
    group_path = arguments.get(HTTP_QUERY_STRING)[0].decode("utf-8")
    # The data should always be found in the "data" sub-directory.
    # It is placed there by the Drupal server.
    group_file = os.path.join(base_path, group_path, 'gq.json')

    with open(group_file, "r") as file:
        data = json.load(file)

    logger.info(f"Session groups found at: {group_file}")
    return data


def load_session_data(x_groups: QueryGroup,
                      y_groups: QueryGroup,
                      current_document: bk.document.Document
                      ) -> Tuple[bk.models.ColumnDataSource,
                                 pd.DataFrame,
                                 dict]:
    """Load data for a document instance based on the provided query groups.

    :returns:

    """

    # Find the paths based on the session context.
    json_paths = get_session_json_paths(current_document)

    # Build Node models from each of the found json files.
    nodes = io.create_nodes_from_files(json_paths)

    # Combine these nodes into a single set of data and metadata
    # based on the user-supplied query groups.
    data, data_metadata, cds_metadata = io.prepare_nodes_for_bokeh(
        x_groups=x_groups, y_groups=y_groups, nodes=nodes)

    # Build a Bokeh column data source object.
    source = bk.models.ColumnDataSource(data)

    logger.info(f"Session data loaded from: {json_paths}")
    return source, data_metadata, cds_metadata


# ----------------------------------------------------------------------------
# Data Preparation Functions
# ----------------------------------------------------------------------------


def categorize_columns(data_frame: pd.DataFrame,
                       x_groups: QueryGroup,
                       y_groups: QueryGroup
                       ) -> dict:
    """Helper function for categorizing user-group defined columns.

    The categories are then used to choose which visualization
    dimension is appropriate for a given column.

    :param data_frame:
    :param x_groups:
    :param y_groups:

    :returns:

    """

    # Extract the keys from the groups -- these are the names of
    # the user-defined columns.
    x_keys = get_group_keys(x_groups)
    y_keys = get_group_keys(y_groups)
    group_keys = x_keys + y_keys

    # Sort the columns, omit any not in group_keys -- ie. the
    # metadata foreign key columns.
    columns = sorted(data_frame.columns)
    columns = [x for x in columns if x in group_keys]

    # Discrete objects (strings and the like).
    discrete = [x for x in columns
                if data_frame[x].dtype == object
                and x in x_keys]

    # Continuous values only should remain.
    continuous = [x for x in columns
                  if x not in discrete
                  and x in x_keys]

    # Some of the continuous values may make more sense to bin
    # if there are few enough unique values.
    quantileable = [x for x in continuous
                    if len(data_frame[x].unique()) < 10
                    and x in x_keys]

    logger.info(f"Columns categorized: {columns}")
    return dict(columns=columns,
                discrete=discrete,
                continuous=continuous,
                quantileable=quantileable)


def get_group_keys(group):
    return [key for key, _, _ in group]


# ----------------------------------------------------------------------------
# Derived Column Preparation Functions
# ----------------------------------------------------------------------------


def create_derived_column(data_frame: pd.DataFrame,
                          derived_group: DerivedGroup
                          ) -> pd.DataFrame:
    """Calculate a column based on those already present in the data frame.

    :param data_frame:
    :param derived_group:
    :returns: A modified data_frame with the new column.

    """

    # Extract the column names and the callable from the derived group.
    new_column, precursor_columns, group_function = derived_group

    precursor_columns = data_frame[list(precursor_columns)].T.values
    # Apply the calculation with the precursor columns, and save the
    # result to the given data frame.
    data_frame[new_column] = group_function(*precursor_columns)

    logger.info(f"Derived column created: {new_column}")

    return data_frame


# ----------------------------------------------------------------------------
# Callback Functions
# ----------------------------------------------------------------------------


def get_metadata_keys(metadata_df: pd.DataFrame,
                      index_selections: List[int]
                      ):
    """Returns a metadata row based on a list of index selections.

    :param bokeh_source:
    :param index_selections:
    :param metadata_columns:
    :return:
    """

    return metadata_df.iloc[index_selections, :].values


# ----------------------------------------------------------------------------
# Bokeh Model Creation
# ----------------------------------------------------------------------------

def build_selection_controls(bokeh_source: bk.models.ColumnDataSource,
                             x_groups: GroupTypes,
                             y_groups: GroupTypes
                             ) -> Dict[str, bk.models.Select]:
    """Build a dictionary of bokeh selection controls based on given
    groups and data.

    :param bokeh_source: The data set to be examined in the form of
        a bokeh ColumnDataSource model.
    :param x_groups: A user-given grouping query for axis values.
    :param y_groups: A user-given grouping query for axis values.
    :return: A dictionary of labels values and controllers.

    """

    selection_controls = dict()  # Dictionary to be returned.

    # Create a dictionary of column groups. They keys are:
    # columns, discrete, continuous, quantileable.
    column_groups = categorize_columns(bokeh_source.to_df(),
                                       x_groups, y_groups)
    # Get the names of those columns in the Y groups.
    y_names = get_group_keys(y_groups)

    # Create the selectors.
    selection_controls["x_axis"] = bk.models.Select(
        title="X-Axis",
        options=column_groups["continuous"],
        value=column_groups["continuous"][0])

    selection_controls["y_axis"] = bk.models.Select(
        title="Y Axis",
        options=y_names,
        value=y_names[0])

    # Create a custom control for the axis scale.
    selection_controls["x_axis_type"] = bk.models.Select(
        title="X Axis Scale",
        options=["linear", "log"],
        value="linear")

    # Check if there are values which can be viewed reasonably with
    # a color or point size dimension, create the selector tool if so.
    if len(column_groups["discrete"]) >= 1:
        color = bk.models.Select(
            title='Color', value="None",
            options=["None"] + column_groups["discrete"])
        selection_controls["color"] = color

    if len(column_groups["continuous"]) >= 1:
        size = bk.models.Select(
            title='Size', value="None",
            options=["None"] + column_groups["continuous"])
        selection_controls["size"] = size

    logger.info(f"Constructed selection controls: {selection_controls.keys()}")
    return selection_controls


def create_colors(bokeh_source: bk.models.ColumnDataSource,
                  color_column: str,
                  palette=PALETTE
                  ) -> Union[str, Dict[str, bk.models.ColorMapper]]:
    """Create a color map based on a given column.

    :param bokeh_source:
    :param color_column:
    :param palette:
    :return:
    """
    if color_column != "None":
        unique_factors = np.unique(bokeh_source.data[color_column])
        color_mapper = bk.models.CategoricalColorMapper(
            factors=unique_factors,
            palette=palette[len(unique_factors)])

        logger.debug(f"Color map generated for {color_column}")
        return {"field": color_column, "transform": color_mapper}

    else:
        # Return a default color.
        logger.debug(f"Default color returned.")
        return "#31AADE"


def create_sizes(bokeh_source: bk.models.ColumnDataSource,
                 size_column: str
                 ) -> Union[Dict[str, bk.models.LinearInterpolator], int]:
    """

    :param bokeh_source:
    :param size_column:
    :return:
    """
    if size_column != "None":
        size_scale = bk.models.LinearInterpolator(
            x=[min(bokeh_source.data[size_column]),
               max(bokeh_source.data[size_column])],
            y=[3, 15])
        logger.debug(f"Size map generated for {size_column}")
        return dict(field=size_column, transform=size_scale)
    else:
        logger.debug(f"Default size returned.")
        return 7


def build_metadata_paragraph(metadata_dict: dict,
                             keys: Tuple[str, ...]
                             ) -> bk.models.widgets.Paragraph:
    """

    :param metadata_dict:
    :param keys:
    :return:
    """
    unique_keys = set(itertools.chain.from_iterable(keys))
    metadata_items = [metadata_dict.get(key) for key in unique_keys]

    text = ""
    for item in metadata_items:
        try:
            text += markdown.markdown(item.as_markdown)
        except Exception as error:
            text += str(item)
            logger.error(error)

    paragraph = bk.models.widgets.Div(text=text)
    return paragraph


def create_metadata_column(metadata_df: pd.DataFrame,
                           metadata: dict,
                           selected_indexes: List[int] = None
                           ) -> bk.layouts.column:
    """

    :param metadata_df:
    :param metadata:
    :param selected_indexes:
    :return:
    """

    logger.debug(f"Points selected: {selected_indexes}")

    # We must handle the None case so that we can call this function
    # upon application start, as well as point deselection.
    if selected_indexes:
        # Get the foreign keys from the bokeh source.
        selected_metadata_keys = get_metadata_keys(metadata_df,
                                                   selected_indexes)

        # Use those active keys to build metadata paragraphs.
        paragraphs = [build_metadata_paragraph(metadata, keys)
                      for keys in selected_metadata_keys]

    else:
        paragraphs = [bk.models.widgets.Paragraph(
            text="No data point selected.")]

    # Build a column of the generated metadata paragraphs.
    # They should resolve from most general to most specific.
    metadata_column = bk.layouts.column(children=paragraphs)

    return metadata_column
