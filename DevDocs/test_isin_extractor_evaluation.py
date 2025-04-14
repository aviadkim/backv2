"""
Test script for evaluating the ISINExtractorAgent.
"""
import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DevDocs.test_agent_evaluation import AgentEvaluator

def test_isin_extractor_agent():
    """Test the ISINExtractorAgent."""
    from DevDocs.backend.agents.isin_extractor_agent import ISINExtractorAgent
    
    # Create the agent
    agent = ISINExtractorAgent()
    
    # Create test cases
    test_cases = [
        {
            "description": "Basic ISIN extraction",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Apple Inc.
                ISIN: US0378331005
                Quantity: 100
                Price: $150.25
                Value: $15,025.00
                
                Security Name: Microsoft Corporation
                ISIN: US5949181045
                Quantity: 50
                Price: $300.50
                Value: $15,025.00
                """,
                "validate": True,
                "include_metadata": True
            },
            "expected": {
                "status": "success",
                "count": 2
            }
        },
        {
            "description": "ISIN extraction without validation",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Apple Inc.
                ISIN: US0378331005
                Quantity: 100
                
                Security Name: Invalid ISIN
                ISIN: XX1234567890
                Quantity: 50
                """,
                "validate": False,
                "include_metadata": True
            },
            "expected": {
                "status": "success",
                "count": 2
            }
        },
        {
            "description": "ISIN extraction without metadata",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Apple Inc.
                ISIN: US0378331005
                Quantity: 100
                """,
                "validate": True,
                "include_metadata": False
            },
            "expected": {
                "status": "success"
            }
        },
        {
            "description": "ISIN extraction with multiple occurrences",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Apple Inc.
                ISIN: US0378331005
                Quantity: 100
                
                Reference to Apple Inc. (US0378331005) again.
                """,
                "validate": True,
                "include_metadata": True
            },
            "expected": {
                "status": "success",
                "count": 1
            }
        },
        {
            "description": "ISIN extraction with no ISINs",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Unknown Company
                No ISIN available
                Quantity: 100
                """,
                "validate": True,
                "include_metadata": True
            },
            "expected": {
                "status": "success",
                "count": 0
            }
        },
        {
            "description": "ISIN extraction with context",
            "input": {
                "text": """
                Portfolio Statement
                
                Security Name: Apple Inc.
                ISIN: US0378331005
                Quantity: 100
                Price: $150.25
                Value: $15,025.00
                
                Security Name: Microsoft Corporation
                ISIN: US5949181045
                Quantity: 50
                Price: $300.50
                Value: $15,025.00
                
                Security Name: Amazon.com Inc.
                ISIN: US0231351067
                Quantity: 25
                Price: $130.75
                Value: $3,268.75
                """,
                "validate": True,
                "include_metadata": True
            },
            "expected": {
                "status": "success",
                "count": 3
            }
        }
    ]
    
    # Evaluate the agent
    evaluator = AgentEvaluator()
    results = evaluator.evaluate_agent("ISINExtractorAgent", agent, test_cases)
    
    return results

if __name__ == "__main__":
    test_isin_extractor_agent()
