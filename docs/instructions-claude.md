# Configuring Naja MCP in Claude Desktop

This guide explains how to add the Naja MCP server to Claude Desktop.

**Note:** This guide assumes you have already installed Naja MCP. See the main README and build script for installation instructions.

## Configuration

### Step 1: Locate Your Configuration File

Find your Claude Desktop configuration file:
- **Linux/Mac**: `~/.config/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Step 2: Add Naja MCP to Your MCP Servers

Edit your configuration file and add the Naja MCP server. Replace the placeholders with your actual paths:
- `<mcp-server-name>`: A name for this server (e.g., `naja`, `naja-mcp`, `netlist-tools`)
- `<path-to-naja-mcp>`: Full path to your Naja MCP repository
- `<path-to-naja-src>`: Path to the Naja Python sources (usually `<path-to-naja-mcp>/thirdparty/naja/src`)

```json
{
  "mcpServers": {
    "<mcp-server-name>": {
      "command": "python3",
      "args": [
        "<path-to-naja-mcp>/server.py"
      ],
      "env": {
        "PYTHONPATH": "<path-to-naja-src>"
      }
    }
  }
}
```

### Step 3: Verify

1. Save the configuration file
2. Restart Claude Desktop
3. Check that your MCP server appears as "Connected" in Claude's MCP server list

## Strongly Recommended: Add a Shared Folder

Adding a shared folder is strongly recommended. Without it, you'll need to copy-paste large netlists and libraries directly into Claude's prompt, which is inefficient and can hit token limits.

With the filesystem MCP server, Claude can access your files directly:

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "<path-to-shared-folder>"
  ]
}
```

Replace `<path-to-shared-folder>` with an absolute path to a folder where you want to store files accessible to Claude. This allows Claude to read netlists, liberty files, and generated outputs without copy-pasting.

## How Claude Should Use Naja MCP

Naja MCP is not a design-comparison tool. It is meant to load netlists, inspect them, and apply updates or optimizations.

Typical workflow:
- Load a liberty file with `load_liberty()` when the operation needs cell models.
- Load the design with `load_verilog()`.
- Inspect the design with `get_top_info()`, `get_max_fanout()`, or `get_max_logic_level()`.
- Apply transformations with `apply_dle()` or `apply_constant_propagation()`.
- Re-check the updated design with `get_top_info()` or another inspection tool.

## Troubleshooting

**Server won't connect:**
- Verify paths are absolute (not relative)
- Restart Claude Desktop after saving the config
- Ensure the config file is valid JSON
- Check that `<path-to-naja-mcp>/server.py` exists

**"Command not found" for python3:**
- Use the full path to Python: `/usr/bin/python3` instead of `python3`

**Invalid JSON errors:**
- Use a JSON validator to check your config file
- Ensure all commas and quotes are correct