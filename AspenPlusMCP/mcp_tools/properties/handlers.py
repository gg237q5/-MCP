from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class PropertyHandlers(BaseHandler):
    async def _add_thermo_method(self, args: Dict[str, Any]) -> List[TextContent]:
        """Set thermodynamic method"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please open a file using open_aspen_plus first."
            )]

        method_name = args["method_name"]

        try:
            self.aspen_instance.Add_ThermoMethod(method_name)

            result = f"Successfully set thermodynamic method: {method_name.upper()}\n\n"
            result += "Important Reminder:\n"
            result += "1. save_aspen_file_as → save as .bkp\n"
            result += "2. close_aspen\n"
            result += "3. open_aspen_plus → reopen .bkp\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to set thermodynamic method: {str(e)}"
            )]

    async def _get_properties_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get property specifications with pagination"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please open a file using open_aspen_plus first."
            )]

        page = args.get("page", 1)
        page_size = args.get("page_size", 25)
        
        OUTPUT_SIZE_WARNING_THRESHOLD = 10000

        try:
            all_specs = self.aspen_instance.Get_PropertiesList(table=True)

            if not all_specs:
                return [TextContent(
                    type="text",
                    text="No property specifications found."
                )]
            
            import math
            spec_items = list(all_specs.items())
            total_specs = len(spec_items)
            total_pages = math.ceil(total_specs / page_size) if total_specs > 0 else 1
            
            # Validate page
            page = max(1, min(page, total_pages))
            
            # Pagination range
            start_idx = (page - 1) * page_size
            end_idx = min(start_idx + page_size, total_specs)
            
            current_page_specs = spec_items[start_idx:end_idx]
            
            # Build output
            result = "Property Specifications\n"
            result += "=" * 50 + "\n"
            
            if total_pages == 1:
                result += f"📄 Showing all {total_specs} specs\n\n"
            else:
                result += f"📄 Page {page} of {total_pages} | Specs {start_idx+1}-{end_idx} of {total_specs}\n\n"
            
            result += "─" * 50 + "\n"
            
            for idx, (name, info) in enumerate(current_page_specs, start=start_idx+1):
                result += f"{idx}. {name}\n"
                result += f"   Description: {info.get('description', 'N/A')}\n\n"
            
            result += "─" * 50 + "\n"
            
            # Size warning
            if len(result) > OUTPUT_SIZE_WARNING_THRESHOLD:
                suggested_size = max(10, page_size // 2)
                result += f"\n⚠️ Output large. Try page_size={suggested_size}\n"
            
            # Pagination info
            result += f"\n📊 Page {page}/{total_pages} | Total: {total_specs}\n"
            
            if page < total_pages:
                result += f"\n⏭️ More: get_properties_list(page={page+1})\n"

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to get property specifications: {str(e)}"
            )]

