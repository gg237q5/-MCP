from typing import List
from mcp.types import Tool

# Global list to accumulate all tools from modules
ALL_TOOLS: List[Tool] = []

def register_tool_definition(tool: Tool):
    """
    Register a tool definition to the global list.
    Usage:
    
    my_tool = Tool(...)
    register_tool_definition(my_tool)
    """
    ALL_TOOLS.append(tool)
