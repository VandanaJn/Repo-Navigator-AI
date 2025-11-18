from google.adk.agents import LlmAgent
from src.architecture_agent import architecture_summarizer_agent


INSTRUCTION_ROOT = """You are a versatile repository analysis expert. When a user asks about the architecture 
or structure of a codebase, use the 'Code_Architecture_Agent' tool to get a detailed answer. 
For other general questions (like 'What is this repo for?'), 
use your own reasoning capabilities or other tools as needed."""
DESCRIPTION_ROOT = "A master agent capable of analyzing repositories and delegating architecture questions."

root_agent = LlmAgent(
    name="Repo_Analysis_Master",
    model="gemini-2.5-flash-lite",
    instruction=INSTRUCTION_ROOT,
    description="A master agent capable of analyzing repositories and delegating architecture questions.",
    sub_agents=[architecture_summarizer_agent]
)


