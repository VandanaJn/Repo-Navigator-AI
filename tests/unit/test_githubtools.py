import pytest
import time
from unittest.mock import MagicMock, patch
from github import GithubException, RateLimitExceededException

import repo_navigator.sub_agents.tools.githubtools   
from repo_navigator.sub_agents.tools.githubtools import extract_owner_and_repo

# ----------------------------
# safe_get_contents()
# ----------------------------

def test_safe_get_contents_success():
    repo = MagicMock()
    fake_file = MagicMock()
    repo.get_contents.return_value = fake_file

    result = repo_navigator.sub_agents.tools.githubtools.safe_get_contents(repo, "path/file.txt", "main")

    assert result == fake_file
    repo.get_contents.assert_called_once_with("path/file.txt", ref="main")


def test_safe_get_contents_404_returns_none():
    repo = MagicMock()
    repo.get_contents.side_effect = GithubException(status=404, data={})

    result = repo_navigator.sub_agents.tools.githubtools.safe_get_contents(repo, "missing.txt", "main")

    assert "Path 'missing.txt' does not exist in repo" in result['error']
    assert "on ref 'main'" in result['error']


def test_safe_get_contents_rate_limit_retries_and_succeeds():
    repo = MagicMock()
    repo.get_contents.side_effect = [
        RateLimitExceededException(403, "rate"),
        MagicMock()  # success
    ]

    result = repo_navigator.sub_agents.tools.githubtools.safe_get_contents(repo, "foo", "main")
    assert result is not None
    assert repo.get_contents.call_count == 2


def test_safe_get_contents_rate_limit_exhausted():
    repo = MagicMock()
    repo.get_contents.side_effect = RateLimitExceededException(403, "rate")

    result = repo_navigator.sub_agents.tools.githubtools.safe_get_contents(repo, "foo", "main", max_retries=2)

    assert isinstance(result, dict)
    assert "error" in result
    assert repo.get_contents.call_count == 2


# ----------------------------
# get_repo_structure()
# ----------------------------

@patch("repo_navigator.sub_agents.tools.githubtools._get_github_client")
def test_get_repo_structure_lists_files(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    file_item = MagicMock()
    file_item.type = "file"
    file_item.name = "a.txt"
    file_item.path = "a.txt"
    file_item.size = 10

    dir_item = MagicMock()
    dir_item.type = "dir"
    dir_item.name = "sub"
    dir_item.path = "sub"

    sub_file = MagicMock()
    sub_file.type = "file"
    sub_file.name = "b.txt"
    sub_file.path = "sub/b.txt"
    sub_file.size = 20

    repo.get_contents.side_effect = [
        [file_item, dir_item],  # root
        [sub_file],             # /sub
    ]

    result = repo_navigator.sub_agents.tools.githubtools.get_repo_structure("me", "testrepo")

    assert "a.txt" in result
    assert "sub" in result
    assert result["a.txt"]["type"] == "file"
    assert "b.txt" in result["sub"]


@patch("repo_navigator.sub_agents.tools.githubtools._get_github_client")
def test_get_repo_structure_truncated(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    # Depth 0 → depth 1 → depth 2 → MAX (should truncate)
    deep_dir = MagicMock()
    deep_dir.type = "dir"
    deep_dir.name = "level1"
    deep_dir.path = "level1"

    level2_dir = MagicMock()
    level2_dir.type = "dir"
    level2_dir.name = "level2"
    level2_dir.path = "level1/level2"

    repo.get_contents.side_effect = [
        [deep_dir],     # root
        [level2_dir],   # level1/
        [],             # level1/level2
    ]

    result = repo_navigator.sub_agents.tools.githubtools.get_repo_structure("me", "repo", max_depth=2)

    # Since max_depth=1, level1 contents should be truncated
    assert result["level1"] ==  {
        "level2": {
            "_truncated": True
        }
    }




# ----------------------------
# read_file_content()
# ----------------------------

@patch("repo_navigator.sub_agents.tools.githubtools._get_github_client")
def test_read_file_content_success(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    mock_file = MagicMock()
    mock_file.decoded_content.decode.return_value = "hello world"

    repo.get_contents.return_value = mock_file

    result = repo_navigator.sub_agents.tools.githubtools.read_file_content("me", "repo", "README.md")

    assert result == "hello world"


@patch("repo_navigator.sub_agents.tools.githubtools._get_github_client")
def test_read_file_content_404(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    repo.get_contents.side_effect = GithubException(404, {})

    result = repo_navigator.sub_agents.tools.githubtools.read_file_content("me", "repo", "missing.md")
    assert result is None


@patch("repo_navigator.sub_agents.tools.githubtools._get_github_client")
def test_read_file_content_rate_limit_retry(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    mock_file = MagicMock()
    mock_file.decoded_content.decode.return_value = "ok"

    repo.get_contents.side_effect = [
        RateLimitExceededException(403, "rate"),
        mock_file,
    ]

    result = repo_navigator.sub_agents.tools.githubtools.read_file_content("me", "repo", "file.txt")
    assert result == "ok"

@pytest.mark.parametrize("url_input, expected_output", [
    # --- Valid URLs (Full Extraction) ---
    # Full URL to a file
    ("https://github.com/VandanaJn/yt-channel-crawler/blob/main/file.py", {'valid': True, 'owner': 'VandanaJn', 'repo': 'yt-channel-crawler'}),
    # Full URL to the repo root
    ("https://github.com/owner-test/repo-test", {'valid': True, 'owner': 'owner-test', 'repo': 'repo-test'}),
    # URL with trailing slash
    ("https://github.com/OwnerName/RepoName/", {'valid': True, 'owner': 'OwnerName', 'repo': 'RepoName'}),
    # URL with query parameters/fragments
    ("https://github.com/test-org/test-repo?query=1#fragment", {'valid': True, 'owner': 'test-org', 'repo': 'test-repo'}),
    # Short path (assuming the context is github.com)
    ("owner/repo", {'valid': True, 'owner': 'owner', 'repo': 'repo'}),
    # Full domain without scheme (handled by your netloc logic)
    ("github.com/owner/repo", {'valid': True, 'owner': 'owner', 'repo': 'repo'}),
    # Path with branch/commit hash
    ("https://github.com/user/project/tree/main/src", {'valid': True, 'owner': 'user', 'repo': 'project'}),
    # Path with keywords in later segments
    ("https://github.com/user/project/blob/main/issues/file.txt", {'valid': True, 'owner': 'user', 'repo': 'project'}),

    # --- Owner Only (Valid=False) ---
    # Only owner provided
    ("https://github.com/just-owner", {'valid': False, 'owner': 'just-owner', 'repo': None}),
    # Owner followed by a known GitHub keyword (should be treated as owner-only)
    ("https://github.com/owner-only/issues", {'valid': False, 'owner': 'owner-only', 'repo': None}),
    ("https://github.com/owner-only/pulls/123", {'valid': False, 'owner': 'owner-only', 'repo': None}),
    ("https://github.com/owner-only/wiki", {'valid': False, 'owner': 'owner-only', 'repo': None}),
    # Owner followed by an unrecognized keyword (should still pass if not in the list)
    ("https://github.com/owner-only/some-other-word", {'valid': True, 'owner': 'owner-only', 'repo': 'some-other-word'}),
    
    # --- Invalid URLs (Failure Cases) ---
    # Empty string
    ("", {'valid': False, 'owner': None, 'repo': None}),
    # None (should be handled by the initial check)
    (None, {'valid': False, 'owner': None, 'repo': None}),
    # Only the GitHub root
    ("https://github.com/", {'valid': False, 'owner': None, 'repo': None}),
    # Garbage input that might raise an exception
    ("not-a-url-at-all", {'valid': False, 'owner': 'not-a-url-at-all', 'repo': None}), # Note: urlparse might yield this as owner
])
def test_extract_owner_and_repo(url_input, expected_output):
    """
    Tests various valid and invalid GitHub URL formats.
    """
    if url_input is None:
        # Since the function checks `if not github_url`, passing None directly is fine.
        result = extract_owner_and_repo(url_input)
    else:
        result = extract_owner_and_repo(url_input)
        
    assert result == expected_output

def test_exception_handling():
    """
    Tests if the function handles non-string inputs gracefully (e.g., list or integer).
    """
    # This assumes non-string input will likely trigger an exception during string methods or url parsing
    # and should be caught by your general try/except block.
    assert extract_owner_and_repo(12345) == {'valid': False, 'owner': None, 'repo': None}
    assert extract_owner_and_repo([]) == {'valid': False, 'owner': None, 'repo': None}
