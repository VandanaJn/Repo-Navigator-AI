import pytest
from repo_navigator.sub_agents.architecture_agent import architecture_summarizer_agent, INSTRUCTION_ARCHITECTURE, DESCRIPTION_ARCHITECTURE
from repo_navigator.sub_agents.file_summarizer_agent import file_architecture_summarizer_agent
from repo_navigator.sub_agents.tools.githubtools import get_repo_structure
from google.adk.tools import AgentTool
@pytest.fixture
def expected_agent_config():
    return {
        "name": "code_architecture_agent",
        "model": "gemini-2.5-pro",
        "instruction": INSTRUCTION_ARCHITECTURE,
        "description": DESCRIPTION_ARCHITECTURE,
        "tools": [get_repo_structure, AgentTool(file_architecture_summarizer_agent)],
        "sub_agents":[]
    }

def test_agent_initialization(expected_agent_config):
    assert architecture_summarizer_agent.name == expected_agent_config["name"]
    assert architecture_summarizer_agent.model == expected_agent_config["model"]
    assert architecture_summarizer_agent.instruction == expected_agent_config["instruction"]
    assert architecture_summarizer_agent.description == expected_agent_config["description"]
    assert architecture_summarizer_agent.tools[0] == expected_agent_config["tools"][0]
    assert architecture_summarizer_agent.tools[1].agent == expected_agent_config["tools"][1].agent
    assert architecture_summarizer_agent.sub_agents == expected_agent_config["sub_agents"]