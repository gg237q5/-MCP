# Aspen Plus MCP Server

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server that enables AI assistants (Claude, Antigravity, etc.) to interact with **Aspen Plus** process simulation software via COM automation.

## 🌟 Features

- **Complete Aspen Plus Automation**: Build, simulate, and analyze process models entirely through natural language
- **42 MCP Tools**: Comprehensive coverage of Aspen Plus functionality
- **Modular Architecture**: Clean separation of concerns across 7 function modules
- **Aspen Core Library**: Reusable Python classes for programmatic Aspen Plus control
- **Test Suite**: Comprehensive tests including ORC simulation example
- **LLM-Optimized**: Rich tool descriptions designed for AI comprehension

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Tool Reference](#-tool-reference)
- [Workflow Examples](#-workflow-examples)
- [Architecture](#-architecture)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Installation

See [INSTALL.md](./INSTALL.md) for detailed installation instructions.

### Prerequisites
- **Windows 10/11** (Required for Aspen Plus COM interface)
- **Aspen Plus V12, V14+** with valid license
- **Python 3.10+**

### Quick Setup
```powershell
# Clone repository
git clone https://github.com/conlinkang/AspenPlusMCP.git
cd AspenPlusMCP

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

### MCP Client Configuration
Add to your MCP client configuration (e.g., Claude Desktop `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "aspen-plus": {
      "command": "D:\\AspenPlusMCP\\venv\\Scripts\\python.exe",
      "args": ["d:\\AspenPlusMCP\\aspen_mcp_server_modular.py"]
    }
  }
}
```

---

## ⚡ Quick Start

Once configured, you can interact with Aspen Plus via natural language:

```
User: Create a simple flash separator simulation with water and ethanol at 80°C and 1 atm.

AI Assistant: I'll create this simulation for you...
```

The assistant will:
1. Create an input file with components
2. Open Aspen Plus and load the file
3. Set thermodynamic method (NRTL)
4. Add Flash2 block and streams
5. Set stream conditions
6. Run simulation
7. Report results

---

## 🔧 Tool Reference

The MCP server provides **42 tools** organized into **8 modules**:

### Core Module (12 tools)

| Tool | Description |
|------|-------------|
| `aspen_connect` | Connect to Aspen Plus via COM interface. Optional version parameter for specific versions (e.g., `Apwn36.0` for V10). |
| `is_aspen_connected` | Check if Aspen Plus is currently connected and accessible. |
| `close_aspen_connection` | Close the COM connection (does not close the file). |
| `create_inp_file` | Create Aspen Plus input file (.inp) with specified components and CAS numbers. |
| `open_aspen_plus` | Open Aspen Plus and load a `.inp` or `.apw` file. |
| `show_aspen_gui` | Show or hide the Aspen Plus graphical interface. |
| `suppress_dialogs` | Suppress pop-up dialogs during automation (recommended: `true`). |
| `save_aspen_file` | Save the current Aspen Plus file. |
| `save_aspen_file_as` | Save with a new filename. `.inp` files are auto-converted to `.bkp`. |
| `close_aspen` | Close Aspen Plus completely. |
| `list_aspen_info` | List blocks, streams, components, or all information in the file. |
| `export_file` | Export model to .inp (with/without graphics), .bkp, .rep, or .sum formats. |

---

### Simulation Module (6 tools)

| Tool | Description |
|------|-------------|
| `check_model_completion_status` | Comprehensive model check: identifies incomplete inputs, errors, and warnings before simulation. |
| `get_incomplete_items` | Get detailed list of items needing attention. Filter by `streams`, `blocks`, or issue type. |
| `run_simulation` | Execute simulation with timeout control. Ensure model is complete first. |
| `run_and_report` | Run simulation with detailed diagnostic report. Best for debugging. |
| `check_and_run` | Smart run: automatically checks model readiness before execution. |
| `reinitialize` | Reinitialize the simulation engine to clear previous results. |

**Recommended Simulation Workflow:**
```
1. check_model_completion_status()  → Verify model ready
2. run_simulation() or check_and_run()  → Execute
3. get_stream_output_conditions() / get_block_output_specifications()  → Review results
```

---

### Blocks Module (9 tools)

| Tool | Description |
|------|-------------|
| `get_blocks_list` | List all blocks with names and types. |
| `get_block_ports` | Get available ports for a block (e.g., `F(IN)`, `VD(OUT)`). |
| `get_block_connections` | List streams connected to a block. |
| `add_block` | Add a new block. Types: `RADFRAC`, `RSTOIC`, `Heater`, `Flash2`, `FSplit`, `Mixer`, `Sep`, `Pump`, `HeatX`, etc. |
| `connect_block_stream` | Connect a stream to a specific block port. |
| `get_block_input_specifications` | Get available input specs for a block. Supports quick view and detailed query. |
| `set_block_input_specifications` | Set block parameters. Supports value, unit, and basis configuration. |
| `remove_block` | Remove a block. Use `force=true` to remove even with connected streams. |
| `get_block_output_specifications` | Get simulation results for a block (only after successful run). |

**Block Specification Example:**
```python
# Set distillation column specifications
set_block_input_specifications(
    block_name="COL1",
    specifications={
        "NSTAGE": 20,
        "BASIS_RR": 2.0,
        "FEED_STAGE\\FEED": 10
    }
)
```

---

### Streams Module (6 tools)

| Tool | Description |
|------|-------------|
| `get_streams_list` | List all streams with names and types (`MATERIAL`, `HEAT`, `WORK`). |
| `add_stream` | Add a new stream. Default type is `MATERIAL`. |
| `remove_stream` | Remove a stream. Use `force=true` if connected. |
| `get_stream_input_conditions_list` | Get available input specifications for a stream. |
| `set_stream_input_conditions` | Set stream conditions: `temp`, `pres`, and advanced specs. |
| `get_stream_output_conditions` | Get stream results after simulation. |

**Stream Specification Example:**
```python
# Set feed stream conditions
set_stream_input_conditions(
    stream_name="FEED",
    temp=25.0,  # °C
    pres=1.01325,  # bar
    specifications_dict={
        "FLOW\\MIXED\\WATER": {"value": 100, "basis": "MASS-FRAC"},
        "FLOW\\MIXED\\ETHANOL": {"value": 50, "basis": "MASS-FRAC"}
    }
)
```

---

### Convergence Module (2 tools)

| Tool | Description |
|------|-------------|
| `get_input_convergence` | Retrieve available convergence specifications (TOL, WEG_MAXIT, etc.). |
| `set_input_convergence` | Set convergence parameters like tolerance and max iterations. |

---

### Properties Module (2 tools)

| Tool | Description |
|------|--------------|
| `add_thermo_method` | Set thermodynamic method for the model. |
| `get_properties_list` | Get available property specifications with pagination support. |

**Supported Methods:**
| Category | Methods |
|----------|---------|
| Equation of State | `PENG-ROB`, `SRK`, `BK10`, `CPA`, `PC-SAFT`, `VTPR` |
| Activity Coefficient | `NRTL`, `UNIQUAC`, `UNIFAC`, `WILSON`, `POLYNRTL` |
| Electrolyte | `ELECNRTL`, `ENRTL-RK`, `ENRTL-SR`, `PITZER` |
| Special | `IDEAL`, `SOLIDS`, `IAPWS-95`, `IF97`, `CHAO-SEA` |

> ⚠️ **Important**: After setting thermodynamic method, save as `.bkp`, close, and reopen the file for proper initialization.

---

### Components Module (1 tool)

| Tool | Description |
|------|-------------|
| `get_components_list` | Retrieve all components defined in the model. |

---

### Utils Module (4 tools)

| Tool | Description |
|------|--------------|
| `timer` | Measure execution time. |
| `unit_list` | Query Aspen Plus unit system. Essential for unit indices. |
| `get_version` | Get MCP server version information. |
| `skills` | Get setup guides for Aspen Plus configuration. 3-level hierarchy. |

**Skills Usage:**
```python
skills()                              # List all categories
skills(category='blocks')             # Show SKILL.md overview
skills(category='blocks', name='RADFRAC')  # Show detailed guide
```

> 📚 **Skills Directory**: See `skills/` folder for setup guides organized by category (blocks, streams, properties, etc.)

**How to Add a New Skill:**

1. **Create Resource File**: Add a new `.md` file in the appropriate `resources/` folder (e.g., `skills/blocks/resources/MYBLOCK.md`).
2. **Update Index**: Edit the `SKILL.md` file in that category folder to include the new resource in the table.
3. **Usage**: The new skill will be immediately available via `skills(category='...', name='MYBLOCK')`.

---

## 📖 Workflow Examples

### Example 1: Simple Flash Separation

```
1. create_inp_file(file_path="C:/sim/flash.inp", 
                   components=["WATER", "ETHANOL"], 
                   cas_numbers=["7732-18-5", "64-17-5"])
2. open_aspen_plus(file_path="C:/sim/flash.inp")
3. add_thermo_method(method_name="NRTL")
4. save_aspen_file_as(filename="C:/sim/flash.bkp")
5. close_aspen()
6. open_aspen_plus(file_path="C:/sim/flash.bkp")
7. add_stream(stream_name="FEED")
8. add_stream(stream_name="VAP")
9. add_stream(stream_name="LIQ")
10. add_block(block_name="FLASH", block_type="Flash2")
11. connect_block_stream(block_name="FLASH", stream_name="FEED", port_type="F(IN)")
12. connect_block_stream(block_name="FLASH", stream_name="VAP", port_type="V(OUT)")
13. connect_block_stream(block_name="FLASH", stream_name="LIQ", port_type="L(OUT)")
14. set_stream_input_conditions(stream_name="FEED", temp=80, pres=1.01325, ...)
15. set_block_input_specifications(block_name="FLASH", specifications={"TEMP": 80})
16. check_and_run()
17. get_stream_output_conditions(stream_name="VAP")
18. get_stream_output_conditions(stream_name="LIQ")
```

### Example 2: Organic Rankine Cycle (ORC)

See [TestPrompt.txt](./TestPrompt.txt) for detailed ORC simulation workflow using n-Pentane as working fluid.

---

## 🏗 Architecture

```
AspenPlusMCP/
├── aspen_mcp_server_modular.py   # Main MCP server entry point
├── mcp_tools/                     # Modular MCP tool definitions
│   ├── base.py                    # Base handler with shared state
│   ├── core/                      # Connection, file, GUI tools
│   ├── simulation/                # Run, check, diagnose tools
│   ├── blocks/                    # Unit operation tools
│   ├── streams/                   # Stream management tools
│   ├── properties/                # Thermodynamic method tools
│   ├── convergence/               # Convergence control tools
│   ├── components/                # Component list tools
│   └── utils/                     # Timer, unit list tools
├── skills/                        # Setup guides (Claude SKILL.md format)
│   ├── blocks/SKILL.md           # Block configuration guides
│   ├── streams/SKILL.md          # Stream configuration guides
│   └── .../resources/*.md        # Detailed guides
├── aspen_core/                    # Core Python library for Aspen Plus
│   ├── __init__.py                # Package exports
│   ├── base.py                    # Base class with COM connection
│   ├── core.py                    # File operations, GUI control
│   ├── blocks.py                  # Block manipulation
│   ├── streams.py                 # Stream manipulation
│   ├── components.py              # Component management
│   ├── properties.py              # Thermodynamic methods
│   ├── simulation.py              # Simulation control & diagnostics
│   └── utils.py                   # Unit system, timer utilities
├── tests/                         # Test suite
│   ├── __init__.py
│   └── test_orc_mcp.py            # ORC simulation test
├── INSTALL.md                     # Installation guide
├── API_SPECIFICATION.md           # API documentation
├── requirements.txt               # Python dependencies
├── version.json                   # Version information
└── user_test_prompt.md            # Example test prompts
```

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Connection failed** | Ensure Aspen Plus is not showing any dialogs. Run `aspenpls.exe /regserver` as admin. |
| **Import error** | Install `pywin32`: `pip install pywin32` |
| **License popup** | Set `suppress_dialogs(suppress=True)` before operations |
| **COM access denied** | Run MCP client as Administrator |
| **Simulation timeout** | Increase `timeout` parameter in `run_simulation()` |

---

## 📄 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📞 Support

For issues and questions, please [open an issue](https://github.com/conlinkang/AspenPlusMCP/issues) on GitHub.
