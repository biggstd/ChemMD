Project Testing
===============

*Describes how to install `ChemMD` for development and how to
run tests on `ChemMD` and some `Bokeh` applications.*

Testing ChemMD
---------------

*From the parent directory of the git repository:* `ChemMD`
```bash
# Standard testing conditions.
pytest
# More verbose testing. (does not suppress print() output).
pytest -s -v
```

*See the `ChemMD.log` file generated.*

**Load a Demo `Node`**

```python
from chemmd.demos.loaders import (demo_keys, node_demo_by_key, 
                                  load_demo_nodes)

# View demo keys.
print(demo_keys)
('SIPOS_NMR', 'SIPOS_NMR_2', 'ERNESTO_NMR_1')

# Load by a key.
test_node = node_demo_by_key("SIPOS_NMR")

# Load all test nodes.
test_nodes = load_demo_nodes()
```

Python Tests Descriptions
-------------------------

+ `conftest.py`
+ `test_helpers.py`
+ `test_io.py`
+ `test_json_demo_vs_schema.py`
+ `test_models.py`


Testing Bokeh Applications
--------------------------

**Bokeh Tests:**

+ `table_test`
+ `scatter_test`
+ `table_scatter_combo_test`

```bash
# Launch the test application.
bokeh serve --show tests/bokeh_tests/table_test/ --log-level debug
```
