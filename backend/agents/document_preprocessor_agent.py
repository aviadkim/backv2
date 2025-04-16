"""
Document Preprocessor Agent for FinDoc Analyzer v1.0

This agent preprocesses financial documents to prepare them for further analysis.
"""
import os
import logging
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
import subprocess
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentPreprocessorAgent:
    """
    Agent for preprocessing financial documents.
    """
    
    def __init__(self, output_dir: Optional[str] = None, **kwargs):
        """
        Initialize the DocumentPreprocessorAgent.
        
        Args:
            output_dir: Directory to save preprocessed files
            **kwargs: Additional arguments
        """
        self.output_dir = output_dir
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        logger.info("DocumentPreprocessorAgent initialized")
    
    def process(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        Preprocess a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            **kwargs: Additional arguments
            
        Returns:
            Dictionary with preprocessing results
        """
        logger.info(f"Preprocessing document: {pdf_path}")
        
        # Create temporary directory if output_dir is not specified
        if not self.output_dir:
            temp_dir = tempfile.mkdtemp()
            output_dir = temp_dir
        else:
            output_dir = self.output_dir
        
        # Get the filename without extension
        filename = Path(pdf_path).stem
        
        # Output path for the preprocessed PDF
        output_path = os.path.join(output_dir, f"{filename}_preprocessed.pdf")
        
        try:
            # Check if OCRmyPDF is available
            try:
                # Try to optimize the PDF with OCRmyPDF
                subprocess.run(
                    ["ocrmypdf", "--optimize", "3", "--skip-text", pdf_path, output_path],
                    check=True,
                    capture_output=True
                )
                logger.info(f"Document optimized with OCRmyPDF: {output_path}")
            except (subprocess.SubprocessError, FileNotFoundError):
                # If OCRmyPDF is not available, just copy the file
                logger.warning("OCRmyPDF not available, copying file instead")
                shutil.copy(pdf_path, output_path)
            
            return {
                "status": "success",
                "output_path": output_path,
                "original_path": pdf_path
            }
        except Exception as e:
            logger.error(f"Error preprocessing document: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_path": pdf_path,  # Return original path on error
                "original_path": pdf_path
            }
