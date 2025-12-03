import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import pytest

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import pytest

@pytest.mark.asyncio
async def test_with_single_turn():
    """Test the agent's basic ability via a session file."""
    
    await AgentEvaluator.evaluate(
        agent_module="repo_navigator",
        eval_dataset_file_path_or_dir="tests/integration/test_files/single_turn/single_turn_test.json",
        print_detailed_results=True, 
        
    )