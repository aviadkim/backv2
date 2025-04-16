"""
Test script for Tesseract OCR.
"""
import os
import sys
import pytesseract
from PIL import Image
import cv2
import numpy as np

def test_tesseract():
    """Test if Tesseract OCR is working."""
    try:
        # Try to get Tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"Error getting Tesseract version: {str(e)}")
        return False

def create_test_image():
    """Create a test image with text."""
    # Create a white image
    img = np.ones((200, 600), dtype=np.uint8) * 255
    
    # Add text to the image
    cv2.putText(img, "Testing Tesseract OCR", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Save the image
    cv2.imwrite("test_image.png", img)
    print("Created test image: test_image.png")
    
    return "test_image.png"

def ocr_test_image(image_path):
    """Perform OCR on the test image."""
    try:
        # Open the image
        img = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        
        print(f"OCR result: {text}")
        return text
    except Exception as e:
        print(f"Error performing OCR: {str(e)}")
        return None

def main():
    """Main function."""
    print("Testing Tesseract OCR...")
    
    # Test if Tesseract is working
    if not test_tesseract():
        print("Tesseract is not working. Please install Tesseract OCR.")
        print("Download from: https://github.com/tesseract-ocr/tesseract")
        return 1
    
    # Create a test image
    image_path = create_test_image()
    
    # Perform OCR on the test image
    ocr_result = ocr_test_image(image_path)
    
    if ocr_result:
        print("Tesseract OCR is working correctly!")
        return 0
    else:
        print("Tesseract OCR failed to extract text from the test image.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
