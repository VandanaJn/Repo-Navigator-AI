from google.adk.agents import LlmAgent
from .tools.githubtools import read_file_content


INSTRUCTION_FILE_SUMMARIZER = """
You are an architecture summarizer agent, your objective is to read a file and return the summarized content 
to understand the flow and architecture of the system. 
1. If the user provides a GitHub URL, you MUST extract:
   - owner = segment after github.com/
   - repo = second segment, IF it exists
   Example: https://github.com/user/repo → owner="user", repo="repo"

2. If the GitHub URL contains ONLY the owner (example: https://github.com/user),
   ASK the user: “Which repository under this owner should I analyze?”
   Never assume or guess.

3. NEVER ask the user for owner/repo if both are already present in the URL.
4. Extract the filename/path
5. for code keep important imports, and signature of important methods
6. for other files summarize it to keep flow and architecture info clear and concise
7. Do not look for performance, errors, security or any other issue in the code
8. Do not suggest architecture advice, this is part of a larger agentic framework
"""

DESCRIPTION_FILE_SUMMARIZER = "An assistant that can read a file and summarize it to be useful for understanding architecture."
file_architecture_summarizer_agent = LlmAgent(
    name="Code_Summarizer_for_architecture",
    model="gemini-2.5-flash-lite", 
    instruction=INSTRUCTION_FILE_SUMMARIZER,
    description=DESCRIPTION_FILE_SUMMARIZER,
    tools=[read_file_content]
)