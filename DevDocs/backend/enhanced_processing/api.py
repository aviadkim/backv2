"""
API Module for Enhanced Document Processing

This module provides API endpoints for the enhanced document processing pipeline.
"""

import os
import logging
import json
import tempfile
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Enhanced Financial Document Processing API")

# Create a global processor instance
processor = DocumentProcessor(api_key=os.getenv('GOOGLE_API_KEY'))

# Create a directory for processed documents
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'processed')
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Store processing results
processing_results = {}

class ProcessingResult(BaseModel):
    """
    Model for processing result status.
    """
    task_id: str
    status: str
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/process", response_model=ProcessingResult)
async def process_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    languages: List[str] = Query(["eng", "heb"], description="Languages for OCR")
):
    """
    Process a financial document.
    
    Args:
        background_tasks: FastAPI background tasks
        file: Uploaded PDF file
        languages: List of languages for OCR
        
    Returns:
        Processing result status
    """
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        # Write uploaded file to temporary file
        tmp_file.write(await file.read())
        tmp_path = tmp_file.name
    
    # Create a task ID
    task_id = f"task_{len(processing_results) + 1}"
    
    # Create a result entry
    processing_results[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0.0,
        "result": None,
        "error": None
    }
    
    # Process document in background
    background_tasks.add_task(
        process_document_task,
        task_id=task_id,
        pdf_path=tmp_path,
        languages=languages
    )
    
    return ProcessingResult(**processing_results[task_id])

@app.get("/status/{task_id}", response_model=ProcessingResult)
async def get_status(task_id: str):
    """
    Get the status of a processing task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Processing result status
    """
    if task_id not in processing_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return ProcessingResult(**processing_results[task_id])

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    """
    Get the result of a processing task.
    
    Args:
        task_id: Task ID
        
    Returns:
        Processing result
    """
    if task_id not in processing_results:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = processing_results[task_id]
    
    if result["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Task is not completed: {result['status']}")
    
    return JSONResponse(content=result["result"])

async def process_document_task(task_id: str, pdf_path: str, languages: List[str]):
    """
    Process a document in the background.
    
    Args:
        task_id: Task ID
        pdf_path: Path to the PDF file
        languages: List of languages for OCR
    """
    try:
        # Update progress
        processing_results[task_id]["progress"] = 0.1
        
        # Create output directory
        output_dir = os.path.join(PROCESSED_DIR, task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Process document
        result = processor.process(pdf_path, output_dir, languages)
        
        # Update result
        processing_results[task_id]["status"] = "completed"
        processing_results[task_id]["progress"] = 1.0
        processing_results[task_id]["result"] = result
        
        logger.info(f"Task {task_id} completed successfully")
    except Exception as e:
        # Update error
        processing_results[task_id]["status"] = "failed"
        processing_results[task_id]["error"] = str(e)
        
        logger.error(f"Task {task_id} failed: {e}")
    finally:
        # Clean up temporary file
        try:
            os.remove(pdf_path)
        except:
            pass
