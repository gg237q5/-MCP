# Aspen Plus MCP Server - API Specification

Version: 1.2.0  
Last Updated: 2026-02-06

---

## Overview

The Aspen Plus MCP Server implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) standard, enabling AI assistants to interact with Aspen Plus process simulation software through a standardized tool interface.

## Server Information

| Property | Value |
|----------|-------|
| Protocol | MCP (Model Context Protocol) |
| Transport | stdio |
| Server Name | `aspen-plus` |
| Entry Point | `aspen_mcp_server_modular.py` |

---

## Tool Schema Reference

### Core Tools

#### `aspen_connect`
Establish COM connection to Aspen Plus.

```json
{
  "name": "aspen_connect",
  "inputSchema": {
    "type": "object",
    "properties": {
      "version": {
        "type": "string",
        "description": "AspenPlus version string (e.g., 'Apwn36.0' for V10.0)"
      }
    },
    "required": []
  }
}
```

#### `is_aspen_connected`
Check connection status.

```json
{
  "name": "is_aspen_connected",
  "inputSchema": {
    "type": "object",
    "properties": {},
    "required": []
  }
}
```

#### `close_aspen_connection`
Close COM connection without closing file.

```json
{
  "name": "close_aspen_connection",
  "inputSchema": {
    "type": "object",
    "required": []
  }
}
```

#### `create_inp_file`
Create Aspen Plus input file.

```json
{
  "name": "create_inp_file",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" },
      "components": { "type": "array", "items": { "type": "string" } },
      "cas_numbers": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["file_path", "components", "cas_numbers"]
  }
}
```

#### `open_aspen_plus`
Open and load a file.

```json
{
  "name": "open_aspen_plus",
  "inputSchema": {
    "type": "object",
    "properties": {
      "file_path": { "type": "string" }
    },
    "required": ["file_path"]
  }
}
```

#### `show_aspen_gui`
Control GUI visibility.

```json
{
  "name": "show_aspen_gui",
  "inputSchema": {
    "type": "object",
    "properties": {
      "visible": { "type": "boolean" }
    },
    "required": ["visible"]
  }
}
```

#### `suppress_dialogs`
Suppress pop-up dialogs.

```json
{
  "name": "suppress_dialogs",
  "inputSchema": {
    "type": "object",
    "properties": {
      "suppress": { "type": "boolean" }
    },
    "required": ["suppress"]
  }
}
```

#### `save_aspen_file`
Save current file.

```json
{
  "name": "save_aspen_file",
  "inputSchema": { "type": "object", "required": [] }
}
```

#### `save_aspen_file_as`
Save with new filename.

```json
{
  "name": "save_aspen_file_as",
  "inputSchema": {
    "type": "object",
    "properties": {
      "filename": { "type": "string" }
    },
    "required": ["filename"]
  }
}
```

#### `close_aspen`
Close Aspen Plus.

```json
{
  "name": "close_aspen",
  "inputSchema": { "type": "object", "required": [] }
}
```

#### `list_aspen_info`
List model information.

```json
{
  "name": "list_aspen_info",
  "inputSchema": {
    "type": "object",
    "properties": {
      "info_type": {
        "type": "string",
        "enum": ["blocks", "streams", "components", "all"]
      }
    },
    "required": ["info_type"]
  }
}
```

---

### Simulation Tools

#### `check_model_completion_status`
Check model readiness.

```json
{
  "name": "check_model_completion_status",
  "inputSchema": {
    "type": "object",
    "properties": {
      "show_complete": { "type": "boolean", "default": false }
    },
    "required": []
  }
}
```

#### `get_incomplete_items`
Get items needing attention.

```json
{
  "name": "get_incomplete_items",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": {
        "type": "string",
        "enum": ["streams", "blocks", "other_nodes"]
      },
      "issue_type": {
        "type": "string",
        "enum": ["needs_attention", "has_errors", "has_warnings", "complete_success", "complete_no_results", "no_results", "disabled_or_not_run", "inaccessible", "incompatible", "unknown"],
        "default": "needs_attention"
      }
    },
    "required": []
  }
}
```


#### `reinitialize`
Reinitialize the simulation engine.

```json
{
  "name": "reinitialize",
  "inputSchema": { "type": "object", "required": [] }
}
```

#### `run_simulation`
Execute simulation.

```json
{
  "name": "run_simulation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "wait_for_completion": { "type": "boolean", "default": true },
      "timeout": { "type": "integer", "default": 300 }
    },
    "required": []
  }
}
```

#### `run_and_report`
Run with detailed report.

```json
{
  "name": "run_and_report",
  "inputSchema": {
    "type": "object",
    "properties": {
      "detailed_report": { "type": "boolean", "default": true },
      "wait_for_completion": { "type": "boolean", "default": true },
      "timeout": { "type": "integer", "default": 300 }
    },
    "required": []
  }
}
```

#### `check_and_run`
Smart check and run.

```json
{
  "name": "check_and_run",
  "inputSchema": {
    "type": "object",
    "properties": {
      "auto_fix_attempt": { "type": "boolean", "default": false }
    },
    "required": []
  }
}
```

---

### Block Tools

#### `get_blocks_list`
```json
{ "name": "get_blocks_list", "inputSchema": { "type": "object", "required": [] } }
```

#### `get_block_ports`
```json
{
  "name": "get_block_ports",
  "inputSchema": {
    "type": "object",
    "properties": { "block_name": { "type": "string" } },
    "required": ["block_name"]
  }
}
```

#### `get_block_connections`
```json
{
  "name": "get_block_connections",
  "inputSchema": {
    "type": "object",
    "properties": { "block_name": { "type": "string" } },
    "required": ["block_name"]
  }
}
```

#### `add_block`
```json
{
  "name": "add_block",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string", "description": "≤ 8 characters" },
      "block_type": { "type": "string" }
    },
    "required": ["block_name", "block_type"]
  }
}
```

**Supported Block Types:**
- Separators: `Flash2`, `Flash3`, `Decanter`, `Sep`, `Sep2`
- Columns: `RADFRAC`, `DSTWU`, `Distl`, `Extract`
- Reactors: `RSTOIC`, `RYIELD`, `RGIBBS`, `RCSTR`, `RPLUG`, `RBATCH`
- Heat Transfer: `Heater`, `HeatX`, `MHeatX`
- Pressure Change: `Pump`, `Compr`, `MCompr`, `Valve`, `Pipe`
- Mixers/Splitters: `Mixer`, `FSplit`

#### `connect_block_stream`
```json
{
  "name": "connect_block_stream",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string" },
      "stream_name": { "type": "string" },
      "port_type": { "type": "string", "description": "e.g., F(IN), VD(OUT), B(OUT)" }
    },
    "required": ["block_name", "stream_name", "port_type"]
  }
}
```

#### `get_block_input_specifications`
```json
{
  "name": "get_block_input_specifications",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string" },
      "specification_names": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["block_name"]
  }
}
```

#### `set_block_input_specifications`
```json
{
  "name": "set_block_input_specifications",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string" },
      "specifications": {
        "type": "object",
        "description": "Format: {spec_name: value} or {spec_name: {value, unit, basis}}"
      }
    },
    "required": ["block_name", "specifications"]
  }
}
```

#### `remove_block`
```json
{
  "name": "remove_block",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string" },
      "force": { "type": "boolean", "default": false }
    },
    "required": ["block_name"]
  }
}
```

#### `get_block_output_specifications`
```json
{
  "name": "get_block_output_specifications",
  "inputSchema": {
    "type": "object",
    "properties": {
      "block_name": { "type": "string" },
      "specification_names": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["block_name"]
  }
}
```

---

### Stream Tools

#### `get_streams_list`
```json
{ "name": "get_streams_list", "inputSchema": { "type": "object", "required": [] } }
```

#### `add_stream`
```json
{
  "name": "add_stream",
  "inputSchema": {
    "type": "object",
    "properties": {
      "stream_name": { "type": "string", "description": "≤ 8 characters" },
      "stream_type": { "type": "string", "default": "MATERIAL" }
    },
    "required": ["stream_name"]
  }
}
```

**Stream Types:** `MATERIAL`, `HEAT`, `WORK`

#### `remove_stream`
```json
{
  "name": "remove_stream",
  "inputSchema": {
    "type": "object",
    "properties": {
      "stream_name": { "type": "string" },
      "force": { "type": "boolean", "default": false }
    },
    "required": ["stream_name"]
  }
}
```

#### `get_stream_input_conditions_list`
```json
{
  "name": "get_stream_input_conditions_list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "stream_name": { "type": "string" },
      "specification_names": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["stream_name"]
  }
}
```

#### `set_stream_input_conditions`
```json
{
  "name": "set_stream_input_conditions",
  "inputSchema": {
    "type": "object",
    "properties": {
      "stream_name": { "type": "string" },
      "temp": { "type": "number", "description": "Temperature (°C)" },
      "pres": { "type": "number", "description": "Pressure (bar)" },
      "specifications_dict": { "type": "object" }
    },
    "required": ["stream_name"]
  }
}
```

#### `get_stream_output_conditions`
```json
{
  "name": "get_stream_output_conditions",
  "inputSchema": {
    "type": "object",
    "properties": {
      "stream_name": { "type": "string" },
      "specification_names": { "type": "array", "items": { "type": "string" } }
    },
    "required": ["stream_name"]
  }
}
```

---

### Convergence Tools

#### `get_input_convergence`
Retrieve convergence specifications.

```json
{
  "name": "get_input_convergence",
  "inputSchema": {
    "type": "object",
    "properties": {
      "specification_names": { "type": "array", "items": { "type": "string" } },
      "page": { "type": "integer", "default": 1 },
      "page_size": { "type": "integer", "default": 25 }
    },
    "required": []
  }
}
```

#### `set_input_convergence`
Set convergence parameters.

```json
{
  "name": "set_input_convergence",
  "inputSchema": {
    "type": "object",
    "properties": {
      "tol": { "type": "number" },
      "weg_maxit": { "type": "integer" },
      "specifications_dict": { "type": "object" }
    },
    "required": []
  }
}
```

---

### Properties Tools

#### `add_thermo_method`
```json
{
  "name": "add_thermo_method",
  "inputSchema": {
    "type": "object",
    "properties": {
      "method_name": { "type": "string" }
    },
    "required": ["method_name"]
  }
}
```

**Supported Methods:**
`BK10`, `CHAO-SEA`, `CPA`, `ELECNRTL`, `ENRTL-RK`, `ENRTL-SR`, `IAPWS-95`, `IDEAL`, `NRTL`, `NRTL-SAC`, `PC-SAFT`, `PENG-ROB`, `POLYNRTL`, `PSRK`, `SOLIDS`, `SRK`, `UNIFAC`, `UNIQUAC`, `VTPR`, `WILSON`, `WILS-GLR`, `IF97`, `PITZER`

#### `get_properties_list`
Get available property specifications.

```json
{
  "name": "get_properties_list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "page": { "type": "integer", "default": 1 },
      "page_size": { "type": "integer", "default": 50 }
    },
    "required": []
  }
}
```

---

### Component Tools

#### `get_components_list`
```json
{ "name": "get_components_list", "inputSchema": { "type": "object", "required": [] } }
```

---

### Utility Tools

#### `timer`
```json
{
  "name": "timer",
  "inputSchema": {
    "type": "object",
    "properties": {
      "start_time": { "type": "string", "description": "Format: YYYY-MM-DD HH:MM:SS" }
    },
    "required": []
  }
}
```

#### `unit_list`
```json
{
  "name": "unit_list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "item": {
        "type": "array",
        "items": { "type": "integer" },
        "description": "[] = all categories, [n] = units in cat n, [n,m] = unit m in cat n"
      }
    },
    "required": []
  }
}
```

#### `get_version`
```json
{ "name": "get_version", "inputSchema": { "type": "object", "required": [] } }
```

#### `skills`
Get setup guides and documentation.

```json
{
  "name": "skills",
  "inputSchema": {
    "type": "object",
    "properties": {
      "category": { "type": "string", "description": "e.g., blocks, streams" },
      "name": { "type": "string", "description": "e.g., RADFRAC, MATERIAL" }
    },
    "required": []
  }
}
```

---

## Error Handling

All tools return responses in this format:

**Success:**
```json
{
  "content": [
    { "type": "text", "text": "Operation result message" }
  ]
}
```

**Error:**
```json
{
  "content": [
    { "type": "text", "text": "Error: Description of what went wrong" }
  ],
  "isError": true
}
```

---

## Common Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| `COM connection failed` | Aspen Plus not running or not registered | Run `aspenpls.exe /regserver` as admin |
| `File not found` | Invalid file path | Verify file path and extension |
| `Block not found` | Block name doesn't exist | Use `get_blocks_list` to verify |
| `Stream not found` | Stream name doesn't exist | Use `get_streams_list` to verify |
| `Simulation timeout` | Model too complex | Increase `timeout` parameter |
| `Model incomplete` | Missing required inputs | Run `check_model_completion_status` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-26 | Initial release with 35 tools |
| 1.1.0 | 2026-01-13 | Added skills tool, property pagination, and doc updates |
| 1.2.0 | 2026-02-06 | Added reinitialize tool, check_and_run improvements, and Convergence module documentation |
