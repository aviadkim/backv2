"""
Test script to verify HebrewOCRAgent functionality.
"""
import os
import sys
import cv2
import numpy as np
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_hebrew_image(text="שלום עולם", width=400, height=100):
    """Create a sample image with Hebrew text."""
    # Create a white image
    img = np.ones((height, width), np.uint8) * 255
    
    # Add text to the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    return img

def test_hebrew_ocr_agent():
    """Test HebrewOCRAgent functionality."""
    try:
        from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent
        
        print("Testing HebrewOCRAgent...")
        
        # Create an instance of the agent
        agent = HebrewOCRAgent()
        
        # Create a test image with Hebrew text
        print("Creating test image with Hebrew text...")
        img = create_sample_hebrew_image()
        
        # Save the image
        output_dir = Path("./test_output")
        output_dir.mkdir(exist_ok=True, parents=True)
        test_image_path = output_dir / "hebrew_agent_test.png"
        cv2.imwrite(str(test_image_path), img)
        print(f"Test image saved to: {test_image_path}")
        
        # Process the image with the agent
        try:
            print("Processing image with HebrewOCRAgent...")
            result = agent.process({"image": img, "with_positions": True})
            
            print(f"Agent result: {result}")
            
            if "text" in result and len(result["text"].strip()) > 0:
                print("HebrewOCRAgent is working!")
                return True
            else:
                print("OCR result is empty. HebrewOCRAgent might not be working correctly.")
                return False
        except Exception as e:
            print(f"Error processing image with HebrewOCRAgent: {e}")
            return False
    
    except ImportError as e:
        print(f"Error importing HebrewOCRAgent: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test HebrewOCRAgent functionality")
    args = parser.parse_args()
    
    success = test_hebrew_ocr_agent()
    
    if success:
        print("\nHebrewOCRAgent test passed!")
        sys.exit(0)
    else:
        print("\nHebrewOCRAgent test failed!")
        sys.exit(1)
