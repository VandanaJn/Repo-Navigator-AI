import pytest
from repo_navigator.agent import root_agent, INSTRUCTION_ROOT, DESCRIPTION_ROOT
from repo_navigator.sub_agents.architecture_agent import architecture_summarizer_agent

@pytest.fixture
def expected_agent_config():
    return {
        "name": "repo_analysis_master",
        "model": "gemini-2.5-flash-lite",
        "instruction": INSTRUCTION_ROOT,
        "description": DESCRIPTION_ROOT,
        "tools": [],
        "sub_agents": [architecture_summarizer_agent]
    }

def test_agent_initialization(expected_agent_config):
    assert root_agent.name == expected_agent_config["name"]
    assert root_agent.model == expected_agent_config["model"]
    assert root_agent.instruction == expected_agent_config["instruction"]
    assert root_agent.description == expected_agent_config["description"]
    assert root_agent.tools == expected_agent_config["tools"]
    assert root_agent.sub_agents == expected_agent_config["sub_agents"]