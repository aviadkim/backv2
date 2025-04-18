"""
Output Generator Module

This module provides structured output generation with error handling.
It ensures consistent and valid JSON output for financial data.
"""

import os
import logging
import json
import jsonschema
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OutputGenerator:
    """
    Structured output generation with error handling.
    Ensures consistent and valid JSON output for financial data.
    """
    
    def __init__(self):
        """
        Initialize the OutputGenerator.
        """
        # Define schema for financial document output
        self.schema = {
            "type": "object",
            "properties": {
                "portfolio": {
                    "type": "object",
                    "properties": {
                        "total_value": {"type": "number"},
                        "currency": {"type": "string"},
                        "securities": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "isin": {"type": "string", "pattern": "^[A-Z]{2}[A-Z0-9]{9}[0-9]$"},
                                    "name": {"type": "string"},
                                    "quantity": {"type": "number"},
                                    "price": {"type": "number"},
                                    "value": {"type": "number"},
                                    "currency": {"type": "string"},
                                    "asset_class": {"type": "string"}
                                },
                                "required": ["isin"]
                            }
                        },
                        "asset_allocation": {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "number"},
                                    "weight": {"type": "number"}
                                }
                            }
                        }
                    },
                    "required": ["securities"]
                },
                "metrics": {
                    "type": "object",
                    "properties": {
                        "total_securities": {"type": "number"},
                        "total_asset_classes": {"type": "number"},
                        "performance_twr": {"type": "number"},
                        "performance_ytd": {"type": "number"},
                        "cash_accounts_value": {"type": "number"},
                        "accrued_interest": {"type": "number"},
                        "collected_income": {"type": "number"}
                    }
                },
                "document_info": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "document_name": {"type": "string"},
                        "document_date": {"type": "string"},
                        "processing_date": {"type": "string"},
                        "processing_time": {"type": "number"}
                    }
                }
            },
            "required": ["portfolio"]
        }
        
        logger.info("Initialized OutputGenerator")
    
    def generate_output(self, financial_data: Dict[str, Any], 
                       document_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate structured output from financial data.
        
        Args:
            financial_data: Extracted financial data
            document_info: Optional document information
            
        Returns:
            Structured output
        """
        logger.info("Generating structured output")
        
        # Create a deep copy to avoid modifying the input
        output = self._deep_copy(financial_data)
        
        # Add document info if provided
        if document_info:
            output["document_info"] = document_info
        
        # Ensure required structure
        output = self._ensure_structure(output)
        
        # Calculate metrics
        output = self._calculate_metrics(output)
        
        # Validate against schema
        output = self._validate_and_fix(output)
        
        logger.info("Output generation complete")
        
        return output
    
    def save_output(self, output: Dict[str, Any], output_path: str) -> None:
        """
        Save output to a file.
        
        Args:
            output: Structured output
            output_path: Path to save the output
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Output saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving output: {e}")
            raise
    
    def _deep_copy(self, data: Any) -> Any:
        """
        Create a deep copy of data.
        
        Args:
            data: Data to copy
            
        Returns:
            Deep copy of data
        """
        if isinstance(data, dict):
            return {k: self._deep_copy(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._deep_copy(item) for item in data]
        else:
            return data
    
    def _ensure_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure the output has the required structure.
        
        Args:
            data: Output data
            
        Returns:
            Structured output
        """
        # Ensure portfolio exists
        if "portfolio" not in data:
            data["portfolio"] = {}
        
        # Ensure securities exists
        if "securities" not in data["portfolio"]:
            # Check if securities is at the top level
            if "securities" in data:
                data["portfolio"]["securities"] = data.pop("securities")
            else:
                data["portfolio"]["securities"] = []
        
        # Ensure asset_allocation exists
        if "asset_allocation" not in data["portfolio"]:
            # Check if asset_allocation is at the top level
            if "asset_allocation" in data:
                data["portfolio"]["asset_allocation"] = data.pop("asset_allocation")
            else:
                data["portfolio"]["asset_allocation"] = {}
        
        # Ensure total_value and currency exist
        if "total_value" not in data["portfolio"]:
            # Check if total_value is at the top level
            if "total_value" in data:
                data["portfolio"]["total_value"] = data.pop("total_value")
        
        if "currency" not in data["portfolio"]:
            # Check if currency is at the top level
            if "currency" in data:
                data["portfolio"]["currency"] = data.pop("currency")
        
        # Ensure metrics exists
        if "metrics" not in data:
            data["metrics"] = {}
        
        return data
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate metrics from financial data.
        
        Args:
            data: Output data
            
        Returns:
            Output with calculated metrics
        """
        # Calculate total_securities
        securities = data["portfolio"].get("securities", [])
        data["metrics"]["total_securities"] = len(securities)
        
        # Calculate total_asset_classes
        asset_allocation = data["portfolio"].get("asset_allocation", {})
        data["metrics"]["total_asset_classes"] = len(asset_allocation)
        
        # Calculate total_value if not present
        if "total_value" not in data["portfolio"] or data["portfolio"]["total_value"] is None:
            total_value = sum(security.get("value", 0) for security in securities)
            if total_value > 0:
                data["portfolio"]["total_value"] = total_value
        
        # Calculate asset allocation values and weights if not present
        if asset_allocation:
            total_value = data["portfolio"].get("total_value", 0)
            
            for asset_class, allocation in asset_allocation.items():
                # Calculate value if not present
                if "value" not in allocation:
                    # Sum values of securities in this asset class
                    class_securities = [s for s in securities if s.get("asset_class") == asset_class]
                    class_value = sum(s.get("value", 0) for s in class_securities)
                    
                    if class_value > 0:
                        allocation["value"] = class_value
                
                # Calculate weight if not present
                if "weight" not in allocation and "value" in allocation and total_value > 0:
                    allocation["weight"] = allocation["value"] / total_value
        
        return data
    
    def _validate_and_fix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate output against schema and fix issues.
        
        Args:
            data: Output data
            
        Returns:
            Validated and fixed output
        """
        try:
            # Validate against schema
            jsonschema.validate(instance=data, schema=self.schema)
            logger.info("Output validation successful")
            return data
        except jsonschema.exceptions.ValidationError as e:
            logger.warning(f"Output validation failed: {e}")
            
            # Try to fix the issue
            fixed_data = self._fix_validation_error(data, e)
            
            # Validate again
            try:
                jsonschema.validate(instance=fixed_data, schema=self.schema)
                logger.info("Output validation successful after fixing")
                return fixed_data
            except jsonschema.exceptions.ValidationError as e2:
                logger.error(f"Output validation failed after fixing: {e2}")
                
                # Return the best we can
                return fixed_data
    
    def _fix_validation_error(self, data: Dict[str, Any], 
                             error: jsonschema.exceptions.ValidationError) -> Dict[str, Any]:
        """
        Fix validation error.
        
        Args:
            data: Output data
            error: Validation error
            
        Returns:
            Fixed output
        """
        # Get error path
        path = list(error.path)
        
        # Get error message
        message = error.message
        
        logger.info(f"Fixing validation error at {path}: {message}")
        
        # Handle different types of errors
        if "is not of type" in message:
            # Type error
            return self._fix_type_error(data, path, message)
        elif "is not valid under any of the given schemas" in message:
            # Schema error
            return self._fix_schema_error(data, path)
        elif "is a required property" in message:
            # Missing property
            return self._fix_missing_property(data, path, message)
        elif "does not match" in message and "pattern" in message:
            # Pattern error
            return self._fix_pattern_error(data, path, message)
        else:
            # Unknown error
            logger.warning(f"Unknown validation error: {message}")
            return data
    
    def _fix_type_error(self, data: Dict[str, Any], path: List[str], 
                       message: str) -> Dict[str, Any]:
        """
        Fix type error.
        
        Args:
            data: Output data
            path: Error path
            message: Error message
            
        Returns:
            Fixed output
        """
        # Get expected type
        import re
        match = re.search(r"is not of type '([^']+)'", message)
        if not match:
            return data
        
        expected_type = match.group(1)
        
        # Navigate to the parent of the error
        parent = data
        for i in range(len(path) - 1):
            key = path[i]
            if isinstance(parent, dict) and key in parent:
                parent = parent[key]
            elif isinstance(parent, list) and isinstance(key, int) and key < len(parent):
                parent = parent[key]
            else:
                return data
        
        # Get the key of the error
        key = path[-1]
        
        # Fix the value
        if isinstance(parent, dict) and key in parent:
            value = parent[key]
            
            if expected_type == "number":
                # Convert to number
                try:
                    if isinstance(value, str):
                        # Remove non-numeric characters
                        numeric_value = ''.join(c for c in value if c.isdigit() or c == '.')
                        parent[key] = float(numeric_value)
                    else:
                        parent[key] = float(value)
                except (ValueError, TypeError):
                    # Remove invalid value
                    del parent[key]
            elif expected_type == "string":
                # Convert to string
                try:
                    parent[key] = str(value)
                except (ValueError, TypeError):
                    # Remove invalid value
                    del parent[key]
            elif expected_type == "array":
                # Convert to array
                if value is None:
                    parent[key] = []
                else:
                    # Remove invalid value
                    del parent[key]
            elif expected_type == "object":
                # Convert to object
                if value is None:
                    parent[key] = {}
                else:
                    # Remove invalid value
                    del parent[key]
        
        return data
    
    def _fix_schema_error(self, data: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
        """
        Fix schema error.
        
        Args:
            data: Output data
            path: Error path
            
        Returns:
            Fixed output
        """
        # Navigate to the parent of the error
        parent = data
        for i in range(len(path) - 1):
            key = path[i]
            if isinstance(parent, dict) and key in parent:
                parent = parent[key]
            elif isinstance(parent, list) and isinstance(key, int) and key < len(parent):
                parent = parent[key]
            else:
                return data
        
        # Get the key of the error
        key = path[-1]
        
        # Fix the value
        if isinstance(parent, dict) and key in parent:
            # Remove invalid value
            del parent[key]
        elif isinstance(parent, list) and isinstance(key, int) and key < len(parent):
            # Remove invalid item
            parent.pop(key)
        
        return data
    
    def _fix_missing_property(self, data: Dict[str, Any], path: List[str], 
                             message: str) -> Dict[str, Any]:
        """
        Fix missing property error.
        
        Args:
            data: Output data
            path: Error path
            message: Error message
            
        Returns:
            Fixed output
        """
        # Get missing property
        import re
        match = re.search(r"'([^']+)' is a required property", message)
        if not match:
            return data
        
        missing_property = match.group(1)
        
        # Navigate to the parent of the error
        parent = data
        for key in path:
            if isinstance(parent, dict) and key in parent:
                parent = parent[key]
            elif isinstance(parent, list) and isinstance(key, int) and key < len(parent):
                parent = parent[key]
            else:
                return data
        
        # Add missing property
        if isinstance(parent, dict):
            if missing_property == "isin":
                # Generate a placeholder ISIN
                parent[missing_property] = "XX0000000000"
            elif missing_property == "securities":
                parent[missing_property] = []
            else:
                parent[missing_property] = None
        
        return data
    
    def _fix_pattern_error(self, data: Dict[str, Any], path: List[str], 
                          message: str) -> Dict[str, Any]:
        """
        Fix pattern error.
        
        Args:
            data: Output data
            path: Error path
            message: Error message
            
        Returns:
            Fixed output
        """
        # Navigate to the parent of the error
        parent = data
        for i in range(len(path) - 1):
            key = path[i]
            if isinstance(parent, dict) and key in parent:
                parent = parent[key]
            elif isinstance(parent, list) and isinstance(key, int) and key < len(parent):
                parent = parent[key]
            else:
                return data
        
        # Get the key of the error
        key = path[-1]
        
        # Fix the value
        if isinstance(parent, dict) and key in parent:
            value = parent[key]
            
            if key == "isin" and isinstance(value, str):
                # Fix ISIN pattern
                if len(value) != 12:
                    # Invalid length, replace with placeholder
                    parent[key] = "XX0000000000"
                elif not value[:2].isalpha():
                    # Invalid country code, replace with placeholder
                    parent[key] = "XX" + value[2:]
                elif not value[2:].isalnum():
                    # Invalid characters, replace with placeholder
                    parent[key] = value[:2] + "0000000000"
                else:
                    # Ensure uppercase
                    parent[key] = value.upper()
        
        return data


# Example usage
if __name__ == "__main__":
    # This will only run when the script is executed directly
    import sys
    import json
    
    if len(sys.argv) > 2:
        input_path = sys.argv[1]
        output_path = sys.argv[2]
        
        # Load input data
        with open(input_path, 'r') as f:
            input_data = json.load(f)
        
        # Create generator
        generator = OutputGenerator()
        
        # Generate output
        output = generator.generate_output(input_data)
        
        # Save output
        generator.save_output(output, output_path)
        
        print(f"Output saved to {output_path}")
    else:
        print("Please provide input and output file paths")
