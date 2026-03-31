from mcp.types import Tool

add_thermo_method = Tool(
    name="add_thermo_method",
    description="""[Properties] Set the thermodynamic method for the Aspen Plus model.

⚠️ For detailed setup guide:
   skills(category='properties', name='THERMO_METHOD')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "method_name": {
                "type": "string",
                "description": "Name of the thermodynamic method (e.g., NRTL, UNIFAC, PENG-ROB, IDEAL, SRK)"
            }
        },
        "required": ["method_name"]
    }
)

get_properties_list = Tool(
    name="get_properties_list",
    description="""[Properties] Get available property specifications for the Aspen Plus model.

Pagination:
- Default: 25 specs per page
- Use `page` parameter to navigate

Usage:
- Page 1: get_properties_list()
- Page 2: get_properties_list(page=2)
""",
    inputSchema={
        "type": "object",
        "properties": {
            "page": {
                "type": "integer",
                "description": "Page number (default: 1)",
                "default": 1
            },
            "page_size": {
                "type": "integer",
                "description": "Specs per page (default: 25)",
                "default": 25
            }
        },
        "required": []
    }
)

tools = [
    add_thermo_method,
    get_properties_list
]
