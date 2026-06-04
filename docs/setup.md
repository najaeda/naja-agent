# Setup Guide for Claude

This guide explains how to add this skill to Claude and how to configure the MCP entries used with Claude Desktop.

## 1. Package the skill

1. Make sure the `skills/naja-base/` folder contains the skill file and its `resources/` and `scripts/` folders.
2. Compress the `naja-base` folder into a ZIP archive.
3. Keep the folder structure inside the ZIP exactly as it is on disk.

## 2. Add the skill to Claude

1. Open Claude.
2. Click **Customize**.
3. Open **Skills**.
4. Click the **+** button.
5. Choose **Create**.
6. Upload the ZIP file that contains the skill.

## 3. Update `claude_desktop_config`

Add these MCP entries to your `claude_desktop_config` file:

- `shared_files` lets Claude read, create, and modify files inside the shared folder path you choose. Replace `<path-to-shared-folder>` with the folder path you want to share.
- `desktop-commander` lets Claude launch scripts and other desktop commands.

```json
{
  "shared_files": {
    "command": "npx",
    "args": [
      "-y",
      "@modelcontextprotocol/server-filesystem",
      "<path-to-shared-folder>"
    ]
  },
  "desktop-commander": {
    "command": "npx",
    "args": [
      "-y",
      "@wonderwhy-er/desktop-commander@latest"
    ]
  }
}
```

## 4. Verify the result

After saving the configuration, restart Claude Desktop so the new skill and MCP servers are loaded.

If the skill does not appear, check that:

- the ZIP contains the `naja-base` folder at the top level
- `SKILL.md` is present in that folder
- the MCP configuration is valid JSON
