# Kepler Formal MCP Tutorial

This file is for an agent that already has access to `kepler-formal-mcp`.

## When To Use It

Use this MCP when the task is one of the following:

- run a formal check on a `.v` netlist;
- validate that a structural change is observable;
- check an ECO or a small netlist transformation;
- avoid spending time on internal or anonymous nets that formal tools are unlikely to expose.

## Data The Agent Needs

The agent needs:

- one Verilog design file: a `.v` file;
- one or more Liberty files;
- optionally, a YAML configuration file if the workflow expects one.

a YAML is required, create it manually or use the workflow helper that generates it.
