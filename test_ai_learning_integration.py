"""
Integration test for AI learning.

This module tests the integration between the AI feedback learning and the AI enhanced processor
to demonstrate that the AI gets smarter with each scan.
"""
import os
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import time

from ai_feedback_learning import AIFeedbackLearning
from ai_enhanced_processor import AIEnhancedProcessor

class TestAILearningIntegration(unittest.TestCase):
    """Integration test for AI learning."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Get the OpenRouter API key from environment variable
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "test_api_key")

        # Initialize the AI feedback learning module
        self.feedback_learning = AIFeedbackLearning(api_key=self.api_key)

        # Initialize the AI enhanced processor
        self.processor = AIEnhancedProcessor(api_key=self.api_key)

        # Create a test document
        self.test_document_path = os.path.join(self.test_dir, "test_document.txt")
        with open(self.test_document_path, "w", encoding="utf-8") as f:
            f.write("This is a test document.\n")
            f.write("It contains some financial information.\n")
            f.write("Portfolio Value: 1,000,000\n")
            f.write("ISIN: US0378331005, Value: 100,000\n")
            f.write("ISIN: US5949181045, Value: 200,000\n")

        # Create a similar document with the same format but different values
        self.similar_document_path = os.path.join(self.test_dir, "similar_document.txt")
        with open(self.similar_document_path, "w", encoding="utf-8") as f:
            f.write("This is a similar document.\n")
            f.write("It also contains some financial information.\n")
            f.write("Portfolio Value: 2,000,000\n")
            f.write("ISIN: US0378331005, Value: 150,000\n")
            f.write("ISIN: US5949181045, Value: 250,000\n")

        # Create output directories
        self.output_dir1 = os.path.join(self.test_dir, "output1")
        os.makedirs(self.output_dir1, exist_ok=True)

        self.output_dir2 = os.path.join(self.test_dir, "output2")
        os.makedirs(self.output_dir2, exist_ok=True)

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
    def test_ai_learning_integration(self, mock_processor):
        """Test that the AI gets smarter with each scan."""
        # Mock the processor
        mock_processor_instance = mock_processor.return_value

        # First document extraction results (incorrect)
        mock_processor_instance.process.return_value = {
            "extraction_results": {
                "portfolio_value": 1000000,  # Incorrect value
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

        # Process the first document
        result1 = self.processor.process_document(self.test_document_path, output_dir=self.output_dir1)

        # Record a correction
        self.processor.record_user_correction(
            "portfolio_value", 1000000, 1500000
        )

        # Process the similar document
        result2 = self.processor.process_document(self.similar_document_path, output_dir=self.output_dir2)

        # Check that the AI applied the learned correction to the similar document
        self.assertEqual(result2["extraction_results"]["portfolio_value"], 1500000)

        # Generate improvement suggestions
        suggestions = self.processor.generate_improvement_suggestions()

        # Check that suggestions were generated
        self.assertGreater(len(suggestions), 0)

        # Print the results
        print("\nAI Learning Integration Test Results:")
        print("=====================================")
        print(f"First document extraction result: {result1['extraction_results']['portfolio_value']}")
        print(f"Correction applied: 1000000 -> 1500000")
        print(f"Similar document extraction result after learning: {result2['extraction_results']['portfolio_value']}")
        print("\nImprovement Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")

    def test_real_world_scenario(self):
        """Test a real-world scenario with multiple corrections and learning."""
        # Skip this test if running in CI environment
        if os.environ.get("CI"):
            self.skipTest("Skipping real-world scenario test in CI environment")

        # Create a more complex test document
        complex_document_path = os.path.join(self.test_dir, "complex_document.txt")
        with open(complex_document_path, "w", encoding="utf-8") as f:
            f.write("Financial Portfolio Report\n")
            f.write("========================\n\n")
            f.write("Portfolio Value: 10,000,000\n\n")
            f.write("Asset Allocation:\n")
            f.write("- Equities: 60% (6,000,000)\n")
            f.write("- Bonds: 30% (3,000,000)\n")
            f.write("- Cash: 10% (1,000,000)\n\n")
            f.write("Securities:\n")
            f.write("1. ISIN: US0378331005, Apple Inc., 1,000,000\n")
            f.write("2. ISIN: US5949181045, Microsoft Corp., 2,000,000\n")
            f.write("3. ISIN: US88160R1014, Tesla Inc., 1,500,000\n")
            f.write("4. ISIN: US0231351067, Amazon.com Inc., 1,500,000\n")
            f.write("5. ISIN: US02079K1079, Alphabet Inc., 1,000,000\n")
            f.write("6. ISIN: US30303M1027, Meta Platforms Inc., 1,000,000\n")
            f.write("7. ISIN: US67066G1040, NVIDIA Corp., 2,000,000\n")

        # Create a similar document
        similar_complex_document_path = os.path.join(self.test_dir, "similar_complex_document.txt")
        with open(similar_complex_document_path, "w", encoding="utf-8") as f:
            f.write("Financial Portfolio Report\n")
            f.write("========================\n\n")
            f.write("Portfolio Value: 15,000,000\n\n")
            f.write("Asset Allocation:\n")
            f.write("- Equities: 70% (10,500,000)\n")
            f.write("- Bonds: 20% (3,000,000)\n")
            f.write("- Cash: 10% (1,500,000)\n\n")
            f.write("Securities:\n")
            f.write("1. ISIN: US0378331005, Apple Inc., 1,500,000\n")
            f.write("2. ISIN: US5949181045, Microsoft Corp., 3,000,000\n")
            f.write("3. ISIN: US88160R1014, Tesla Inc., 2,000,000\n")
            f.write("4. ISIN: US0231351067, Amazon.com Inc., 2,000,000\n")
            f.write("5. ISIN: US02079K1079, Alphabet Inc., 1,500,000\n")
            f.write("6. ISIN: US30303M1027, Meta Platforms Inc., 1,500,000\n")
            f.write("7. ISIN: US67066G1040, NVIDIA Corp., 3,000,000\n")

        # Create output directories
        complex_output_dir = os.path.join(self.test_dir, "complex_output")
        os.makedirs(complex_output_dir, exist_ok=True)

        similar_complex_output_dir = os.path.join(self.test_dir, "similar_complex_output")
        os.makedirs(similar_complex_output_dir, exist_ok=True)

        # Process the complex document
        with patch('ai_enhanced_processor.FinancialDocumentProcessorV2') as mock_processor:
            # Mock the processor
            mock_processor_instance = mock_processor.return_value

            # Complex document extraction results (with some errors)
            mock_processor_instance.process.return_value = {
                "extraction_results": {
                    "portfolio_value": 10000000,
                    "asset_allocation": [
                        {
                            "asset_class": "Equities",
                            "percentage": 60,
                            "value": 6000000
                        },
                        {
                            "asset_class": "Bonds",
                            "percentage": 30,
                            "value": 3000000
                        },
                        {
                            "asset_class": "Cash",
                            "percentage": 10,
                            "value": 1000000
                        }
                    ],
                    "securities": [
                        {
                            "isin": "US0378331005",
                            "description": "Apple Inc.",
                            "valuation": 1000000
                        },
                        {
                            "isin": "US5949181045",
                            "description": "Microsoft Corp.",
                            "valuation": 2000000
                        },
                        {
                            "isin": "US88160R1014",
                            "description": "Tesla Inc.",
                            "valuation": 1500000
                        },
                        {
                            "isin": "US0231351067",
                            "description": "Amazon.com Inc.",
                            "valuation": 1500000
                        },
                        {
                            "isin": "US02079K1079",
                            "description": "Alphabet Inc.",
                            "valuation": 1000000
                        },
                        # Missing Meta Platforms
                        {
                            "isin": "US67066G1040",
                            "description": "NVIDIA Corp.",
                            "valuation": 2000000
                        }
                    ]
                }
            }
            mock_processor_instance.get_portfolio_value.return_value = 10000000
            mock_processor_instance.get_securities.return_value = mock_processor_instance.process.return_value["extraction_results"]["securities"]
            mock_processor_instance.get_asset_allocation.return_value = mock_processor_instance.process.return_value["extraction_results"]["asset_allocation"]
            mock_processor_instance.get_structured_products.return_value = []

            # Process the complex document
            result1 = self.processor.process_document(complex_document_path, output_dir=complex_output_dir)

            # Record corrections
            self.processor.record_user_correction(
                "portfolio_value", 10000000, 12000000  # Corrected portfolio value
            )

            self.processor.record_user_correction(
                "securities",
                mock_processor_instance.process.return_value["extraction_results"]["securities"],
                mock_processor_instance.process.return_value["extraction_results"]["securities"] + [
                    {
                        "isin": "US30303M1027",
                        "description": "Meta Platforms Inc.",
                        "valuation": 1000000
                    }
                ]
            )

            # Similar complex document extraction results (with similar errors)
            mock_processor_instance.process.return_value = {
                "extraction_results": {
                    "portfolio_value": 15000000,
                    "asset_allocation": [
                        {
                            "asset_class": "Equities",
                            "percentage": 70,
                            "value": 10500000
                        },
                        {
                            "asset_class": "Bonds",
                            "percentage": 20,
                            "value": 3000000
                        },
                        {
                            "asset_class": "Cash",
                            "percentage": 10,
                            "value": 1500000
                        }
                    ],
                    "securities": [
                        {
                            "isin": "US0378331005",
                            "description": "Apple Inc.",
                            "valuation": 1500000
                        },
                        {
                            "isin": "US5949181045",
                            "description": "Microsoft Corp.",
                            "valuation": 3000000
                        },
                        {
                            "isin": "US88160R1014",
                            "description": "Tesla Inc.",
                            "valuation": 2000000
                        },
                        {
                            "isin": "US0231351067",
                            "description": "Amazon.com Inc.",
                            "valuation": 2000000
                        },
                        {
                            "isin": "US02079K1079",
                            "description": "Alphabet Inc.",
                            "valuation": 1500000
                        },
                        # Missing Meta Platforms
                        {
                            "isin": "US67066G1040",
                            "description": "NVIDIA Corp.",
                            "valuation": 3000000
                        }
                    ]
                }
            }
            mock_processor_instance.get_portfolio_value.return_value = 15000000
            mock_processor_instance.get_securities.return_value = mock_processor_instance.process.return_value["extraction_results"]["securities"]
            mock_processor_instance.get_asset_allocation.return_value = mock_processor_instance.process.return_value["extraction_results"]["asset_allocation"]

            # Process the similar complex document
            result2 = self.processor.process_document(similar_complex_document_path, output_dir=similar_complex_output_dir)

            # Check that the AI applied the learned corrections to the similar document
            self.assertEqual(result2["extraction_results"]["portfolio_value"], 18000000)  # 15000000 * (12000000 / 10000000)
            self.assertEqual(len(result2["extraction_results"]["securities"]), 7)  # Should include Meta Platforms

            # Generate improvement suggestions
            suggestions = self.processor.generate_improvement_suggestions()

            # Print the results
            print("\nReal-World Scenario Test Results:")
            print("=================================")
            print(f"First document extraction result: {result1['extraction_results']['portfolio_value']}")
            print(f"Correction applied: 10000000 -> 12000000")
            print(f"Similar document extraction result after learning: {result2['extraction_results']['portfolio_value']}")
            print(f"First document securities count: {len(result1['extraction_results']['securities'])}")
            print(f"Correction applied: Added Meta Platforms")
            print(f"Similar document securities count after learning: {len(result2['extraction_results']['securities'])}")
            print("\nImprovement Suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"{i}. {suggestion}")

if __name__ == "__main__":
    unittest.main()
