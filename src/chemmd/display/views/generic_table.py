"""Provides a generic Bokeh table layout.

These layouts will typically be used to form a Tab entry in a Panel
object. This allows several different applications to be run at
once with the same data set requested by the user.

"""
# ----------------------------------------------------------------------------
# Generic Imports
# ----------------------------------------------------------------------------
import pkg_resources

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.layouts
import bokeh.models

# ----------------------------------------------------------------------------
# Data science imports
# ----------------------------------------------------------------------------
import pandas as pd

# ----------------------------------------------------------------------------
# Local project imports
# ----------------------------------------------------------------------------
from .. import helpers
from ...models import GroupTypes

# ----------------------------------------------------------------------------
# Global style definitions.
# ----------------------------------------------------------------------------
TITLE = "Data Table"


# ----------------------------------------------------------------------------
# Bokeh Layout Definition
# ----------------------------------------------------------------------------
def table_layout(x_groups: GroupTypes,
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
    :returns:

    """
    # Convert the data frame to a Bokeh data format.
    source = bk.models.ColumnDataSource(main_df)

    # Parse the requested keys to use as column names.
    x_keys = helpers.get_group_keys(x_groups)
    y_keys = helpers.get_group_keys(y_groups)

    # Create the Bokeh table.
    table_columns = [bk.models.TableColumn(field=key, title=key)
                     for key in x_keys + y_keys]
    table = bk.models.DataTable(
        source=source, columns=table_columns, width=800)

    # Create the download button.
    button = bk.models.widgets.Button(label="Download",
                                      button_type="success")

    # Load the custom java script.
    js_code_path = pkg_resources.resource_filename(
        "chemmd", "display/views/custom_js/download.js")

    print(js_code_path)

    with open(js_code_path, 'r') as file:
        js_code = file.read()

    # Apply the custom java script to the button.
    button.callback = bk.models.CustomJS(args=dict(source=source),
                                         code=js_code)

    # Build the controls widget box.
    controls = bk.layouts.widgetbox(button)

    # Built and return the layout object.
    layout = bk.layouts.layout(children=[controls, table])
    return layout
