from mcp.types import Tool

check_model_completion_status = Tool(
    name="check_model_completion_status",
    description="""[Simulation] Comprehensively check the model completion status in Aspen Plus.

Features:
- Scans the entire model, including streams, blocks, and other elements
- Identifies items that require attention (e.g., incomplete inputs, errors, warnings)
- Provides detailed statistical summary and problem localization
- Focuses only on user input issues, excluding output variables

When to use:
- After building the model, before running the simulation
- For diagnosing run failures
- After modifying the model
- For periodic health checks of the model

Status Categories:
- Needs Attention: Items with missing or incomplete input (highest priority)
- Has Errors: Elements with runtime or configuration errors
- Has Warnings: Elements with warnings but still runnable
- Complete & Success: Properly configured and executed elements
- Other States: Disabled, inaccessible, incompatible, etc.

Recommended Workflow:
1. Run this tool after model construction
2. Fix all items that need attention or have errors
3. Use get_incomplete_items to get a detailed issue list
4. Re-check the model after making fixes
5. If no critical issues remain, proceed to run the simulation
""",
    inputSchema={
        "type": "object",
        "properties": {
            "show_complete": {
                "type": "boolean",
                "description": "Whether to include completed and successful items in the output (default: False)",
                "default": False
            }
        },
        "required": []
    }
)

get_incomplete_items = Tool(
    name="get_incomplete_items",
    description="""[Simulation] Retrieve a detailed list of items with specific issue types.

Functionality:
- Filter specific types of issues from the model integrity check results
- Provide full path, description, and status details
- Help users target and fix specific problems efficiently

Use Cases:
- After checking the model, focus on resolving specific issue types
- After a failed simulation run, examine specific error items
- Track progress while fixing problems one by one

Supported Issue Types:
- needs_attention: Items with incomplete inputs (**most critical**)
- has_errors: Items with errors
- has_warnings: Items with warnings
- complete_success: Items that are complete and valid (for confirmation)

Category Filters:
- streams: Show only stream-related issues
- blocks: Show only block-related issues
- other_nodes: Show other node issues
- If no category is specified, all types will be returned

Recommended Workflow:
1. Use `check_model_completion_status` to understand overall status
2. Use this tool to retrieve the list of `needs_attention` items
3. Fix those issues one by one
4. Then check for `has_errors` items
5. Finally, confirm the overall model completion status
""",
    inputSchema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "enum": ["streams", "blocks", "other_nodes"],
                "description": "Category to filter (optional; if not specified, returns all)"
            },
            "issue_type": {
                "type": "string",
                "enum": [
                    "needs_attention", "has_errors", "has_warnings", "complete_success",
                    "complete_no_results", "no_results", "disabled_or_not_run", "inaccessible",
                    "incompatible", "unknown"
                ],
                "description": "Type of issue to retrieve",
                "default": "needs_attention"
            }
        },
        "required": []
    }
)

reinitialize = Tool(
    name="reinitialize",
    description="""[Simulation] Reinitialize the Aspen Plus simulation engine.

Use this to reset engine state and clear previous results before a fresh run.
Note: This is also called internally by run_simulation.
""",
    inputSchema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

run_simulation = Tool(
    name="run_simulation",
    description="""[Simulation] Execute Aspen Plus simulation.

⚠️ For detailed simulation guide:
   skills(category='simulation', name='RUN')

Mandatory Preconditions:
- Before running, use `check_model_completion_status` to verify model readiness.
- The response from `check_model_completion_status` **must include 'COMPLETE'** before executing `run_and_report`.

Functionality:
- Start Aspen Plus simulation
- Monitor simulation status and progress
- Provide run results and statistics
- Compare issues before and after the simulation

Run Options:
- wait_for_completion: Whether to wait until the simulation finishes (recommended: True)
- timeout: Maximum wait time in seconds (default: 300 seconds = 5 minutes)

Run Status Possibilities:
- Available: Simulation completed successfully, results available
- Warning: Completed with warnings
- Error: Completed with errors
- Timeout: Simulation timed out
- Failed: Simulation failed

Recommended Workflow:
1. Use `check_model_completion_status` to validate model before running
2. Ensure the response includes 'COMPLETE'
3. Execute this simulation tool
4. After running, check model status again for results
5. If problems exist, use `get_incomplete_items` to analyze in detail

Notes:
- Ensure model inputs are complete before running
- It is recommended to activate `suppress_dialogs` to avoid interruptions
- Complex models may take longer—adjust `timeout` accordingly
- If simulation fails, inspect error messages and model status
""",
    inputSchema={
        "type": "object",
        "properties": {
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for the simulation to complete before returning (recommended: True)",
                "default": True
            },
            "timeout": {
                "type": "integer",
                "description": "Maximum wait time in seconds (default is 300 seconds = 5 minutes)",
                "default": 300
            }
        },
        "required": []
    }
)

run_and_report = Tool(
    name="run_and_report",
    description="""[Simulation] Run simulation and generate a detailed report.

⚠️ For detailed simulation guide:
   skills(category='simulation', name='RUN')

Mandatory Requirements:
- Before execution, use `check_model_completion_status` to verify model readiness.
- The response from `check_model_completion_status` **must include 'COMPLETE'** to proceed with `run_and_report`.

Functionality:
- Check model status before execution
- Execute Aspen Plus simulation
- Analyze post-run status in detail
- Provide a comprehensive report and actionable suggestions

Report Contents:
1. Pre-run model check
2. Simulation execution details
3. Post-run status analysis
4. Diagnostics and recommendations

Applicable Scenarios:
- When a full execution report is required
- Monitoring of complex model simulations
- Troubleshooting and issue analysis
- Comprehensive evaluation of simulation results

Report Options:
- detailed_report: Whether to include a full model integrity report (recommended: True)
- wait_for_completion: Whether to wait for the simulation to finish before returning (recommended: True)
- timeout: Maximum wait time in seconds (default: 300 seconds)

Difference from `run_simulation`:
- `run_simulation`: Lightweight execution with basic status info
- `run_and_report`: Full execution with detailed diagnostics and suggestions

Recommended Use Cases:
- First-time execution of a newly built model
- When simulations fail and detailed diagnostics are needed
- When full documentation of simulation run is required
- For monitoring and analyzing complex simulation models
""",
    inputSchema={
        "type": "object",
        "properties": {
            "detailed_report": {
                "type": "boolean",
                "description": "Whether to include a detailed model integrity report (recommended: True)",
                "default": True
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for the simulation to complete before returning (recommended: True)",
                "default": True
            },
            "timeout": {
                "type": "integer",
                "description": "Maximum wait time in seconds (default: 300 seconds = 5 minutes)",
                "default": 300
            }
        },
        "required": []
    }
)

check_and_run = Tool(
    name="check_and_run",
    description="""[Simulation] Smart Check and Run: Automatically assess model readiness and decide whether to execute the simulation.

⚠️ For detailed simulation guide:
   skills(category='simulation', name='RUN')

Features:
- Automatically checks model integrity and readiness
- Evaluates whether it is safe to run
- Automatically runs the simulation if the model is ready
- If issues are found, provides detailed diagnostics and suggestions
- Optionally attempts basic auto-repair (experimental)

Intelligent Decision Flow:
1. Check model completion status
2. Evaluate number of critical issues
3. If no critical issues → automatically run
4. If issues are present → report details and suggestions
5. Optional: attempt basic auto-fix (experimental)

Suitable Scenarios:
- One-click model execution
- Automated workflows
- Quick model validation
- Beginner-friendly simulation trigger

Auto-Fix Function (Experimental):
- Currently focuses on diagnostics
- Can be extended in the future with basic fix strategies
- Examples: setting default values, checking connections, etc.

Comparison with Other Run Tools:
- run_simulation: Directly executes the simulation without checking
- run_and_report: Executes and generates a detailed report
- check_and_run: Evaluates then decides to run or not

Recommended Usage:
- When unsure if the model is ready to run
- Safe execution in automated scripts
- Quick verification of model configuration
- Useful for learning and testing phases
""",
    inputSchema={
        "type": "object",
        "properties": {
            "auto_fix_attempt": {
                "type": "boolean",
                "description": "Whether to attempt basic auto-repair (experimental, default: False)",
                "default": False
            }
        },
        "required": []
    }
)

tools = [
    check_model_completion_status,
    get_incomplete_items,
    reinitialize,
    run_simulation,
    run_and_report,
    check_and_run
]
