# -*- coding: utf-8 -*-
"""
Convergence operations for Aspen Plus COM interface.
Handles convergence settings for simulation loops.

Corresponds to: mcp_tools/convergence/
"""

import UserDifineException as UDE


class ConvergenceMixin:
    """Mixin class for Aspen Plus convergence operations."""

    def Get_InputConvergence(self, table=False):
        """Get all available input specifications for convergence settings.
        Includes unit_category (HAP_UNITROW) for each specification to enable unit_list queries.
        
        :param table: Boolean. If True, return as dictionary; if False, print to console
        :return: Dictionary with specification names, descriptions, values, units, and unit_category (if table=True)
        """
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

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
            conv_node = self.aspen.Tree.FindNode(r"\Data\Convergence\Conv-Options\Input")
            specifications = _traverse_elements(conv_node)
            
            if table:
                return specifications
            else:
                print(f"\nConvergence Input Specifications:")
                for name, info in specifications.items():
                    unit_cat = f" [unit_category={info['unit_category']}]" if info['unit_category'] else ""
                    print(f"  {name}: {info['description']}{unit_cat}")
                    
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get convergence specifications: {str(e)}")

    def Set_InputConvergence(self, specifications_dict=None, **specifications):
        """Set convergence conditions with support for value, unit and basis configuration.
        Uses dynamic specification discovery and supports setting value, unit and basis simultaneously.

        :param specifications_dict: Dictionary. Specifications as {spec_name: config} format
        :param specifications: Keyword arguments for convergence specifications
        :return: None

        Configuration formats:
        1. Simple value: spec_name = value
        2. Value with unit: spec_name = {'value': value, 'unit': unit_index}
        3. Complete config: spec_name = {'value': value, 'unit': unit_index, 'basis': basis_string}

        Examples:
            # Method 1: Simple values
            Set_InputConvergence(TOL=0.001, WEG_MAXIT=100)

            # Method 2: With units (unit_index from UnitList)
            Set_InputConvergence(TOL={'value': 0.001, 'unit': 1})

            # Method 3: Using dictionary
            specs = {
                'TOL': 0.001,
                'WEG_MAXIT': 100
            }
            Set_InputConvergence(specifications_dict=specs)
        """
        # Merge all input methods
        all_specs = {}
        if specifications_dict:
            all_specs.update(specifications_dict)
        all_specs.update(specifications)

        if not all_specs:
            print("No specifications provided for convergence settings")
            return

        def _normalize_config(spec_name, config):
            """Normalize configuration to standard format."""
            if isinstance(config, (int, float)):
                # Simple value
                return {'value': config, 'unit': None, 'basis': None}
            elif isinstance(config, dict):
                # Dictionary configuration
                return {
                    'value': config.get('value'),
                    'unit': config.get('unit'),
                    'basis': config.get('basis')
                }
            else:
                # String or other types as simple value
                return {'value': config, 'unit': None, 'basis': None}

        def _set_element_with_config(element, config):
            """Set element value with optional unit."""
            value = config['value']
            unit = config['unit']

            if value is None:
                print(f"Warning: No value provided for element")
                return False

            try:
                if unit is not None:
                    # Use SetValueAndUnit method
                    element.SetValueAndUnit(value, unit)
                else:
                    # Only set value
                    element.Value = value
                return True

            except Exception as e:
                print(f"Error setting element: {str(e)}")
                return False

        try:
            conv_node = self.aspen.Tree.FindNode(r"\Data\Convergence\Conv-Options\Input")

            print(f"\nSetting convergence specifications:")
            print("-" * 70)

            successful_sets = 0
            failed_sets = 0

            for spec_name, raw_config in all_specs.items():
                try:
                    # Normalize configuration
                    config = _normalize_config(spec_name, raw_config)
                    spec_name_upper = spec_name.upper()

                    # Find target element
                    target_element = None

                    # Handle paths (e.g., NESTED\SPEC)
                    if '\\' in spec_name_upper:
                        path_parts = spec_name_upper.split('\\')
                        current_node = conv_node

                        # Navigate to target node
                        for part in path_parts[:-1]:
                            current_node = current_node.Elements(part)

                        # Final element
                        final_element = path_parts[-1]
                        target_element = current_node.Elements(final_element)

                    else:
                        # Simple spec name - try direct access
                        try:
                            target_element = conv_node.Elements(spec_name_upper)
                        except:
                            print(f"  Warning: {spec_name} not found")
                            failed_sets += 1
                            continue

                    # Set value
                    if target_element is not None:
                        success = _set_element_with_config(target_element, config)

                        if success:
                            # Display info
                            display_parts = [f"value={config['value']}"]
                            if config['unit'] is not None:
                                try:
                                    unit_name = self.UnitList([target_element.AttributeValue(2), config['unit']],
                                                              table=True)
                                    display_parts.append(f"unit={unit_name}")
                                except:
                                    display_parts.append(f"unit=index_{config['unit']}")

                            print(f"  Set {spec_name}: {', '.join(display_parts)}")
                            successful_sets += 1
                        else:
                            failed_sets += 1
                    else:
                        print(f"  Could not find element for {spec_name}")
                        failed_sets += 1

                except Exception as e:
                    print(f"  Failed to set {spec_name}: {str(e)}")
                    failed_sets += 1

            print(f"\nSummary: {successful_sets} successful, {failed_sets} failed")

            if failed_sets > 0:
                print(f"\nTips:")
                print(f"- Use Get_InputConvergence() to see available specifications")
                print(f"- Use UnitList() to find correct unit indices")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to set convergence conditions: {str(e)}")
