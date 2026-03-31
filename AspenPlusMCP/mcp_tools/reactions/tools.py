from mcp.types import Tool

add_reaction_set = Tool(
    name="add_reaction_set",
    description="""[Reactions] Add a new reaction set to Aspen Plus.
    
    :param set_name: Reaction set name.
    :param reactions_type: Exact type string (e.g., 'POWERLAW', 'LHHW').
    
    Work flow:
    1. Use get_reaction_set_list() to get the list of reaction sets to check if the set_name is exist or not.
    2. Use get_reaction_set_type_list() to get the list of reaction set types to check if the reactions_type is exist or not.
    3. Use add_reaction_set() to add the new reaction set, make sure the set_name and reactions_type are valid.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the new Reaction Set (Max 8 characters)."
            },
            "reactions_type": {
                "type": "string",
                "description": "The type of reactions. MUST be one of the types returned by get_reaction_set_type_list"
            }
        },
        "required": ["set_name", "reactions_type"]
    }
)

remove_reaction_set = Tool(
    name="remove_reaction_set",
    description="""[Reactions] Remove a Reaction Set from Aspen Plus.
    
    :param set_name: The name of the reaction set to remove.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the Reaction Set to remove (e.g., 'R-1')."
            }
        },
        "required": ["set_name"]
    }
)

get_reaction_set_list = Tool(
    name="get_reaction_set_list",
    description="""[Reactions] Retrieve the list of all available Reaction Sets.
    Returns a list of set names (e.g., ['R-1', 'LGE']).
    """,
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_reaction_set_type_list = Tool(
    name="get_reaction_set_type_list",
    description="""[Reactions] Retrieve the list of available Reaction Set Types (e.g., 'KINETIC', 'LGE').
    Returns a list of type names.
    """,
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_reaction_input_specifications = Tool(
    name="get_reaction_input_specifications",
    description="""[Reactions] Retrieve all available enterable specifications for a specific Reaction Set.
    Includes description, value, unit, unit category, and basis for each specification.
    Returns the FULL list of specifications.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "reac_set": {
                "type": "string",
                "description": "The name of the Reaction Set to query (e.g., 'R-1')."
            }
        },
        "required": ["reac_set"]
    }
)

set_reaction_input_specifications = Tool(
    name="set_reaction_input_specifications",
    description="""[Reactions] Set specifications for a specific Reaction Set.
    Supports setting values, units, and basis.
    
    CRITICAL: Before using this tool, you MUST call `skills` to read the guide for the specific reaction type!
    - Example: `skills(category='reactions', name='KINETIC')` or `skills(category='reactions', name='POWERLAW')`
    - Read the guide to understand valid spec keys, units, and basis options.
    - DO NOT assume or guess parameter string formats!
    
    :param set_name: The name of the reaction set (e.g., 'R-1').
    :param specifications_dict: A dictionary of specifications to set.
         Key: Specification path/name (e.g., 'KEY' or 'SUB\\KEY').
         Value: Can be a simple value, or a dictionary {'value': val, 'unit': unit_id, 'basis': basis_str}.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the Reaction Set (e.g., 'R-1')."
            },
            "specifications_dict": {
                "type": "object",
                "description": "Dictionary of specifications to set. Example: {'TEMP': 50, 'PRES': {'value': 2, 'unit': 3}}"
            }
        },
        "required": ["set_name", "specifications_dict"]
    }
)

add_reaction = Tool(
    name="add_reaction",
    description="""[Reactions] Modify INP file to insert new reaction string at the bottom of a specific Reaction Set block.
    read skills(category='reactions', name='ADD_REACTION_WORKFLOW') and (category='reactions', name='<reaction_type>') first.
    
    CRITICAL WORKFLOW:
    1. If you have a .bkp file, FIRST use `convert_aspen_file` to convert it to .inp.
    2. Use this tool (`add_reaction`) on the generated .inp file.
    3. After modification, use `convert_aspen_file` again on the .inp file to convert it back to .bkp (if needed).
    
    Note:
    - This tool REQUIRES an .inp file path. It will NOT work with .bkp files directly.
    - The `reactions_data` should explicitly declare each stoichiometric equation as a dict with `id` and `stoic` values.
    - IMPORTANT: This tool is ONLY for adding reaction stoichiometry/equations. DO NOT attempt to add reaction parameters (e.g., ACT_ENERGY) here. It will cause parsing errors.
    - To configure reaction parameters, you MUST use `set_reaction_input_specifications` back in Aspen Plus AFTER converting the INP back to BKP. Before doing so, you MUST read the specific reaction type documentation (e.g., `skills(category='reactions', name='POWERLAW')`).
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "inp_path": {
                "type": "string",
                "description": "Full absolute path to the .inp file."
            },
            "set_name": {
                "type": "string",
                "description": "Name of the Reaction Set (Max 8 characters, e.g., 'MEA-RXN')."
            },
            "reactions_data": {
                "type": "array",
                "description": "List of dictionaries containing 'id' and 'stoic'.\nOptional: 'default_ssid' can be specified at the reaction id level to apply a default substream ID (e.g., 'MIXED') to all components in 'stoic'.\n'stoic' can be simple: {'MEA': -1.0} or complex with ssid: {'CO2': {'coef': -1.0, 'ssid': 'MIXED'}}.\nExample: [{\"id\": 1, \"default_ssid\": \"MIXED\", \"stoic\": {\"MEA\": -1.0, \"CO2\": {\"coef\": -1.0, \"ssid\": \"MIXED\"}, \"H2O\": 1.0}}]",
                "items": {"type": "object"}
            },
            "reaction_type": {
                "type": "string",
                "description": "Type of reaction if creating a new block (default: 'REAC-DIST').",
                "default": "REAC-DIST"
            }
        },
        "required": ["inp_path", "set_name", "reactions_data", "reaction_type"]
    }
)


remove_reaction = Tool(
    name="remove_reaction",
    description="""[Reactions] Modify INP file to reconstruct a specific Reaction Set block, retaining only the provided reactions and parameters. This effectively removes any reactions not passed in.
    read skills(category='reactions', name='REMOVE_REACTION_WORKFLOW') and (category='reactions', name='<reaction_type>') first.
    CRITICAL WORKFLOW:
    1. If you have a .bkp file, FIRST use `convert_aspen_file` to convert it to .inp.
    2. Use this tool (`remove_reaction`) on the generated .inp file.
    3. After modification, use `convert_aspen_file` again on the .inp file to convert it back to .bkp (if needed).
    
    Note:
    - This tool REQUIRES an .inp file path. It will NOT work with .bkp files directly.
    - The `reactions_data` should explicitly declare each stoichiometric equation as a dict with `id` and `stoic` values.
    - This tool deletes the existing Reaction Set block and reconstructs it with ONLY the provided reactions' basic STOIC definitions.
    - **CRITICAL**: DO NOT include reaction parameters (like RATE-CON) in `reactions_data`. It will cause parsing errors just like in `add_reaction`.
    - **WORKFLOW**: To preserve parameters for the retained reactions, you MUST first backup the parameters using `get_reaction_input_specifications`, run this tool on the INP to trim the reactions, reopen the file, and then restore the parameters using `set_reaction_input_specifications`.
    - **CRITICAL RESTORE STEP**: Before using `set_reaction_input_specifications` to restore parameters, you MUST read the specific reaction type documentation (e.g., `skills(category='reactions', name='POWERLAW')`) to ensure correct parameter formatting.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "inp_path": {
                "type": "string",
                "description": "Full absolute path to the .inp file."
            },
            "set_name": {
                "type": "string",
                "description": "Name of the Reaction Set (Max 8 characters, e.g., 'ABSORBER')."
            },
            "reactions_data": {
                "type": "array",
                "description": "List of dictionaries containing ONLY 'id' and 'stoic'. Do NOT include parameter keys. Example: [{'id': 1, 'stoic': {'H2O': -1.0, 'H3O+': 1.0, 'OH-': 1.0}}]",
                "items": {"type": "object"}
            },
            "reaction_type": {
                "type": "string",
                "description": "Type of the reaction (e.g., POWERLAW, KINETIC). Default is 'POWERLAW'.",
                "default": "POWERLAW"
            }
        },
        "required": ["inp_path", "set_name", "reactions_data", "reaction_type"]
    }
)


tools = [
    add_reaction_set,
    remove_reaction_set,
    get_reaction_set_list,
    get_reaction_set_type_list,
    get_reaction_input_specifications,
    set_reaction_input_specifications,
    add_reaction,
    remove_reaction
]
