"""
Multi-Stage Validator - Validates financial data extraction results.

This module provides tools to validate financial data extraction results
using multiple validation stages and cross-validation between different
extraction methods.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Set, Union
import json
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiStageValidator:
    """
    Validates financial data extraction results using multiple validation stages.
    """
    
    def __init__(self):
        """Initialize the multi-stage validator."""
        self.validation_results = {
            "portfolio_value": {
                "valid": False,
                "issues": []
            },
            "securities": {
                "valid": False,
                "issues": []
            },
            "asset_allocation": {
                "valid": False,
                "issues": []
            },
            "overall": {
                "valid": False,
                "issues": []
            }
        }
        
        # Tolerance for numerical validation
        self.tolerance = 0.05  # 5% tolerance
    
    def validate(self, extraction_results: Dict[str, Any], output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate financial data extraction results.
        
        Args:
            extraction_results: Dictionary containing extraction results
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing validation results
        """
        logger.info("Validating financial data extraction results")
        
        # Reset validation results
        self.validation_results = {
            "portfolio_value": {
                "valid": False,
                "issues": []
            },
            "securities": {
                "valid": False,
                "issues": []
            },
            "asset_allocation": {
                "valid": False,
                "issues": []
            },
            "overall": {
                "valid": False,
                "issues": []
            }
        }
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            # Validate portfolio value
            self._validate_portfolio_value(extraction_results)
            
            # Validate securities
            self._validate_securities(extraction_results)
            
            # Validate asset allocation
            self._validate_asset_allocation(extraction_results)
            
            # Perform overall validation
            self._validate_overall(extraction_results)
            
            # Save results if output_dir is specified
            if output_dir:
                self._save_results(output_dir)
            
            logger.info("Validation completed.")
            return self.validation_results
            
        except Exception as e:
            logger.error(f"Error validating extraction results: {str(e)}")
            return {"error": str(e)}
    
    def _validate_portfolio_value(self, extraction_results: Dict[str, Any]):
        """Validate portfolio value."""
        # Check if portfolio value exists
        if "portfolio_value" not in extraction_results or not extraction_results["portfolio_value"]:
            self.validation_results["portfolio_value"]["issues"].append("Portfolio value not found")
            return
        
        # Get portfolio value
        portfolio_value = None
        confidence = 0.0
        
        if isinstance(extraction_results["portfolio_value"], dict):
            if "value" in extraction_results["portfolio_value"]:
                portfolio_value = extraction_results["portfolio_value"]["value"]
                confidence = extraction_results["portfolio_value"].get("confidence", 0.0)
        elif isinstance(extraction_results["portfolio_value"], (int, float)):
            portfolio_value = float(extraction_results["portfolio_value"])
            confidence = 1.0
        
        if portfolio_value is None:
            self.validation_results["portfolio_value"]["issues"].append("Invalid portfolio value format")
            return
        
        # Check if portfolio value is reasonable
        if portfolio_value <= 0:
            self.validation_results["portfolio_value"]["issues"].append(f"Portfolio value ({portfolio_value}) is not positive")
        
        # Check confidence
        if confidence < 0.5:
            self.validation_results["portfolio_value"]["issues"].append(f"Low confidence in portfolio value ({confidence:.2f})")
        
        # Mark as valid if no issues
        if not self.validation_results["portfolio_value"]["issues"]:
            self.validation_results["portfolio_value"]["valid"] = True
        
        logger.info(f"Portfolio value validation: {self.validation_results['portfolio_value']['valid']}")
    
    def _validate_securities(self, extraction_results: Dict[str, Any]):
        """Validate securities."""
        # Check if securities exist
        if "securities" not in extraction_results or not extraction_results["securities"]:
            self.validation_results["securities"]["issues"].append("No securities found")
            return
        
        securities = extraction_results["securities"]
        
        # Check if securities is a list
        if not isinstance(securities, list):
            self.validation_results["securities"]["issues"].append("Securities is not a list")
            return
        
        # Check each security
        for i, security in enumerate(securities):
            # Check if security has required fields
            if not isinstance(security, dict):
                self.validation_results["securities"]["issues"].append(f"Security at index {i} is not a dictionary")
                continue
            
            # Check for ISIN
            if "isin" not in security or not security["isin"]:
                self.validation_results["securities"]["issues"].append(f"Security at index {i} has no ISIN")
            elif not self._is_valid_isin(security["isin"]):
                self.validation_results["securities"]["issues"].append(f"Security at index {i} has invalid ISIN: {security['isin']}")
            
            # Check for security type
            if "security_type" not in security or not security["security_type"]:
                self.validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no security type")
            
            # Check for valuation
            if "valuation" not in security or security["valuation"] is None:
                self.validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has no valuation")
            elif not isinstance(security["valuation"], (int, float)) or security["valuation"] <= 0:
                self.validation_results["securities"]["issues"].append(f"Security {security.get('isin', f'at index {i}')} has invalid valuation: {security['valuation']}")
        
        # Check for duplicate ISINs
        isin_counts = defaultdict(int)
        for security in securities:
            if "isin" in security and security["isin"]:
                isin_counts[security["isin"]] += 1
        
        for isin, count in isin_counts.items():
            if count > 1:
                self.validation_results["securities"]["issues"].append(f"Duplicate ISIN: {isin} appears {count} times")
        
        # Mark as valid if no issues or only minor issues
        if not self.validation_results["securities"]["issues"]:
            self.validation_results["securities"]["valid"] = True
        else:
            # Count serious issues
            serious_issues = [issue for issue in self.validation_results["securities"]["issues"] if "no ISIN" in issue or "invalid ISIN" in issue or "Duplicate ISIN" in issue]
            
            # If only minor issues (missing security type), still mark as valid
            if not serious_issues:
                self.validation_results["securities"]["valid"] = True
        
        logger.info(f"Securities validation: {self.validation_results['securities']['valid']} ({len(self.validation_results['securities']['issues'])} issues)")
    
    def _is_valid_isin(self, isin: str) -> bool:
        """Check if an ISIN is valid."""
        # Basic format check
        if not re.match(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$', isin):
            return False
        
        # TODO: Implement checksum validation
        
        return True
    
    def _validate_asset_allocation(self, extraction_results: Dict[str, Any]):
        """Validate asset allocation."""
        # Check if asset allocation exists
        if "asset_allocation" not in extraction_results or not extraction_results["asset_allocation"]:
            self.validation_results["asset_allocation"]["issues"].append("No asset allocation found")
            return
        
        asset_allocation = extraction_results["asset_allocation"]
        
        # Check if asset allocation is a list
        if not isinstance(asset_allocation, list):
            self.validation_results["asset_allocation"]["issues"].append("Asset allocation is not a list")
            return
        
        # Check each asset allocation entry
        for i, entry in enumerate(asset_allocation):
            # Check if entry has required fields
            if not isinstance(entry, dict):
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry at index {i} is not a dictionary")
                continue
            
            # Check for asset class
            if "asset_class" not in entry or not entry["asset_class"]:
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry at index {i} has no asset class")
            
            # Check for value
            if "value" not in entry or entry["value"] is None:
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry for {entry.get('asset_class', f'at index {i}')} has no value")
            elif not isinstance(entry["value"], (int, float)):
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry for {entry.get('asset_class', f'at index {i}')} has invalid value: {entry['value']}")
            
            # Check for percentage
            if "percentage" not in entry or entry["percentage"] is None:
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry for {entry.get('asset_class', f'at index {i}')} has no percentage")
            elif not isinstance(entry["percentage"], (int, float)):
                self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation entry for {entry.get('asset_class', f'at index {i}')} has invalid percentage: {entry['percentage']}")
        
        # Check if percentages sum to approximately 100%
        total_percentage = sum(entry.get("percentage", 0) or 0 for entry in asset_allocation if not entry.get("is_total", False))
        
        if abs(total_percentage - 100) > 5:
            self.validation_results["asset_allocation"]["issues"].append(f"Asset allocation percentages sum to {total_percentage:.2f}%, which is not close to 100%")
        
        # Mark as valid if no issues or only minor issues
        if not self.validation_results["asset_allocation"]["issues"]:
            self.validation_results["asset_allocation"]["valid"] = True
        else:
            # Count serious issues
            serious_issues = [issue for issue in self.validation_results["asset_allocation"]["issues"] if "sum to" in issue]
            
            # If only minor issues, still mark as valid
            if not serious_issues:
                self.validation_results["asset_allocation"]["valid"] = True
        
        logger.info(f"Asset allocation validation: {self.validation_results['asset_allocation']['valid']} ({len(self.validation_results['asset_allocation']['issues'])} issues)")
    
    def _validate_overall(self, extraction_results: Dict[str, Any]):
        """Perform overall validation."""
        # Check if portfolio value exists
        if "portfolio_value" not in extraction_results or not extraction_results["portfolio_value"]:
            self.validation_results["overall"]["issues"].append("Portfolio value not found")
            return
        
        # Get portfolio value
        portfolio_value = None
        
        if isinstance(extraction_results["portfolio_value"], dict):
            if "value" in extraction_results["portfolio_value"]:
                portfolio_value = extraction_results["portfolio_value"]["value"]
        elif isinstance(extraction_results["portfolio_value"], (int, float)):
            portfolio_value = float(extraction_results["portfolio_value"])
        
        if portfolio_value is None:
            self.validation_results["overall"]["issues"].append("Invalid portfolio value format")
            return
        
        # Check if securities exist
        if "securities" not in extraction_results or not extraction_results["securities"]:
            self.validation_results["overall"]["issues"].append("No securities found")
        else:
            # Calculate sum of securities
            securities_sum = sum(security.get("valuation", 0) or 0 for security in extraction_results["securities"])
            
            # Check if securities sum is close to portfolio value
            if portfolio_value > 0:
                difference_percentage = abs(securities_sum - portfolio_value) / portfolio_value * 100
                
                if difference_percentage > 10:
                    self.validation_results["overall"]["issues"].append(f"Sum of securities ({securities_sum:.2f}) does not match portfolio value ({portfolio_value:.2f}), difference: {difference_percentage:.2f}%")
        
        # Check if asset allocation exists
        if "asset_allocation" not in extraction_results or not extraction_results["asset_allocation"]:
            self.validation_results["overall"]["issues"].append("No asset allocation found")
        else:
            # Calculate sum of asset allocations
            asset_allocation_sum = sum(entry.get("value", 0) or 0 for entry in extraction_results["asset_allocation"] if not entry.get("is_total", False))
            
            # Check if asset allocation sum is close to portfolio value
            if portfolio_value > 0:
                difference_percentage = abs(asset_allocation_sum - portfolio_value) / portfolio_value * 100
                
                if difference_percentage > 10:
                    self.validation_results["overall"]["issues"].append(f"Sum of asset allocations ({asset_allocation_sum:.2f}) does not match portfolio value ({portfolio_value:.2f}), difference: {difference_percentage:.2f}%")
            
            # Check if percentages sum to approximately 100%
            total_percentage = sum(entry.get("percentage", 0) or 0 for entry in extraction_results["asset_allocation"] if not entry.get("is_total", False))
            
            if abs(total_percentage - 100) > 5:
                self.validation_results["overall"]["issues"].append(f"Asset allocation percentages sum to {total_percentage:.2f}%, which is not close to 100%")
        
        # Mark as valid if no issues
        if not self.validation_results["overall"]["issues"]:
            self.validation_results["overall"]["valid"] = True
        
        logger.info(f"Overall validation: {self.validation_results['overall']['valid']} ({len(self.validation_results['overall']['issues'])} issues)")
    
    def _save_results(self, output_dir):
        """Save validation results."""
        # Save validation results as JSON
        json_path = os.path.join(output_dir, "validation_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2)
        
        logger.info(f"Saved validation results to {json_path}")
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Returns:
            Dict containing validation summary
        """
        return {
            "portfolio_value": {
                "valid": self.validation_results["portfolio_value"]["valid"],
                "issues_count": len(self.validation_results["portfolio_value"]["issues"])
            },
            "securities": {
                "valid": self.validation_results["securities"]["valid"],
                "issues_count": len(self.validation_results["securities"]["issues"])
            },
            "asset_allocation": {
                "valid": self.validation_results["asset_allocation"]["valid"],
                "issues_count": len(self.validation_results["asset_allocation"]["issues"])
            },
            "overall": {
                "valid": self.validation_results["overall"]["valid"],
                "issues_count": len(self.validation_results["overall"]["issues"])
            }
        }
    
    def get_all_issues(self) -> List[str]:
        """
        Get all validation issues.
        
        Returns:
            List of all validation issues
        """
        issues = []
        
        for section, result in self.validation_results.items():
            for issue in result["issues"]:
                issues.append(f"{section}: {issue}")
        
        return issues
    
    def cross_validate(self, extraction_results1: Dict[str, Any], extraction_results2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cross-validate two sets of extraction results.
        
        Args:
            extraction_results1: First set of extraction results
            extraction_results2: Second set of extraction results
        
        Returns:
            Dict containing cross-validation results
        """
        cross_validation = {
            "portfolio_value": {
                "match": False,
                "difference": None,
                "difference_percentage": None
            },
            "securities_count": {
                "match": False,
                "difference": None
            },
            "asset_allocation_count": {
                "match": False,
                "difference": None
            },
            "overall_match": False
        }
        
        # Cross-validate portfolio value
        portfolio_value1 = self._get_portfolio_value(extraction_results1)
        portfolio_value2 = self._get_portfolio_value(extraction_results2)
        
        if portfolio_value1 is not None and portfolio_value2 is not None:
            difference = abs(portfolio_value1 - portfolio_value2)
            difference_percentage = difference / max(portfolio_value1, portfolio_value2) * 100
            
            cross_validation["portfolio_value"]["difference"] = difference
            cross_validation["portfolio_value"]["difference_percentage"] = difference_percentage
            
            if difference_percentage <= 5:
                cross_validation["portfolio_value"]["match"] = True
        
        # Cross-validate securities count
        securities_count1 = len(extraction_results1.get("securities", []))
        securities_count2 = len(extraction_results2.get("securities", []))
        
        cross_validation["securities_count"]["difference"] = abs(securities_count1 - securities_count2)
        
        if abs(securities_count1 - securities_count2) <= 5:
            cross_validation["securities_count"]["match"] = True
        
        # Cross-validate asset allocation count
        asset_allocation_count1 = len(extraction_results1.get("asset_allocation", []))
        asset_allocation_count2 = len(extraction_results2.get("asset_allocation", []))
        
        cross_validation["asset_allocation_count"]["difference"] = abs(asset_allocation_count1 - asset_allocation_count2)
        
        if abs(asset_allocation_count1 - asset_allocation_count2) <= 5:
            cross_validation["asset_allocation_count"]["match"] = True
        
        # Overall match
        if (
            cross_validation["portfolio_value"]["match"] and
            cross_validation["securities_count"]["match"] and
            cross_validation["asset_allocation_count"]["match"]
        ):
            cross_validation["overall_match"] = True
        
        return cross_validation
    
    def _get_portfolio_value(self, extraction_results: Dict[str, Any]) -> Optional[float]:
        """Get portfolio value from extraction results."""
        if "portfolio_value" not in extraction_results:
            return None
        
        portfolio_value = extraction_results["portfolio_value"]
        
        if isinstance(portfolio_value, dict):
            if "value" in portfolio_value:
                return portfolio_value["value"]
        elif isinstance(portfolio_value, (int, float)):
            return float(portfolio_value)
        
        return None

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate financial data extraction results.")
    parser.add_argument("extraction_file", help="Path to the extraction results JSON file")
    parser.add_argument("--cross-validation-file", help="Path to another extraction results JSON file for cross-validation")
    parser.add_argument("--output-dir", help="Directory to save output files")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.extraction_file):
        logger.error(f"Error: Extraction file not found: {args.extraction_file}")
        return 1
    
    # Read the extraction results
    with open(args.extraction_file, "r", encoding="utf-8") as f:
        extraction_results = json.load(f)
    
    # Validate extraction results
    validator = MultiStageValidator()
    validation_results = validator.validate(extraction_results, output_dir=args.output_dir)
    
    # Print summary
    print("\nValidation Summary:")
    print("=================")
    
    for section, result in validation_results.items():
        print(f"{section.capitalize()}: {'Valid' if result['valid'] else 'Invalid'}")
        
        if result["issues"]:
            print(f"  Issues ({len(result['issues'])}):")
            for issue in result["issues"]:
                print(f"  - {issue}")
    
    # Cross-validate if another file is provided
    if args.cross_validation_file:
        if not os.path.exists(args.cross_validation_file):
            logger.error(f"Error: Cross-validation file not found: {args.cross_validation_file}")
            return 1
        
        # Read the cross-validation extraction results
        with open(args.cross_validation_file, "r", encoding="utf-8") as f:
            cross_validation_results = json.load(f)
        
        # Cross-validate
        cross_validation = validator.cross_validate(extraction_results, cross_validation_results)
        
        # Print cross-validation summary
        print("\nCross-Validation Summary:")
        print("=======================")
        
        print(f"Portfolio Value: {'Match' if cross_validation['portfolio_value']['match'] else 'Mismatch'}")
        if cross_validation["portfolio_value"]["difference"] is not None:
            print(f"  Difference: {cross_validation['portfolio_value']['difference']:,.2f} ({cross_validation['portfolio_value']['difference_percentage']:.2f}%)")
        
        print(f"Securities Count: {'Match' if cross_validation['securities_count']['match'] else 'Mismatch'}")
        print(f"  Difference: {cross_validation['securities_count']['difference']}")
        
        print(f"Asset Allocation Count: {'Match' if cross_validation['asset_allocation_count']['match'] else 'Mismatch'}")
        print(f"  Difference: {cross_validation['asset_allocation_count']['difference']}")
        
        print(f"Overall Match: {'Yes' if cross_validation['overall_match'] else 'No'}")
    
    return 0

if __name__ == "__main__":
    main()
