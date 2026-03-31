
import os
import sys

# Ensure the aspen_mcp root is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming this script is running from the 'test' directory or root
# Try to find the root directory of the project (d:\AspenPlusMCP)
project_root = r"d:\AspenPlusMCP"
if project_root not in sys.path:
    sys.path.append(project_root)

from aspen_core import AP

def test_ipa_convergence():
    aspen = AP()
    
    # Path from the user's uploaded image
    file_path = r"D:\AspenPlusMCP_paper\CaseStudies\IPA_2\IPA_3col_conv.bkp"
    
    print(f"Testing with file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    try:
        # Connect and Load
        print("Connecting to Aspen Plus...")
        aspen.AspenConnect()
        print(f"Loading {file_path}...")
        aspen.LoadFile(file_path)

        print("\n" + "="*80)
        print("TEST 1: Reinit()")
        print("="*80)
        reinit_result = aspen.Reinit()
        print(f"Result: {reinit_result}")

        print("\n" + "="*80)
        print("TEST 2: Get_ModelStatusSummary()")
        print("="*80)
        summary = aspen.Get_ModelStatusSummary()
        print(f"Summary: {summary}")

        print("\n" + "="*80)
        print("TEST 3: CheckAndRun()")
        print("="*80)
        # This checks model and runs if ready. 
        # Based on previous run, it might report NOT_READY.
        check_run_result = aspen.CheckAndRun()
        print(f"Result: {check_run_result}")

        print("\n" + "="*80)
        print("TEST 4: RunAndReport()")
        print("="*80)
        # This interprets 'Run' and 'Check_ModelCompletionStatus'
        # It forces a run.
        run_report_result = aspen.RunAndReport(detailed_report=True, wait_for_completion=True)
        print(f"Result Status: {run_report_result.get('status')}")
        print(f"Result Message: {run_report_result.get('message')}")

        print("\n" + "="*80)
        print("TEST 5: Get_IncompleteItems()")
        print("="*80)
        
        print("\n--- Items with Errors (Blocks) ---")
        block_errors = aspen.Get_IncompleteItems(category='blocks', issue_type='has_errors')
        import json
        print(json.dumps(block_errors, indent=2))

        print("\n--- Items Needing Attention (Streams) ---")
        stream_attention = aspen.Get_IncompleteItems(category='streams', issue_type='needs_attention')
        print(json.dumps(stream_attention, indent=2))
        
        print("\n" + "="*80)
        print("TEST 6: Check_ModelCompletionStatus(table=True)")
        print("="*80)
        full_status = aspen.Check_ModelCompletionStatus(table=True)
        # Just check the summary part
        print(f"Full Status Summary: {full_status.get('summary')}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        # aspen.CloseAspenConnection()
        print("\nAll tests completed.")

if __name__ == "__main__":
    test_ipa_convergence()
