from mcp.types import Tool

aspen_connect = Tool(
    name="aspen_connect",
    description="""[Core] Connect to AspenPlus application via COM interface.

CRITICAL: Before starting, read the global overview:
   skills(category='core', name='OVERVIEW')

This tool establishes a connection to the AspenPlus COM object. 
If no version is specified, it connects to the default installed version.

Version format examples:
- None (default): Connect to default AspenPlus installation
- "Apwn.Document": Default version
- "Apwn36.0": AspenPlus V10.0
- "Apwn40.0": AspenPlus V11.0

Use cases:
- Initialize AspenPlus before loading files
- Connect to a specific version of AspenPlus
- Re-establish connection after disconnection

Note: This is different from 'open_aspen_plus' which loads a file.
This tool only establishes the COM connection without loading any file.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "version": {
                "type": "string",
                "description": "AspenPlus version string (e.g., 'Apwn36.0' for V10.0). If not specified, connects to default version."
            }
        },
        "required": []
    }
)

is_aspen_connected = Tool(
    name="is_aspen_connected",
    description="""[Core] Check if AspenPlus application is currently connected.

CRITICAL: Before starting, read the global overview:
   skills(category='core', name='OVERVIEW')

This tool verifies the connection status to the AspenPlus COM object.

Use cases:
- Verify connection before performing operations
- Check connection health
- Diagnose connection issues
- Validate setup before file operations

Returns:
- True: AspenPlus is connected and accessible
- False: No active connection or connection lost

Recommendation: Call this before critical operations to ensure connectivity.
""",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

close_aspen_connection = Tool(
    name="close_aspen_connection",
    description="""[Core] Close the connection to AspenPlus application.

This tool properly closes the COM connection to AspenPlus.

Important notes:
- This closes the COM connection, not the file
- Use 'close_aspen' to close both file and connection
- After closing, you'll need to use 'aspen_connect' to reconnect
- Any unsaved changes in the file will be lost

Use cases:
- Clean shutdown of AspenPlus connection
- Release COM resources
- Prepare for version switching
- Troubleshoot connection issues

Recommendation: Save your work before closing the connection.
""",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

create_inp_file = Tool(
    name="create_inp_file",
    description="""[Core] Create Aspen Plus input file (.inp)

CRITICAL: Before starting, read the global overview:
   skills(category='core', name='OVERVIEW')

⚠️ ELECTROLYTE SYSTEMS (MEA-CO2, acid gas, amine-based, ionic):
   - Add MOLECULAR components ONLY
   - Do NOT add ionic species
   - Ions are auto-added by elec_wizard later
   - See: skills(category='components', name='ELECTROLYTE')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Full path for output file (including .inp extension)"
            },
            "components": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of chemical formulas (no spaces, max 8 characters)"
            },
            "cas_numbers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of corresponding CAS numbers"
            }
        },
        "required": ["file_path", "components", "cas_numbers"]
    }
)

open_aspen_plus = Tool(
    name="open_aspen_plus",
    description="""[Core] Open Aspen Plus and load the specified file

CRITICAL: Before starting, read the global overview:
   skills(category='core', name='OVERVIEW')
""",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the .inp or .apw file to be loaded"
            }
        },
        "required": ["file_path"]
    }
)

show_aspen_gui = Tool(
    name="show_aspen_gui",
    description="[Core] Show or hide the Aspen Plus GUI",
    inputSchema={
        "type": "object",
        "properties": {
            "visible": {
                "type": "boolean",
                "description": "True to show GUI, False to hide GUI"
            }
        },
        "required": ["visible"]
    }
)

suppress_dialogs = Tool(
    name="suppress_dialogs",
    description="[Core] Control whether Aspen Plus shows pop-up dialogs. Recommended to set True during automation to prevent interruption.",
    inputSchema={
        "type": "object",
        "properties": {
            "suppress": {
                "type": "boolean",
                "description": "True to suppress dialogs, False to allow"
            }
        },
        "required": ["suppress"]
    }
)

save_aspen_file = Tool(
    name="save_aspen_file",
    description="[Core] Save the current Aspen Plus file",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

save_aspen_file_as = Tool(
    name="save_aspen_file_as",
    description="[Core] Save the current Aspen Plus file with a new name",
    inputSchema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Path and name of the file to save. If the extension is .inp, it will be automatically converted to .bkp"
            }
        },
        "required": ["filename"]
    }
)

close_aspen = Tool(
    name="close_aspen",
    description="[Core] Close Aspen Plus",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

list_aspen_info = Tool(
    name="list_aspen_info",
    description="[Core] List information in the Aspen Plus file (blocks, streams, components)",
    inputSchema={
        "type": "object",
        "properties": {
            "info_type": {
                "type": "string",
                "enum": ["blocks", "streams", "components", "all"],
                "description": "Type of information to list"
            }
        },
        "required": ["info_type"]
    }
)

export_file = Tool(
    name="export_file",
    description="""[Core] Export the current Aspen Plus model to various file formats.

Export Types:
- inp: Input file (.inp) WITHOUT graphics - useful for flowsheet re-layout
- inp_graphics: Input file (.inp) WITH graphics
- bkp: Backup file (.bkp)
- rep: Report file (.rep) - simulation results
- sum: Summary file (.sum)

⚠️ For detailed usage guide:
   skills(category='core', name='EXPORT')

Key Use Case:
Export to .inp (without graphics) before running simulation, then reopen 
the .inp file to let Aspen Plus auto-arrange the flowsheet layout.
""",
    inputSchema={
        "type": "object",
        "properties": {
            "export_type": {
                "type": "string",
                "enum": ["inp", "inp_graphics", "bkp", "rep", "sum"],
                "description": "Type of file to export: inp (no graphics), inp_graphics, bkp, rep, sum"
            },
            "file_path": {
                "type": "string",
                "description": "Full path for the exported file (including extension)"
            }
        },
        "required": ["export_type", "file_path"]
    }
)

tools = [
    aspen_connect,
    is_aspen_connected,
    close_aspen_connection,
    create_inp_file,
    open_aspen_plus,
    show_aspen_gui,
    suppress_dialogs,
    save_aspen_file,
    save_aspen_file_as,
    close_aspen,
    list_aspen_info,
    export_file
]
