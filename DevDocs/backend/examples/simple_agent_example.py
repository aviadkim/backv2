"""
Simple example of using the OpenRouter API with a basic agent.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

class SimpleAgent(BaseAgent):
    """A simple agent that responds to questions."""
    
    def __init__(self, api_key=None):
        """Initialize the simple agent."""
        super().__init__(
            name="Simple Assistant",
            description="I am a helpful assistant that can answer questions about various topics.",
            api_key=api_key
        )
    
    def run(self, input_data, **kwargs):
        """
        Run the agent on the input data.
        
        Args:
            input_data: Input text
            **kwargs: Additional parameters
            
        Returns:
            Response text
        """
        if not self.is_ready:
            raise RuntimeError("Agent is not ready. OpenRouter client initialization failed.")
        
        # Get the response
        response = self.get_completion(input_data, **kwargs)
        
        return {
            "input": input_data,
            "response": response
        }

def main():
    """Run the simple agent example."""
    parser = argparse.ArgumentParser(description="Simple Agent Example")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--prompt", default="Tell me about financial document analysis.", help="Prompt to send to the agent")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    try:
        # Create the agent
        agent = SimpleAgent(api_key=api_key)
        
        # Run the agent
        print(f"Sending prompt: {args.prompt}")
        result = agent.run(args.prompt)
        
        # Print the response
        print("\nResponse:")
        print("-" * 40)
        print(result["response"])
        print("-" * 40)
        
        return 0
    
    except Exception as e:
        print(f"Error running agent: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
