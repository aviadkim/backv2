"""
Routes for testing OCR functionality.
"""
import os
import base64
import io
import cv2
import numpy as np
import pytesseract
from flask import Blueprint, request, jsonify
from PIL import Image

ocr_test_bp = Blueprint('ocr_test', __name__, url_prefix='/api/ocr-test')

@ocr_test_bp.route('/tesseract-version', methods=['GET'])
def get_tesseract_version():
    """Get Tesseract OCR version and available languages."""
    try:
        version = pytesseract.get_tesseract_version()
        languages = pytesseract.get_languages()
        
        return jsonify({
            "status": "success",
            "version": str(version),
            "languages": languages
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ocr_test_bp.route('/test-hebrew', methods=['POST'])
def test_hebrew_ocr():
    """Test Hebrew OCR on an image."""
    try:
        # Get image from request
        if 'image' not in request.files:
            # If no image file, check if there's a base64 image in the JSON
            if request.json and 'image' in request.json:
                # Decode base64 image
                image_data = request.json['image']
                if image_data.startswith('data:image'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert PIL Image to OpenCV format
                image = np.array(image)
                if len(image.shape) == 3 and image.shape[2] == 4:
                    # Convert RGBA to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            else:
                return jsonify({
                    "status": "error",
                    "message": "No image provided"
                }), 400
        else:
            # Get image file
            image_file = request.files['image']
            image_bytes = image_file.read()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Perform OCR with Hebrew language
        text = pytesseract.image_to_string(image, lang='heb')
        
        return jsonify({
            "status": "success",
            "text": text
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@ocr_test_bp.route('/test-table', methods=['POST'])
def test_table_detection():
    """Test table detection on an image."""
    try:
        # Get image from request
        if 'image' not in request.files:
            # If no image file, check if there's a base64 image in the JSON
            if request.json and 'image' in request.json:
                # Decode base64 image
                image_data = request.json['image']
                if image_data.startswith('data:image'):
                    # Remove data URL prefix
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convert PIL Image to OpenCV format
                image = np.array(image)
                if len(image.shape) == 3 and image.shape[2] == 4:
                    # Convert RGBA to RGB
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            else:
                return jsonify({
                    "status": "error",
                    "message": "No image provided"
                }), 400
        else:
            # Get image file
            image_file = request.files['image']
            image_bytes = image_file.read()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by size
        min_area = 1000
        table_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
        
        # Extract tables
        tables = []
        for i, cnt in enumerate(table_contours):
            # Get bounding rectangle
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Extract table region
            table_img = image[y:y+h, x:x+w]
            
            # Perform OCR on the table
            table_text = pytesseract.image_to_string(table_img)
            
            tables.append({
                "id": i,
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "text": table_text
            })
        
        return jsonify({
            "status": "success",
            "tables": tables
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
