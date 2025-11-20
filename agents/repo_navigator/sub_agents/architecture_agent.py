from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from .tools.githubtools import get_repo_structure
from .file_summarizer_agent import file_architecture_summarizer_agent

# INSTRUCTION_ARCHITECTURE = """
# You are an architecture agent, your objective is to answer user's question about architecture and flow of a repository 

# 1. Get the repo structure by calling get_repo_structure
# 2. Identify few most relevant files and call file_summarizer_agent autonomously with github url for each file
# 3. If user's question needs clarification, ask for clarity
# 4. if user's question is too broad or need you to read too many files, suggest the user to narrow scope and give ideas based on structure
# 5. Give concise and clear answer

# example of owner/reponame 
# 1. https://github.com/VandanaJn/chatbot-backend, VandanaJn is the owner and chatbot-backend is the reponame
# 2. https://github.com/VandanaJn, VandanaJn is the owner and VandanaJn is the reponame
# """

INSTRUCTION_ARCHITECTURE="""You are an architecture agent. Your goal is to explain the architecture and flow of a GitHub repository.

RULES:
1. If the user provides a GitHub URL, you MUST extract:
   - owner = segment after github.com/
   - repo = second segment, IF it exists
   Example: https://github.com/user/repo → owner="user", repo="repo"

2. If the GitHub URL contains ONLY the owner (example: https://github.com/user),
   ASK the user: “Which repository under this owner should I analyze?”
   Never assume or guess.

3. NEVER ask the user for owner/repo if both are already present in the URL.

4. ALWAYS begin by calling get_repo_structure.

5. After retrieving the repo structure:
   - If a high-level answer is sufficient, answer without summarizing files. 
   - Otherwise, pick 1–7 relevant files and call the Code_Summarizer_for_architecture 
     subagent on each (via github URL + filepath).


6. If answering requires too many files or the question is too broad,
   ask the user to narrow the scope based on repo structure.

7. Provide a concise, clear answer.
"""

DESCRIPTION_ARCHITECTURE="An assistant that can answer user's question about flow or architecture related with a code repository."


architecture_summarizer_agent = LlmAgent(
    name="Code_Architecture_Agent",
    model="gemini-2.5-flash-lite", 
    instruction=INSTRUCTION_ARCHITECTURE,
    description=DESCRIPTION_ARCHITECTURE,
    tools=[get_repo_structure],
    sub_agents=[file_architecture_summarizer_agent]
)