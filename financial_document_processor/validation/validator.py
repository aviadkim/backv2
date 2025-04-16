"""
Validator for financial document extraction results.
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExtractionValidator:
    """Validator for financial document extraction results."""
    
    def __init__(self, tolerance: float = 0.05):
        """
        Initialize the validator.
        
        Args:
            tolerance: Tolerance for numerical comparisons (as a fraction)
        """
        self.tolerance = tolerance
        logger.info(f"Initialized extraction validator with tolerance: {tolerance}")
    
    def validate(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extraction results.
        
        Args:
            extraction_result: Extraction results to validate
        
        Returns:
            Dictionary with validation results
        """
        logger.info("Validating extraction results")
        
        validation_results = {
            "portfolio_value": self._validate_portfolio_value(extraction_result),
            "asset_allocation": self._validate_asset_allocation(extraction_result),
            "securities": self._validate_securities(extraction_result),
            "currency": self._validate_currency(extraction_result),
            "risk_profile": self._validate_risk_profile(extraction_result),
            "overall": {
                "valid": True,
                "issues": []
            }
        }
        
        # Check if any validation failed
        for key, result in validation_results.items():
            if key == "overall":
                continue
            
            if not result["valid"]:
                validation_results["overall"]["valid"] = False
                validation_results["overall"]["issues"].extend(result["issues"])
        
        logger.info(f"Validation completed: {'valid' if validation_results['overall']['valid'] else 'invalid'}")
        return validation_results
    
    def _validate_portfolio_value(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate portfolio value."""
        logger.info("Validating portfolio value")
        
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if portfolio value exists
        portfolio_value = extraction_result.get("portfolio_value", {})
        if not portfolio_value or portfolio_value.get("value") is None:
            result["valid"] = False
            result["issues"].append("Portfolio value not found")
            return result
        
        # Check if portfolio value is reasonable
        value = portfolio_value["value"]
        if value <= 0:
            result["valid"] = False
            result["issues"].append(f"Portfolio value is not positive: {value}")
        
        # Check if portfolio value matches sum of asset allocations
        asset_allocations = extraction_result.get("asset_allocation", [])
        if asset_allocations:
            total_value = sum(a.get("value", 0) or 0 for a in asset_allocations)
            if total_value > 0:
                # Calculate relative difference
                relative_diff = abs(total_value - value) / value
                if relative_diff > self.tolerance:
                    result["valid"] = False
                    result["issues"].append(f"Portfolio value ({value}) does not match sum of asset allocations ({total_value}), difference: {relative_diff:.2%}")
        
        # Check if portfolio value matches sum of securities
        securities = extraction_result.get("securities", [])
        if securities:
            total_value = sum(s.get("valuation", 0) or 0 for s in securities)
            if total_value > 0:
                # Calculate relative difference
                relative_diff = abs(total_value - value) / value
                if relative_diff > self.tolerance:
                    result["valid"] = False
                    result["issues"].append(f"Portfolio value ({value}) does not match sum of securities ({total_value}), difference: {relative_diff:.2%}")
        
        return result
    
    def _validate_asset_allocation(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate asset allocation."""
        logger.info("Validating asset allocation")
        
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if asset allocation exists
        asset_allocations = extraction_result.get("asset_allocation", [])
        if not asset_allocations:
            result["valid"] = False
            result["issues"].append("Asset allocation not found")
            return result
        
        # Check if percentages sum to approximately 100%
        total_percentage = sum(a.get("percentage", 0) or 0 for a in asset_allocations)
        if abs(total_percentage - 100) > self.tolerance * 100:
            result["valid"] = False
            result["issues"].append(f"Asset allocation percentages sum to {total_percentage:.2f}%, which is not close to 100%")
        
        # Check if values are consistent with percentages
        portfolio_value = extraction_result.get("portfolio_value", {}).get("value")
        if portfolio_value:
            for allocation in asset_allocations:
                if allocation.get("value") is not None and allocation.get("percentage") is not None:
                    expected_value = portfolio_value * allocation["percentage"] / 100
                    actual_value = allocation["value"]
                    
                    # Calculate relative difference
                    if expected_value > 0:
                        relative_diff = abs(actual_value - expected_value) / expected_value
                        if relative_diff > self.tolerance:
                            result["valid"] = False
                            result["issues"].append(f"Asset allocation value for {allocation['asset_class']} ({actual_value}) does not match expected value ({expected_value}), difference: {relative_diff:.2%}")
        
        return result
    
    def _validate_securities(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate securities."""
        logger.info("Validating securities")
        
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if securities exist
        securities = extraction_result.get("securities", [])
        if not securities:
            result["valid"] = False
            result["issues"].append("No securities found")
            return result
        
        # Check for duplicate ISINs
        isin_counts = defaultdict(int)
        for security in securities:
            isin = security.get("isin")
            if isin:
                isin_counts[isin] += 1
        
        duplicates = [isin for isin, count in isin_counts.items() if count > 1]
        if duplicates:
            result["valid"] = False
            result["issues"].append(f"Duplicate ISINs found: {duplicates}")
        
        # Check if securities have required fields
        for i, security in enumerate(securities):
            if not security.get("isin"):
                result["valid"] = False
                result["issues"].append(f"Security at index {i} has no ISIN")
            
            if not security.get("description") or security.get("description") == "Unknown":
                result["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no description")
            
            if not security.get("security_type") or security.get("security_type") == "Unknown":
                result["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no security type")
            
            if security.get("valuation") is None:
                result["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no valuation")
        
        # Check if securities match asset allocation
        portfolio_value = extraction_result.get("portfolio_value", {}).get("value")
        if portfolio_value:
            total_value = sum(s.get("valuation", 0) or 0 for s in securities)
            if total_value > 0:
                # Calculate relative difference
                relative_diff = abs(total_value - portfolio_value) / portfolio_value
                if relative_diff > self.tolerance:
                    result["valid"] = False
                    result["issues"].append(f"Sum of securities ({total_value}) does not match portfolio value ({portfolio_value}), difference: {relative_diff:.2%}")
        
        # Group securities by type and check against asset allocation
        asset_allocations = extraction_result.get("asset_allocation", [])
        if asset_allocations:
            security_types = defaultdict(float)
            for security in securities:
                if security.get("security_type") and security.get("valuation"):
                    security_types[security.get("security_type")] += security.get("valuation", 0) or 0
            
            # Map security types to asset classes
            type_to_class = {
                "Bond": ["Bonds", "Fixed Income", "Debt"],
                "Equity": ["Equities", "Stocks", "Shares"],
                "Fund": ["Funds", "Mixed Funds", "Mutual Funds"],
                "Structured Product": ["Structured Products", "Structured Notes"]
            }
            
            # Check if security types match asset classes
            for security_type, total_value in security_types.items():
                # Find matching asset class
                matching_classes = []
                for asset_class in asset_allocations:
                    class_name = asset_class.get("asset_class", "").lower()
                    for type_key, class_names in type_to_class.items():
                        if security_type.lower() == type_key.lower() or any(class_name in c.lower() for c in class_names):
                            matching_classes.append(asset_class)
                
                if matching_classes:
                    # Sum values of matching asset classes
                    class_value = sum(c.get("value", 0) or 0 for c in matching_classes)
                    
                    # Calculate relative difference
                    if class_value > 0:
                        relative_diff = abs(total_value - class_value) / class_value
                        if relative_diff > self.tolerance:
                            result["issues"].append(f"Sum of {security_type} securities ({total_value}) does not match asset allocation ({class_value}), difference: {relative_diff:.2%}")
        
        return result
    
    def _validate_currency(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate currency."""
        logger.info("Validating currency")
        
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if currency exists
        currency = extraction_result.get("currency", {})
        if not currency or currency.get("value") is None:
            result["valid"] = False
            result["issues"].append("Currency not found")
            return result
        
        # Check if currency is valid
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "CNY", "HKD", "SGD", "ILS"]
        if currency["value"] not in valid_currencies and len(currency["value"]) != 3:
            result["valid"] = False
            result["issues"].append(f"Invalid currency: {currency['value']}")
        
        return result
    
    def _validate_risk_profile(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate risk profile."""
        logger.info("Validating risk profile")
        
        result = {
            "valid": True,
            "issues": []
        }
        
        # Check if risk profile exists
        risk_profile = extraction_result.get("risk_profile", {})
        if not risk_profile or risk_profile.get("value") is None:
            result["valid"] = False
            result["issues"].append("Risk profile not found")
            return result
        
        # Check if risk profile is valid
        valid_profiles = ["Low", "Medium-low", "Medium", "Medium-high", "High", "Conservative", "Moderate", "Aggressive", "Balanced"]
        if not any(profile.lower() in risk_profile["value"].lower() for profile in valid_profiles):
            result["issues"].append(f"Unusual risk profile: {risk_profile['value']}")
        
        return result
