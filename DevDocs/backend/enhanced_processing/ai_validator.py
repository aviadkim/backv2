"""
AI Validator Module

This module provides AI-enhanced validation for financial data extraction.
It uses LlamaIndex and AI models to validate and enhance extracted data.
"""

import os
import logging
import json
import tempfile
from typing import List, Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIValidator:
    """
    AI-enhanced validation for financial data extraction.
    Uses LlamaIndex and AI models to validate and enhance extracted data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the AIValidator.
        
        Args:
            api_key: API key for AI service (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY') or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("No API key provided, AI validation will be limited")
        
        logger.info("Initialized AIValidator")
    
    def validate_financial_data(self, financial_data: Dict[str, Any], 
                               extracted_text: str) -> Dict[str, Any]:
        """
        Validate and enhance financial data using AI.
        
        Args:
            financial_data: Extracted financial data
            extracted_text: Raw text extracted from the document
            
        Returns:
            Validated and enhanced financial data
        """
        logger.info("Validating financial data with AI")
        
        # Check if we have an API key
        if not self.api_key:
            logger.warning("No API key available, skipping AI validation")
            return financial_data
        
        # Validate securities
        if 'securities' in financial_data:
            financial_data['securities'] = self._validate_securities(
                financial_data['securities'], extracted_text
            )
        
        # Validate asset allocation
        if 'asset_allocation' in financial_data:
            financial_data['asset_allocation'] = self._validate_asset_allocation(
                financial_data['asset_allocation'], extracted_text
            )
        
        # Validate total value
        if 'total_value' in financial_data:
            financial_data['total_value'], financial_data['currency'] = self._validate_total_value(
                financial_data.get('total_value'), 
                financial_data.get('currency'),
                extracted_text
            )
        
        # Check for missing ISINs
        financial_data = self._check_for_missing_isins(financial_data, extracted_text)
        
        # Ensure data consistency
        financial_data = self._ensure_data_consistency(financial_data)
        
        logger.info("AI validation complete")
        
        return financial_data
    
    def _validate_securities(self, securities: List[Dict[str, Any]], 
                            extracted_text: str) -> List[Dict[str, Any]]:
        """
        Validate and enhance securities data.
        
        Args:
            securities: List of securities
            extracted_text: Raw text extracted from the document
            
        Returns:
            Validated and enhanced securities data
        """
        logger.info(f"Validating {len(securities)} securities")
        
        # Check if we have enough securities
        if len(securities) < 10:
            # Try to extract more securities using AI
            additional_securities = self._extract_additional_securities(extracted_text, securities)
            securities.extend(additional_securities)
            logger.info(f"Added {len(additional_securities)} additional securities")
        
        # Validate each security
        validated_securities = []
        
        for security in securities:
            # Skip if no ISIN
            if 'isin' not in security:
                continue
            
            # Validate security data
            validated_security = self._validate_security(security, extracted_text)
            validated_securities.append(validated_security)
        
        # Remove duplicates
        unique_securities = self._remove_duplicate_securities(validated_securities)
        
        logger.info(f"Validated {len(unique_securities)} unique securities")
        
        return unique_securities
    
    def _validate_security(self, security: Dict[str, Any], 
                          extracted_text: str) -> Dict[str, Any]:
        """
        Validate and enhance a single security.
        
        Args:
            security: Security data
            extracted_text: Raw text extracted from the document
            
        Returns:
            Validated and enhanced security data
        """
        # Create a copy to avoid modifying the original
        validated_security = security.copy()
        
        # Check if we have an ISIN
        if 'isin' not in validated_security:
            return validated_security
        
        isin = validated_security['isin']
        
        # Find context around this ISIN in the extracted text
        isin_index = extracted_text.find(isin)
        if isin_index >= 0:
            context_start = max(0, isin_index - 200)
            context_end = min(len(extracted_text), isin_index + 200)
            context = extracted_text[context_start:context_end]
            
            # Use AI to extract missing information from context
            missing_fields = []
            
            if 'name' not in validated_security or not validated_security['name']:
                missing_fields.append('name')
            
            if 'quantity' not in validated_security:
                missing_fields.append('quantity')
            
            if 'price' not in validated_security:
                missing_fields.append('price')
            
            if 'value' not in validated_security:
                missing_fields.append('value')
            
            if 'asset_class' not in validated_security:
                missing_fields.append('asset_class')
            
            if missing_fields:
                # Use AI to extract missing fields
                extracted_fields = self._extract_fields_with_ai(
                    isin, context, missing_fields
                )
                
                # Update security with extracted fields
                for field, value in extracted_fields.items():
                    if field in missing_fields and value is not None:
                        validated_security[field] = value
        
        # Ensure consistency
        if 'quantity' in validated_security and 'price' in validated_security and 'value' not in validated_security:
            # Calculate value from quantity and price
            validated_security['value'] = validated_security['quantity'] * validated_security['price']
        
        if 'quantity' in validated_security and 'value' in validated_security and 'price' not in validated_security:
            # Calculate price from quantity and value
            if validated_security['quantity'] > 0:
                validated_security['price'] = validated_security['value'] / validated_security['quantity']
        
        return validated_security
    
    def _extract_fields_with_ai(self, isin: str, context: str, 
                               fields: List[str]) -> Dict[str, Any]:
        """
        Extract fields from context using AI.
        
        Args:
            isin: ISIN code
            context: Text context around the ISIN
            fields: List of fields to extract
            
        Returns:
            Dictionary with extracted fields
        """
        # Prepare prompt for AI
        prompt = f"""
Extract the following information for the security with ISIN {isin} from this financial document text:
{', '.join(fields)}

Text context:
{context}

Format your response as a JSON object with the following fields:
{json.dumps({field: None for field in fields}, indent=2)}

If you cannot find a value for a field, leave it as null.
"""
        
        try:
            # Call AI API
            response = self._call_ai_api(prompt)
            
            # Parse response
            extracted_fields = {}
            
            try:
                # Try to parse as JSON
                json_match = self._extract_json_from_text(response)
                if json_match:
                    extracted_fields = json.loads(json_match)
                else:
                    # Parse manually
                    for field in fields:
                        field_match = self._extract_field_from_text(response, field)
                        if field_match:
                            extracted_fields[field] = field_match
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response}")
                # Parse manually
                for field in fields:
                    field_match = self._extract_field_from_text(response, field)
                    if field_match:
                        extracted_fields[field] = field_match
            
            return extracted_fields
        except Exception as e:
            logger.error(f"Error extracting fields with AI: {e}")
            return {}
    
    def _extract_additional_securities(self, extracted_text: str, 
                                      existing_securities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract additional securities using AI.
        
        Args:
            extracted_text: Raw text extracted from the document
            existing_securities: List of already extracted securities
            
        Returns:
            List of additional securities
        """
        # Get existing ISINs
        existing_isins = [s['isin'] for s in existing_securities if 'isin' in s]
        
        # Prepare prompt for AI
        prompt = f"""
Extract all securities from this financial document text that are not already in the list of existing ISINs.
For each security, extract the ISIN, name, quantity, price, value, currency, and asset class.

Existing ISINs:
{', '.join(existing_isins)}

Text:
{extracted_text[:5000]}  # Limit text length to avoid token limits

Format your response as a JSON array of objects, each with the following fields:
- isin: ISIN code (12 characters, starting with 2 letters)
- name: Security name
- quantity: Quantity/nominal value
- price: Price per unit
- value: Total value
- currency: Currency code (e.g., USD, EUR)
- asset_class: Asset class (e.g., Bonds, Equities, Structured products)

Only include securities that have a valid ISIN and are not in the list of existing ISINs.
"""
        
        try:
            # Call AI API
            response = self._call_ai_api(prompt)
            
            # Parse response
            additional_securities = []
            
            try:
                # Try to parse as JSON
                json_match = self._extract_json_from_text(response)
                if json_match:
                    parsed_securities = json.loads(json_match)
                    
                    # Validate each security
                    for security in parsed_securities:
                        if 'isin' in security and security['isin'] not in existing_isins:
                            additional_securities.append(security)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response}")
            
            return additional_securities
        except Exception as e:
            logger.error(f"Error extracting additional securities with AI: {e}")
            return []
    
    def _validate_asset_allocation(self, asset_allocation: Dict[str, Dict[str, float]], 
                                  extracted_text: str) -> Dict[str, Dict[str, float]]:
        """
        Validate and enhance asset allocation data.
        
        Args:
            asset_allocation: Asset allocation data
            extracted_text: Raw text extracted from the document
            
        Returns:
            Validated and enhanced asset allocation data
        """
        logger.info(f"Validating asset allocation with {len(asset_allocation)} classes")
        
        # Check if we have the expected asset classes
        expected_classes = ['Liquidity', 'Bonds', 'Equities', 'Structured products', 'Other assets']
        missing_classes = [cls for cls in expected_classes if cls not in asset_allocation]
        
        if missing_classes:
            # Try to extract missing asset classes using AI
            extracted_allocation = self._extract_asset_allocation_with_ai(
                extracted_text, missing_classes
            )
            
            # Update asset allocation with extracted classes
            for asset_class, data in extracted_allocation.items():
                if asset_class not in asset_allocation:
                    asset_allocation[asset_class] = data
        
        # Ensure weights sum to 100%
        total_weight = sum(data.get('weight', 0) for data in asset_allocation.values())
        
        if abs(total_weight - 1.0) > 0.01:  # Allow small rounding errors
            # Normalize weights
            for asset_class in asset_allocation:
                if 'weight' in asset_allocation[asset_class]:
                    asset_allocation[asset_class]['weight'] /= total_weight
        
        return asset_allocation
    
    def _extract_asset_allocation_with_ai(self, extracted_text: str, 
                                         missing_classes: List[str]) -> Dict[str, Dict[str, float]]:
        """
        Extract asset allocation using AI.
        
        Args:
            extracted_text: Raw text extracted from the document
            missing_classes: List of missing asset classes
            
        Returns:
            Dictionary with extracted asset allocation
        """
        # Prepare prompt for AI
        prompt = f"""
Extract the asset allocation for the following asset classes from this financial document text:
{', '.join(missing_classes)}

For each asset class, extract the value and weight (percentage).

Text:
{extracted_text[:5000]}  # Limit text length to avoid token limits

Format your response as a JSON object with the following structure:
{{
  "asset_class_name": {{
    "value": numeric_value,
    "weight": percentage_as_decimal
  }},
  ...
}}

For example:
{{
  "Bonds": {{
    "value": 1000000,
    "weight": 0.5
  }}
}}

Ensure that weights are expressed as decimals (e.g., 0.5 for 50%).
If you cannot find a value or weight for an asset class, provide your best estimate based on the context.
"""
        
        try:
            # Call AI API
            response = self._call_ai_api(prompt)
            
            # Parse response
            extracted_allocation = {}
            
            try:
                # Try to parse as JSON
                json_match = self._extract_json_from_text(response)
                if json_match:
                    extracted_allocation = json.loads(json_match)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response}")
            
            return extracted_allocation
        except Exception as e:
            logger.error(f"Error extracting asset allocation with AI: {e}")
            return {}
    
    def _validate_total_value(self, total_value: Optional[float], 
                             currency: Optional[str],
                             extracted_text: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Validate and enhance total value and currency.
        
        Args:
            total_value: Total portfolio value
            currency: Currency code
            extracted_text: Raw text extracted from the document
            
        Returns:
            Tuple of (validated_total_value, validated_currency)
        """
        logger.info(f"Validating total value: {total_value} {currency}")
        
        if total_value is None or currency is None:
            # Try to extract total value and currency using AI
            extracted_total, extracted_currency = self._extract_total_value_with_ai(extracted_text)
            
            if total_value is None and extracted_total is not None:
                total_value = extracted_total
            
            if currency is None and extracted_currency is not None:
                currency = extracted_currency
        
        return total_value, currency
    
    def _extract_total_value_with_ai(self, extracted_text: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Extract total value and currency using AI.
        
        Args:
            extracted_text: Raw text extracted from the document
            
        Returns:
            Tuple of (total_value, currency)
        """
        # Prepare prompt for AI
        prompt = f"""
Extract the total portfolio value and currency from this financial document text.
Look for phrases like "Total", "Total Value", "Portfolio Value", etc.

Text:
{extracted_text[:5000]}  # Limit text length to avoid token limits

Format your response as a JSON object with the following fields:
{{
  "total_value": numeric_value,
  "currency": currency_code
}}

For example:
{{
  "total_value": 1000000,
  "currency": "USD"
}}
"""
        
        try:
            # Call AI API
            response = self._call_ai_api(prompt)
            
            # Parse response
            total_value = None
            currency = None
            
            try:
                # Try to parse as JSON
                json_match = self._extract_json_from_text(response)
                if json_match:
                    parsed_data = json.loads(json_match)
                    total_value = parsed_data.get('total_value')
                    currency = parsed_data.get('currency')
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse AI response as JSON: {response}")
                
                # Try to extract manually
                import re
                
                # Look for total value
                value_match = re.search(r'total_value"?\s*:\s*(\d[\d,\.]*)', response)
                if value_match:
                    try:
                        total_value = float(value_match.group(1).replace(',', ''))
                    except ValueError:
                        pass
                
                # Look for currency
                currency_match = re.search(r'currency"?\s*:\s*"([A-Z]{3})"', response)
                if currency_match:
                    currency = currency_match.group(1)
            
            return total_value, currency
        except Exception as e:
            logger.error(f"Error extracting total value with AI: {e}")
            return None, None
    
    def _check_for_missing_isins(self, financial_data: Dict[str, Any], 
                                extracted_text: str) -> Dict[str, Any]:
        """
        Check for missing ISINs in the extracted data.
        
        Args:
            financial_data: Extracted financial data
            extracted_text: Raw text extracted from the document
            
        Returns:
            Updated financial data with additional ISINs
        """
        # Extract all ISINs from the text
        import re
        isin_pattern = r'[A-Z]{2}[A-Z0-9]{9}[0-9]'
        text_isins = re.findall(isin_pattern, extracted_text)
        
        # Get existing ISINs
        existing_isins = [s['isin'] for s in financial_data.get('securities', []) if 'isin' in s]
        
        # Find missing ISINs
        missing_isins = [isin for isin in text_isins if isin not in existing_isins]
        
        if missing_isins:
            logger.info(f"Found {len(missing_isins)} missing ISINs")
            
            # Add missing ISINs to securities
            for isin in missing_isins:
                # Find context around this ISIN
                isin_index = extracted_text.find(isin)
                context = ""
                
                if isin_index >= 0:
                    context_start = max(0, isin_index - 200)
                    context_end = min(len(extracted_text), isin_index + 200)
                    context = extracted_text[context_start:context_end]
                
                # Extract security information
                security = {
                    'isin': isin
                }
                
                # Use AI to extract additional information
                extracted_fields = self._extract_fields_with_ai(
                    isin, context, ['name', 'quantity', 'price', 'value', 'currency', 'asset_class']
                )
                
                # Update security with extracted fields
                for field, value in extracted_fields.items():
                    if value is not None:
                        security[field] = value
                
                # Add to securities list
                if 'securities' not in financial_data:
                    financial_data['securities'] = []
                
                financial_data['securities'].append(security)
        
        return financial_data
    
    def _ensure_data_consistency(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure consistency in the financial data.
        
        Args:
            financial_data: Extracted financial data
            
        Returns:
            Consistent financial data
        """
        # Check if securities list exists
        if 'securities' not in financial_data:
            return financial_data
        
        # Calculate total value from securities
        securities_total = sum(s.get('value', 0) for s in financial_data['securities'])
        
        # Compare with reported total value
        reported_total = financial_data.get('total_value')
        
        if reported_total is not None and securities_total > 0:
            # If the difference is significant, adjust security values
            if abs(reported_total - securities_total) / reported_total > 0.1:  # More than 10% difference
                logger.warning(f"Significant difference between reported total ({reported_total}) "
                              f"and sum of securities ({securities_total})")
                
                # Adjust security values proportionally
                adjustment_factor = reported_total / securities_total
                
                for security in financial_data['securities']:
                    if 'value' in security:
                        security['value'] *= adjustment_factor
                        
                        # Also adjust price if quantity is available
                        if 'quantity' in security and security['quantity'] > 0:
                            security['price'] = security['value'] / security['quantity']
        
        # Ensure asset allocation percentages sum to 100%
        if 'asset_allocation' in financial_data:
            total_weight = sum(data.get('weight', 0) for data in financial_data['asset_allocation'].values())
            
            if abs(total_weight - 1.0) > 0.01:  # Allow small rounding errors
                # Normalize weights
                for asset_class in financial_data['asset_allocation']:
                    if 'weight' in financial_data['asset_allocation'][asset_class]:
                        financial_data['asset_allocation'][asset_class]['weight'] /= total_weight
        
        return financial_data
    
    def _call_ai_api(self, prompt: str) -> str:
        """
        Call AI API with a prompt.
        
        Args:
            prompt: Prompt for the AI
            
        Returns:
            AI response
            
        Raises:
            Exception: If API call fails
        """
        # Check if we're using Google API
        if 'GOOGLE_API_KEY' in os.environ or (self.api_key and len(self.api_key) > 30 and self.api_key.startswith('AIza')):
            return self._call_google_ai_api(prompt)
        else:
            # Default to OpenAI
            return self._call_openai_api(prompt)
    
    def _call_google_ai_api(self, prompt: str) -> str:
        """
        Call Google AI API with a prompt.
        
        Args:
            prompt: Prompt for the AI
            
        Returns:
            AI response
            
        Raises:
            Exception: If API call fails
        """
        api_key = self.api_key or os.getenv('GOOGLE_API_KEY')
        
        if not api_key:
            raise ValueError("No Google API key available")
        
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2000
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
        
        response_json = response.json()
        
        if 'candidates' in response_json and len(response_json['candidates']) > 0:
            candidate = response_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
                return candidate['content']['parts'][0]['text']
        
        raise Exception(f"Unexpected API response format: {response_json}")
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call OpenAI API with a prompt.
        
        Args:
            prompt: Prompt for the AI
            
        Returns:
            AI response
            
        Raises:
            Exception: If API call fails
        """
        api_key = self.api_key or os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("No OpenAI API key available")
        
        url = "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a financial document analysis expert. Extract information accurately and format as requested."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 2000
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}: {response.text}")
        
        response_json = response.json()
        
        if 'choices' in response_json and len(response_json['choices']) > 0:
            return response_json['choices'][0]['message']['content']
        
        raise Exception(f"Unexpected API response format: {response_json}")
    
    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON from text.
        
        Args:
            text: Text containing JSON
            
        Returns:
            Extracted JSON string, or None if not found
        """
        # Look for JSON between triple backticks
        import re
        
        # Pattern 1: JSON between ```json and ```
        pattern1 = r'```json\n([\s\S]*?)\n```'
        match = re.search(pattern1, text)
        if match:
            return match.group(1)
        
        # Pattern 2: JSON between ``` and ```
        pattern2 = r'```\n([\s\S]*?)\n```'
        match = re.search(pattern2, text)
        if match:
            return match.group(1)
        
        # Pattern 3: JSON object or array
        pattern3 = r'(\{[\s\S]*\}|\[[\s\S]*\])'
        match = re.search(pattern3, text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_field_from_text(self, text: str, field: str) -> Any:
        """
        Extract a field value from text.
        
        Args:
            text: Text containing field
            field: Field name
            
        Returns:
            Extracted field value, or None if not found
        """
        import re
        
        # Pattern: field: value or "field": value
        pattern = rf'["\']?{field}["\']?\s*:\s*([^,\n\}]+)'
        match = re.search(pattern, text, re.IGNORECASE)
        
        if match:
            value_str = match.group(1).strip()
            
            # Remove quotes if present
            if (value_str.startswith('"') and value_str.endswith('"')) or \
               (value_str.startswith("'") and value_str.endswith("'")):
                value_str = value_str[1:-1]
            
            # Convert to appropriate type
            if value_str.lower() == 'null' or value_str.lower() == 'none':
                return None
            
            try:
                # Try as number
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                # Return as string
                return value_str
        
        return None
    
    def _remove_duplicate_securities(self, securities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate securities based on ISIN.
        
        Args:
            securities: List of securities
            
        Returns:
            List of unique securities
        """
        # Create a map of ISINs to securities
        isin_to_security = {}
        
        for security in securities:
            if 'isin' in security:
                isin = security['isin']
                
                if isin in isin_to_security:
                    # Merge with existing security
                    existing = isin_to_security[isin]
                    
                    # Keep non-null values
                    for field, value in security.items():
                        if field not in existing or existing[field] is None:
                            existing[field] = value
                else:
                    # Add new security
                    isin_to_security[isin] = security.copy()
        
        # Convert back to list
        return list(isin_to_security.values())


# Example usage
if __name__ == "__main__":
    # This will only run when the script is executed directly
    import sys
    import json
    
    if len(sys.argv) > 2:
        financial_data_path = sys.argv[1]
        extracted_text_path = sys.argv[2]
        
        # Load financial data
        with open(financial_data_path, 'r') as f:
            financial_data = json.load(f)
        
        # Load extracted text
        with open(extracted_text_path, 'r') as f:
            extracted_text = f.read()
        
        # Create validator
        validator = AIValidator()
        
        # Validate financial data
        validated_data = validator.validate_financial_data(financial_data, extracted_text)
        
        # Print results
        print(json.dumps(validated_data, indent=2))
    else:
        print("Please provide paths to financial data JSON and extracted text")
