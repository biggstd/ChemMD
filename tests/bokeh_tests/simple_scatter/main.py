"""An test application that serves a table scatter plot combination.

"""

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.io
import bokeh.plotting
import bokeh.models


# ----------------------------------------------------------------------------
# ChemMD imports
# ----------------------------------------------------------------------------
import chemmd.io
from chemmd.demos import loaders


# ----------------------------------------------------------------------------
# Test Fixtures.
# ----------------------------------------------------------------------------
# Load the demo data from ChemMD.
nmr_nodes = [loaders.node_demo_by_key("SIPOS_NMR"), ]

main_df, metadata_df, metadata_dict = chemmd.io.prepare_nodes_for_bokeh(
    loaders.NMR_GROUPS["x_groups"],
    loaders.NMR_GROUPS["y_groups"],
    nmr_nodes)

source = bk.models.ColumnDataSource(main_df)


def build_figure() -> bk.plotting.Figure:
    """

    :return:
    """
    # Create the basic figure object.
    figure = bk.plotting.Figure(name="scatter_panel_figure",
                                plot_width=600,
                                plot_height=600)

    # Draw circles (corresponding to data) on the figure.
    figure.circle(
        source=source,
        x=loaders.NMR_GROUPS["x_groups"][0][0],
        y=loaders.NMR_GROUPS["y_groups"][0][0]
    )

    return figure


bk.io.curdoc().add_root(build_figure())
