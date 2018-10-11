ChemMD
======

*Main Package Directory*

**Description**  
This is the directory that is installed when the `setup.py`
script is run. The `test` directory is not created when
`chemmd` is installed.

Module Descriptions
-------------------

+ `__init__.py` Config file loading, package declarations.
+ `transforms.py` Transforms for data.

Package Descriptions
--------------------

+ `demos` Load demo `.json` files, `chemmd` objects, etc.
+ `display` Tools for building `bokeh` applications.
+ `io` Create `chemmd` models from `.json` files, prepare
   `chemmd` models for `bokeh` visualizations.
+ `models` Models for `chemmd`.

File Descriptions
-----------------

+ `chemmd_schema.json` A schema describing the `.json` input
  files required by `chemmd`.
+ `config.json` A configuration file where a options can be
  declared.
+ `README.md` This file.
