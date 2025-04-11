"""
Script to query a document using the document agent.
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from agents.document_agent import DocumentAgent

async def query_document(document_id, question):
    """Query a document using the document agent."""
    print(f"Querying document {document_id} with question: {question}")
    
    # Create a document agent
    agent_config = {
        "api_key": os.environ.get("OPENROUTER_API_KEY", "demo_key"),
        "document_id": document_id
    }
    agent = DocumentAgent(
        agent_id="doc_agent_1",
        name="Document Analysis Agent",
        description="Agent that analyzes documents and answers questions about them",
        config=agent_config
    )
    
    # Process the question
    response = await agent.process(question)
    
    print(f"Answer: {response.content}")
    print(f"Metadata: {json.dumps(response.metadata, indent=2)}")
    
    return response.content

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python query_document.py <document_id> <question>")
        sys.exit(1)
    
    document_id = sys.argv[1]
    question = sys.argv[2]
    
    asyncio.run(query_document(document_id, question))
