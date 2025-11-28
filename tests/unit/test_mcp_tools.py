import importlib
import pytest

import repo_navigator.sub_agents.tools.mcp_tools as mcptools


@pytest.fixture(autouse=True)
def clear_env_and_cache(monkeypatch):
    # Ensure TEST_ENV is cleared by default
    monkeypatch.delenv("TEST_ENV", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    mcptools._toolset_cache = {}
    yield
    mcptools._toolset_cache = {}


def test_get_mcp_toolset_returns_none_in_test_env(monkeypatch):
    monkeypatch.setenv("TEST_ENV", "1")

    mcptools._toolset_cache = {}  # clear cache
    result = mcptools.get_mcp_toolset("get_repository_tree")
    assert result is None


def test_get_mcp_toolset_uses_cache():
    fake_toolset = object()
    mcptools._toolset_cache = {
        "get_repository_tree": fake_toolset
    }

    result = mcptools.get_mcp_toolset("get_repository_tree")
    assert result is fake_toolset


def test_get_mcp_toolset_invalid_name(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

    mcptools._toolset_cache = {}  # clear cache
    with pytest.raises(ValueError) as excinfo:
        mcptools.get_mcp_toolset("unknown_tool")
    assert "Unknown tool name" in str(excinfo.value)


def test_get_mcp_toolset_initializes_mcp_toolset(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")

    fake = object()

    def fake_ctor(*args, **kwargs):
        return fake

    # Patch McpToolset where it's used in mcptools
    monkeypatch.setattr(mcptools, "McpToolset", fake_ctor)

    mcptools._toolset_cache = {}  # clear cache
    result = mcptools.get_mcp_toolset("get_file_contents")

    assert result is fake
    # Should also be cached
    assert mcptools._toolset_cache["get_file_contents"] is fake


def test_mcp_globals_none_in_test_env(monkeypatch):
    monkeypatch.setenv("TEST_ENV", "1")
    # Force reload to re-run top-level code
    importlib.reload(mcptools)

    assert mcptools.mcp_tools_get_tree is None
    assert mcptools.mcp_tools_get_content is None

def test_mcp_globals_in_test_env(monkeypatch):
    monkeypatch.setenv("TEST_ENV", "1")
    mcptools._toolset_cache = {}
    import importlib
    importlib.reload(mcptools)

    assert mcptools.mcp_tools_get_tree is None
    assert mcptools.mcp_tools_get_content is None
    







