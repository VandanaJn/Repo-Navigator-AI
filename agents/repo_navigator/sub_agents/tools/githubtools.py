import os
import time
from github import Github, GithubException, RateLimitExceededException

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

def get_repo_structure(owner:str, repo_name:str, branch:str="main", max_depth:int=3)->dict:
    """Return directory structure of a GitHub repo.
    Return the directory structure of a GitHub repository. 
    
    Args: owner: GitHub username or organization. 
    repo_name: Repository name. 
    branch: Branch name (default "main"). 
    max_depth: Maximum recursion depth (default 3). 
    
    Returns: Dictionary representing directory and file structure.
    """
    repo = client.get_repo(f"{owner}/{repo_name}")

    def walk(path, depth):
        if depth > max_depth:
            return {"_truncated": True}

        contents = safe_get_contents(repo, path, branch)
        if not contents or isinstance(contents, dict) and "error" in contents:
            return contents

        tree = {}

        for item in contents:
            if item.type == "dir":
                if item.name=="tests":
                    continue
                tree[item.name] = walk(item.path, depth + 1)
            else:
                tree[item.name] = {
                    "type": "file",
                    "path": item.path,
                    "size": item.size
                }

        return tree

    return walk("", 0)

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