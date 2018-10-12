"""Input and Output Operations

This module provides functions for transforming to and from ChemMD models.

ChemMD ``models`` can be created from:

+ .json source files

ChemMD ``models`` can be output to data frame, metadata dictionary pairs
with the use of ``query groups``.


"""

# ----------------------------------------------------------------------------
# Imports for API use.
#
# These functions will be available as `chemmd.io.func`.
# ----------------------------------------------------------------------------
from .input import (read_chemmd_json,
                    load_csv_as_dict,
                    create_nodes_from_files,
                    node_from_path)

from .output import (prepare_nodes_for_bokeh,
                     create_group_mapping,
                     group_mapping_as_df)
