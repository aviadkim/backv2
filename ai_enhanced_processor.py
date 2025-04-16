"""
AI Enhanced Financial Document Processor - Integrates OpenRouter API for enhanced processing.

This module integrates the financial document processor with OpenRouter API
for enhanced AI processing and learning from corrections.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import requests
from datetime import datetime

# Import the financial document processor
try:
    # Try to import the real financial document processor
    from financial_document_processor_v2 import FinancialDocumentProcessorV2
except ImportError:
    # If not available, use the mock version for testing
    from mock_financial_document_processor import FinancialDocumentProcessorV2
from ai_feedback_learning import AIFeedbackLearning

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEnhancedProcessor:
    """
    Integrates the financial document processor with OpenRouter API for enhanced processing.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the AI enhanced processor.

        Args:
            api_key: OpenRouter API key (default: None, will try to get from environment)
        """
        # Use the provided API key or get from environment
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            logger.warning("No OpenRouter API key provided. AI enhancement will be limited.")
        else:
            logger.info("OpenRouter API key loaded successfully.")

        self.processor = FinancialDocumentProcessorV2()
        self.feedback_learning = AIFeedbackLearning(api_key=self.api_key)

        self.current_document_fingerprint = None
        self.current_document_content = None

    def process_document(self, pdf_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a financial document with AI enhancement.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save output files (default: None)

        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing document with AI enhancement: {pdf_path}")

        try:
            # Register document for feedback learning
            self.current_document_fingerprint, _ = self.feedback_learning.register_document(pdf_path)

            # Extract text from PDF
            self.current_document_content = self._extract_text(pdf_path)

            # Process document with standard processor
            result = self.processor.process(pdf_path, output_dir=output_dir)

            # Apply learned corrections
            if "extraction_results" in result:
                result["extraction_results"] = self.feedback_learning.apply_learned_corrections(
                    result["extraction_results"], self.current_document_content
                )

            # Enhance extraction with AI
            if self.api_key:
                result = self._enhance_extraction_with_ai(result)

            # Save enhanced results
            if output_dir:
                enhanced_path = os.path.join(output_dir, "enhanced_result.json")
                with open(enhanced_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2)

            logger.info("AI enhanced processing completed.")
            return result

        except Exception as e:
            logger.error(f"Error in AI enhanced processing: {str(e)}")
            return {"error": str(e)}

    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                    text += "\n\n"

                return text
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""

    def _enhance_extraction_with_ai(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance extraction results with AI.

        Args:
            result: Extraction results

        Returns:
            Enhanced extraction results
        """
        try:
            if "extraction_results" not in result:
                return result

            extraction_results = result["extraction_results"]

            # Prepare message for AI
            message = {
                "role": "system",
                "content": "You are an AI assistant that helps enhance financial document extraction. "
                           "Analyze the extraction results and the document content to identify any issues "
                           "or missing information."
            }

            extraction_text = json.dumps(extraction_results, indent=2)
            user_message = {
                "role": "user",
                "content": f"Here are the extraction results from a financial document:\n\n{extraction_text}\n\n"
                           f"Here is the document content:\n\n{self.current_document_content[:5000]}...\n\n"
                           f"Please analyze the extraction results and identify any issues or missing information. "
                           f"Focus on portfolio value, securities, asset allocation, and structured products. "
                           f"If you identify any issues, provide the correct values."
            }

            # Call OpenRouter API
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "anthropic/claude-3-opus:beta",  # Using Claude 3 Opus for best reasoning
                    "messages": [message, user_message]
                }
            )

            if response.status_code == 200:
                ai_response = response.json()

                # Extract analysis from AI response
                analysis = ai_response["choices"][0]["message"]["content"]

                # Add AI analysis to result
                result["ai_analysis"] = analysis

                # Extract corrections from AI analysis
                corrections = self._extract_corrections_from_analysis(analysis, extraction_results)

                # Apply corrections
                for field, correction in corrections.items():
                    if field in extraction_results:
                        # Record correction for learning
                        self.feedback_learning.record_correction(
                            self.current_document_fingerprint,
                            field,
                            extraction_results[field],
                            correction
                        )

                        # Apply correction
                        extraction_results[field] = correction

                # Add corrections to result
                result["ai_corrections"] = corrections
            else:
                logger.error(f"Error calling OpenRouter API: {response.status_code} - {response.text}")

            return result

        except Exception as e:
            logger.error(f"Error enhancing extraction with AI: {str(e)}")
            return result

    def _extract_corrections_from_analysis(self, analysis: str, extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract corrections from AI analysis.

        Args:
            analysis: AI analysis
            extraction_results: Extraction results

        Returns:
            Dict of corrections
        """
        corrections = {}

        try:
            # This is a simplified implementation - in a real system, you would use more sophisticated
            # techniques to extract corrections from AI analysis

            # Look for correction patterns
            lines = analysis.split("\n")
            for line in lines:
                line = line.strip()

                # Look for portfolio value corrections
                if "portfolio value" in line.lower() and "should be" in line.lower():
                    import re
                    value_match = re.search(r"(\d[\d,.]*)", line)
                    if value_match:
                        value_str = value_match.group(1)
                        value = float(value_str.replace(",", ""))
                        corrections["portfolio_value"] = value

                # Look for security corrections
                if "security" in line.lower() and "isin" in line.lower() and "should be" in line.lower():
                    import re
                    isin_match = re.search(r"([A-Z]{2}[A-Z0-9]{9}[0-9])", line)
                    value_match = re.search(r"(\d[\d,.]*)", line)
                    if isin_match and value_match:
                        isin = isin_match.group(1)
                        value_str = value_match.group(1)
                        value = float(value_str.replace(",", ""))

                        # Find security in extraction results
                        if "securities" in extraction_results:
                            for i, security in enumerate(extraction_results["securities"]):
                                if security.get("isin") == isin:
                                    corrections[f"securities[{i}].valuation"] = value

            # Call OpenRouter API to extract corrections in a structured format
            if self.api_key:
                message = {
                    "role": "system",
                    "content": "You are an AI assistant that helps extract corrections from analysis. "
                               "Extract corrections in a structured JSON format."
                }

                extraction_text = json.dumps(extraction_results, indent=2)
                user_message = {
                    "role": "user",
                    "content": f"Here are the extraction results from a financial document:\n\n{extraction_text}\n\n"
                               f"Here is the analysis of the extraction results:\n\n{analysis}\n\n"
                               f"Please extract corrections from the analysis in a structured JSON format. "
                               f"The format should be: {{'field': 'corrected_value'}}. "
                               f"For securities, use the format: {{'securities[index].field': 'corrected_value'}}."
                }

                # Call OpenRouter API
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3-opus:beta",  # Using Claude 3 Opus for best reasoning
                        "messages": [message, user_message]
                    }
                )

                if response.status_code == 200:
                    ai_response = response.json()

                    # Extract corrections from AI response
                    corrections_text = ai_response["choices"][0]["message"]["content"]

                    # Extract JSON from text
                    import re
                    json_match = re.search(r"\{.*\}", corrections_text, re.DOTALL)
                    if json_match:
                        try:
                            structured_corrections = json.loads(json_match.group(0))
                            corrections.update(structured_corrections)
                        except:
                            logger.error("Error parsing corrections JSON")
                else:
                    logger.error(f"Error calling OpenRouter API: {response.status_code} - {response.text}")

        except Exception as e:
            logger.error(f"Error extracting corrections from analysis: {str(e)}")

        return corrections

    def record_user_correction(self, field: str, original_value: Any, corrected_value: Any) -> bool:
        """
        Record a correction made by the user.

        Args:
            field: Field that was corrected
            original_value: Original value
            corrected_value: Corrected value

        Returns:
            True if correction was successfully recorded, False otherwise
        """
        if not self.current_document_fingerprint:
            logger.warning("No document registered for feedback learning")
            # For testing purposes, set a mock document fingerprint
            self.current_document_fingerprint = "test_document_fingerprint"

        return self.feedback_learning.record_correction(
            self.current_document_fingerprint, field, original_value, corrected_value
        )

    def generate_improvement_suggestions(self) -> List[str]:
        """
        Generate suggestions for improving extraction based on corrections.

        Returns:
            List of improvement suggestions
        """
        if not self.current_document_fingerprint:
            logger.warning("No document registered for feedback learning")
            # For testing purposes, set a mock document fingerprint
            self.current_document_fingerprint = "test_document_fingerprint"

        return self.feedback_learning.generate_improvement_suggestions(self.current_document_fingerprint)

    def get_portfolio_value(self) -> Optional[float]:
        """
        Get the portfolio value.

        Returns:
            Portfolio value or None if not found
        """
        return self.processor.get_portfolio_value()

    def get_securities(self) -> List[Dict[str, Any]]:
        """
        Get securities.

        Returns:
            List of securities
        """
        return self.processor.get_securities()

    def get_asset_allocation(self) -> List[Dict[str, Any]]:
        """
        Get asset allocation.

        Returns:
            List of asset allocation entries
        """
        return self.processor.get_asset_allocation()

    def get_structured_products(self) -> List[Dict[str, Any]]:
        """
        Get structured products.

        Returns:
            List of structured products
        """
        return self.processor.get_structured_products()

    def get_top_securities(self, n: int = 5) -> List[Dict[str, Any]]:
        """
        Get the top N securities by valuation.

        Args:
            n: Number of securities to retrieve (default: 5)

        Returns:
            List of top N securities by valuation
        """
        return self.processor.get_top_securities(n)

def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="AI Enhanced Financial Document Processor")
    parser.add_argument("file_path", help="Path to the financial document")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--output-dir", help="Directory to save output files")
    parser.add_argument("--correct", action="store_true", help="Record a correction")
    parser.add_argument("--field", help="Field to correct")
    parser.add_argument("--original", help="Original value")
    parser.add_argument("--corrected", help="Corrected value")
    parser.add_argument("--suggestions", action="store_true", help="Generate improvement suggestions")

    args = parser.parse_args()

    # Check if the file exists
    if not os.path.exists(args.file_path):
        logger.error(f"Error: File not found: {args.file_path}")
        return 1

    # Create output directory if not specified
    if not args.output_dir:
        file_name = os.path.splitext(os.path.basename(args.file_path))[0]
        args.output_dir = f"{file_name}_ai_enhanced_results"

    # Initialize AI enhanced processor
    processor = AIEnhancedProcessor(api_key=args.api_key)

    if args.correct and args.field and args.original and args.corrected:
        # Process document
        processor.process_document(args.file_path, output_dir=args.output_dir)

        # Record correction
        success = processor.record_user_correction(
            args.field, args.original, args.corrected
        )

        if success:
            print(f"Correction recorded for field: {args.field}")
        else:
            print("Failed to record correction")

    elif args.suggestions:
        # Process document
        processor.process_document(args.file_path, output_dir=args.output_dir)

        # Generate improvement suggestions
        suggestions = processor.generate_improvement_suggestions()

        print("Improvement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")

    else:
        # Process document
        result = processor.process_document(args.file_path, output_dir=args.output_dir)

        # Print summary
        print("\nAI Enhanced Financial Document Processing Summary:")
        print("=================================================")

        portfolio_value = processor.get_portfolio_value()
        if portfolio_value:
            print(f"Portfolio Value: ${portfolio_value:,.2f}")
        else:
            print("Portfolio Value: Not found")

        securities = processor.get_securities()
        print(f"Securities: {len(securities)}")

        asset_allocation = processor.get_asset_allocation()
        print(f"Asset Allocation Entries: {len(asset_allocation)}")

        structured_products = processor.get_structured_products()
        print(f"Structured Products: {len(structured_products)}")

        # Print top securities
        top_securities = processor.get_top_securities(5)
        if top_securities:
            print("\nTop 5 Securities by Valuation:")
            for i, security in enumerate(top_securities, 1):
                print(f"{i}. {security.get('description', security.get('isin', 'Unknown'))}: ${security.get('valuation', 0):,.2f}")

        # Print AI analysis if available
        if "ai_analysis" in result:
            print("\nAI Analysis:")
            print(result["ai_analysis"])

        # Print AI corrections if available
        if "ai_corrections" in result and result["ai_corrections"]:
            print("\nAI Corrections:")
            for field, correction in result["ai_corrections"].items():
                print(f"{field}: {correction}")

        print(f"\nResults saved to: {args.output_dir}")

    return 0

if __name__ == "__main__":
    main()
