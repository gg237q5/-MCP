from mcp.types import Tool

get_input_convergence = Tool(
    name="get_input_convergence",
    description="""[Convergence] Retrieve the list of available input specifications for convergence settings.

CRITICAL: Before using this tool, you MUST call `skills` to read the guide!
- Call `skills(category='convergence', name='CONVERGENCE')`
- Read the guide to understand valid keys, units, and options.

Functionality:
1. Quick View Mode (with pagination): Return specs with full info, paginated
2. Detailed Query Mode: Return full info for specified specs (no pagination)

Pagination:
- Default: 25 specs per page
- Use `page` parameter to navigate (page=1, page=2, ...)
- If output is too large, a warning will suggest reducing page_size

Usage:
- Quick View (page 1): get_input_convergence()
- Quick View (page 2): get_input_convergence(page=2)
- Detailed: get_input_convergence(specification_names=['TOL', 'WEG_MAXIT'])
""",
    inputSchema={
        "type": "object",
        "properties": {
            "specification_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of spec names for detailed query (no pagination)"
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination (default: 1)",
                "default": 1
            },
            "page_size": {
                "type": "integer",
                "description": "Specs per page (default: 25). Reduce if output is too large.",
                "default": 25
            }
        },
        "required": []
    }
)

set_input_convergence = Tool(
    name="set_input_convergence",
    description="""[Convergence] Set convergence operating conditions.

CRITICAL: Before using this tool, you MUST call `skills` to read the guide!
- Call `skills(category='convergence', name='CONVERGENCE')`
- Read the guide to understand valid keys, units, and options.

Parameters:
- tol: Tolerance value (default: 0.01) – directly usable, no spec query needed
- weg_maxit: Maximum Wegstein iterations (default: 5000) – directly usable
- specifications_dict: Advanced specs {path: {value, unit}}

Workflow:
1. skills(category='convergence', name='CONVERGENCE') → READ THIS FIRST!
2. get_input_convergence → get available specs
3. unit_list → get unit indices (if needed)
4. set_input_convergence → set values
""",
    inputSchema={
        "type": "object",
        "properties": {
            "tol": {
                "type": "number",
                "description": "Tolerance value (default: 0.01) – directly usable, no spec query needed"
            },
            "weg_maxit": {
                "type": "integer",
                "description": "Maximum Wegstein iterations (default: 5000) – directly usable, no spec query needed"
            },
            "specifications_dict": {
                "type": "object",
                "description": "Advanced spec dictionary. Format: {spec_path: value} or {spec_path: {'value': v, 'unit': u}}. Spec paths must exactly match those from `get_input_convergence`. Use `unit_list` to get unit indices if needed!",
                "additionalProperties": True
            }
        },
        "required": []
    }
)

tools = [
    get_input_convergence,
    set_input_convergence
]
