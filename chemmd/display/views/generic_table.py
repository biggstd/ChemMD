"""

"""

from typing import ChainMap

# ----------------------------------------------------------------------------
# Bokeh imports
# ----------------------------------------------------------------------------
import bokeh as bk
import bokeh.layouts
import bokeh.models
import bokeh.palettes
import bokeh.plotting
import bokeh.transform


# ----------------------------------------------------------------------------
# Data science imports
# ----------------------------------------------------------------------------
import pandas as pd

# ----------------------------------------------------------------------------
# Local project imports
# ----------------------------------------------------------------------------
from .. import helpers
from ...models.core import GroupTypes

# ----------------------------------------------------------------------------
# Global style definitions.
# ----------------------------------------------------------------------------
TITLE = "Data Table"


# ----------------------------------------------------------------------------
# Bokeh Panel Definition
# ----------------------------------------------------------------------------
def table_panel(x_groups: GroupTypes,
                y_groups: GroupTypes,
                main_df: pd.DataFrame,
                metadata_df: pd.DataFrame,
                metadata: dict) -> bk.models.Panel:
    """

    :param x_groups:
    :param y_groups:
    :param data:
    :param metadata:
    :return:

    """
    source = bk.models.ColumnDataSource(main_df)

    x_keys = helpers.get_group_keys(x_groups)
    y_keys = helpers.get_group_keys(y_groups)

    table_columns = [bk.models.TableColumn(field=key, title=key)
                     for key in x_keys + y_keys]

    table = bk.models.DataTable(
        source=source, columns=table_columns, width=1000)
    panel = bk.models.Panel(child=table, title=TITLE)

    return panel
