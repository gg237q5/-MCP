import os
import asyncio
from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class CoreHandlers(BaseHandler):
    async def _aspen_connect(self, args: Dict[str, Any]) -> List[TextContent]:
        """Connect to AspenPlus via COM interface"""
        version = args.get("version", None)
        
        # Check for orphaned connections
        orphaned_warning = ""
        if hasattr(self, 'check_orphaned_connection'):
            orphaned = self.check_orphaned_connection()
            if orphaned:
                orphaned_warning = (
                    f"\n⚠️ Detected previous unclosed connection:\n"
                    f"   File: {orphaned.get('file_path', 'Unknown')}\n"
                    f"   Connected at: {orphaned.get('connected_at', 'Unknown')}\n"
                    f"   Attempting to clean up and establish new connection...\n\n"
                )

        try:
            # If there is an existing instance, close it first
            if self.aspen_instance:
                try:
                    self.aspen_instance.Close()
                    print("Closed existing AspenPlus instance")
                except:
                    pass

            # Create a new AP instance
            from aspen_core import AP
            self.aspen_instance = AP()

            # Connect to AspenPlus
            self.aspen_instance.AspenConnect(version=version)

            version_info = version if version else "default version"
            
            # Update connection state
            if hasattr(self, 'update_connection_state'):
                self.update_connection_state(connected=True, file_path=None)

            return [TextContent(
                type="text",
                text=f"{orphaned_warning}Successfully connected to AspenPlus ({version_info}).\n\n"
                     f"Connection Status:\n"
                     f"- COM Interface: Active\n"
                     f"- Version: {version_info}\n\n"
                     f"NEXT STEP: Call skills(category='core') then skills(category='core', name='OVERVIEW') for workflow guide.\n\n"
                     f"Then:\n"
                     f"1. Use 'open_aspen_plus' to load a file\n"
                     f"2. Use 'show_aspen_gui' to show/hide the GUI\n"
                     f"3. Use 'suppress_dialogs' to control popup dialogs"
            )]

        except Exception as e:
            # Clean up on failure
            if self.aspen_instance:
                try:
                    self.aspen_instance = None
                except:
                    pass
            
            # Clear connection state
            if hasattr(self, 'update_connection_state'):
                self.update_connection_state(connected=False)

            return [TextContent(
                type="text",
                text=f"Failed to connect to AspenPlus: {str(e)}\n\n"
                     f"Troubleshooting:\n"
                     f"1. Ensure AspenPlus is installed\n"
                     f"2. Check if the version string is correct\n"
                     f"3. Verify COM registration: Run 'aspenpls.exe /regserver' as administrator\n"
                     f"4. Try connecting without specifying version\n"
                     f"5. Close any running AspenPlus instances"
            )]

    async def _is_aspen_connected(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check if AspenPlus is connected"""

        # Check if instance exists
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="AspenPlus is NOT connected.\n\n"
                     "Status: No instance created\n\n"
                     "To connect:\n"
                     "- Use 'aspen_connect' to establish connection\n"
                     "- Or use 'open_aspen_plus' to connect and load a file"
            )]

        try:
            # Use the IsAspenConnected method from AP class
            is_connected = self.aspen_instance.IsAspenConnected()

            if is_connected:
                # Try to get additional info
                try:
                    visible = self.aspen_instance.aspen.Visible
                    visibility_status = "GUI shown" if visible else "GUI hidden"
                except:
                    visibility_status = "Unknown"

                return [TextContent(
                    type="text",
                    text=f"✅ AspenPlus is connected and accessible.\n\n"
                         f"Connection Details:\n"
                         f"- Status: Active\n"
                         f"- GUI Status: {visibility_status}\n"
                         f"- Instance: Ready for operations\n\n"
                         f"Available operations:\n"
                         f"- Load files with 'open_aspen_plus'\n"
                         f"- Control GUI with 'show_aspen_gui'\n"
                         f"- Run simulations\n"
                         f"- Modify model specifications"
                )]
            else:
                return [TextContent(
                    type="text",
                    text="⚠️ AspenPlus connection appears to be lost.\n\n"
                         "Status: Instance exists but not accessible\n\n"
                         "Recommended actions:\n"
                         "1. Try 'close_aspen_connection' to clean up\n"
                         "2. Use 'aspen_connect' to reconnect\n"
                         "3. Check if AspenPlus process is running in Task Manager"
                )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"⚠️ Error checking AspenPlus connection: {str(e)}\n\n"
                     "Status: Connection check failed\n\n"
                     "Possible causes:\n"
                     "1. COM interface error\n"
                     "2. AspenPlus process crashed\n"
                     "3. Connection was interrupted\n\n"
                     "Recommended actions:\n"
                     "1. Use 'close_aspen_connection' to clean up\n"
                     "2. Restart with 'aspen_connect'"
            )]

    async def _close_aspen_connection(self, args: Dict[str, Any]) -> List[TextContent]:
        """Close AspenPlus COM connection"""

        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="No active AspenPlus connection to close.\n\n"
                     "Status: Already disconnected\n\n"
                     "Note: If you want to start fresh, use 'aspen_connect' to establish a new connection."
            )]

        try:
            # Check if there's an open file
            has_file = False
            try:
                # Try to access a property that would indicate a file is loaded
                _ = self.aspen_instance.aspen.Title
                has_file = True
            except:
                pass

            if has_file:
                print("Warning: A file appears to be open. Closing connection will close the file too.")

            # Use the CloseAspenConnection method from AP class
            self.aspen_instance.CloseAspenConnection()

            # Clean up the instance
            self.aspen_instance = None
            
            # 清除連接狀態
            if hasattr(self, 'update_connection_state'):
                self.update_connection_state(connected=False)

            result_text = "Successfully closed AspenPlus connection.\n\n"
            result_text += "Status: Disconnected\n"
            result_text += "COM Interface: Released\n"

            if has_file:
                result_text += "\nNote: Any open file was also closed.\n"
                result_text += "Make sure you saved your work before disconnecting.\n"

            result_text += "\nTo reconnect:\n"
            result_text += "- Use 'aspen_connect' to establish a new connection\n"
            result_text += "- Or use 'open_aspen_plus' to connect and load a file directly"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception as e:
            # Even if there's an error, try to clean up
            try:
                self.aspen_instance = None
            except:
                pass

            return [TextContent(
                type="text",
                text=f"Error while closing AspenPlus connection: {str(e)}\n\n"
                     f"Status: Connection cleanup attempted\n\n"
                     f"The instance has been cleared, but the error suggests:\n"
                     f"1. The connection may already have been lost\n"
                     f"2. AspenPlus process may have crashed\n"
                     f"3. COM interface encountered an error\n\n"
                     f"Recommendation:\n"
                     f"- Check Task Manager for orphaned AspenPlus processes\n"
                     f"- Use 'aspen_connect' to start fresh"
            )]

    def _get_model_status_summary(self):
        """獲取模型狀態摘要的輔助方法"""
        try:
            if not self.aspen_instance:
                return None

            full_status = self.aspen_instance.Check_ModelCompletionStatus(table=True)
            summary = full_status.get('summary', {})
            return summary
        except:
            return None

    async def _create_inp_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Create Aspen Plus input (.inp) file"""
        file_path = args["file_path"]
        components = args["components"]
        cas_numbers = args["cas_numbers"]

        # Validate input
        if len(components) != len(cas_numbers):
            raise ValueError("Number of components does not match number of CAS numbers")

        if not file_path.endswith('.inp'):
            file_path += '.inp'

        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Use CreateInpFile logic from your AP class
        inp_content = """DYNAMICS
    DYNAMICS RESULTS=ON

IN-UNITS SI ENERGY=kJ FLOW='kg/hr' MASS-FLOW='kg/hr'  &
        MOLE-FLOW='kmol/hr' VOLUME-FLOW='cum/hr' ENTHALPY-FLO=kW  &
        MOLE-HEAT-CA='kJ/kmol-K' HEAT-TRANS-C='kW/sqm-K' POWER=kW  &
        PRESSURE=bar SURFACE-TENS='dyne/cm' TEMPERATURE=C  &
        THERMAL-COND='kW/m-K' VISCOSITY=cP DELTA-T=C  &
        MOLE-ENTHALP='MBtu/lbmol' MASS-ENTHALP='kJ/kg'  &
        MOLE-ENTROPY='kJ/kmol-K' MASS-ENTROPY='kJ/kg-K'  &
        ELEC-POWER=kW MASS-HEAT-CA='kJ/kg-K' UA='kJ/sec-K' WORK=kJ  &
        HEAT=kJ PDROP-PER-HT='mbar/m' PDROP=bar  &
        VOL-HEAT-CAP='kJ/cum-K' INVERSE-PRES='1/bar'  &
        INVERSE-HT-C='sqm-K/kW' VOL-ENTHALPY='kJ/cum'

DEF-STREAMS CONVEN ALL

SIM-OPTIONS MASS-BAL-CHE=YES TLOWER=-17.777778 FLASH-MAXIT=100  &
        FLASH-TOL=1E-005 PARADIGM=SM GAMUS-BASIS=AQUEOUS

MODEL-OPTION

DATABANKS 'APV140 PURE40' / 'APV140 AQUEOUS' / 'APV140 SOLIDS' &
         / 'APV140 INORGANIC' / 'APV140 PC-SAFT' / NOASPENPCD

PROP-SOURCES 'APV140 PURE40' / 'APV140 AQUEOUS' /  &
        'APV140 SOLIDS' / 'APV140 INORGANIC' / 'APV140 PC-SAFT'

COMPONENTS """

        for component, cas in zip(components, cas_numbers):
            inp_content += f""" 
        {component}  {cas}/"""

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(inp_content)

        return [TextContent(
            type="text",
            text=f"Successfully created Aspen Plus input file: {file_path}\nComponents: {', '.join(components)}"
        )]

    async def _open_aspen_plus(self, args: Dict[str, Any]) -> List[TextContent]:
        """Open Aspen Plus and load a file"""
        file_path = args["file_path"]

        # Check if the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # # Use your AP class
            # from AP import AP
            #
            # # If there is an existing instance, close it first
            # if self.aspen_instance:
            #     try:
            #         self.aspen_instance.Close()
            #     except:
            #         pass
            #
            # # Create a new instance
            # self.aspen_instance = AP()

            # Load the file
            self.aspen_instance.LoadFile(file_path)
            
            # Update connection state (with file path)
            if hasattr(self, 'update_connection_state'):
                self.update_connection_state(connected=True, file_path=file_path)

            return [TextContent(
                type="text",
                text=f"Successfully opened Aspen Plus.\nFile: {file_path}\n\n"
                     f"NEXT STEP: Call skills(category='core') then skills(category='core', name='OVERVIEW') for workflow guide."
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to open Aspen Plus: {str(e)}"
            )]

    async def _show_aspen_gui(self, args: Dict[str, Any]) -> List[TextContent]:
        """Show or hide the Aspen Plus GUI"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        visible = args["visible"]

        try:
            # Call the Show method from the AP class
            self.aspen_instance.Show(visible)

            status_text = "shown" if visible else "hidden"
            return [TextContent(
                type="text",
                text=f"Aspen Plus GUI is now {status_text}."
            )]

        except TypeError as e:
            return [TextContent(
                type="text",
                text="Parameter error: 'visible' must be a boolean value (True/False)."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to change GUI visibility: {str(e)}"
            )]

    async def _suppress_dialogs(self, args: Dict[str, Any]) -> List[TextContent]:
        """Control whether Aspen Plus dialog boxes are shown"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        suppress = args["suppress"]

        try:
            self.aspen_instance.SuppressDialogs(suppress)

            status_text = "disabled" if suppress else "enabled"
            recommendation = "\nRecommendation: Set to True for automation, False for manual operation." if suppress else ""

            return [TextContent(
                type="text",
                text=f"Aspen Plus pop-up dialogs are {status_text}.{recommendation}"
            )]

        except TypeError as e:
            return [TextContent(
                type="text",
                text="Parameter error: 'suppress' must be a boolean value (True/False)."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to update dialog visibility setting: {str(e)}"
            )]

    async def _save_aspen_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Save the currently open Aspen Plus file"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please open a file using open_aspen_plus first."
            )]

        try:
            self.aspen_instance.Save()
            return [TextContent(
                type="text",
                text="Successfully saved the current Aspen Plus file."
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to save the file: {str(e)}"
            )]

    async def _save_aspen_file_as(self, args: Dict[str, Any]) -> List[TextContent]:
        """Save the current Aspen Plus file with a new filename"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please open a file using open_aspen_plus first."
            )]

        filename = args["filename"]

        try:
            # Call the SaveAs method from the AP class (automatically handles .inp to .bkp conversion)
            self.aspen_instance.SaveAs(filename)

            # Check for extension conversion
            file_path, file_ext = os.path.splitext(filename)
            final_filename = filename
            if file_ext.lower() == '.inp':
                final_filename = file_path + '.bkp'

            return [TextContent(
                type="text",
                text=f"Successfully saved the file as: {final_filename}"
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to save the file: {str(e)}"
            )]

    async def _close_aspen(self, args: Dict[str, Any]) -> List[TextContent]:
        """Close Aspen Plus"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running."
            )]

        try:
            self.aspen_instance.Close()
            self.aspen_instance = None
            
            # 清除連接狀態
            if hasattr(self, 'update_connection_state'):
                self.update_connection_state(connected=False)
            
            return [TextContent(
                type="text",
                text="Aspen Plus has been closed."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to close Aspen Plus: {str(e)}"
            )]

    async def _list_aspen_info(self, args: Dict[str, Any]) -> List[TextContent]:
        """List Aspen Plus file information"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running."
            )]

        info_type = args["info_type"]

        try:
            result = ""

            if info_type in ["blocks", "all"]:
                blocks = self.aspen_instance.BlocksList()
                result += f"Blocks ({len(blocks)}):\n"
                for block in blocks:
                    block_name, block_type = block
                    result += f"  - {block_name} ({block_type})\n"
                result += "\n"

            if info_type in ["streams", "all"]:
                streams = self.aspen_instance.StreamsList()
                result += f"Streams ({len(streams)}):\n"
                for stream in streams:
                    stream_name, stream_type = stream
                    result += f"  - {stream_name} ({stream_type})\n"
                result += "\n"

            if info_type in ["components", "all"]:
                components = self.aspen_instance.ComponentsList()
                result += f"Components ({len(components)}):\n"
                for component in components:
                    result += f"  - {component}\n"

            return [TextContent(
                type="text",
                text=result.strip()
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve Aspen information: {str(e)}"
            )]

    async def _export_file(self, args: Dict[str, Any]) -> List[TextContent]:
        """Export Aspen Plus file to various formats"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please open a file using open_aspen_plus first."
            )]

        export_type_str = args["export_type"]
        file_path = args["file_path"]

        # Import centralized constants
        from aspen_core.constants import ExportType

        try:
            export_type = ExportType.get_value(export_type_str)
        except ValueError as e:
            return [TextContent(
                type="text",
                text=str(e)
            )]

        try:
            # Call the Export method from the AP class
            self.aspen_instance.Export(export_type, file_path)

            return [TextContent(
                type="text",
                text=f"Successfully exported file.\n\n"
                     f"Export Type: {ExportType.get_description(export_type)}\n"
                     f"File Path: {file_path}\n\n"
                     f"Tip: For 'inp' exports, reopen the file in Aspen Plus to get an auto-arranged flowsheet layout."
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to export file: {str(e)}"
            )]


