import os
import pytest
from unittest.mock import MagicMock, patch
from github import GithubException

from repo_navigator.sub_agents.tools.github_tools import (
    extract_owner_and_repo,
    get_repo_structure,
    read_file_content, 
    _get_github_client
)

# --------------------------
# extract_owner_and_repo tests
# --------------------------
@pytest.mark.parametrize("url, expected", [
    ("https://github.com/user/repo", {"valid": True, "owner": "user", "repo": "repo"}),
    ("user/repo", {"valid": True, "owner": "user", "repo": "repo"}),
    ("https://github.com/user", {"valid": False, "owner": "user", "repo": None}),
    ("", {"error": {"message": "GitHub URL is empty."}})
])
def test_extract_owner_and_repo(url, expected):
    result = extract_owner_and_repo(url)
    for key in expected:
        assert result[key] == expected[key]

def test_extract_owner_and_repo_netloc_fallback():
    # URL where path is empty but netloc exists → triggers line 62
    url = "https://github.com"

    result = extract_owner_and_repo(url)

    # Expected outcome: error envelope because no owner can be extracted
    assert "error" in result
    assert result["error"]["message"] == "Could not parse owner from URL."

def test_extract_owner_and_repo_exception():
    # Force urlparse to throw inside the function
    with patch("repo_navigator.sub_agents.tools.github_tools.urlparse", side_effect=Exception("boom")):
        resp = extract_owner_and_repo("https://github.com/owner/repo")
        assert resp["error"]["message"] == "Failed to parse GitHub URL."

# --------------------------
# get_repo_structure tests
# --------------------------
@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_get_repo_structure_mocked(client_mock):
    mock_repo = MagicMock()
    mock_repo.get_contents.return_value = []
    client_mock.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo")
    assert isinstance(result, dict)

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_get_repo_structure_module_missing(client_mock):
    mock_repo = MagicMock()
    mock_repo.get_contents.return_value = {"error": "not found"}
    client_mock.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo", module="missing")
    assert "error" in result

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_get_repo_structure_safe_get_contents_error(client_mock):
    mock_repo = MagicMock()
    mock_repo.get_contents.side_effect = [{"error": "failed"}]
    client_mock.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo")
    assert "error" in result

@patch.dict(os.environ, {}, clear=True)
def test_get_repo_structure_no_token():
    result = get_repo_structure("user", "repo")
    assert "error" in result
    assert "GitHub client unavailable" in result["error"]["message"]

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_get_repo_structure_duck_typing_file(client_mock):
    mock_file = MagicMock()
    mock_file.name = "file.txt"
    mock_file.path = "file.txt"
    mock_file.decoded_content = b"hello"
    mock_file.size = 123

    mock_repo = MagicMock()
    mock_repo.get_contents.return_value = mock_file
    client_mock.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo")
    assert "file.txt" in result
    assert result["file.txt"]["type"] == "file"

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
@patch("repo_navigator.sub_agents.tools.github_tools.safe_get_contents")
def test_get_repo_structure_handles_files_and_dirs(mock_safe_get, mock_client):
    """
    Covers the branch where item.type == 'dir' AND the else branch for files.
    """
    # Fake directory item
    dir_item = MagicMock()
    dir_item.type = "dir"
    dir_item.name = "src"
    dir_item.path = "src"

    # Fake file item
    file_item = MagicMock()
    file_item.type = "file"
    file_item.name = "main.py"
    file_item.path = "main.py"
    file_item.size = 123

    # safe_get_contents() called twice:
    # - First call for root returns both directory and file
    # - Second call for walking into "src" returns an empty list
    mock_safe_get.side_effect = [
        [dir_item, file_item],  # first call (root)
        []                      # second call (inside src)
    ]

    # Mock GitHub repo client
    mock_repo = MagicMock()
    mock_client.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo")

    # Validate file was added
    assert "main.py" in result
    assert result["main.py"]["type"] == "file"
    assert result["main.py"]["path"] == "main.py"
    assert result["main.py"]["size"] == 123

    # Validate directory branch recursion executed
    assert "src" in result
    assert result["src"] == {}  # inside src is empty

# --------------------------
# read_file_content tests
# --------------------------
@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_read_file_content_mocked(client_mock):
    mock_file = MagicMock()
    mock_file.decoded_content = b"Hello World"
    mock_repo = MagicMock()
    mock_repo.get_contents.return_value = mock_file
    client_mock.return_value.get_repo.return_value = mock_repo

    result = read_file_content("user", "repo", "file.txt")
    assert "content" in result
    assert result["content"] == "Hello World"

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_read_file_content_rate_limit(client_mock):
    mock_file = MagicMock()
    mock_file.decoded_content = b"Retry Success"

    mock_repo = MagicMock()
    mock_repo.get_contents.side_effect = [Exception("Rate limit"), mock_file]
    client_mock.return_value.get_repo.return_value = mock_repo

    result = read_file_content("user", "repo", "file.txt")
    assert "error" in result
    assert result["error"]["details"]["message"]=="Rate limit"

@patch.dict(os.environ, {}, clear=True)
def test_read_file_content_no_token():
    result = read_file_content("user", "repo", "file.txt")
    assert "error" in result
    assert "GitHub client unavailable" in result["error"]["message"]

@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_read_file_content_github_exception(client_mock):
    mock_repo = MagicMock()
    mock_repo.get_contents.side_effect = GithubException(500, "Server Error", None)
    client_mock.return_value.get_repo.return_value = mock_repo

    result = read_file_content("user", "repo", "file.txt")
    assert "error" in result
    assert "read_file_content: unexpected error" in result["error"]["message"]

def test_get_github_client_initialization_failure():
    # Ensure the token exists so it gets past the "no token" branch
    os.environ["GITHUB_TOKEN"] = "dummy-token"

    # Force Github() constructor to raise an exception
    with patch("repo_navigator.sub_agents.tools.github_tools.Github",
               side_effect=Exception("boom")):
        client = _get_github_client()
        assert client is None  # Should return None when exception is thrown
