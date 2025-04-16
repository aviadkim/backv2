"""
Hebrew OCR Agent for accurate text recognition in Hebrew financial documents.
"""
import pytesseract
from PIL import Image
import numpy as np
import cv2
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from .base_agent import BaseAgent
from ..utils.ocr_processor import OCRProcessor

class HebrewOCRAgent(BaseAgent):
    """Agent specialized in recognizing Hebrew text in financial documents."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the Hebrew OCR agent.

        Args:
            api_key: OpenRouter API key (not used for this agent)
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Hebrew OCR Agent")
        self.description = "I specialize in recognizing Hebrew text in financial documents with high accuracy."

        # OCR configuration
        self.lang = "heb+eng"  # Support for Hebrew and English
        self.config = "--psm 6 --oem 1"  # Tesseract configuration

        # Financial keywords in Hebrew for improving recognition accuracy
        self.financial_keywords = [
            "סה\"כ", "סך הכל", "חשבון", "תיק", "השקעות", "ריבית",
            "מניות", "אג\"ח", "תשואה", "דיבידנד", "עמלה", "מט\"ח",
            "יתרה", "הפקדה", "משיכה", "שער", "עו\"ש", "ני\"ע"
        ]

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to extract text from an image or PDF.

        Args:
            task: Task dictionary with the following keys:
                - image_path: Path to the image file
                - or
                - image: Image as numpy array
                - or
                - pdf_path: Path to the PDF file
                - with_positions: Whether to include text positions (default: False)
                - language: OCR language (default: "heb+eng")
                - financial_doc: Whether this is a financial document (default: True)

        Returns:
            Dictionary with extracted text
        """
        # Get options
        with_positions = task.get('with_positions', False)
        language = task.get('language', self.lang)
        financial_doc = task.get('financial_doc', True)

        # Check if this is a PDF file
        if 'pdf_path' in task:
            pdf_path = task['pdf_path']
            if not isinstance(pdf_path, str):
                return {
                    'status': 'error',
                    'message': 'pdf_path must be a string'
                }

            # Get output path
            output_path = task.get('output_path', None)

            try:
                # Process the PDF with OCRmyPDF
                if financial_doc:
                    processed_pdf_path = OCRProcessor.process_financial_pdf(pdf_path, output_path)
                else:
                    processed_pdf_path = OCRProcessor.process_pdf(
                        pdf_path,
                        output_path,
                        language=language,
                        deskew=True,
                        clean=True
                    )

                # Extract text from the processed PDF
                text = OCRProcessor.extract_text_from_pdf(processed_pdf_path)

                return {
                    'status': 'success',
                    'text': text,
                    'processed_pdf_path': processed_pdf_path,
                    'ocr_options': {
                        'language': language,
                        'financial_doc': financial_doc
                    }
                }
            except Exception as e:
                return {
                    'status': 'error',
                    'message': f'Failed to process PDF: {str(e)}'
                }

        # Get the image
        if 'image_path' in task:
            image_path = task['image_path']
            if isinstance(image_path, str) or isinstance(image_path, Path):
                try:
                    img = Image.open(image_path)
                    img_array = np.array(img)
                except Exception as e:
                    return {
                        'status': 'error',
                        'message': f'Failed to read image from {image_path}: {str(e)}'
                    }
            else:
                return {
                    'status': 'error',
                    'message': 'image_path must be a string or Path object'
                }
        elif 'image' in task:
            img_array = task['image']
            if not isinstance(img_array, np.ndarray):
                return {
                    'status': 'error',
                    'message': 'image must be a numpy array'
                }
        else:
            return {
                'status': 'error',
                'message': 'Task must contain either image_path, image, or pdf_path'
            }

        # We already got the options above

        # Process the image
        if with_positions:
            result = self.extract_text_with_positions(img_array)
            return {
                'status': 'success',
                'text_with_positions': result
            }
        else:
            text = self.extract_text(img_array)
            return {
                'status': 'success',
                'text': text
            }

    def extract_text(self, image) -> str:
        """
        Extract text from an image with emphasis on Hebrew text.

        Args:
            image: Input image (path, PIL Image, or numpy array)

        Returns:
            Extracted text
        """
        # Load the image
        if isinstance(image, str) or isinstance(image, Path):
            img = Image.open(image)
            img_array = np.array(img)
        else:
            # If already received as numpy array
            img_array = image

        # Additional enhancement for financial documents
        enhanced = self._enhance_for_finance(img_array)

        # Run OCR
        text = pytesseract.image_to_string(enhanced, lang=self.lang, config=self.config)

        # Post-process the text
        processed_text = self._postprocess_text(text)

        return processed_text

    def extract_text_with_positions(self, image) -> List[Dict[str, Any]]:
        """
        Extract text with position in the image - important for document structure recognition.

        Args:
            image: Input image (path, PIL Image, or numpy array)

        Returns:
            List of dictionaries with text and position information
        """
        if isinstance(image, str) or isinstance(image, Path):
            img = Image.open(image)
            img_array = np.array(img)
        else:
            img_array = image

        enhanced = self._enhance_for_finance(img_array)

        # Get text data with position
        data = pytesseract.image_to_data(
            enhanced, lang=self.lang, config=self.config,
            output_type=pytesseract.Output.DICT
        )

        # Create list of words with positions
        text_with_positions = []
        for i in range(len(data['text'])):
            if int(data['conf'][i]) > 60:  # Only text above certain confidence level
                text_with_positions.append({
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': data['conf'][i],
                    'block_num': data['block_num'][i],
                    'par_num': data['par_num'][i],
                    'line_num': data['line_num'][i]
                })

        return text_with_positions

    def _enhance_for_finance(self, img_array):
        """
        Enhance image specifically for financial text recognition.

        Args:
            img_array: Input image as numpy array

        Returns:
            Enhanced image
        """
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_array.copy()

        # Increase contrast - effective for financial documents
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # Use filter to improve small text (common in financial tables)
        enhanced = cv2.GaussianBlur(enhanced, (3, 3), 0)
        enhanced = cv2.addWeighted(gray, 1.5, enhanced, -0.5, 0)

        return enhanced

    def _postprocess_text(self, text):
        """
        Additional processing to improve recognized text.

        Args:
            text: OCR-recognized text

        Returns:
            Processed text
        """
        # Fix spacing
        processed = ' '.join(text.split())

        # Handle specific replacements for common OCR errors in Hebrew
        replacements = {
            'ו1': 'ני',
            '11"ס': 'ני"ע',
            'סהי"נ': 'סה"כ',
            'טר\'ח': 'מט"ח'
        }

        for old, new in replacements.items():
            processed = processed.replace(old, new)

        # Improve keyword recognition
        for keyword in self.financial_keywords:
            # Check if there's a similar but not identical word to a keyword
            for word in processed.split():
                if self._similar_words(word, keyword) and word != keyword:
                    processed = processed.replace(word, keyword)

        return processed

    def _similar_words(self, word1, word2, threshold=0.7):
        """
        Check if two words are similar (Levenshtein distance).

        Args:
            word1: First word
            word2: Second word
            threshold: Similarity threshold

        Returns:
            True if words are similar, False otherwise
        """
        # For financial documents, we can use a simpler similarity check
        # if there are many identical letters and similar length
        if abs(len(word1) - len(word2)) > 2:
            return False

        # Calculate number of common characters
        common_chars = set(word1) & set(word2)
        similarity = len(common_chars) / max(len(set(word1)), len(set(word2)))

        return similarity > threshold
