"""
Agent module initialization.
"""
from .base import Agent, AgentResponse, AgentFactory
from .openrouter_agent import OpenRouterAgent
from .document_agent import DocumentAgent
from .sql_agent import SQLAgent
from .web_agent import WebAgent
from .adk_agents import FinancialAgent

# Import any additional agent types here

__all__ = [
    'Agent',
    'AgentResponse',
    'AgentFactory',
    'OpenRouterAgent',
    'DocumentAgent',
    'SQLAgent',
    'WebAgent',
    'FinancialAgent'
]
