"""

"""

# ----------------------------------------------------------------------------
# Standard and data science imports
# ----------------------------------------------------------------------------
import itertools
from typing import ChainMap, Dict, List, Tuple, Union

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.layouts
import bokeh.models
import bokeh.plotting
import pandas as pd

# ----------------------------------------------------------------------------
# ISADream imports
# ----------------------------------------------------------------------------
from .. import helpers
from ...models.core import GroupTypes

# ----------------------------------------------------------------------------
# Global style definitions.
# ----------------------------------------------------------------------------
TITLE = "Scatter Plot"


# ----------------------------------------------------------------------------
# Bokeh Layout Definition
# ----------------------------------------------------------------------------
def scatter_layout(x_groups: GroupTypes,
                  y_groups: GroupTypes,
                  main_df: pd.DataFrame,
                  metadata_df: pd.DataFrame,
                  metadata: dict) -> bk.models.Panel:
    """

    :param x_groups:
    :param y_groups:
    :param main_df:
    :param metadata_df:
    :param metadata:
    :return:
    """
    # ------------------------------------------------------------------------
    # Create the interactive bokeh column data source.
    # ------------------------------------------------------------------------
    source = bk.models.ColumnDataSource(main_df)

    # ------------------------------------------------------------------------
    # Define point selection callback.
    # ------------------------------------------------------------------------
    def point_selection_callback(attr, old, new):
        # Get the selected value indices or None with a ternary operator.
        selected_indexes = new['1d']['indices'] \
            if new['1d']['indices'] else None

        # Create the metadata column layout element.
        column = helpers.create_metadata_column(
            metadata_df, metadata, selected_indexes)
        # Get the parent layout element and update its children.
        curr_layout = bk.plotting.curdoc().get_model_by_name(
            'metadata_column')
        curr_layout.children[0] = column

    # Add the point selection callback to the bokeh source object.
    source.on_change("selected", point_selection_callback)

    # ------------------------------------------------------------------------
    # Define selector controls, and add a callback function.
    # ------------------------------------------------------------------------
    # Create dictionary of controls based on the given groups and data.
    controls = helpers.build_selection_controls(source, x_groups, y_groups)

    def controller_callback(attr, old, new):
        # Get the parent layout that contains the main figure.
        curr_layout = bk.plotting.curdoc().get_model_by_name('main_figure')
        # Replace the current child with an updated figure.
        curr_layout.children[0] = build_figure()

    # Assign the callback function defined above to each of the generated
    # selector controls.
    for control in controls.values():
        control.on_change("value", controller_callback)

    # Create a bokeh widget box layout to hold the controls.
    control_widget = bk.layouts.widgetbox(list(controls.values()))

    # ------------------------------------------------------------------------
    # Define the primary figure.
    # ------------------------------------------------------------------------
    def build_figure() -> bk.plotting.Figure:
        """

        :return:
        """
        # Create the basic figure object.
        figure = bk.plotting.Figure(name="scatter_panel_figure",
                                    x_axis_type=controls["x_axis_type"].value,
                                    plot_width=600,
                                    plot_height=600)

        # Set the axis titles of the figure.
        figure.xaxis.axis_label = controls["x_axis"].value
        figure.yaxis.axis_label = controls["y_axis"].value

        # Draw circles (corresponding to data) on the figure.
        circles = figure.circle(
            source=source,
            x=controls["x_axis"].value,
            y=controls["y_axis"].value,
            color=helpers.create_colors(source, controls["color"].value),
            size=helpers.create_sizes(source, controls["size"].value))

        # An ad-hoc method to create a legend outside of the plot area.
        # The renderer created above is used to give context to the legend.
        # TODO: Fix the resizing bug associated with this.
        if controls["color"].value != "None":
            legend_item = bk.models.LegendItem(
                label=dict(field=controls["color"].value),
                renderers=[circles])
            legend = bk.models.Legend(items=[legend_item])
            figure.add_layout(legend, "below")
            figure.legend.orientation = "horizontal"

        # Add tools for interactivity to the figure.
        figure.add_tools(bk.models.TapTool())  # Required for selections.

        return figure

    # ------------------------------------------------------------------------
    # Initialize defaults and define the layout.
    #
    # The layout elements can be retrieved and updated by their assigned
    # names.
    # ------------------------------------------------------------------------
    layout = bk.layouts.layout(
        name="panel_layout",
        # Top level lists are columns, nested lists are rows.
        children=[[
            bk.layouts.column(name="control_widget",
                              children=[control_widget]),
            bk.layouts.column(name="main_figure",
                              children=[build_figure()]),
            bk.layouts.column(name="metadata_column",
                              children=[helpers.create_metadata_column(
                                  source, metadata)])
        ]])
    return layout
