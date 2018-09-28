Scripts
=======

`entrypoint.sh`: The default script to be run by a Docker image, it launches
the a `Bokeh` server with the `bokeh server` command. It is here that
allowed web-socket origins are defined, as well as a list of the applications
to be launched.
