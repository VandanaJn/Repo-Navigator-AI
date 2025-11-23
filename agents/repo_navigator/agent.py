from google.adk.agents import LlmAgent
from .sub_agents.architecture_agent import architecture_summarizer_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.plugins.logging_plugin import (
    LoggingPlugin,
) 
import logging
logging.basicConfig(level=logging.INFO)

INSTRUCTION_ROOT = """You are a versatile repository analysis expert. When a user asks about the architecture 
or structure of a codebase, use the 'Code_Architecture_Agent' tool to get a detailed answer. 
You only support https://github.com repositories.
"""
DESCRIPTION_ROOT = "A master agent capable of analyzing repositories and delegating architecture questions."

AGENT_NAME_ROOT = "repo_analysis_master"
    

root_agent = LlmAgent(
    name=AGENT_NAME_ROOT,
    model="gemini-2.5-flash-lite",
    instruction=INSTRUCTION_ROOT,
    description="A master agent capable of analyzing repositories and delegating architecture questions.",
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


