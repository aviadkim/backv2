"""
OCR Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import logging
import tempfile
import numpy as np
import cv2
from PIL import Image
from typing import List, Dict, Any, Optional

from ..utils import ensure_dir

logger = logging.getLogger(__name__)

class OCRAgent:
    """
    OCR Agent for extracting text from documents.
    """
    
    def __init__(self, config):
        """
        Initialize the OCR Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.ocr_config = config["ocr"]
        self.output_config = config["output"]
        
        logger.info("Initialized OCR Agent")
    
    def process(self, pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process a PDF document with OCR.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Output directory
            
        Returns:
            Dictionary with OCR results
        """
        logger.info(f"Processing {pdf_path} with OCR")
        
        # Create output directory
        ensure_dir(output_dir)
        
        # Convert PDF to images
        images = self._convert_pdf_to_images(pdf_path)
        logger.info(f"Converted PDF to {len(images)} images")
        
        # Process each image with OCR
        ocr_results = []
        
        for i, image in enumerate(images):
            logger.info(f"Processing page {i+1}/{len(images)}")
            
            # Preprocess image
            preprocessed = self._preprocess_image(image)
            
            # Save preprocessed image if configured
            if self.output_config["save_intermediates"]:
                preprocessed_path = os.path.join(output_dir, f"page_{i+1}_preprocessed.jpg")
                preprocessed.save(preprocessed_path)
            
            # Perform OCR
            ocr_result = self._perform_ocr(preprocessed)
            
            # Add page number
            ocr_result["page"] = i + 1
            
            # Add to results
            ocr_results.append(ocr_result)
        
        # Combine results
        combined_text = "\n\n".join([r["text"] for r in ocr_results])
        
        # Save combined text
        text_path = os.path.join(output_dir, "ocr_text.txt")
        with open(text_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        
        logger.info(f"OCR processing complete, text saved to {text_path}")
        
        return {
            "text": combined_text,
            "pages": ocr_results,
            "text_path": text_path,
            "image_paths": [os.path.join(output_dir, f"page_{i+1}_preprocessed.jpg") for i in range(len(images))] if self.output_config["save_intermediates"] else []
        }
    
    def _convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        Convert a PDF to images.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL images
        """
        try:
            # Try to convert PDF to images using pdf2image
            try:
                from pdf2image import convert_from_path
                return convert_from_path(
                    pdf_path,
                    dpi=self.ocr_config["dpi"],
                    thread_count=os.cpu_count() or 1
                )
            except Exception as pdf2image_error:
                logger.warning(f"Error using pdf2image: {pdf2image_error}")
                
                # Fallback to PyMuPDF (fitz)
                try:
                    import fitz
                    logger.info("Falling back to PyMuPDF for PDF conversion")
                    
                    doc = fitz.open(pdf_path)
                    images = []
                    
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        images.append(img)
                    
                    return images
                except ImportError:
                    logger.warning("PyMuPDF not available, trying another fallback")
                    
                    # Fallback to pdfplumber with PIL
                    try:
                        import pdfplumber
                        from PIL import Image
                        import numpy as np
                        
                        logger.info("Falling back to pdfplumber for PDF conversion")
                        
                        images = []
                        with pdfplumber.open(pdf_path) as pdf:
                            for page in pdf.pages:
                                # Get page as image
                                img = page.to_image(resolution=150).original
                                images.append(img)
                        
                        return images
                    except Exception as plumber_error:
                        logger.error(f"Error using pdfplumber fallback: {plumber_error}")
                        
                        # Last resort: create a blank image with text
                        logger.warning("Creating blank image as last resort")
                        img = Image.new('RGB', (800, 1000), color='white')
                        images = [img]
                        return images
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            
            # Return a blank image as a last resort
            img = Image.new('RGB', (800, 1000), color='white')
            return [img]
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess an image for OCR.
        
        Args:
            image: PIL image
            
        Returns:
            Preprocessed PIL image
        """
        # Convert PIL image to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        # Convert back to PIL image
        return Image.fromarray(denoised)
    
    def _perform_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """
        Perform OCR on an image.
        
        Args:
            image: PIL image
            
        Returns:
            Dictionary with OCR results
        """
        try:
            # Try to use pytesseract
            try:
                import pytesseract
                
                # Prepare OCR configuration
                config = f"--psm {self.ocr_config['page_segmentation_mode']} --oem {self.ocr_config['ocr_engine_mode']}"
                
                # Join languages
                lang = "+".join(self.ocr_config["languages"])
                
                # Perform OCR
                text = pytesseract.image_to_string(image, lang=lang, config=config)
                
                # Get bounding boxes for words
                boxes = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)
                
                # Filter valid boxes
                valid_indices = [i for i, conf in enumerate(boxes["conf"]) if conf > 0]
                
                words = []
                for i in valid_indices:
                    word = {
                        "text": boxes["text"][i],
                        "confidence": boxes["conf"][i],
                        "box": {
                            "x": boxes["left"][i],
                            "y": boxes["top"][i],
                            "width": boxes["width"][i],
                            "height": boxes["height"][i]
                        }
                    }
                    words.append(word)
                
                return {
                    "text": text,
                    "words": words
                }
            except (ImportError, NameError) as e:
                logger.warning(f"Pytesseract not available: {e}")
                
                # Try to use easyocr
                try:
                    import easyocr
                    logger.info("Falling back to EasyOCR")
                    
                    # Initialize reader
                    reader = easyocr.Reader(self.ocr_config["languages"])
                    
                    # Perform OCR
                    results = reader.readtext(np.array(image))
                    
                    # Extract text and boxes
                    text = "\n".join([result[1] for result in results])
                    
                    words = []
                    for result in results:
                        bbox, text, confidence = result
                        top_left, top_right, bottom_right, bottom_left = bbox
                        x = int(top_left[0])
                        y = int(top_left[1])
                        width = int(bottom_right[0] - top_left[0])
                        height = int(bottom_right[1] - top_left[1])
                        
                        word = {
                            "text": text,
                            "confidence": confidence * 100,  # Convert to percentage
                            "box": {
                                "x": x,
                                "y": y,
                                "width": width,
                                "height": height
                            }
                        }
                        words.append(word)
                    
                    return {
                        "text": text,
                        "words": words
                    }
                except ImportError:
                    logger.warning("EasyOCR not available")
                    
                    # Last resort: use pdfplumber to extract text
                    try:
                        import pdfplumber
                        import io
                        
                        logger.info("Falling back to pdfplumber for text extraction")
                        
                        # Save image to temporary file
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp:
                            image.save(temp.name)
                            temp_path = temp.name
                        
                        # Extract text using pdfplumber
                        with pdfplumber.open(temp_path) as pdf:
                            page = pdf.pages[0]
                            text = page.extract_text() or ""
                        
                        # Clean up
                        os.unlink(temp_path)
                        
                        return {
                            "text": text,
                            "words": []
                        }
                    except Exception as plumber_error:
                        logger.error(f"Error using pdfplumber for text extraction: {plumber_error}")
                        
                        # Last resort: return empty text
                        return {
                            "text": "",
                            "words": []
                        }
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            
            # Return empty text
            return {
                "text": "",
                "words": []
            }
