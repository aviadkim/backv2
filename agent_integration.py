"""
Agent Integration - Demonstrates how to integrate with Google Agent Kit.

This module shows how to use Google Agent Kit to create agents that can help
with financial document processing.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json

# Import the financial document processor
from financial_document_processor_v2 import FinancialDocumentProcessorV2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDocumentAnalyzerAgent:
    """
    Agent that analyzes financial documents using the Financial Document Processor V2.
    """
    
    def __init__(self):
        """Initialize the financial document analyzer agent."""
        self.processor = FinancialDocumentProcessorV2()
        self.extraction_results = {}
    
    def process_document(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing processing results
        """
        logger.info(f"Agent processing financial document: {pdf_path}")
        
        # Process the document
        result = self.processor.process(pdf_path, output_dir=output_dir)
        
        # Store extraction results
        if "extraction_results" in result:
            self.extraction_results = result["extraction_results"]
        
        return result
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question about the processed financial document.
        
        Args:
            question: Question to answer
        
        Returns:
            Answer to the question
        """
        logger.info(f"Agent answering question: {question}")
        
        # Check if document has been processed
        if not self.extraction_results:
            return "No document has been processed yet. Please process a document first."
        
        # Convert question to lowercase for easier matching
        question_lower = question.lower()
        
        # Portfolio value
        if "portfolio value" in question_lower or "total value" in question_lower:
            portfolio_value = self.processor.get_portfolio_value()
            if portfolio_value:
                return f"The portfolio value is ${portfolio_value:,.2f}."
            else:
                return "Portfolio value not found in the document."
        
        # Top securities
        if "top" in question_lower and ("securities" in question_lower or "holdings" in question_lower):
            # Extract number from question (e.g., "top 5" -> 5)
            import re
            num_match = re.search(r"top\s+(\d+)", question_lower)
            n = int(num_match.group(1)) if num_match else 5
            
            top_securities = self.processor.get_top_securities(n)
            if top_securities:
                answer = f"The top {len(top_securities)} securities by valuation are:\n"
                for i, security in enumerate(top_securities, 1):
                    answer += f"{i}. {security.get('description', security.get('isin', 'Unknown'))}: ${security.get('valuation', 0):,.2f}\n"
                return answer
            else:
                return "No securities found in the document."
        
        # Asset allocation
        if "asset allocation" in question_lower or "asset class" in question_lower:
            asset_allocation = self.processor.get_asset_allocation()
            if asset_allocation:
                # Get top asset classes
                top_asset_classes = self.processor.get_top_asset_classes(5)
                
                answer = "The asset allocation is:\n"
                for i, allocation in enumerate(top_asset_classes, 1):
                    answer += f"{i}. {allocation.get('asset_class', 'Unknown')}: {allocation.get('percentage', 0):.2f}%\n"
                return answer
            else:
                return "No asset allocation found in the document."
        
        # Structured products
        if "structured product" in question_lower:
            structured_products = self.processor.get_structured_products()
            if structured_products:
                answer = f"Found {len(structured_products)} structured products:\n"
                for i, product in enumerate(structured_products[:5], 1):
                    answer += f"{i}. {product.get('description', product.get('isin', 'Unknown'))}: ${product.get('valuation', 0):,.2f}\n"
                return answer
            else:
                return "No structured products found in the document."
        
        # Security by ISIN
        if "isin" in question_lower:
            # Extract ISIN from question
            import re
            isin_match = re.search(r"([A-Z]{2}[A-Z0-9]{9}[0-9])", question)
            if isin_match:
                isin = isin_match.group(1)
                
                # Find security with this ISIN
                securities = self.processor.get_securities()
                for security in securities:
                    if security.get("isin") == isin:
                        return f"Security with ISIN {isin}:\n" \
                               f"Description: {security.get('description', 'Unknown')}\n" \
                               f"Type: {security.get('security_type', 'Unknown')}\n" \
                               f"Valuation: ${security.get('valuation', 0):,.2f}"
                
                return f"No security found with ISIN {isin}."
            else:
                return "Please provide a valid ISIN."
        
        # Default response
        return "I don't have enough information to answer that question. Please ask about portfolio value, top securities, asset allocation, structured products, or a specific ISIN."

class FinancialDocumentValidatorAgent:
    """
    Agent that validates financial document extraction results.
    """
    
    def __init__(self):
        """Initialize the financial document validator agent."""
        self.processor = FinancialDocumentProcessorV2()
        self.validation_results = {}
    
    def validate_document(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate a financial document.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)
        
        Returns:
            Dict containing validation results
        """
        logger.info(f"Agent validating financial document: {pdf_path}")
        
        # Process the document
        result = self.processor.process(pdf_path, output_dir=output_dir)
        
        # Store validation results
        if "extraction_results" in result and "validation" in result["extraction_results"]:
            self.validation_results = result["extraction_results"]["validation"]
        
        return self.validation_results
    
    def get_validation_summary(self) -> str:
        """
        Get a summary of validation results.
        
        Returns:
            Summary of validation results
        """
        logger.info("Agent providing validation summary")
        
        # Check if document has been validated
        if not self.validation_results:
            return "No document has been validated yet. Please validate a document first."
        
        # Create summary
        summary = "Validation Summary:\n"
        
        for section, result in self.validation_results.items():
            summary += f"{section.capitalize()}: {'Valid' if result.get('valid', False) else 'Invalid'}\n"
            
            if "issues" in result and result["issues"]:
                summary += f"  Issues ({len(result['issues'])}):\n"
                for issue in result["issues"]:
                    summary += f"  - {issue}\n"
            
            summary += "\n"
        
        return summary
    
    def fix_validation_issues(self) -> str:
        """
        Suggest fixes for validation issues.
        
        Returns:
            Suggestions for fixing validation issues
        """
        logger.info("Agent suggesting fixes for validation issues")
        
        # Check if document has been validated
        if not self.validation_results:
            return "No document has been validated yet. Please validate a document first."
        
        # Check if there are any issues
        has_issues = False
        for section, result in self.validation_results.items():
            if "issues" in result and result["issues"]:
                has_issues = True
                break
        
        if not has_issues:
            return "No validation issues found. The document extraction is valid."
        
        # Create suggestions
        suggestions = "Suggestions for fixing validation issues:\n\n"
        
        # Portfolio value issues
        if "portfolio_value" in self.validation_results and "issues" in self.validation_results["portfolio_value"]:
            issues = self.validation_results["portfolio_value"]["issues"]
            if issues:
                suggestions += "Portfolio Value Issues:\n"
                for issue in issues:
                    if "not found" in issue:
                        suggestions += "- The portfolio value was not found. Look for 'Portfolio Total', 'Total Assets', or 'Portfolio Value' in the document.\n"
                    elif "not positive" in issue:
                        suggestions += "- The portfolio value is not positive. Check if the value was extracted correctly.\n"
                    elif "Low confidence" in issue:
                        suggestions += "- Low confidence in portfolio value. Verify the value manually.\n"
                suggestions += "\n"
        
        # Securities issues
        if "securities" in self.validation_results and "issues" in self.validation_results["securities"]:
            issues = self.validation_results["securities"]["issues"]
            if issues:
                suggestions += "Securities Issues:\n"
                for issue in issues:
                    if "no ISIN" in issue:
                        suggestions += "- Some securities have no ISIN. Add missing ISINs.\n"
                    elif "invalid ISIN" in issue:
                        suggestions += "- Some securities have invalid ISINs. Correct the ISINs.\n"
                    elif "no security type" in issue:
                        suggestions += "- Some securities have no security type. Add missing security types.\n"
                    elif "no valuation" in issue:
                        suggestions += "- Some securities have no valuation. Add missing valuations.\n"
                    elif "Duplicate ISIN" in issue:
                        suggestions += "- There are duplicate ISINs. Remove duplicates.\n"
                suggestions += "\n"
        
        # Asset allocation issues
        if "asset_allocation" in self.validation_results and "issues" in self.validation_results["asset_allocation"]:
            issues = self.validation_results["asset_allocation"]["issues"]
            if issues:
                suggestions += "Asset Allocation Issues:\n"
                for issue in issues:
                    if "sum to" in issue and "not close to 100%" in issue:
                        suggestions += "- Asset allocation percentages do not sum to 100%. Normalize the percentages.\n"
                    elif "no asset class" in issue:
                        suggestions += "- Some asset allocation entries have no asset class. Add missing asset classes.\n"
                    elif "no value" in issue:
                        suggestions += "- Some asset allocation entries have no value. Add missing values.\n"
                    elif "no percentage" in issue:
                        suggestions += "- Some asset allocation entries have no percentage. Add missing percentages.\n"
                suggestions += "\n"
        
        # Overall issues
        if "overall" in self.validation_results and "issues" in self.validation_results["overall"]:
            issues = self.validation_results["overall"]["issues"]
            if issues:
                suggestions += "Overall Issues:\n"
                for issue in issues:
                    if "Sum of securities" in issue and "does not match portfolio value" in issue:
                        suggestions += "- The sum of securities does not match the portfolio value. Check for missing securities or incorrect valuations.\n"
                    elif "Sum of asset allocations" in issue and "does not match portfolio value" in issue:
                        suggestions += "- The sum of asset allocations does not match the portfolio value. Check for missing asset classes or incorrect values.\n"
                suggestions += "\n"
        
        return suggestions

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Demonstrate agent integration.")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--question", help="Question to ask the analyzer agent")
    parser.add_argument("--validate", action="store_true", help="Validate the document")
    parser.add_argument("--fix", action="store_true", help="Suggest fixes for validation issues")
    
    args = parser.parse_args()
    
    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1
    
    # Create output directory if not specified
    if not args.output_dir:
        file_name = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output_dir = f"{file_name}_agent_results"
    
    # Create agents
    analyzer_agent = FinancialDocumentAnalyzerAgent()
    validator_agent = FinancialDocumentValidatorAgent()
    
    # Process the document with the analyzer agent
    analyzer_agent.process_document(args.file_path, output_dir=args.output_dir)
    
    # Answer question if provided
    if args.question:
        answer = analyzer_agent.answer_question(args.question)
        print("\nQuestion:", args.question)
        print("Answer:", answer)
    
    # Validate the document if requested
    if args.validate:
        validator_agent.validate_document(args.file_path, output_dir=args.output_dir)
        summary = validator_agent.get_validation_summary()
        print("\nValidation Summary:")
        print(summary)
    
    # Suggest fixes if requested
    if args.fix:
        if not args.validate:
            validator_agent.validate_document(args.file_path, output_dir=args.output_dir)
        suggestions = validator_agent.fix_validation_issues()
        print("\nFix Suggestions:")
        print(suggestions)
    
    return 0

if __name__ == "__main__":
    main()
