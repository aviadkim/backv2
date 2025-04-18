"""
OCR Processor Module

This module provides enhanced OCR capabilities with language-specific support.
It uses OCRmyPDF and Tesseract to improve text extraction from financial documents.
"""

import os
import logging
import tempfile
import subprocess
from typing import List, Dict, Any, Optional
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OCRProcessor:
    """
    Enhanced OCR processing with language-specific support.
    Uses OCRmyPDF and Tesseract to improve text extraction from financial documents.
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize the OCRProcessor with a PDF file path.
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.output_path = None
        self.images = []
        self.ocr_text = ""
        
        # Verify the PDF file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Initialized OCRProcessor for {pdf_path}")
    
    def process(self, languages: List[str] = ['eng', 'heb'], 
                dpi: int = 300) -> str:
        """
        Process the PDF with OCR.
        
        Args:
            languages: List of language codes for OCR
            dpi: DPI for image conversion
            
        Returns:
            Path to the OCR-processed PDF
        """
        logger.info(f"Processing {self.pdf_path} with OCR (languages: {languages}, dpi: {dpi})")
        
        # Create a temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            self.output_path = tmp_file.name
        
        # Try to use OCRmyPDF if available
        if self._is_ocrmypdf_available():
            self._process_with_ocrmypdf(languages, self.output_path)
        else:
            # Fallback to manual OCR with Tesseract
            self._process_with_tesseract(languages, dpi, self.output_path)
        
        logger.info(f"OCR processing complete, output saved to {self.output_path}")
        
        return self.output_path
    
    def _is_ocrmypdf_available(self) -> bool:
        """
        Check if OCRmyPDF is available.
        
        Returns:
            Boolean indicating if OCRmyPDF is available
        """
        try:
            subprocess.run(['ocrmypdf', '--version'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            logger.warning("OCRmyPDF not available, falling back to Tesseract")
            return False
    
    def _process_with_ocrmypdf(self, languages: List[str], output_path: str) -> None:
        """
        Process the PDF with OCRmyPDF.
        
        Args:
            languages: List of language codes
            output_path: Path to save the output PDF
        """
        try:
            # Prepare language parameter
            lang_param = '+'.join(languages)
            
            # Run OCRmyPDF
            subprocess.run([
                'ocrmypdf',
                '--language', lang_param,
                '--deskew',              # Straighten skewed pages
                '--clean',               # Clean pages before OCR
                '--optimize', '1',       # Optimize PDF
                '--skip-text',           # Skip pages with text
                '--force-ocr',           # Force OCR even if text is present
                '--output-type', 'pdf',  # Output as PDF
                self.pdf_path,
                output_path
            ], check=True)
            
            logger.info("OCRmyPDF processing successful")
        except subprocess.SubprocessError as e:
            logger.error(f"Error processing with OCRmyPDF: {e}")
            # Fallback to Tesseract
            self._process_with_tesseract(languages, 300, output_path)
    
    def _process_with_tesseract(self, languages: List[str], dpi: int, output_path: str) -> None:
        """
        Process the PDF with Tesseract OCR.
        
        Args:
            languages: List of language codes
            dpi: DPI for image conversion
            output_path: Path to save the output PDF
        """
        try:
            # Convert PDF to images
            self.images = convert_from_path(self.pdf_path, dpi=dpi)
            logger.info(f"Converted PDF to {len(self.images)} images")
            
            # Prepare language parameter
            lang_param = '+'.join(languages)
            
            # Process each image with Tesseract
            all_text = []
            
            for i, image in enumerate(self.images):
                logger.info(f"Processing image {i+1}/{len(self.images)}")
                
                # Convert PIL image to OpenCV format for preprocessing
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Preprocess image
                img_processed = self._preprocess_image(img_cv)
                
                # Perform OCR
                text = pytesseract.image_to_string(img_processed, lang=lang_param)
                all_text.append(text)
                
                # Save processed image
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_img:
                    cv2.imwrite(tmp_img.name, img_processed)
                    logger.debug(f"Saved processed image to {tmp_img.name}")
            
            # Combine all text
            self.ocr_text = '\n\n'.join(all_text)
            
            # Save OCR text to a file
            text_path = output_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(self.ocr_text)
            
            logger.info(f"Saved OCR text to {text_path}")
            
            # Create a PDF from the processed images
            self.images[0].save(
                output_path,
                save_all=True,
                append_images=self.images[1:],
                resolution=dpi
            )
            
            logger.info("Tesseract processing successful")
        except Exception as e:
            logger.error(f"Error processing with Tesseract: {e}")
            # If output file doesn't exist, copy the original
            if not os.path.exists(output_path):
                import shutil
                shutil.copy(self.pdf_path, output_path)
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        
        Args:
            image: OpenCV image
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised
    
    def extract_text(self) -> str:
        """
        Extract text from the OCR-processed PDF.
        
        Returns:
            Extracted text
        """
        if not self.ocr_text and self.output_path:
            # If we used OCRmyPDF, extract text from the output PDF
            try:
                import pdfplumber
                
                with pdfplumber.open(self.output_path) as pdf:
                    text_parts = []
                    for page in pdf.pages:
                        text_parts.append(page.extract_text() or '')
                    
                    self.ocr_text = '\n\n'.join(text_parts)
            except Exception as e:
                logger.error(f"Error extracting text from OCR-processed PDF: {e}")
        
        return self.ocr_text
    
    def cleanup(self) -> None:
        """
        Clean up temporary files.
        """
        if self.output_path and os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
                logger.info(f"Removed temporary file {self.output_path}")
                
                # Also remove text file if it exists
                text_path = self.output_path.replace('.pdf', '.txt')
                if os.path.exists(text_path):
                    os.remove(text_path)
                    logger.info(f"Removed temporary file {text_path}")
            except Exception as e:
                logger.error(f"Error cleaning up temporary files: {e}")


# Example usage
if __name__ == "__main__":
    # This will only run when the script is executed directly
    import sys
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        processor = OCRProcessor(pdf_path)
        output_path = processor.process()
        
        print(f"OCR processing complete, output saved to {output_path}")
        
        # Extract text
        text = processor.extract_text()
        print(f"Extracted {len(text)} characters of text")
        
        # Print first 500 characters
        print(text[:500] + '...')
        
        # Clean up
        processor.cleanup()
    else:
        print("Please provide a PDF file path")
