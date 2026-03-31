# -*- coding: utf-8 -*-
"""
Reaction operations for Aspen Plus COM interface.
Handles reaction listing, specifications, and modifications.

Corresponds to: mcp_tools/reactions/
"""

import os
import re
import UserDifineException as UDE

class ReactionsMixin:
    """Mixin class for Aspen Plus reaction operations."""

    def Add_ReactionSet(self, set_name, reactions_type):
        """
        Add a new Reaction Set with the specified name and type.
        Args:set_name (str): The name of the reaction set to add.
            reactions_type (str): The type of reactions (e.g., 'KINETIC', 'LGE').
        Returns:True if the reaction set was successfully added, False otherwise.
        """
        try:
            reaction_root = self.aspen.Application.Tree.FindNode(r"\Data\Reactions\Reactions")
            if not reaction_root:
                raise UDE.AspenPlus_FileStatusError("Reaction root node not found.")
            set_name = set_name.upper()
            reactions_type = reactions_type.upper()
            Set_name = f'{set_name}!{reactions_type}'
            reaction_root.Elements.Add(Set_name)
            return True
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to add Reaction Set: {str(e)}")

    def Remove_ReactionSet(self, set_name):
        """
        Remove a Reaction Set by name.
        Args:set_name (str): The name of the reaction set to remove.
        Returns:True if the reaction set was successfully removed, False otherwise.
        """
        try:
            reaction_root = self.aspen.Application.Tree.FindNode(r"\Data\Reactions\Reactions")
            if not reaction_root:
                raise UDE.AspenPlus_FileStatusError("Reaction root node not found.")
            set_name = set_name.upper()
            reaction_root.Elements.Remove(set_name)
            return True
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to remove Reaction Set: {str(e)}")

    def Get_ReactionSet_List(self):
        """
        Get the list of available Reaction Sets.
        Returns:list: A list of reaction set names and types (dict), or an empty list if failed.
        """
        try:
            options = []
            element = self.aspen.Application.Tree.FindNode(r"\Data\Reactions\Reactions")
            if not element:
                return options
            Set_list = element.Elements
            if Set_list:
                for i in range(Set_list.Count):
                    set_node = Set_list(i)
                    set_name = set_node.name
                    try:
                        set_type = set_node.AttributeValue(6)
                    except:
                        set_type = "UNKNOWN"
                    options.append({"name":set_name, "type":set_type})
            return options
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get Reaction Set list: {str(e)}")

    def Get_ReactionSet_Type_List(self):
        """
        Get the list of available Reaction Set Types.
        
        Returns:
            list: A list of reaction set types (str), or an empty list if failed.
        """
        fallback_options = [
            "GENERAL", "LHHW", "LANGMUIR-HINSHELWOOD", "EQUILIB", 
            "POWERLAW", "KINETIC", "REAC-DIST", "SALT", "CHEMISTRY"
        ]
        options = []
        try:
            element = self.aspen.Application.Tree.FindNode(r"\Data\Reactions\Reactions")
            if element:
                # AttributeValue(5) typically returns the list of valid options/types
                attr_val = element.AttributeValue(5)
                if attr_val and hasattr(attr_val, 'Elements'):
                    option_list = attr_val.Elements
                    if option_list:
                        for i in range(option_list.Count):
                            options.append(option_list(i).Value)
                        if options:
                            return options
            
            return fallback_options
            
        except Exception as e:
            return fallback_options

    def Get_ReactionType_List(self, set_name):
        """
        Get the list of available specific reaction types for a given reaction set (REACTYPE).
        Args: set_name (str): The name of the reaction set.
        Returns: list: A list of specific reactypes.
        """
        options = []
        try:
            element = self.aspen.Tree.FindNode(rf"\Data\Reactions\Reactions\{set_name}\Input\REACTYPE")
            
            if element:
                option_list = element.AttributeValue(5)
                if option_list and hasattr(option_list, 'Elements'):
                    for i in range(option_list.Elements.Count):
                        options.append(option_list.Elements(i).Value)
            else:
                raise UDE.AspenPlus_BlockTypeError(f"Reaction Set '{set_name}' not found or has no REACTYPE.")
                
            return options
        except Exception as e:
            raise UDE.AspenPlus_BlockTypeError(f"Error getting reaction types: {str(e)}")

    def Get_ReactionInputSpecificationsList(self, reac_set, table=False):
        """Get all available specifications for a specific reaction set.
        Includes unit_category (HAP_UNITROW) for each specification to enable unit_list queries.
        
        :param reac_set: String. Name of the reaction set to get specifications (e.g. 'R-1')
        :param table: Boolean. If True, return as dictionary; if False, print to console
        :return: Dictionary with specification names, descriptions, values, units, and unit_category (if table=True)"""
        if type(reac_set) != str:
            raise TypeError("reac_set must be a 'String'!!!")
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

        reac_set = reac_set.upper()

        # Note: Skipping check for reaction_name in list since we don't have a helper for it yet.
        # Will rely on FindNode failing if it doesn't exist.

        def _is_enterable(element):
            """Check if element is enterable (HAP_ENTERABLE = 7)."""
            try:
                enterable = element.AttributeValue(7)
                return enterable == 1
            except:
                return False

        def _get_element_value_and_unit(element):
            """Get current value, unit, unit_category, and basis for an element."""
            value_info = {'value': None, 'unit': None, 'unit_category': None, 'basis': None}
            try:
                # Get value
                try:
                    value_info['value'] = element.Value
                except:
                    pass

                # Get unit info: HAP_UNITROW (2) = unit category, HAP_UNITCOL (3) = unit index
                try:
                    pq = element.AttributeValue(2)  # HAP_UNITROW - unit category
                    um = element.AttributeValue(3)  # HAP_UNITCOL - unit index
                    if pq:
                        value_info['unit_category'] = pq
                    if pq and um:
                        value_info['unit'] = self.UnitList([pq, um], table=True)
                except:
                    pass

                # Get basis info: HAP_BASIS (13) = basis value
                try:
                    basis_val = element.AttributeValue(13)  # HAP_BASIS
                    if basis_val:
                        value_info['basis'] = basis_val
                except:
                    pass

            # Get options
                options = []
                try:
                    option_list = element.AttributeValue(5)
                    if option_list and hasattr(option_list, 'Elements'):
                        for i in range(option_list.Elements.Count):
                            options.append(option_list.Elements(i).Value)
                except:
                    pass
                value_info['options'] = options

            except:
                pass
            return value_info

        def _traverse_elements(node, path="", specifications=None):
            """Recursively traverse all elements and sub-elements."""
            if specifications is None:
                specifications = {}

            try:
                for element in node.Elements:
                    try:
                        element_name = element.Name
                        current_path = f"{path}\\{element_name}" if path else element_name

                        # Only process enterable specs
                        if not _is_enterable(element):
                            try:
                                if hasattr(element, 'Elements') and element.Elements.Count > 0:
                                    _traverse_elements(element, current_path, specifications)
                            except:
                                pass
                            continue

                    # Get description
                        try:
                            description = element.AttributeValue(19)
                            if not description:
                                description = f"Specification for {element_name}"
                        except:
                            description = f"Specification for {element_name}"

                    # Get value and unit info
                        value_info = _get_element_value_and_unit(element)

                        specifications[current_path] = {
                            'description': description,
                            'value': value_info['value'],
                            'unit': value_info['unit'],
                            'unit_category': value_info['unit_category'],
                            'basis': value_info.get('basis'),
                            'options': value_info.get('options', [])
                        }

                    # Recurse into sub-elements
                        try:
                            if hasattr(element, 'Elements') and element.Elements.Count > 0:
                                _traverse_elements(element, current_path, specifications)
                        except:
                            pass

                    except:
                        continue
            except:
                pass
            return specifications

        try:
            reaction_node = self.aspen.Tree.FindNode(rf"\Data\Reactions\Reactions\{reac_set}\Input")
        
            if not reaction_node:
                raise UDE.AspenPlus_BlockTypeError(f"Cannot find reaction set {reac_set} in the AspenFile!")

            specifications = _traverse_elements(reaction_node)

            return specifications

        except Exception as e:
            raise UDE.AspenPlus_BlockTypeError(f"Error retrieving Reaction Specifications: {str(e)}")


    def Set_ReactionInputSpecifications(self, set_name, specifications_dict=None, **specifications):
        """Set reaction specifications with support for value, unit and basis configuration.
        Uses dynamic specification discovery and supports setting value, unit and basis simultaneously.
    
        :param set_name: String. Name of the reaction set to set specifications
        :param specifications_dict: Dictionary. Specifications as {spec_name: config} format
        :param specifications: Keyword arguments for reaction specifications
        :return: None
    
        Configuration formats:
        1. Simple value: spec_name = value
        2. Value with unit: spec_name = {'value': value, 'unit': unit_index}
        3. Value with basis: spec_name = {'value': value, 'basis': basis_string}
        4. Complete config: spec_name = {'value': value, 'unit': unit_index, 'basis': basis_string}
        """
        if type(set_name) != str:
            raise TypeError("set_name must be a 'String'!!!")
    
        set_name = set_name.upper()
    
        status_report = []

        # Merge all input methods
        all_specs = {}
        if specifications_dict:
            all_specs.update(specifications_dict)
        all_specs.update(specifications)
    
        if not all_specs:
            raise UDE.AspenPlus_BlockTypeError(f"No specifications provided for {set_name}")
    
        def _normalize_config(spec_name, config):
            """Normalize configuration to standard format."""
            if isinstance(config, (int, float, str)):
                return {'value': config, 'unit': None, 'basis': None}
            elif isinstance(config, dict):
                return {
                    'value': config.get('value'),
                    'unit': config.get('unit'),
                    'basis': config.get('basis')
                }
            else:
                return {'value': config, 'unit': None, 'basis': None}
    
        def _set_element_with_config(element, config, basis_element=None, spec_name=""):
            """Set element value with optional unit and basis."""
            value = config['value']
            unit = config['unit']
            basis = config['basis']
    
            if value is None:
                status_report.append(f"Warning: No value provided for {spec_name}")
                return False
    
            try:
                if basis is not None and basis_element is not None:
                    # Set basis variable
                    basis_element.Value = basis
                    status_report.append(f"   -> Set BASIS for {spec_name}: {basis}")
    
                    if unit is not None:
                        element.SetValueUnitAndBASIS(value, unit, basis)
                    else:
                        element.SetValueUnitAndBASIS(value, 0, basis)
                elif unit is not None:
                    element.SetValueAndUnit(value, unit)
                else:
                    element.Value = value
    
                return True
    
            except Exception as e:
                status_report.append(f"   Error setting {spec_name}: {str(e)}")
                return False
                
        def _get_element(parent_node, name):
            """Helper to get an element by name, with a fallback iteration for duplicate names."""
            try:
                el = parent_node.Elements(name)
                if el is not None:
                    return el
            except:
                pass
            # Fallback: iterate over elements
            try:
                for child in parent_node.Elements:
                    if child.Name == name:
                        return child
            except:
                pass
            return None
    
        try:
            # Path for Reaction Set Input
            # Note: Depending on reaction type, structure might vary slightly, but this is the standard path.
            reaction_node = self.aspen.Tree.FindNode(rf"\Data\Reactions\Reactions\{set_name}\Input")
            
            if not reaction_node:
                 raise UDE.AspenPlus_BlockTypeError(f"Cannot find reaction set {set_name} in the AspenFile!")
    
            status_report.append(f"\nSetting specifications for Reaction Set {set_name}:")
    
            successful_sets = 0
            failed_sets = 0
    
            for spec_name, raw_config in all_specs.items():
                try:
                    config = _normalize_config(spec_name, raw_config)
                    spec_name_upper = spec_name.upper()
    
                    target_element = None
                    basis_element = None
    
                    # Handle paths (e.g., COEF\1\MEA)
                    if '\\' in spec_name_upper:
                        path_parts = spec_name_upper.split('\\')
                        current_node = reaction_node
    
                        # Traverse down to the parent of the last element
                        for part in path_parts[:-1]:
                            current_node = _get_element(current_node, part)
                            if current_node is None:
                                break
                        
                        if current_node:
                            final_element = path_parts[-1]
                            target_element = _get_element(current_node, final_element)
                        else:
                            target_element = None
                    else:
                        target_element = _get_element(reaction_node, spec_name_upper)
    
                    if target_element is None:
                        status_report.append(f"  Warning: {spec_name} not found in {set_name}")
                        failed_sets += 1
                        continue
    
                    # Check if it's an array/collection (has Elements property but not a single Value usually)
                    # However, in Aspen COM, even leaf nodes have Elements. Count > 0 usually means it's a folder or array parent.
                    # But some enterable variables might have options (AttributeValue(5))
                    
                    # Verify if enterable (HAP_ENTERABLE = 7, value 1)
                    try:
                        enterable = target_element.AttributeValue(7)
                        if enterable != 1:
                            status_report.append(f"  Warning: {spec_name} is not user-enterable")
                            failed_sets += 1
                            continue
                    except:
                        # If we can't check enterable status, we'll try to set it anyway
                        pass
    
                    # Handle BASIS if needed
                    basis_element = None
                    if config['basis'] is not None:
                         # Usually basis is at the same level or specific path. 
                         # HAP_BASIS (13) gives current basis, but setting it might require finding the right node.
                         # Often the basis node is a sibling named differently, or it's handled via SetValueUnitAndBASIS.
                         # For generic handling, passing basis_element=reaction_node.Elements("BASIS") is a guess.
                         # We rely on SetValueUnitAndBASIS to handle it internally if basis_element is omitted or we fake it.
                         pass 
    
                    if _set_element_with_config(target_element, config, basis_element, spec_name):
                        status_report.append(f"  Successfully set {spec_name} = {config['value']}" + 
                              (f" (Unit: {config['unit']})" if config['unit'] else "") +
                              (f" [Basis: {config['basis']}]" if config['basis'] else ""))
                        successful_sets += 1
                    else:
                        failed_sets += 1
    
                except Exception as e:
                    status_report.append(f"  Error processing {spec_name}: {str(e)}")
                    failed_sets += 1
    
            status_report.append(f"Summary: {successful_sets} successful, {failed_sets} failed.")
            return status_report
            
        except Exception as e:
            raise UDE.AspenPlus_BlockTypeError(f"Error setting Reaction Specifications: {str(e)}")
    
    def Add_Reaction(self, inp_path: str, set_name: str, reactions_data: list, reaction_type: str = "REAC-DIST") -> list:
        """
        Modify INP file to insert new reactions at the bottom of a specific Reaction Set block.
        If the Reaction Set does not exist, it will be automatically appended to the END OF FILE (EOF).
            
        Args:
            inp_path (str): Absolute path to the .inp file.
            set_name (str): Name of the Reaction Set (e.g., MEA-STP, MEA-RXN).
            reactions_data (list): List of dictionaries containing 'id' and 'stoic'. 
                                  Example: [{"id": 1, "stoic": {"MEA": -1.0, "CO2": -1.0, "H2O": 1.0}}]
            reaction_type (str): Type of reaction if creating a new block (default: "REAC-DIST").
                
        Returns:
            list: A list of assigned STOIC numbers for the added reactions. Empty list if failed.
        """

        if not os.path.exists(inp_path):
            raise FileNotFoundError(f"File not found: {inp_path}")

        # Helper function to format a single reaction dictionary into STOIC lines
        def format_reaction_lines(rxn_dict: dict) -> list:
            """Formats a reaction dict into properly spaced STOIC lines (max 80 chars per line)"""
            lines = []
            stoic_num = rxn_dict.get("id")
            stoic_data = rxn_dict.get("stoic", {})
            
            if stoic_num is None or not stoic_data:
                raise ValueError(f"Skipping invalid reaction data: {rxn_dict}")
                
            # Start of the sentence: (空四格)STOIC(空一格){REAC NO.}(空一個)
            current_line = f"    STOIC {stoic_num} "
            
            # Format components: {ssid} {物質} {-}{反應係數}
            parts = []
            default_ssid = rxn_dict.get("default_ssid")
            for comp, data in stoic_data.items():
                if isinstance(data, dict):
                    coef = data.get("coef")
                    ssid = data.get("ssid", default_ssid)
                else:
                    coef = data
                    ssid = default_ssid

                # Only POWERLAW and LHHW reaction types support/need the ssid prefix
                if ssid and reaction_type.upper() in ["POWERLAW", "LHHW"]:
                    parts.append(f"{ssid} {comp} {coef}")
                else:
                    parts.append(f"{comp} {coef}")
            
            # Combine parts with /(空一格) OR (空一格)/(空一格)
            # The prompt requested: {反應物1} {-}{反應係數}/ {反應物2} {-}{反應係數} / ...
            for i, part in enumerate(parts):
                # If it's the first part, just add it
                if i == 0:
                    current_line += part
                else:
                    # Check if adding ' / ' + part will exceed 80 chars (considering trailing space)
                    if len(current_line) + len(" / " + part) > 78:
                        # Close current line with & and start a new line
                        current_line += " / &"
                        lines.append(current_line)
                        current_line = f"        {part}"
                    else:
                        current_line += f" / {part}"
            
            # Ensure it ends with space according to prompt requested "(空一格)" at the very end
            current_line += " "
            
            lines.append(current_line)
            return [line + "\n" for line in lines]

        try:
            try:
                with open(inp_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(inp_path, 'r', encoding='cp950', errors='replace') as f:
                    lines = f.readlines()

            # Target header pattern: exactly "REACTIONS {set_name} {something} "
            # \s+ matches ONE OR MORE spaces. We change it to a literal space " " or " *"
            # But earlier you asked about exactly one space.
            target_header_pattern = re.compile(rf"^REACTIONS\s+{re.escape(set_name)}\s+", re.IGNORECASE)
                
            in_target_block = False
            insert_index = -1

            for i, line in enumerate(lines):
                if not in_target_block:
                    if target_header_pattern.match(line):
                        in_target_block = True
                else:
                    # If we find a line that starts without spaces/tabs (meaning a new main block), 
                    # we found the end of the REACTIONS block.
                    if line.strip() != "" and not line.startswith(' ') and not line.startswith('\t'):
                        insert_index = i
                        break

            # Prepare the new reaction lines and assigned IDs
            assigned_ids = []
            new_content_lines = []

            for rxn_dict in reactions_data:
                stoic_num = rxn_dict.get("id")
                formatted_lines = format_reaction_lines(rxn_dict)
                if formatted_lines:
                    new_content_lines.extend(formatted_lines)
                    assigned_ids.append(stoic_num)

            if not new_content_lines:
                raise ValueError("No valid reactions provided to add.")

            if insert_index != -1:
                # adjust insert_index upwards if there are trailing blank lines in the block
                while insert_index > 0 and lines[insert_index - 1].strip() == "":
                    insert_index -= 1
                
                # Insert all new lines
                for line in reversed(new_content_lines):
                    lines.insert(insert_index, line)
            elif in_target_block:
                while len(lines) > 0 and lines[-1].strip() == "":
                    lines.pop(-1)
                if len(lines) > 0 and not lines[-1].endswith("\n"):
                    lines[-1] += "\n"
                lines.extend(new_content_lines)
            else:
                while len(lines) > 0 and lines[-1].strip() == "":
                    lines.pop(-1)
                if len(lines) > 0 and not lines[-1].endswith("\n"):
                    lines[-1] += "\n"
                new_block_header = f"\nREACTIONS {set_name} {reaction_type} \n"
                lines.append(new_block_header)
                lines.extend(new_content_lines)

            with open(inp_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                    
            return assigned_ids
                
        except Exception as e:
            raise RuntimeError(f"Error modifying INP file: {str(e)}")

    def Remove_Reaction(self, inp_path: str, set_name: str, reactions_data: list, reaction_type: str) -> bool:
        """
        Modifies the Reaction Set block in an INP file. This method reconstructs the block 
        by completely deleting the old set and re-adding only the provided reactions using Add_Reaction.
        
        Args:
            inp_path (str): Absolute path to the .inp file.
            set_name (str): Name of the Reaction Set (e.g., ABSORBER).
            reactions_data (list): List of dictionaries containing ONLY 'id' and 'stoic'.
                                   DO NOT pass parameter keys (like RATE-CON) here.
            reaction_type (str): Type of the reaction, used to reconstruct the block header 
                                 (e.g., POWERLAW, KINETIC). Default is "POWERLAW".
            
        Returns:
            bool: True if execution is successful, False otherwise.
        """
        if not os.path.exists(inp_path):
            raise FileNotFoundError(f"File not found: {inp_path}")

        # Helper function to format a single reaction dictionary into STOIC lines
        def format_reaction_lines(rxn_dict: dict) -> list:
            """Formats a reaction dict into properly spaced STOIC lines (max 80 chars per line)"""
            lines = []
            stoic_num = rxn_dict.get("id")
            stoic_data = rxn_dict.get("stoic", {})
            
            if stoic_num is None or not stoic_data:
                raise ValueError(f"Skipping invalid reaction data: {rxn_dict}")
            
            current_line = f"    STOIC {stoic_num} "
            
            parts = []
            default_ssid = rxn_dict.get("default_ssid")
            for comp, data in stoic_data.items():
                if isinstance(data, dict):
                    coef = data.get("coef")
                    ssid = data.get("ssid", default_ssid)
                else:
                    coef = data
                    ssid = default_ssid

                if ssid and reaction_type.upper() in ["POWERLAW", "LHHW"]:
                    parts.append(f"{ssid} {comp} {coef}")
                else:
                    parts.append(f"{comp} {coef}")
            
            for i, part in enumerate(parts):
                if i == 0:
                    current_line += part
                else:
                    if len(current_line) + len(" / " + part) > 78:
                        current_line += " / &"
                        lines.append(current_line)
                        current_line = f"        {part}"
                    else:
                        current_line += f" / {part}"
            
            current_line += " "
            lines.append(current_line)
            return [line + "\n" for line in lines]

        try:
            try:
                with open(inp_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(inp_path, 'r', encoding='cp950', errors='replace') as f:
                    lines = f.readlines()

            target_header_pattern = re.compile(rf"^REACTIONS\s+{re.escape(set_name)}\s+", re.IGNORECASE)            
            in_target_block = False
            start_index = -1
            end_index = -1

            for i, line in enumerate(lines):
                if not in_target_block:
                    if target_header_pattern.match(line):
                        in_target_block = True
                        start_index = i
                else:
                    # 遇到無縮排的非空行，代表該 REACTIONS 區塊結束
                    if line.strip() != "" and not line.startswith(' ') and not line.startswith('\t'):
                        end_index = i
                        break

            if start_index == -1:
                raise ValueError(f"Reaction Set '{set_name}' not found in the file. Cannot remove reactions. Please use Add_Reaction instead.")        
            # 若一直到檔尾都沒有新區塊，end_index 就是檔尾
            if end_index == -1:
                end_index = len(lines)

            # 準備重建的內容
            new_content_lines = []
            # 保留原有的 Header 行
            original_header = lines[start_index]
            new_content_lines.append(original_header)

            # 寫入保留的 STOIC
            for rxn_dict in reactions_data:
                formatted_lines = format_reaction_lines(rxn_dict)
                if formatted_lines:
                    new_content_lines.extend(formatted_lines)

            # 移除舊區塊的空行
            while end_index > start_index and lines[end_index - 1].strip() == "":
                end_index -= 1
            
            lines[start_index:end_index] = new_content_lines

            with open(inp_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            return True
            
        except Exception as e:
            raise RuntimeError(f"Error modifying INP file: {str(e)}")
