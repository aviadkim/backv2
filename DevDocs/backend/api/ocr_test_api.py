"""
API routes for testing OCR functionality.
"""
import os
import base64
import io
import cv2
import numpy as np
import pytesseract
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from PIL import Image

router = APIRouter()

class Base64ImageRequest(BaseModel):
    """Request model for base64 encoded image."""
    image: str
    language: Optional[str] = "eng"

@router.get("/tesseract-version")
async def get_tesseract_version():
    """Get Tesseract OCR version and available languages."""
    try:
        version = pytesseract.get_tesseract_version()
        languages = pytesseract.get_languages()
        
        return {
            "status": "success",
            "version": str(version),
            "languages": languages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-hebrew")
async def test_hebrew_ocr(
    image: Optional[UploadFile] = File(None),
    base64_request: Optional[Base64ImageRequest] = None
):
    """Test Hebrew OCR on an image."""
    try:
        if image:
            # Read image file
            image_bytes = await image.read()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(image_bytes, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif base64_request:
            # Decode base64 image
            image_data = base64_request.image
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert PIL Image to OpenCV format
            cv_image = np.array(pil_image)
            if len(cv_image.shape) == 3 and cv_image.shape[2] == 4:
                # Convert RGBA to RGB
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2RGB)
        else:
            raise HTTPException(status_code=400, detail="No image provided")
        
        # Perform OCR with Hebrew language
        text = pytesseract.image_to_string(cv_image, lang='heb')
        
        return {
            "status": "success",
            "text": text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-table")
async def test_table_detection(
    image: Optional[UploadFile] = File(None),
    base64_request: Optional[Base64ImageRequest] = None
):
    """Test table detection on an image."""
    try:
        if image:
            # Read image file
            image_bytes = await image.read()
            
            # Convert to OpenCV format
            nparr = np.frombuffer(image_bytes, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        elif base64_request:
            # Decode base64 image
            image_data = base64_request.image
            if image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert PIL Image to OpenCV format
            cv_image = np.array(pil_image)
            if len(cv_image.shape) == 3 and cv_image.shape[2] == 4:
                # Convert RGBA to RGB
                cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2RGB)
        else:
            raise HTTPException(status_code=400, detail="No image provided")
        
        # Convert to grayscale
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
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
            table_img = cv_image[y:y+h, x:x+w]
            
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
        
        return {
            "status": "success",
            "tables": tables
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
