# CIS Assistant MCP Server

A Model Context Protocol (MCP) server that provides intelligent code development assistance using the Circulatory Informatics System (CIS) methodology, enhanced with blockchain automation for the Base layer 2 platform — bridging supply chain management, blockchain technology, and small business adoption.

## Overview

CIS Assistant is an MCP server that enables AI applications (like Claude) to:
- Generate formal contract specifications for software components
- Validate code implementations against contracts
- Learn from error patterns to provide better suggestions
- Manage a library of code examples
- Guide developers through contract-first development
- **Access the Circulatory Informatics Bible for methodology adherence**
- **Get guidance on common LLM coding issues**
- **Check code for CIS principle compliance**
- **Automate blockchain development on Base L2**
- **Generate supply chain smart contracts (Solidity)**
- **Onboard small businesses to blockchain technology**
- **Validate smart contracts for security and best practices**

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

### 📖 Circulatory Informatics Bible Integration
- Access Bible sections for methodology guidance
- Seven Principles of Living Code reference
- Nine Systems architecture patterns

### 🔧 LLM Coding Aids
- Solutions for common LLM coding issues
- Guidance for context window overflow, hallucinated imports, etc.
- Best practices for LLM-assisted development

### 📊 CIS Compliance Checking
- Validate code against CIS principles
- Get recommendations for improvement
- Compliance scoring

### ⛓️ Base L2 Blockchain Automation
- Base mainnet and Sepolia testnet configuration
- Network details, RPC endpoints, and deployment guides
- Gas cost estimates and optimization tips

### 📦 Supply Chain Smart Contracts
- Product tracking with provenance verification
- Supplier registry with reputation system
- Invoice management with on-chain payments
- Certification NFTs for compliance verification

### 🏪 Small Business Onboarding
- Step-by-step blockchain adoption guides
- Cost analysis (< $0.01 per transaction on Base)
- Industry-specific use case recommendations
- Integration guides for existing business systems

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

### 9. get_cis_principles
Get CIS (Circulatory Informatics System) principles and methodology guidelines for maintaining adherence to circulatory informatics structure.

**Parameters:**
- `principle` (optional): Specific principle to retrieve. Options: `distributed_autonomy`, `continuous_sensing`, `feedback_driven_adaptation`, `emergent_intelligence`, `memory_and_learning`, `graceful_degradation`, `efficient_resource_flow`

**Example:**
```json
{
  "principle": "graceful_degradation"
}
```

### 10. get_llm_coding_aid
Get guidance for common LLM coding issues and their solutions.

**Parameters:**
- `issue_type` (optional): Type of LLM coding issue. Options: `context_window_overflow`, `hallucinated_imports`, `inconsistent_naming`, `missing_error_handling`, `type_hint_inconsistency`, `incomplete_implementation`, `security_vulnerabilities`, `logic_drift`

**Example:**
```json
{
  "issue_type": "hallucinated_imports"
}
```

### 11. get_bible_section
Get a section from the Circulatory Informatics Bible for methodology reference and adherence guidance.

**Parameters:**
- `section`: Section to retrieve. Options: `philosophy`, `seven_principles`, `nine_systems`, `vibe_coding`, `scientific_foundations`

**Example:**
```json
{
  "section": "seven_principles"
}
```

### 12. check_cis_compliance
Check if code or design adheres to CIS principles and get recommendations for improvement.

**Parameters:**
- `code`: Code to check for CIS compliance
- `component_description`: Description of what the component does

**Example:**
```json
{
  "code": "class DataProcessor:\n    def process(self, data):\n        return data",
  "component_description": "A data processing class"
}
```

### 13. get_base_network_info
Get Base L2 network configuration, endpoints, and details for blockchain development.

**Parameters:**
- `network` (optional): Network to query — `mainnet` or `sepolia`

**Example:**
```json
{
  "network": "mainnet"
}
```

### 14. generate_supply_chain_contract
Generate a Solidity smart contract template for supply chain use cases on Base L2.

**Parameters:**
- `template_type`: Type of contract — `product_tracking`, `supplier_registry`, `invoice_management`, `certification_nft`
- `business_name` (optional): Name of the business

**Example:**
```json
{
  "template_type": "product_tracking",
  "business_name": "FreshFarm Foods"
}
```

### 15. get_supply_chain_templates
List all available supply chain smart contract templates with descriptions and use cases.

### 16. get_business_onboarding_guide
Get step-by-step guidance for small businesses to adopt blockchain technology on Base L2.

**Parameters:**
- `guide_section` (optional): Section — `getting_started`, `cost_analysis`, `use_case_guide`, `integration_guide`
- `business_type` (optional): Business type for tailored recommendations — `retail`, `food_beverage`, `manufacturing`, `services`, `wholesale_distribution`

**Example:**
```json
{
  "guide_section": "use_case_guide",
  "business_type": "retail"
}
```

### 17. validate_smart_contract
Validate Solidity smart contract code for security patterns, common issues, and Base L2 compatibility.

**Parameters:**
- `code`: Solidity smart contract code to validate
- `contract_type` (optional): Type for context-aware validation — `product_tracking`, `supplier_registry`, `invoice_management`, `certification_nft`, `custom`

**Example:**
```json
{
  "code": "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.19;\ncontract Test { ... }",
  "contract_type": "product_tracking"
}
```

## Available Prompts

### 1. contract_first_development
Guide for contract-first development workflow.

**Usage:** Provides a step-by-step workflow for developing components using the contract-first approach.

### 2. debug_validation_error
Guide for debugging validation errors.

**Usage:** Helps debug validation errors with specific steps and suggestions.

### 3. cis_methodology_guide
Guide for implementing code following Circulatory Informatics System principles.

**Usage:** Provides comprehensive guidance on the Seven Principles of Living Code and how to apply them in your implementations.

**Arguments:**
- `focus_area` (optional): Area to focus on - `architecture`, `error_handling`, `observability`, `resilience`

### 4. llm_coding_best_practices
Best practices for LLM-assisted code generation to avoid common issues.

**Usage:** Provides a comprehensive guide to common LLM coding issues and their solutions.

### 5. blockchain_supply_chain_setup
Step-by-step workflow for setting up supply chain tracking on Base L2 blockchain.

**Arguments:**
- `business_type` (optional): Type of business — `retail`, `food_beverage`, `manufacturing`, `services`, `wholesale_distribution`

**Usage:** Guides you through choosing contracts, deploying to Base, and integrating with your business.

### 6. small_business_onboarding
Complete guide for small businesses to adopt blockchain technology on Base L2.

**Arguments:**
- `focus_area` (optional): Area to focus on — `getting_started`, `cost_analysis`, `integration`, `all`

**Usage:** Comprehensive onboarding covering wallet setup, costs, use cases, and integration.

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
- **Base L2 Blockchain**: Supply chain smart contract generation, validation, and deployment guidance
- **Small Business Focus**: Onboarding guides, cost analysis, and industry-specific recommendations

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

This MCP server is based on the CIS (Circulatory Informatics System) code scaffold methodology, enhanced with blockchain automation for the Base layer 2 platform. It serves as a critical business tool bridging:
- **Supply Chain Management**: Transparent, immutable tracking of goods and services
- **Blockchain Technology**: Low-cost, fast transactions on Base L2 (Ethereum Layer 2)
- **Small Business Adoption**: Making blockchain accessible and affordable for businesses of all sizes

The approach ensures high-quality, maintainable code by establishing clear specifications, continuously learning from development patterns, and providing production-ready smart contract templates for supply chain solutions.
