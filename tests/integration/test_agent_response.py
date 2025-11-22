import os
from dotenv import load_dotenv
os.environ["ADK_EVALUATION_TIMEOUT_SECONDS"] = "180"
# Load environment variables from .env file

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import pytest

@pytest.mark.asyncio
async def test_with_single_test_file():
    """Test the agent's basic ability via a session file."""
    
    await AgentEvaluator.evaluate(
        agent_module="repo_navigator",
        eval_dataset_file_path_or_dir="tests/integration/integration_evalset.json",print_detailed_results=True,
        
    )