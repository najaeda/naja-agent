# Catalog: Naja API Functions

**Reference:** https://najaeda.readthedocs.io/en/latest
**Module:** `import najaeda.netlist as netlist`

This catalog lists all documented Naja functions. Always consult before generating a script.
If a function is not listed here, do not use it — ask for clarification instead.

---

## Loading Functions

### load_verilog(filepath)
**Objective:** Load a Verilog design from file
- **Input:** File path (string)
- **Output:** Design object loaded in memory
- **Return:** Design object
- **Example:** `top = netlist.load_verilog("circuit.v", config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True))`
- **Notes:** Most common format for digital designs

### load_system_verilog(filepath)
**Objective:** Load a SystemVerilog design from file
- **Input:** File path (string)
- **Output:** Design object loaded in memory
- **Return:** Design object
- **Example:** `top = netlist.load_verilog("design.sv", config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True))`
- **Notes:** Prefer `load_verilog` with explicit `VerilogConfig`

### load_liberty(filepath)
**Objective:** Load a Liberty library file
- **Input:** File path (string)
- **Output:** Library object with cell definitions
- **Return:** None
- **Example:** `netlist.load_liberty([str(f) for f in Path(design_dir).glob("*.lib")])`
- **Notes:** Always load `.lib` files before Verilog

### load_primitives(filepath)
**Objective:** Load primitive definitions
- **Input:** File path (string)
- **Output:** Primitives object
- **Return:** Primitives object
- **Example:** `prims = netlist.load_primitives("primitives.def")`
- **Notes:** Defines basic gates and components.

**Availability:** `load_primitives()` may not be available in all Naja builds. Generated code should not assume its presence. Use a runtime check or try/except, for example:

```python
if hasattr(netlist, 'load_primitives'):
    prims = netlist.load_primitives("primitives.def")
else:
    logger.debug("load_primitives not available in this build")
```

### load_primitives_from_file(file)
**Objective:** Load a primitives library from a Python file
- **Input:** File path (string)
- **Output:** Primitives library loaded from code
- **Return:** None
- **Example:** `netlist.load_primitives_from_file("primitives.py")`
- **Notes:** The file must define `load(db)`

### load_naja_if(path)
**Objective:** Load a Naja IF file
- **Input:** Path to a Naja IF file
- **Output:** Current netlist restored from disk
- **Return:** None
- **Example:** `netlist.load_naja_if("design.naja")`
- **Notes:** Use when round-tripping a design in Naja IF format

---

## Navigation Functions

### get_top()
**Objective:** Get the top-level module
- **Input:** Design object (implicit from context)
- **Output:** Top module reference
- **Return:** Module object
- **Example:** `top = netlist.get_top()`

### get_instance_by_path(path)
**Objective:** Navigate to an instance by hierarchical path
- **Input:** Path string (e.g., "top/cpu/alu")
- **Output:** Instance object at that path
- **Return:** Instance object or None
- **Example:** `inst = top.get_instance_by_path("top/cpu")`
- **Notes:** Hierarchical navigation; path separator is "/"

### get_leaf_children()
**Objective:** Get all leaf (non-hierarchical) children
- **Input:** Instance (implicit)
- **Output:** Iterator of leaf instances
- **Return:** Iterator[Instance]
- **Example:** `leaves = list(module.get_leaf_children())`

## Term/Net Connectivity Functions

### get_name()
**Objective:** Get the instance name
- **Input:** Instance or module (implicit)
- **Output:** Instance name as string
- **Return:** str
- **Example:** `name = instance.get_name()`

### get_model_name()
**Objective:** Get the model/cell name
- **Input:** Instance or module (implicit)
- **Output:** Model name as string
- **Return:** str
- **Example:** `name = instance.get_model_name()`
- **Notes:** Useful for identifying cell types

### get_input_bit_terms()
**Objective:** Get all input bit terminals
- **Input:** Instance (implicit)
- **Output:** Generator of input terminals
- **Return:** Generator[Term]
- **Example:** `inputs = list(instance.get_input_bit_terms())`
- **Notes:** Wrap in `list()` before indexing or using `len()`

### get_output_bit_terms()
**Objective:** Get all output bit terminals
- **Input:** Instance (implicit)
- **Output:** Generator of output terminals
- **Return:** Generator[Term]
- **Example:** `outputs = list(instance.get_output_bit_terms())`
- **Notes:** Wrap in `list()` before indexing or using `len()`

### get_flat_input_terms()
**Objective:** Get flattened input terms
- **Input:** Instance (implicit)
- **Output:** Flat list of input bits
- **Return:** List[Term]
- **Example:** `flat_inputs = instance.get_flat_input_terms()`

### get_flat_output_terms()
**Objective:** Get flattened output terms
- **Input:** Instance (implicit)
- **Output:** Flat list of output bits
- **Return:** List[Term]
- **Example:** `flat_outputs = instance.get_flat_output_terms()`

## Modification Functions

### create_net(name)
**Objective:** Create a scalar net in an instance
- **Input:** Net name (string)
- **Output:** New scalar net
- **Return:** Net
- **Example:** `net = top.create_net("new_signal")`
- **Notes:** Use `create_bus_net` when you need a bus

## Module / Utility Functions

### create_top(name)
**Objective:** Create a new top instance
- **Input:** Top instance name (string)
- **Output:** Empty top instance
- **Return:** Instance
- **Example:** `top = netlist.create_top("top")`

### dump_naja_if(path)
**Objective:** Export the current design to Naja IF
- **Input:** Output path
- **Output:** Naja IF file on disk
- **Return:** None
- **Example:** `netlist.dump_naja_if("output.naja")`

### consistent_hash(obj)
**Objective:** Compute a stable hash for a Naja object
- **Input:** Object reference
- **Output:** Stable hash value
- **Return:** Hash value
- **Example:** `key = netlist.consistent_hash(obj)`

### get_max_fanout()
**Objective:** Get the maximum fanout of the top design
- **Input:** None
- **Output:** Maximum fanout value
- **Return:** int
- **Example:** `fanout = netlist.get_max_fanout()`

### get_max_logic_level()
**Objective:** Get the maximum logic level of the top design
- **Input:** None
- **Output:** Maximum logic level value
- **Return:** int
- **Example:** `level = netlist.get_max_logic_level()`

### get_primitives_library()
**Objective:** Return the embedded primitives library
- **Input:** None
- **Output:** Loaded primitives library object
- **Return:** Library object
- **Example:** `library = netlist.get_primitives_library()`

### get_snl_instance_from_id_list(id_list)
**Objective:** Resolve an SNL instance from an ID path
- **Input:** List of IDs
- **Output:** SNL instance object
- **Return:** SNLInstance
- **Example:** `inst = netlist.get_snl_instance_from_id_list([1, 2, 3])`

### get_snl_path_from_id_list(id_list)
**Objective:** Resolve an SNL path from an ID path
- **Input:** List of IDs
- **Output:** SNL path object
- **Return:** SNLPath
- **Example:** `path = netlist.get_snl_path_from_id_list([1, 2, 3])`

### get_snl_term_for_ids_with_path(path, termID, bit)
**Objective:** Resolve an SNL term from path and IDs
- **Input:** Path, term ID, bit index
- **Output:** SNL term object
- **Return:** Term object from the underlying SNL layer
- **Example:** `term = netlist.get_snl_term_for_ids_with_path(path, term_id, bit)`

### reset()
**Objective:** Reset the current environment
- **Input:** None
- **Output:** Cleared netlist state
- **Return:** None
- **Example:** `netlist.reset()`

---

## Transformation Functions


### apply_dle()
**Objective:** Apply dead logic elimination.
- **Input:** No explicit argument (uses current netlist context)
- **Output:** Updated netlist state
- **Return:** Transform-specific result, depending on installed Naja version
- **Example:** `result = netlist.apply_dle()`
- **Notes:** Native API; do not rebuild this transform manually



### apply_constant_propagation()
**Objective:** Propagate constants through the netlist.
- **Input:** No explicit argument (uses current netlist context)
- **Output:** Updated design object
- **Return:** Transform-specific result, depending on the installed Naja version
- **Example:** `result = netlist.apply_constant_propagation()`
- **Notes:** Used by the multi-step template

---

## Export / Save Functions

### dump_verilog(filepath)
**Objective:** Write the current top design to disk.
- **Input:** Destination path on top instance
- **Output:** Verilog file on disk
- **Return:** None
- **Example:** `top.dump_verilog("output.v")`
- **Notes:** Path must end with `.v`, and output directory must exist

For the canonical list of forbidden or deprecated API calls, see [resources/api-rules.md](resources/api-rules.md).

---

## Attribute Functions

### get_attributes()
**Objective:** Get all attributes of an object
- **Input:** Object reference (implicit)
- **Output:** Dictionary of attributes
- **Return:** Dict[str, Any]
- **Example:** `attrs = instance.get_attributes()`
- **Notes:** Includes metadata like location, timing, power

---

## Common Error Handling

| Function | Common Error | Solution |
|----------|--------------|----------|
| `load_verilog()` | FileNotFoundError | Check absolute path |
| `get_instance_by_path()` | Invalid path | Verify path with get_top() navigation |
| `connect()` | TypeError: width mismatch | Ensure net width matches terminal |
| `delete_net()` | RuntimeError: still connected | Call disconnect() first |
| `rename()` | NameError: already exists | Check for naming conflicts |

---

## Usage Pattern in Scripts

```python
from pathlib import Path

import najaeda.netlist as netlist

# Load design
input_path = "circuit.v"
design_dir = Path(input_path).resolve().parent
netlist.load_liberty([str(f) for f in design_dir.glob("*.lib")])
top = netlist.load_verilog(
    input_path,
    config=netlist.VerilogConfig(keep_assigns=True, allow_unknown_designs=True),
)
if top is None:
    exit(1)

# Navigate
target_inst = top.get_instance_by_path("top/cpu/alu")
if target_inst is None:
    exit(1)

# Query connectivity
input_terms = list(target_inst.get_input_bit_terms())
output_terms = list(target_inst.get_output_bit_terms())

# Modify
net = top.create_net("new_signal", 1)
success = input_terms[0].connect(net)

# Transform
netlist.apply_dle()
netlist.apply_constant_propagation()

# Export/Save
top.dump_verilog("output.v")
```