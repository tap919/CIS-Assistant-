# Example Contracts and Use Cases

This document provides example contracts and use cases for the CIS Assistant MCP Server.

## Example 1: Web API Handler

### Contract Definition

```json
{
  "component_name": "UserAPIHandler",
  "component_type": "class",
  "requirements": {
    "description": "Handle HTTP requests for user management API",
    "methods": [
      {
        "name": "get_user",
        "parameters": [
          {"name": "user_id", "type": "str"}
        ],
        "return_type": "Dict[str, Any]",
        "description": "Retrieve user information by ID"
      },
      {
        "name": "create_user",
        "parameters": [
          {"name": "user_data", "type": "Dict[str, Any]"}
        ],
        "return_type": "Dict[str, Any]",
        "description": "Create a new user"
      },
      {
        "name": "update_user",
        "parameters": [
          {"name": "user_id", "type": "str"},
          {"name": "updates", "type": "Dict[str, Any]"}
        ],
        "return_type": "Dict[str, Any]",
        "description": "Update user information"
      }
    ],
    "constraints": [
      "Must validate input data before processing",
      "Must return proper HTTP status codes",
      "Must handle errors gracefully",
      "Must log all operations"
    ]
  }
}
```

### Expected Implementation

```python
from typing import Dict, Any
import logging

class UserAPIHandler:
    """Handle HTTP requests for user management API"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Retrieve user information by ID"""
        self.logger.info(f"Getting user {user_id}")
        
        if not user_id:
            return {"error": "User ID required", "status": 400}
        
        # Implementation here
        return {"user_id": user_id, "status": 200}
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        self.logger.info("Creating new user")
        
        if not self._validate_user_data(user_data):
            return {"error": "Invalid user data", "status": 400}
        
        # Implementation here
        return {"user_id": "new_id", "status": 201}
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information"""
        self.logger.info(f"Updating user {user_id}")
        
        if not user_id or not updates:
            return {"error": "User ID and updates required", "status": 400}
        
        # Implementation here
        return {"user_id": user_id, "updated": True, "status": 200}
    
    def _validate_user_data(self, data: Dict[str, Any]) -> bool:
        """Validate user data"""
        required_fields = ["email", "name"]
        return all(field in data for field in required_fields)
```

## Example 2: Data Processing Pipeline

### Contract Definition

```json
{
  "component_name": "DataPipeline",
  "component_type": "class",
  "requirements": {
    "description": "Process data through multiple transformation stages",
    "methods": [
      {
        "name": "add_stage",
        "parameters": [
          {"name": "stage_name", "type": "str"},
          {"name": "transform_func", "type": "Callable"}
        ],
        "return_type": "None",
        "description": "Add a transformation stage to the pipeline"
      },
      {
        "name": "execute",
        "parameters": [
          {"name": "input_data", "type": "Any"}
        ],
        "return_type": "Any",
        "description": "Execute the pipeline on input data"
      },
      {
        "name": "reset",
        "parameters": [],
        "return_type": "None",
        "description": "Reset the pipeline to initial state"
      }
    ],
    "properties": ["stages", "results"],
    "constraints": [
      "Must execute stages in order",
      "Must handle stage failures gracefully",
      "Must track results at each stage",
      "Must be reusable after reset"
    ]
  }
}
```

### Expected Implementation

```python
from typing import Any, Callable, List, Dict

class DataPipeline:
    """Process data through multiple transformation stages"""
    
    def __init__(self):
        self.stages: List[Dict[str, Any]] = []
        self.results: List[Any] = []
    
    def add_stage(self, stage_name: str, transform_func: Callable) -> None:
        """Add a transformation stage to the pipeline"""
        self.stages.append({
            "name": stage_name,
            "func": transform_func
        })
    
    def execute(self, input_data: Any) -> Any:
        """Execute the pipeline on input data"""
        current_data = input_data
        self.results = []
        
        for stage in self.stages:
            try:
                current_data = stage["func"](current_data)
                self.results.append({
                    "stage": stage["name"],
                    "output": current_data,
                    "success": True
                })
            except Exception as e:
                self.results.append({
                    "stage": stage["name"],
                    "error": str(e),
                    "success": False
                })
                raise
        
        return current_data
    
    def reset(self) -> None:
        """Reset the pipeline to initial state"""
        self.stages = []
        self.results = []
```

## Example 3: Caching Layer

### Contract Definition

```json
{
  "component_name": "CacheManager",
  "component_type": "class",
  "requirements": {
    "description": "Manage cached data with TTL and eviction policies",
    "methods": [
      {
        "name": "get",
        "parameters": [
          {"name": "key", "type": "str"}
        ],
        "return_type": "Optional[Any]",
        "description": "Retrieve cached value by key"
      },
      {
        "name": "set",
        "parameters": [
          {"name": "key", "type": "str"},
          {"name": "value", "type": "Any"},
          {"name": "ttl", "type": "Optional[int]"}
        ],
        "return_type": "None",
        "description": "Store value in cache with optional TTL"
      },
      {
        "name": "delete",
        "parameters": [
          {"name": "key", "type": "str"}
        ],
        "return_type": "bool",
        "description": "Remove key from cache"
      },
      {
        "name": "clear",
        "parameters": [],
        "return_type": "None",
        "description": "Clear all cached data"
      }
    ],
    "constraints": [
      "Must handle expired entries automatically",
      "Must be thread-safe",
      "Must track cache hits and misses",
      "Must support configurable eviction policy"
    ]
  }
}
```

## Example 4: Simple Function

### Contract Definition

```json
{
  "component_name": "validate_email",
  "component_type": "function",
  "requirements": {
    "description": "Validate email address format",
    "parameters": [
      {"name": "email", "type": "str"}
    ],
    "return_type": "bool",
    "constraints": [
      "Must check for @ symbol",
      "Must check for domain",
      "Must handle edge cases",
      "Must not raise exceptions"
    ]
  }
}
```

### Expected Implementation

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    # Simple regex pattern for email validation
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    try:
        return bool(re.match(pattern, email))
    except Exception:
        return False
```

## Common Error Patterns and Fixes

### Pattern 1: Missing Type Hints

**Before:**
```python
def process(self, data):
    return data
```

**After:**
```python
def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
    return data
```

### Pattern 2: Missing Docstring

**Before:**
```python
class UserManager:
    def create_user(self, name: str) -> User:
        return User(name)
```

**After:**
```python
class UserManager:
    """Manage user lifecycle operations"""
    
    def create_user(self, name: str) -> User:
        """Create a new user with the given name"""
        return User(name)
```

### Pattern 3: Missing Error Handling

**Before:**
```python
def get_user(self, user_id: str) -> Dict[str, Any]:
    return self.database[user_id]
```

**After:**
```python
def get_user(self, user_id: str) -> Dict[str, Any]:
    """Retrieve user by ID"""
    try:
        return self.database.get(user_id, {})
    except Exception as e:
        self.logger.error(f"Error getting user: {e}")
        return {"error": "User not found"}
```

## Best Practices

1. **Always Start with a Contract**
   - Define clear interfaces
   - Specify all constraints
   - Document expected behavior

2. **Validate Early and Often**
   - Check implementation against contract
   - Fix issues immediately
   - Re-validate after changes

3. **Record Successful Fixes**
   - Build a knowledge base
   - Help future development
   - Share patterns with team

4. **Use Descriptive Names**
   - Clear component names
   - Meaningful method names
   - Consistent naming conventions

5. **Include All Constraints**
   - Performance requirements
   - Security considerations
   - Error handling rules
   - Thread safety needs

## Using These Examples

To try these examples with CIS Assistant:

1. Ask Claude to generate a contract using one of the JSON definitions above
2. Review the generated contract
3. Implement the code following the expected implementation
4. Validate your implementation
5. Record any fixes you make

Example prompt for Claude:
```
Use the CIS Assistant to generate a contract for a UserAPIHandler class with 
methods for get_user, create_user, and update_user. The class should handle 
HTTP requests, validate input data, return proper status codes, and log all 
operations.
```
