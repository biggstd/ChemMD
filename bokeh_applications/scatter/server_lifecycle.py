"""A Bokeh-specific file that launches functions at specific points
within the Bokeh server's lifecycle.

"""
import os
import time
import shutil
import logging
from src.chemmd import config


# ----------------------------------------------------------------------------
# Globals and constants
# ----------------------------------------------------------------------------
# Setup the error logger.
logger = logging.getLogger(__name__)

# Get the environment variable to find the base path for data files
# described in the loaded metadata.
HTTP_QUERY_STRING = config["HTTP_QUERY_STRING"]
GROUP_QUERY = config["HTTP_GROUP_QUERY"]


# ----------------------------------------------------------------------------
# Life cycle functions.
# ----------------------------------------------------------------------------
def on_session_destroyed(session_context):
    """If present, this function is called when a session is closed.
    """
    # Get the file path of the generated json files for this instance.
    args = session_context.request.arguments
    # Try to read and remove the file path.
    try:
        folder_path = args.get(HTTP_QUERY_STRING)[0]
        group_file = args.get(GROUP_QUERY)[0]
        # Wait 3 minutes.
        time.sleep(180)
        # Remove the folder and all its contents.
        shutil.rmtree(folder_path)
        logger.info(f"Removed {folder_path} and nested files.")
        os.remove(group_file)
        logger.info(f"Removed {group_file}.")

    except:
        # TODO: Use better form on this exception.
        pass
