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


# ----------------------------------------------------------------------------
# Configuration loading and setup.
# ----------------------------------------------------------------------------
# Try to load the environment variable, if it is not found, instead assume
# a development environment and load the default config. This should fail
# on the Docker image (production) as the default configuration file will
# not be available.
config_env = os.environ.get("CHEMMD_CONFIG", "TESTING")
config_path = os.path.join("/md_config/config.json")

with open(config_path, "r") as json_config:
    config = json.load(json_config)

# demo_path = os.path.dirname(os.path.dirname(__file__))

demos = config['JSON_DEMOS']
config = config[config_env]

# config["TESTING"]["BASE_PATH"] = os.path.join(
#     demo_path, config["TESTING"]["BASE_PATH"])


logging.basicConfig(filename='ChemMD.log', level=config["LOG_LEVEL"])
