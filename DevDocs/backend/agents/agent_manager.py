"""
Agent Manager for managing and orchestrating multiple agents.
"""
import os
import logging
from typing import Dict, Any, List, Optional, Type, Union
from .base_agent import BaseAgent

class AgentManager:
    """Manager for creating, configuring, and running agents."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent manager.
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.agents = {}
        self.logger = logging.getLogger("agent_manager")
        
        if not self.api_key:
            self.logger.warning("No API key provided. Some agents may not work properly.")
    
    def create_agent(
        self, 
        agent_id: str, 
        agent_class: Type[BaseAgent], 
        **kwargs
    ) -> BaseAgent:
        """
        Create a new agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_class: Agent class to instantiate
            **kwargs: Additional parameters for the agent
            
        Returns:
            The created agent
        """
        if agent_id in self.agents:
            self.logger.warning(f"Agent with ID '{agent_id}' already exists. Overwriting.")
        
        # Create the agent
        agent = agent_class(api_key=self.api_key, **kwargs)
        
        # Store the agent
        self.agents[agent_id] = agent
        
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            The agent, or None if not found
        """
        return self.agents.get(agent_id)
    
    def run_agent(
        self, 
        agent_id: str, 
        *args, 
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run an agent.
        
        Args:
            agent_id: Agent ID
            *args: Positional arguments for the agent
            **kwargs: Keyword arguments for the agent
            
        Returns:
            Agent result
        """
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent with ID '{agent_id}' not found")
        
        # Create a task from the arguments
        task = kwargs
        
        # Run the agent
        return agent.process(task)
    
    def run_pipeline(
        self, 
        pipeline: List[Dict[str, Any]], 
        input_data: Any
    ) -> Dict[str, Any]:
        """
        Run a pipeline of agents.
        
        Args:
            pipeline: List of pipeline steps, each with:
                - agent_id: Agent ID
                - params: Parameters for the agent
                - output_key: Key to store the output
            input_data: Input data for the first agent
            
        Returns:
            Pipeline results
        """
        results = {
            "input": input_data,
            "steps": []
        }
        
        current_input = input_data
        
        for step in pipeline:
            agent_id = step.get("agent_id")
            params = step.get("params", {})
            output_key = step.get("output_key")
            
            if not agent_id:
                raise ValueError("Pipeline step must have an agent_id")
            
            # Create the task
            task = params.copy()
            task["input"] = current_input
            
            # Run the agent
            try:
                output = self.run_agent(agent_id, **task)
                
                # Store the step result
                step_result = {
                    "agent_id": agent_id,
                    "success": True,
                    "output": output
                }
                
                # Update the current input for the next step
                if output_key:
                    results[output_key] = output
                
                current_input = output
            except Exception as e:
                self.logger.error(f"Error running agent '{agent_id}': {e}")
                
                # Store the error
                step_result = {
                    "agent_id": agent_id,
                    "success": False,
                    "error": str(e)
                }
                
                # Stop the pipeline
                break
            
            results["steps"].append(step_result)
        
        results["output"] = current_input
        return results
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent information
        """
        return [
            {
                "id": agent_id,
                "name": agent.name,
                "description": getattr(agent, "description", ""),
                "type": agent.__class__.__name__
            }
            for agent_id, agent in self.agents.items()
        ]
