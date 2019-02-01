"""An application that serves a table and a scatter plot.

"""

# ----------------------------------------------------------------------------
# Standard Python Library.
# ----------------------------------------------------------------------------
import logging

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.io
import bokeh.models

# ----------------------------------------------------------------------------
# ChemMD imports
# ----------------------------------------------------------------------------
import chemmd.io.input
import chemmd.io.output
from chemmd.display import helpers
from chemmd.display.views.generic_table import table_layout
from chemmd.display.views.generic_cross_filter_scatter import scatter_layout

logger = logging.getLogger(__name__)
# ----------------------------------------------------------------------------
# Read the HTML session.
# TODO: Refactor this section into `helpers.py` for easier re-use.
# ----------------------------------------------------------------------------
try:
    # Get the list of all the .json files served by the Drupal server. Each of
    # these files represents a Drupal Node selected bu the user.
    json_file_paths = helpers.get_session_json_paths(bk.io.curdoc())

except FileNotFoundError as not_found:
    # Log the error.
    logger.error(f"Unable to read in the .json metadata"
                 f" files from:\n{json_file_paths}")
    # Log the Python error object as well.
    logger.error(not_found)
    # Warn somebody with a print statement.
    print(f"The .json metadata file could not be found!")
    raise FileNotFoundError

try:
    # Get the query groups supplied by the Drupal server. Each of these
    # represents a data column to be constructed.
    # This reads the current HTML session to get any groups provided.
    groups = helpers.get_session_groups(bk.io.curdoc())

except FileNotFoundError as not_found:
    # Log the error.
    logger.error(f"Unable to read in the .json group file"
                 f" from:\n{json_file_paths}")
    # Log the Python error object as well.
    logger.error(not_found)
    # Warn somebody with a print statement.
    print(f"The .json group file could not be found!")
    raise FileNotFoundError

try:
    # Create the ChemMD data model objects.
    nodes = chemmd.io.input.create_nodes_from_files(json_file_paths)

except FileNotFoundError as not_found:
    # Log the error.
    logger.error(f"Unable to read data files specified in the .json metadata"
                 f" files from:\n{json_file_paths}")
    # Log the Python error object as well.
    logger.error(not_found)
    # Warn somebody with a print statement.
    print(f"The a data .csv file could not be found!")
    raise FileNotFoundError

try:
    # Prepare those created nodes for Bokeh.
    main_df, metadata_df, metadata_dict = chemmd.io.output.prepare_nodes_for_bokeh(
        groups["x_groups"],
        groups["y_groups"],
        nodes)

except Exception as error:
    # Log the error.
    logger.error(f"Unable to parse the data for display, "
                 f"due to {error}")
    raise error

# ----------------------------------------------------------------------------
# Table creation
# ----------------------------------------------------------------------------
table = table_layout(
    groups["x_groups"],
    groups["y_groups"],
    main_df,
    metadata_df,
    metadata_dict)
table_panel = bk.models.Panel(child=table, title="Data Table")

# ----------------------------------------------------------------------------
# Scatter plot creation
# ----------------------------------------------------------------------------
scatter = scatter_layout(
    groups["x_groups"],
    groups["y_groups"],
    main_df,
    metadata_df,
    metadata_dict)
scatter_panel = bk.models.Panel(child=table, title="Scatter")

# ----------------------------------------------------------------------------
# Tab creation
# ----------------------------------------------------------------------------
tabs = bk.models.widgets.Tabs(tabs=[table_panel, scatter_panel])
# Add the created tabs to the current document.
bk.io.curdoc().add_root(tabs)
