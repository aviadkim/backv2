"""
Test script for evaluating the HebrewOCRAgent.
"""
import os
import sys
import cv2
import numpy as np
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DevDocs.test_agent_evaluation import AgentEvaluator

def create_sample_hebrew_image(width=500, height=500, text="שלום עולם", skew_angle=0, noise_level=10):
    """
    Create a sample image with Hebrew text for testing.
    
    Args:
        width: Image width
        height: Image height
        text: Text to add to the image
        skew_angle: Angle to skew the image
        noise_level: Level of noise to add
        
    Returns:
        Sample image as numpy array
    """
    # Create a blank image
    image = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add some text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, text, (width // 4, height // 2), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Add some noise
    if noise_level > 0:
        noise = np.random.randint(0, noise_level, (height, width), dtype=np.uint8)
        image = cv2.subtract(image, noise)
    
    # Add skew
    if skew_angle != 0:
        M = cv2.getRotationMatrix2D((width / 2, height / 2), skew_angle, 1)
        image = cv2.warpAffine(image, M, (width, height))
    
    return image

def create_sample_financial_hebrew_image(width=800, height=600):
    """
    Create a sample image with Hebrew financial text for testing.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Sample image as numpy array
    """
    # Create a blank image
    image = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add some financial text in Hebrew
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Header
    cv2.putText(image, "דוח תיק השקעות", (width // 2 - 100, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Table headers
    cv2.putText(image, "שם נייר", (width - 100, 100), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "כמות", (width - 200, 100), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "מחיר", (width - 300, 100), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "שווי", (width - 400, 100), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Table rows
    cv2.putText(image, "אפל", (width - 100, 150), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "100", (width - 200, 150), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "150.25", (width - 300, 150), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "15,025.00", (width - 400, 150), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    cv2.putText(image, "מיקרוסופט", (width - 100, 200), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "50", (width - 200, 200), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "300.50", (width - 300, 200), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "15,025.00", (width - 400, 200), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Summary
    cv2.putText(image, "סה\"כ", (width - 100, 250), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "30,050.00", (width - 400, 250), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Add some noise
    noise = np.random.randint(0, 10, (height, width), dtype=np.uint8)
    image = cv2.subtract(image, noise)
    
    return image

def test_hebrew_ocr_agent():
    """Test the HebrewOCRAgent."""
    try:
        from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent
        
        # Create the agent
        agent = HebrewOCRAgent()
        
        # Create test cases
        test_cases = [
            {
                "description": "Basic Hebrew text extraction",
                "input": {
                    "image": create_sample_hebrew_image(500, 500, "שלום עולם", 0, 10),
                    "with_positions": False
                },
                "expected": {
                    "status": "success"
                }
            },
            {
                "description": "Hebrew text extraction with positions",
                "input": {
                    "image": create_sample_hebrew_image(500, 500, "שלום עולם", 0, 10),
                    "with_positions": True
                },
                "expected": {
                    "status": "success"
                }
            },
            {
                "description": "Hebrew financial text extraction",
                "input": {
                    "image": create_sample_financial_hebrew_image(),
                    "with_positions": False
                },
                "expected": {
                    "status": "success"
                }
            },
            {
                "description": "Hebrew text extraction with skew",
                "input": {
                    "image": create_sample_hebrew_image(500, 500, "שלום עולם", 15, 10),
                    "with_positions": False
                },
                "expected": {
                    "status": "success"
                }
            },
            {
                "description": "Hebrew text extraction with noise",
                "input": {
                    "image": create_sample_hebrew_image(500, 500, "שלום עולם", 0, 30),
                    "with_positions": False
                },
                "expected": {
                    "status": "success"
                }
            }
        ]
        
        # Evaluate the agent
        evaluator = AgentEvaluator()
        results = evaluator.evaluate_agent("HebrewOCRAgent", agent, test_cases)
        
        return results
    except ImportError as e:
        print(f"Error importing HebrewOCRAgent: {str(e)}")
        print("This test requires pytesseract to be installed.")
        print("You can install it with: pip install pytesseract")
        print("You also need to install Tesseract OCR with Hebrew language support.")
        
        # Create dummy results
        return {
            "agent_name": "HebrewOCRAgent",
            "test_date": datetime.now().isoformat(),
            "total_tests": 5,
            "passed_tests": 0,
            "failed_tests": 5,
            "success_rate": 0,
            "error": str(e)
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test HebrewOCRAgent evaluation")
    args = parser.parse_args()
    
    test_hebrew_ocr_agent()
