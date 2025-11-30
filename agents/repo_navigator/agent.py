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

INSTRUCTION_ROOT = """ you are the routing agent for GitHub analysis. Your job is to extract OWNER/REPO from URLs and delegate all architecture and structure questions to the specialized sub-agent
ROUTING AGENT PROTOCOL - FOLLOW EXACTLY AS WRITTEN.

You have TWO abilities:
1. Tool: extract_owner_and_repo(github_url) - extracts owner and repo from a URL
2. Sub-Agent: code_architecture_agent - handles all repository questions after extraction

WORKFLOW:
Step 1: User asks question with GitHub URL or provides github URL - call extract_owner_and_repo(github URL)
Step 2: Analyze result of extract_owner_and_repo:
   - If owner AND repo both exist (not None) 
        a.  transfer to "code_architecture_agent" and pass original_user_question, owner, repo, github_url. **DO NOT OUTPUT ANYTHING YOURSELF. IMMEDIATELY TRANSFER TO THE SUB-AGENT. No transfer message**
   - If ONLY owner exists 
        a. respond: "Which repository under this owner should I analyze? I need full github url, url ex: https://github.com/owner/repo"
   - If NEITHER exists
        a. respond: "I need full github url, url ex: https://github.com/owner/repo"
Step 4: If no URL in user message 
        a. respond: "I can help you navigate github repositories, which github repository would you like to explore?"
"""

DESCRIPTION_ROOT = "The primary routing agent for GitHub analysis. It extracts OWNER/REPO from URLs and delegates all architecture and structure questions to the specialized sub-agent."

AGENT_NAME_ROOT = "repo_analysis_master"
    

root_agent = LlmAgent(
    name=AGENT_NAME_ROOT,
    model="gemini-2.5-flash-lite",
    instruction=INSTRUCTION_ROOT,
    description=DESCRIPTION_ROOT,
    tools=[extract_owner_and_repo],
    sub_agents=[architecture_summarizer_agent],
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


