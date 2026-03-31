# -*- coding: utf-8 -*-
"""
Component operations for Aspen Plus COM interface.
Handles component listing.

Corresponds to: mcp_tools/components/
"""


class ComponentsMixin:
    """Mixin class for Aspen Plus component operations."""

    def ComponentsList(self) -> list:
        """Get the components-list in AspenFile with 'List Type'.

        :return: List. a list with all components name in AspenFile.
        """
        a_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Components").Elements("Comp-Lists").Elements(
                "GLOBAL").Elements("Input").Elements("CID").Elements:
            a_list.append(e.Value)
        return a_list

    def HenryCompsList(self, table=False, set_name="GLOBAL"): 
        """Get all available property specifications including nested elements, option lists, values and units.
        Only shows specifications where HAP_ENTERABLE = 1 (user can input values).

        :param table: Boolean. If True, return as dictionary; if False, print to console
        :param set_name: String. Henry-Comps set name
        :return: Dictionary with property specification names and descriptions (if table=True)

        Example:
            props = HenryCompsList(table=True, set_name="HC-1")
            HenryCompsList(set_name="HC-1")
        """
        ## 檢查輸入的資料型態是否正確
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

        def _is_enterable(element):
            """Check if element is enterable (HAP_ENTERABLE = 7)."""
            try:
                # 7 is HAP_ENTERABLE.
                enterable = element.AttributeValue(7)  # HAP_ENTERABLE = 7
                return enterable == 1
            except:
                return False

        def _get_element_options(element):
            """Get option list for an element if available."""
            options = []
            try:
                # 嘗試獲取選項列表 (AttributeValue 5 是選項列表)
                option_list = element.AttributeValue(5).Elements
                if option_list:
                    for i in range(option_list.Count):
                        options.append(option_list(i).Value)
            except:
                pass
            return options

        def _get_element_value_and_unit(element):
            """Get current value and unit for an element if available."""
            value_info = {}
            try:
                # 嘗試獲取數值
                try:
                    current_value = element.Value
                    if current_value is not None:
                        value_info['value'] = current_value
                    else:
                        value_info['value'] = None
                except:
                    value_info['value'] = None

                # 嘗試獲取單位信息
                try:
                    # AttributeValue(2) 通常是物理量類型 (PQ)
                    # AttributeValue(3) 通常是單位索引 (UM)
                    pq = element.AttributeValue(2)
                    um = element.AttributeValue(3)
                    if pq and um:
                        # Assuming UnitList uses underlying AP method, need to ensure self.UnitList works
                        # AP class generally has UnitList.
                        unit_name = self.UnitList([pq, um], table=True)
                        value_info['unit'] = unit_name
                    else:
                        value_info['unit'] = None
                except:
                    value_info['unit'] = None

                # 嘗試獲取選項列表
                options = _get_element_options(element)
                value_info['options'] = options

            except:
                value_info = {'value': None, 'unit': None, 'options': []}

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

                        # 只處理可輸入的規格 (HAP_ENTERABLE = 7)
                        if not _is_enterable(element):
                            # 遞歸處理子元素
                            try:
                                if hasattr(element, 'Elements') and element.Elements.Count > 0:
                                    _traverse_elements(element, current_path, specifications)
                            except:
                                pass
                            continue

                        # 獲取描述
                        try:
                            description = element.AttributeValue(19)  # HAP_PROMPT = 19
                            if not description:
                                description = f"Component Henry-Comps specification for {element_name}"
                        except:
                            description = f"Component Henry-Comps specification for {element_name}"

                        # 獲取數值和單位信息
                        value_info = _get_element_value_and_unit(element)

                        # 構建完整的描述
                        full_description = description

                        # 添加數值信息
                        if value_info['value'] is not None:
                            value_str = f"Value: {value_info['value']}"
                            if value_info['unit']:
                                value_str += f" {value_info['unit']}"
                            full_description += f" [{value_str}]"
                        else:
                            full_description += " [No Value]"

                        # 添加選項信息
                        if value_info['options']:
                            full_description += f" (Options: {', '.join(value_info['options'])})"

                        specifications[current_path] = {
                            'HenryCompsSet': set_name,
                            'description': description,
                            'full_description': full_description,
                            'value': value_info['value'],
                            'unit': value_info['unit'],
                            'options': value_info['options']
                        }

                        # 遞歸處理子元素
                        try:
                            if hasattr(element, 'Elements') and element.Elements.Count > 0:
                                _traverse_elements(element, current_path, specifications)
                        except:
                            pass

                    except Exception as e:
                        continue

            except Exception as e:
                pass

            return specifications

        try:
            target_path = r"\Data\Components\Henry-Comps\{}\Input".format(set_name)
            
            properties_node = self.aspen.Tree.FindNode(target_path)

            # 遞歸獲取所有可輸入的規格
            specifications = _traverse_elements(properties_node)

            if not table:
                output = []
                output.append(f"\nAvailable ENTERABLE property specifications:")
                output.append("=" * 105)
                output.append(f"{'Specification Path':<40}{'Value':<15}{'Unit':<15}{'Description'}")
                output.append("-" * 105)

                if not specifications:
                    output.append("No enterable property specifications found.")
                    return "\n".join(output)

                for spec_path, spec_info in specifications.items():
                    value_str = str(spec_info['value']) if spec_info['value'] is not None else "N/A"
                    unit_str = spec_info['unit'] if spec_info['unit'] else "N/A"

                    # 截斷過長的路徑和數值
                    path_display = spec_path[:39] if len(spec_path) <= 39 else spec_path[:36] + "..."
                    value_display = value_str[:14] if len(value_str) <= 14 else value_str[:11] + "..."
                    unit_display = unit_str[:14] if len(unit_str) <= 14 else unit_str[:11] + "..."

                    # 如果有選項，在下一行顯示
                    if spec_info['options']:
                        output.append(
                            f"{path_display:<40}{value_display:<15}{unit_display:<15}{spec_info['description']}  {'Options: ' + ', '.join(spec_info['options'])}")
                    else:
                        output.append(f"{path_display:<40}{value_display:<15}{unit_display:<15}{spec_info['description']}")

                output.append(f"\nTotal ENTERABLE property specifications available: {len(specifications)}")

                # 統計信息
                valued_specs = sum(1 for spec in specifications.values() if spec['value'] is not None)
                option_specs = sum(1 for spec in specifications.values() if spec['options'])

                output.append(f"Statistics: {valued_specs} with values, {option_specs} with options")
                
                final_output = "\n".join(output)
                return final_output

            else:
                return specifications

        except Exception as e:
            raise Exception(f"Failed to get property specifications: {str(e)}")

    def Add_HenryCompsSet(self, set_name=""):
        """
        Add a new Henry Components Set to the Aspen Plus simulation.
        you will chenck the set_name is exist or not.
        if return error, you will use Get_HenryCompsSetList() chenck the set_name is exist or not.
        :param set_name: String. The name/ID of the new Henry Component Set.(e.g., HC-1, HC-2).
        :return: None
        """
        
        # Find the root node for Henry Components
        henry_root = self.aspen.Tree.FindNode(r"\Data\Components\Henry-Comps")
            
        set_name = set_name.upper()

        if not set_name:
                existing_names = []
                # Collect existing names
                for e in henry_root.Elements:
                    existing_names.append(e.Name)
                
                # Find the first available HC-{num}
                num = 1
                while f"HC-{num}" in existing_names:
                    num += 1
                
                set_name = f"HC-{num}"
            
        # Check if the Set_name already exists to avoid throwing an error
        for element in henry_root.Elements:
            if element.Name == set_name:
                return element

        # Try to add the new set
        try:
            new_object = henry_root.Elements.Add(set_name)
            return new_object
        except Exception as e:
            raise e

    def Remove_HenryCompsSet(self, set_name):
        """
        Remove a Henry Components Set from the Aspen Plus simulation.
        
        :param set_name: String. The name/ID of the Henry Component Set to remove.
        :return: Boolean. True if successful, False otherwise.
        """
        if type(set_name) != str:
            raise TypeError("set_name must be a 'String'!!!")
            
        # Convert to uppercase to match Aspen's internal naming convention usually
        set_name = set_name.upper()

        try:
            # Find the root node for Henry Components
            henry_root = self.aspen.Tree.FindNode(r"\Data\Components\Henry-Comps")
            
            # Explicitly check if the component exists by iterating through the list
            # This ensures we confirm existence before attempting removal as requested
            found = False
            for element in henry_root.Elements:
                if element.Name == set_name:
                    found = True
                    break
            
            if found:
                henry_root.Elements.Remove(set_name)
                return True
            else:
                return False

        except Exception as e:
            raise e

    def Get_HenryCompsSetList(self):
        """
        Get the list of Henry Components Set.
        :return: List of strings
        """
        try:
            options = []
            element = self.aspen.Application.Tree.FindNode(r"\Data\Components\Henry-Comps")
            Set_list = element.Elements
            if Set_list:
                for i in range(Set_list.Count):
                    options.append(Set_list(i).Name)
            return options
        except Exception as e:
            raise Exception(f"Failed to get Henry Components Set list: {str(e)}")

    def Set_HenryComps(self, inp_path, comps, set_name="HC-1"):
        """
        Set Henry Components in an Aspen Plus Input File (.inp) by directly modifying the text content.
        
        :param inp_path: Absolute path to the .inp file
        :param comps: List of component names (e.g. ["CO2", "H2S"])
        :param set_name: Name of the Henry Component Set (default: "HC-1")
        :return: None
        """
        import os
        
        if not os.path.exists(inp_path):
            raise FileNotFoundError(f"File not found: {inp_path}")
            
        if not inp_path.lower().endswith('.inp'):
             raise ValueError(f"Set_HenryComps requires an .inp file. Got: {inp_path}")
        
        try:
            try:
                with open(inp_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(inp_path, 'r', encoding='cp950', errors='replace') as f:
                    lines = f.readlines()
            
            # Prepare the new component string
            comp_str = " ".join(comps)
            modified = False
            
            # 1. Try to find existing HENRY-COMPS line for this set to replace
            for i, line in enumerate(lines):
                if "HENRY-COMPS" in line and set_name in line:
                    # Keep original indentation
                    indent = line[:len(line) - len(line.lstrip())]
                    new_line = f"{indent}HENRY-COMPS {set_name} {comp_str} \n"
                    lines[i] = new_line
                    if i + 1 < len(lines) and lines[i + 1].strip() != "":
                        lines.insert(i + 1, "\n")
                    modified = True
                    break
            
            # 2. If not found, look for a good place to insert (e.g., before PROPERTIES or after COMPONENTS)
            if not modified:
                # Strategy: Search for PROPERTIES line
                insert_index = -1
                base_indent = " " # Default indentation
                
                for i, line in enumerate(lines):
                    if line.strip().startswith("PROPERTIES"):
                        insert_index = i
                        # Use indentation from this line if possible
                        base_indent = line[:len(line) - len(line.lstrip())]
                        break
                
                if insert_index != -1:
                    new_line = f"{base_indent}HENRY-COMPS {set_name} {comp_str} \n"
                    lines.insert(insert_index, new_line)
                    # Add blank line between HENRY-COMPS and PROPERTIES
                    lines.insert(insert_index + 1, "\n")
                    modified = True
                else:
                    lines.append(f"\nHENRY-COMPS {set_name} {comp_str} \n")
                    modified = True
                 
            with open(inp_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            
        except Exception as e:
            raise Exception(f"Failed to modify INP file: {str(e)}")

    def Elec_Wizard(self, filename, chem_source="APV140 REACTIONS", ref_state="Unsymmetric", h_ion="Hydronium ion H3O+", reaction_opts=None, prop_method="ENRTL-RK", sim_approach="True component approach"):
        """
        Aspen Plus Electrolyte Wizard Automation Tool.
        
        Args:
            filename (str): The Aspen Plus backup filename (e.g., "E2.bkp") used to identify the main window.
            chem_source (str): Chemistry Data Source (e.g., "APV140 REACTIONS").
            ref_state (str): Reference State ("Symmetric" or "Unsymmetric").
            h_ion (str): Hydrogen Ion Type ("Hydronium ion H3O+" or "Hydrogen ion H+").
            reaction_opts (list): List of reaction options to check (e.g., ["Include salt formation"]).
            prop_method (str): Global Property Method (e.g., "ENRTL-RK").
            sim_approach (str): Simulation Approach (e.g., "True component approach").
            
        Returns:
            dict: Result dictionary with "success" (bool) and "message" (str).
        """
        import uiautomation as auto
        import time

        # Shared State
        aspen_window = None
        wizard_window = None
        
        if reaction_opts is None: 
            reaction_opts = ["Include salt formation"]

        # --- Nested Helper Functions ---



        def get_aspen_window_helper(class_name_pattern=None):
            nonlocal aspen_window
            search_properties = {
                "searchDepth": 1,
                "SubName": filename,
            }
            if class_name_pattern:
                search_properties["RegexClassName"] = class_name_pattern
                
            window = auto.WindowControl(**search_properties)
            
            if window.Exists(maxSearchSeconds=3):
                window.SetTopmost(True)
                window.SetTopmost(False)
                window.SetActive()
                aspen_window = window
                return window
            else:
                return None

        def check_properties_node():
            if not aspen_window: return None
            
            nav_bar = aspen_window.CustomControl(AutomationId="PART_NavigatorBar")
            
            if nav_bar.Exists(maxSearchSeconds=2):
                nav_rect = nav_bar.BoundingRectangle
                nav_height = nav_rect.height()
                nav_mid_y = nav_rect.top + (nav_height / 2)
                
                target_prop_node = None
                for control, depth in auto.WalkControl(nav_bar, maxDepth=4):
                    if control.Name == "Properties" and control.ControlTypeName == "TextControl":
                        rect = control.BoundingRectangle
                        if rect.top < nav_mid_y: 
                            target_prop_node = control
                            break
                
                if target_prop_node and target_prop_node.Exists(maxSearchSeconds=1):
                    return target_prop_node
                else:
                    bottom_prop_btn = None
                    for control, depth in auto.WalkControl(nav_bar, maxDepth=4):
                         if control.Name == "Properties" and control.BoundingRectangle.top > nav_mid_y:
                             bottom_prop_btn = control
                             break
                    
                    if bottom_prop_btn:
                        time.sleep(2)
                        bottom_prop_btn.Click()
                        time.sleep(1)
                        # Recursion via self-call not clean in nested, just retry once logic
                        # Or call check_properties_node() again? Yes, function is defined.
                        return check_properties_node() 
                    else:
                        return None
            else:
                return None

        def check_components_node():
            if not aspen_window: return None

            nav_bar = aspen_window.CustomControl(AutomationId="PART_NavigatorBar")
            if not nav_bar.Exists(maxSearchSeconds=1):
                return None
                
            for control, depth in auto.WalkControl(nav_bar, maxDepth=8):
                if control.Name and control.Name.strip() == "Components":
                    if control.ControlTypeName == "TreeItemControl":
                        return control
                    try:
                        parent = control.GetParentControl()
                    except:
                        parent = control.GetParent()

                    if parent and parent.ControlTypeName == "TreeItemControl":
                        return parent
                    else:
                         return control
            return None

        def check_specifications_node(comp_node):
            if not comp_node: return None

            try:
                expand_pattern = comp_node.GetExpandCollapsePattern()
                if expand_pattern:
                    if str(expand_pattern.ExpandCollapseState) != "ExpandCollapseState_Expanded":
                         expand_pattern.Expand()
                         time.sleep(1)
            except: pass
            
            try:
                comp_runtime_id = comp_node.GetRuntimeId()
            except:
                comp_runtime_id = None

            for control, depth in auto.WalkControl(comp_node, maxDepth=4):
                if control.Name and control.Name.strip() == "Specifications":
                    try:
                        parent = control.GetParentControl()
                        if parent:
                            if comp_runtime_id:
                                parent_id = parent.GetRuntimeId()
                                if parent_id == comp_runtime_id: 
                                    return control
                    except: pass
                    return control
            return None

        def click_elec_wizard_button():
            if not aspen_window: return False
            
            wizard_btn = aspen_window.ButtonControl(Name="Elec Wizard")
            if wizard_btn.Exists(maxSearchSeconds=2):
                if wizard_btn.IsEnabled:
                    time.sleep(2)
                    wizard_btn.Click()
                    return True
                else:
                    return False
                    
            container = aspen_window.CustomControl(AutomationId="cmdElecWizard")
            if container.Exists(maxSearchSeconds=2):
                btn = container.ButtonControl(searchDepth=2)
                if btn.Exists(maxSearchSeconds=1):
                    time.sleep(2)
                    btn.Click()
                    return True
            return False

        def check_wizard_window_exists_helper():
            nonlocal wizard_window
            win = auto.WindowControl(Name="Electrolyte Wizard", searchDepth=2)
            if not win.Exists(maxSearchSeconds=5):
                if aspen_window:
                    win = aspen_window.WindowControl(Name="Electrolyte Wizard")
                
            if win.Exists(maxSearchSeconds=2):
                wizard_window = win
                return win
            else:
                return None

        def action_open_wizard():
            existing = check_wizard_window_exists_helper()
            if existing: return existing
            
            if not aspen_window: return None

            prop_node = check_properties_node()
            if not prop_node: return None
            
            comp_node = check_components_node()
            if not comp_node:
                try:
                    prop_node.Click()
                    time.sleep(1)
                except: pass
                comp_node = check_components_node()
                
            if not comp_node: return None
                
            spec_node = check_specifications_node(comp_node)
            if not spec_node: return None

            max_retries = 3
            for attempt in range(max_retries):
                try:
                    spec_node.SetFocus()
                    time.sleep(2)
                    spec_node.Click()
                    time.sleep(5) 
                except: return None

                if click_elec_wizard_button():
                    if check_wizard_window_exists_helper():
                        time.sleep(2)
                        return wizard_window
            return None

        def click_next_button(next_page_title=None):
            if not wizard_window: return False
            
            max_retries = 3
            for attempt in range(max_retries):
                next_btn = wizard_window.ButtonControl(Name="Next>")
                
                if next_btn.Exists(maxSearchSeconds=2):
                    if next_btn.IsEnabled:
                        try:
                            time.sleep(2)
                            next_btn.Click()
                            time.sleep(1)
                            if next_page_title:
                                if wizard_window.TextControl(Name=next_page_title, searchDepth=5).Exists(maxSearchSeconds=3):
                                    return True
                                else:
                                    continue
                            else:
                                return True
                        except: return False
                    else:
                        return False
                else:
                    return False
            return False

        # --- Page Helpers (Nested) ---

        def handle_chemistry_data_source(source_name):
            combo_box = wizard_window.ComboBoxControl(AutomationId="cboDBSelect")
            if not combo_box.Exists(maxSearchSeconds=5): return False
            
            current_selection = "Unknown"
            try:
                val_pattern = combo_box.GetValuePattern()
                if val_pattern: current_selection = val_pattern.Value
            except: pass
            
            if current_selection == "Unknown" or not current_selection:
                 try:
                     legacy = combo_box.GetLegacyIAccessiblePattern()
                     if legacy: current_selection = legacy.Value
                 except: pass
                 
            if current_selection != source_name:
                 try:
                     sel_pattern = combo_box.GetSelectionPattern()
                     if sel_pattern:
                         items = sel_pattern.GetSelection()
                         if items: current_selection = items[0].Name
                 except: pass

            if current_selection == source_name: return True
            
            try:
                combo_box.SetFocus()
                time.sleep(2)
                combo_box.Click()
                time.sleep(1)
            except: pass
            
            list_item = combo_box.ListItemControl(Name=source_name)
            if list_item.Exists(maxSearchSeconds=2):
                try:
                    time.sleep(2)
                    list_item.Click()
                    return True
                except: return False
            return False

        def handle_reference_state(target_state):
            target_state = target_state.capitalize()

            
            combo_box = wizard_window.ComboBoxControl(AutomationId="cboRefStateSelect")
            if not combo_box.Exists(maxSearchSeconds=5): 
                return False
            
            for attempt in range(3):
                current = "Unknown"
                try:
                    val = combo_box.GetValuePattern()
                    if val: current = val.Value
                except: pass
                
                if current == "Unknown":
                    try:
                        legacy = combo_box.GetLegacyIAccessiblePattern()
                        if legacy: current = legacy.Value
                    except: pass
                
                if not current or current == "":
                    try:
                         sel_pattern = combo_box.GetSelectionPattern()
                         if sel_pattern:
                             items = sel_pattern.GetSelection()
                             if items: current = items[0].Name
                    except: pass
                    
                    if not current or current == "":
                         try:
                             children = combo_box.GetChildren()
                             for child in children:
                                 if child.ControlTypeName == "TextControl" and child.Name:
                                     current = child.Name
                                     break
                                 grand_children = child.GetChildren()
                                 for grandchild in grand_children:
                                      if grandchild.ControlTypeName == "TextControl" and grandchild.Name:
                                           current = grandchild.Name
                                           break
                         except: pass
                

                
                if current == target_state: 
                    return True
                

                try:
                    combo_box.SetFocus()
                    time.sleep(2)
                    combo_box.Click()
                    time.sleep(1)
                except: pass
                
                list_item = combo_box.ListItemControl(Name=target_state)
                if list_item.Exists(maxSearchSeconds=2):
                    try:
                        try:
                            scroll = list_item.GetScrollItemPattern()
                            if scroll: scroll.ScrollIntoView()
                        except: pass
                        time.sleep(2)
                        list_item.Click()
                        time.sleep(1)
                        continue
                    except Exception as e: 
                        return False
            return False

        def handle_select_all_components():
            btn = wizard_window.ButtonControl(Name=">>")
            if not btn.Exists(maxSearchSeconds=1):
                btn = wizard_window.ButtonControl(AutomationId="M22")
                
            if btn.Exists(maxSearchSeconds=2):
                try:
                    time.sleep(2)
                    btn.Click()
                    time.sleep(1)
                    return True
                except: return False
            return False

        def handle_hydrogen_ion(h_ion_type):
            radio = wizard_window.RadioButtonControl(Name=h_ion_type)
            if not radio.Exists(maxSearchSeconds=1):
                radio = wizard_window.RadioButtonControl(SubName=h_ion_type)
                
            if radio.Exists(maxSearchSeconds=2):
                try:
                    is_sel = False
                    try:
                        p = radio.GetSelectionItemPattern()
                        if p: is_sel = p.IsSelected
                    except: pass
                    
                    if not is_sel:
                        try:
                            l = radio.GetLegacyIAccessiblePattern()
                            if l and (l.State & auto.State.Selected): is_sel = True
                        except: pass
                        
                    if not is_sel:
                        time.sleep(2)
                        radio.Click()
                    return True
                except:
                    try: time.sleep(2); radio.Click(); return True
                    except: return False
            return False

        def handle_reaction_options(options_list):
            if options_list is None: options_list = []
            known_options = [
                "Include ice formation", 
                "Include salt formation", 
                "Include water dissociation reaction"
            ]
            targets = list(set(known_options) | set(options_list))
            targets.sort()
            
            for opt in targets:
                should_check = opt in options_list
                chk = wizard_window.CheckBoxControl(Name=opt)
                if not chk.Exists(maxSearchSeconds=0.5):
                    chk = wizard_window.CheckBoxControl(SubName=opt)
                    
                if chk.Exists(maxSearchSeconds=1):
                    try:
                        is_checked = False
                        try:
                            t = chk.GetTogglePattern()
                            if t and t.ToggleState == auto.ToggleState.On: is_checked = True
                        except: pass
                        
                        if not is_checked:
                            try:
                                l = chk.GetLegacyIAccessiblePattern()
                                if l and (l.State & auto.State.Checked): is_checked = True
                            except: pass
                            
                        if is_checked != should_check:
                            time.sleep(2)
                            chk.Click()
                            time.sleep(0.5)
                    except: return False
            return True

        def handle_global_property_method(method):
            radio = wizard_window.RadioButtonControl(Name="Set up with property method:")
            if not radio.Exists(maxSearchSeconds=2): return False
            
            try:
                sel = radio.GetSelectionItemPattern()
                if sel and not sel.IsSelected: 
                    time.sleep(2)
                    radio.Click()
                time.sleep(1)
            except: time.sleep(2); radio.Click()
            
            combo = None
            parent = radio.GetParentControl()
            if parent: combo = parent.ComboBoxControl(searchDepth=2)
            
            if not combo or not combo.Exists(maxSearchSeconds=1):
                group = wizard_window.GroupControl(Name="Set up global property method")
                if group.Exists(maxSearchSeconds=1): combo = group.ComboBoxControl()
                else: combo = wizard_window.ComboBoxControl(AutomationId="", searchDepth=4)
                
            if combo and combo.Exists(maxSearchSeconds=2):
                current = "Unknown"
                try:
                    v = combo.GetValuePattern()
                    if v: current = v.Value
                except: pass
                
                if current != method:
                    time.sleep(2)
                    combo.Click()
                    time.sleep(1)
                    item = combo.ListItemControl(Name=method)
                    if item.Exists(maxSearchSeconds=2):
                        time.sleep(2)
                        item.Click()
                        return True
                    return False
                return True
            return False

        def handle_simulation_approach(approach):
            radio = wizard_window.RadioButtonControl(Name=approach)
            if not radio.Exists(maxSearchSeconds=1):
                g = wizard_window.GroupControl(Name="Select electrolyte simulation approach")
                if g.Exists(maxSearchSeconds=1): radio = g.RadioButtonControl(Name=approach)
                
            if radio.Exists(maxSearchSeconds=2):
                try:
                    is_sel = False
                    try:
                        s = radio.GetSelectionItemPattern()
                        if s: is_sel = s.IsSelected
                    except: pass
                    
                    if not is_sel:
                        try:
                            l = radio.GetLegacyIAccessiblePattern()
                            if l and (l.State & auto.State.Selected): is_sel = True
                        except: pass
                        
                    if not is_sel:
                        time.sleep(2)
                        radio.Click()
                        time.sleep(0.5)
                    return True
                except: return False
            return False

        def page5_finish():
            if not wizard_window.TextControl(Name="Summary").Exists(maxSearchSeconds=2):
                return False
            
            btn = wizard_window.ButtonControl(Name="Finish")
            if btn.Exists(maxSearchSeconds=2) and btn.IsEnabled:
                time.sleep(2)
                btn.Click()
                return True
            return False

        # --- Error Handling Helper ---
        
        def close_wizard_window():
            if not wizard_window: return
            
            try:
                # Direct Window Pattern Close
                if wizard_window.Exists(maxSearchSeconds=1):
                    wp = wizard_window.GetWindowPattern()
                    if wp: 
                        wp.Close()
                        # Check for "Are you sure?" confirmation dialog
                        time.sleep(1.0)
                        if wizard_window.Exists(maxSearchSeconds=0.5):
                            # Try to find and click "Yes" button (common in confirmation popups)
                            yes_btn = wizard_window.ButtonControl(Name="Yes", searchDepth=3)
                            if yes_btn.Exists(maxSearchSeconds=1):
                                time.sleep(2)
                                yes_btn.Click()
            except: pass
                
        def handle_error(msg):
            try:
                close_wizard_window()
            except: pass
            return {"success": False, "message": msg}

        # --- Start Execution Logic ---

        print(f"Starting Elec Wizard Automation for {filename}...")
        
        # 1. Connect
        if not get_aspen_window_helper():
            return {"success": False, "message": "Aspen Window not found"}
            
        # 2. Open Wizard
        if not action_open_wizard():
            return {"success": False, "message": "Failed to open Wizard"}
            
        print("Wizard Opened.")
        
        # 3. Page 1
        if not handle_chemistry_data_source(chem_source): return handle_error("Page 1: Chem Source Failed")
        if not handle_reference_state(ref_state): return handle_error("Page 1: Ref State Failed")
        
        if not click_next_button("Base Components and Reactions Generation Options"):
            return handle_error("Failed to transition to Page 2")
            
        # 4. Page 2
        if not handle_select_all_components(): return handle_error("Page 2: Select All Failed")
        if not handle_hydrogen_ion(h_ion): return handle_error("Page 2: H Ion Failed")
        if not handle_reaction_options(reaction_opts): return handle_error("Page 2: Options Failed")
        
        if not click_next_button("Generated Species and Reactions"):
            return handle_error("Failed to transition to Page 3")
            
        # 5. Page 3
        if not wizard_window.TextControl(Name="Generated Species and Reactions").Exists(maxSearchSeconds=2):
                return handle_error("Page 3 title verify failed")
                
        if not handle_global_property_method(prop_method):
                return handle_error("Page 3: Prop Method Failed")
                
        if not click_next_button("Simulation Approach"):
            return handle_error("Failed to transition to Page 4")
            
        # 6. Page 4
        if not wizard_window.TextControl(Name="Simulation Approach").Exists(maxSearchSeconds=2):
                # Try double check
                time.sleep(1)
                if not wizard_window.TextControl(Name="Simulation Approach").Exists(maxSearchSeconds=1):
                    print("Warning: Page 4 title not strictly found, attempting to proceed...")
     
        if not handle_simulation_approach(sim_approach):
                return handle_error("Page 4: Sim Approach Failed")
                
        if not click_next_button("Summary"):
            return handle_error("Failed to transition to Page 5")
            
        # 7. Page 5
        if not page5_finish():
                return handle_error("Page 5: Finish Failed")
                
        return {"success": True, "message": "Wizard Completed Successfully"}