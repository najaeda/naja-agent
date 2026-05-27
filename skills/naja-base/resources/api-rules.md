# Canonical: Forbidden and Deprecated API Rules

This file centralizes forbidden, deprecated, or otherwise disallowed Naja API calls and export patterns.

Maintainers: update this single file; other documentation references it instead of repeating the list.

## Forbidden / Non-existent APIs (Do NOT use)
- `netlist.export_verilog()`
- `netlist.export_netlist()`
- `naja_lib.load_verilog()`
- `naja_lib.apply_del()`
- `VerilogDumpConfig.dump()`

## Export guidance
- Preferred export: call `top.dump_verilog("output.v")` on the top instance.
- Output path must end with `.v` and the parent directory must exist prior to export.

## Loading / Compatibility Rules
- `netlist.load_primitives()` is mandatory for Xilinx FPGA netlists. Call `netlist.load_primitives('xilinx')` first, before `load_liberty()` and `load_verilog()`, and abort on failure.
- For non-Xilinx flows, only use `load_primitives()` if the build and workflow explicitly require it.

## Notes for script generators
- Do not copy this list into other files. Reference this canonical file when producing documentation or validation logic.
