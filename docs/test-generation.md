# Using Naja MCP for Netlist Test Generation

This guide explains how to use the Naja MCP tools to generate and validate netlist-oriented test cases.

## Overview

Naja MCP is designed to load netlists, inspect their structure, and apply updates or optimizations:

- Loading a design and extracting structural information
- Loading a liberty file and applying constant propagation
- Checking the effect of an update by re-reading the updated top design

## Step 1: Prepare Inputs

Put the following files in your shared folder:

- One or more `.v` Verilog netlists
- Optional `.lib` liberty files
- Optional generated output files if you want to validate a transformation

If you want sample Verilog files already available in this repository, use the `list_verilog_tests()` tool to discover them.

## Step 2: Clone the Naja Repository

```bash
git clone --recurse-submodules https://github.com/najaeda/naja.git <path-to-naja>
```

## Step 3: Copy Example Files to Your Shared Folder

Copy example inputs to your shared folder:

```bash
# Choose one example
cp <path-to-naja>/src/najaeda/benchmarks/verilog/tinyrocket.v <path-to-shared-folder>/
# or
cp -r <path-to-naja>/regress/sv <path-to-shared-folder>/naja_regress_sv
```

Your shared folder now contains benchmark or regress examples ready for Naja MCP analysis and updates.


Suggested test pattern:

1. Load the example design
2. Capture `get_top_info()` before the update
3. Apply `apply_dle()` or `apply_constant_propagation()`
4. Capture `get_top_info()` again and compare the observable counts

## Step 4: Load the Design

Use Claude with the Naja MCP tools to load the design and inspect it:

1. Call `load_verilog()` on the input netlist
2. If the test needs library information, call `load_liberty()` first
3. Call `get_top_info()` to capture the current structure of the design

Useful checks for a test:

- `nb_terms`
- `nb_nets`
- `nb_instances`
- term directions and widths
- instance models and leaf / blackbox status

## Step 5: Apply an Update

Choose the transformation your test is meant to validate:

- `apply_dle()` for dead logic elimination
- `apply_constant_propagation()` for constant propagation

Important:
- `apply_constant_propagation()` requires exactly one loaded liberty library
- If the design changes after an update, call `get_top_info()` again to confirm the new counts or hierarchy state

## Step 6: Write the Test Expectation

Tests should assert the observable outcome of the transformation, for example:

- the top design name is preserved
- the number of nets decreases after DLE
- the number of instances decreases after pruning unused logic
- a constant-driven structure disappears after constant propagation
- a known driver or fanout pattern changes as expected

You can also inspect:

- `get_max_fanout()` to confirm fanout changes
- `get_max_logic_level()` to confirm logic depth changes

## Example Test Prompt

"Load `tinyrocket.v`, inspect the top design, apply DLE, then report how the number of nets and instances changed."

Or, for regression examples:

"Load a design from `regress/sv`, apply constant propagation if a liberty file is present, then check whether the updated top design has fewer nets and whether the fanout changed."

## Practical Rule

For Naja MCP, a good test is usually a before/after check on the same design, not a comparison between two independent netlists.