import asyncio
import os
import sys
import atexit
import signal
import json
from datetime import datetime

# Add the current directory to sys.path to ensure modules can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Project root for connection state file
PROJECT_ROOT = current_dir
CONNECTION_STATE_FILE = os.path.join(PROJECT_ROOT, "connection_state.json")

from mcp.server import Server
import mcp.types as types
import mcp.server.stdio

from mcp_tools.core.handlers import CoreHandlers
from mcp_tools.blocks.handlers import BlockHandlers
from mcp_tools.streams.handlers import StreamHandlers
from mcp_tools.components.handlers import ComponentHandlers
from mcp_tools.simulation.handlers import SimulationHandlers
from mcp_tools.properties.handlers import PropertyHandlers
from mcp_tools.convergence.handlers import ConvergenceHandlers
from mcp_tools.reactions.handlers import ReactionHandlers
from mcp_tools.utils.handlers import UtilsHandlers
from mcp_tools.base import BaseHandler

from mcp_tools.core.tools import tools as core_tools
from mcp_tools.blocks.tools import tools as block_tools
from mcp_tools.streams.tools import tools as stream_tools
from mcp_tools.components.tools import tools as component_tools
from mcp_tools.simulation.tools import tools as simulation_tools
from mcp_tools.properties.tools import tools as property_tools
from mcp_tools.convergence.tools import tools as convergence_tools
from mcp_tools.reactions.tools import tools as reaction_tools
from mcp_tools.utils.tools import tools as utils_tools

class AspenMCPServer(
    CoreHandlers,
    BlockHandlers,
    StreamHandlers,
    ComponentHandlers,
    SimulationHandlers,
    PropertyHandlers,
    ConvergenceHandlers,
    ReactionHandlers,
    UtilsHandlers,
    BaseHandler
):
    def __init__(self):
        super().__init__()
        self.app = Server("AspenPlusMCP")
        self.aspen_instance = None
        self._cleanup_done = False
        self._register_tools()
        self._register_cleanup_handlers()

    def _register_cleanup_handlers(self):
        """Register cleanup handlers for graceful shutdown"""
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        # Windows compatibility: SIGTERM may not be available
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle termination signals"""
        print(f"\nReceived signal {signum}, cleaning up Aspen Plus connection...", file=sys.stderr)
        self._cleanup()
        sys.exit(0)

    def _cleanup(self):
        """Clean up Aspen Plus connection and update state file"""
        if self._cleanup_done:
            return
        self._cleanup_done = True
        
        if self.aspen_instance:
            try:
                print("Closing Aspen Plus connection...", file=sys.stderr)
                self.aspen_instance.Close()
                print("Aspen Plus connection closed successfully.", file=sys.stderr)
            except Exception as e:
                print(f"Cleanup error: {e}", file=sys.stderr)
            finally:
                self.aspen_instance = None
        
        # 清除連接狀態檔
        self._clear_connection_state()

    def _clear_connection_state(self):
        """Clear connection state file"""
        try:
            if os.path.exists(CONNECTION_STATE_FILE):
                os.remove(CONNECTION_STATE_FILE)
        except Exception as e:
            print(f"Failed to clear connection state file: {e}", file=sys.stderr)

    def update_connection_state(self, connected: bool, file_path: str = None):
        """Update connection state file (called by handlers)"""
        if connected:
            state = {
                "is_connected": True,
                "file_path": file_path,
                "connected_at": datetime.now().isoformat(),
                "pid": os.getpid()
            }
            try:
                with open(CONNECTION_STATE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2)
            except Exception as e:
                print(f"Failed to update connection state file: {e}", file=sys.stderr)
        else:
            self._clear_connection_state()

    def check_orphaned_connection(self) -> dict:
        """Check for orphaned connections (called by handlers)"""
        if os.path.exists(CONNECTION_STATE_FILE):
            try:
                with open(CONNECTION_STATE_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                if state.get("is_connected"):
                    return state
            except Exception:
                pass
        return None

    def __del__(self):
        """Fallback cleanup on garbage collection"""
        self._cleanup()

    def _register_tools(self):
        """Register all tools with the MCP server"""
        
        all_tools_list = (
            core_tools +
            block_tools +
            stream_tools +
            component_tools +
            simulation_tools +
            property_tools +
            convergence_tools +
            reaction_tools +
            utils_tools
        )

        @self.app.list_tools()
        async def list_tools() -> list[types.Tool]:
            return all_tools_list

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            # Map tool names to their handler methods
            # Convention: tool 'name' -> handler '_name'
            method_name = f"_{name}"
            
            if hasattr(self, method_name):
                method = getattr(self, method_name)
                try:
                    return await method(arguments)
                except Exception as e:
                    return [types.TextContent(
                        type="text",
                        text=f"Error executing tool '{name}': {str(e)}"
                    )]
            else:
                 return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def run(self):
        """Start the MCP server using stdio protocol"""
        import traceback
        try:
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.app.run(
                    read_stream,
                    write_stream,
                    self.app.create_initialization_options()
                )
        except Exception as e:
            print("MCP Server failed to start.", file=sys.stderr)
            print("Error details:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        finally:
            self._cleanup()

async def main():
    server = AspenMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
