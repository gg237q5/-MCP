# -*- coding: utf-8 -*-
"""
Block operations for Aspen Plus COM interface.
Handles block creation, listing, specifications, and connections.
"""

import UserDifineException as UDE


class BlocksMixin:
    """Mixin class for Aspen Plus block operations."""

    def BlocksList(self) -> list:
        """Get the block-list in AspenFile with 'List Type'.

        :return: List. a list with [all block name, block type] in AspenFile.
        """
        HAP_RECODERTYPE = 6
        a_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements:
            a_list.append([e.Name, e.AttributeValue(HAP_RECODERTYPE)])
        return a_list

    def BlocksNameList(self) -> list:
        """Get only the block names in AspenFile.

        :return: List. a list with all block names in AspenFile.
        """
        name_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements:
            name_list.append(e.Name)
        return name_list

    def BlockPortList(self, bname) -> list:
        """Get the ports for the block with 'List Type'.

        :param bname: block name in 'Str-Type'.
        :return: List. a list with [all ports name, it's description] in AspenFile.
        """
        HAP_PROMPT = 19
        a_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).Elements("Ports").Elements:
            a_list.append([e.Name, e.AttributeValue(HAP_PROMPT)])
        return a_list

    def BlockPortNameList(self, bname) -> list:
        """Get the port names for the block with 'List Type'.

        :param bname: block name in 'Str-Type'.
        :return: List. a list with all port names in AspenFile.
        """
        a_list = []
        for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).Elements("Ports").Elements:
            a_list.append(e.Name)
        return a_list

    def BlockType(self, bname) -> str:
        """Get the block type of the bname in string.

        :param bname: Block name in AspenFile.
        :return: String. a string in block type for specified block.
        """
        if type(bname) is not str:
            raise TypeError("bname must be a 'String'!!!")

        bname = bname.upper()

        if bname not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError("Cannot Find " + bname
                                               + " in the AspenFile. "
                                               + "Please Check the name you type!!")

        return self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).AttributeValue(6)

    def Add_Block(self, block_name, block_type):
        """Add a block to AspenPlus model.

        :param block_name: String. Name of the block to be added
        :param block_type: String. Type of the block (e.g., 'RADFRAC', 'RStoic', 'Heater', 'Flash2', etc.)
        :return: COM object of the added block
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'.")
        if type(block_type) != str:
            raise TypeError("block_type must be a 'String'.")

        block_name = block_name.upper()
        block_type = block_type.upper()

        if block_name in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError(f"Block {block_name} already exists in the AspenFile!")

        try:
            blocks = self.aspen.Tree.FindNode(r"\Data\Blocks")
            new_block = blocks.Elements.Add(f"{block_name}!{block_type}")
            print(f"Successfully added {block_type} block: {block_name}")
            return new_block
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to add block: {str(e)}")

    def Connect_Block2Stream(self, block_name, stream_name, port_type):
        """Connect a stream to a block at specified port.

        :param block_name: String. Name of the block
        :param stream_name: String. Name of the stream to connect
        :param port_type: String. Port type (e.g., 'F(IN)', 'VD(OUT)', 'B(OUT)', 'P(OUT)', etc.)
        :return: None
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'.")
        if type(stream_name) != str:
            raise TypeError("stream_name must be a 'String'.")
        if type(port_type) != str:
            raise TypeError("port_type must be a 'String'.")

        block_name = block_name.upper()
        stream_name = stream_name.upper()
        port_type = port_type.upper()

        if block_name not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError(f"Cannot find block {block_name} in the AspenFile!")
        if stream_name not in self.StreamsNameList():
            raise UDE.AspenPlus_StreamTypeError(f"Cannot find stream {stream_name} in the AspenFile!")

        try:
            block = self.aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}")
            block.Elements("Ports").Elements(port_type).Elements.Add(stream_name)
            print(f"Successfully connected stream {stream_name} to block {block_name} at port {port_type}")
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to connect stream to block: {str(e)}")

    def Connections(self, bname, table=False):
        """Show the connected stream of the desired block.

        :param bname: block name in 'Str-Type'.
        :param table: a boolen value. default is False for print the result on the screen.
        """
        if type(bname) is not str:
            raise TypeError("bname must be a 'String'.")
        if type(table) is not bool:
            raise TypeError("table must be a 'Boolean' value.")

        bname = bname.upper()

        if bname not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError("Cannot Find " + bname
                                               + " in the AspenFile. "
                                               + "Please Check the name you type!!")

        if not table:
            print("{0[0]:13s}{0[1]:13s}".format(["Stream_Name", "Streams_Type"]))
            print("==========================")
            for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).Elements(
                    "Connections").Elements:
                streamtype = self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).Elements(
                    "Connections").Elements(e.Name).Value
                print("{0:13s}{1:13s}".format(e.Name, streamtype))
        elif table:
            a_list = []
            for e in self.aspen.Tree.Elements("Data").Elements("Blocks").Elements(bname).Elements(
                    "Connections").Elements:
                a_list.append(e.Name)
            return a_list

    def Remove_Block(self, block_name, force=False):
        """Remove a block from AspenPlus model.

        :param block_name: String. Name of the block to be removed
        :param force: Boolean. If True, remove even if streams are connected
        :return: Dictionary with removal status and message
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'!!!")
        if type(force) != bool:
            raise TypeError("force must be a 'Boolean' value.")

        block_name = block_name.upper()

        if block_name not in self.BlocksNameList():
            return {
                'status': 'NOT_FOUND',
                'message': f"Block {block_name} not found in the AspenFile!"
            }

        try:
            connected_streams = []
            try:
                connected_streams = self.Connections(block_name, table=True)
            except:
                pass

            if connected_streams and not force:
                return {
                    'status': 'CONNECTED',
                    'message': f"Block {block_name} has connected streams: {', '.join(connected_streams)}. Use force=True to remove anyway.",
                    'connected_streams': connected_streams
                }

            if force and connected_streams:
                print(f"Forcing removal: {block_name} has {len(connected_streams)} connected streams")

            blocks_node = self.aspen.Tree.FindNode(r"\Data\Blocks")
            blocks_node.Elements.Remove(block_name)

            print(f"Successfully removed block: {block_name}")
            return {
                'status': 'SUCCESS',
                'message': f"Block {block_name} removed successfully",
                'had_connected_streams': connected_streams if connected_streams else []
            }

        except Exception as e:
            return {
                'status': 'ERROR',
                'message': f"Failed to remove block {block_name}: {str(e)}"
            }

    # Note: Get_BlockInputSpecificationsList and Set_BlockInputSpecifications are complex methods
    # They are included in the full implementation. For brevity, we reference the patterns from AP.py
    # The full implementation should copy these methods from lines 1375-1941 of AP.py

    def Get_BlockInputSpecificationsList(self, block_name, table=False):
        """Get all available specifications for a specific block.
        Includes unit_category (HAP_UNITROW) for each specification to enable unit_list queries.
        
        :param block_name: String. Name of the block to get specifications
        :param table: Boolean. If True, return as dictionary; if False, print to console
        :return: Dictionary with specification names, descriptions, values, units, and unit_category (if table=True)
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'!!!")
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")

        block_name = block_name.upper()

        if block_name not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError(f"Cannot find block {block_name} in the AspenFile!")

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
            block_node = self.aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}\Input")
            specifications = _traverse_elements(block_node)
            
            if table:
                return specifications
            else:
                print(f"\nSpecifications for block {block_name}:")
                for name, info in specifications.items():
                    unit_cat = f" [unit_category={info['unit_category']}]" if info['unit_category'] else ""
                    print(f"  {name}: {info['description']}{unit_cat}")
                    
        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get specifications for {block_name}: {str(e)}")

    def Set_BlockInputSpecifications(self, block_name, specifications_dict=None, **specifications):
        """Set block specifications with support for value, unit and basis configuration.
        Uses dynamic specification discovery and supports setting value, unit and basis simultaneously.

        :param block_name: String. Name of the block to set specifications
        :param specifications_dict: Dictionary. Specifications as {spec_name: config} format
        :param specifications: Keyword arguments for block specifications
        :return: None

        Configuration formats:
        1. Simple value: spec_name = value
        2. Value with unit: spec_name = {'value': value, 'unit': unit_index}
        3. Value with basis: spec_name = {'value': value, 'basis': basis_string}
        4. Complete config: spec_name = {'value': value, 'unit': unit_index, 'basis': basis_string}

        Examples:
            # Method 1: Simple values
            Set_BlockInputSpecifications('COL1', NSTAGE=20, BASIS_RR=2.0)

            # Method 2: With units
            Set_BlockInputSpecifications('HEATER1',
                                        TEMP={'value': 100, 'unit': 22})

            # Method 3: With basis (for RADFRAC)
            Set_BlockInputSpecifications('COL1',
                                        BASIS_D={'value': 50, 'unit': 3, 'basis': 'MASS'})

            # Method 4: Using dictionary
            specs = {'NSTAGE': 20, 'BASIS_RR': 2.0, 'FEED_STAGE\\FEED': 10}
            Set_BlockInputSpecifications('COL1', specifications_dict=specs)
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'!!!")

        block_name = block_name.upper()

        if block_name not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError(f"Cannot find block {block_name} in the AspenFile!")

        # Merge all input methods
        all_specs = {}
        if specifications_dict:
            all_specs.update(specifications_dict)
        all_specs.update(specifications)

        if not all_specs:
            print(f"No specifications provided for {block_name}")
            return

        def _normalize_config(spec_name, config):
            """Normalize configuration to standard format."""
            if isinstance(config, (int, float)):
                return {'value': config, 'unit': None, 'basis': None}
            elif isinstance(config, dict):
                return {
                    'value': config.get('value'),
                    'unit': config.get('unit'),
                    'basis': config.get('basis')
                }
            else:
                return {'value': config, 'unit': None, 'basis': None}

        def _get_basis_element_name(spec_name):
            """Get the basis element name for a specification."""
            spec_upper = spec_name.upper()

            # RADFRAC specific mappings
            basis_mappings = {
                'BASIS_D': 'D_BASIS',
                'BASIS_B': 'B_BASIS',
                'BASIS_RR': 'RR_BASIS',
                'BASIS_BR': 'BR_BASIS',
                'BASIS_L1': 'L1_BASIS',
                'BASIS_VN': 'VN_BASIS',
                'D:F': 'D:F_BASIS',
                'B:F': 'B:F_BASIS',
            }

            # Check exact match
            if spec_upper in basis_mappings:
                return basis_mappings[spec_upper]

            # Check if contains specific string
            for key, basis_name in basis_mappings.items():
                if key in spec_upper:
                    return basis_name

            # Try common BASIS patterns
            if spec_upper.startswith('BASIS_'):
                base_name = spec_upper.replace('BASIS_', '')
                return f"{base_name}_BASIS"
            elif ':F' in spec_upper:
                return f"{spec_upper}_BASIS"
            elif spec_upper.endswith('_RATE') or spec_upper.endswith('_FLOW'):
                return f"{spec_upper}_BASIS"

            # No BASIS
            return None

        def _set_element_with_config(element, config, basis_element=None, spec_name=""):
            """Set element value with optional unit and basis."""
            value = config['value']
            unit = config['unit']
            basis = config['basis']

            if value is None:
                print(f"Warning: No value provided for {spec_name}")
                return False

            try:
                if basis is not None and basis_element is not None:
                    # Set basis variable
                    basis_element.Value = basis
                    print(f"   -> Set BASIS for {spec_name}: {basis}")

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
                print(f"   Error setting {spec_name}: {str(e)}")
                return False

        try:
            block_node = self.aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}\Input")
            block_type = self.BlockType(block_name)

            print(f"\nSetting specifications for {block_name} ({block_type}):")
            print("-" * 70)

            successful_sets = 0
            failed_sets = 0

            for spec_name, raw_config in all_specs.items():
                try:
                    config = _normalize_config(spec_name, raw_config)
                    spec_name_upper = spec_name.upper()

                    target_element = None
                    basis_element = None

                    # Handle paths (e.g., FEED_STAGE\FEED, B:F)
                    if '\\' in spec_name_upper:
                        path_parts = spec_name_upper.split('\\')
                        current_node = block_node

                        for part in path_parts[:-1]:
                            current_node = current_node.Elements(part)

                        final_element = path_parts[-1]
                        target_element = current_node.Elements(final_element)

                    else:
                        try:
                            target_element = block_node.Elements(spec_name_upper)
                        except:
                            print(f"  Warning: {spec_name} not found in {block_name}")
                            failed_sets += 1
                            continue

                    # If basis is needed, find basis element
                    if config['basis'] is not None:
                        try:
                            basis_element_name = _get_basis_element_name(spec_name)
                            if basis_element_name:
                                basis_element = block_node.Elements(basis_element_name)
                                print(f"   -> Found BASIS element: {basis_element_name}")
                            else:
                                print(f"   Warning: No BASIS element pattern found for {spec_name}")
                        except Exception as e:
                            print(f"   Warning: Could not find BASIS element for {spec_name}: {str(e)}")
                            # Try common patterns
                            try:
                                basis_element = block_node.Elements(f"{spec_name_upper}_BASIS")
                                print(f"   -> Found BASIS element using pattern: {spec_name_upper}_BASIS")
                            except:
                                try:
                                    if spec_name_upper.startswith('BASIS_'):
                                        alt_basis_name = spec_name_upper.replace('BASIS_', '') + '_BASIS'
                                        basis_element = block_node.Elements(alt_basis_name)
                                        print(f"   -> Found BASIS element using alt pattern: {alt_basis_name}")
                                except:
                                    basis_element = None

                    # Set value
                    if target_element is not None:
                        success = _set_element_with_config(target_element, config, basis_element, spec_name)

                        if success:
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
                print(f"- Use Get_BlockInputSpecificationsList('{block_name}') to see available specifications")
                print(f"- Use UnitList() to find correct unit indices")
                print(f"- Common basis values for RADFRAC: 'MASS', 'MOLE', 'VOLUME'")
                print(f"- BASIS elements are automatically detected for supported specifications")

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to set block specifications for {block_name}: {str(e)}")

    def Get_BlockOutputSpecificationsList(self, block_name, table=False):
        """Get all available output specifications for a specific block.
        
        Note: Output data is only available after running the simulation.
        Recursive traversal is used to find all HAP_OUTVAR=18 elements.
        """
        if type(block_name) != str:
            raise TypeError("block_name must be a 'String'!!!")
        
        block_name = block_name.upper()
        
        if block_name not in self.BlocksNameList():
            raise UDE.AspenPlus_BlockTypeError(f"Cannot find block {block_name} in the AspenFile!")

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
                # Option List
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
                block_node = self.aspen.Tree.FindNode(rf"\Data\Blocks\{block_name}\Output")
            except:
                # If Output node doesn't exist
                if not table:
                    print(f"No output data available for block {block_name}")
                    print("Note: Output data is only available after running the simulation")
                return {} if table else None

            block_type = self.BlockType(block_name)

            # Recursive traversal
            specifications = _traverse_elements(block_node)

            if not table:
                print(f"\nAvailable OUTPUT specifications for {block_name} ({block_type}):")
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

                print(f"\nTotal OUTPUT specifications available: {len(specifications)}")

                # Simple stats
                valued_specs = sum(1 for spec in specifications.values() if spec['value'] is not None)
                option_specs = sum(1 for spec in specifications.values() if spec['options'])

                print(f"Statistics: {valued_specs} with values, {option_specs} with options")

            else:
                return specifications

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to get output specifications for {block_name}: {str(e)}")
