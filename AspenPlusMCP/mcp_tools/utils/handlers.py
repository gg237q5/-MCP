from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class UtilsHandlers(BaseHandler):
    async def _timer(self, args: Dict[str, Any]) -> List[TextContent]:
        """Simple timer tool"""
        from datetime import datetime

        start_time_input = args.get("start_time", None)

        # Get the current time
        current_time = datetime.now()
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')

        # If no start_time is provided, return current time only
        if start_time_input is None:
            return [TextContent(type="text", text=current_time_str)]

        try:
            # Parse the input start time
            start_datetime = datetime.strptime(start_time_input, '%Y-%m-%d %H:%M:%S')

            # Calculate elapsed time in seconds
            time_diff = (current_time - start_datetime).total_seconds()

            result = f"{current_time_str}, {time_diff:.0f}s"
            return [TextContent(type="text", text=result)]

        except ValueError:
            return [TextContent(
                type="text",
                text="Invalid time format. Please use: YYYY-MM-DD HH:MM:SS"
            )]

    async def _unit_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Retrieve Aspen Plus unit list"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use 'open_aspen_plus' to open a file first."
            )]

        item = args.get("item", None)

        try:
            # Call the UnitList method from the Aspen interface
            unit_data = self.aspen_instance.UnitList(item=item, table=True)

            # Construct JSON response
            response_data = {
                "query_type": "all_categories" if item is None else
                "units in category" if len(item) == 1 else "specific_unit",
                "query_parameters": item,
                "unit_data": unit_data
            }

            import json
            json_result = json.dumps(response_data, indent=2, ensure_ascii=False)

            # Construct readable output
            # result = "Aspen Plus Unit List Query Result:\n"
            # result += "=" * 50 + "\n"

            result = ""  # 初始化 result，避免 UnboundLocalError

            if item is None:
                result += f"Showing all unit categories (total: {len(unit_data)}):\n"
                result += "Index  Category Name\n"
                result += "-" * 30 + "\n"
                for index, category_name in unit_data.items():
                    result += f"{index:3d}   {category_name}\n"

            elif len(item) == 1:
                result += f"Units in Category {item[0]} (total: {len(unit_data)}):\n"
                result += "Index  Unit Name\n"
                result += "-" * 30 + "\n"
                for index, unit_name in unit_data.items():
                    result += f"{index:3d}   {unit_name}\n"

            elif len(item) == 2:
                result += f"Unit in Category {item[0]}, Index {item[1]}:\n"
                result += f"Unit Name: {unit_data}\n"

            result += f"\nUsage Instructions:\n"
            result += "- Use the index when specifying units in stream or block specifications.\n"
            result += "- For example: {{'Category': 25, 'unit': 22}} means Category index 25 with unit index 22.\n"
            result += "- Unit indices start from 1.\n\n"

            result += "JSON Result:\n"
            result += "-" * 40 + "\n"
            result += json_result

            return [TextContent(
                type="text",
                text=result
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve unit list: {str(e)}\n\n"
                     f"Possible Causes:\n"
                     f"1. Invalid input format\n"
                     f"2. Index out of range\n"
                     f"3. Aspen Plus connection issue\n\n"
                     f"Usage Examples:\n"
                     f"- unit_list() - List all categories\n"
                     f"- unit_list(item=[1]) - List units in category 1\n"
                     f"- unit_list(item=[1,2]) - Get unit at index 2 in category 1"
            )]

    async def _get_version(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get MCP server version information from version.json"""
        import json
        import os
        
        # Get the path to version.json (relative to project root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        version_file = os.path.join(project_root, "version.json")
        
        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version_info = json.load(f)
        except FileNotFoundError:
            return [TextContent(
                type="text",
                text="Error: version.json not found. Please ensure the file exists in the project root."
            )]
        except json.JSONDecodeError as e:
            return [TextContent(
                type="text",
                text=f"Error: Invalid JSON in version.json: {str(e)}"
            )]
        
        result = "=== Aspen Plus MCP Server Version ===\n"
        result += f"Name: {version_info.get('name', 'Unknown')}\n"
        result += f"Version: {version_info.get('version', 'Unknown')}\n"
        result += f"Build Type: {version_info.get('build_type', 'Unknown').upper()}\n"
        result += f"Build Date: {version_info.get('build_date', 'Unknown')}\n"
        if version_info.get('description'):
            result += f"Description: {version_info.get('description')}\n"
        result += "\n"
        result += f"JSON: {json.dumps(version_info, indent=2)}"
        
        return [TextContent(type="text", text=result)]

    async def _skills(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get setup guides for Aspen Plus configuration"""
        import os
        
        # Get skills directory path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        skills_path = os.path.join(project_root, "skills")
        
        category = args.get("category")
        name = args.get("name")
        
        try:
            if not category:
                # Level 1: List all categories
                if not os.path.exists(skills_path):
                    return [TextContent(type="text", text="Skills directory not found.")]
                
                categories = [d for d in os.listdir(skills_path) 
                             if os.path.isdir(os.path.join(skills_path, d))]
                
                result = "Available Skills Categories:\n"
                result += "=" * 40 + "\n\n"
                
                for cat in sorted(categories):
                    cat_path = os.path.join(skills_path, cat)
                    resources_path = os.path.join(cat_path, 'resources')
                    if os.path.exists(resources_path):
                        files = [f for f in os.listdir(resources_path) if f.endswith('.md')]
                    else:
                        files = []
                    result += f"  - {cat:15} ({len(files)} guides)\n"
                
                result += f"\nUsage:\n"
                result += f"  skills(category='blocks')              -> show SKILL.md\n"
                result += f"  skills(category='blocks', name='RADFRAC') -> show resource\n"
                
                return [TextContent(type="text", text=result)]
            
            elif not name:
                # Level 2: Show SKILL.md content
                category_path = os.path.join(skills_path, category)
                skill_file = os.path.join(category_path, 'SKILL.md')
                
                if not os.path.exists(category_path):
                    categories = [d for d in os.listdir(skills_path) 
                                 if os.path.isdir(os.path.join(skills_path, d))]
                    return [TextContent(
                        type="text",
                        text=f"Category '{category}' not found.\n\n"
                             f"Available categories: {', '.join(sorted(categories))}"
                    )]
                
                if os.path.exists(skill_file):
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return [TextContent(type="text", text=content)]
                else:
                    # Fallback: list resources
                    resources_path = os.path.join(category_path, 'resources')
                    if os.path.exists(resources_path):
                        files = [f[:-3] for f in os.listdir(resources_path) if f.endswith('.md')]
                    else:
                        files = []
                    
                    result = f"Skills in '{category}':\n"
                    result += "=" * 40 + "\n\n"
                    for f in sorted(files):
                        result += f"  - {f}\n"
                    result += f"\nUsage: skills(category='{category}', name='<NAME>')\n"
                    return [TextContent(type="text", text=result)]
            
            else:
                # Level 3: Show resource content from resources/
                resources_path = os.path.join(skills_path, category, 'resources')
                file_path = os.path.join(resources_path, f'{name}.md')
                
                if not os.path.exists(file_path):
                    file_path = os.path.join(resources_path, f'{name.upper()}.md')
                
                if not os.path.exists(file_path):
                    if os.path.exists(resources_path):
                        files = [f[:-3] for f in os.listdir(resources_path) if f.endswith('.md')]
                        return [TextContent(
                            type="text",
                            text=f"Resource '{name}' not found in '{category}'.\n\n"
                                 f"Available: {', '.join(sorted(files))}"
                        )]
                    return [TextContent(type="text", text=f"Category '{category}' not found.")]
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return [TextContent(type="text", text=content)]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


