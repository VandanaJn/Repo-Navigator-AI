import pytest
from repo_navigator.sub_agents.file_summarizer_agent import file_architecture_summarizer_agent, INSTRUCTION_FILE_SUMMARIZER, DESCRIPTION_FILE_SUMMARIZER
from repo_navigator.sub_agents.tools.githubtools import read_file_content

@pytest.fixture
def expected_agent_config():
    return {
        "name": "Code_Summarizer_for_architecture",
        "model": "gemini-2.5-flash-lite",
        "instruction": INSTRUCTION_FILE_SUMMARIZER,
        "description": DESCRIPTION_FILE_SUMMARIZER,
        "tools": [read_file_content],
        "sub_agents": []
    }

def test_agent_initialization(expected_agent_config):
    assert file_architecture_summarizer_agent.name == expected_agent_config["name"]
    assert file_architecture_summarizer_agent.model == expected_agent_config["model"]
    assert file_architecture_summarizer_agent.instruction == expected_agent_config["instruction"]
    assert file_architecture_summarizer_agent.description == expected_agent_config["description"]
    assert file_architecture_summarizer_agent.tools == expected_agent_config["tools"]
    assert file_architecture_summarizer_agent.sub_agents == expected_agent_config["sub_agents"]