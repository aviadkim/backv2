"""
Base classes and interfaces for agents.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class AgentResponse:
    """Response from an agent."""
    
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())
        self.timestamp = None  # Will be set when stored
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentResponse':
        """Create from dictionary."""
        response = cls(content=data["content"], metadata=data.get("metadata", {}))
        response.id = data.get("id", str(uuid.uuid4()))
        response.timestamp = data.get("timestamp")
        return response


class Agent(ABC):
    """Base class for all agents."""
    
    def __init__(self, agent_id: str, name: str, description: str, config: Dict[str, Any] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.config = config or {}
        self.conversation_history: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def process(self, query: str, context: Dict[str, Any] = None) -> AgentResponse:
        """Process a query and return a response."""
        pass
    
    def add_to_history(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "metadata": metadata or {}
        })
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "config": self.config,
            "type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create from dictionary."""
        # This will be implemented by the AgentFactory
        raise NotImplementedError("Use AgentFactory to create agents from dictionaries")


class AgentFactory:
    """Factory for creating agents."""
    
    _agent_types: Dict[str, type] = {}
    
    @classmethod
    def register(cls, agent_type: str):
        """Register an agent type."""
        def decorator(agent_class):
            cls._agent_types[agent_type] = agent_class
            return agent_class
        return decorator
    
    @classmethod
    def create(cls, agent_type: str, agent_id: str, name: str, description: str, config: Dict[str, Any] = None) -> Agent:
        """Create an agent of the specified type."""
        if agent_type not in cls._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_types[agent_type]
        return agent_class(agent_id=agent_id, name=name, description=description, config=config)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Agent:
        """Create an agent from a dictionary."""
        agent_type = data.get("type")
        if not agent_type:
            raise ValueError("Agent type not specified")
        
        return cls.create(
            agent_type=agent_type,
            agent_id=data.get("agent_id", str(uuid.uuid4())),
            name=data.get("name", "Unnamed Agent"),
            description=data.get("description", ""),
            config=data.get("config", {})
        )
    
    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get a list of available agent types."""
        return list(cls._agent_types.keys())
