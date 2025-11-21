import pytest
from repo_navigator.sub_agents.architecture_agent import architecture_summarizer_agent, INSTRUCTION_ARCHITECTURE, DESCRIPTION_ARCHITECTURE
from repo_navigator.sub_agents.file_summarizer_agent import file_architecture_summarizer_agent
from repo_navigator.sub_agents.tools.githubtools import get_repo_structure

@pytest.fixture
def expected_agent_config():
    return {
        "name": "Code_Architecture_Agent",
        "model": "gemini-2.5-flash-lite",
        "instruction": INSTRUCTION_ARCHITECTURE,
        "description": DESCRIPTION_ARCHITECTURE,
        "tools": [get_repo_structure],
        "sub_agents": [file_architecture_summarizer_agent]
    }

def test_agent_initialization(expected_agent_config):
    assert architecture_summarizer_agent.name == expected_agent_config["name"]
    assert architecture_summarizer_agent.model == expected_agent_config["model"]
    assert architecture_summarizer_agent.instruction == expected_agent_config["instruction"]
    assert architecture_summarizer_agent.description == expected_agent_config["description"]
    assert architecture_summarizer_agent.tools == expected_agent_config["tools"]
    assert architecture_summarizer_agent.sub_agents == expected_agent_config["sub_agents"]