"""ChemMD Initialization File.

This is run whenever `ChemMD` is imported. In this case the configuration
file is loaded and supplied to the rest of the package as `config`.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import os
import json
import logging
import pkg_resources


# ----------------------------------------------------------------------------
# Configuration loading and setup.
# ----------------------------------------------------------------------------
# Try to load the environment variable, if it is not found, instead assume
# a development environment and load the default config. This should fail
# on the Docker image (production) as the default configuration file will
# not be available.
config_env = os.environ.get("CHEMMD_CONFIG", "TESTING")
config_path = os.environ.get("CHEMMD_CONFIG_PATH")

if config_path is None:
    path = pkg_resources.resource_filename(__name__, "config.json")
    with open(path, "r") as json_config:
        config = json.load(json_config)
else:
    with open(config_path, "r") as json_config:
        config = json.load(json_config)


demos = config['JSON_DEMOS']
config = config[config_env]

logging.basicConfig(filename='ChemMD.log', level=config["LOG_LEVEL"])
