from mcp.types import Tool

timer = Tool(
    name="timer",
    description="""[Utils] Simple timer utility to measure execution time.

Usage:
1. timer() – Returns the current time
2. timer(start_time='Start time') – Returns current time and elapsed time in seconds

Time format: 'YYYY-MM-DD HH:MM:SS'
""",
    inputSchema={
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "description": "Start time in the format: 'YYYY-MM-DD HH:MM:SS'"
            }
        },
        "required": []
    }
)

unit_list = Tool(
    name="unit_list",
    description="""[Utils] Query Aspen Plus unit system.

CRITICAL: You MUST call `unit_list()` (no arguments) FIRST to view all unit categories!
Then use the returned category index to query specific units.

Usage:
1. unit_list() → CRITICAL: CALL THIS FIRST to see all categories
2. unit_list(item=[n]) → list units in category n
3. unit_list(item=[n, m]) → get unit name for index m in category n

For detailed guide:
   skills(category='utils', name='UNIT_LIST')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "item": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Query input: empty = all categories, [n] = units in category n, [n, m] = name of unit m in category n"
            }
        },
        "required": []
    }
)

get_version = Tool(
    name="get_version",
    description="""[Utils] Get the current MCP server version information.

Returns:
- Version number
- Build type (dev/stable)
- Build date

Use this tool to verify which version of the Aspen Plus MCP server is currently running.
""",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

skills = Tool(
    name="skills",
    description="""[Utils] Get setup guides for Aspen Plus configuration.

CRITICAL BEST PRACTICES - READ THIS FIRST:

1. START HERE: Before using specific tools, you MUST read the global guide:
   → skills(category='core')
   → skills(category='core', name='OVERVIEW')
   This is NOT optional. It defines the standard workflow you must follow.

2. CONSULT SKILL BEFORE ACTION: Before using any tool for the first time in a task:
   - Setting streams? → Read skills(category='streams', name='MATERIAL')
   - Adding a block? → Read skills(category='blocks', name='<BLOCK_TYPE>')
   - Checking results? → Read skills(category='streams', name='OUTPUT')
   - Electrolyte system? → Read skills(category='components', name='ELECTROLYTE')
   - Reactions? → Read skills(category='reactions', name='<REACTIONS>')
   
   Always read the relevant guide first to understand valid keys, units, and procedures.

3. IDENTIFY SYSTEM TYPE FIRST: Before building any model, determine if it is an electrolyte system.
   Electrolyte indicators: amines, acid gases, ionic species, dissociation reactions.
   → If YES: MUST read skills(category='components', name='ELECTROLYTE') before proceeding.
   → The workflow is fundamentally different (use elec_wizard, NOT add_thermo_method).

---

Three-level hierarchy:
1. skills() - List all available categories
2. skills(category='blocks') - List guides in a category
3. skills(category='blocks', name='RADFRAC') - Show guide content

Available Categories:
- core:        Essential workflows
- blocks:      Unit configuration
- streams:     Stream setup & results
- reactions:   Reaction configuration
- simulation:  Execution & Troubleshooting
- convergence: Convergence settings
- properties:  Property methods
- components:  Component definitions
- utils:       Utilities & helpers

Example:
1. Check Category Content First:
   - skills(category='core')

2. Then Check Specific Guide:
   - skills(category='core', name='OVERVIEW') → MUST READ FIRST               
""",
    inputSchema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category name (e.g., streams, blocks, properties)"
            },
            "name": {
                "type": "string",
                "description": "Guide name without .md extension (e.g., RADFRAC, MATERIAL)"
            }
        },
        "required": []
    }
)

tools = [
    timer,
    unit_list,
    get_version,
    skills
]
