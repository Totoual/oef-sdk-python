A simple application that shows how the Python API for OEFCore can be used.

In this demo, every agent has its own coordinates `(x, y)`. 
The locations are randomly initialized.

After the initialization, every agent does the following:
    - Register to the node;
    - Make a query for other agents in the proximity of it's location

## How to run

```
python examples/demo/main.py
```
