"""
Tool Registry with @tool decorator and JSON Schema generation.

A lightweight tool registration system that automatically generates
OpenAI-compatible function schemas from Python type hints and docstrings.
"""

import inspect
import json
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, get_type_hints, get_origin, get_args
from dataclasses import dataclass, field


@dataclass
class Tool:
    """Registered tool with metadata."""
    name: str
    func: Callable
    description: str
    parameters: Dict[str, Any]
    required: List[str]
    module: str = ""
    
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": self.required,
                    "additionalProperties": False
                }
            }
        }


class ToolRegistry:
    """Registry for tools with automatic schema generation."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(self, func: Callable, name: Optional[str] = None) -> Tool:
        """Register a function as a tool."""
        tool_name = name or func.__name__
        sig = inspect.signature(func)
        hints = get_type_hints(func)
        docstring = inspect.getdoc(func) or ""
        
        # Parse docstring for parameter descriptions
        param_descriptions = self._parse_param_descriptions(docstring)
        
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue
            
            param_type = hints.get(param_name, Any)
            param_schema = self._type_to_schema(param_type)
            param_schema["description"] = param_descriptions.get(param_name, "")
            
            properties[param_name] = param_schema
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
        
        tool = Tool(
            name=tool_name,
            func=func,
            description=self._extract_summary(docstring),
            parameters=properties,
            required=required,
            module=func.__module__
        )
        
        self._tools[tool_name] = tool
        return tool
    
    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)
    
    def get_all(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_schemas(self) -> List[Dict[str, Any]]:
        """Get all tool schemas for LLM."""
        return [tool.to_openai_schema() for tool in self._tools.values()]
    
    def call(self, name: str, args: Dict[str, Any]) -> Any:
        """Call a tool by name with arguments."""
        tool = self._tools.get(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool.func(**args)
    
    def _parse_param_descriptions(self, docstring: str) -> Dict[str, str]:
        """Extract parameter descriptions from docstring."""
        descriptions = {}
        lines = docstring.split("\n")
        in_params = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.lower().startswith("args:") or stripped.lower().startswith("parameters:"):
                in_params = True
                continue
            if in_params and stripped and not stripped[0].isspace() and ":" not in stripped:
                in_params = False
            if in_params and ":" in stripped:
                param, desc = stripped.split(":", 1)
                descriptions[param.strip()] = desc.strip()
        
        return descriptions
    
    def _extract_summary(self, docstring: str) -> str:
        """Extract first line of docstring as summary."""
        lines = docstring.strip().split("\n")
        return lines[0] if lines else ""
    
    def _type_to_schema(self, typ: type) -> Dict[str, Any]:
        """Convert Python type to JSON Schema."""
        origin = get_origin(typ)
        args = get_args(typ)
        
        # Handle Optional[T] = Union[T, None]
        if origin is type(None) or (origin is Union and type(None) in args):
            non_none = [a for a in args if a is not type(None)]
            if non_none:
                schema = self._type_to_schema(non_none[0])
                schema["nullable"] = True
                return schema
        
        # Handle Union
        if origin is Union:
            return {"anyOf": [self._type_to_schema(a) for a in args if a is not type(None)]}
        
        # Handle List/Sequence
        if origin in (list, List, tuple, Tuple):
            item_type = args[0] if args else Any
            return {"type": "array", "items": self._type_to_schema(item_type)}
        
        # Handle Dict/Mapping
        if origin in (dict, Dict):
            key_type, val_type = args if len(args) == 2 else (str, Any)
            return {"type": "object", "additionalProperties": self._type_to_schema(val_type)}
        
        # Primitive types
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            Any: {"type": "object"},
        }
        
        return type_map.get(typ, {"type": "object"})


# Global registry instance
registry = ToolRegistry()


def tool(func: Optional[Callable] = None, *, name: Optional[str] = None) -> Callable:
    """
    Decorator to register a function as a tool.
    
    Usage:
        @tool
        def search(query: str, limit: int = 10) -> List[str]:
            \"\"\"Search the web for query.\"\"\"
            ...
        
        @tool(name="custom_name")
        def my_func(...):
            ...
    """
    def decorator(f: Callable) -> Callable:
        registry.register(f, name=name)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


# Import Union for type hints
from typing import Union, Tuple