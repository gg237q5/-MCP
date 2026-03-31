from mcp.types import Tool

get_components_list = Tool(
    name="get_components_list",
    description="[Components] Retrieve the list of all components in the Aspen Plus file",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

get_henrycomps_list = Tool(
    name="get_henrycomps_list",
    description="[Components] Retrieve the list of all Henry-Comps in the Aspen Plus file",
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the Henry-Comps set"
            }
        },
        "required": ["set_name"]
    }
)

add_henrycomps_set = Tool(
    name="add_henrycomps_set",
    description="""[Components]
    Add a new Henry Components Set to the Aspen Plus simulation.
    you will chenck the set_name is exist or not.
    if return error, you will use Get_HenryComps_Set_List() chenck the set_name is exist or not.
    :param Set_name: String. The name/ID of the new Henry Component Set.(e.g., HC-1, HC-2).
    :return: None
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the new Henry Component Set (e.g., 'HC-1'). Leave empty for auto-naming."
            }
        },
        "required": ["set_name"]
    }
)

remove_henrycomps_set = Tool(
    name="remove_henrycomps_set",
    description="""[Components]
    Remove a Henry Components Set from the Aspen Plus simulation.
    
    :param Set_name: String. The name/ID of the Henry Component Set to remove.
    :return: Boolean. True if successful, False otherwise.
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "set_name": {
                "type": "string",
                "description": "The name of the Henry Component Set to remove (e.g., 'HC-1')."
            }
        },
        "required": ["set_name"]
    }
)

get_henrycomps_set_list = Tool(
    name="get_henrycomps_set_list",
    description="[Components] Retrieve the list of all Henry-Comps sets in the Aspen Plus file",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

add_henrycomps = Tool(
    name="add_henrycomps",
    description="""[Components]
    Add or update Henry Components in an Aspen Plus Input File (.inp).
    This tool directly modifies the .inp file to add Henry Components data.
    
    ⚠️ IMPORTANT: This is a SET operation, NOT an incremental add.
    The `comps` parameter must contain ALL components you want selected in the Henry-Comps set,
    including any components that are already selected.
    
    Example: If HC-1 currently has [CO2] and you want to add MEA:
      → comps = ['CO2', 'MEA']  (all components you want selected)
      ✗ comps = ['MEA']  (WRONG - this would replace CO2 with only MEA)
    
    ⚠️ WORKFLOW: This tool modifies .inp files only.
    Required steps:
    1. Export current model to .inp (export_file)
    2. Close the .bkp file (close_aspen)
    3. Call this tool to modify the .inp
    4. Reopen the .inp file (open_aspen_plus) to load changes
    
    :param inp_path: Absolute path to the .inp file
    :param comps: List of ALL component names to select (e.g., ['CO2', 'MEA'])
    :param set_name: String. The name/ID of the Henry Component Set (e.g., 'HC-1').
    :return: None
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "inp_path": {
                "type": "string",
                "description": "Absolute path to the .inp file"
            },
            "comps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of ALL component names to select (including existing ones)"
            },
            "set_name": {
                "type": "string",
                "description": "The name of the Henry Component Set (e.g., 'HC-1')"
            }
        },
        "required": ["inp_path", "comps", "set_name"]
    }
)

remove_henrycomps = Tool(
    name="remove_henrycomps",
    description="""[Components]
    Remove Henry Components from an Aspen Plus Input File (.inp).
    This tool directly modifies the .inp file to update Henry Components data.
    
    ⚠️ IMPORTANT: This is a SET operation. To "remove" a component,
    pass all components you want to KEEP (excluding the ones to remove).
    
    Example: If HC-1 currently has [CO2, MEA] and you want to remove MEA:
      → comps = ['CO2']  (only the components you want to KEEP)
      ✗ comps = ['MEA']  (WRONG - this would keep MEA and remove CO2)
    
    ⚠️ WORKFLOW: This tool modifies .inp files only.
    Required steps:
    1. Export current model to .inp (export_file)
    2. Close the .bkp file (close_aspen)
    3. Call this tool to modify the .inp
    4. Reopen the .inp file (open_aspen_plus) to load changes
    
    :param inp_path: Absolute path to the .inp file
    :param comps: List of component names to KEEP (e.g., ['CO2'])
    :param set_name: String. The name/ID of the Henry Component Set (e.g., 'HC-1').
    :return: None
    """,
    inputSchema={
        "type": "object",
        "properties": {
            "inp_path": {
                "type": "string",
                "description": "Absolute path to the .inp file"
            },
            "comps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of component names to KEEP (excluding ones to remove)"
            },
            "set_name": {
                "type": "string",
                "description": "The name of the Henry Component Set (e.g., 'HC-1')"
            }
        },
        "required": ["inp_path", "comps", "set_name"]
    }
)

elec_wizard = Tool(
    name="elec_wizard",
    description="""[Components]
    Automates the Aspen Plus Electrolyte Wizard.
    Please read skills(category='components', name='ELECTROLYTE') first.
    
    The Electrolyte Wizard will automatically:
    - Add IONIC species based on the molecular components.
    - Configure Henry Components sets (Henry-Comps) for dissolved gas components.
    - Set up the thermodynamic property method (e.g., ENRTL-RK, ELENRTL).
    - Generate electrolyte reaction chemistry.
    
    Recommended Workflow (Electrolyte System Setup):
    1. Use create_inp_file to add MOLECULAR components.
    2. Open the .inp file (open_aspen_plus).
    3. Save as .bkp (save_aspen_file_as).
    4. Close and Reopen the .bkp file (close_aspen, open_aspen_plus).
    5. Set the Aspen Plus GUI to visible (show_aspen_gui visible=True).
    6. Run this elec_wizard tool.
    
    Important Warning:
    - This tool interacts with the current Windows graphical interface.
    - Do not run this tool concurrently with other tools.
    - Ensure the Aspen Plus graphical interface is set to visible (True).
    - Verify the currently open file is in .bkp format (a prerequisite for the Electrolyte Wizard).
    - Enter only the filename (not the full path) in the filename field, e.g., 'aspen.bkp'.
    Function Description:
    - Configuration items: Reference state, hydrogen ion concentration, reaction equations, property calculation methods, simulation methods.
    - Automated "Next" button navigation completes wizard setup.
    - If execution fails, the Electrochemistry Wizard page closes and displays an error message. Please rerun elec_wizard.
    - When you selected Symmetric, the prop_method will be "ENRTL-SR".
    - When you selected Unsymmetric, the prop_method will be "ENRTL-RK" or "ELENRTL".
    Options:
    - chem_source: "APV140 REACTIONS"
    - ref_state: "Unsymmetric", 'Symmetric'
    - h_ion: "Hydronium ion H3O+", "Hydrogen ion H+"
    - reaction_opts: "Include ice formation", "Include salt formation", "Include water dissociation reaction"
    - prop_method: "ENRTL-RK", "ENRTL-SR", "ELENRTL"
    - sim_approach: "True component approach", "Apparent component approach"
""",
    inputSchema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Aspen Plus file name, for example: 'aspen.bkp'.",
            },
            "chem_source": {
                "type": "string",
                "description": "Chemistry Source (化學來源)。",
            },
            "ref_state": {
                "type": "string",
                "description": "Reference State (參考狀態) 方案。",
            },
            "h_ion": {
                "type": "string",
                "description": "Hydrogen Ion type (氫離子類型)。",
            },
            "reaction_opts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of reaction options to enable (e.g. ['Include salt formation']).",
            },
            "prop_method": {
                "type": "string",
                "description": "Base Property Method (基礎物性方法)。",
            },
            "sim_approach": {
                "type": "string",
                "description": "Simulation Approach (模擬方法)。",
            }
        },
        "required": ["filename", "chem_source", "ref_state", "h_ion", "reaction_opts", "prop_method", "sim_approach"]
    }
)

tools = [
    get_components_list,
    get_henrycomps_list,
    add_henrycomps_set,
    remove_henrycomps_set,
    get_henrycomps_set_list,
    add_henrycomps,
    remove_henrycomps,
    elec_wizard
]
