import os
from dotenv import load_dotenv
os.environ["ADK_EVALUATION_TIMEOUT_SECONDS"] = "180"
# Load environment variables from .env file

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import pytest
import asyncio
from .retry import retry_async


@pytest.mark.asyncio
async def test_with_multi_turn():
    """Test the agent's basic ability via a session file.

    Uses `retry_async` to retry transient network/timeout errors with
    exponential backoff and logging. Only a narrow set of exceptions are
    retried to avoid masking real test failures.
    """

    await retry_async(
        AgentEvaluator.evaluate,
        agent_module="repo_navigator",
        eval_dataset_file_path_or_dir="tests/integration/test_files/multi_turn/multiturn_test.json",
        print_detailed_results=True,
        num_runs=1,
        attempts=3,
        exceptions=(OSError, ConnectionError, asyncio.TimeoutError, TimeoutError),
    )