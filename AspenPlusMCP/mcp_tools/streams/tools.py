from mcp.types import Tool

get_streams_list = Tool(
    name="get_streams_list",
    description="[Streams] List all streams in the current Aspen model, including stream names and types.",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

add_stream = Tool(
    name="add_stream",
    description="[Streams] Add a new stream to the Aspen model. Default type is MATERIAL; other types include HEAT and WORK.",
    inputSchema={
        "type": "object",
        "properties": {
            "stream_name": {
                "type": "string",
                "description": "Stream name (must be ≤ 8 characters)"
            },
            "stream_type": {
                "type": "string",
                "description": "Stream type: MATERIAL (default), HEAT, or WORK",
                "default": "MATERIAL"
            }
        },
        "required": ["stream_name"]
    }
)

remove_stream = Tool(
    name="remove_stream",
    description="""[Streams] Remove a specified stream from the Aspen Plus model.

Functionality:
- Safely remove streams, checking for existing unit connections
- Provide a force removal option
- Automatically disconnect streams if forced
- Return a detailed removal status report

Safety Checks:
- Check whether the stream is connected to any unit
- By default, removal is not allowed if connections exist
- If connected, return a list of associated unit blocks
- Recommended to disconnect first or use force mode

Removal Modes:
- Safe Mode (`force=False`): Refuses to remove if connections exist
- Force Mode (`force=True`): Removes the stream even if connections exist

Return Status:
- SUCCESS: Successfully removed
- NOT_FOUND: Stream not found in the model
- CONNECTED: Stream is connected and `force` is False
- ERROR: An error occurred during the removal process

Usage Recommendations:
- Use Safe Mode under normal circumstances
- Use Force Mode only when sure about removal
- Use `get_block_connections` beforehand to check stream connections
- For batch removal, consider using relevant batch operation tools
""",
    inputSchema={
        "type": "object",
        "properties": {
            "stream_name": {
                "type": "string",
                "description": "Name of the stream to be removed"
            },
            "force": {
                "type": "boolean",
                "description": "Whether to force removal (even if the stream is connected); default is False",
                "default": False
            }
        },
        "required": ["stream_name"]
    }
)

get_stream_input_conditions_list = Tool(
    name="get_stream_input_conditions_list",
    description="""[Streams] Retrieve the list of available input specifications for a stream.

CRITICAL: Before using this tool, you MUST call `skills` to read the guide!
- For MATERIAL streams: Call `skills(category='streams', name='MATERIAL')`
- Read the guide to understand valid keys, units, and basis options.

Functionality:
1. Quick View Mode (with pagination): Return specs with full info, paginated
2. Detailed Query Mode: Return full info for specified specs (no pagination)

Pagination:
- Default: 25 specs per page
- Use `page` parameter to navigate (page=1, page=2, ...)
- If output is too large, a warning will suggest reducing page_size

Usage:
- Quick View (page 1): get_stream_input_conditions_list('FEED')
- Quick View (page 2): get_stream_input_conditions_list('FEED', page=2)
- Detailed: get_stream_input_conditions_list('FEED', specification_names=['TEMP\\\\MIXED'])

Note: Both modes return BASIS information for each specification.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "stream_name": {
                "type": "string",
                "description": "Name of the stream to query"
            },
            "specification_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of spec paths for detailed query (no pagination)"
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
        "required": ["stream_name"]
    }
)

set_stream_input_conditions = Tool(
    name="set_stream_input_conditions",
    description="""[Streams] Set stream operating conditions.

CRITICAL: Before using this tool, you MUST call `skills` to read the guide!
- For MATERIAL streams: Call `skills(category='streams', name='MATERIAL')`
- Read the guide to understand valid keys, units, and basis options.

Parameters:
- temp: Temperature (°C) - direct use
- pres: Pressure (bar) - direct use
- specifications_dict: Advanced specs {path: {value, unit, basis}}

Workflow:
1. skills(category='streams', name='MATERIAL') -> READ THIS FIRST!
2. get_stream_input_conditions_list -> get available specs
3. unit_list -> get unit indices
4. set_stream_input_conditions -> set values
""",
    inputSchema={
        "type": "object",
        "properties": {
            "stream_name": {
                "type": "string",
                "description": "Name of the stream to configure"
            },
            "temp": {
                "type": "number",
                "description": "Temperature (°C) – directly usable, no spec query needed"
            },
            "pres": {
                "type": "number",
                "description": "Pressure (bar) – directly usable, no spec query needed"
            },
            "specifications_dict": {
                "type": "object",
                "description": "Advanced spec dictionary. Format: {spec_path: value} or {spec_path: {'value': v, 'unit': u, 'basis': b}}. Spec paths must exactly match those from `get_stream_input_conditions_list`. Use `unit_list` to get unit indices!",
                "additionalProperties": True
            }
        },
        "required": ["stream_name"]
    }
)

get_stream_output_conditions = Tool(
    name="get_stream_output_conditions",
    description="""[Streams] Get stream output conditions after simulation.

[WARNING] Requires successful simulation first.

Functionality:
1. Quick View Mode (with pagination): Return conditions with full info, paginated
2. Detailed Query Mode: Return full info for specified conditions (no pagination)

Pagination:
- Default: 25 conditions per page
- Use `page` parameter to navigate (page=1, page=2, ...)
- If output is too large, a warning will suggest reducing page_size

Usage:
- Quick view (page 1): get_stream_output_conditions(stream_name='PRODUCT')
- Quick view (page 2): get_stream_output_conditions(stream_name='PRODUCT', page=2)
- Detailed: get_stream_output_conditions(stream_name='PRODUCT', specification_names=['TEMP\\\\MIXED', 'MOLEFRAC\\\\MIXED\\\\ETHANOL'])

[NOTE] For detailed guide:
   skills(category='streams', name='OUTPUT')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "stream_name": {
                "type": "string",
                "description": "Name of the stream whose output conditions you want to retrieve"
            },
            "specification_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of specific output condition names to retrieve (optional). If omitted, paginated quick view is returned."
            },
            "page": {
                "type": "integer",
                "description": "Page number for pagination (default: 1)",
                "default": 1
            },
            "page_size": {
                "type": "integer",
                "description": "Conditions per page (default: 25). Reduce if output is too large.",
                "default": 25
            }
        },
        "required": ["stream_name"]
    }
)

tools = [
    get_streams_list,
    add_stream,
    remove_stream,
    get_stream_input_conditions_list,
    set_stream_input_conditions,
    get_stream_output_conditions
]
