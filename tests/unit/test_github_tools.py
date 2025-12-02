import pytest
from unittest.mock import MagicMock, patch
from repo_navigator.sub_agents.tools.github_tools import extract_owner_and_repo, get_repo_structure, read_file_content




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

# --------------------------
# get_repo_structure tests
# --------------------------
@patch("repo_navigator.sub_agents.tools.github_tools._get_github_client")
def test_get_repo_structure_mocked(client_mock):
    # Mock client and repo
    mock_repo = MagicMock()
    mock_repo.get_contents.return_value = []
    client_mock.return_value.get_repo.return_value = mock_repo

    result = get_repo_structure("user", "repo")
    assert isinstance(result, dict)

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
