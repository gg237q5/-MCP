from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class ReactionHandlers(BaseHandler):
    async def _add_reaction_set(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add a new reaction set"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        set_name = args["set_name"]
        reactions_type = args["reactions_type"]

        try:
            self.aspen_instance.Add_ReactionSet(set_name, reactions_type)
            return [TextContent(
                type="text",
                text=f"Successfully added Reaction Set '{set_name}' of type '{reactions_type}'."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to add reaction set: {str(e)}"
            )]

    async def _remove_reaction_set(self, args: Dict[str, Any]) -> List[TextContent]:
        """Remove a reaction set"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        set_name = args["set_name"]

        try:
            self.aspen_instance.Remove_ReactionSet(set_name)
            return [TextContent(
                type="text",
                text=f"Successfully removed Reaction Set '{set_name}'."
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to remove reaction set: {str(e)}"
            )]

    async def _get_reaction_set_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get list of reaction sets"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        try:
            sets = self.aspen_instance.Get_ReactionSet_List()
            result = f"Reaction Sets ({len(sets)} sets):\n"
            for s in sets:
                result += f"- {s}\n"

            return [TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to get reaction set list: {str(e)}"
            )]

    async def _get_reaction_set_type_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get list of reaction set types"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        try:
            types = self.aspen_instance.Get_ReactionSet_Type_List()
            result = f"Reaction Set Types ({len(types)} types):\n"
            for t in types:
                result += f"- {t}\n"

            return [TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to get reaction set type list: {str(e)}"
            )]

    async def _get_reaction_input_specifications(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get input specifications for a reaction set"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        reac_set = args["reac_set"]

        try:
            specs = self.aspen_instance.Get_ReactionInputSpecificationsList(reac_set, table=True)
            
            if not specs:
                 return [TextContent(
                    type="text",
                    text=f"No input specifications found for reaction set '{reac_set}'."
                )]

            result = f"Input Specifications for Reaction Set '{reac_set}':\n"
            result += "=" * 50 + "\n"
            
            for path, info in specs.items():
                result += f"Path: {path}\n"
                result += f"  Description: {info.get('description', 'N/A')}\n"
                result += f"  Value: {info.get('value', 'N/A')}\n"
                result += f"  Unit: {info.get('unit', 'None')} (category: {info.get('unit_category', 'None')})\n"
                result += f"  Basis: {info.get('basis', 'None')}\n"
                if info.get('options'):
                    result += f"  Options: {info.get('options')}\n"
                result += "-" * 30 + "\n"

            return [TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to get input specifications: {str(e)}"
            )]

    async def _set_reaction_input_specifications(self, args: Dict[str, Any]) -> List[TextContent]:
        """Set specifications for a reaction set"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        set_name = args["set_name"]
        specifications_dict = args["specifications_dict"]

        if not specifications_dict:
             return [TextContent(
                type="text",
                text="No specifications provided."
            )]

        try:
            status_report = self.aspen_instance.Set_ReactionInputSpecifications(set_name, **specifications_dict)
            
            result = ""
            if status_report:
                result += "--- Execution Report ---\n"
                result += "\n".join(status_report) + "\n"
                result += "------------------------\n\n"
                
            result += f"Successfully initiated specification changes for Reaction Set '{set_name}'.\n"
            result += "Applied configurations:\n"
            for k, v in specifications_dict.items():
                result += f"  {k}: {v}\n"

            return [TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to set reaction specifications: {str(e)}"
            )]

    async def _add_reaction(self, args: Dict[str, Any]) -> List[TextContent]:
        """Add reaction using INP file modification"""
        # Note: This tool modifies .inp files, it doesn't strictly need a running COM instance.
        # But we still pass it through the Aspen instance if the method is bound there. 
        inp_path = args["inp_path"]
        set_name = args["set_name"]
        reactions_data = args["reactions_data"]
        reaction_type = args.get("reaction_type", "REAC-DIST")

        try:
            from aspen_core.reactions import ReactionsMixin
            assigned_ids = ReactionsMixin.Add_Reaction(None, inp_path, set_name, reactions_data, reaction_type)
            if assigned_ids:
                return [TextContent(
                    type="text",
                    text=f"Successfully added {len(assigned_ids)} reactions to set '{set_name}' in file '{inp_path}'.\nAdded reaction IDs (STOIC numbers): {assigned_ids}"
                )]
            else:
                 return [TextContent(
                    type="text",
                    text="Failed to add reactions to the file. Please ensure 'id' and 'stoic' are properly provided."
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Exception while adding reaction to INP file: {str(e)}"
            )]

    async def _remove_reaction(self, args: Dict[str, Any]) -> List[TextContent]:
        """Remove reaction using INP file modification"""
        inp_path = args["inp_path"]
        set_name = args["set_name"]
        reactions_data = args["reactions_data"]
        reaction_type = args.get("reaction_type")

        try:
            from aspen_core.reactions import ReactionsMixin
            result = ReactionsMixin.Remove_Reaction(None, inp_path, set_name, reactions_data, reaction_type)
            if result:
                return [TextContent(
                    type="text",
                    text=f"Successfully reconstructed Reaction Set '{set_name}' in file '{inp_path}'."
                )]
            else:
                 return [TextContent(
                    type="text",
                    text="Failed to remove reactions from the file. Please check logs."
                )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Exception while removing reaction from INP file: {str(e)}"
            )]
