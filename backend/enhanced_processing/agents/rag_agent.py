"""
RAG Agent for the RAG Multimodal Financial Document Processor.
"""

import os
import json
import logging
import requests
import re
from typing import List, Dict, Any, Optional, Tuple
import base64
from PIL import Image
import io

from ..utils import ensure_dir

logger = logging.getLogger(__name__)

class RAGAgent:
    """
    RAG Agent for validating and enhancing financial data using AI.
    """
    
    def __init__(self, config):
        """
        Initialize the RAG Agent.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.rag_config = config["rag"]
        self.output_config = config["output"]
        
        # Get API keys
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Determine which API to use
        self.api_type = "openai" if self.openai_api_key else "google" if self.google_api_key else None
        
        if not self.api_type:
            logger.warning("No API key found for OpenAI or Google. RAG validation will be skipped.")
        
        logger.info(f"Initialized RAG Agent using {self.api_type} API")
    
    def process(self, ocr_results: Dict[str, Any], financial_results: Dict[str, Any], 
               pdf_path: str, output_dir: str) -> Dict[str, Any]:
        """
        Process financial data with RAG for validation and enhancement.
        
        Args:
            ocr_results: OCR results
            financial_results: Financial analysis results
            pdf_path: Path to the PDF file
            output_dir: Output directory
            
        Returns:
            Dictionary with RAG validation results
        """
        logger.info("Validating financial data with RAG")
        
        # Create output directory
        rag_dir = os.path.join(output_dir, "rag")
        ensure_dir(rag_dir)
        
        # Skip if no API key
        if not self.api_type:
            logger.warning("Skipping RAG validation due to missing API keys")
            return {
                "validated_data": financial_results["financial_data"],
                "rag_dir": rag_dir
            }
        
        # Convert PDF to images
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=150)
        except Exception as e:
            logger.warning(f"Error converting PDF to images: {e}")
            try:
                import fitz
                doc = fitz.open(pdf_path)
                images = []
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    images.append(img)
            except Exception as e2:
                logger.error(f"Error converting PDF to images with PyMuPDF: {e2}")
                images = []
        
        # Save images
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(rag_dir, f"page_{i+1}.jpg")
            image.save(image_path, "JPEG")
            image_paths.append(image_path)
        
        # Validate total value
        total_value, currency = self._validate_total_value(
            financial_results["financial_data"], 
            ocr_results["text"],
            image_paths
        )
        
        # Validate securities
        securities = self._validate_securities(
            financial_results["financial_data"]["securities"],
            ocr_results["text"],
            image_paths
        )
        
        # Validate asset allocation
        asset_allocation = self._validate_asset_allocation(
            financial_results["financial_data"]["asset_allocation"],
            ocr_results["text"],
            image_paths
        )
        
        # Create validated data
        validated_data = {
            "securities": securities,
            "total_value": total_value,
            "currency": currency,
            "asset_allocation": asset_allocation,
            "metrics": financial_results["financial_data"]["metrics"]
        }
        
        # Save results
        with open(os.path.join(rag_dir, "validated_data.json"), "w", encoding="utf-8") as f:
            json.dump(validated_data, f, indent=2, ensure_ascii=False)
        
        logger.info("RAG validation complete")
        
        return {
            "validated_data": validated_data,
            "rag_dir": rag_dir
        }
    
    def _validate_total_value(self, financial_data: Dict[str, Any], 
                             text: str, image_paths: List[str]) -> Tuple[float, str]:
        """
        Validate total portfolio value using RAG.
        
        Args:
            financial_data: Financial data
            text: OCR text
            image_paths: List of image paths
            
        Returns:
            Tuple of (total value, currency)
        """
        logger.info("Validating total portfolio value with RAG")
        
        # Get current values
        current_total = financial_data.get("total_value")
        current_currency = financial_data.get("currency")
        
        # Skip if no API
        if not self.api_type:
            return current_total, current_currency
        
        # Prepare prompt
        prompt = f"""
        You are a financial document analysis expert. I need you to find the total portfolio value in this document.
        
        The document appears to be a financial statement or portfolio report. Look for terms like:
        - "Total Value"
        - "Total Portfolio Value"
        - "Total Assets"
        - "Grand Total"
        
        The current extracted value is: {current_total} {current_currency}
        
        Please analyze the document and:
        1. Find the total portfolio value
        2. Identify the currency
        3. Return the results in JSON format with keys "total_value" and "currency"
        
        If you can't find a clear total value, return the current extracted value.
        """
        
        # Call API
        try:
            response = self._call_vision_api(prompt, image_paths[:3])  # Use first 3 pages
            
            # Parse response
            result = self._parse_json_from_response(response)
            
            if result and "total_value" in result:
                total_value = result["total_value"]
                currency = result.get("currency", current_currency)
                
                # Validate total value
                if isinstance(total_value, (int, float)) and total_value > 0:
                    logger.info(f"RAG validated total value: {total_value} {currency}")
                    return total_value, currency
        except Exception as e:
            logger.error(f"Error validating total value with RAG: {e}")
        
        return current_total, current_currency
    
    def _validate_securities(self, securities: List[Dict[str, Any]], 
                            text: str, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Validate securities using RAG.
        
        Args:
            securities: List of securities
            text: OCR text
            image_paths: List of image paths
            
        Returns:
            Validated list of securities
        """
        logger.info("Validating securities with RAG")
        
        # Skip if no API
        if not self.api_type:
            return securities
        
        # Prepare prompt
        prompt = f"""
        You are a financial document analysis expert. I need you to validate the extracted securities from this document.
        
        I have extracted {len(securities)} securities from the document. Here are the first 5 for reference:
        {json.dumps(securities[:5], indent=2)}
        
        Please analyze the document and:
        1. Verify if the number of securities is correct
        2. Check if any ISINs are missing
        3. Validate the names, quantities, and values
        
        Return your findings in JSON format with the key "validation_result" containing your assessment.
        Do not return the full list of securities, just your validation findings.
        """
        
        # Call API
        try:
            response = self._call_vision_api(prompt, image_paths)
            
            # Parse response
            result = self._parse_json_from_response(response)
            
            if result and "validation_result" in result:
                validation = result["validation_result"]
                logger.info(f"RAG validation result: {validation}")
                
                # TODO: Use validation to improve securities
                # This would require more complex logic to update securities based on validation
        except Exception as e:
            logger.error(f"Error validating securities with RAG: {e}")
        
        return securities
    
    def _validate_asset_allocation(self, asset_allocation: Dict[str, Dict[str, Any]], 
                                  text: str, image_paths: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Validate asset allocation using RAG.
        
        Args:
            asset_allocation: Asset allocation dictionary
            text: OCR text
            image_paths: List of image paths
            
        Returns:
            Validated asset allocation
        """
        logger.info("Validating asset allocation with RAG")
        
        # Skip if no API
        if not self.api_type:
            return asset_allocation
        
        # Prepare prompt
        prompt = f"""
        You are a financial document analysis expert. I need you to validate the extracted asset allocation from this document.
        
        I have extracted the following asset allocation:
        {json.dumps(asset_allocation, indent=2)}
        
        Please analyze the document and:
        1. Verify if the asset classes are correct
        2. Check if any asset classes are missing
        3. Validate the values and weights
        
        Return your findings in JSON format with the key "asset_allocation" containing the corrected asset allocation.
        Each asset class should have "value" and "weight" properties.
        """
        
        # Call API
        try:
            response = self._call_vision_api(prompt, image_paths[:5])  # Use first 5 pages
            
            # Parse response
            result = self._parse_json_from_response(response)
            
            if result and "asset_allocation" in result:
                validated_allocation = result["asset_allocation"]
                
                # Validate structure
                if isinstance(validated_allocation, dict):
                    valid_allocation = True
                    
                    for asset_class, allocation in validated_allocation.items():
                        if not isinstance(allocation, dict) or "value" not in allocation or "weight" not in allocation:
                            valid_allocation = False
                            break
                    
                    if valid_allocation:
                        logger.info(f"RAG validated asset allocation: {validated_allocation}")
                        return validated_allocation
        except Exception as e:
            logger.error(f"Error validating asset allocation with RAG: {e}")
        
        return asset_allocation
    
    def _call_vision_api(self, prompt: str, image_paths: List[str]) -> str:
        """
        Call vision API (OpenAI or Google).
        
        Args:
            prompt: Prompt text
            image_paths: List of image paths
            
        Returns:
            API response text
        """
        if self.api_type == "openai":
            return self._call_openai_vision(prompt, image_paths)
        elif self.api_type == "google":
            return self._call_google_vision(prompt, image_paths)
        else:
            return "No API available"
    
    def _call_openai_vision(self, prompt: str, image_paths: List[str]) -> str:
        """
        Call OpenAI Vision API.
        
        Args:
            prompt: Prompt text
            image_paths: List of image paths
            
        Returns:
            API response text
        """
        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        # Prepare messages
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
        
        # Add images (up to 5)
        for image_path in image_paths[:5]:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                messages[0]["content"].append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                })
        
        # Prepare data
        data = {
            "model": self.rag_config["model"],
            "messages": messages,
            "max_tokens": self.rag_config["max_tokens"],
            "temperature": self.rag_config["temperature"]
        }
        
        # Call API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        # Parse response
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            logger.error(f"OpenAI API error: {response.status_code} {response.text}")
            return ""
    
    def _call_google_vision(self, prompt: str, image_paths: List[str]) -> str:
        """
        Call Google Vision API.
        
        Args:
            prompt: Prompt text
            image_paths: List of image paths
            
        Returns:
            API response text
        """
        # Prepare API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.google_api_key}"
        }
        
        # Prepare content parts
        content_parts = [
            {
                "text": prompt
            }
        ]
        
        # Add images (up to 5)
        for image_path in image_paths[:5]:
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
                content_parts.append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": base64_image
                    }
                })
        
        # Prepare data
        data = {
            "contents": [
                {
                    "parts": content_parts
                }
            ],
            "generationConfig": {
                "temperature": self.rag_config["temperature"],
                "maxOutputTokens": self.rag_config["max_tokens"]
            }
        }
        
        # Call API
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-vision:generateContent",
            headers=headers,
            json=data
        )
        
        # Parse response
        if response.status_code == 200:
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            logger.error(f"Google API error: {response.status_code} {response.text}")
            return ""
    
    def _parse_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON from API response.
        
        Args:
            response: API response text
            
        Returns:
            Parsed JSON or None
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON without markdown
                json_match = re.search(r'(\{.*\})', response, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group(1)
                else:
                    json_str = response
            
            # Parse JSON
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing JSON from response: {e}")
            return None
