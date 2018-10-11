#!/usr/bin/env bash

bokeh serve --show\
  tests/bokeh_tests/table_test/ \
  tests/bokeh_tests/scatter_test/ \
  tests/bokeh_tests/scatter_table_combo_test/ \
  --log-level debug
