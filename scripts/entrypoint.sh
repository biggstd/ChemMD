#!/usr/bin/env bash

echo "Starting Bokeh server..."

bokeh serve\
  --port 5006\
  --use-xheaders\
  --address 0.0.0.0\
  --allow-websocket-origin=130.20.47.245:8123\
  --allow-websocket-origin localhost:8123\
  --allow-websocket-origin idreamvisualization.pnl.gov\
  --allow-websocket-origin lampdev02.pnl.gov:8123\
  /opt/bkapps/scatter\
  /opt/bkapps/table
