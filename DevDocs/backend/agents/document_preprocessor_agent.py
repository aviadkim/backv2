"""
Document Preprocessor Agent for preparing documents before OCR.
"""
import cv2
import numpy as np
import os
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
from .base_agent import BaseAgent
from ..utils.ocr_processor import OCRProcessor

class DocumentPreprocessorAgent(BaseAgent):
    """Agent for preprocessing documents before OCR to improve text recognition quality."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the document preprocessor agent.

        Args:
            api_key: OpenRouter API key (not used for this agent)
            **kwargs: Additional parameters for the base agent
        """
        super().__init__(name="Document Preprocessor Agent")
        self.description = "I prepare documents for OCR by improving image quality, fixing skew, and removing noise."

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a task to preprocess a document image or PDF.

        Args:
            task: Task dictionary with the following keys:
                - image_path: Path to the image file
                - or
                - image: Image as numpy array
                - or
                - pdf_path: Path to the PDF file
                - options: Dictionary with preprocessing options:
                    - enhance_contrast: Whether to enhance contrast (default: True)
                    - fix_skew: Whether to fix skew (default: True)
                    - remove_noise: Whether to remove noise (default: True)
                    - binarize: Whether to binarize the image (default: False)
                    - dpi: Target DPI for the image (default: 300)
                    - language: OCR language(s) (default: "eng+heb")
                    - financial_doc: Whether this is a financial document (default: False)
                - output_path: Path to save the preprocessed image/PDF (optional)

        Returns:
            Dictionary with preprocessed image or PDF path
        """
        # Get the options
        options = task.get('options', {})
        enhance_contrast = options.get('enhance_contrast', True)
        fix_skew = options.get('fix_skew', True)
        remove_noise = options.get('remove_noise', True)
        binarize = options.get('binarize', False)
        target_dpi = options.get('dpi', 300)
        language = options.get('language', 'eng+heb')
        financial_doc = options.get('financial_doc', False)

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
                        deskew=fix_skew,
                        clean=remove_noise
                    )

                # Extract text from the processed PDF
                text = OCRProcessor.extract_text_from_pdf(processed_pdf_path)

                return {
                    'status': 'success',
                    'processed_pdf_path': processed_pdf_path,
                    'text': text,
                    'preprocessing_options': {
                        'enhance_contrast': enhance_contrast,
                        'fix_skew': fix_skew,
                        'remove_noise': remove_noise,
                        'binarize': binarize,
                        'target_dpi': target_dpi,
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
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    return {
                        'status': 'error',
                        'message': f'Failed to read image from {image_path}'
                    }
            else:
                return {
                    'status': 'error',
                    'message': 'image_path must be a string'
                }
        elif 'image' in task:
            image = task['image']
            if not isinstance(image, np.ndarray):
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

        # Preprocess the image
        preprocessed_image = self.preprocess_image(
            image,
            enhance_contrast=enhance_contrast,
            fix_skew=fix_skew,
            remove_noise=remove_noise,
            binarize=binarize,
            target_dpi=target_dpi
        )

        # Save the preprocessed image if output_path is provided
        if 'output_path' in task:
            output_path = task['output_path']
            cv2.imwrite(output_path, preprocessed_image)

        return {
            'status': 'success',
            'preprocessed_image': preprocessed_image,
            'original_shape': image.shape,
            'preprocessed_shape': preprocessed_image.shape,
            'preprocessing_options': {
                'enhance_contrast': enhance_contrast,
                'fix_skew': fix_skew,
                'remove_noise': remove_noise,
                'binarize': binarize,
                'target_dpi': target_dpi
            }
        }

    def preprocess_image(
        self,
        image: np.ndarray,
        enhance_contrast: bool = True,
        fix_skew: bool = True,
        remove_noise: bool = True,
        binarize: bool = False,
        target_dpi: int = 300
    ) -> np.ndarray:
        """
        Preprocess an image for OCR.

        Args:
            image: Input image
            enhance_contrast: Whether to enhance contrast
            fix_skew: Whether to fix skew
            remove_noise: Whether to remove noise
            binarize: Whether to binarize the image
            target_dpi: Target DPI for the image

        Returns:
            Preprocessed image
        """
        # Make a copy of the image to avoid modifying the original
        processed_image = image.copy()

        # Convert to grayscale if the image is in color
        if len(processed_image.shape) == 3:
            gray = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = processed_image.copy()

        # Fix skew if requested
        if fix_skew:
            gray = self._fix_skew(gray)

        # Enhance contrast if requested
        if enhance_contrast:
            gray = self._enhance_contrast(gray)

        # Remove noise if requested
        if remove_noise:
            gray = self._remove_noise(gray)

        # Binarize if requested
        if binarize:
            gray = self._binarize(gray)

        # Resize to target DPI if needed
        # Note: This is a simplified approach. In a real-world scenario,
        # you would need to know the original DPI of the image.
        # Here we assume a standard size and scale accordingly.
        if target_dpi != 0:
            # Assuming the image is originally at 72 DPI (standard screen resolution)
            scale_factor = target_dpi / 72.0
            if scale_factor != 1.0:
                new_width = int(gray.shape[1] * scale_factor)
                new_height = int(gray.shape[0] * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)

        return gray

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance the contrast of an image.

        Args:
            image: Input grayscale image

        Returns:
            Contrast-enhanced image
        """
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)

        return enhanced

    def _fix_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Fix the skew of an image.

        Args:
            image: Input grayscale image

        Returns:
            Deskewed image
        """
        # Threshold the image to get a binary image
        thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Find all contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea, default=None)

        if largest_contour is None:
            # No contours found, return the original image
            return image

        # Get the minimum area rectangle that contains the contour
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]

        # Adjust the angle
        if angle < -45:
            angle = 90 + angle

        # Rotate the image to correct the skew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Remove noise from an image.

        Args:
            image: Input grayscale image

        Returns:
            Denoised image
        """
        # Apply a bilateral filter to remove noise while preserving edges
        denoised = cv2.bilateralFilter(image, 9, 75, 75)

        return denoised

    def _binarize(self, image: np.ndarray) -> np.ndarray:
        """
        Binarize an image.

        Args:
            image: Input grayscale image

        Returns:
            Binarized image
        """
        # Apply Otsu's thresholding
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return binary

    def detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect text regions in an image.

        Args:
            image: Input image

        Returns:
            List of text regions as (x, y, width, height) tuples
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply Otsu's thresholding
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Apply morphological operations to connect nearby text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3))
        dilated = cv2.dilate(binary, kernel, iterations=3)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by size
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out very small regions
            if w > 20 and h > 10:
                text_regions.append((x, y, w, h))

        return text_regions

    def crop_text_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect and crop text regions from an image.

        Args:
            image: Input image

        Returns:
            List of dictionaries with cropped text regions
        """
        # Detect text regions
        regions = self.detect_text_regions(image)

        # Crop each region
        cropped_regions = []
        for i, (x, y, w, h) in enumerate(regions):
            # Add some padding
            pad = 5
            x_start = max(0, x - pad)
            y_start = max(0, y - pad)
            x_end = min(image.shape[1], x + w + pad)
            y_end = min(image.shape[0], y + h + pad)

            # Crop the region
            cropped = image[y_start:y_end, x_start:x_end]

            cropped_regions.append({
                'id': i,
                'region': (x, y, w, h),
                'padded_region': (x_start, y_start, x_end - x_start, y_end - y_start),
                'image': cropped
            })

        return cropped_regions
