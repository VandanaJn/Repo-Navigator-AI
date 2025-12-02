# github_tools.py
import os
import time
import re
from urllib.parse import urlparse
from github import Github
from dotenv import load_dotenv
from github import Github, GithubException, RateLimitExceededException

from .utils import logger, error_response, tool_safety

load_dotenv()

# -----------------------------
# GitHub client
# -----------------------------
def _get_github_client():
    """Create a GitHub API client from GITHUB_TOKEN."""
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GITHUB_TOKEN not set.")
        return None
    try:
        return Github(token, timeout=15)
    except Exception as e:
        logger.exception("Failed to initialize GitHub client: %s", e)
        return None


# -----------------------------
# extract_owner_and_repo
# -----------------------------
@tool_safety("extract_owner_and_repo")
def extract_owner_and_repo(github_url: str) -> dict:
    """
    Extract the GitHub repository owner and name from a URL or path.

    This tool parses full GitHub URLs, short paths, and URLs pointing to specific
    files or branches. It ensures only the first two meaningful path segments are
    used as owner and repository name. Known GitHub keywords (e.g., 'issues', 'wiki')
    are ignored when detecting the repository.

    Args:
        github_url (str): GitHub URL or path (e.g., 
                          "https://github.com/user/repo/blob/main/file.py" or 
                          "user/repo").

    Returns:
        dict: A dictionary describing the extraction result:
            - {"valid": True, "owner": <owner>, "repo": <repo>} if both found
            - {"valid": False, "owner": <owner>, "repo": None} if only owner found
            - {"error": {...}} if parsing fails or input is invalid
    """
    if not github_url:
        return error_response("GitHub URL is empty.")

    GITHUB_KEYWORDS = r'^(issues|pulls|wiki|settings|marketplace|orgs|topics|notifications|stars|trending|gists)$'

    try:
        parsed = urlparse(github_url)
        path = parsed.path.strip("/")
        if not path and parsed.netloc:
            path = parsed.netloc.strip("/")

        segments = [s for s in path.split("/") if s]
        if segments and segments[0].lower() == "github.com":
            segments = segments[1:]

        if not segments:
            return error_response("Could not parse owner from URL.")

        owner = segments[0]
        repo = None
        if len(segments) >= 2 and not re.match(GITHUB_KEYWORDS, segments[1], re.IGNORECASE):
            repo = segments[1]

        return {"valid": True, "owner": owner, "repo": repo} if repo else {"valid": False, "owner": owner, "repo": None}
    except Exception as e:
        logger.exception("Error parsing GitHub URL '%s': %s", github_url, e)
        return error_response("Failed to parse GitHub URL.")


            
def safe_get_contents(repo, path, ref, max_retries=3):
    """GitHub get_contents() with retries ONLY for rate-limit conditions."""
    delay = 1

    for attempt in range(max_retries):
        try:
            return repo.get_contents(path, ref=ref)

        # ------------------------------------
        # Retry ONLY RateLimitExceededException
        # ------------------------------------
        except RateLimitExceededException:
            if attempt == max_retries - 1:
                # Final retry failed → return structured error
                return error_response(f"Rate limited while fetching path: {path}")

            print(f"⚠️ GitHub rate-limited {path}. Retrying in {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, 8)  # exponential backoff
            continue

        # ------------------------------------
        # 404 → return clean structured error
        # ------------------------------------
        except GithubException as e:
            if e.status == 404:
                return {
                    "error": (
                        f"Path '{path}' does not exist in repo "
                        f"'{repo.full_name}' on ref '{ref}'."
                    )
                }
            # Non-404 GithubException → no retry, raise immediately
            raise e

        # ------------------------------------
        # Any OTHER exception → no retry
        # ------------------------------------
        except Exception:
            raise

    # We should never reach here, but return a defensive error
    return error_response(f"Failed to fetch path after retries: {path}")




# -----------------------------
# get_repo_structure
# -----------------------------
@tool_safety("get_repo_structure")
def get_repo_structure(owner: str, repo_name: str, branch: str = "main", max_depth: int = 3, module: str | None = None) -> dict:
    """
    Retrieve the directory structure of a GitHub repository.

    Traverses the repository starting at the root or an optional subdirectory (`module`)
    and builds a nested dictionary of folders and files. The depth of recursion is limited
    by `max_depth` to prevent very large outputs.

    Args:
        owner (str): GitHub username or organization.
        repo_name (str): Repository name.
        branch (str, optional): Branch name. Defaults to "main".
        max_depth (int, optional): Maximum folder depth to traverse. Defaults to 3.
        module (str | None, optional): Optional subdirectory to start traversal.

    Returns:
        dict: Nested dictionary representing repository structure:
            - Directories are represented as nested dicts
            - Files are represented as {"type": "file", "path": ..., "size": ...}
            - {"_truncated": True} when max_depth is exceeded
            - {"error": {...}} on failure
    """
    client = _get_github_client()
    if not client:
        return error_response("GitHub client unavailable.")

    repo = client.get_repo(f"{owner}/{repo_name}")
    start_path = module.strip("/") if module else ""

    if module:
        mod = safe_get_contents(repo, start_path, branch)
        if isinstance(mod, dict) and "error" in mod:
            return error_response(f"Module '{module}' does not exist.", details={"owner": owner, "repo": repo_name})

    def walk(path: str, depth: int):
        if depth >= max_depth:
            return {"_truncated": True}

        contents = safe_get_contents(repo, path, branch)
        if isinstance(contents, dict) and "error" in contents:
            return contents
        if hasattr(contents, "decoded_content") and hasattr(contents, "path"):
            return {
                contents.name: {
                    "type": "file",
                    "path": contents.path,
                    "size": getattr(contents, "size", None),
                }
            }

        tree = {}
        for item in contents:
            if item.type == "dir":
                tree[item.name] = walk(item.path, depth + 1)
            else:
                tree[item.name] = {"type": "file", "path": item.path, "size": item.size}
        return tree

    return walk(start_path, 0)


# -----------------------------
# read_file_content
# -----------------------------
@tool_safety("read_file_content")
def read_file_content(owner: str, repo_name: str, file_path: str, branch: str = "main"):
    """
    Read the content of a specific file in a GitHub repository.

    This tool fetches the contents of a single file in the repository at the specified
    branch. It automatically retries on GitHub API rate limits and returns an LLM-safe
    error envelope if the file does not exist or other errors occur.

    Args:
        owner (str): GitHub username or organization.
        repo_name (str): Repository name.
        file_path (str): Path to the file inside the repository.
        branch (str, optional): Branch name. Defaults to "main".

    Returns:
        dict: A dictionary containing the file content or an error:
            - {"content": "<file content>"} on success
            - {"error": {...}} on failure
    """
    client = _get_github_client()
    if not client:
        return error_response("GitHub client unavailable.")

    repo = client.get_repo(f"{owner}/{repo_name}")
    delay = 1

    for _ in range(3):
        try:
            file = repo.get_contents(file_path, ref=branch)
            return {"content": file.decoded_content.decode("utf-8", errors="ignore")}
        except RateLimitExceededException:
            time.sleep(delay)
            delay = min(delay * 2, 8)
        except GithubException as e:
            if e.status == 404:
                return {"error": f"Path '{file_path}' does not exist in '{owner}/{repo_name}' on '{branch}'."}
            raise e

    return error_response(f"Rate limited repeatedly while fetching file: {file_path} from repository {owner}/{repo_name}.")
