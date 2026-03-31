# -*- coding: utf-8 -*-
"""
Property operations for Aspen Plus COM interface.
Handles thermodynamic method and property specifications.

Corresponds to: mcp_tools/properties/
"""

import UserDifineException as UDE


class PropertiesMixin:
    """Mixin class for Aspen Plus property operations."""

    def Get_PropertiesList(self, table=False):
        """Get all available property specifications.
        
        :param table: Boolean. If True, return as dictionary; if False, print to console
        :return: Dictionary with property specification names and descriptions (if table=True)
        """
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

        try:
            properties_node = self.aspen.Tree.FindNode(r"\Data\Properties\Specifications\Input")
            specifications = {}

            for element in properties_node.Elements:
                try:
                    spec_name = element.Name
                    try:
                        description = element.AttributeValue(19)
                    except:
                        description = f"Property specification for {spec_name}"

                    specifications[spec_name] = {
                        'description': description,
                        'value': None,
                        'unit': None
                    }
                except:
                    continue

            if table:
                return specifications
            else:
                print(f"\nAvailable property specifications:")
                for name, info in specifications.items():
                    print(f"  {name}: {info['description']}")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get property specifications: {str(e)}")

    def Set_Properties(self, specifications_dict=None, **specifications):
        """Set property specifications using dynamic specification discovery.

        :param specifications_dict: Dictionary. Specifications as {spec_name: value} format
        :param specifications: Keyword arguments for property specifications
        :return: None
        """
        all_specs = {}
        if specifications_dict:
            all_specs.update(specifications_dict)
        all_specs.update(specifications)

        if not all_specs:
            print("No property specifications provided")
            return

        try:
            properties_node = self.aspen.Tree.FindNode(r"\Data\Properties\Specifications\Input")

            print(f"\nSetting property specifications:")
            print("-" * 60)

            for spec_name, value in all_specs.items():
                try:
                    spec_name_upper = spec_name.upper()

                    if '\\' in spec_name_upper:
                        path_parts = spec_name_upper.split('\\')
                        current_node = properties_node
                        for part in path_parts[:-1]:
                            current_node = current_node.Elements(part)
                        current_node.Elements(path_parts[-1]).Value = value
                    else:
                        properties_node.Elements(spec_name_upper).Value = value

                    print(f"Set {spec_name}: {value}")

                except Exception as e:
                    print(f"Failed to set {spec_name}: {str(e)}")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to set property specifications: {str(e)}")

    def Add_ThermoMethod(self, method_name):
        """Add thermodynamic method to AspenPlus model.

        :param method_name: String. Name of the thermodynamic method (e.g., 'NRTL', 'UNIFAC', 'PENG-ROB')
        :return: None
        """
        if type(method_name) != str:
            raise TypeError("method_name must be a 'String'.")

        print(f"Setting thermodynamic method using Set_Properties...")
        self.Set_Properties(GBASEOPSET=method_name.upper())

    def Set_CommonPropertyMethods(self, thermo_method, **additional_specs):
        """Set common property method combinations with additional specifications.

        :param thermo_method: String. Main thermodynamic method
        :param additional_specs: Additional property specifications as keyword arguments
        :return: None
        """
        if type(thermo_method) != str:
            raise TypeError("thermo_method must be a 'String'.")

        base_specs = {'GBASEOPSET': thermo_method.upper()}
        base_specs.update(additional_specs)

        print(f"Setting property method combination: {thermo_method.upper()}")
        if additional_specs:
            print(f"Additional specifications: {list(additional_specs.keys())}")

        self.Set_Properties(specifications_dict=base_specs)
