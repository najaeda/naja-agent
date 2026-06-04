# Canonical: Forbidden and Deprecated API Rules

This file centralizes forbidden, deprecated, or otherwise disallowed Naja API calls and export patterns.

Maintainers: update this single file; other documentation references it instead of repeating the list.

## Forbidden / Non-existent APIs (Do NOT use)
- `netlist.export_verilog()`
- `netlist.export_netlist()`
- `naja_lib.load_verilog()`
- `naja_lib.apply_del()`
- `VerilogDumpConfig.dump()`
- `term.disconnect()`

## Export guidance
- Preferred export: call `top.dump_verilog("output.v")` on the top instance.
- Output path must end with `.v` and the parent directory must exist prior to export.

## Loading / Compatibility Rules
- Use `netlist.load_primitives('xilinx')` only for Xilinx FPGA netlists. Call it before `load_liberty()` and `load_verilog()`, and abort on failure.
- For standard ASIC or Liberty-based flows, load `.lib` files and do not call `load_primitives('xilinx')` unless the workflow explicitly requires it.

## Hierarchy / Connectivity Rules
- Do not call `disconnect()` by itself for term rewiring. Use `term.disconnect_upper_net()` or `term.disconnect_lower_net()` explicitly.
- For a leaf child created with `create_child_instance()`, always use `connect_upper_net()` / `disconnect_upper_net()` on its terms when wiring from the parent side.
- Use `connect_lower_net()` / `disconnect_lower_net()` only for top-level terms or when the documentation explicitly asks for the lower side.
- A wrong upper/lower choice can trigger `RuntimeError` mismatch failures because the term is being attached to the wrong design side.

## Notes for script generators
- Do not copy this list into other files. Reference this canonical file when producing documentation or validation logic.
