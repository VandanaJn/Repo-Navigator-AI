from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from src.githubtools import get_repo_structure, read_file_content

SYSTEM_INSTRUCTION = """You must NEVER guess the purpose of a repository.
When asked about a repository's purpose, behavior, architecture, design,
how it works, or what it does, you MUST autonomously:
1. Call get_repo_structure to retrieve the file tree.
2. Identify the most relevant files WITHOUT asking the user.
3. Automatically call read_file_content on relevant files.
4. Only after reading them, answer the question based on real code,
   not filenames or assumptions.
"""

root_agent = LlmAgent(
    name="Repo_Navigator",
    model="gemini-2.5-flash-lite", # Or your preferred Gemini model
    instruction=SYSTEM_INSTRUCTION,
    description="An assistant that can navigate a repo and answer question about it.",
    tools=[get_repo_structure, read_file_content]
)