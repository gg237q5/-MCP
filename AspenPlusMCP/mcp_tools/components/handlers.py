from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class ComponentHandlers(BaseHandler):
    async def _get_components_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """List all components in the simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open a file first."
            )]

        try:
            components = self.aspen_instance.ComponentsList()
            result = f"Components list ({len(components)} components):\n"
            for comp in components:
                result += f"- {comp}\n"

            return [TextContent(
                type="text",
                text=result
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve components list: {str(e)}"
            )]

    async def _get_henrycomps_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for get_henry_comps_list tool"""
        if not self.aspen_instance:
            return [TextContent(type="text", text="Aspen Plus is not connected.")]
        set_id = args["set_name"]
        try:
            result = self.aspen_instance.HenryCompsList(table=False, set_name=set_id)
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error accessing Henry Comps '{set_id}': {str(e)}")]

    async def _add_henrycomps_set(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for add_henry_comps_set tool"""
        if not self.aspen_instance:
            return [TextContent(type="text", text="Aspen Plus is not connected.")]
            
        set_name = args.get("set_name", "")
        try:
            self.aspen_instance.Add_HenryCompsSet(set_name=set_name)
            return [TextContent(type="text", text=f"Successfully added Henry Components Set: {set_name}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding Henry Components Set: {str(e)}")]

    async def _remove_henrycomps_set(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for remove_henrycomps_set tool"""
        if not self.aspen_instance:
            return [TextContent(type="text", text="Aspen Plus is not connected.")]
            
        set_name = args["set_name"]
        
        try:
            result = self.aspen_instance.Remove_HenryCompsSet(set_name=set_name)
            
            if result:
                return [TextContent(type="text", text=f"Successfully removed Henry Components Set: {set_name}")]
            else:
                return [TextContent(type="text", text=f"Failed to remove Henry Components Set: {set_name}. It may not exist.")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error removing Henry Components Set: {str(e)}")]

    async def _get_henrycomps_set_list(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for get_henrycomps_set_list tool"""
        if not self.aspen_instance:
            return [TextContent(type="text", text="Aspen Plus is not connected.")]
            
        try:
            result = self.aspen_instance.Get_HenryCompsSetList()
            
            if result:
                return [TextContent(type="text", text=f"Henry Components Set list: {', '.join(result)}")]
            else:
                return [TextContent(type="text", text="No Henry Components Sets found.")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting Henry Components Set list: {str(e)}")]

    async def _add_henrycomps(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for add_henrycomps tool"""
        inp_path = args["inp_path"]
        comps = args["comps"]
        set_name = args["set_name"]
        
        try:
            from aspen_core.components import ComponentsMixin
            ComponentsMixin.Set_HenryComps(None, inp_path=inp_path, comps=comps, set_name=set_name)
            
            return [TextContent(type="text", text=f"Successfully updated Henry Components Set '{set_name}' in {inp_path}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error setting Henry Components: {str(e)}")]

    async def _remove_henrycomps(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for remove_henrycomps tool"""
        inp_path = args["inp_path"]
        comps = args["comps"]
        set_name = args["set_name"]
        
        try:
            from aspen_core.components import ComponentsMixin
            ComponentsMixin.Set_HenryComps(None, inp_path=inp_path, comps=comps, set_name=set_name)
            
            return [TextContent(type="text", text=f"Successfully updated Henry Components Set '{set_name}' in {inp_path}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error setting Henry Components: {str(e)}")]

    async def _elec_wizard(self, args: Dict[str, Any]) -> List[TextContent]:
        """Handler for elec_wizard tool"""
        if not self.aspen_instance:
            return [TextContent(type="text", text="Aspen Plus is not connected.")]
            
        try:
            filename = args["filename"]
            chem_source = args["chem_source"]
            ref_state = args["ref_state"]
            h_ion = args["h_ion"]
            reaction_opts = args["reaction_opts"]
            prop_method = args["prop_method"]
            sim_approach = args["sim_approach"]

            # Call the synchronous method in AP.py
            # Since Elec_Wizard involves GUI automation, it might block, but we are running it directly.
            result = self.aspen_instance.Elec_Wizard(
                filename=filename,
                chem_source=chem_source,
                ref_state=ref_state,
                h_ion=h_ion,
                reaction_opts=reaction_opts,
                prop_method=prop_method,
                sim_approach=sim_approach
            )
            
            return [TextContent(type="text", text=str(result))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error executing Elec Wizard: {str(e)}")]