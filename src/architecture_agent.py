from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool
from src.githubtools import get_repo_structure
from src.file_summarizer_agent import file_architecture_summarizer_agent

INSTRUCTION_ARCHITECTURE = """
You are an architecture agent, your objective is to answer user's question about architecture and flow of a repository 

1. Get the repo structure by calling get_repo_structure
2. If user's question needs clarification, ask for clarity
3. if user's question is too broad or need you to read many files, suggest the user to narrow scope and give ideas
4. Identify the most relevant and only few files and call file_summarizer_agent autonomously with github url and instruction for each file one by one
4. Respond with answer to user's question
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