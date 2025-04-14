"""
Test script for the HebrewOCRAgent.
"""
import os
import sys
import cv2
import numpy as np
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DevDocs.backend.agents.hebrew_ocr_agent import HebrewOCRAgent
from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent

def test_hebrew_ocr(image_path=None):
    """Test the HebrewOCRAgent."""
    print("\n=== Testing HebrewOCRAgent ===")
    
    # Create the agents
    ocr_agent = HebrewOCRAgent()
    preprocessor_agent = DocumentPreprocessorAgent()
    
    # Use the provided image or a sample image
    if image_path is None:
        # Create a sample image with Hebrew text
        image = np.ones((500, 500), dtype=np.uint8) * 255
        
        # Add some Hebrew text (this is just a placeholder, real Hebrew text would be better)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, 'Hebrew Text Sample', (100, 250), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Save the sample image
        sample_path = "sample_hebrew_image.png"
        cv2.imwrite(sample_path, image)
        image_path = sample_path
        print(f"Created sample image: {sample_path}")
    
    # Preprocess the image
    preprocess_result = preprocessor_agent.process({
        'image_path': image_path,
        'options': {
            'enhance_contrast': True,
            'fix_skew': True,
            'remove_noise': True
        }
    })
    
    if preprocess_result['status'] != 'success':
        print(f"Error preprocessing image: {preprocess_result['message']}")
        return False
    
    # Extract text
    preprocessed_image = preprocess_result['preprocessed_image']
    
    # Test basic text extraction
    print("\nTesting basic text extraction...")
    text = ocr_agent.extract_text(preprocessed_image)
    print(f"Extracted text:\n{text}")
    
    # Test text extraction with positions
    print("\nTesting text extraction with positions...")
    text_with_positions = ocr_agent.extract_text_with_positions(preprocessed_image)
    print(f"Extracted {len(text_with_positions)} text elements with positions")
    
    # Print the first few text elements with positions
    for i, item in enumerate(text_with_positions[:5]):
        print(f"Text {i+1}: '{item['text']}' at position ({item['x']}, {item['y']}) with confidence {item['conf']}")
    
    # Save image with text positions highlighted
    if text_with_positions:
        highlighted = cv2.cvtColor(preprocessed_image, cv2.COLOR_GRAY2BGR)
        for item in text_with_positions:
            x, y = item['x'], item['y']
            w, h = item['width'], item['height']
            cv2.rectangle(highlighted, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Add confidence score
            cv2.putText(highlighted, f"{item['conf']}", (x, y - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        
        positions_path = f"text_positions_{Path(image_path).name}"
        cv2.imwrite(positions_path, highlighted)
        print(f"Saved text positions image to: {positions_path}")
    
    # Test the agent's process method
    print("\nTesting agent's process method...")
    result = ocr_agent.process({
        'image': preprocessed_image,
        'with_positions': True
    })
    
    if result['status'] == 'success':
        print("OCR processing successful!")
        if 'text_with_positions' in result:
            print(f"Extracted {len(result['text_with_positions'])} text elements")
        elif 'text' in result:
            print(f"Extracted text length: {len(result['text'])}")
        return True
    else:
        print(f"Error: {result.get('message', 'Unknown error')}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the HebrewOCRAgent")
    parser.add_argument("--image", help="Path to an image file with Hebrew text")
    args = parser.parse_args()
    
    test_hebrew_ocr(args.image)
