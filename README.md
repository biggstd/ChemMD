ChemMD
======

*ChemMD is a wrapper for interpreting data and metadata `.json` files
for analysis and visualization.*

[![BCH compliance](https://bettercodehub.com/edge/badge/biggstd/ChemMD?branch=master)](https://bettercodehub.com/)
[![Build Status](https://travis-ci.org/biggstd/ChemMD.svg?branch=master)](https://travis-ci.org/biggstd/ChemMD)

**To do:**

+ [x] Refactor query group objects.
+ [ ] Complete query group setup on Drupal.
    *These should be content types that the user selects.*
+ [x] Fix UI on experiment creation on Drupal.
+ [x] DockerHub integration.
+ [x] Travis CI integration.
+ [x] Complete `ChemMD` repository setup.
    + [x] Apply new structure to Bokeh applications.
    + [x] Generic Scatter with a data table application.
    + [x] Data table application.
    + [x] Describe commands in `entrypoint.sh`.
+ [x] Add download button to table views.
    + [ ] Convert download to generic, only works in one case now.
+ [x] Better code integration.
+ [x] Complete tests setup for `ChemMD`.
+ [x] Repair `io` functions.
+ [x] Update `bokeh` tests.
+ [ ] Sphinx documentation setup.
+ [ ] Add a license.
+ [ ] Bettercode recommendations and re-factors..

Folder Descriptions
-------------------

*See the README files in each directory for a more detailed
description.*

+ `bokeh_apps` [Bokeh](https://github.com/bokeh/bokeh) web
    applications which display data / metadata sets provided
    by `ChemMD`.
+ `chemmd` The Python package which provides the data
    for the `bokeh` applications in `bokeh_apps`.
+ `scripts` Scripts used for deploying applications within
    `bokeh_apps`.
+ `tests` Tests for the contained programs.

File Descriptions
-----------------

*Files in this top-level directory.*

+ `.gitignore` Files and folders to be ignored by Git.
+ `.travis.yml` A travis.ci workflow file.
+ `Dockerfile` A file which defines the Docker image with
   ChemMD and associated visualizations. The image launches
   a Bokeh server by default. 
+ `LICENSE.txt` 
+ `README.md` This readme file.
+ `requirements.txt` A list of Python packages needed for
   ChemMD to function.
+ `setup.py` The installation script for the ChemMD package.


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
 docker build -t ChemMD .
```

*To run the container from Docker Hub:*

```bash
docker run -p 0.0.0.1:8001:5006\
  -e "CHEMMD_CONFIG=DEFAULT"\
  -v /data/dir/on/host:/opt/isadream/data \
  -t -d --name chemmd tylerbiggs/chemmd:VERSION
```

*To open a bash shell within the container:*

```bash
docker exec -it ChemMD bash
```

*To stop and delete the container:*

```bash
docker stop ChemMD && docker rm ChemMD
```

Testing
-------

**Testing on Docker**

```bash
docker run -p 0.0.0.1:8001:5006\
  -e "CHEMMD_CONFIG=TESTING"\
  -t -d --name chemmd tylerbiggs/chemmd:VERSION
```
