"""An test application that serves only a Table.

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
import chemmd.io.output
from chemmd.demos import loaders
from chemmd.display.views.generic_table import table_layout


# ----------------------------------------------------------------------------
# Test Fixtures.
# ----------------------------------------------------------------------------
# Load the demo data from ChemMD.
nmr_nodes = [loaders.node_demo_by_key("SIPOS_NMR"), ]

main_df, metadata_df, metadata_dict = chemmd.io.output.prepare_nodes_for_bokeh(
    loaders.NMR_GROUPS["x_groups"],
    loaders.NMR_GROUPS["y_groups"],
    nmr_nodes)


# ----------------------------------------------------------------------------
# Table creation
# ----------------------------------------------------------------------------
table = table_layout(
    loaders.NMR_GROUPS["x_groups"],
    loaders.NMR_GROUPS["y_groups"],
    main_df,
    metadata_df,
    metadata_dict)

table_panel = bk.models.Panel(child=table, title="Data Table")


# ----------------------------------------------------------------------------
# Tab creation
# ----------------------------------------------------------------------------
tabs = bk.models.widgets.Tabs(tabs=[table_panel])

# Add the created tabs to the current document.
bk.io.curdoc().add_root(tabs)
