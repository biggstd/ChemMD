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
from chemmd import demos, io
from chemmd.display.views.generic_table import table_layout

# ----------------------------------------------------------------------------
# Test Fixtures.
# ----------------------------------------------------------------------------
NMR_GROUPS = dict(
    x_groups=(('Total Aluminate Concentration', ('Molar',), ("Al",)),
              ('Counter Ion Concentration', ('Molar',),
               ("Na+", "Li+", "Cs+", "K+")),
              ('Counter Ion', ('Species',), ("Na+", "Li+", "Cs+", "K+",)),
              ('Base Concentration', ('Molar',), ("OH-",))),
    y_groups=(('27 Al ppm', ('ppm',), ("Al",)),)
)

# Load the demo data from ChemMD.
nmr_json_paths = [demos["SIPOS_NMR"], demos["SIPOS_NMR_2"]]

nmr_nodes = io.create_nodes_from_files(nmr_json_paths)

main_df, metadata_df, metadata_dict = io.prepare_nodes_for_bokeh(
    NMR_GROUPS["x_groups"],
    NMR_GROUPS["y_groups"],
    nmr_nodes)


# ----------------------------------------------------------------------------
# Table creation
# ----------------------------------------------------------------------------
table = table_layout(
    NMR_GROUPS["x_groups"],
    NMR_GROUPS["y_groups"],
    main_df,
    metadata_df,
    metadata_dict)

table_panel = bk.models.Panel(child=table, title="Data Table")

tabs = bk.models.widgets.Tabs(tabs=[table_panel])

# Add the created tabs to the current document.
bk.io.curdoc().add_root(tabs)
