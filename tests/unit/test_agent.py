import pytest
from google.adk.tools import google_search
from src.agent import root_agent

@pytest.fixture
def expected_agent_config():
    return {
        "name": "search_assistant",
        "model": "gemini-2.5-flash",
        "instruction": "You are a helpful assistant. Answer user questions using Google Search when needed.",
        "description": "An assistant that can search the web.",
        "tools": [google_search]
    }

def test_agent_initialization(expected_agent_config):
    assert root_agent.name == expected_agent_config["name"]
    assert root_agent.model == expected_agent_config["model"]
    assert root_agent.instruction == expected_agent_config["instruction"]
    assert root_agent.description == expected_agent_config["description"]
    assert root_agent.tools == expected_agent_config["tools"]