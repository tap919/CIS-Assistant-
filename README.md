# CIS Assistant MCP Server

A Model Context Protocol (MCP) server that provides intelligent code development assistance using the Circulatory Informatics System (CIS) methodology.

## Overview

CIS Assistant is an MCP server that enables AI applications (like Claude) to:
- Generate formal contract specifications for software components
- Validate code implementations against contracts
- Learn from error patterns to provide better suggestions
- Manage a library of code examples
- Guide developers through contract-first development

## Features

### 🎯 Contract-First Development
- Generate formal specifications before coding
- Define clear interfaces and constraints
- Validate implementations automatically

### 🔍 Error Pattern Learning
- Record successful fixes for future reference
- Get targeted suggestions based on historical patterns
- Continuously improve recommendations

### 📚 Example Library
- Store and search code examples
- Tag and categorize patterns
- Quick access to proven solutions

### ✅ Validation & Compliance
- Automated contract validation
- Constraint checking
- Type hint enforcement

## Installation

### Prerequisites
- Python 3.10 or higher
- pip

### Install Dependencies

```bash
# Install the package in development mode
pip install -e .

# Or install dependencies directly
pip install mcp
```

## Usage

### Running the Server

The server uses stdio transport for communication with MCP clients:

```bash
python -m cis_assistant_mcp.server
```

Or using the module directly:

```bash
python src/cis_assistant_mcp/server.py
```

### Configuring with Claude Desktop

To use this server with Claude Desktop, add the following to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cis-assistant": {
      "command": "python",
      "args": [
        "-m",
        "cis_assistant_mcp.server"
      ],
      "cwd": "/path/to/CIS-Assistant-"
    }
  }
}
```

Replace `/path/to/CIS-Assistant-` with the actual path to this repository.

## Available Tools

### 1. generate_contract
Generate a formal contract specification for a software component.

**Parameters:**
- `component_name`: Name of the component
- `component_type`: Type (class, function, module, service, api)
- `requirements`: Requirements and constraints object

**Example:**
```json
{
  "component_name": "DataProcessor",
  "component_type": "class",
  "requirements": {
    "description": "Process and transform data",
    "methods": [
      {
        "name": "process",
        "parameters": [{"name": "data", "type": "Dict[str, Any]"}],
        "return_type": "Dict[str, Any]",
        "description": "Process the input data"
      }
    ],
    "constraints": [
      "Must handle empty input gracefully",
      "Must be thread-safe"
    ]
  }
}
```

### 2. validate_implementation
Validate code implementation against a contract.

**Parameters:**
- `contract_id`: ID of the contract to validate against
- `code`: Code to validate

### 3. record_error_pattern
Record an error pattern for future learning.

**Parameters:**
- `error_type`: Type of error
- `code_before`: Code before fix
- `code_after`: Code after fix
- `context`: Optional context information

### 4. get_fix_suggestions
Get fix suggestions based on historical error patterns.

**Parameters:**
- `error_type`: Type of error
- `current_code`: Current code with error

### 5. add_example
Add a code example to the library.

**Parameters:**
- `example_type`: Type of example
- `code`: Example code
- `description`: Description of the example
- `tags`: Optional tags for categorization

### 6. search_examples
Search the example library.

**Parameters:**
- `query`: Search query
- `example_type`: Optional type filter
- `tags`: Optional tag filter

### 7. list_contracts
List all generated contracts.

### 8. get_contract
Get details of a specific contract.

**Parameters:**
- `contract_id`: ID of the contract

## Available Prompts

### 1. contract_first_development
Guide for contract-first development workflow.

**Usage:** Provides a step-by-step workflow for developing components using the contract-first approach.

### 2. debug_validation_error
Guide for debugging validation errors.

**Usage:** Helps debug validation errors with specific steps and suggestions.

## Workflow Example

Here's a typical workflow using CIS Assistant:

1. **Generate a Contract**
   ```
   Use generate_contract to define your component specification
   ```

2. **Review the Contract**
   ```
   Use get_contract to review the generated specification
   ```

3. **Implement the Code**
   ```
   Write your implementation following the contract
   ```

4. **Validate the Implementation**
   ```
   Use validate_implementation to check compliance
   ```

5. **Fix Issues (if any)**
   ```
   Use get_fix_suggestions for guidance
   Record successful fixes with record_error_pattern
   ```

6. **Iterate Until Valid**
   ```
   Repeat validation and fixes until all checks pass
   ```

## Architecture

The CIS Assistant MCP server is built with:
- **MCP Protocol**: Standard protocol for AI-tool integration
- **Contract-First Design**: Formal specifications before implementation
- **Learning System**: Captures and reuses successful patterns
- **Example Library**: Searchable collection of proven solutions

## Development

### Project Structure
```
CIS-Assistant-/
├── src/
│   └── cis_assistant_mcp/
│       ├── __init__.py
│       └── server.py
├── pyproject.toml
├── README.md
└── CIS Assistant (original scaffold implementation)
```

### Running in Development Mode

```bash
# Install in editable mode
pip install -e .

# Run with verbose output
python -m cis_assistant_mcp.server
```

## Contributing

Contributions are welcome! Please ensure:
- Code follows the contract-first methodology
- All tools are properly documented
- Error patterns are well-defined
- Examples are clear and useful

## License

See repository license for details.

## Support

For issues and questions:
- Check the documentation in this README
- Use the `debug_validation_error` prompt for validation issues
- Review the example library with `search_examples`

## Background

This MCP server is based on the CIS (Circulatory Informatics System) code scaffold methodology, which emphasizes:
- Clear contracts before implementation
- Validation-driven development
- Learning from patterns
- Iterative refinement

The approach ensures high-quality, maintainable code by establishing clear specifications and continuously learning from development patterns.
