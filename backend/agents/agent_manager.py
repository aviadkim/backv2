"""
Agent Manager for FinDoc Analyzer v1.0

This module manages the different agents used in the financial document processing pipeline.
"""
import os
import logging
from typing import Dict, Any, Type, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the creation and execution of different agents in the financial document processing pipeline.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AgentManager.
        
        Args:
            api_key: OpenRouter API key for AI-enhanced processing
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.agents = {}
        logger.info("AgentManager initialized")
    
    def create_agent(self, agent_id: str, agent_class: Type, **kwargs):
        """
        Create and register an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_class: Class of the agent to create
            **kwargs: Additional arguments to pass to the agent constructor
        """
        if self.api_key and "api_key" not in kwargs:
            kwargs["api_key"] = self.api_key
            
        self.agents[agent_id] = agent_class(**kwargs)
        logger.info(f"Agent '{agent_id}' created")
    
    def run_agent(self, agent_id: str, **kwargs) -> Dict[str, Any]:
        """
        Run a registered agent.
        
        Args:
            agent_id: Identifier of the agent to run
            **kwargs: Arguments to pass to the agent's process method
            
        Returns:
            Dictionary with the results of the agent's processing
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        logger.info(f"Running agent '{agent_id}'")
        result = self.agents[agent_id].process(**kwargs)
        logger.info(f"Agent '{agent_id}' completed")
        
        return result
    
    def get_agent(self, agent_id: str):
        """
        Get a registered agent.
        
        Args:
            agent_id: Identifier of the agent to get
            
        Returns:
            The requested agent
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent '{agent_id}' not found")
        
        return self.agents[agent_id]
