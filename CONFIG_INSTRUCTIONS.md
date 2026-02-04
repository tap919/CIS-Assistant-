# MCP Configuration Instructions

This file provides instructions for configuring the CIS Assistant MCP server with various MCP clients.

## Configuration File Template

The `mcp-config.json` file in this repository is a **TEMPLATE**. You need to:

1. **Copy it to your MCP client's configuration location**
2. **Replace placeholder paths with actual paths on your system**

## For Claude Desktop

### Step 1: Locate Your Config File

- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Update the Template

In `mcp-config.json`, replace these placeholders:
- `/path/to/CIS-Assistant-` → Full path where you cloned this repo

Example (MacOS):
```json
{
  "mcpServers": {
    "cis-assistant": {
      "command": "python",
      "args": ["-m", "cis_assistant_mcp.server"],
      "cwd": "/Users/yourusername/projects/CIS-Assistant-",
      "env": {
        "PYTHONPATH": "/Users/yourusername/projects/CIS-Assistant-/src"
      }
    }
  }
}
```

Example (Windows):
```json
{
  "mcpServers": {
    "cis-assistant": {
      "command": "python",
      "args": ["-m", "cis_assistant_mcp.server"],
      "cwd": "C:\\Users\\YourUsername\\projects\\CIS-Assistant-",
      "env": {
        "PYTHONPATH": "C:\\Users\\YourUsername\\projects\\CIS-Assistant-\\src"
      }
    }
  }
}
```

### Step 3: Merge with Existing Config

If you already have other MCP servers configured, merge the configurations:

```json
{
  "mcpServers": {
    "existing-server": {
      // ... your existing server config
    },
    "cis-assistant": {
      // ... add the CIS Assistant config here
    }
  }
}
```

### Step 4: Restart Claude Desktop

Close and reopen Claude Desktop for the changes to take effect.

## For Other MCP Clients

The basic structure is similar for other MCP-compatible clients:

1. Find the client's configuration location
2. Add the CIS Assistant server configuration
3. Update paths to match your system
4. Restart the client

## Verifying Configuration

To verify your configuration is correct:

1. Open your MCP client (e.g., Claude Desktop)
2. Look for CIS Assistant tools in the available tools list
3. Try a simple command like "List all contracts"

## Troubleshooting

### Server Won't Start

1. Check that Python is available: `python --version`
2. Verify dependencies are installed: `pip list | grep mcp`
3. Test the server manually:
   ```bash
   cd /path/to/CIS-Assistant-
   PYTHONPATH=src python -m cis_assistant_mcp.server
   ```

### Wrong Path Errors

- Ensure paths use forward slashes on Unix/MacOS
- Ensure paths use backslashes on Windows (or double backslashes in JSON)
- Use absolute paths, not relative paths
- Don't include trailing slashes

### Permission Errors

- Ensure you have read/write permissions in the CIS-Assistant directory
- On Unix/MacOS, you may need to make files executable

### Module Not Found

- Verify PYTHONPATH includes the `src` directory
- Check that all files were properly installed
- Try reinstalling: `pip install -e .`

## Alternative: Install as Package

Instead of using PYTHONPATH, you can install the package:

```bash
cd /path/to/CIS-Assistant-
pip install -e .
```

Then use this simpler config (no PYTHONPATH needed):

```json
{
  "mcpServers": {
    "cis-assistant": {
      "command": "cis-assistant",
      "cwd": "/path/to/CIS-Assistant-"
    }
  }
}
```

## Getting Help

If you're still having issues:

1. Check the QUICKSTART.md guide
2. Review the README.md documentation
3. Run the example_usage.py to test locally
4. Check your MCP client's logs for error messages
