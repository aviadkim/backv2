"""
Example script demonstrating how to use the lightweight ADK Financial Agent.
This version is optimized for low resource usage.
"""
import asyncio
import logging
import os
import sys
import uuid

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import the agent
from agents.adk_agents.financial_agent import FinancialAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main function."""
    print("Starting lightweight ADK agent example...")

    # Create the agent with low resource configuration
    agent = FinancialAgent(
        agent_id=str(uuid.uuid4()),
        name="Financial Analysis Agent (Lightweight)",
        description="Agent for analyzing financial documents and providing insights",
        config={
            "low_resource_mode": True,
            "use_cache": True,
            "cache_size": 50
        }
    )

    # Example document text (smaller for demonstration)
    document_text = """
    Annual Financial Report 2023

    Revenue: $10.5 million
    Profit: $2.3 million

    The company experienced a 15% growth in revenue compared to the previous year.
    """

    # Process a query
    query = f"Analyze this financial document: {document_text}"
    print("\nProcessing query...")
    response = await agent.process(query)

    # Print the response
    print("\nQuery:")
    print(query[:50] + "..." if len(query) > 50 else query)
    print("\nResponse:")
    print(response.content)
    print("\nMetadata:")
    print(response.metadata)

    print("\nExample completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())
