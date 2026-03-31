import io
import contextlib
from typing import Dict, Any, List, Optional
from mcp.types import TextContent
from ..base import BaseHandler

class BlockHandlers(BaseHandler):
    async def _get_blocks_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all blocks in the simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        blocks = self.aspen_instance.BlocksList()
        result = f"Blocks list ({len(blocks)} blocks):\n"
        for block_name, block_type in blocks:
            result += f"- {block_name} (Type: {block_type})\n"

        return [TextContent(
            type="text",
            text=result
        )]

    async def _get_block_ports(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get ports for a specific block"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        block_name = args["block_name"]
        
        # Verify block exists
        blocks = [b[0] for b in self.aspen_instance.BlocksList()]
        if block_name not in blocks:
             return [TextContent(
                type="text",
                text=f"Block '{block_name}' not found. Please check the block name using get_blocks_list."
            )]

        try:
            ports = self.aspen_instance.BlockPortList(block_name)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve ports for block '{block_name}': {str(e)}"
            )]
        
        if not ports:
            return [TextContent(
                type="text",
                text=f"No ports found for block '{block_name}'."
            )]
        
        result = f"Ports for block '{block_name}':\n"
        for port in ports:
            # Handle different port data formats robustly
            if isinstance(port, (list, tuple)):
                if len(port) >= 3:
                    # Expected format: [Name, Description, Direction]
                    result += f"- {port[0]}: {port[1]} ({port[2]})\n"
                elif len(port) == 2:
                    # Format: [Name, Description] or [Name, Direction]
                    result += f"- {port[0]}: {port[1]}\n"
                elif len(port) == 1:
                    result += f"- {port[0]}\n"
                else:
                    result += f"- (empty port entry)\n"
            else:
                # If port is just a string or other type
                result += f"- {str(port)}\n"

        return [TextContent(
            type="text",
            text=result
        )]

    async def _get_block_connections(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get connections for a specific block"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        block_name = args["block_name"]
        
        # Verify block exists
        blocks = [b[0] for b in self.aspen_instance.BlocksList()]
        if block_name not in blocks:
             return [TextContent(
                type="text",
                text=f"Block '{block_name}' not found. Please check the block name using get_blocks_list."
            )]

        connections = self.aspen_instance.Connections(block_name, table=True)
        
        result = f"Connections for block '{block_name}':\n"
        if not connections:
            result += "No connections found."
        else:
            for conn in connections:
                # Format depends on your AP.py implementation, usually list of strings or tuples
                result += f"- {str(conn)}\n"

        return [TextContent(
            type="text",
            text=result
        )]

    async def _add_block(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add a new block to the simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        block_name = args["block_name"]
        block_type = args["block_type"]

        try:
            self.aspen_instance.Add_Block(block_name, block_type)
            return [TextContent(
                type="text",
                text=f"Successfully added block '{block_name}' of type '{block_type}'.\n\n"
                     f"NEXT STEP: Call skills(category='blocks') then skills(category='blocks', name='{block_type}') for configuration guide."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to add block: {str(e)}"
            )]

    async def _connect_block_stream(self, args: Dict[str, Any]) -> List[TextContent]:
        """Connect a stream to a block port"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        block_name = args["block_name"]
        stream_name = args["stream_name"]
        port_type = args["port_type"]

        try:
            # Assuming AP class has a ConnectStream method or similar
            self.aspen_instance.Connect_Block2Stream(block_name, stream_name, port_type)
            
            return [TextContent(
                type="text",
                text=f"Successfully connected stream '{stream_name}' to port '{port_type}' of block '{block_name}'."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to connect stream: {str(e)}"
            )]

    async def _get_block_input_specifications(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve input specifications for a block - supports quick view (paginated) and detailed query"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        block_name = args["block_name"]
        specification_names = args.get("specification_names", None)
        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        # Constants
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            # Retrieve all specs
            all_specs = self.aspen_instance.Get_BlockInputSpecificationsList(block_name, table=True)

            if not all_specs:
                return [TextContent(
                    type="text",
                    text=f"No configurable input specifications found for block '{block_name}'.\n"
                         f"Please verify the block name and ensure it is a valid unit operation block."
                )]
            
            # Get block type
            block_type = None
            for b in self.aspen_instance.BlocksList():
                if b[0] == block_name.upper():
                    block_type = b[1]
                    break
            
            if specification_names is None:
                # Quick view mode with pagination
                import math
                
                spec_items = list(all_specs.items())
                total_specs = len(spec_items)
                total_pages = math.ceil(total_specs / page_size) if total_specs > 0 else 1
                
                # Validate page number
                page = max(1, min(page, total_pages))
                
                # Calculate pagination range
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, total_specs)
                
                # Get current page specs
                current_page_specs = spec_items[start_idx:end_idx]
                
                # Build output
                result = f"Block '{block_name}' ({block_type}) Input Specifications\n"
                result += "=" * 60 + "\n"
                
                if total_pages == 1:
                    result += f"📄 Showing all {total_specs} specs\n\n"
                else:
                    result += f"📄 Page {page} of {total_pages} | Showing specs {start_idx+1}-{end_idx} of {total_specs}\n\n"
                
                result += "─" * 60 + "\n"
                
                # Format each spec
                for idx, (spec_path, spec_info) in enumerate(current_page_specs, start=start_idx+1):
                    result += f"{idx}. {spec_path}\n"
                    result += f"   Description: {spec_info.get('description', 'N/A')}\n"
                    result += f"   Value: {spec_info.get('value')}\n"
                    result += f"   Unit: {spec_info.get('unit')} (category: {spec_info.get('unit_category')})\n"
                    result += f"   Basis: {spec_info.get('basis')}\n"
                    if spec_info.get('options'):
                        result += f"   Options: {spec_info.get('options')}\n"
                    result += "\n"
                
                result += "─" * 60 + "\n"
                
                # Check output size and add warning if needed
                if len(result) > OUTPUT_SIZE_WARNING_THRESHOLD:
                    suggested_size = max(10, page_size // 2)
                    result += f"\n⚠️ WARNING: Output size is large ({len(result)} chars).\n"
                    result += f"   If errors occur, try: page_size={suggested_size}\n"
                
                # Pagination info
                result += "\n📊 Pagination Info:\n"
                if total_pages == 1:
                    result += f"   • Total: {total_specs} specs (all displayed)\n"
                else:
                    result += f"   • Page {page} of {total_pages}"
                    if page == total_pages:
                        result += " (LAST PAGE)\n"
                    else:
                        result += "\n"
                    result += f"   • Showing: {end_idx - start_idx} specs\n"
                    result += f"   • Total: {total_specs} specs\n"
                
                # Navigation
                if page < total_pages:
                    result += f"\n⏭️ MORE SPECS AVAILABLE!\n"
                    result += f"   Call: get_block_input_specifications(block_name='{block_name}', page={page+1})\n"
                elif total_pages > 1:
                    result += f"\n✅ All specs have been displayed across {total_pages} pages.\n"
                
                # Detailed query tip
                result += f"\nTo set specifications:\n"
                result += f"   set_block_input_specifications(block_name='{block_name}', specifications={{'SPEC_NAME': value}})\n"
                result += f"\nNEXT STEP: Call skills(category='blocks') then skills(category='blocks', name='{block_type}') for configuration guide.\n"

                return [TextContent(type="text", text=result)]

            else:
                # Detailed query mode
                filtered_specs = {}
                not_found = []

                for name in specification_names:
                    if name in all_specs:
                        filtered_specs[name] = all_specs[name]
                    else:
                        not_found.append(name)

                result = ""
                if filtered_specs:
                    result += f"Detailed Input Specifications for Block '{block_name}':\n"
                    result += "=" * 50 + "\n"
                    
                    import json
                    # Use json dumps for pretty printing dictionary structure
                    result += json.dumps(filtered_specs, indent=2, ensure_ascii=False)
                    result += "\n\n"
                    
                    # Add dynamic unit_category guidance for LLM
                    # Collect unique unit categories from filtered specs
                    unit_categories = set()
                    for spec_info in filtered_specs.values():
                        if spec_info.get('unit_category'):
                            unit_categories.add(spec_info['unit_category'])
                    
                    if unit_categories:
                        result += "📋 Unit Category Reference (from returned specs):\n"
                        result += "-" * 50 + "\n"
                        result += "Each spec includes 'unit_category' field. To find available units, call:\n"
                        for cat in sorted(unit_categories):
                            result += f"  - unit_list(item=[{cat}])  # for unit_category={cat}\n"
                        result += "\nThe 'unit' field shows the current unit name.\n"
                        result += "Use `unit_list()` to see all available unit categories.\n\n"

                if not_found:
                    result += "⚠️ The following specifications were not found:\n"
                    for name in not_found:
                        result += f"- {name}\n"
                    result += "\nTip: Use Quick View mode (no specification_names) to see all valid spec names."

                return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve input specifications for block '{block_name}': {str(e)}"
            )]

    async def _set_block_input_specifications(self, args: Dict[str, Any]) -> List[TextContent]:
        """Set input specifications for a block"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        block_name = args["block_name"]
        specifications = args["specifications"]

        if not specifications:
            return [TextContent(
                type="text",
                text=f"No specifications were provided for block '{block_name}'."
            )]

        try:
            # Check the connection status of the block first
            connection_info = ""
            connection_count = 0
            try:
                connections = self.aspen_instance.Connections(block_name, table=True)
                connection_count = len(connections) if connections else 0
                
                connection_info += f"Connection check for block '{block_name}':\n"
                connection_info += f"Number of connected streams: {connection_count}\n"
                
                if connection_count == 0:
                    connection_info += "Warning: This block has no connected streams.\n"
                    connection_info += "Some specifications may not be applied correctly.\n"
                else:
                    connection_info += f"Connected streams: {', '.join(connections)}\n"
                
                connection_info += "\n"

            except Exception as conn_error:
                connection_info = f"Unable to check connections for block '{block_name}': {str(conn_error)}\n\n"

            # Capture output from Set_BlockInputSpecifications
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                self.aspen_instance.Set_BlockInputSpecifications(block_name, specifications_dict=specifications)
            
            # 獲取設定過程的詳細輸出
            setting_output = f.getvalue()

            # Construct result message
            result = connection_info
            result += f"Specification setting result for block '{block_name}':\n"
            result += "=" * 50 + "\n"

            # 如果有捕獲到輸出，顯示詳細的設定過程
            if setting_output.strip():
                result += "Detailed log:\n"
                result += "-" * 30 + "\n"
                result += setting_output
                result += "\n"

            # Summary
            result += "Summary of specifications set:\n"
            result += "-" * 30 + "\n"
            
            successful_specs = 0
            for spec_name, value in specifications.items():
                result += f"{spec_name}: {value}\n"
                successful_specs += 1
                
            result += f"\nTotal specifications applied: {successful_specs}\n"
            
            result += "\nRecommendations:\n"
            if connection_count == 0:
                result += "- Use get_block_connections to verify and ensure necessary stream connections\n"
                result += "- Use connect_block_stream to add input/output streams\n"
            else:
                result += "- Stream connections appear to be valid\n"
                
            result += f"- Use get_block_input_specifications('{block_name}') to verify applied values\n"
            result += "- Use check_model_completion_status to check model readiness\n"
            result += "\nNEXT STEP: Call skills(category='blocks') for block configuration best practices.\n"
            
            return [TextContent(
                type="text",
                text=result
            )]

        except Exception as e:
            # Detailed error message
            error_msg = f"Failed to set specifications for block '{block_name}':\n"
            error_msg += "=" * 50 + "\n"
            error_msg += f"Error: {str(e)}\n\n"
            
            error_msg += "Input parameters:\n"
            error_msg += f"   - Block name: {repr(block_name)}\n"
            error_msg += f"   - Number of specifications: {len(specifications)}\n"
            
            error_msg += "\nSpecification details:\n"
            for spec_name, value in specifications.items():
                error_msg += f"   - Spec name: {repr(spec_name)}\n"
                error_msg += f"   - Value: {repr(value)}\n"
                
            error_msg += "\nTroubleshooting tips:\n"
            error_msg += "1. Use get_block_connections to verify block connection status\n"
            error_msg += "2. Use get_block_input_specifications to retrieve valid spec names\n"
            error_msg += "3. Check for exact case-sensitive match of spec names\n"
            error_msg += "4. Ensure necessary streams are connected to the block\n"
            error_msg += "5. Check that values are within valid data type and range\n"
            error_msg += f"6. Use get_blocks_list to verify that '{block_name}' exists\n"

            return [TextContent(
                type="text",
                text=error_msg
            )]

    async def _remove_block(self, args: Dict[str, Any]) -> List[TextContent]:
        """Remove a unit operation block from the Aspen Plus model"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to launch the file."
            )]

        block_name = args["block_name"]
        force = args.get("force", False)

        try:
            # Call Aspen API to remove the block
            result = self.aspen_instance.Remove_Block(block_name, force=force)

            # Extract result
            status = result['status']
            message = result['message']

            if status == 'SUCCESS':
                result_text = f"Successfully removed block: {block_name}\n"
                result_text += f"Message: {message}\n"

                if 'had_connected_streams' in result and result['had_connected_streams']:
                    result_text += f"Previously connected streams: {', '.join(result['had_connected_streams'])}\n"
                    result_text += "Note: These streams still exist but are now disconnected.\n"

                result_text += "\nSuggestions:\n"
                result_text += "- Use get_blocks_list to confirm removal\n"
                result_text += "- Check if streams need to be reconnected to other blocks\n"
                result_text += "- Use remove_stream separately to delete any unneeded streams"

            elif status == 'NOT_FOUND':
                result_text = f"Block not found: {block_name}\n"
                result_text += f"Message: {message}\n"
                result_text += "\nSuggestions:\n"
                result_text += "- Use get_blocks_list to view available blocks\n"
                result_text += "- Double-check the block name spelling"

            elif status == 'CONNECTED':
                result_text = f"Cannot remove block: {block_name}\n"
                result_text += f"Message: {message}\n"

                if 'connected_streams' in result:
                    result_text += f"Connected streams: {', '.join(result['connected_streams'])}\n"

                result_text += "\nSolutions:\n"
                result_text += "1. Use force=True to remove the block while keeping the streams\n"
                result_text += "2. Manually disconnect the streams first\n"
                result_text += "3. Use get_block_connections to check detailed connections"

            elif status == 'ERROR':
                result_text = f"Failed to remove block: {block_name}\n"
                result_text += f"Error message: {message}\n"
                result_text += "\nTroubleshooting:\n"
                result_text += "- Verify Aspen Plus connection status\n"
                result_text += "- Ensure the block name is correct\n"
                result_text += "- Check if the file is read-only\n"
                result_text += "- Ensure the block is not locked by other operations"

            else:
                result_text = f"Unknown status: {status}\nMessage: {message}"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Exception occurred while removing block: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Aspen Plus connection issue\n"
                     f"2. File permission issue\n"
                     f"3. Block is currently in use by another operation\n"
                     f"4. Block has unresolved dependencies\n\n"
                     f"Please verify Aspen Plus status and try again."
            )]

    async def _get_block_output_specifications(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve output specifications of a block - supports quick view (paginated) and detailed query"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        block_name = args["block_name"]
        specification_names = args.get("specification_names", None)
        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        # Constants
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            # Retrieve all output specifications
            all_output_specs = self.aspen_instance.Get_BlockOutputSpecificationsList(block_name, table=True)

            if not all_output_specs:
                return [TextContent(
                    type="text",
                    text=f"Block '{block_name}' has no available output data.\n\n"
                         f"Possible causes:\n"
                         f"1. Simulation has not been executed - use run_simulation to execute\n"
                         f"2. Simulation failed - use check_model_completion_status to diagnose\n"
                         f"3. Invalid block name - use get_blocks_list to confirm\n"
                         f"4. Incomplete block connections - use get_block_connections to verify\n\n"
                         f"Output specifications are only available after a successful simulation run."
                )]

            block_type = self.aspen_instance.BlockType(block_name)

            if specification_names is None:
                # Quick view mode with pagination
                import math
                
                spec_items = list(all_output_specs.items())
                total_specs = len(spec_items)
                total_pages = math.ceil(total_specs / page_size) if total_specs > 0 else 1
                
                # Validate page number
                page = max(1, min(page, total_pages))
                
                # Calculate pagination range
                start_idx = (page - 1) * page_size
                end_idx = min(start_idx + page_size, total_specs)
                
                # Get current page specs
                current_page_specs = spec_items[start_idx:end_idx]
                
                # Build output
                result = f"Block '{block_name}' ({block_type}) Output Specifications\n"
                result += "=" * 60 + "\n"
                
                if total_pages == 1:
                    result += f"📄 Showing all {total_specs} specs\n\n"
                else:
                    result += f"📄 Page {page} of {total_pages} | Showing specs {start_idx+1}-{end_idx} of {total_specs}\n\n"
                
                result += "─" * 60 + "\n"
                
                # Format each spec
                for idx, (spec_path, spec_info) in enumerate(current_page_specs, start=start_idx+1):
                    description = spec_info.get('description', 'No description')
                    value = spec_info.get('value', 'N/A')
                    unit = spec_info.get('unit', '')
                    
                    if value != 'N/A' and value is not None:
                        if isinstance(value, (int, float)):
                            value_display = f"{value:.4g} {unit}" if unit else f"{value:.4g}"
                        else:
                            value_display = str(value)
                    else:
                        value_display = "N/A"
                    
                    result += f"{idx}. {spec_path}\n"
                    result += f"   Value: {value_display}\n"
                    result += f"   Description: {description}\n\n"
                
                result += "─" * 60 + "\n"
                
                # Check output size and add warning if needed
                if len(result) > OUTPUT_SIZE_WARNING_THRESHOLD:
                    suggested_size = max(10, page_size // 2)
                    result += f"\n⚠️ WARNING: Output size is large ({len(result)} chars).\n"
                    result += f"   If errors occur, try: page_size={suggested_size}\n"
                
                # Pagination info
                result += "\n📊 Pagination Info:\n"
                if total_pages == 1:
                    result += f"   • Total: {total_specs} specs (all displayed)\n"
                else:
                    result += f"   • Page {page} of {total_pages}"
                    if page == total_pages:
                        result += " (LAST PAGE)\n"
                    else:
                        result += "\n"
                    result += f"   • Showing: {end_idx - start_idx} specs\n"
                    result += f"   • Total: {total_specs} specs\n"
                
                # Navigation
                if page < total_pages:
                    result += f"\n⏭️ MORE SPECS AVAILABLE!\n"
                    result += f"   Call: get_block_output_specifications(block_name='{block_name}', page={page+1})\n"
                elif total_pages > 1:
                    result += f"\n✅ All specs have been displayed across {total_pages} pages.\n"
                
                # Detailed query tip
                result += f"\n💡 To query specific specs in detail:\n"
                result += f"   get_block_output_specifications(block_name='{block_name}', specification_names=['SPEC_NAME'])\n"

                return [TextContent(type="text", text=result)]

            else:
                # Detailed query mode
                filtered_specs = {}
                not_found = []

                for spec_name in specification_names:
                    spec_name_upper = spec_name.upper()
                    if spec_name_upper in all_output_specs:
                        filtered_specs[spec_name_upper] = all_output_specs[spec_name_upper]
                    else:
                        not_found.append(spec_name)

                response_data = {
                    "block_name": block_name.upper(),
                    "block_type": block_type,
                    "query_mode": "detailed_output",
                    "simulation_status": "completed_with_results",
                    "requested_specifications": specification_names,
                    "found_count": len(filtered_specs),
                    "not_found_count": len(not_found),
                    "output_specifications": filtered_specs,
                    "not_found": not_found
                }

                import json
                json_result = json.dumps(response_data, indent=2, ensure_ascii=False)

                result = f"Detailed Output Specification Query for Block '{block_name}' ({block_type}):\n"
                result += "=" * 80 + "\n"
                result += f"Specifications requested: {len(specification_names)}\n"
                result += f"Specifications found: {len(filtered_specs)}\n"
                result += f"Not found: {len(not_found)}\n"
                result += f"Simulation status: Completed with results\n\n"

                if not_found:
                    result += f"Not found: {', '.join(not_found)}\n\n"

                if filtered_specs:
                    result += "Details of found specifications:\n"
                    for spec_path, spec_info in filtered_specs.items():
                        value = spec_info.get('value', 'N/A')
                        unit = spec_info.get('unit', '')
                        description = spec_info.get('description', 'No description')

                        result += f"  {spec_path}:\n"
                        result += f"    Value: {value} {unit}\n"
                        result += f"    Description: {description}\n\n"

                result += "JSON Output:\n"
                result += "-" * 40 + "\n"
                result += json_result

                return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve output specifications for block '{block_name}': {str(e)}\n\n"
                     f"Troubleshooting:\n"
                     f"1. Confirm block name using get_blocks_list\n"
                     f"2. Ensure simulation is executed via run_simulation\n"
                     f"3. Check simulation status with check_model_completion_status\n"
                     f"4. Validate block connections using get_block_connections\n"
                     f"5. Confirm Aspen Plus connection is active"
            )]
