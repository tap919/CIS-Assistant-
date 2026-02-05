#!/usr/bin/env python3
"""
CIS Assistant MCP Server

This server provides tools for LLM-augmented code development using the
Circulatory Informatics System (CIS) methodology.

The server integrates the Circulatory Informatics Bible to maintain adherence
to CIS structure and provides aids for common LLM coding issues.
"""

import asyncio
import ast
import json
import uuid
import re
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
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
    - Circulatory Informatics methodology guidance
    - Common LLM coding issue aids
    
    Note: This implementation uses in-memory storage. All contracts, patterns,
    and examples will be lost when the server restarts. For production use,
    consider implementing persistent storage using files or a database.
    """
    
    # Constants for code truncation
    MAX_CODE_SNIPPET_LENGTH = 500
    MAX_BEFORE_AFTER_LENGTH = 200
    MAX_BIBLE_SECTION_LENGTH = 5000
    
    # Common LLM coding issues and their solutions
    LLM_CODING_AIDS = {
        "context_window_overflow": {
            "description": "LLM loses context with large codebases",
            "solutions": [
                "Break code into smaller, focused modules",
                "Use progressive context loading (start with interfaces, add details)",
                "Summarize distant context before providing detail",
                "Use adaptive token budgeting - prioritize most relevant context"
            ]
        },
        "hallucinated_imports": {
            "description": "LLM invents non-existent libraries or APIs",
            "solutions": [
                "Always verify imports exist before using them",
                "Provide explicit list of available dependencies",
                "Include actual import statements from working code as examples",
                "Cross-reference with requirements.txt or package.json"
            ]
        },
        "inconsistent_naming": {
            "description": "LLM uses inconsistent naming conventions across code",
            "solutions": [
                "Provide explicit naming convention rules upfront",
                "Include examples of correct naming in context",
                "Use constraint checklists that specify naming patterns",
                "Review generated code for naming consistency before execution"
            ]
        },
        "missing_error_handling": {
            "description": "LLM omits try/except blocks and edge case handling",
            "solutions": [
                "Explicitly require error handling in contracts",
                "Provide examples with comprehensive error handling",
                "Add validation rules that check for exception handling",
                "Include 'graceful degradation' as a behavioral constraint"
            ]
        },
        "type_hint_inconsistency": {
            "description": "LLM provides incomplete or incorrect type hints",
            "solutions": [
                "Enforce type hints through validation rules",
                "Provide type hint examples for complex types",
                "Use TypedDict and Protocol examples for clarity",
                "Validate with mypy or similar tools"
            ]
        },
        "incomplete_implementation": {
            "description": "LLM provides stub implementations or 'pass' statements",
            "solutions": [
                "Require complete implementations in constraints",
                "Validate that no 'pass' or 'TODO' remains",
                "Use progressive example complexity (simple → complete)",
                "Check for stub patterns in validation"
            ]
        },
        "security_vulnerabilities": {
            "description": "LLM generates code with common security issues",
            "solutions": [
                "Include security constraints in contracts",
                "Validate input sanitization and parameterized queries",
                "Check for hardcoded secrets patterns",
                "Require secure defaults in configuration"
            ]
        },
        "logic_drift": {
            "description": "LLM solution drifts from original intent over iterations",
            "solutions": [
                "Maintain explicit contract reference throughout",
                "Use checkpoints to preserve known-good states",
                "Re-state original requirements when iterating",
                "Compare current solution against initial constraints"
            ]
        }
    }
    
    # CIS Seven Principles for methodology adherence
    CIS_SEVEN_PRINCIPLES = {
        "distributed_autonomy": {
            "principle": "No single point of control. Each 'organ' operates autonomously within a decentralized governance framework.",
            "implication": "Services should make decisions without asking permission from a central authority. Use event-driven pub/sub patterns.",
            "code_pattern": "Decouple components, use message queues, avoid synchronous dependencies"
        },
        "continuous_sensing": {
            "principle": "The organism must continuously monitor its own state through events.",
            "implication": "Observability isn't optional—it's part of the organism's nervous system. Every event is a data point.",
            "code_pattern": "Add logging, metrics, and health checks to all components"
        },
        "feedback_driven_adaptation": {
            "principle": "Adaptation requires feedback loops that measure deviation and trigger corrective action.",
            "implication": "Self-healing and auto-remediation are baseline expectations, not optional features.",
            "code_pattern": "Implement retry logic, circuit breakers, and automatic recovery mechanisms"
        },
        "emergent_intelligence": {
            "principle": "Intelligence emerges from interaction of simple agents following local rules.",
            "implication": "Don't create one super-intelligent controller. Create multiple specialized agents that collaborate.",
            "code_pattern": "Design small, focused components that communicate through well-defined interfaces"
        },
        "memory_and_learning": {
            "principle": "The organism learns from past events and adjusts future behavior.",
            "implication": "Pattern analysis and learning from history aren't optional—they're how the system improves.",
            "code_pattern": "Record error patterns, track successful fixes, build adaptive example libraries"
        },
        "graceful_degradation": {
            "principle": "No single component is essential. The system continues functioning when components fail.",
            "implication": "Design for fault tolerance at every level. Failures should not cascade.",
            "code_pattern": "Use fallbacks, timeouts, and isolation patterns to prevent cascading failures"
        },
        "efficient_resource_flow": {
            "principle": "Resources flow to where they're needed. Demand drives allocation.",
            "implication": "Auto-scaling, load balancing, and resource optimization are structural requirements.",
            "code_pattern": "Implement resource pooling, lazy loading, and demand-based scaling"
        }
    }

    def __init__(self):
        self.server = Server("cis-assistant")
        self.contracts: Dict[str, Any] = {}
        self.error_patterns: Dict[str, List[Dict[str, Any]]] = {}
        self.examples: List[Dict[str, Any]] = []
        self.bible_content: str = self._load_bible_content()
        
        # Register handlers
        self._setup_handlers()
    
    def _load_bible_content(self) -> str:
        """Load the Circulatory Informatics Bible content"""
        # Try to find the Bible file relative to the package or from environment
        bible_env_path = os.environ.get("CIS_BIBLE_PATH")
        
        possible_paths = []
        if bible_env_path:
            possible_paths.append(Path(bible_env_path))
        
        possible_paths.extend([
            Path(__file__).parent.parent.parent.parent / "Bible",
            Path(__file__).parent.parent.parent / "Bible",
            Path.cwd() / "Bible",
        ])
        
        for bible_path in possible_paths:
            if bible_path.exists():
                try:
                    with open(bible_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except (IOError, OSError, FileNotFoundError):
                    # Continue to try other paths if this one fails
                    continue
        
        return ""
    
    def _extract_bible_section(self, section_name: str) -> str:
        """Extract a specific section from the Bible content"""
        if not self.bible_content:
            return "Bible content not available."
        
        # Define section markers and their content ranges
        sections = {
            "philosophy": ("PART I: PHILOSOPHICAL FOUNDATIONS", "PART II: SCIENTIFIC"),
            "seven_principles": ("2.1 The Seven Principles", "2.2 The Circulatory Metaphor"),
            "nine_systems": ("5. The Nine Systems", "PART III:"),
            "vibe_coding": ("3. How Living Code Achieves", "PART II:"),
            "scientific_foundations": ("PART II: SCIENTIFIC FOUNDATIONS", "PART III:"),
        }
        
        if section_name.lower() not in sections:
            return f"Section '{section_name}' not found. Available: {', '.join(sections.keys())}"
        
        start_marker, end_marker = sections[section_name.lower()]
        
        start_idx = self.bible_content.find(start_marker)
        end_idx = self.bible_content.find(end_marker, start_idx + len(start_marker))
        
        if start_idx == -1:
            return f"Section '{section_name}' not found in Bible content."
        
        if end_idx == -1:
            return self.bible_content[start_idx:][:self.MAX_BIBLE_SECTION_LENGTH]
        
        return self.bible_content[start_idx:end_idx][:self.MAX_BIBLE_SECTION_LENGTH]

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
                Tool(
                    name="get_cis_principles",
                    description="Get CIS (Circulatory Informatics System) principles and methodology guidelines for maintaining adherence to circulatory informatics structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "principle": {
                                "type": "string",
                                "description": "Specific principle to retrieve (optional). Options: distributed_autonomy, continuous_sensing, feedback_driven_adaptation, emergent_intelligence, memory_and_learning, graceful_degradation, efficient_resource_flow",
                                "enum": ["distributed_autonomy", "continuous_sensing", "feedback_driven_adaptation", "emergent_intelligence", "memory_and_learning", "graceful_degradation", "efficient_resource_flow"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_llm_coding_aid",
                    description="Get guidance for common LLM coding issues and their solutions",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "issue_type": {
                                "type": "string",
                                "description": "Type of LLM coding issue. Options: context_window_overflow, hallucinated_imports, inconsistent_naming, missing_error_handling, type_hint_inconsistency, incomplete_implementation, security_vulnerabilities, logic_drift",
                                "enum": ["context_window_overflow", "hallucinated_imports", "inconsistent_naming", "missing_error_handling", "type_hint_inconsistency", "incomplete_implementation", "security_vulnerabilities", "logic_drift"]
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_bible_section",
                    description="Get a section from the Circulatory Informatics Bible for methodology reference and adherence guidance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "section": {
                                "type": "string",
                                "description": "Section to retrieve. Options: philosophy, seven_principles, nine_systems, vibe_coding, scientific_foundations",
                                "enum": ["philosophy", "seven_principles", "nine_systems", "vibe_coding", "scientific_foundations"]
                            }
                        },
                        "required": ["section"]
                    }
                ),
                Tool(
                    name="check_cis_compliance",
                    description="Check if code or design adheres to CIS principles and get recommendations for improvement",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Code to check for CIS compliance"
                            },
                            "component_description": {
                                "type": "string",
                                "description": "Description of what the component does"
                            }
                        },
                        "required": ["code", "component_description"]
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
            elif name == "get_cis_principles":
                return await self._get_cis_principles(arguments)
            elif name == "get_llm_coding_aid":
                return await self._get_llm_coding_aid(arguments)
            elif name == "get_bible_section":
                return await self._get_bible_section(arguments)
            elif name == "check_cis_compliance":
                return await self._check_cis_compliance(arguments)
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
                Prompt(
                    name="cis_methodology_guide",
                    description="Guide for implementing code following Circulatory Informatics System principles",
                    arguments=[
                        PromptArgument(
                            name="focus_area",
                            description="Area to focus on: architecture, error_handling, observability, resilience",
                            required=False
                        )
                    ]
                ),
                Prompt(
                    name="llm_coding_best_practices",
                    description="Best practices for LLM-assisted code generation to avoid common issues",
                    arguments=[]
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
            elif name == "cis_methodology_guide":
                focus_area = arguments.get("focus_area", "general") if arguments else "general"
                return GetPromptResult(
                    description="Circulatory Informatics System methodology guide",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text=f"""# Circulatory Informatics System (CIS) Methodology Guide

## Focus Area: {focus_area.replace('_', ' ').title()}

## The Seven Principles of Living Code

### 1. Distributed Autonomy
**Principle:** No single point of control. Each 'organ' operates autonomously within a decentralized governance framework.
**Code Pattern:** Decouple components, use message queues, avoid synchronous dependencies.

### 2. Continuous Sensing
**Principle:** The organism must continuously monitor its own state through events.
**Code Pattern:** Add logging, metrics, and health checks to all components.

### 3. Feedback-Driven Adaptation
**Principle:** Adaptation requires feedback loops that measure deviation and trigger corrective action.
**Code Pattern:** Implement retry logic, circuit breakers, and automatic recovery mechanisms.

### 4. Emergent Intelligence
**Principle:** Intelligence emerges from interaction of simple agents following local rules.
**Code Pattern:** Design small, focused components that communicate through well-defined interfaces.

### 5. Memory and Learning
**Principle:** The organism learns from past events and adjusts future behavior.
**Code Pattern:** Record error patterns, track successful fixes, build adaptive example libraries.

### 6. Graceful Degradation
**Principle:** No single component is essential. The system continues functioning when components fail.
**Code Pattern:** Use fallbacks, timeouts, and isolation patterns to prevent cascading failures.

### 7. Efficient Resource Flow
**Principle:** Resources flow to where they're needed. Demand drives allocation.
**Code Pattern:** Implement resource pooling, lazy loading, and demand-based scaling.

## Implementation Checklist

When developing a component, ensure it follows these CIS principles:

- [ ] Component can operate independently (Distributed Autonomy)
- [ ] Component emits events/logs for monitoring (Continuous Sensing)
- [ ] Component handles failures and retries (Feedback-Driven Adaptation)
- [ ] Component has single responsibility (Emergent Intelligence)
- [ ] Component learns from errors (Memory and Learning)
- [ ] Component fails gracefully (Graceful Degradation)
- [ ] Component scales with demand (Efficient Resource Flow)

## Tools Available

Use these CIS Assistant tools to maintain methodology adherence:
- `get_cis_principles` - Get detailed principle guidance
- `check_cis_compliance` - Validate code against CIS principles
- `get_bible_section` - Access Circulatory Informatics Bible sections
- `get_llm_coding_aid` - Get help with common LLM coding issues"""
                            )
                        )
                    ]
                )
            elif name == "llm_coding_best_practices":
                return GetPromptResult(
                    description="Best practices for LLM-assisted code generation",
                    messages=[
                        PromptMessage(
                            role="user",
                            content=TextContent(
                                type="text",
                                text="""# LLM-Assisted Code Generation Best Practices

## Common Issues and Solutions

### 1. Context Window Overflow
**Problem:** LLM loses context with large codebases
**Solutions:**
- Break code into smaller, focused modules
- Use progressive context loading
- Summarize distant context before providing detail

### 2. Hallucinated Imports
**Problem:** LLM invents non-existent libraries or APIs
**Solutions:**
- Always verify imports exist before using them
- Provide explicit list of available dependencies
- Include actual import statements from working code

### 3. Inconsistent Naming
**Problem:** LLM uses inconsistent naming conventions
**Solutions:**
- Provide explicit naming convention rules upfront
- Include examples of correct naming in context
- Use constraint checklists that specify naming patterns

### 4. Missing Error Handling
**Problem:** LLM omits try/except blocks and edge case handling
**Solutions:**
- Explicitly require error handling in contracts
- Provide examples with comprehensive error handling
- Add validation rules that check for exception handling

### 5. Type Hint Inconsistency
**Problem:** LLM provides incomplete or incorrect type hints
**Solutions:**
- Enforce type hints through validation rules
- Provide type hint examples for complex types
- Validate with mypy or similar tools

### 6. Incomplete Implementation
**Problem:** LLM provides stub implementations or 'pass' statements
**Solutions:**
- Require complete implementations in constraints
- Validate that no 'pass' or 'TODO' remains
- Use progressive example complexity

### 7. Security Vulnerabilities
**Problem:** LLM generates code with common security issues
**Solutions:**
- Include security constraints in contracts
- Validate input sanitization
- Check for hardcoded secrets patterns

### 8. Logic Drift
**Problem:** LLM solution drifts from original intent over iterations
**Solutions:**
- Maintain explicit contract reference throughout
- Use checkpoints to preserve known-good states
- Re-state original requirements when iterating

## Tools Available

Use `get_llm_coding_aid` with a specific issue type for detailed guidance on any of these issues."""
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
        
        # Validate inputs
        if not self._validate_component_name(component_name):
            return [TextContent(
                type="text",
                text=f"Error: Invalid component name '{component_name}'. Must be a valid Python identifier."
            )]
        
        allowed_types = ["class", "function", "module", "service", "api"]
        if component_type not in allowed_types:
            return [TextContent(
                type="text",
                text=f"Error: Invalid component type '{component_type}'. Must be one of: {', '.join(allowed_types)}"
            )]
        
        if not isinstance(requirements, dict):
            return [TextContent(
                type="text",
                text="Error: Requirements must be a dictionary/object."
            )]
        
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        
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
            "id": f"pattern_{uuid.uuid4().hex[:8]}",
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
        
        # Increment usage count for patterns being shown
        suggestions = []
        for i, pattern in enumerate(sorted_patterns[:3], 1):
            # Increment usage count to track popularity (how often patterns are shown to users)
            # Note: In a production system, consider only incrementing when user confirms the fix was helpful
            pattern["usage_count"] += 1
            
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
            "id": f"example_{uuid.uuid4().hex[:8]}",
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

    async def _get_cis_principles(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get CIS principles and methodology guidelines"""
        principle = arguments.get("principle")
        
        if principle:
            if principle not in self.CIS_SEVEN_PRINCIPLES:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown principle '{principle}'. Available: {', '.join(self.CIS_SEVEN_PRINCIPLES.keys())}"
                )]
            
            p = self.CIS_SEVEN_PRINCIPLES[principle]
            result = f"""# CIS Principle: {principle.replace('_', ' ').title()}

## Principle
{p['principle']}

## Implication for Code
{p['implication']}

## Code Pattern
{p['code_pattern']}

## How to Apply

When implementing this principle:
1. Design components that follow the principle's guidance
2. Validate your implementation adheres to the code pattern
3. Use `check_cis_compliance` to verify your code
4. Refer to `get_bible_section` for deeper understanding"""
        else:
            principles_list = []
            for name, p in self.CIS_SEVEN_PRINCIPLES.items():
                principles_list.append(f"""
### {name.replace('_', ' ').title()}
**Principle:** {p['principle']}
**Code Pattern:** {p['code_pattern']}
""")
            
            result = f"""# The Seven Principles of CIS (Circulatory Informatics System)

These principles guide the design of living, adaptive software systems inspired by biological organisms.

{chr(10).join(principles_list)}

## Usage

Use `get_cis_principles` with a specific principle name for detailed guidance:
- `get_cis_principles(principle="distributed_autonomy")`
- `get_cis_principles(principle="graceful_degradation")`

Use `check_cis_compliance` to validate your code against these principles."""
        
        return [TextContent(type="text", text=result)]

    async def _get_llm_coding_aid(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get guidance for common LLM coding issues"""
        issue_type = arguments.get("issue_type")
        
        if issue_type:
            if issue_type not in self.LLM_CODING_AIDS:
                return [TextContent(
                    type="text",
                    text=f"Error: Unknown issue type '{issue_type}'. Available: {', '.join(self.LLM_CODING_AIDS.keys())}"
                )]
            
            aid = self.LLM_CODING_AIDS[issue_type]
            solutions_list = "\n".join([f"- {s}" for s in aid['solutions']])
            
            result = f"""# LLM Coding Aid: {issue_type.replace('_', ' ').title()}

## Problem Description
{aid['description']}

## Solutions
{solutions_list}

## Prevention Strategy

To prevent this issue in future code generation:
1. Include explicit constraints in your contracts
2. Provide working examples that demonstrate the correct approach
3. Use validation rules to catch violations
4. Record successful fixes with `record_error_pattern`

## Related CIS Principles

This issue relates to:
- **Memory and Learning**: Learn from past mistakes
- **Feedback-Driven Adaptation**: Use validation feedback to improve"""
        else:
            aids_list = []
            for name, aid in self.LLM_CODING_AIDS.items():
                aids_list.append(f"- **{name.replace('_', ' ').title()}**: {aid['description']}")
            
            result = f"""# LLM Coding Aids

Common issues encountered when using LLMs for code generation and their solutions.

## Available Aids

{chr(10).join(aids_list)}

## Usage

Get detailed guidance for a specific issue:
```
get_llm_coding_aid(issue_type="context_window_overflow")
get_llm_coding_aid(issue_type="hallucinated_imports")
```

## Integration with CIS

These aids integrate with the Circulatory Informatics System methodology:
- Use contracts to prevent issues upfront
- Validate implementations to catch issues
- Record patterns to learn from fixes"""
        
        return [TextContent(type="text", text=result)]

    async def _get_bible_section(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Get a section from the Circulatory Informatics Bible"""
        section = arguments.get("section")
        if section is None:
            return [TextContent(
                type="text",
                text="Error: missing required argument 'section' for Bible lookup."
            )]
        if not self.bible_content:
            return [TextContent(
                type="text",
                text="""# Circulatory Informatics Bible

The Bible file was not found. Please ensure the 'Bible' file is present in the repository root.

## Core Concepts (Summary)

The Circulatory Informatics System treats software as a living organism:

1. **Biological Metaphors**: Systems are organisms, not machines
2. **The Seven Principles**: Distributed autonomy, continuous sensing, feedback-driven adaptation, emergent intelligence, memory and learning, graceful degradation, efficient resource flow
3. **The Nine Systems**: Each maps to a biological system (Circulatory, Digestive, Nervous, etc.)
4. **Vibe Coding**: Code that feels right - elegant, purposeful, aesthetically coherent

Use `get_cis_principles` for detailed principle guidance."""
            )]
        
        section_content = self._extract_bible_section(section)
        
        result = f"""# Circulatory Informatics Bible: {section.replace('_', ' ').title()}

{section_content}

---

## Other Available Sections

- `philosophy` - Philosophical foundations
- `seven_principles` - The Seven Principles of Living Code
- `nine_systems` - The Nine Systems architecture
- `vibe_coding` - How Living Code Achieves Vibe Coding
- `scientific_foundations` - Scientific foundations and research

Use `get_bible_section(section="<name>")` to access other sections."""
        
        return [TextContent(type="text", text=result)]

    async def _check_cis_compliance(self, arguments: Dict[str, Any]) -> list[TextContent]:
        """Check code for CIS principle compliance"""
        code = arguments["code"]
        component_description = arguments["component_description"]
        
        compliance_checks = []
        recommendations = []
        
        # Check for Distributed Autonomy indicators
        has_event_patterns = any(pattern in code.lower() for pattern in 
                                 ['event', 'message', 'queue', 'publish', 'subscribe', 'async'])
        compliance_checks.append({
            "principle": "Distributed Autonomy",
            "passed": has_event_patterns,
            "detail": "Event-driven or async patterns found" if has_event_patterns else "Consider adding event-driven patterns for decoupling"
        })
        if not has_event_patterns:
            recommendations.append("Add event-driven patterns (async/await, message queues) for better decoupling")
        
        # Check for Continuous Sensing (logging, monitoring)
        has_observability = any(pattern in code.lower() for pattern in 
                                ['log', 'logger', 'metric', 'monitor', 'trace', 'debug', 'info'])
        compliance_checks.append({
            "principle": "Continuous Sensing",
            "passed": has_observability,
            "detail": "Logging/monitoring patterns found" if has_observability else "Add logging and monitoring for observability"
        })
        if not has_observability:
            recommendations.append("Add logging statements for monitoring and debugging")
        
        # Check for Feedback-Driven Adaptation (error handling, retry)
        has_error_handling = any(pattern in code.lower() for pattern in 
                                 ['try:', 'except', 'retry', 'fallback', 'recover'])
        compliance_checks.append({
            "principle": "Feedback-Driven Adaptation",
            "passed": has_error_handling,
            "detail": "Error handling patterns found" if has_error_handling else "Add try/except blocks and recovery mechanisms"
        })
        if not has_error_handling:
            recommendations.append("Add try/except blocks and implement retry/recovery logic")
        
        # Check for Graceful Degradation (fallbacks, timeouts)
        has_resilience = any(pattern in code.lower() for pattern in 
                            ['timeout', 'fallback', 'default_value', 'fallback_to', 'default_behavior', 'circuit', 'breaker', 'optional'])
        compliance_checks.append({
            "principle": "Graceful Degradation",
            "passed": has_resilience,
            "detail": "Resilience patterns found" if has_resilience else "Add fallback mechanisms and timeouts"
        })
        if not has_resilience:
            recommendations.append("Implement fallback mechanisms and timeouts for resilience")
        
        # Check for type hints (related to Emergent Intelligence - clear interfaces)
        # Use regex to detect function/method signatures with type hints
        type_hint_pattern = re.compile(r'def\s+\w+\s*\([^)]*:.*\)|def\s+\w+\s*\([^)]*\)\s*->')
        has_type_hints = bool(type_hint_pattern.search(code)) or 'typing' in code.lower()
        compliance_checks.append({
            "principle": "Emergent Intelligence (Clear Interfaces)",
            "passed": has_type_hints,
            "detail": "Type hints found" if has_type_hints else "Add type hints for clear interfaces"
        })
        if not has_type_hints:
            recommendations.append("Add type hints for clearer interfaces between components")
        
        # Calculate compliance score
        passed_count = sum(1 for c in compliance_checks if c['passed'])
        total_count = len(compliance_checks)
        compliance_score = (passed_count / total_count) * 100 if total_count > 0 else 0
        
        # Format results
        checks_output = []
        for check in compliance_checks:
            status = "✅" if check['passed'] else "❌"
            checks_output.append(f"{status} **{check['principle']}**: {check['detail']}")
        
        recommendations_output = "\n".join([f"- {r}" for r in recommendations]) if recommendations else "No recommendations - code follows CIS principles well!"
        
        result = f"""# CIS Compliance Check

## Component
{component_description}

## Compliance Score: {compliance_score:.0f}% ({passed_count}/{total_count} principles)

## Principle Checks

{chr(10).join(checks_output)}

## Recommendations

{recommendations_output}

## Next Steps

1. Address the recommendations above
2. Use `get_cis_principles` for detailed guidance on specific principles
3. Re-run `check_cis_compliance` after making changes
4. Use `get_llm_coding_aid` if you encounter implementation issues"""
        
        return [TextContent(type="text", text=result)]

    # Helper methods
    
    def _validate_component_name(self, name: str) -> bool:
        """Validate that component name is a valid Python identifier"""
        if not name or not isinstance(name, str):
            return False
        # Check if it's a valid Python identifier
        return name.isidentifier()
    
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
        """Validate code against contract using AST parsing for accuracy"""
        errors = []
        
        # Try to parse the code with AST
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            errors.append({
                "type": "syntax_error",
                "severity": "critical",
                "message": f"Syntax error in code: {str(e)}",
                "line": e.lineno if hasattr(e, 'lineno') else 0,
                "fix_suggestion": "Fix syntax errors in the code"
            })
            return {
                "passed": False,
                "errors": errors
            }
        
        # Find the component in the AST
        component_found = False
        component_has_docstring = False
        
        for node in ast.walk(tree):
            # Check for class or function definition matching the contract
            if contract["type"] == "class" and isinstance(node, ast.ClassDef):
                if node.name == contract["name"]:
                    component_found = True
                    # Check for class docstring
                    component_has_docstring = ast.get_docstring(node) is not None
                    
                    # For classes, check methods have type hints
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Check if method has return type annotation
                            # Skip dunder methods (special methods) as they commonly omit return annotations
                            is_dunder = item.name.startswith("__") and item.name.endswith("__")
                            if item.returns is None and not is_dunder:
                                errors.append({
                                    "type": "type_hint_missing",
                                    "severity": "high",
                                    "message": f"Method '{item.name}' missing return type annotation",
                                    "line": item.lineno,
                                    "fix_suggestion": f"Add return type annotation to method '{item.name}'"
                                })
                    
            elif contract["type"] == "function" and isinstance(node, ast.FunctionDef):
                if node.name == contract["name"]:
                    component_found = True
                    # Check for function docstring
                    component_has_docstring = ast.get_docstring(node) is not None
                    
                    # Check for return type annotation
                    if node.returns is None:
                        errors.append({
                            "type": "type_hint_missing",
                            "severity": "high",
                            "message": "Return type annotation missing",
                            "line": node.lineno,
                            "fix_suggestion": "Add return type annotation (-> ReturnType)"
                        })
        
        # Check if component was found
        if not component_found:
            errors.append({
                "type": "interface_violation",
                "severity": "critical",
                "message": f"Component '{contract['name']}' not found in implementation",
                "line": 0,
                "fix_suggestion": f"Ensure your code defines '{contract['name']}' as a {contract['type']}"
            })
        
        # Check for docstring
        if component_found and not component_has_docstring:
            errors.append({
                "type": "documentation_missing",
                "severity": "medium",
                "message": f"{contract['type'].capitalize()} '{contract['name']}' is missing a docstring",
                "line": 0,
                "fix_suggestion": f"Add a docstring to document the {contract['type']}"
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
