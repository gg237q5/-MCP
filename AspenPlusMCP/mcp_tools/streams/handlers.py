import io
import contextlib
from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class StreamHandlers(BaseHandler):
    async def _get_streams_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all streams in the simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        streams = self.aspen_instance.StreamsList()
        result = f"Streams list ({len(streams)} streams):\n"
        for stream_name, stream_type in streams:
            result += f"- {stream_name} (Type: {stream_type})\n"

        return [TextContent(
            type="text",
            text=result
        )]

    async def _add_stream(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add a new stream to the simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        stream_name = args["stream_name"]
        stream_type = args.get("stream_type", "MATERIAL")

        try:
            self.aspen_instance.Add_Stream(stream_name, stream_type)
            return [TextContent(
                type="text",
                text=f"Successfully added stream '{stream_name}' of type '{stream_type}'.\n\n"
                     f"NEXT STEP: Call skills(category='streams') then skills(category='streams', name='MATERIAL') for configuration guide."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to add stream: {str(e)}"
            )]

    async def _remove_stream(self, args: Dict[str, Any]) -> List[TextContent]:
        """Remove a stream from the Aspen Plus model"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to launch the file."
            )]

        stream_name = args["stream_name"]
        force = args.get("force", False)

        try:
            # Use the Aspen instance to remove the stream
            result = self.aspen_instance.Remove_Stream(stream_name, force=force)

            # Extract status and message
            status = result['status']
            message = result['message']

            if status == 'SUCCESS':
                result_text = f"Successfully removed stream: {stream_name}\n"
                result_text += f"Message: {message}\n"

                if 'was_connected_to' in result and result['was_connected_to']:
                    result_text += f"Originally connected to units: {', '.join(result['was_connected_to'])}\n"

                result_text += "\nTips:\n"
                result_text += "- Use get_streams_list to confirm the stream has been removed\n"
                result_text += "- Check if related blocks need to reconnect to new streams"

            elif status == 'NOT_FOUND':
                result_text = f"Stream not found: {stream_name}\n"
                result_text += f"Message: {message}\n"
                result_text += "\nSuggestions:\n"
                result_text += "- Use get_streams_list to view available streams\n"
                result_text += "- Check for typos in the stream name"

            elif status == 'CONNECTED':
                result_text = f"Cannot remove stream: {stream_name}\n"
                result_text += f"Message: {message}\n"

                if 'connected_blocks' in result:
                    result_text += f"Connected blocks: {', '.join(result['connected_blocks'])}\n"

                result_text += "\nSolutions:\n"
                result_text += "1. Set force=True to force removal\n"
                result_text += "2. Manually disconnect the stream from blocks first\n"
                result_text += "3. Use get_block_connections to check current stream-block connections"

            elif status == 'ERROR':
                result_text = f"Failed to remove stream: {stream_name}\n"
                result_text += f"Error Message: {message}\n"
                result_text += "\nTroubleshooting:\n"
                result_text += "- Check Aspen Plus connection status\n"
                result_text += "- Confirm the stream name is correct\n"
                result_text += "- Ensure the file is not read-only"

            else:
                result_text = f"Unknown status: {status}\nMessage: {message}"

            return [TextContent(
                type="text",
                text=result_text
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Exception occurred while removing stream: {str(e)}\n\n"
                     f"Possible causes:\n"
                     f"1. Aspen Plus connection issue\n"
                     f"2. File permission issue\n"
                     f"3. The stream is in use by another operation\n\n"
                     f"Please verify Aspen Plus status and try again."
            )]

    async def _get_stream_input_conditions_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve input specifications for a stream - supports quick view (paginated) and detailed query"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        stream_name = args["stream_name"]
        specification_names = args.get("specification_names", None)
        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        # Constants
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            # Retrieve all specs
            all_specs = self.aspen_instance.Get_StreamInputConditionsList(stream_name, table=True)

            if not all_specs:
                return [TextContent(
                    type="text",
                    text=f"No configurable input specifications found for stream '{stream_name}'.\n"
                         f"Please verify the stream name."
                )]
            
            # Get stream type
            stream_type = None
            for s in self.aspen_instance.StreamsList():
                if s[0] == stream_name.upper():
                    stream_type = s[1]
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
                result = f"Stream '{stream_name}' ({stream_type}) Input Specifications\n"
                result += "=" * 60 + "\n"
                
                if total_pages == 1:
                    result += f"Showing all {total_specs} specs\n\n"
                else:
                    result += f"Page {page} of {total_pages} | Showing specs {start_idx+1}-{end_idx} of {total_specs}\n\n"
                
                result += "-" * 60 + "\n"
                
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
                
                result += "-" * 60 + "\n"
                
                # Check output size and add warning if needed
                if len(result) > OUTPUT_SIZE_WARNING_THRESHOLD:
                    suggested_size = max(10, page_size // 2)
                    result += f"\n[WARNING] Output size is large ({len(result)} chars).\n"
                    result += f"   If errors occur, try: page_size={suggested_size}\n"
                
                # Pagination info
                result += "\nPagination Info:\n"
                if total_pages == 1:
                    result += f"   - Total: {total_specs} specs (all displayed)\n"
                else:
                    result += f"   - Page {page} of {total_pages}"
                    if page == total_pages:
                        result += " (LAST PAGE)\n"
                    else:
                        result += "\n"
                    result += f"   - Showing: {end_idx - start_idx} specs\n"
                    result += f"   - Total: {total_specs} specs\n"
                
                # Navigation
                if page < total_pages:
                    result += f"\n>>> MORE SPECS AVAILABLE!\n"
                    result += f"   Call: get_stream_input_conditions_list(stream_name='{stream_name}', page={page+1})\n"
                elif total_pages > 1:
                    result += f"\n[OK] All specs have been displayed across {total_pages} pages.\n"
                
                # Detailed query tip
                result += f"\nTo set specifications:\n"
                result += f"   set_stream_input_conditions(stream_name='{stream_name}', specifications_dict={{'SPEC': {{'value': v, 'unit': u}}}})\n"
                result += f"\nNEXT STEP: Call skills(category='streams') then skills(category='streams', name='MATERIAL') for configuration guide.\n"

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
                    result += f"Detailed Input Specifications for Stream '{stream_name}':\n"
                    result += "=" * 50 + "\n"
                    
                    import json
                    result += json.dumps(filtered_specs, indent=2, ensure_ascii=False)
                    result += "\n\n"
                    
                    # Add dynamic unit_category guidance for LLM
                    # Collect unique unit categories from filtered specs
                    unit_categories = set()
                    for spec_info in filtered_specs.values():
                        if spec_info.get('unit_category'):
                            unit_categories.add(spec_info['unit_category'])
                    
                    if unit_categories:
                        result += "Unit Category Reference (from returned specs):\n"
                        result += "-" * 50 + "\n"
                        result += "Each spec includes 'unit_category' field. To find available units, call:\n"
                        for cat in sorted(unit_categories):
                            result += f"  - unit_list(item=[{cat}])  # for unit_category={cat}\n"
                        result += "\nThe 'unit' field shows the current unit name.\n"
                        result += "Use `unit_list()` to see all available unit categories.\n\n"
                
                if not_found:
                    result += "[WARNING] The following specifications were not found:\n"
                    for name in not_found:
                        result += f"- {name}\n"
                    result += "\nTip: Use Quick View mode (no specification_names) to see all valid spec paths."

                return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve input specifications for stream '{stream_name}': {str(e)}"
            )]

    async def _set_stream_input_conditions(self, args: Dict[str, Any]) -> List[TextContent]:
        """Set input specifications for a stream"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        stream_name = args["stream_name"]
        
        # Combine direct parameters and dictionary
        specifications = args.get("specifications_dict", {})
        if not specifications:
            specifications = {}

        # Handle simplified parameters
        if "temp" in args and args["temp"] is not None:
             specifications["TEMP\\MIXED"] = {"value": args["temp"], "unit": 4} # Assuming 4 is C from docstring
        if "pres" in args and args["pres"] is not None:
             specifications["PRES\\MIXED"] = {"value": args["pres"], "unit": 5} # Assuming 5 is bar from docstring

        if not specifications:
            return [TextContent(
                type="text",
                text=f"No specifications were provided for stream '{stream_name}'."
            )]

        try:
            # Capture output
            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                self.aspen_instance.Set_StreamInputConditions(stream_name, specifications_dict=specifications)
            
            setting_output = f.getvalue()

            # Result message
            result = f"Specification setting result for stream '{stream_name}':\n"
            result += "=" * 50 + "\n"

            if setting_output.strip():
                result += "Detailed log:\n"
                result += "-" * 30 + "\n"
                result += setting_output
                result += "\n"

            result += "Summary of specifications set:\n"
            result += "-" * 30 + "\n"
            
            successful_specs = 0
            for spec_name, value in specifications.items():
                result += f"{spec_name}: {value}\n"
                successful_specs += 1
                
            result += f"\nTotal specifications applied: {successful_specs}\n"
            
            result += "\nRecommendations:\n"
            result += f"- Use get_stream_input_conditions_list('{stream_name}') to verify applied values\n"
            result += "- Use check_model_completion_status to check model readiness\n"
            result += "\nNEXT STEP: Call skills(category='streams') for stream configuration best practices.\n"

            return [TextContent(
                type="text",
                text=result
            )]

        except Exception as e:
            error_msg = f"Failed to set specifications for stream '{stream_name}':\n"
            error_msg += "=" * 50 + "\n"
            error_msg += f"Error: {str(e)}\n\n"
            
            error_msg += "Input parameters:\n"
            error_msg += f"   - Stream name: {repr(stream_name)}\n"
            
            error_msg += "\nSpecification details:\n"
            for spec_name, value in specifications.items():
                error_msg += f"   - Spec path: {repr(spec_name)}\n"
                error_msg += f"   - Value: {repr(value)}\n"
                
            error_msg += "\nTroubleshooting tips:\n"
            error_msg += "1. Use get_stream_input_conditions_list to retrieve valid spec names\n"
            error_msg += "2. Check that the specification paths are case-sensitive and match exactly\n"
            error_msg += "3. Ensure that values are of the correct data type\n"
            error_msg += "4. Confirm the stream exists in the model\n"
            error_msg += f"5. Use get_streams_list to verify that '{stream_name}' is present\n"

            return [TextContent(
                type="text",
                text=error_msg
            )]

    async def _get_stream_output_conditions(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve output conditions of a stream - supports quick view (paginated) and detailed query"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        stream_name = args["stream_name"]
        specification_names = args.get("specification_names", None)
        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        # Constants
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            # Retrieve all output conditions
            all_output_conditions = self.aspen_instance.Get_StreamOutputConditionsList(stream_name, table=True)

            if not all_output_conditions:
                 return [TextContent(
                    type="text",
                    text=f"Stream '{stream_name}' has no available output data.\n\n"
                         f"Possible causes:\n"
                         f"1. Simulation has not been executed - use run_simulation to run it\n"
                         f"2. Simulation failed - use check_model_completion_status to diagnose\n"
                         f"3. Invalid stream name - use get_streams_list to confirm\n\n"
                         f"Output conditions are only available after a successful simulation run."
                )]

            # Get stream type
            stream_type = None
            for s in self.aspen_instance.StreamsList():
                if s[0] == stream_name.upper():
                    stream_type = s[1]
                    break

            if specification_names is None:
                # Quick view mode with pagination
                import math
                
                spec_items = list(all_output_conditions.items())
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
                result = f"Stream '{stream_name}' ({stream_type}) Output Conditions\n"
                result += "=" * 60 + "\n"
                
                if total_pages == 1:
                    result += f"Showing all {total_specs} conditions\n\n"
                else:
                    result += f"Page {page} of {total_pages} | Showing conditions {start_idx+1}-{end_idx} of {total_specs}\n\n"
                
                result += "-" * 60 + "\n"
                
                # Format each condition
                for idx, (condition_path, condition_info) in enumerate(current_page_specs, start=start_idx+1):
                    description = condition_info.get('description', 'No description')
                    value = condition_info.get('value', 'N/A')
                    unit = condition_info.get('unit', '')
                    
                    if value != 'N/A' and value is not None:
                        if isinstance(value, (int, float)):
                            value_display = f"{value:.4g} {unit}" if unit else f"{value:.4g}"
                        else:
                            value_display = str(value)
                    else:
                        value_display = "N/A"
                    
                    result += f"{idx}. {condition_path}\n"
                    result += f"   Value: {value_display}\n"
                    result += f"   Description: {description}\n\n"
                
                result += "-" * 60 + "\n"
                
                # Check output size and add warning if needed
                if len(result) > OUTPUT_SIZE_WARNING_THRESHOLD:
                    suggested_size = max(10, page_size // 2)
                    result += f"\n[WARNING] Output size is large ({len(result)} chars).\n"
                    result += f"   If errors occur, try: page_size={suggested_size}\n"
                
                # Pagination info
                result += "\nPagination Info:\n"
                if total_pages == 1:
                    result += f"   - Total: {total_specs} conditions (all displayed)\n"
                else:
                    result += f"   - Page {page} of {total_pages}"
                    if page == total_pages:
                        result += " (LAST PAGE)\n"
                    else:
                        result += "\n"
                    result += f"   - Showing: {end_idx - start_idx} conditions\n"
                    result += f"   - Total: {total_specs} conditions\n"
                
                # Navigation
                if page < total_pages:
                    result += f"\n>>> MORE CONDITIONS AVAILABLE!\n"
                    result += f"   Call: get_stream_output_conditions(stream_name='{stream_name}', page={page+1})\n"
                elif total_pages > 1:
                    result += f"\n[OK] All conditions have been displayed across {total_pages} pages.\n"
                
                # Detailed query tip
                result += f"\nTo query specific conditions in detail:\n"
                result += f"   get_stream_output_conditions(stream_name='{stream_name}', specification_names=['CONDITION_NAME'])\n"

                return [TextContent(type="text", text=result)]

            else:
                # Detailed query mode
                filtered_conditions = {}
                not_found = []

                for spec_name in specification_names:
                    spec_name_upper = spec_name.upper()
                    if spec_name_upper in all_output_conditions:
                        filtered_conditions[spec_name_upper] = all_output_conditions[spec_name_upper]
                    else:
                        not_found.append(spec_name)
                
                response_data = {
                    "stream_name": stream_name.upper(),
                    "stream_type": stream_type,
                    "query_mode": "detailed_output",
                    "simulation_status": "completed_with_results",
                    "requested_conditions": specification_names,
                    "found_count": len(filtered_conditions),
                    "not_found_count": len(not_found),
                    "output_conditions": filtered_conditions,
                    "not_found": not_found
                }

                import json
                json_result = json.dumps(response_data, indent=2, ensure_ascii=False)

                result = f"Detailed Output Condition Query for Stream '{stream_name}' ({stream_type}):\n"
                result += "=" * 80 + "\n"
                result += f"Conditions requested: {len(specification_names)}\n"
                result += f"Conditions found: {len(filtered_conditions)}\n"
                result += f"Conditions not found: {len(not_found)}\n"
                result += f"Simulation status: Completed with results\n\n"

                if not_found:
                    result += f"Not found: {', '.join(not_found)}\n\n"

                if filtered_conditions:
                    result += "Details of found conditions:\n"
                    for condition_path, condition_info in filtered_conditions.items():
                        value = condition_info.get('value', 'N/A')
                        unit = condition_info.get('unit', '')
                        description = condition_info.get('description', 'No description')

                        result += f"  {condition_path}:\n"
                        result += f"    Value: {value} {unit}\n"
                        result += f"    Description: {description}\n\n"

                result += "JSON Output:\n"
                result += "-" * 40 + "\n"
                result += json_result

                return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve output conditions for stream '{stream_name}': {str(e)}\n\n"
                     f"Troubleshooting:\n"
                     f"1. Verify stream name using get_streams_list\n"
                     f"2. Ensure simulation has been executed via run_simulation\n"
                     f"3. Check model status with check_model_completion_status\n"
                     f"4. Confirm Aspen Plus connection status"
            )]
