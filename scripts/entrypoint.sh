#!/usr/bin/env bash

#
# See the documentation concerning the bokeh serve command here:
# https://bokeh.pydata.org/en/latest/docs/reference/command/subcommands/serve.html
#
# The each of the lines after the options are an application directory.
# These must be copied over in the Dockerfile for this script to find them.
#

echo "Checking the CHEMMD_CONFIG environment variable..."
echo "$CHEMMD_CONFIG"

if [ "$CHEMMD_CONFIG" == "TESTING" ]; then
    echo "Test configuration loaded. Starting test Bokeh server..."
    bokeh serve\
      --port 5006\
      --use-xheaders\
      --address 0.0.0.0\
      --log-level debug\
      --allow-websocket-origin localhost:8001\
      /tests/bokeh_tests/table_test
else
    echo "Starting production Bokeh server..."
    bokeh serve\
      --port 5006\
      --use-xheaders\
      --address 0.0.0.0\
      --allow-websocket-origin=130.20.47.245:8123\
      --allow-websocket-origin localhost:8123\
      --allow-websocket-origin localhost:8001\
      --allow-websocket-origin idreamvisualization.pnl.gov\
      --allow-websocket-origin lampdev02.pnl.gov:8123\
      /opt/bkapps/scatter\
      /opt/bkapps/table
fi
