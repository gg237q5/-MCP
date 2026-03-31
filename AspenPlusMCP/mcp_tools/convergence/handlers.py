import math
from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler


class ConvergenceHandlers(BaseHandler):
    """Handler class for convergence-related MCP tools."""

    async def _get_input_convergence(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve input specifications for convergence - supports quick view (paginated) and detailed query"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        specification_names = args.get("specification_names", None)
        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        # Constants
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            # Retrieve all specs
            all_specs = self.aspen_instance.Get_InputConvergence(table=True)

            if not all_specs:
                return [TextContent(
                    type="text",
                    text="No configurable input specifications found for convergence settings.\n"
                         "Please verify the model has convergence options configured."
                )]
            
            if specification_names is None:
                # Quick view mode with pagination
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
                result = "Convergence Input Specifications\n"
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
                    if spec_info.get('unit'):
                        result += f"   Unit: {spec_info.get('unit')} (category: {spec_info.get('unit_category')})\n"
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
                    result += f"   Call: get_input_convergence(page={page+1})\n"
                elif total_pages > 1:
                    result += f"\n✅ All specs have been displayed across {total_pages} pages.\n"
                
                # Detailed query tip
                result += f"\nTo set convergence parameters:\n"
                result += f"   set_input_convergence(tol=0.001, weg_maxit=100)\n"
                result += f"\nNEXT STEP: Call skills(category='convergence') for troubleshooting guide.\n"

                return [TextContent(type="text", text=result)]
            else:
                # Detailed query mode
                filtered_specs = {}
                not_found = []

                for name in specification_names:
                    name_upper = name.upper()
                    found = False
                    for spec_path, spec_info in all_specs.items():
                        if name_upper in spec_path.upper():
                            filtered_specs[spec_path] = spec_info
                            found = True
                    if not found:
                        not_found.append(name)

                result = "Convergence Input Specifications (Detailed Query)\n"
                result += "=" * 60 + "\n\n"

                if filtered_specs:
                    for spec_path, spec_info in filtered_specs.items():
                        result += f"📌 {spec_path}\n"
                        result += f"   Description: {spec_info.get('description', 'N/A')}\n"
                        result += f"   Value: {spec_info.get('value')}\n"
                        if spec_info.get('unit'):
                            result += f"   Unit: {spec_info.get('unit')}\n"
                            result += f"   Unit Category: {spec_info.get('unit_category')}\n"
                        if spec_info.get('basis'):
                            result += f"   Basis: {spec_info.get('basis')}\n"
                        if spec_info.get('options'):
                            result += f"   Options: {spec_info.get('options')}\n"
                        result += "\n"

                if not_found:
                    result += f"⚠️ Not found: {', '.join(not_found)}\n"
                    result += "   Use get_input_convergence() to see all available specs.\n"

                return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error retrieving convergence specifications: {str(e)}"
            )]

    async def _set_input_convergence(self, args: Dict[str, Any]) -> List[TextContent]:
        """Set input specifications for convergence"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file first."
            )]

        tol = args.get("tol")
        weg_maxit = args.get("weg_maxit")
        specifications_dict = args.get("specifications_dict", {})

        # Build specifications from quick parameters
        all_specs = {}
        
        if tol is not None:
            all_specs['TOL'] = tol
        
        if weg_maxit is not None:
            all_specs['WEG_MAXIT'] = weg_maxit
        
        # Add advanced specifications
        if specifications_dict:
            all_specs.update(specifications_dict)

        if not all_specs:
            return [TextContent(
                type="text",
                text="No specifications provided.\n"
                     "Usage:\n"
                     "  - set_input_convergence(tol=0.001)\n"
                     "  - set_input_convergence(weg_maxit=100)\n"
                     "  - set_input_convergence(specifications_dict={'TOL': 0.001})\n"
                     "\n💡 Use get_input_convergence() to see available specs."
            )]

        try:
            # Capture output
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            with contextlib.redirect_stdout(output_buffer):
                self.aspen_instance.Set_InputConvergence(specifications_dict=all_specs)
            
            captured_output = output_buffer.getvalue()
            
            result = "Convergence Settings Update\n"
            result += "=" * 60 + "\n\n"
            result += captured_output
            result += "\nUse get_input_convergence() to verify the settings.\n"
            result += "\nNEXT STEP: Call skills(category='convergence') for troubleshooting guide."

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error setting convergence specifications: {str(e)}\n"
                     f"\n💡 Use get_input_convergence() to see available specs and correct paths."
            )]
