Project Testing
===============

*Describes how to install `ChemMD` for development and how to
run tests on `ChemMD` and some `Bokeh` applications.*

Testing ChemMD
---------------

**Import ChemMD**



**Load a Demo `Node`**

```python
from chemmd import io
from chemmd import demos

demo_node = io.parse_node_json(io.read_idream_json(demos["SIPOS_NMR"]))
```

Testing Bokeh Applications
--------------------------
