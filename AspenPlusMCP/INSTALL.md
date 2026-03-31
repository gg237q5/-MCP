# Aspen Plus MCP Server Installation Guide

This guide describes how to install and configure the Aspen Plus MCP Server on your local machine to work with Antigravity or other MCP clients.

## 1. Prerequisites

### Software Requirements
- **OS**: Windows 10/11 (Required for Aspen Plus COM interface)
- **Aspen Plus**: Version V12, V14, or higher must be installed and licensed.
- **Python**: Version 3.10 or higher.

### Verify Aspen Plus Installation
To ensure the MCP server can connect, ensure Aspen Plus is installed and the COM interface is registered.
Open a terminal (cmd/PowerShell) as Administrator and run:
```powershell
aspenpls.exe /regserver
```
*(Note: If `aspenpls.exe` is not in your PATH, navigate to the Aspen Plus installation directory first, typically `C:\Program Files\AspenTech\Aspen Plus V14\GUI`)*

## 2. Project Setup

### Install Dependencies
1. Open a terminal in the project directory: `D:\AspenPlusMCP`
2. Create and activate a virtual environment (Recommended):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. Install required Python packages:
   ```powershell
   pip install -r requirements.txt
   ```
   *(Content of requirements.txt: `mcp`, `pywin32`)*

## 3. Configuration for Antigravity / Claude Desktop

To use this MCP server, you need to add it to your MCP client configuration file.

### Configuration File Location
- **Claude Desktop**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Antigravity**: Check your specific agent configuration settings or workflow definitions.

### Configuration JSON
Add the following entry to the `mcpServers` object in your config file:

```json
{
  "mcpServers": {
    "aspen-plus": {
      "command": "python",
      "args": [
        "D:\\AspenPlusMCP\\aspen_mcp_server_modular.py"
      ]
    }
  }
}
```

**Important**: 
- If using a virtual environment, replace `"python"` with the absolute path to your venv python executable, e.g., `"D:\\AspenPlusMCP\\venv\\Scripts\\python.exe"`.
- Ensure the path to `aspen_mcp_server_modular.py` is correct.

## 4. Testing the Installation

1. **Restart your MCP Client** (Antigravity/Claude Desktop).
2. The client should automatically connect to the Aspen Plus MCP Server.
3. You verify the connection by asking the agent:
   > "Check if Aspen Plus is connected."
   or
   > "List available tools."

## 5. Troubleshooting

- **Connection Failed**: Ensure Aspen Plus is not showing a license popup or error dialog blocking the connection.
- **Import Error**: Ensure you installed `pywin32` (`pip install pywin32`).
- **Access Denied**: Try running the MCP Client as Administrator if regular permissions fail to access the COM object.
