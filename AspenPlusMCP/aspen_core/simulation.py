# -*- coding: utf-8 -*-
"""
Simulation control and model checking for Aspen Plus COM interface.
Handles running simulations, reporting results, and model validation.

Corresponds to: mcp_tools/simulation/
"""

import time
import UserDifineException as UDE


class SimulationMixin:
    """Mixin class for Aspen Plus simulation control and model checking."""

    # ========== Model Checking Methods ==========

    def Check_ModelCompletionStatus(self, table=False, show_complete=False):
        """Scan the entire AspenPlus model to check completion status of all specifications.
        
        Analyzes HAP_COMPSTATUS(12) for all streams, blocks, and other nodes under Data.
        Excludes output variables (HAP_OUTVAR = 1) from the results.

        Optimization: If Data node itself shows complete_no_results or complete_success,
        returns early without detailed scanning.

        :param table: Boolean. If True, return as dictionary; if False, print to console
        :param show_complete: Boolean. If True, also show completed items
        :return: Dictionary with completion status (if table=True)

        HAP_COMPSTATUS bitmask values:
        - 0x00000001: RESULTS_SUCCESS
        - 0x00000002: NO_RESULTS
        - 0x00000004: RESULTS_WARNINGS
        - 0x00000008: RESULTS_INACCESS
        - 0x00000010: RESULTS_INCOMPAT
        - 0x00000020: RESULTS_ERRORS
        - 0x00000040: INPUT_INCOMPLETE
        - 0x00000080: INPUT_COMPLETE
        - 0x00000100: INPUT_INACCESS
        - 0x00000200: INPUT_NEUTRAL
        - 0x00000400: UNRECONCILED
        - 0x00000800: RECONCILED
        - 0x00001000: DISABLED
        - 0x00002000: ENABLED
        - 0x00004000: EOSYNC
        - 0x00008000: EOSYNC_WARNINGS
        - 0x00010000: EOSYNC_ERRORS
        - 0x00040000: EOFAIL
        - 0x00080000: EOERROR
        - 0x00100000: EOSYNC_UNSYNC
        - 0x00200000: EODISABLE (also adds NOT_RUN)
        """
        if type(table) != bool:
            raise TypeError("table must be a 'Boolean' value.")
        if type(show_complete) != bool:
            raise TypeError("show_complete must be a 'Boolean' value.")

        def _interpret_status(status_code):
            """Decode HAP_COMPSTATUS bitmask."""
            if status_code is None:
                return ["UNKNOWN"]

            COMPSTATUS_FLAGS = {
                0x00000001: "RESULTS_SUCCESS",
                0x00000002: "NO_RESULTS",
                0x00000004: "RESULTS_WARNINGS",
                0x00000008: "RESULTS_INACCESS",
                0x00000010: "RESULTS_INCOMPAT",
                0x00000020: "RESULTS_ERRORS",
                0x00000040: "INPUT_INCOMPLETE",
                0x00000080: "INPUT_COMPLETE",
                0x00000100: "INPUT_INACCESS",
                0x00000200: "INPUT_NEUTRAL",
                0x00000400: "UNRECONCILED",
                0x00000800: "RECONCILED",
                0x00001000: "DISABLED",
                0x00002000: "ENABLED",
                0x00004000: "EOSYNC",
                0x00008000: "EOSYNC_WARNINGS",
                0x00010000: "EOSYNC_ERRORS",
                0x00040000: "EOFAIL",
                0x00080000: "EOERROR",
                0x00100000: "EOSYNC_UNSYNC",
                0x00200000: "EODISABLE",
            }

            status = [label for bit, label in COMPSTATUS_FLAGS.items() if status_code & bit]
            if 0x00200000 & status_code:
                status.append("NOT_RUN")

            return status if status else ["NO_STATUS"]

        def _get_completion_status(element):
            """Get completion status of an element."""
            try:
                status_code = element.AttributeValue(12)  # HAP_COMPSTATUS = 12
                return status_code, _interpret_status(status_code)
            except:
                return None, ["UNKNOWN"]

        def _get_element_description(element):
            """Get description of an element."""
            try:
                description = element.AttributeValue(19)  # HAP_PROMPT = 19
                if not description:
                    description = f"Element: {element.Name}"
            except:
                description = f"Element: {element.Name}"
            return description

        def _categorize_status(status_list):
            """Categorize status based on flags with correct priority."""
            if "RESULTS_ERRORS" in status_list or "EOERROR" in status_list or "EOFAIL" in status_list:
                return "has_errors"
            elif "INPUT_INCOMPLETE" in status_list:
                return "needs_attention"
            elif "INPUT_COMPLETE" in status_list and "RESULTS_SUCCESS" in status_list:
                return "complete_success"
            elif "INPUT_COMPLETE" in status_list:
                return "complete_no_results"
            elif "RESULTS_WARNINGS" in status_list or "EOSYNC_WARNINGS" in status_list:
                return "has_warnings"
            elif "EODISABLE" in status_list or "NOT_RUN" in status_list or "DISABLED" in status_list:
                return "disabled_or_not_run"
            elif "NO_RESULTS" in status_list:
                return "no_results"
            elif "RESULTS_INACCESS" in status_list or "INPUT_INACCESS" in status_list:
                return "inaccessible"
            elif "RESULTS_INCOMPAT" in status_list:
                return "incompatible"
            else:
                return "unknown"

        def _get_status_messages(element):
            """Get specific status messages from Output node if State > 0."""
            messages = []
            try:
                # Try to access Output node
                try:
                    output_node = element.Elements("Output")
                except:
                    return ""

                # Check Property Status (PROPSTATE)
                try:
                    prop_state = output_node.Elements("PROPSTAT").Value
                    if prop_state and int(prop_state) > 0:  # 1=Error, 2=Warning
                        msg = output_node.Elements("PROPMSG").Value
                        if msg:
                            messages.append(f"[PROPMSG]: {msg}")
                except:
                    pass

                # Check Block Status (BLKSTATE)
                try:
                    blk_state = output_node.Elements("BLKSTAT").Value
                    if blk_state and int(blk_state) > 0:  # 1=Error, 2=Warning
                        msg = output_node.Elements("BLKMSG").Value
                        if msg:
                            messages.append(f"[BLKMSG]: {msg}")
                except:
                    pass

            except:
                pass

            return " | ".join(messages)

        def _create_early_exit_result(data_status_category, data_status_list):
            """Create a simplified result when Data node is already complete."""
            categories = ['needs_attention', 'has_errors', 'has_warnings', 'complete_success',
                          'complete_no_results', 'no_results', 'disabled_or_not_run',
                          'inaccessible', 'incompatible', 'unknown']
            return {
                'streams': {cat: {} for cat in categories},
                'blocks': {cat: {} for cat in categories},
                'other_nodes': {cat: {} for cat in categories},
                'summary': {cat: (1 if cat == data_status_category else 0) for cat in categories},
                'early_exit': True,
                'data_status': data_status_category,
                'data_status_flags': data_status_list
            }

        def _traverse_elements(node, path="", specifications=None):
            """Recursively traverse all elements and sub-elements."""
            if specifications is None:
                specifications = {}

            try:
                for element in node.Elements:
                    try:
                        element_name = element.Name
                        current_path = f"{path}\\{element_name}" if path else element_name

                        # Skip output variables (HAP_OUTVAR = 18)
                        try:
                            outvar = element.AttributeValue(18)
                            if outvar == 1:
                                continue
                        except:
                            pass


                        # Get status
                        status_code, status_list = _get_completion_status(element)
                        category = _categorize_status(status_list)

                        # Get potential error messages
                        messages = ""
                        if category in ['has_errors', 'has_warnings']:
                            messages = _get_status_messages(element)

                        # Get description
                        description = _get_element_description(element)

                        # Get element type
                        try:
                            element_type = element.AttributeValue(0) or "Unknown"
                        except:
                            element_type = "Unknown"

                        # Store info
                        specifications[current_path] = {
                            'type': str(element_type)[:14],
                            'status_code': status_code,
                            'status_flags': status_list,
                            'status_summary': ', '.join(status_list)[:89],
                            'description': description[:50] if description else "",
                            'messages': messages,
                            'category': category
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
            # Check Data node status first
            data_node = self.aspen.Tree.FindNode(r"\Data")
            data_status_code, data_status_list = _get_completion_status(data_node)
            data_status_category = _categorize_status(data_status_list)

            print(f"Checking Data node status: {', '.join(data_status_list)}")
            print(f"Data status category: {data_status_category}")

            # Early exit if complete
            if data_status_category in ['complete_no_results', 'complete_success']:
                print(f"Early exit: Data node shows {data_status_category}")
                result = _create_early_exit_result(data_status_category, data_status_list)

                if table:
                    return result
                else:
                    print(f"\nModel Completion Status Summary (Early Exit):")
                    print(f"Data Node Status: {data_status_category.upper()}")
                    print(f"Model appears to be properly configured!")
                    return None

            # Detailed scanning
            print(f"Data node not complete ({data_status_category}), performing detailed scan...")

            categories = ['needs_attention', 'has_errors', 'has_warnings', 'complete_success',
                          'complete_no_results', 'no_results', 'disabled_or_not_run',
                          'inaccessible', 'incompatible', 'unknown']

            all_results = {
                'streams': {cat: {} for cat in categories},
                'blocks': {cat: {} for cat in categories},
                'other_nodes': {cat: {} for cat in categories},
                'summary': {},
                'early_exit': False
            }

            # Scan Streams
            print("Checking Streams...")
            try:
                streams_node = data_node.Elements("Streams")
                stream_results = _traverse_elements(streams_node, "Streams")
                for path, info in stream_results.items():
                    category = info['category']
                    all_results['streams'][category][path] = info
            except Exception as e:
                print(f"Note: Could not scan Streams - {str(e)}")

            # Scan Blocks
            print("Checking Blocks...")
            try:
                blocks_node = data_node.Elements("Blocks")
                block_results = _traverse_elements(blocks_node, "Blocks")
                for path, info in block_results.items():
                    category = info['category']
                    all_results['blocks'][category][path] = info
            except Exception as e:
                print(f"Note: Could not scan Blocks - {str(e)}")

            # Scan other important nodes
            print("Checking Other Nodes...")
            other_important_nodes = ['Properties', 'Components', 'Flowsheeting Options', 'Setup', 'Convergence']
            for node_name in other_important_nodes:
                try:
                    node = data_node.Elements(node_name)
                    node_results = _traverse_elements(node, node_name)
                    for path, info in node_results.items():
                        category = info['category']
                        all_results['other_nodes'][category][path] = info
                except Exception as e:
                    print(f"Note: Could not scan {node_name} - {str(e)}")

            # Calculate statistics
            stats = {}
            for category in categories:
                count = (len(all_results['streams'][category]) +
                         len(all_results['blocks'][category]) +
                         len(all_results['other_nodes'][category]))
                stats[category] = count

            all_results['summary'] = stats
            total_items = sum(stats.values())

            if not table:
                print(f"\nModel Completion Status Summary:")
                print("=" * 90)
                print(f"Data Node Status: {data_status_category.upper()} ({', '.join(data_status_list)})")
                print(f"Total Items Scanned: {total_items}")
                print(f"Needs Attention: {stats['needs_attention']}")
                print(f"Has Errors: {stats['has_errors']}")
                print(f"Has Warnings: {stats['has_warnings']}")
                print(f"Complete & Successful: {stats['complete_success']}")
                print(f"Complete (No Results Yet): {stats['complete_no_results']}")

                total_issues = stats['needs_attention'] + stats['has_errors']
                if total_issues == 0:
                    print("\nModel appears to be properly configured!")
                else:
                    print(f"\n{total_issues} critical items need attention")

                # Show items needing attention
                if stats['needs_attention'] > 0:
                    print(f"\nITEMS NEEDING ATTENTION ({stats['needs_attention']}):")
                    print("-" * 80)
                    item_count = 1
                    for category_name, category_data in all_results.items():
                        if category_name in ['summary', 'early_exit', 'data_status', 'data_status_flags']:
                            continue
                        for path, info in category_data.get('needs_attention', {}).items():
                            msg_text = f" -> {info['messages']}" if info.get('messages') else ""
                            print(f"{item_count}. {path}: {info['description']}{msg_text}")
                            item_count += 1

                # Show errors
                if stats['has_errors'] > 0:
                    print(f"\nITEMS WITH ERRORS ({stats['has_errors']}):")
                    print("-" * 80)
                    item_count = 1
                    for category_name, category_data in all_results.items():
                        if category_name in ['summary', 'early_exit', 'data_status', 'data_status_flags']:
                            continue
                        for path, info in category_data.get('has_errors', {}).items():
                            msg_text = f" -> {info['messages']}" if info.get('messages') else ""
                            print(f"{item_count}. {path}: {info['description']}{msg_text}")
                            item_count += 1

                # Show warnings
                if stats['has_warnings'] > 0:
                    print(f"\nITEMS WITH WARNINGS ({stats['has_warnings']}):")
                    print("-" * 80)
                    item_count = 1
                    for category_name, category_data in all_results.items():
                        if category_name in ['summary', 'early_exit', 'data_status', 'data_status_flags']:
                            continue
                        for path, info in category_data.get('has_warnings', {}).items():
                            msg_text = f" -> {info['messages']}" if info.get('messages') else ""
                            print(f"{item_count}. {path}: {info['description']}{msg_text}")
                            item_count += 1

                return None
            else:
                return all_results

        except Exception as e:
            raise UDE.AspenPlus_FileStatusError(f"Failed to check model completion status: {str(e)}")

    def Get_IncompleteItems(self, category=None, issue_type='needs_attention'):
        """Get items with specific issues from the model.

        :param category: String. Filter by category ('streams', 'blocks', 'other_nodes').
        :param issue_type: String. Type of issues to return.
        :return: Dictionary with items matching the criteria
        """
        if category is not None and type(category) != str:
            raise TypeError("category must be a 'String' or None.")
        if type(issue_type) != str:
            raise TypeError("issue_type must be a 'String'.")

        if category is not None:
            category = category.lower()
            valid_categories = ['streams', 'blocks', 'other_nodes']
            if category not in valid_categories:
                raise ValueError(f"category must be one of {valid_categories}")

        # Get full status report
        full_status = self.Check_ModelCompletionStatus(table=True)

        # Extract specified type items
        filtered_items = {}

        if category is None:
            for cat_name, cat_data in full_status.items():
                if isinstance(cat_data, dict) and cat_name not in ['summary', 'early_exit', 'data_status']:
                    if issue_type in cat_data and cat_data[issue_type]:
                        filtered_items[cat_name] = cat_data[issue_type]
        else:
            if category in full_status and issue_type in full_status[category]:
                filtered_items[category] = full_status[category][issue_type]

        return filtered_items

    def Get_ModelStatusSummary(self):
        """Get a quick summary of the model status.

        :return: Dictionary with summary statistics only
        """
        full_status = self.Check_ModelCompletionStatus(table=True)
        return full_status.get('summary', {
            'needs_attention': 0,
            'has_errors': 0,
            'has_warnings': 0,
            'complete_success': 0,
            'complete_no_results': 0
        })

    # ========== Simulation Methods ==========

    def Reinit(self):
        """Reinitialize the Aspen Plus simulation engine."""
        try:
            self.aspen.Engine.Reinit(4)
            return {
                'status': 'SUCCESS',
                'message': 'Simulation engine reinitialized successfully'
            }
        except Exception as e:
            return {
                'status': 'FAILED',
                'message': f'Failed to reinitialize: {str(e)}'
            }

    def Run(self, wait_for_completion=True, timeout=300):
        """Run the AspenPlus simulation and return status message.

        :param wait_for_completion: Boolean. If True, wait for simulation to complete before returning
        :param timeout: Integer. Maximum time to wait in seconds (default 300s = 5 minutes)
        :return: Dictionary with run status and message
        """
        if type(wait_for_completion) != bool:
            raise TypeError("wait_for_completion must be a 'Boolean' value.")
        if type(timeout) != int:
            raise TypeError("timeout must be an 'Integer' value.")

        try:
            print("Starting AspenPlus simulation...")

            # Check pre-run status
            pre_run_status = self.Get_ModelStatusSummary()
            critical_issues = pre_run_status['needs_attention'] + pre_run_status['has_errors']

            if critical_issues > 0:
                print(f"Warning: {critical_issues} critical issues detected before run")

            # Start run
            start_time = time.time()
            self.aspen.Engine.Run2()

            if not wait_for_completion:
                return {
                    'status': 'STARTED',
                    'message': 'Simulation started successfully (not waiting for completion)',
                    'run_time': 0,
                    'pre_run_issues': critical_issues
                }

            # Wait for completion
            print("Waiting for simulation to complete...")
            elapsed_time = 0

            while elapsed_time < timeout:
                time.sleep(2)
                elapsed_time = time.time() - start_time

                try:
                    engine_status = self.aspen.Engine.IsRunning
                    if not engine_status:
                        break

                    if int(elapsed_time) % 30 == 0:
                        print(f"Still running... ({int(elapsed_time)}s elapsed)")
                except:
                    break

            total_time = time.time() - start_time

            # Check timeout
            if elapsed_time >= timeout:
                return {
                    'status': 'TIMEOUT',
                    'message': f'Simulation timed out after {timeout} seconds',
                    'run_time': total_time,
                    'pre_run_issues': critical_issues
                }

            # Check run result
            try:
                run_status = self.RunStatus()

                result = {
                    'status': run_status,
                    'run_time': total_time,
                    'pre_run_issues': critical_issues
                }

                if run_status == 'Available':
                    result['message'] = f'Simulation completed successfully in {total_time:.1f}s'
                elif run_status == 'Warning':
                    result['message'] = f'Simulation completed with warnings in {total_time:.1f}s'
                elif run_status == 'Error':
                    result['message'] = f'Simulation completed with errors in {total_time:.1f}s'

                print(result['message'])
                return result

            except Exception as e:
                return {
                    'status': 'UNKNOWN',
                    'message': f'Simulation finished but status check failed: {str(e)}',
                    'run_time': total_time,
                    'pre_run_issues': critical_issues
                }

        except Exception as e:
            return {
                'status': 'FAILED',
                'message': f'Failed to start simulation: {str(e)}',
                'run_time': 0,
                'pre_run_issues': critical_issues if 'critical_issues' in locals() else 0
            }

    def RunAndReport(self, detailed_report=True, wait_for_completion=True, timeout=300):
        """Run simulation and provide detailed status report.

        :param detailed_report: Boolean. If True, show detailed completion status after run
        :param wait_for_completion: Boolean. If True, wait for simulation to complete
        :param timeout: Integer. Maximum time to wait in seconds
        :return: Dictionary with comprehensive run results
        """
        print("=" * 80)
        print("ASPENPLUS SIMULATION RUN")
        print("=" * 80)

        # Pre-run check
        print("\n1. PRE-RUN STATUS CHECK:")
        print("-" * 40)
        pre_status = self.Get_ModelStatusSummary()

        if pre_status['needs_attention'] > 0:
            print(f"Input Issues: {pre_status['needs_attention']}")
        if pre_status['has_errors'] > 0:
            print(f"Existing Errors: {pre_status['has_errors']}")

        # Run simulation
        print("\n2. RUNNING SIMULATION:")
        print("-" * 40)
        run_result = self.Run(wait_for_completion=wait_for_completion, timeout=timeout)

        # Post-run check
        if wait_for_completion and run_result['status'] in ['Available', 'Warning', 'Error']:
            print("\n3. POST-RUN STATUS:")
            print("-" * 40)

            if detailed_report:
                print("Detailed completion status:")
                self.Check_ModelCompletionStatus(show_complete=False)
            else:
                post_status = self.Get_ModelStatusSummary()
                print(f"Successful: {post_status['complete_success']}")
                print(f"Warnings: {post_status['has_warnings']}")
                print(f"Errors: {post_status['has_errors']}")

        # Summary
        print("\n4. SUMMARY:")
        print("-" * 40)
        print(f"Run Status: {run_result['status']}")
        print(f"Message: {run_result['message']}")
        if 'run_time' in run_result:
            print(f"Run Time: {run_result['run_time']:.1f} seconds")

        print("=" * 80)
        return run_result

    def CheckAndRun(self, auto_fix_attempt=False):
        """Check model status and run if ready, with optional auto-fix attempt.

        :param auto_fix_attempt: Boolean. If True, attempt basic fixes before running
        :return: Dictionary with check and run results
        """
        print("CHECKING MODEL READINESS...")
        print("=" * 50)

        # Check model status
        status = self.Get_ModelStatusSummary()
        ready_to_run = status['needs_attention'] == 0 and status['has_errors'] == 0

        print(f"Critical Issues: {status['needs_attention'] + status['has_errors']}")

        if ready_to_run:
            print("[OK] Model appears ready to run!")
            return self.RunAndReport()
        else:
            print("[!] Model has issues that need attention:")
            self.Check_ModelCompletionStatus(show_complete=False)

            if auto_fix_attempt:
                print("\n[FIX] ATTEMPTING BASIC AUTO-FIX...")
                print("(This feature would require implementation of specific fix strategies)")

            print("\n[INFO] Please resolve issues before running simulation")

            return {
                'status': 'NOT_READY',
                'message': 'Model has critical issues that prevent running',
                'issues': {
                    'needs_attention': status['needs_attention'],
                    'has_errors': status['has_errors']
                },
                'recommendation': 'Use Check_ModelCompletionStatus() for detailed issue list'
            }
