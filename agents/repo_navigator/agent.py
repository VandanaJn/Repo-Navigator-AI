from google.adk.agents import LlmAgent
from .sub_agents.architecture_agent import architecture_summarizer_agent
from .sub_agents.tools.githubtools import extract_owner_and_repo

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
) 
import logging
logging.basicConfig(level=logging.INFO)

INSTRUCTION_ROOT = """
You are a versatile repository analysis expert.

--- URL & TOOL CONSTRAINTS ---

1. If the latest user query contains a GitHub URL of any kind, you MUST call 
   the `extract_owner_and_repo` tool before deciding anything else.

2. After the tool returns values:
   a. If both OWNER and REPO are present → proceed immediately to Instruction 5 (Transfer Flow).
   b. If the URL contains only an OWNER without a REPO → respond exactly:
      "Which repository under this owner should I analyze?"
   c. If either OWNER or REPO is null, respond with:
      "I need full github url, url ex: https://github.com/owner/repo"

3. Only skip the tool call when no GitHub URL is present.

4. Always overwrite any previously stored OWNER/REPO with the new extraction.

5. Transfer Flow (CRITICAL - Data Persistence):
   - ALWAYS call extract_owner_and_repo first when a URL is detected.
   - IMMEDIATELY after extraction returns successfully (2a), you MUST transfer to Code_Architecture_Agent.
   - **When transferring, you MUST explicitly include the ORIGINAL USER QUESTION, the extracted OWNER, and the extracted REPO in the transfer payload or context.**
   - Do NOT try to answer the repository question yourself.
   - The sub-agent will handle structure fetching, summarization, and final responses.

6. If the user asks about anything other than GitHub repositories, respond 
   politely and say:
   "I can help you navigate github repositories, which github repository would you like to explore?"

7. CRITICAL: You MUST transfer control to Code_Architecture_Agent for ALL repository-related questions *after* successful extraction.
"""
DESCRIPTION_ROOT = "The primary routing agent for GitHub analysis. It extracts OWNER/REPO from URLs and delegates all architecture and structure questions to the specialized sub-agent."

AGENT_NAME_ROOT = "repo_analysis_master"
    

root_agent = LlmAgent(
    name=AGENT_NAME_ROOT,
    model="gemini-2.5-flash-lite",
    instruction=INSTRUCTION_ROOT,
    description="A master agent capable of analyzing repositories and delegating architecture questions.",
    tools=[extract_owner_and_repo],
    sub_agents=[architecture_summarizer_agent]
    )


root_app_compacting = App(
    name="repo_analysis_app_compacting",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,  # Trigger compaction every 3 invocations
        overlap_size=1,  # Keep 1 previous turn for context
    ), 
    plugins=[
        LoggingPlugin()
    ],
)

session_service = InMemorySessionService() 
runner = Runner(
    app=root_app_compacting,
    session_service=session_service ,
)


