import json
import os
import shutil
import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator
# Assuming you fixed the RunConfig import as discussed:
# from google.adk.runners import RunConfig 

# IMPORTANT: Ensure your imports point to the correct file path.
from .utils import ALL_EVAL_CASES 
CONFIG_SOURCE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "test_config.json"
)
# --- Pytest Parametrized Test ---

# Update the parametrize decorator to include new fields:
@pytest.mark.parametrize(
    "case_id, query, expected_tool_use, reference, must_not_call, score_threshold, must_include_text", 
    ALL_EVAL_CASES, 
    ids=[case[0] for case in ALL_EVAL_CASES]
)
@pytest.mark.asyncio
async def test_agent_evaluation_case(
    case_id: str, 
    query: str, 
    expected_tool_use: list, 
    reference: str, 
    must_not_call: list, 
    score_threshold: float,
    must_include_text: list
):
    # --- 1. Prepare and Write Temporary JSON File ---
    
    # Data structure for the single case that the ADK evaluator requires
    single_case_data = [{
        "query": query,
        "expected_tool_use": expected_tool_use,
        "reference": reference,
        # Apply custom score threshold for the ADK metric
        "metrics": {"response_match_score": score_threshold} 
    }]
    
    temp_dir = "temp_eval_data"
    temp_file_path = os.path.join(temp_dir, f"{case_id}.json")
    print(temp_file_path)
    
    # Use try...finally to ensure cleanup runs even if evaluation fails
    try:
        # Create directory and write the unique JSON file
        os.makedirs(temp_dir, exist_ok=True)
        # Copy Configuration File 
        config_dest_path = os.path.join(temp_dir, "test_config.json")
        # Use shutil.copy to copy the file from source to the new temp directory
        shutil.copy(CONFIG_SOURCE_PATH, config_dest_path) 
       
        with open(temp_file_path, 'w') as f:
            json.dump(single_case_data, f, indent=2)

        # --- 2. Run Agent Evaluation ---
        results = await AgentEvaluator.evaluate(
            agent_module="repo_navigator",
            # CORRECTED: Passing the required file path argument
            eval_dataset_file_path_or_dir=temp_file_path, 
            print_detailed_results=True 
        )
        
        # # --- 3. Extract Results and Assertions ---
        # # The results object contains a list of evaluation runs; we target the first (and only) one.
        # evaluation_data = results.evaluation_data[0]
        # summary = evaluation_data.overall_summary
        
        # # 4a. Check overall success (Tool trajectory and response match)
        # assert summary.eval_status.name == "PASSED", \
        #     f"Case {case_id} Failed: {summary.reason} \nDetails: {results.to_dict()}"

        # # 4b. Custom assertion for FORBIDDEN tools (must_not_call)
        # if must_not_call:
        #     # actual_tool_calls is retrieved from the evaluation results
        #     actual_tool_calls = [
        #         call.name for call in evaluation_data.actual_tool_calls
        #     ]
            
        #     for forbidden_tool in must_not_call:
        #         assert forbidden_tool not in actual_tool_calls, \
        #             f"Case {case_id} Failed: Forbidden tool '{forbidden_tool}' was called."

        # # 4c. Custom assertion for REQUIRED text (must_include_text)
        # if must_include_text:
        #     # Get the actual final response text
        #     actual_response = evaluation_data.actual_response
            
        #     for required_text in must_include_text:
        #         # Use .lower() for case-insensitive matching
        #         assert required_text.lower() in actual_response.lower(), \
        #             f"Case {case_id} Failed: Required text '{required_text}' not found in response."

    finally:
        # --- 5. Clean up the temporary directory and file ---
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

