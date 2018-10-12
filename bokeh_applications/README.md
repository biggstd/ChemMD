Bokeh Applications
==================

Each folder within this directory is a Bokeh application. These are normally
launched from `entrypoint.sh`. These directories are setup according to the
structure outlined in the `bokeh` documentation.

[`bokeh` server documentation.](https://bokeh.pydata.org/en/latest/docs/user_guide/server.html)

*To launch one of these applications:*

```bash
# Launch a test application.
bokeh serve --show path/to/dir/
```

Although they may not work correctly without the Drupal server. See the
test applications for testing.


`scatter`
---------

A generic cross-filter scatter plot. This application is served in tabs,
one of which is the scatter plot, the other is a table of the data.


`table`
-------

A table of the requested data. This would be used for exporting data
based on a user `QueryGroup` request.
