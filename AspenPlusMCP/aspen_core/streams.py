# -*- coding: utf-8 -*-
"""
Stream operations for Aspen Plus COM interface.
Handles stream creation, listing, conditions, and connections.
"""

import UserDifineException as UDE


class StreamsMixin:
    """Mixin class for Aspen Plus stream operations."""

    def StreamsList(self) -> list:
        """Get the streams-list in AspenFile with 'List Type'.

        :return: List. a list with [all stream name, stream type] in AspenFile.
        """
        HAP_RECODERTYPE = 6
        a_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Streams").Elements:
            a_list.append([e.Name, e.AttributeValue(HAP_RECODERTYPE)])
        return a_list

    def StreamsNameList(self) -> list:
        """Get only the stream names in AspenFile.

        :return: List. a list with all stream names in AspenFile.
        """
        name_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Streams").Elements:
            name_list.append(e.Name)
        return name_list

    def Add_Stream(self, stream_name, stream_type="MATERIAL"):
        """Add a stream to AspenPlus model.

        :param stream_name: String. Name of the stream to be added
        :param stream_type: String. Type of the stream (default: 'MATERIAL', can also be 'HEAT', 'WORK')
        :return: COM object of the added stream
        """
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'.")
        if type(stream_type) != str:
            raise TypeError("stream_type must be a 'String'.")

        stream_name = stream_name.upper()
        stream_type = stream_type.upper()

        if stream_name in self.StreamsNameList():
            raise UDE.AspenPlus_StreamTypeError(f"Stream {stream_name} already exists in the AspenFile!")

        try:
            streams = self.aspen.Tree.FindNode(r"\Data\Streams")
            new_stream = streams.Elements.Add(f"{stream_name}!{stream_type}")
            print(f"Successfully added {stream_type} stream: {stream_name}")
            return new_stream
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to add stream: {str(e)}")

    def Remove_Stream(self, stream_name, force=False):
        """Remove a stream from AspenPlus model.

        :param stream_name: String. Name of the stream to be removed
        :param force: Boolean. If True, remove even if connected to blocks
        :return: Dictionary with removal status and message
        """
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'!!!")
        if type(force) != bool:
            raise TypeError("force must be a 'Boolean' value.")

        stream_name = stream_name.upper()

        if stream_name not in self.StreamsNameList():
            return {
                'status': 'NOT_FOUND',
                'message': f"Stream {stream_name} not found in the AspenFile!"
            }

        try:
            # Check if stream is connected to any block
            connected_blocks = []
            for block_name in self.BlocksNameList():
                try:
                    connections = self.Connections(block_name, table=True)
                    if stream_name in connections:
                        connected_blocks.append(block_name)
                except:
                    continue

            if connected_blocks and not force:
                return {
                    'status': 'CONNECTED',
                    'message': f"Stream {stream_name} is connected to blocks: {', '.join(connected_blocks)}. Use force=True to remove anyway.",
                    'connected_blocks': connected_blocks
                }

            # Remove stream
            streams_node = self.aspen.Tree.FindNode(r"\Data\Streams")
            streams_node.Elements.Remove(stream_name)

            print(f"Successfully removed stream: {stream_name}")
            return {
                'status': 'SUCCESS',
                'message': f"Stream {stream_name} removed successfully",
                'was_connected_to': connected_blocks if connected_blocks else []
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f"Failed to remove stream {stream_name}: {str(e)}"
            }

    def Get_StreamInputConditionsList(self, stream_name, table=False):
        """Get all available specifications for a specific stream.
        Includes unit_category (HAP_UNITROW) for each specification to enable unit_list queries.
        
        :param stream_name: String. Name of the stream to get specifications
        :param table: Boolean. If True, return as dictionary; if False, print to console
        :return: Dictionary with specification names, descriptions, values, units, and unit_category (if table=True)
        """
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'!!!")
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

        stream_name = stream_name.upper()

        if stream_name not in self.StreamsNameList():
            raise UDE.AspenPlus_StreamTypeError(f"Cannot find stream {stream_name} in the AspenFile!")

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
            stream_node = self.aspen.Tree.FindNode(rf"\Data\Streams\{stream_name}\Input")
            specifications = _traverse_elements(stream_node)
            
            if table:
                return specifications
            else:
                print(f"\nSpecifications for stream {stream_name}:")
                for name, info in specifications.items():
                    unit_cat = f" [unit_category={info['unit_category']}]" if info['unit_category'] else ""
                    print(f"  {name}: {info['description']}{unit_cat}")
                    
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get specifications for {stream_name}: {str(e)}")

    def Set_StreamInputConditions(self, stream_name, specifications_dict=None, **specifications):
        """Set stream conditions with support for value, unit and basis configuration.
        Uses dynamic specification discovery and supports setting value, unit and basis simultaneously.

        :param stream_name: String. Name of the stream to set conditions
        :param specifications_dict: Dictionary. Specifications as {spec_name: config} format
        :param specifications: Keyword arguments for stream specifications
        :return: None

        Configuration formats:
        1. Simple value: spec_name = value
        2. Value with unit: spec_name = {'value': value, 'unit': unit_index}
        3. Value with basis: spec_name = {'value': value, 'basis': basis_string}
        4. Complete config: spec_name = {'value': value, 'unit': unit_index, 'basis': basis_string}

        Examples:
            # Method 1: Simple values
            Set_StreamInputConditions('FEED', TEMP=25, PRES=1.01325)

            # Method 2: With units (unit_index from UnitList)
            Set_StreamInputConditions('FEED',
                                    TEMP={'value': 25, 'unit': 22},  # 22 for Celsius
                                    PRES={'value': 1.01325, 'unit': 2})  # 2 for bar

            # Method 3: With basis (for flow specifications)
            Set_StreamInputConditions('FEED',
                                    TOTFLOW={'value': 100, 'unit': 3, 'basis': 'MASS'},
                                    **{'FLOW\\MIXED\\WATER': {'value': 0.5, 'unit': 3, 'basis': 'MASS-FRAC'}})

            # Method 4: Using dictionary
            specs = {
                'TEMP\\MIXED': {'value': 25, 'unit': 22},
                'PRES\\MIXED': {'value': 1.01325, 'unit': 2},
                'TOTFLOW': {'value': 100, 'unit': 3, 'basis': 'MASS'},
                'FLOW\\MIXED\\WATER': {'value': 0.5, 'unit': 3, 'basis': 'MASS-FRAC'}
            }
            Set_StreamInputConditions('FEED', specifications_dict=specs)
        """
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'!!!")

        stream_name = stream_name.upper()

        if stream_name not in self.StreamsNameList():
            raise UDE.AspenPlus_StreamTypeError(f"Cannot find stream {stream_name} in the AspenFile!")

        # Merge all input methods
        all_specs = {}
        if specifications_dict:
            all_specs.update(specifications_dict)
        all_specs.update(specifications)

        if not all_specs:
            print(f"No specifications provided for {stream_name}")
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

        def _get_basis_path(spec_path, stream_node):
            """Get the appropriate basis path for a specification."""
            # Handle specific basis paths
            if 'TOTFLOW' in spec_path.upper():
                return stream_node.Elements("FLOWBASE").Elements("MIXED")
            elif 'FLOW\\MIXED\\' in spec_path.upper():
                return stream_node.Elements("BASIS").Elements("MIXED")
            else:
                # Other specs may not have basis
                return None

        def _set_element_with_config(element, config, basis_element=None):
            """Set element value with optional unit and basis."""
            value = config['value']
            unit = config['unit']
            basis = config['basis']

            if value is None:
                print(f"Warning: No value provided for element")
                return False

            try:
                if basis is not None and basis_element is not None:
                    # Set basis variable
                    basis_element.Value = basis

                    if unit is not None:
                        # Use SetValueUnitAndBASIS method
                        element.SetValueUnitAndBASIS(value, unit, basis)
                    else:
                        # Set value and basis with default unit
                        element.SetValueUnitAndBASIS(value, element.AttributeValue(3) or 1, basis)
                elif unit is not None:
                    # Use SetValueAndUnit method (no basis)
                    element.SetValueAndUnit(value, unit)
                else:
                    # Only set value
                    element.Value = value

                return True

            except Exception as e:
                print(f"Error setting element: {str(e)}")
                return False

        try:
            stream_node = self.aspen.Tree.FindNode(rf"\Data\Streams\{stream_name}\Input")
            stream_type = None
            for s in self.StreamsList():
                if s[0] == stream_name:
                    stream_type = s[1]
                    break

            print(f"\nSetting specifications for stream {stream_name} ({stream_type}):")
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
                    basis_element = None

                    # Handle paths (e.g., TEMP\MIXED, FLOW\MIXED\WATER)
                    if '\\' in spec_name_upper:
                        path_parts = spec_name_upper.split('\\')
                        current_node = stream_node

                        # Navigate to target node
                        for part in path_parts[:-1]:
                            current_node = current_node.Elements(part)

                        # Final element
                        final_element = path_parts[-1]
                        target_element = current_node.Elements(final_element)

                    else:
                        # Simple spec name - try auto-adding \MIXED path
                        simple_specs = ['TEMP', 'PRES', 'TOTFLOW', 'MASSFLMX', 'VOLFLMX']
                        if spec_name_upper in simple_specs:
                            target_element = stream_node.Elements(spec_name_upper).Elements("MIXED")
                        else:
                            # Direct spec (if exists)
                            try:
                                target_element = stream_node.Elements(spec_name_upper)
                            except:
                                print(f"  Warning: {spec_name} not found")
                                failed_sets += 1
                                continue

                    # If basis is needed, find basis element
                    if config['basis'] is not None:
                        try:
                            basis_element = _get_basis_path(spec_name_upper, stream_node)
                            if basis_element is None:
                                print(f"  Warning: No BASIS element found for {spec_name}")
                        except Exception as e:
                            print(f"  Warning: Could not find BASIS element for {spec_name}: {str(e)}")

                    # Set value
                    if target_element is not None:
                        success = _set_element_with_config(target_element, config, basis_element)

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
                            if config['basis'] is not None:
                                display_parts.append(f"basis={config['basis']}")

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
                print(f"- Use Get_StreamInputConditionsList('{stream_name}') to see available specifications")
                print(f"- Use UnitList() to find correct unit indices")
                print(f"- Common basis values: 'MASS', 'MOLE', 'VOLUME', 'MASS-FRAC', 'MOLE-FRAC'")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to set stream conditions for {stream_name}: {str(e)}")

    def Get_StreamOutputConditionsList(self, stream_name, table=False):
        """Get all available output conditions for a specific stream.
        
        Note: Output data is only available after running the simulation.
        Recursive traversal is used to find all HAP_OUTVAR=18 elements.
        """
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'!!!")

        stream_name = stream_name.upper()

        if stream_name not in self.StreamsNameList():
            raise UDE.AspenPlus_StreamTypeError(f"Cannot find stream {stream_name} in the AspenFile!")

        def _is_output_variable(element):
            """Check if element is an output variable (HAP_OUTVAR = 18)."""
            try:
                outvar = element.AttributeValue(18)  # HAP_OUTVAR = 18
                return outvar == 1
            except:
                return False

        def _get_element_options(element):
            """Get options list for element if available."""
            options = []
            try:
                # Option List (AttributeValue 5 is option list)
                option_list = element.AttributeValue(5).Elements
                if option_list:
                    for i in range(option_list.Count):
                        options.append(option_list(i).Value)
            except:
                element_name = element.Name.upper()
                if element_name == 'FLOW':
                    options = ['MASS-FLOW', 'MOLE-FLOW', 'STDVOL-FLOW', 'MASS-FRAC', 'MOLE-FRAC', 'STDVOL-FRAC',
                               'MASS-CONC', 'MOLE-CONC']
            return options

        def _get_element_value_and_unit(element):
            """Get current value and unit for an element if available."""
            value_info = {}
            try:
                # Value
                try:
                    current_value = element.Value
                    if current_value is not None:
                        value_info['value'] = current_value
                    else:
                        value_info['value'] = None
                except:
                    value_info['value'] = None

                # Unit
                try:
                    # AttributeValue(2) is usually physical quantity (PQ)
                    # AttributeValue(3) is usually unit index (UM)
                    pq = element.AttributeValue(2)
                    um = element.AttributeValue(3)
                    if pq and um:
                        unit_name = self.UnitList([pq, um], table=True)
                        value_info['unit'] = unit_name
                    else:
                        value_info['unit'] = None
                except:
                    value_info['unit'] = None

                # Options
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

                        # Only process output variables (HAP_OUTVAR = 18)
                        if not _is_output_variable(element):
                            # Recursively process child nodes
                            try:
                                if hasattr(element, 'Elements') and element.Elements.Count > 0:
                                    _traverse_elements(element, current_path, specifications)
                            except:
                                pass
                            continue

                        # Description
                        try:
                            description = element.AttributeValue(19)  # HAP_PROMPT = 19
                            if not description:
                                description = f"Output for {element_name}"
                        except:
                            description = f"Output for {element_name}"

                        # Value and Unit
                        value_info = _get_element_value_and_unit(element)

                        specifications[current_path] = {
                            'description': description,
                            'value': value_info['value'],
                            'unit': value_info['unit'],
                            'options': value_info['options']
                        }

                        # recurse into sub-elements
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
            # Check if Output node exists
            try:
                stream_node = self.aspen.Tree.FindNode(rf"\Data\Streams\{stream_name}\Output")
            except:
                # If Output node doesn't exist
                if not table:
                    print(f"No output data available for stream {stream_name}")
                    print("Note: Output data is only available after running the simulation")
                return {} if table else None

            stream_type = None
            # Need to access self.aspen if self.StreamsList() references it, 
            # or use self.StreamsList() directly if it handles the call.
            # Assuming self.StreamsList() works as defined in this mixin/class.
            for s in self.StreamsList():
                if s[0] == stream_name:
                    stream_type = s[1]
                    break

            # Recursive traversal
            specifications = _traverse_elements(stream_node)

            if not table:
                print(f"\nAvailable OUTPUT conditions for stream {stream_name} ({stream_type}):")
                print("=" * 105)
                print(f"{'Output Path':<40}{'Value':<15}{'Unit':<15}{'Description'}")
                print("-" * 105)

                if not specifications:
                    print("No output data available. Run simulation first to generate results.")
                    return

                for spec_path, spec_info in specifications.items():
                    value_str = str(spec_info['value']) if spec_info['value'] is not None else "N/A"
                    unit_str = spec_info['unit'] if spec_info['unit'] else "N/A"

                    # Truncate long strings
                    path_display = spec_path[:39] if len(spec_path) <= 39 else spec_path[:36] + "..."
                    value_display = value_str[:14] if len(value_str) <= 14 else value_str[:11] + "..."
                    unit_display = unit_str[:14] if len(unit_str) <= 14 else unit_str[:11] + "..."

                    # Show options if available
                    if spec_info['options']:
                        print(
                            f"{path_display:<40}{value_display:<15}{unit_display:<15}{spec_info['description']}  {'Options: ' + ', '.join(spec_info['options'])}")
                    else:
                        print(
                            f"{path_display:<40}{value_display:<15}{unit_display:<15}{spec_info['description']}")

                print(f"\nTotal OUTPUT conditions available: {len(specifications)}")

                # Simple stats
                valued_specs = sum(1 for spec in specifications.values() if spec['value'] is not None)
                option_specs = sum(1 for spec in specifications.values() if spec['options'])

                print(f"Statistics: {valued_specs} with values, {option_specs} with options")

            else:
                return specifications

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get output conditions for {stream_name}: {str(e)}")
