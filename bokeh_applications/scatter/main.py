"""An application that serves a table and a scatter plot.

"""

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.io
import bokeh.models

# ----------------------------------------------------------------------------
# ChemMD imports
# ----------------------------------------------------------------------------
from chemmd import io
from chemmd.display import helpers
from chemmd.display.views.generic_table import table_layout
from chemmd.display.views.generic_cross_filter_scatter import scatter_layout


# ----------------------------------------------------------------------------
# Read the HTML session.
# ----------------------------------------------------------------------------
try:
    # Get the list of all the .json files served by the Drupal server. Each of
    # these files represents a Drupal Node selected bu the user.
    json_file_paths = helpers.get_session_json_paths(bk.io.curdoc())

    # Get the query groups supplied by the Drupal server. Each of these
    # represents a data column to be constructed.
    groups = helpers.get_session_groups(bk.io.curdoc())

    # Create the ChemMD data model objects.
    nodes = io.create_nodes_from_files(json_file_paths)

    # Prepare those created nodes for Bokeh.
    main_df, metadata_df, metadata_dict = io.prepare_nodes_for_bokeh(
        groups["x_groups"],
        groups["y_groups"],
        nodes)

except Exception as error:
    # TODO: Placeholder / error values that make sense to an end user.
    print(error)


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
