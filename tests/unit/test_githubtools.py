import pytest
import time
from unittest.mock import MagicMock, patch
from github import GithubException, RateLimitExceededException

import repo_navigator.tools.githubtools   


# ----------------------------
# safe_get_contents()
# ----------------------------

def test_safe_get_contents_success():
    repo = MagicMock()
    fake_file = MagicMock()
    repo.get_contents.return_value = fake_file

    result = repo_navigator.tools.githubtools.safe_get_contents(repo, "path/file.txt", "main")

    assert result == fake_file
    repo.get_contents.assert_called_once_with("path/file.txt", ref="main")


def test_safe_get_contents_404_returns_none():
    repo = MagicMock()
    repo.get_contents.side_effect = GithubException(status=404, data={})

    result = repo_navigator.tools.githubtools.safe_get_contents(repo, "missing.txt", "main")

    assert result is None


def test_safe_get_contents_rate_limit_retries_and_succeeds():
    repo = MagicMock()
    repo.get_contents.side_effect = [
        RateLimitExceededException(403, "rate"),
        MagicMock()  # success
    ]

    result = repo_navigator.tools.githubtools.safe_get_contents(repo, "foo", "main")
    assert result is not None
    assert repo.get_contents.call_count == 2


def test_safe_get_contents_rate_limit_exhausted():
    repo = MagicMock()
    repo.get_contents.side_effect = RateLimitExceededException(403, "rate")

    result = repo_navigator.tools.githubtools.safe_get_contents(repo, "foo", "main", max_retries=2)

    assert isinstance(result, dict)
    assert "error" in result
    assert repo.get_contents.call_count == 2


# ----------------------------
# get_repo_structure()
# ----------------------------

@patch("repo_navigator.tools.githubtools.client")
def test_get_repo_structure_lists_files(mock_client):
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

    result = repo_navigator.tools.githubtools.get_repo_structure("me", "testrepo")

    assert "a.txt" in result
    assert "sub" in result
    assert result["a.txt"]["type"] == "file"
    assert "b.txt" in result["sub"]


@patch("repo_navigator.tools.githubtools.client")
def test_get_repo_structure_truncated(mock_client):
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

    result = repo_navigator.tools.githubtools.get_repo_structure("me", "repo", max_depth=1)

    # Since max_depth=1, level1 contents should be truncated
    assert result["level1"] ==  {
        "level2": {
            "_truncated": True
        }
    }




# ----------------------------
# read_file_content()
# ----------------------------

@patch("repo_navigator.tools.githubtools.client")
def test_read_file_content_success(mock_client):
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    mock_file = MagicMock()
    mock_file.decoded_content.decode.return_value = "hello world"

    repo.get_contents.return_value = mock_file

    result = repo_navigator.tools.githubtools.read_file_content("me", "repo", "README.md")

    assert result == "hello world"


@patch("repo_navigator.tools.githubtools.client")
def test_read_file_content_404(mock_client):
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    repo.get_contents.side_effect = GithubException(404, {})

    result = repo_navigator.tools.githubtools.read_file_content("me", "repo", "missing.md")
    assert result is None


@patch("repo_navigator.tools.githubtools.client")
def test_read_file_content_rate_limit_retry(mock_client):
    repo = MagicMock()
    mock_client.get_repo.return_value = repo

    mock_file = MagicMock()
    mock_file.decoded_content.decode.return_value = "ok"

    repo.get_contents.side_effect = [
        RateLimitExceededException(403, "rate"),
        mock_file,
    ]

    result = repo_navigator.tools.githubtools.read_file_content("me", "repo", "file.txt")
    assert result == "ok"
