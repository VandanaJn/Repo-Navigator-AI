import pytest
from src.githubtools import get_repo_structure, read_file_content
from src.agent import root_agent, SYSTEM_INSTRUCTION

@pytest.fixture
def expected_agent_config():
    return {
        "name": "Repo_Navigator",
        "model": "gemini-2.5-flash-lite",
        "instruction": SYSTEM_INSTRUCTION,
        "description": "An assistant that can navigate a repo and answer question about it.",
        "tools": [get_repo_structure, read_file_content]
    }

def test_agent_initialization(expected_agent_config):
    assert root_agent.name == expected_agent_config["name"]
    assert root_agent.model == expected_agent_config["model"]
    assert root_agent.instruction == expected_agent_config["instruction"]
    assert root_agent.description == expected_agent_config["description"]
    assert root_agent.tools == expected_agent_config["tools"]