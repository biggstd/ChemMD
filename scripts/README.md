Scripts
=======

`entrypoint.sh`: The default script to be run by a Docker image, it launches
the a `Bokeh` server with the `bokeh server` command. It is here that
allowed web-socket origins are defined, as well as a list of the applications
to be launched.

`run_test_bokeh_server.sh`: A testing script. This runs all of the bokeh
test applications found in `tests/bokeh_tests/`.
