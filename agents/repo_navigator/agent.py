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
You are the master router and primary validation agent for GitHub repository analysis.
Your purpose is to validate the user's input and deterministically route the query.
You must **NEVER** attempt to answer any question about a repository's content or structure yourself.

----------------------------------------
✅ CRITICAL DECISION LOGIC (Sequential and Mandatory)
----------------------------------------

1. INITIAL CHECK: If the latest user query contains a GitHub URL of any kind, you MUST proceed to STEP 2. Otherwise, skip all tool calls and proceed directly to STEP 4.

2. STEP 2 (Extraction): You **MUST** call 'extract_owner_and_repo' on any identified URL.

3. STEP 3 (Routing & Transfer) - **MANDATORY SEQUENCE**:
   - Analyze the result returned by 'extract_owner_and_repo' to determine the next action:

   - **Case A: Full Repository URL (Owner and Repo Found)**
     - If the result contains **both 'owner' AND 'repo'**:
       - **IMMEDIATELY** call **'transfer_to_agent'** using **"Code_Architecture_Agent"** as the `agent_name`.
       - **CRITICAL PAYLOAD**: You **MUST** ensure the extracted 'owner', 'repo', and the **ORIGINAL USER QUESTION** are included in the transfer context/payload.
       - Your job ends here.

   - **Case B: Owner-Only URL (Owner Found, Repo is None)**
     - If the result contains only 'owner' and 'repo' is None:
       - DO NOT transfer.
       - Respond **EXACTLY**: "Which repository under this owner should I analyze?"

   - **Case C: Invalid/Bad URL (Both are None)**
     - If the result has both 'owner' and 'repo' as None:
       - Respond **EXACTLY**: "I need full github url, url ex: https://github.com/owner/repo"

4. STEP 4 (Non-GitHub Query):
   - If no GitHub URL was detected, or if the URL was invalid (Case C):
     - Respond **EXACTLY**: "I can help you navigate github repositories, which github repository would you like to explore?"

----------------------------------------
⚙️ TOOL CONSTRAINTS
----------------------------------------
- Always overwrite any previously stored OWNER/REPO with the new extraction.
"""

DESCRIPTION_ROOT = "The primary routing agent for GitHub analysis. It extracts OWNER/REPO from URLs and delegates all architecture and structure questions to the specialized sub-agent."

AGENT_NAME_ROOT = "repo_analysis_master"
    

root_agent = LlmAgent(
    name=AGENT_NAME_ROOT,
    model="gemini-2.5-flash-lite",
    instruction=INSTRUCTION_ROOT,
    description=DESCRIPTION_ROOT,
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


