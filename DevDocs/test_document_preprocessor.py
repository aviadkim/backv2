"""
Test script for the DocumentPreprocessorAgent.
"""
import os
import sys
import cv2
import numpy as np
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DevDocs.backend.agents.document_preprocessor_agent import DocumentPreprocessorAgent

def test_document_preprocessor(image_path=None):
    """Test the DocumentPreprocessorAgent."""
    print("\n=== Testing DocumentPreprocessorAgent ===")
    
    # Create the agent
    agent = DocumentPreprocessorAgent()
    
    # Use the provided image or a sample image
    if image_path is None:
        # Create a sample image with skew and noise
        image = np.ones((500, 500), dtype=np.uint8) * 255
        
        # Add some text
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, 'Sample Text', (100, 250), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        
        # Add some noise
        noise = np.random.randint(0, 50, (500, 500), dtype=np.uint8)
        image = cv2.subtract(image, noise)
        
        # Add skew
        rows, cols = image.shape
        M = cv2.getRotationMatrix2D((cols/2, rows/2), 15, 1)
        image = cv2.warpAffine(image, M, (cols, rows))
        
        # Save the sample image
        sample_path = "sample_image.png"
        cv2.imwrite(sample_path, image)
        image_path = sample_path
        print(f"Created sample image: {sample_path}")
    
    # Process the image
    result = agent.process({
        'image_path': image_path,
        'options': {
            'enhance_contrast': True,
            'fix_skew': True,
            'remove_noise': True,
            'binarize': False
        }
    })
    
    if result['status'] == 'success':
        print("Image preprocessing successful!")
        print(f"Original shape: {result['original_shape']}")
        print(f"Preprocessed shape: {result['preprocessed_shape']}")
        
        # Save the preprocessed image
        output_path = f"preprocessed_{Path(image_path).name}"
        cv2.imwrite(output_path, result['preprocessed_image'])
        print(f"Saved preprocessed image to: {output_path}")
        
        # Test text region detection
        text_regions = agent.detect_text_regions(result['preprocessed_image'])
        print(f"Detected {len(text_regions)} text regions")
        
        # Save image with text regions highlighted
        highlighted = cv2.cvtColor(result['preprocessed_image'], cv2.COLOR_GRAY2BGR)
        for x, y, w, h in text_regions:
            cv2.rectangle(highlighted, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        regions_path = f"text_regions_{Path(image_path).name}"
        cv2.imwrite(regions_path, highlighted)
        print(f"Saved text regions image to: {regions_path}")
        
        # Test cropping text regions
        cropped_regions = agent.crop_text_regions(result['preprocessed_image'])
        print(f"Cropped {len(cropped_regions)} text regions")
        
        # Save cropped regions
        for i, region in enumerate(cropped_regions):
            region_path = f"region_{i}_{Path(image_path).name}"
            cv2.imwrite(region_path, region['image'])
            print(f"Saved region {i} to: {region_path}")
        
        return True
    else:
        print(f"Error: {result['message']}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the DocumentPreprocessorAgent")
    parser.add_argument("--image", help="Path to an image file to process")
    args = parser.parse_args()
    
    test_document_preprocessor(args.image)
