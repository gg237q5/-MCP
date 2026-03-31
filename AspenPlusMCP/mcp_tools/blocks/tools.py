from mcp.types import Tool

get_blocks_list = Tool(
    name="get_blocks_list",
    description="[Blocks] Retrieve the list of all blocks in the Aspen Plus file, including block names and types",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_block_ports = Tool(
    name="get_block_ports",
    description="[Blocks] Get all port names of the specified block. Each port includes name and description (e.g., 'Feed port F (MATERIAL, IN)').",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the block"
            }
        },
        "required": ["block_name"]
    }
)

get_block_connections = Tool(
    name="get_block_connections",
    description="[Blocks] Get the list of streams connected to the specified block (includes both input and output streams).",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the block"
            }
        },
        "required": ["block_name"]
    }
)

add_block = Tool(
    name="add_block",
    description="[Blocks] Add a new block to the Aspen model. Must specify block name and type (e.g., RADFRAC, RSTOIC, Heater, Flash2, FSplit, Mixer, Sep, Pump, HeatX, etc.).",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Block name (must be ≤ 8 characters)"
            },
            "block_type": {
                "type": "string",
                "description": "Type of block to add"
            }
        },
        "required": ["block_name", "block_type"]
    }
)

connect_block_stream = Tool(
    name="connect_block_stream",
    description="[Blocks] Connect a stream to a specified port of a block. You need to specify the block name, stream name, and port type (e.g., F(IN), VD(OUT)). Use get_block_ports to find valid ports.",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the block"
            },
            "stream_name": {
                "type": "string",
                "description": "Name of the stream"
            },
            "port_type": {
                "type": "string",
                "description": "Port type of the block, e.g., F(IN), VD(OUT), B(OUT), P(OUT), etc."
            }
        },
        "required": ["block_name", "stream_name", "port_type"]
    }
)

get_block_input_specifications = Tool(
    name="get_block_input_specifications",
    description="""[Blocks] Retrieve the list of available input specifications for a block.

Functionality:
1. Quick View Mode (with pagination): Return specs with full info, paginated
2. Detailed Query Mode: Return full info for specified specs (no pagination)

Pagination:
- Default: 25 specs per page
- Use `page` parameter to navigate (page=1, page=2, ...)
- If output is too large, a warning will suggest reducing page_size

Usage:
- Quick View (page 1): get_block_input_specifications('COL1')
- Quick View (page 2): get_block_input_specifications('COL1', page=2)
- Detailed: get_block_input_specifications('COL1', specification_names=['NSTAGE'])

Note: Both modes return BASIS information for each specification.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the block to query"
            },
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
        "required": ["block_name"]
    }
)

set_block_input_specifications = Tool(
    name="set_block_input_specifications",
    description="""[Blocks] Set block specifications.

CRITICAL: Before using this tool, you MUST call `skills` to read the guide for the specific block type!
- Example: `skills(category='blocks', name='RADFRAC')`
- Read the guide to understand valid spec names, units, and basis options.

Parameters:
- specifications: {spec_name: value} or {spec_name: {value, unit, basis}}

Workflow:
1. get_blocks_list & get_block_connections
2. skills(category='blocks', name='<BLOCK_TYPE>') → READ THIS FIRST!
3. get_block_input_specifications → get available specs
4. unit_list → get unit indices
5. set_block_input_specifications → set values

⚠️ For detailed setup guide by block type:
   skills(category='blocks', name='RADFRAC')
   skills(category='blocks', name='FLASH2')
   skills(category='blocks', name='HEATER')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the unit operation block to configure"
            },
            "specifications": {
                "type": "object",
                "description": "Specification dictionary. Format: {spec_name: value} or {spec_name: {'value': v, 'unit': u, 'basis': b}}. Spec names must **exactly match** those from `get_block_input_specifications`. Make sure to check connections via `get_block_connections` and retrieve unit index via `unit_list` before setting!",
                "additionalProperties": True
            }
        },
        "required": ["block_name", "specifications"]
    }
)

remove_block = Tool(
    name="remove_block",
    description="""[Blocks] Remove a specified unit (block) from the Aspen Plus model.

Functionality:
- Safely remove unit blocks with connection checks
- Provide a force removal option
- Retain connected streams (only remove the block's connections)
- Return a detailed status report of the removal process

Safety Checks:
- Check whether the block is connected to any streams
- If connections exist, removal is denied by default
- Provide a list of connected streams if applicable
- Recommended to disconnect streams first or use force mode

Removal Modes:
- Safe Mode (`force=False`): Denies removal if connected
- Force Mode (`force=True`): Removes the block even if it has connected streams

Important Notes:
- Removing a block does **not** delete connected streams
- Streams remain in the model but lose their connection to this block
- To remove associated streams, use `remove_stream` separately

Return Status:
- SUCCESS: Block successfully removed
- NOT_FOUND: Block not found
- CONNECTED: Block has connections and `force` is False
- ERROR: Error occurred during the removal process

Usage Recommendations:
- Use safe mode under normal conditions
- Use force mode when certain removal is required
- Check connections beforehand using `get_block_connections`
- Useful when redesigning process flows
""",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "Name of the unit block to be removed"
            },
            "force": {
                "type": "boolean",
                "description": "Whether to force removal (even if the block is connected to streams); default is False",
                "default": False
            }
        },
        "required": ["block_name"]
    }
)

get_block_output_specifications = Tool(
    name="get_block_output_specifications",
    description="""[Blocks] Get block output specs after simulation.

⚠️ Requires successful simulation first.

Functionality:
1. Quick View Mode (with pagination): Return specs with full info, paginated
2. Detailed Query Mode: Return full info for specified specs (no pagination)

Pagination:
- Default: 25 specs per page
- Use `page` parameter to navigate (page=1, page=2, ...)
- If output is too large, a warning will suggest reducing page_size

Usage:
- Quick view (page 1): get_block_output_specifications(block_name='COL1')
- Quick view (page 2): get_block_output_specifications(block_name='COL1', page=2)
- Detailed: get_block_output_specifications(block_name='COL1', specification_names=['MOLE_RR', 'TOP_TEMP'])

⚠️ For detailed guide:
   skills(category='blocks', name='OUTPUT')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "block_name": {
                "type": "string",
                "description": "The name of the unit block to query"
            },
            "specification_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of specification names to query. If omitted, paginated quick view is returned."
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
        "required": ["block_name"]
    }
)

tools = [
    get_blocks_list,
    get_block_ports,
    get_block_connections,
    add_block,
    connect_block_stream,
    get_block_input_specifications,
    set_block_input_specifications,
    remove_block,
    get_block_output_specifications
]
