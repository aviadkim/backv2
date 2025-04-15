"""
Test script to verify Tesseract OCR installation with Hebrew support.
"""
import os
import sys
import cv2
import numpy as np
import pytesseract
from PIL import Image
import argparse
from pathlib import Path

def create_sample_hebrew_image(text="שלום עולם", width=400, height=100):
    """Create a sample image with Hebrew text."""
    # Create a white image
    img = np.ones((height, width), np.uint8) * 255
    
    # Add text to the image
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
    
    return img

def test_tesseract_installation():
    """Test Tesseract OCR installation."""
    print("Testing Tesseract OCR installation...")
    
    # Check Tesseract version
    try:
        tesseract_version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {tesseract_version}")
    except Exception as e:
        print(f"Error getting Tesseract version: {e}")
        return False
    
    # Check available languages
    try:
        languages = pytesseract.get_languages()
        print(f"Available languages: {languages}")
        
        # Check if Hebrew is available
        if 'heb' not in languages:
            print("Hebrew language pack is not installed!")
            return False
        else:
            print("Hebrew language pack is installed.")
    except Exception as e:
        print(f"Error getting available languages: {e}")
        return False
    
    # Create a test image with Hebrew text
    print("Creating test image with Hebrew text...")
    img = create_sample_hebrew_image()
    
    # Save the image
    output_dir = Path("./test_output")
    output_dir.mkdir(exist_ok=True, parents=True)
    test_image_path = output_dir / "hebrew_test.png"
    cv2.imwrite(str(test_image_path), img)
    print(f"Test image saved to: {test_image_path}")
    
    # Perform OCR on the test image
    try:
        print("Performing OCR with Hebrew language...")
        text = pytesseract.image_to_string(img, lang='heb')
        print(f"OCR result: {text}")
        
        if len(text.strip()) > 0:
            print("Tesseract OCR is working with Hebrew!")
            return True
        else:
            print("OCR result is empty. Tesseract might not be working correctly with Hebrew.")
            return False
    except Exception as e:
        print(f"Error performing OCR: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Tesseract OCR installation")
    args = parser.parse_args()
    
    success = test_tesseract_installation()
    
    if success:
        print("\nTesseract OCR installation test passed!")
        sys.exit(0)
    else:
        print("\nTesseract OCR installation test failed!")
        sys.exit(1)
