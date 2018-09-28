ChemMD
======

*ChemMD is a wrapper for interpreting data and metadata `.json` files
for analysis and visualization.*

**To do:**

+ [ ] Travis CI integration
+ [ ] DockerHub integration
+ [ ] Better code integration
+ [ ] Sphinx documentation setup
+ [ ] Add a license
+ [ ] `io.py` see contained todo items.

Component Summaries
-------------------

*See the README files in each directory for a more detailed
description.*

+ `bokeh_apps`: [Bokeh](https://github.com/bokeh/bokeh) web
    applications which display data / metadata sets provided
    by `ChemMD`.
+ `chemmd`: The Python package which provides the data
    for the `bokeh` applications in `bokeh_apps`.
+ `scripts`: Scripts used for deploying applications within
    `bokeh_apps`.
+ `tests`: Tests for the contained programs.

Installation Instructions
-------------------------

**Basic Installation:**

```bash
# Clone the repository.
git clone git@github.com:biggstd/ChemMD.git
# Change to the parent directory and run the installer with pip.
cd ChemMD
pip install .
```

**Run in Docker:**

*To build the image locally:*

```bash
# Not yet implemented.
# docker build -t chemmd .
```

*To run the container from Docker Hub:*

```bash

```
