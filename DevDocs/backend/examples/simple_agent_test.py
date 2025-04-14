"""
Simple test for the OpenRouter integration with a basic agent.
"""
import os
import sys
import argparse
import requests
from pathlib import Path

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.base_agent import BaseAgent

class SimpleTestAgent(BaseAgent):
    """A simple agent for testing the OpenRouter integration."""

    def __init__(self, api_key=None):
        """Initialize the simple test agent."""
        super().__init__(name="Test Agent")
        self.api_key = api_key

    def process(self, task):
        """
        Process a task.

        Args:
            task: Task to process

        Returns:
            Processed task
        """
        # Simple implementation for testing
        prompt = task.get('prompt', 'Hello, world!')

        # Use requests for direct API call

        # Set up the API URL
        api_url = "https://openrouter.ai/api/v1/chat/completions"

        # Set up the headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://backv2.com",
            "X-Title": "FinDoc Analyzer"
        }

        # Set up the data
        data = {
            "model": "openrouter/optimus-alpha",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }

        # Send the request
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        response_text = result["choices"][0]["message"]["content"]

        return {
            "input": prompt,
            "response": response_text
        }

def main():
    """Run the simple agent test."""
    parser = argparse.ArgumentParser(description="Simple Agent Test")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--prompt", default="Explain how financial document analysis works in 3 sentences.", help="Prompt to send to the agent")
    args = parser.parse_args()

    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1

    try:
        # Create the agent
        agent = SimpleTestAgent(api_key=api_key)

        # Process the task
        print(f"Sending prompt: {args.prompt}")
        task = {"prompt": args.prompt}
        result = agent.process(task)

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
