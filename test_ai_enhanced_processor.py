"""
Test module for AI Enhanced Processor.

This module tests the AI enhanced processor functionality to ensure that
it correctly processes financial documents and applies learned corrections.
"""
import os
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock
import tempfile

from ai_enhanced_processor import AIEnhancedProcessor

class TestAIEnhancedProcessor(unittest.TestCase):
    """Test cases for AI Enhanced Processor."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create a mock API key
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "test_api_key")

        # Initialize the AI enhanced processor with the mock API key
        self.processor = AIEnhancedProcessor(api_key=self.api_key)

        # Create a test document
        self.test_document_path = os.path.join(self.test_dir, "test_document.pdf")
        with open(self.test_document_path, "w", encoding="utf-8") as f:
            f.write("This is a test document.\n")
            f.write("It contains some financial information.\n")
            f.write("Portfolio Value: 1,000,000\n")
            f.write("ISIN: US0378331005, Value: 100,000\n")
            f.write("ISIN: US5949181045, Value: 200,000\n")

        # Create output directory
        self.output_dir = os.path.join(self.test_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory and files
        shutil.rmtree(self.test_dir)

        # Remove feedback and corrections store files
        if os.path.exists("feedback_store.json"):
            os.remove("feedback_store.json")
        if os.path.exists("corrections_store.json"):
            os.remove("corrections_store.json")

    @patch('ai_enhanced_processor.FinancialDocumentProcessorV2')
    @patch('ai_enhanced_processor.AIFeedbackLearning')
    @patch('requests.post')
    def test_process_document(self, mock_post, mock_feedback_learning, mock_processor):
        """Test processing a document."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value
        mock_processor_instance.process.return_value = {
            "extraction_results": {
                "portfolio_value": 1000000,
                "securities": [
                    {
                        "isin": "US0378331005",
                        "description": "Apple Inc.",
                        "valuation": 100000
                    },
                    {
                        "isin": "US5949181045",
                        "description": "Microsoft Corp.",
                        "valuation": 200000
                    }
                ]
            }
        }
        mock_processor_instance.get_portfolio_value.return_value = 1000000
        mock_processor_instance.get_securities.return_value = [
            {
                "isin": "US0378331005",
                "description": "Apple Inc.",
                "valuation": 100000
            },
            {
                "isin": "US5949181045",
                "description": "Microsoft Corp.",
                "valuation": 200000
            }
        ]
        mock_processor_instance.get_asset_allocation.return_value = []
        mock_processor_instance.get_structured_products.return_value = []
        mock_processor_instance.get_top_securities.return_value = [
            {
                "isin": "US5949181045",
                "description": "Microsoft Corp.",
                "valuation": 200000
            },
            {
                "isin": "US0378331005",
                "description": "Apple Inc.",
                "valuation": 100000
            }
        ]

        # Mock the feedback learning
        mock_feedback_learning_instance = mock_feedback_learning.return_value
        mock_feedback_learning_instance.register_document.return_value = ("doc_fingerprint", "source_fingerprint")
        mock_feedback_learning_instance.apply_learned_corrections.return_value = {
            "portfolio_value": 1500000,
            "securities": [
                {
                    "isin": "US0378331005",
                    "description": "Apple Inc.",
                    "valuation": 150000
                },
                {
                    "isin": "US5949181045",
                    "description": "Microsoft Corp.",
                    "valuation": 250000
                }
            ]
        }

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The AI has analyzed the document."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Process the document
        result = self.processor.process_document(self.test_document_path, output_dir=self.output_dir)

        # Check that the document was processed
        self.assertIn("extraction_results", result)
        self.assertEqual(result["extraction_results"]["portfolio_value"], 1500000)

        # Check that the feedback learning was used
        mock_feedback_learning_instance.register_document.assert_called_once_with(self.test_document_path)
        mock_feedback_learning_instance.apply_learned_corrections.assert_called_once()

        # Check that the API was called
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["model"], "anthropic/claude-3-opus:beta")

    @patch('ai_enhanced_processor.FinancialDocumentProcessorV2')
    @patch('ai_enhanced_processor.AIFeedbackLearning')
    def test_record_user_correction(self, mock_feedback_learning, mock_processor):
        """Test recording a user correction."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value

        # Mock the feedback learning
        mock_feedback_learning_instance = mock_feedback_learning.return_value
        mock_feedback_learning_instance.register_document.return_value = ("doc_fingerprint", "source_fingerprint")
        mock_feedback_learning_instance.record_correction.return_value = True

        # Set the current document fingerprint
        self.processor.current_document_fingerprint = "doc_fingerprint"

        # Record a correction
        field = "portfolio_value"
        original_value = 1000000
        corrected_value = 1500000

        success = self.processor.record_user_correction(field, original_value, corrected_value)

        # Check that the correction was recorded
        self.assertTrue(success)
        mock_feedback_learning_instance.record_correction.assert_called_once_with(
            "doc_fingerprint", field, original_value, corrected_value
        )

    @patch('ai_enhanced_processor.FinancialDocumentProcessorV2')
    @patch('ai_enhanced_processor.AIFeedbackLearning')
    def test_generate_improvement_suggestions(self, mock_feedback_learning, mock_processor):
        """Test generating improvement suggestions."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value

        # Mock the feedback learning
        mock_feedback_learning_instance = mock_feedback_learning.return_value
        mock_feedback_learning_instance.generate_improvement_suggestions.return_value = [
            "Suggestion 1",
            "Suggestion 2",
            "Suggestion 3"
        ]

        # Set the current document fingerprint
        self.processor.current_document_fingerprint = "doc_fingerprint"

        # Generate improvement suggestions
        suggestions = self.processor.generate_improvement_suggestions()

        # Check that suggestions were generated
        self.assertEqual(len(suggestions), 3)
        self.assertEqual(suggestions[0], "Suggestion 1")
        self.assertEqual(suggestions[1], "Suggestion 2")
        self.assertEqual(suggestions[2], "Suggestion 3")

        # Check that the feedback learning was used
        mock_feedback_learning_instance.generate_improvement_suggestions.assert_called_once_with("doc_fingerprint")

    @patch('ai_enhanced_processor.FinancialDocumentProcessorV2')
    @patch('ai_enhanced_processor.AIFeedbackLearning')
    @patch('requests.post')
    def test_enhance_extraction_with_ai(self, mock_post, mock_feedback_learning, mock_processor):
        """Test enhancing extraction with AI."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value

        # Mock the feedback learning
        mock_feedback_learning_instance = mock_feedback_learning.return_value
        mock_feedback_learning_instance.record_correction.return_value = True

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "The portfolio value should be 1,500,000 instead of 1,000,000."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Set the current document fingerprint and content
        self.processor.current_document_fingerprint = "doc_fingerprint"
        self.processor.current_document_content = "This is a test document."

        # Create extraction results
        extraction_results = {
            "portfolio_value": 1000000,
            "securities": [
                {
                    "isin": "US0378331005",
                    "description": "Apple Inc.",
                    "valuation": 100000
                },
                {
                    "isin": "US5949181045",
                    "description": "Microsoft Corp.",
                    "valuation": 200000
                }
            ]
        }

        # Enhance extraction with AI
        result = self.processor._enhance_extraction_with_ai({"extraction_results": extraction_results})

        # Check that the extraction was enhanced
        self.assertIn("ai_analysis", result)
        self.assertEqual(result["ai_analysis"], "The portfolio value should be 1,500,000 instead of 1,000,000.")

        # Check that the API was called
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["model"], "anthropic/claude-3-opus:beta")

    @patch('ai_enhanced_processor.FinancialDocumentProcessorV2')
    @patch('ai_enhanced_processor.AIFeedbackLearning')
    @patch('requests.post')
    def test_extract_corrections_from_analysis(self, mock_post, mock_feedback_learning, mock_processor):
        """Test extracting corrections from AI analysis."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value

        # Mock the feedback learning
        mock_feedback_learning_instance = mock_feedback_learning.return_value

        # Mock the API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"portfolio_value": 1500000, "securities[0].valuation": 150000}'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        # Create extraction results
        extraction_results = {
            "portfolio_value": 1000000,
            "securities": [
                {
                    "isin": "US0378331005",
                    "description": "Apple Inc.",
                    "valuation": 100000
                },
                {
                    "isin": "US5949181045",
                    "description": "Microsoft Corp.",
                    "valuation": 200000
                }
            ]
        }

        # Extract corrections from analysis
        analysis = "The portfolio value should be 1,500,000 instead of 1,000,000."
        corrections = self.processor._extract_corrections_from_analysis(analysis, extraction_results)

        # Check that corrections were extracted
        self.assertEqual(len(corrections), 2)
        self.assertEqual(corrections["portfolio_value"], 1500000)
        self.assertEqual(corrections["securities[0].valuation"], 150000)

        # Check that the API was called
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://openrouter.ai/api/v1/chat/completions")
        self.assertEqual(kwargs["headers"]["Authorization"], f"Bearer {self.api_key}")
        self.assertEqual(kwargs["json"]["model"], "anthropic/claude-3-opus:beta")

if __name__ == "__main__":
    unittest.main()
