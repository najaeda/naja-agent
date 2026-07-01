# Naja SKILLS

This repository contains a single Claude skill package for Naja-related MCP workflows.

## What is here

- `skills/naja-base/SKILL.md`: the main skill definition. It explains how to generate Python scripts for Naja EDA netlist transformations and how to follow the required workflow.
- `skills/naja-base/resources/`: reference material used by the skill.
  - `api-functions.md`: API catalog and function reference.
  - `api-functions-old.md`: older API reference material kept for comparison.
  - `api-rules.md`: rules and forbidden API patterns.
  - `common-steps.md`: standard workflows and recurring patterns.
  - `kepler-formal-mcp-tutorial.md`: tutorial material.
  - `script-template.md`: recommended script structure.
  - `working-examples.md`: example scripts and usage patterns.
- `skills/naja-base/scripts/naja_utils.py`: helper utilities used by the skill.
- `docs/`: documentation for setup and usage.

## Purpose

The skill is designed to help generate safe, consistent Python scripts for Naja EDA tasks such as:

- loading Verilog or Liberty data
- inspecting and modifying netlists
- traversing hierarchy and terminals
- applying optimizations like DLE or constant propagation
- exporting results back to Verilog

## Recommended entry point

If you want to use this skill in Claude, read `docs/setup.md`.
