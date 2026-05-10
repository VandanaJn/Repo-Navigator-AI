from dotenv import load_dotenv
load_dotenv()

from google.adk.evaluation.agent_evaluator import AgentEvaluator

import pytest


@pytest.mark.asyncio
async def test_hallucination_model_name():
    """Regression test for the 1.5/2.5 hallucination seen during demo:
    the agent reads `gemini-2.5-pro` from constants.py but used to respond
    with `gemini-1.5-pro` due to training-prior override.
    """

    await AgentEvaluator.evaluate(
        agent_module="repo_navigator",
        eval_dataset_file_path_or_dir="tests/integration/test_files/hallucination/hallucination_test.json",
        print_detailed_results=True,
    )
