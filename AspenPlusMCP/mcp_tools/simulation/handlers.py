import time
import asyncio
from typing import Dict, Any, List
from mcp.types import TextContent
from ..base import BaseHandler

class SimulationHandlers(BaseHandler):
    async def _check_model_completion_status(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check the model completeness status"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to start the file first."
            )]

        show_complete = args.get("show_complete", False)

        try:
            import asyncio

            async def quick_check():
                return self.aspen_instance.Check_ModelCompletionStatus(table=True)

            status_data = await asyncio.wait_for(quick_check(), timeout=30.0)
            summary = status_data.get('summary', {})

            result = "Model Completion Status Check (Quick Mode):\n"
            result += "=" * 50 + "\n"
            result += f"Needs Attention (Incomplete): {summary.get('needs_attention', 0)}\n"
            result += f"Has Errors: {summary.get('has_errors', 0)}\n"
            result += f"Has Warnings: {summary.get('has_warnings', 0)}\n"
            result += f"Complete & Successful: {summary.get('complete_success', 0)}\n"
            result += f"Complete (No Result): {summary.get('complete_no_results', 0)}\n"
            result += f"Disabled / Not Run: {summary.get('disabled_or_not_run', 0)}\n"
            result += f"Inaccessible: {summary.get('inaccessible', 0)}\n"
            result += f"Incompatible: {summary.get('incompatible', 0)}\n"
            result += f"Unknown: {summary.get('unknown', 0)}\n"

            total_items = sum(summary.values())
            total_issues = summary.get('needs_attention', 0) + summary.get('has_errors', 0)

            result += "\nSummary:\n"
            result += f"   Total Items Checked: {total_items}\n"
            result += f"   Critical Issues: {total_issues}\n"

            if total_issues == 0:
                result += "\nModel is complete and ready to run!"
            else:
                result += f"\n{total_issues} critical issues must be resolved before simulation."
                result += "\nUse get_incomplete_items to view detailed issues."

            if show_complete and total_issues <= 20:
                result += "\n\nFewer issues found. Attempting detailed check..."
                try:
                    async def detailed_check():
                        import io
                        import contextlib
                        f = io.StringIO()
                        with contextlib.redirect_stdout(f):
                            self.aspen_instance.Check_ModelCompletionStatus(show_complete=True)
                        return f.getvalue()

                    detailed_output = await asyncio.wait_for(detailed_check(), timeout=60.0)
                    if detailed_output.strip():
                        result += "\n\n" + "=" * 60 + "\n"
                        result += "Detailed Check Output:\n"
                        result += "=" * 60 + "\n"
                        result += detailed_output
                except asyncio.TimeoutError:
                    result += "\nDetailed check timed out. Use get_incomplete_items instead."
                except Exception as e:
                    result += f"\nDetailed check failed: {str(e)}"

            return [TextContent(type="text", text=result)]

        except asyncio.TimeoutError:
            # Fallback if quick check also times out
            result = "Timeout occurred during completeness check. Providing basic status info:\n"
            result += "=" * 50 + "\n"
            try:
                blocks = self.aspen_instance.BlocksNameList()
                streams = self.aspen_instance.StreamsNameList()
                components = self.aspen_instance.ComponentsList()

                result += "Basic Model Info:\n"
                result += f"   Number of Blocks: {len(blocks)}\n"
                result += f"   Number of Streams: {len(streams)}\n"
                result += f"   Number of Components: {len(components)}\n"

                try:
                    run_status = self.aspen_instance.RunStatus()
                    result += f"   Run Status: {run_status}\n"
                except:
                    result += f"   Run Status: Unknown (possibly not run yet)\n"

                result += "\nRecommendations:\n"
                result += "1. For complex models, checking may take longer.\n"
                result += "2. Use get_incomplete_items to check issues in categories.\n"
                result += "3. Try running the model directly with run_simulation.\n"
                result += "4. Test on smaller models if needed."

            except Exception as basic_error:
                result += f"Basic fallback check also failed: {str(basic_error)}\n"
                result += "Please verify Aspen Plus connection status."

            return [TextContent(type="text", text=result)]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Model completion status check failed: {str(e)}\n\n"
                     f"Possible Causes:\n"
                     f"1. Model is too complex and the check timed out.\n"
                     f"2. Aspen Plus connection issues.\n"
                     f"3. Insufficient memory.\n\n"
                     f"Suggested Alternatives:\n"
                     f"1. Use get_incomplete_items to examine by category.\n"
                     f"2. Try run_simulation to test the model directly.\n"
                     f"3. Inspect blocks and streams with get_blocks_list or get_streams_list."
            )]

    async def _get_incomplete_items(self, args: Dict[str, Any]) -> List[TextContent]:
        """Get list of incomplete model items by category and issue type"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to launch it first."
            )]

        category = args.get("category", None)
        issue_type = args.get("issue_type", "needs_attention")

        try:
            incomplete_items = self.aspen_instance.Get_IncompleteItems(category=category, issue_type=issue_type)

            if not incomplete_items:
                category_text = f"'{category}' " if category else ""
                return [TextContent(
                    type="text",
                    text=f"No {category_text}items found with issue type '{issue_type}'."
                )]

            result = f"Incomplete Items List - Type: {issue_type}\n"
            if category:
                result += f"Category: {category}\n"
            result += "=" * 60 + "\n"

            total_items = 0
            for cat_name, cat_items in incomplete_items.items():
                if cat_items:
                    result += f"\n{cat_name.upper()} ({len(cat_items)} items):\n"
                    result += "-" * 40 + "\n"
                    for item_path, item_info in cat_items.items():
                        total_items += 1
                        msg_text = f" -> {item_info['messages']}" if item_info.get('messages') else ""
                        result += f"{total_items:2d}. {item_path}\n"
                        result += f"    Description: {item_info.get('description', 'N/A')}\n"
                        result += f"    Type: {item_info.get('type', 'N/A')}\n"
                        result += f"    Status: {item_info.get('status_summary', 'N/A')}{msg_text}\n"
                        result += "\n"

            result += f"Total incomplete items: {total_items}\n"

            if issue_type == "needs_attention":
                result += "\nRecommendations:\n"
                result += "1. Use get_stream_input_conditions_list to inspect stream input specs\n"
                result += "2. Use get_block_input_specifications to inspect unit input specs\n"
                result += "3. Set the missing required inputs\n"
                result += "4. Run check_model_completion_status again for verification\n"

            return [TextContent(
                type="text",
                text=result
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Failed to retrieve incomplete items list: {str(e)}"
            )]

    async def _reinitialize(self, args: Dict[str, Any]) -> List[TextContent]:
        """Reinitialize the Aspen Plus simulation engine"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus first."
            )]

        try:
            result = self.aspen_instance.Reinit()
            return [TextContent(
                type="text",
                text=f"Status: {result['status']}\n{result['message']}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Reinitialization failed: {str(e)}")]

    async def _run_simulation(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run Aspen Plus simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to start the file."
            )]

        wait_for_completion = args.get("wait_for_completion", True)
        timeout = args.get("timeout", 300)

        try:
            # Run the simulation
            run_result = self.aspen_instance.Run(wait_for_completion=wait_for_completion, timeout=timeout)

            # Construct result message
            result = "Aspen Plus Simulation Result:\n"
            result += "=" * 40 + "\n"
            result += f"Status: {run_result['status']}\n"
            result += f"Message: {run_result['message']}\n"

            if 'run_time' in run_result:
                result += f"Run Time: {run_result['run_time']:.1f} seconds\n"

            if 'pre_run_issues' in run_result:
                result += f"Issues Before Run: {run_result['pre_run_issues']}\n"

            if 'post_run_errors' in run_result:
                result += f"Errors After Run: {run_result['post_run_errors']}\n"

            if 'post_run_warnings' in run_result:
                result += f"Warnings After Run: {run_result['post_run_warnings']}\n"

            if 'post_run_success' in run_result:
                result += f"Successful Items: {run_result['post_run_success']}\n"

            # Provide recommendations based on run status
            status = run_result.get('status', '')
            if status == 'Available':
                result += "\nSimulation completed successfully! You can now review the results."
            elif status == 'Warning':
                result += "\nSimulation completed with warnings. Please review the warning messages."
            elif status == 'Error':
                result += "\nSimulation failed with errors. Please review and fix the issues."
                result += "\nUse get_incomplete_items(issue_type='has_errors') to check error details."
            elif status == 'TIMEOUT':
                result += "\nSimulation timed out. Consider increasing the timeout or simplifying the model."
            elif status == 'FAILED':
                result += "\nSimulation failed to start. Please check the model configuration."

            result += "\n\nNEXT STEP: Call skills(category='simulation') then skills(category='simulation', name='TROUBLESHOOTING') for troubleshooting guide."

            return [TextContent(
                type="text",
                text=result
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Simulation run failed: {str(e)}"
            )]

    async def _run_and_report(self, args: Dict[str, Any]) -> List[TextContent]:
        """Run simulation and generate detailed report"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file."
            )]

        detailed_report = args.get("detailed_report", True)
        wait_for_completion = args.get("wait_for_completion", True)
        timeout = args.get("timeout", 300)

        try:
            # Capture stdout from RunAndReport
            import io
            import contextlib

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                run_result = self.aspen_instance.RunAndReport(
                    detailed_report=detailed_report,
                    wait_for_completion=wait_for_completion,
                    timeout=timeout
                )

            output = f.getvalue()

            # Append additional information from run_result
            if run_result:
                output += "\n\nDetailed Simulation Summary:\n"
                output += f"Status: {run_result.get('status', 'Unknown')}\n"
                output += f"Message: {run_result.get('message', 'No message')}\n"

                if 'run_time' in run_result:
                    output += f"Execution Time: {run_result['run_time']:.1f} seconds\n"

                output += "\nNEXT STEP: Call skills(category='simulation') then skills(category='simulation', name='TROUBLESHOOTING') for result TROUBLESHOOTING guide."

            return [TextContent(
                type="text",
                text=output
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Simulation and report generation failed: {str(e)}"
            )]

    async def _check_and_run(self, args: Dict[str, Any]) -> List[TextContent]:
        """Check model integrity and execute simulation"""
        if not self.aspen_instance:
            return [TextContent(
                type="text",
                text="Aspen Plus is not running. Please use open_aspen_plus to open the file."
            )]

        auto_fix_attempt = args.get("auto_fix_attempt", False)

        try:
            # Capture output from CheckAndRun
            import io
            import contextlib

            f = io.StringIO()
            with contextlib.redirect_stdout(f):
                check_result = self.aspen_instance.CheckAndRun(auto_fix_attempt=auto_fix_attempt)

            output = f.getvalue()

            # Append additional information from check_result
            if check_result:
                output += "\n\nCheck and Run Result:\n"
                output += f"Status: {check_result.get('status', 'Unknown')}\n"
                output += f"Message: {check_result.get('message', 'No message')}\n"

                if 'issues' in check_result:
                    issues = check_result['issues']
                    output += f"Issues Needing Attention: {issues.get('needs_attention', 0)}\n"
                    output += f"Number of Errors: {issues.get('has_errors', 0)}\n"

                if 'recommendation' in check_result:
                    output += f"Recommendation: {check_result['recommendation']}\n"

                output += "\nNEXT STEP: Call skills(category='simulation') then skills(category='simulation', name='TROUBLESHOOTING') for troubleshooting guide."

            return [TextContent(
                type="text",
                text=output
            )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Check and run failed: {str(e)}"
            )]
