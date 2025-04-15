"""
Test script to verify FinancialTableDetectorAgent functionality.
"""
import os
import sys
import cv2
import numpy as np
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_table_image(width=800, height=600):
    """
    Create a sample image with a financial table for testing.
    
    Args:
        width: Image width
        height: Image height
        
    Returns:
        Sample image as numpy array
    """
    # Create a blank image
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add table grid lines
    # Horizontal lines
    for y in range(100, 401, 50):
        cv2.line(image, (100, y), (700, y), (0, 0, 0), 1)
    
    # Vertical lines
    for x in range(100, 701, 150):
        cv2.line(image, (x, 100), (x, 400), (0, 0, 0), 1)
    
    # Add table headers
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, "Security", (120, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Quantity", (270, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Price", (420, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "Value", (570, 90), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    # Add table data
    cv2.putText(image, "Apple Inc.", (120, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "100", (270, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$150.25", (420, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$15,025.00", (570, 140), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.putText(image, "Microsoft", (120, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "50", (270, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$300.50", (420, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$15,025.00", (570, 190), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.putText(image, "Amazon", (120, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "25", (270, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$130.75", (420, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$3,268.75", (570, 240), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.putText(image, "Tesla", (120, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "30", (270, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$220.00", (420, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$6,600.00", (570, 290), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.putText(image, "NVIDIA", (120, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "40", (270, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$450.25", (420, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(image, "$18,010.00", (570, 340), font, 0.6, (0, 0, 0), 1, cv2.LINE_AA)
    
    cv2.putText(image, "Total", (120, 390), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(image, "$57,928.75", (570, 390), font, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
    
    return image

def test_financial_table_detector_agent(api_key=None):
    """Test FinancialTableDetectorAgent functionality."""
    try:
        from DevDocs.backend.agents.financial_table_detector_agent import FinancialTableDetectorAgent
        
        # Check for API key
        api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("Error: OpenRouter API key is required. Set OPENROUTER_API_KEY environment variable.")
            return False
        
        print("Testing FinancialTableDetectorAgent...")
        
        # Create an instance of the agent
        agent = FinancialTableDetectorAgent(api_key=api_key)
        
        # Create a test image with a financial table
        print("Creating test image with financial table...")
        img = create_sample_table_image()
        
        # Save the image
        output_dir = Path("./test_output")
        output_dir.mkdir(exist_ok=True, parents=True)
        test_image_path = output_dir / "financial_table_test.png"
        cv2.imwrite(str(test_image_path), img)
        print(f"Test image saved to: {test_image_path}")
        
        # Process the image with the agent
        try:
            print("Processing image with FinancialTableDetectorAgent...")
            result = agent.process({"image": img, "language": "eng"})
            
            print(f"Agent result: {result}")
            
            if "tables" in result and len(result["tables"]) > 0:
                print("FinancialTableDetectorAgent is working!")
                return True
            else:
                print("No tables detected. FinancialTableDetectorAgent might not be working correctly.")
                return False
        except Exception as e:
            print(f"Error processing image with FinancialTableDetectorAgent: {e}")
            return False
    
    except ImportError as e:
        print(f"Error importing FinancialTableDetectorAgent: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test FinancialTableDetectorAgent functionality")
    parser.add_argument("--api-key", help="OpenRouter API key")
    args = parser.parse_args()
    
    success = test_financial_table_detector_agent(args.api_key)
    
    if success:
        print("\nFinancialTableDetectorAgent test passed!")
        sys.exit(0)
    else:
        print("\nFinancialTableDetectorAgent test failed!")
        sys.exit(1)
