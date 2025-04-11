"""
Base agent class for all agents in the FinDoc system.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class BaseAgent:
    """Base class for all agents in the system."""
    
    def __init__(self, name: str = "base", memory_path: Optional[str] = None):
        """Initialize the base agent.
        
        Args:
            name: Name of the agent
            memory_path: Optional path to persist agent memory
        """
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        
        # Setup memory persistence if path provided
        self.memory_path = memory_path
        self.memory = self._load_memory() if memory_path else {}
        
    def _load_memory(self) -> Dict:
        """Load agent memory from disk if it exists."""
        if not self.memory_path:
            return {}
            
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
        
        try:
            if os.path.exists(self.memory_path):
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load memory: {e}")
        
        return {}
        
    def _save_memory(self) -> bool:
        """Save agent memory to disk."""
        if not self.memory_path:
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.memory_path), exist_ok=True)
            
            with open(self.memory_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save memory: {e}")
            return False
    
    def remember(self, key: str, value: Any) -> None:
        """Store information in agent memory."""
        self.memory[key] = value
        self._save_memory()
        
    def recall(self, key: str, default: Any = None) -> Any:
        """Retrieve information from agent memory."""
        return self.memory.get(key, default)
        
    def forget(self, key: str) -> None:
        """Remove information from agent memory."""
        if key in self.memory:
            del self.memory[key]
            self._save_memory()
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement process()")
