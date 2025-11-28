import os
import time
from github import Github, GithubException, RateLimitExceededException
from github.ContentFile import ContentFile

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
client = Github(GITHUB_TOKEN)

def safe_get_contents(repo, path, ref, max_retries=3):
    """GitHub get_contents() with short retries — LLM-safe."""
    delay = 1

    for _ in range(max_retries):
        try:
            return repo.get_contents(path, ref=ref)
        except RateLimitExceededException:
            print(f"⚠️ GitHub rate-limited {path}. Retrying in {delay}s...")
            time.sleep(delay)
            delay = min(delay * 2, 8)  # max 8s
        except GithubException as e:
            if e.status == 404:
                return None
            raise e

    return {"error": f"Rate limited while fetching: {path}"}

def get_repo_structure(
    owner: str,
    repo_name: str,
    branch: str = "main",
    max_depth: int = 3,
    module: str | None = None,
) -> dict:
    """
    Return the directory structure of a GitHub repository.

    Traverses from the repo root or an optional subdirectory (`module`).
    Depth starts at 0 for the starting path. max_depth limits how many
    levels below the start are returned; deeper levels are truncated.
    If the module path doesn't exist, an error dict is returned.

    Args:
        owner (str): GitHub username or organization.
        repo_name (str): Repository name.
        branch (str, optional): Branch name. Defaults to "main".
        max_depth (int, optional): Maximum recursion depth. Depth is counted
            relative to the starting path. Defaults to 3.
        module (str, optional): Optional subdirectory path to restrict traversal
            (e.g., "src", "services/api"). If provided, its existence is validated.

    Returns:
        dict: A nested dictionary representing directory and file structure.
            Includes:
                - Directories as nested dicts
                - Files as { "type": "file", "path": ..., "size": ... }
                - { "_truncated": True } when max_depth is exceeded
                - { "error": "..." } when module validation fails
    """

    repo = client.get_repo(f"{owner}/{repo_name}")
    start_path = module.strip("/") if module else ""

    # --- Module validation ---
    if module:
        validation_contents = safe_get_contents(repo, start_path, branch)
        if not validation_contents or (
            isinstance(validation_contents, dict) and "error" in validation_contents
        ):
            return {
                "error": (
                    f"Module '{module}' does not exist in repo "
                    f"'{owner}/{repo_name}' on branch '{branch}'."
                )
            }

    def walk(path: str, depth: int):
        # --- TRUNCATE at max_depth ---
        if depth >= max_depth:
            return {"_truncated": True}

        contents = safe_get_contents(repo, path, branch)

        # --- Handle single file path ---
        if contents is None:
            return {}
        if isinstance(contents, ContentFile):
            return {
                contents.name: {
                    "type": "file",
                    "path": contents.path,
                    "size": contents.size,
                }
            }

        # --- Handle API error ---
        if isinstance(contents, dict) and "error" in contents:
            return contents

        # --- Normal directory walk ---
        tree = {}
        for item in contents:
            if item.type == "dir":
                if item.name == "tests":  # skip tests folder
                    continue
                tree[item.name] = walk(item.path, depth + 1)
            else:
                tree[item.name] = {
                    "type": "file",
                    "path": item.path,
                    "size": item.size,
                }
        return tree

    return walk(start_path, depth=0)





def read_file_content(owner:str, repo_name:str, file_path:str, branch:str="main"):
    """reads file from github repo 
    
    Args: owner: GitHub username or organization. 
    repo_name: Repository name. 
    file_path: path of the file 
    branch: Branch name (default "main"). 
    
    Returns: str representing file content."""
    repo = client.get_repo(f"{owner}/{repo_name}")

    for delay in [1, 2, 4]:
        try:
            file = repo.get_contents(file_path, ref=branch)
            return file.decoded_content.decode("utf-8", errors="ignore")
        except RateLimitExceededException:
            time.sleep(delay)
        except GithubException as e:
            if e.status == 404:
                return None
            raise e

    return None