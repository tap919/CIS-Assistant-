# CIS Assistant MCP Server - Quick Start Guide

Get up and running with CIS Assistant in 5 minutes!

## What is CIS Assistant?

CIS Assistant is an AI-powered development tool that helps you:
- 📝 Write formal specifications (contracts) before coding
- ✅ Validate your code automatically
- 🧠 Learn from past mistakes
- 📚 Build a library of reusable patterns

## Installation

### Step 1: Install Dependencies

```bash
pip install mcp pandas numpy
```

### Step 2: Clone or Download

```bash
git clone https://github.com/tap919/CIS-Assistant-.git
cd CIS-Assistant-
```

### Step 3: Test the Installation

```bash
PYTHONPATH=src python example_usage.py
```

You should see a demonstration of all CIS Assistant features!

## Using with Claude Desktop

### Step 1: Locate Your Config File

- **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Add CIS Assistant

Edit the config file and add:

```json
{
  "mcpServers": {
    "cis-assistant": {
      "command": "python",
      "args": ["-m", "cis_assistant_mcp.server"],
      "cwd": "/full/path/to/CIS-Assistant-",
      "env": {
        "PYTHONPATH": "/full/path/to/CIS-Assistant-/src"
      }
    }
  }
}
```

**Important**: Replace `/full/path/to/CIS-Assistant-` with the actual path where you cloned the repository.

### Step 3: Restart Claude Desktop

Close and reopen Claude Desktop. You should now see CIS Assistant tools available!

## Your First Contract

Try asking Claude:

> "Use the CIS Assistant to generate a contract for a UserAuthentication class that has login and logout methods."

Claude will use the `generate_contract` tool to create a formal specification!

## Basic Workflow

### 1. Generate a Contract

Ask Claude to create a contract:
```
Generate a contract for a DataValidator class with a validate method that 
checks if data is valid JSON.
```

### 2. Implement the Code

Write your implementation:
```python
class DataValidator:
    """Validates data formats"""
    
    def validate(self, data: str) -> bool:
        """Check if data is valid JSON"""
        try:
            json.loads(data)
            return True
        except:
            return False
```

### 3. Validate Your Implementation

Ask Claude:
```
Validate this implementation against the contract
```

### 4. Fix Any Issues

If validation fails, ask:
```
Get fix suggestions for the validation errors
```

### 5. Record Successful Fixes

When you fix an issue:
```
Record this error pattern so we can help with similar issues in the future
```

## Example Prompts for Claude

Here are some useful prompts to try:

### Contract Generation
- "Create a contract for a PaymentProcessor service"
- "Generate a specification for a caching layer class"
- "Define a contract for an API endpoint handler"

### Validation
- "Validate my implementation against contract_1_20260204"
- "Check if this code satisfies the contract requirements"

### Learning from Errors
- "Record this fix pattern for missing type hints"
- "Get suggestions for fixing this validation error"

### Example Management
- "Add this authentication pattern to the example library"
- "Search examples for error handling patterns"
- "Find examples tagged with 'async' and 'validation'"

### Workflow Guidance
- "Show me the contract-first development workflow"
- "How do I debug this validation error?"

## Available Tools Summary

| Tool | Purpose |
|------|---------|
| `generate_contract` | Create formal specifications |
| `validate_implementation` | Check code against contracts |
| `record_error_pattern` | Save successful fixes |
| `get_fix_suggestions` | Get help for errors |
| `add_example` | Add to example library |
| `search_examples` | Find relevant examples |
| `list_contracts` | View all contracts |
| `get_contract` | Get contract details |

## Tips for Success

### ✅ DO:
- Generate contracts **before** writing code
- Validate frequently during development
- Record successful fixes to build knowledge
- Use specific, descriptive names for components
- Add examples for patterns you use often

### ❌ DON'T:
- Skip the contract generation step
- Ignore validation errors
- Write code without reviewing the contract
- Forget to record successful fixes

## Troubleshooting

### "No module named 'mcp'"

Install the MCP package:
```bash
pip install mcp
```

### "Contract not found"

List available contracts:
```
Ask Claude: "List all contracts"
```

### Claude doesn't see the tools

1. Check the config file path is correct
2. Verify the `cwd` path points to the repository
3. Restart Claude Desktop
4. Check Claude's settings for MCP servers

### Server won't start

Test manually:
```bash
cd /path/to/CIS-Assistant-
PYTHONPATH=src python -m cis_assistant_mcp.server
```

If it starts without errors, the issue is likely in the config file.

## Next Steps

1. **Read the Full README**: Check `README.md` for detailed documentation
2. **Run the Demo**: Execute `example_usage.py` to see all features
3. **Try the Workflow**: Start with a simple class and follow the contract-first process
4. **Build Your Library**: Add examples as you discover useful patterns
5. **Share Patterns**: Contribute successful patterns back to the project

## Getting Help

- Review the demo: `python example_usage.py`
- Read the full documentation: `README.md`
- Check the example config: `mcp-config.json`
- Ask Claude to use the prompts: "Show me the contract-first development workflow"

## What Makes CIS Assistant Special?

Unlike traditional code generation:
- **Specifications First**: Clear contracts before implementation
- **Learning System**: Gets smarter from every fix
- **Validation-Driven**: Automatic compliance checking
- **Pattern Library**: Reusable, proven solutions

Start using contract-first development today! 🚀
