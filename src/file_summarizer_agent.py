from google.adk.agents import LlmAgent
from src.githubtools import read_file_content


INSTRUCTION_FILE_SUMMARIZER = """
You are an architecture summarizer agent, your objective is to read a file and return the summarized content 
to understand the flow and architecture of the system. 
1. for code keep important imports, and signature of important methods
2. for other files summarize it to keep flow and architecture info clear and concise
3. Do not look for performance, errors, security or any other issue in the code
4. Do not suggest architecture advice, this is part of a larger agentic framework
"""

DESCRIPTION_FILE_SUMMARIZER = "An assistant that can read a file and summarize it to be useful for understanding architecture."
file_architecture_summarizer_agent = LlmAgent(
    name="Code_Summarizer_for_architecture",
    model="gemini-2.5-flash-lite", 
    instruction=INSTRUCTION_FILE_SUMMARIZER,
    description=DESCRIPTION_FILE_SUMMARIZER,
    tools=[read_file_content]
)