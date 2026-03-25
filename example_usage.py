#!/usr/bin/env python3
"""
Example usage of CIS Assistant MCP Server

This script demonstrates how to interact with the CIS Assistant server
programmatically (for testing purposes).
"""

import asyncio
from cis_assistant_mcp.server import CISAssistantServer


async def demo():
    """Demonstrate CIS Assistant capabilities"""
    
    print("=" * 60)
    print("CIS ASSISTANT MCP SERVER - DEMONSTRATION")
    print("=" * 60)
    print()
    
    server = CISAssistantServer()
    
    # Example 1: Generate a contract
    print("1. Generating a contract for a DataProcessor class...")
    print("-" * 60)
    
    contract_args = {
        "component_name": "DataProcessor",
        "component_type": "class",
        "requirements": {
            "description": "A class for processing and transforming data",
            "methods": [
                {
                    "name": "process",
                    "parameters": [
                        {"name": "data", "type": "Dict[str, Any]"}
                    ],
                    "return_type": "Dict[str, Any]",
                    "description": "Process the input data and return transformed result"
                },
                {
                    "name": "validate",
                    "parameters": [
                        {"name": "data", "type": "Dict[str, Any]"}
                    ],
                    "return_type": "bool",
                    "description": "Validate input data before processing"
                }
            ],
            "properties": ["config", "state"],
            "constraints": [
                "Must handle empty input gracefully",
                "Must be thread-safe",
                "Must log all operations"
            ]
        }
    }
    
    result = await server._generate_contract(contract_args)
    print(result[0].text)
    print()
    
    # Get the contract ID from the result
    contract_id = list(server.contracts.keys())[0]
    
    # Example 2: Validate an implementation (incorrect)
    print("\n2. Validating an INCORRECT implementation...")
    print("-" * 60)
    
    bad_code = """
class DataProcessor:
    def process(self, data):
        return data
"""
    
    validation_args = {
        "contract_id": contract_id,
        "code": bad_code
    }
    
    result = await server._validate_implementation(validation_args)
    print(result[0].text)
    print()
    
    # Example 3: Validate a correct implementation
    print("\n3. Validating a CORRECT implementation...")
    print("-" * 60)
    
    good_code = '''
class DataProcessor:
    """A class for processing and transforming data"""
    
    def __init__(self):
        self.config = {}
        self.state = {}
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the input data and return transformed result"""
        if not data:
            return {}
        return {"processed": True, "data": data}
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """Validate input data before processing"""
        return isinstance(data, dict)
'''
    
    validation_args = {
        "contract_id": contract_id,
        "code": good_code
    }
    
    result = await server._validate_implementation(validation_args)
    print(result[0].text)
    print()
    
    # Example 4: Record an error pattern
    print("\n4. Recording an error pattern...")
    print("-" * 60)
    
    error_pattern_args = {
        "error_type": "missing_type_hints",
        "code_before": "def process(self, data):",
        "code_after": "def process(self, data: Dict[str, Any]) -> Dict[str, Any]:",
        "context": {
            "component_type": "method",
            "fix_type": "add_type_annotations"
        }
    }
    
    result = await server._record_error_pattern(error_pattern_args)
    print(result[0].text)
    print()
    
    # Example 5: Get fix suggestions
    print("\n5. Getting fix suggestions for similar error...")
    print("-" * 60)
    
    fix_args = {
        "error_type": "missing_type_hints",
        "current_code": "def validate(self, input): return True"
    }
    
    result = await server._get_fix_suggestions(fix_args)
    print(result[0].text)
    print()
    
    # Example 6: Add an example
    print("\n6. Adding a code example to library...")
    print("-" * 60)
    
    example_args = {
        "example_type": "pattern",
        "code": """
def validate_dict(data: Dict[str, Any]) -> bool:
    '''Validate that input is a non-empty dictionary'''
    return isinstance(data, dict) and len(data) > 0
""",
        "description": "Example of input validation pattern",
        "tags": ["validation", "type-checking", "pattern"]
    }
    
    result = await server._add_example(example_args)
    print(result[0].text)
    print()
    
    # Example 7: Search examples
    print("\n7. Searching examples for 'validation'...")
    print("-" * 60)
    
    search_args = {
        "query": "validation",
        "tags": ["validation"]
    }
    
    result = await server._search_examples(search_args)
    print(result[0].text)
    print()
    
    # Example 8: List all contracts
    print("\n8. Listing all contracts...")
    print("-" * 60)
    
    result = await server._list_contracts({})
    print(result[0].text)
    print()
    
    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print()
    print("The CIS Assistant MCP server is ready to use!")
    print("Run with: python -m cis_assistant_mcp.server")
    print()

    print()
    print("=" * 60)
    print("BLOCKCHAIN SUPPLY CHAIN FEATURES - DEMONSTRATION")
    print("=" * 60)
    print()

    # Example 9: Get Base network info
    print("9. Getting Base L2 network information...")
    print("-" * 60)

    result = await server._get_base_network_info({"network": "mainnet"})
    print(result[0].text)
    print()

    # Example 10: Browse supply chain templates
    print("\n10. Browsing supply chain smart contract templates...")
    print("-" * 60)

    result = await server._get_supply_chain_templates({})
    print(result[0].text)
    print()

    # Example 11: Generate a supply chain contract
    print("\n11. Generating a Product Tracking smart contract...")
    print("-" * 60)

    result = await server._generate_supply_chain_contract({
        "template_type": "product_tracking",
        "business_name": "FreshFarm Foods"
    })
    print(result[0].text)
    print()

    # Example 12: Validate a smart contract
    print("\n12. Validating a smart contract for security issues...")
    print("-" * 60)

    sample_contract = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract SimpleTracker {
    address public owner;
    mapping(uint256 => string) public items;
    uint256 public itemCount;

    event ItemAdded(uint256 indexed id, string name);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not contract owner");
        _;
    }

    function addItem(string memory _name) external onlyOwner {
        require(bytes(_name).length > 0, "Name required");
        itemCount++;
        items[itemCount] = _name;
        emit ItemAdded(itemCount, _name);
    }
}"""

    result = await server._validate_smart_contract({
        "code": sample_contract,
        "contract_type": "product_tracking"
    })
    print(result[0].text)
    print()

    # Example 13: Get business onboarding guide
    print("\n13. Getting small business onboarding guide for retail...")
    print("-" * 60)

    result = await server._get_business_onboarding_guide({
        "guide_section": "use_case_guide",
        "business_type": "retail"
    })
    print(result[0].text)
    print()

    # Example 14: Get cost analysis
    print("\n14. Getting blockchain cost analysis...")
    print("-" * 60)

    result = await server._get_business_onboarding_guide({
        "guide_section": "cost_analysis"
    })
    print(result[0].text)
    print()

    print("=" * 60)
    print("FULL DEMONSTRATION COMPLETE")
    print("=" * 60)
    print()
    print("The CIS Assistant MCP server with blockchain supply chain")
    print("features is ready to use!")
    print("Run with: python -m cis_assistant_mcp.server")
    print()


if __name__ == "__main__":
    asyncio.run(demo())
