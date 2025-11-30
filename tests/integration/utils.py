import os
import json
def load_eval_cases(file_path):
    """Loads all evaluation cases from a single JSON file."""
    
    # Adjust path if your project structure is different
    # Assumes 'tests' is the parent directory for 'utils.py'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, "eval_datasets", file_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Evaluation file not found at: {full_path}")
        
    with open(full_path, 'r') as f:
        data = json.load(f)
    
    # Prepare the data tuple for Pytest parametrization
    return [
        (
            case['case_id'], # NOTE: Changed 'id' to 'case_id' to match your new JSON structure
            case['query'], 
            case.get('expected_tool_use', []), # Use .get for tool_use, as it might be empty
            case.get('reference', ''), 
            case.get('must_not_call', []),
            case.get('score_threshold', 0.6),
            case.get('must_include_text', []) # <--- ADD THIS NEW FIELD
        )
        for case in data
    ]

# Define the dataset to be used for parametrization
ALL_EVAL_CASES = load_eval_cases("all_eval_cases.json")