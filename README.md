ChemMD
======

*ChemMD is a wrapper for interpreting data and metadata `.json` files
for analysis and visualization.*

[![BCH compliance](https://bettercodehub.com/edge/badge/biggstd/ChemMD?branch=master)](https://bettercodehub.com/)
[![Build Status](https://travis-ci.org/biggstd/ChemMD.svg?branch=master)](https://travis-ci.org/biggstd/ChemMD)

Program Description
-------------------

`ChemMD` interprets a set of .json files, informed by an HTML session
request, served to a `bokeh` application. These metadata .json files
describe and point to data .csv files (provided to the application),
which are then visualized for the user.

Specifications for each .json object type can be found in the
`scr/chemmd/chemmd_schema.json`. *The query group specification has
not yet been created.*

Folder Descriptions
-------------------

*See the README files in each directory for a more detailed
description.*

+ `bokeh_applications` [Bokeh](https://github.com/bokeh/bokeh) web
    applications which display data / metadata sets provided
    by `ChemMD`.
+ `src/chemmd` The Python package which provides the data
    for the `bokeh` applications in `bokeh_apps`. The `src`
    directory is used to prevent tests from importing a local
    version of the package.
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

**To do:**

+ [x] Refactor query group objects.
+ [ ] Add query group .json specification.
+ [ ] Update README.
+ [ ] Create tutorials and place in documentation.
+ [ ] Repair typos within assays on Drupal.
+ [ ] Host documentation with PNNL? Or on readthedocs.
+ [ ] Fix bug causing the first row of .csv files to be dropped.
+ [ ] Complete query group setup on Drupal.
    *These should be content types that the user selects.*
+ [ ] Update metadata views.
+ [x] Add download button to table views.
    + [ ] Convert download to generic, only works in one case now.
+ [ ] Improve logging output.
+ [ ] Further update tests.
+ [ ] Sphinx documentation setup.
+ [ ] Add a license.
+ [ ] Bettercode recommendations and re-factors.
