#!/usr/bin/env python3
"""
CIS Assistant MCP Server

This server provides tools for LLM-augmented code development using the
Circulatory Informatics System (CIS) methodology.
"""

import asyncio
import json
from typing import Any, Dict, List
from datetime import datetime

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    CallToolResult,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
)


class CISAssistantServer:
    """
    MCP Server for CIS Assistant
    
    Provides tools for:
    - Contract generation for software components
    - Code implementation with validation
    - Constraint checking
    - Adaptive example management
    - Error pattern analysis
    """
    
    # Constants for code truncation
    MAX_CODE_SNIPPET_LENGTH = 500
    MAX_BEFORE_AFTER_LENGTH = 200

    def __init__(self):
        self.server = Server("cis-assistant")
        self.contracts: Dict[str, Any] = {}
        self.implementations: Dict[str, Any] = {}
        self.error_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.examples: List[Dict[str, Any]] = []
        
        # Register handlers
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available CIS Assistant tools"""
            return [
                Tool(
                    name="generate_contract",
                    description="Generate a contract specification for a software component",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "component_name": {
                                "type": "string",
                                "description": "Name of the component to generate a contract for"
                            },
                            "component_type": {
                                "type": "string",
                                "description": "Type of component (e.g., 'class', 'function', 'module')",
                                "enum": ["class", "function", "module", "service", "api"]
                            },
                            "requirements": {
                                "type": "object",
                                "description": "Requirements and constraints for the component"
                            }
                        },
                        "required": ["component_name", "component_type", "requirements"]
                    }
                ),
                Tool(
                    name="validate_implementation",
                    description="Validate code implementation against a contract",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_id": {
                                "type": "string",
                                "description": "ID of the contract to validate against"
                            },
                            "code": {
                                "type": "string",
                                "description": "Code to validate"
                            }
                        },
                        "required": ["contract_id", "code"]
                    }
                ),
                Tool(
                    name="record_error_pattern",
                    description="Record an error pattern for future learning",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Type of error encountered"
                            },
                            "code_before": {
                                "type": "string",
                                "description": "Code before fix"
                            },
                            "code_after": {
                                "type": "string",
                                "description": "Code after fix"
                            },
                            "context": {
                                "type": "object",
                                "description": "Context information about the error"
                            }
                        },
                        "required": ["error_type", "code_before", "code_after"]
                    }
                ),
                Tool(
                    name="get_fix_suggestions",
                    description="Get fix suggestions based on historical error patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Type of error to get suggestions for"
                            },
                            "current_code": {
                                "type": "string",
                                "description": "Current code with error"
                            }
                        },
                        "required": ["error_type", "current_code"]
                    }
                ),
                Tool(
                    name="add_example",
                    description="Add a code example to the example library",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "example_type": {
                                "type": "string",
                                "description": "Type of example (e.g., 'pattern', 'implementation', 'test')"
                            },
                            "code": {
                                "type": "string",
                                "description": "Example code"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the example"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorization"
                            }
                        },
                        "required": ["example_type", "code", "description"]
                    }
                ),
                Tool(
                    name="search_examples",
                    description="Search the example library",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "example_type": {
                                "type": "string",
                                "description": "Optional filter by example type"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional filter by tags"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="list_contracts",
                    description="List all generated contracts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_contract",
                    description="Get details of a specific contract",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "contract_id": {
                                "type": "string",
                                "description": "ID of the contract to retrieve"
                            }
                        },
                        "required": ["contract_id"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            
            if name == "generate_contract":
                return await self._generate_contract(arguments)
            elif name == "validate_implementation":
                return await self._validate_implementation(arguments)
            elif name == "record_error_pattern":
                return await self._record_error_pattern(arguments)
            elif name == "get_fix_suggestions":
                return await self._get_fix_suggestions(arguments)
            elif name == "add_example":
                return await self._add_example(arguments)
            elif name == "search_examples":
                return await self._search_examples(arguments)
            elif name == "list_contracts":
                return await self._list_contracts(arguments)
            elif name == "get_contract":
                return await self._get_contract(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_prompts()
        async def list_prompts() -> list[Prompt]:
            """List available prompts"""
            return [
                Prompt(
                    name="contract_first_development",
                    description="Guide for contract-first development workflow",
                    arguments=[
                        PromptArgument(
                            name="component_type",
                            description="Type of component to develop",
                            required=True
                        )
                    ]
                ),
                Prompt(
                    name="debug_validation_error",
                    description="Guide for debugging validation errors",
                    arguments=[
                        PromptArgument(
                            name="error_message",
                            description="The validation error message",
                            required=True
                        )
                    ]
                ),
            ]

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
            """Get a specific prompt"""
            if name == "contract_first_development":
                component_type = arguments.get("component_type", "component") if arguments else "component"
                return GetPromptResult(
                    description=f"Contract-first development workflow for {component_type}",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Contract-First Development Workflow for {component_type}

## Step 1: Generate Contract
Use the `generate_contract` tool to create a formal specification:
- Define clear input/output interfaces
- Specify constraints and validation rules
- Document expected behavior

## Step 2: Review Contract
Ensure the contract captures all requirements:
- Check completeness of interface definitions
- Verify constraints are explicit
- Confirm validation criteria are clear

## Step 3: Implement Code
Write code that satisfies the contract:
- Follow the interface specification
- Respect all constraints
- Handle edge cases

## Step 4: Validate Implementation
Use `validate_implementation` tool to check compliance:
- Verify interface conformance
- Check constraint satisfaction
- Review validation results

## Step 5: Iterate if Needed
If validation fails:
- Use `get_fix_suggestions` for guidance
- Record successful fixes with `record_error_pattern`
- Re-validate until all checks pass

This workflow ensures high-quality, maintainable code by establishing clear contracts before implementation."""
                            )
                        )
                    ]
                )
            elif name == "debug_validation_error":
                error_message = arguments.get("error_message", "") if arguments else ""
                return GetPromptResult(
                    description="Guide for debugging validation errors",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Debugging Validation Error

## Error Message
{error_message}

## Debugging Steps

1. **Understand the Error**
   - Read the error message carefully
   - Identify the specific contract violation
   - Locate the problematic code section

2. **Search for Similar Patterns**
   Use `get_fix_suggestions` with the error type to find:
   - Historical fixes for similar errors
   - Common patterns and solutions
   - Context-specific guidance

3. **Apply the Fix**
   - Make minimal changes to address the error
   - Maintain code consistency
   - Preserve all other constraints

4. **Re-validate**
   - Use `validate_implementation` again
   - Ensure the fix doesn't introduce new errors
   - Verify all constraints are satisfied

5. **Record Success**
   Once fixed, use `record_error_pattern` to:
   - Document the fix for future reference
   - Help others with similar issues
   - Improve the system's learning

## Tips
- Start with the most specific error first
- Check for type mismatches and missing imports
- Verify all required methods/properties are present
- Ensure naming conventions are followed"""
                            )
                        )
                    ]
                )
            else:
                raise ValueError(f"Unknown prompt: {name}")

    async def _generate_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Generate a contract specification"""
        component_name = arguments["component_name"]
        component_type = arguments["component_type"]
        requirements = arguments["requirements"]
        
        contract_id = f"contract_{len(self.contracts) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        contract = {
            "id": contract_id,
            "name": component_name,
            "type": component_type,
            "requirements": requirements,
            "generated_at": datetime.now().isoformat(),
            "interface": self._generate_interface(component_name, component_type, requirements),
            "constraints": self._extract_constraints(requirements),
            "validation_rules": self._generate_validation_rules(requirements)
        }
        
        self.contracts[contract_id] = contract
        
        result = f"""# Contract Generated: {component_name}

**Contract ID:** {contract_id}
**Type:** {component_type}
**Generated:** {contract["generated_at"]}

## Interface Definition
```python
{contract["interface"]}
```

## Constraints
{self._format_constraints(contract["constraints"])}

## Validation Rules
{self._format_validation_rules(contract["validation_rules"])}

## Next Steps
1. Review the contract to ensure it captures all requirements
2. Use this contract_id ({contract_id}) when implementing
3. Validate your implementation with `validate_implementation` tool

The contract has been saved and can be retrieved using `get_contract` tool."""
        
        return [TextContent(type="text", text=result)]

    async def _validate_implementation(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Validate code implementation against contract"""
        contract_id = arguments["contract_id"]
        code = arguments["code"]
        
        if contract_id not in self.contracts:
            return [TextContent(
                type="text",
                text=f"Error: Contract {contract_id} not found. Use `list_contracts` to see available contracts."
            )]
        
        contract = self.contracts[contract_id]
        validation_results = self._validate_code(code, contract)
        
        if validation_results["passed"]:
            result = f"""# ✓ Validation PASSED

**Contract:** {contract["name"]} ({contract_id})
**Implementation Status:** Valid

All checks passed:
- Interface compliance: ✓
- Constraint satisfaction: ✓
- Type correctness: ✓

The implementation satisfies all contract requirements."""
        else:
            errors = validation_results["errors"]
            result = f"""# ✗ Validation FAILED

**Contract:** {contract["name"]} ({contract_id})
**Errors Found:** {len(errors)}

## Issues to Fix:

{self._format_validation_errors(errors)}

## Recommended Actions:
1. Fix the errors listed above
2. Use `get_fix_suggestions` for guidance on similar errors
3. Re-validate after making changes

## Tips:
- Address errors in order of severity
- Check the contract interface for expected signatures
- Verify all constraints are met"""
        
        return [TextContent(type="text", text=result)]

    async def _record_error_pattern(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Record an error pattern for learning"""
        error_type = arguments["error_type"]
        code_before = arguments["code_before"]
        code_after = arguments["code_after"]
        context = arguments.get("context", {})
        
        if error_type not in self.error_patterns:
            self.error_patterns[error_type] = []
        
        pattern = {
            "id": f"pattern_{len(self.error_patterns[error_type]) + 1}",
            "error_type": error_type,
            "code_before": code_before,
            "code_after": code_after,
            "context": context,
            "recorded_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.error_patterns[error_type].append(pattern)
        
        result = f"""# Error Pattern Recorded

**Pattern ID:** {pattern["id"]}
**Error Type:** {error_type}
**Recorded:** {pattern["recorded_at"]}

The fix pattern has been saved and will be used to provide suggestions for similar errors in the future.

**Total patterns for {error_type}:** {len(self.error_patterns[error_type])}

You can retrieve this pattern using `get_fix_suggestions` tool when encountering similar errors."""
        
        return [TextContent(type="text", text=result)]

    async def _get_fix_suggestions(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get fix suggestions based on error patterns"""
        error_type = arguments["error_type"]
        
        patterns = self.error_patterns.get(error_type, [])
        
        if not patterns:
            return [TextContent(
                type="text",
                text=f"""# No Historical Patterns Found

**Error Type:** {error_type}

No previous fixes have been recorded for this error type yet.

**Suggestions:**
1. Carefully review the error message
2. Check the contract specification
3. Look for similar patterns in the codebase
4. Once you fix it, use `record_error_pattern` to help future similar issues"""
            )]
        
        # Sort by usage count (most successful patterns first)
        sorted_patterns = sorted(patterns, key=lambda p: p["usage_count"], reverse=True)
        
        suggestions = []
        for i, pattern in enumerate(sorted_patterns[:3], 1):
            before_code = self._smart_truncate(pattern["code_before"], self.MAX_BEFORE_AFTER_LENGTH)
            after_code = self._smart_truncate(pattern["code_after"], self.MAX_BEFORE_AFTER_LENGTH)
            
            suggestions.append(f"""
## Fix Pattern #{i} (Used {pattern["usage_count"]} times)

**Pattern ID:** {pattern["id"]}

### Before:
```python
{before_code}
```

### After:
```python
{after_code}
```

**Context:** {json.dumps(pattern.get("context", {}), indent=2)}
""")
        
        result = f"""# Fix Suggestions for {error_type}

**Found {len(patterns)} historical fix patterns**
**Showing top {min(3, len(patterns))} most successful fixes**

{chr(10).join(suggestions)}

## How to Apply:
1. Review the patterns above
2. Identify which one best matches your situation
3. Apply similar changes to your code
4. Validate the fix
5. Record your successful fix with `record_error_pattern`"""
        
        return [TextContent(type="text", text=result)]

    async def _add_example(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Add an example to the library"""
        example_type = arguments["example_type"]
        code = arguments["code"]
        description = arguments["description"]
        tags = arguments.get("tags", [])
        
        example = {
            "id": f"example_{len(self.examples) + 1}",
            "type": example_type,
            "code": code,
            "description": description,
            "tags": tags,
            "added_at": datetime.now().isoformat()
        }
        
        self.examples.append(example)
        
        result = f"""# Example Added to Library

**Example ID:** {example["id"]}
**Type:** {example_type}
**Tags:** {', '.join(tags) if tags else 'None'}

The example has been saved and can be found using the `search_examples` tool.

**Total examples in library:** {len(self.examples)}"""
        
        return [TextContent(type="text", text=result)]

    async def _search_examples(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Search the example library"""
        query = arguments["query"].lower()
        example_type = arguments.get("example_type")
        tags = arguments.get("tags", [])
        
        matching_examples = []
        
        for example in self.examples:
            # Check type filter
            if example_type and example["type"] != example_type:
                continue
            
            # Check tags filter
            if tags and not any(tag in example["tags"] for tag in tags):
                continue
            
            # Check query match
            if (query in example["description"].lower() or 
                query in example["code"].lower() or
                any(query in tag.lower() for tag in example["tags"])):
                matching_examples.append(example)
        
        if not matching_examples:
            return [TextContent(
                type="text",
                text=f"""# No Examples Found

**Query:** {query}
**Type Filter:** {example_type or 'None'}
**Tag Filter:** {', '.join(tags) if tags else 'None'}

No examples match your search criteria. Try:
- Broader search terms
- Removing filters
- Adding examples with `add_example` tool"""
            )]
        
        results = []
        for example in matching_examples[:5]:  # Limit to top 5
            code_snippet = self._smart_truncate(example["code"], self.MAX_CODE_SNIPPET_LENGTH)
            
            results.append(f"""
## {example["id"]} - {example["type"]}

**Description:** {example["description"]}
**Tags:** {', '.join(example["tags"])}
**Added:** {example["added_at"]}

```python
{code_snippet}
```
""")
        
        result = f"""# Search Results

**Found {len(matching_examples)} matching examples**
**Showing top {min(5, len(matching_examples))}**

{chr(10).join(results)}"""
        
        return [TextContent(type="text", text=result)]

    async def _list_contracts(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """List all contracts"""
        if not self.contracts:
            return [TextContent(
                type="text",
                text="# No Contracts Available\n\nNo contracts have been generated yet. Use `generate_contract` tool to create one."
            )]
        
        contract_list = []
        for contract_id, contract in self.contracts.items():
            contract_list.append(f"""
- **{contract_id}**
  - Name: {contract["name"]}
  - Type: {contract["type"]}
  - Generated: {contract["generated_at"]}
""")
        
        result = f"""# Available Contracts

**Total Contracts:** {len(self.contracts)}

{chr(10).join(contract_list)}

Use `get_contract` with a contract ID to see full details."""
        
        return [TextContent(type="text", text=result)]

    async def _get_contract(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get a specific contract"""
        contract_id = arguments["contract_id"]
        
        if contract_id not in self.contracts:
            return [TextContent(
                type="text",
                text=f"Error: Contract {contract_id} not found. Use `list_contracts` to see available contracts."
            )]
        
        contract = self.contracts[contract_id]
        
        result = f"""# Contract Details: {contract["name"]}

**Contract ID:** {contract_id}
**Type:** {contract["type"]}
**Generated:** {contract["generated_at"]}

## Interface Definition
```python
{contract["interface"]}
```

## Constraints
{self._format_constraints(contract["constraints"])}

## Validation Rules
{self._format_validation_rules(contract["validation_rules"])}

## Requirements
```json
{json.dumps(contract["requirements"], indent=2)}
```"""
        
        return [TextContent(type="text", text=result)]

    # Helper methods
    
    def _generate_interface(self, name: str, component_type: str, requirements: Dict[str, Any]) -> str:
        """Generate interface code based on component type"""
        if component_type == "class":
            methods = requirements.get("methods", [])
            properties = requirements.get("properties", [])
            
            interface = f"class {name}:\n"
            interface += '    """' + requirements.get("description", f"{name} class") + '"""\n\n'
            
            if properties:
                interface += "    def __init__(self):\n"
                for prop in properties:
                    interface += f"        self.{prop}: Any = None\n"
                interface += "\n"
            
            for method in methods:
                params = method.get("parameters", [])
                param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in params])
                return_type = method.get("return_type", "None")
                interface += f"    def {method['name']}(self, {param_str}) -> {return_type}:\n"
                interface += f'        """{method.get("description", "")}"""\n'
                interface += "        pass\n\n"
            
            return interface
            
        elif component_type == "function":
            params = requirements.get("parameters", [])
            param_str = ", ".join([f"{p['name']}: {p.get('type', 'Any')}" for p in params])
            return_type = requirements.get("return_type", "None")
            
            interface = f"def {name}({param_str}) -> {return_type}:\n"
            interface += '    """' + requirements.get("description", f"{name} function") + '"""\n'
            interface += "    pass\n"
            
            return interface
        
        else:
            return f"# {component_type}: {name}\n# Interface to be defined based on requirements"

    def _extract_constraints(self, requirements: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract constraints from requirements"""
        constraints = {
            "type_constraints": [],
            "validation_constraints": [],
            "behavioral_constraints": []
        }
        
        if "constraints" in requirements:
            for constraint in requirements["constraints"]:
                if isinstance(constraint, dict):
                    category = constraint.get("category", "behavioral_constraints")
                    constraints[category].append(constraint.get("rule", str(constraint)))
                else:
                    constraints["behavioral_constraints"].append(str(constraint))
        
        return constraints

    def _generate_validation_rules(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate validation rules"""
        rules = []
        
        # Add interface validation
        rules.append({
            "type": "interface_check",
            "description": "Verify all required methods/functions are present",
            "severity": "critical"
        })
        
        # Add type validation
        rules.append({
            "type": "type_check",
            "description": "Verify type hints match specification",
            "severity": "high"
        })
        
        # Add constraint validation
        if "constraints" in requirements:
            rules.append({
                "type": "constraint_check",
                "description": "Verify all constraints are satisfied",
                "severity": "critical"
            })
        
        return rules

    def _format_constraints(self, constraints: Dict[str, List[str]]) -> str:
        """Format constraints for display"""
        if not any(constraints.values()):
            return "No specific constraints defined."
        
        formatted = []
        for category, rules in constraints.items():
            if rules:
                formatted.append(f"\n### {category.replace('_', ' ').title()}")
                for i, rule in enumerate(rules, 1):
                    formatted.append(f"{i}. {rule}")
        
        return "\n".join(formatted)

    def _format_validation_rules(self, rules: List[Dict[str, Any]]) -> str:
        """Format validation rules for display"""
        if not rules:
            return "No validation rules defined."
        
        formatted = []
        for i, rule in enumerate(rules, 1):
            severity = rule.get("severity", "medium")
            formatted.append(f"{i}. **{rule['type']}** ({severity})")
            formatted.append(f"   {rule['description']}")
        
        return "\n".join(formatted)

    def _validate_code(self, code: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code against contract (simplified validation)"""
        errors = []
        
        # Check if code contains the expected component name
        if contract["name"] not in code:
            errors.append({
                "type": "interface_violation",
                "severity": "critical",
                "message": f"Component '{contract['name']}' not found in implementation",
                "line": 0,
                "fix_suggestion": f"Ensure your code defines '{contract['name']}'"
            })
        
        # Check for type hints (simple check)
        if contract["type"] == "function" and "def " in code:
            if "->" not in code:
                errors.append({
                    "type": "type_hint_missing",
                    "severity": "high",
                    "message": "Return type annotation missing",
                    "line": 0,
                    "fix_suggestion": "Add return type annotation (-> ReturnType)"
                })
        
        # Check for docstrings
        if '"""' not in code and "'''" not in code:
            errors.append({
                "type": "documentation_missing",
                "severity": "medium",
                "message": "Docstring missing",
                "line": 0,
                "fix_suggestion": "Add docstring to document the component"
            })
        
        return {
            "passed": len(errors) == 0,
            "errors": errors
        }

    def _format_validation_errors(self, errors: List[Dict[str, Any]]) -> str:
        """Format validation errors for display"""
        formatted = []
        
        for i, error in enumerate(errors, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢"
            }.get(error.get("severity", "medium"), "⚪")
            
            formatted.append(f"\n### {severity_emoji} Error {i}: {error['type']}")
            formatted.append(f"**Message:** {error['message']}")
            if error.get("line"):
                formatted.append(f"**Line:** {error['line']}")
            if error.get("fix_suggestion"):
                formatted.append(f"**Fix:** {error['fix_suggestion']}")
        
        return "\n".join(formatted)
    
    def _smart_truncate(self, code: str, max_length: int) -> str:
        """Truncate code intelligently at line boundaries"""
        if len(code) <= max_length:
            return code
        
        lines = code.split('\n')
        truncated_lines = []
        current_length = 0
        
        for line in lines:
            if current_length + len(line) + 1 > max_length:
                break
            truncated_lines.append(line)
            current_length += len(line) + 1
        
        if truncated_lines:
            return '\n'.join(truncated_lines) + '\n# ... (truncated)'
        else:
            # If first line is too long, truncate at max_length
            return code[:max_length] + '\n# ... (truncated)'

    async def run(self):
        """Run the MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    server = CISAssistantServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
