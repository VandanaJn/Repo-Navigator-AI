# mcptools.py

import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# Internal cache to hold the initialized toolset instances
_toolset_cache = {}

def get_mcp_toolset(tool_name: str):
    """
    Lazy-loads and caches a specific McpToolset instance.
    """
    if tool_name in _toolset_cache:
        return _toolset_cache[tool_name]
    
    if 'TEST_ENV' in os.environ:
        # DO NOT perform the initialization logic.
        # This prevents the network connection that causes the CancelledError.
        # We raise a simple error to signal that the tool is unavailable, 
        # which will be caught by the calling agent's setup, but the monkeypatch
        # should have already replaced the global variables.
        # However, for robustness, it's safer to let the main logic handle the mock injection.
        
        # For this setup, simply return None here, and rely on the agent definition
        # or the monkeypatch to handle the replacement.
        return None

    load_dotenv()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    try:
        if not GITHUB_TOKEN:
            raise EnvironmentError("GITHUB_TOKEN is not set.")
            
        git_hub_serrver_params = StreamableHTTPServerParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "X-MCP-Toolsets": "all",
                "X-MCP-Readonly": "true",
            },
        )
        
        if tool_name == "get_repository_tree":
            toolset = McpToolset(
                connection_params=git_hub_serrver_params,
                tool_filter=["get_repository_tree"], 
            )
        elif tool_name == "get_file_contents":
            toolset = McpToolset(
                connection_params=git_hub_serrver_params,
                tool_filter=["get_file_contents"], 
            )
        else:
            raise ValueError(f"Unknown tool name requested: {tool_name}")

        # Cache and return the newly created toolset
        _toolset_cache[tool_name] = toolset
        print(f"Real MCP Toolset '{tool_name}' initialized successfully.")
        return toolset

    except Exception as e:
        print(f"Error initializing MCP Toolset '{tool_name}': {e}")
        # Raising the error stops the agent run if a critical tool is missing
        raise e

# The variables now point to the lazy-loaded function call
mcp_tools_get_tree = get_mcp_toolset("get_repository_tree")
mcp_tools_get_content = get_mcp_toolset("get_file_contents")