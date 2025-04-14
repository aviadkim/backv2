"""
Script to run the financial agent tests.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and print the output."""
    print(f"Running command: {command}")
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )
    stdout, stderr = process.communicate()

    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    return process.returncode

def main():
    """Run the financial agent tests."""
    parser = argparse.ArgumentParser(description="Run Financial Agent Tests")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--test-type", choices=["unit", "example", "agent", "all"], default="all", help="Type of tests to run")
    parser.add_argument("--agent", choices=["document_preprocessor", "hebrew_ocr", "isin_extractor", "financial_table_detector", "document_merge", "all"], default="all", help="Agent to test")
    args = parser.parse_args()

    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: OpenRouter API key is not provided. Some features may not work properly.")
    else:
        # Set the API key in the environment
        os.environ["OPENROUTER_API_KEY"] = api_key

    # Get the current directory
    current_dir = Path(__file__).parent

    # Run the unit tests
    if args.test_type in ["unit", "all"]:
        print("Running unit tests...")
        test_script = current_dir / "backend/tests/test_financial_agents.py"
        if not test_script.exists():
            print(f"Warning: Unit test script not found: {test_script}")
        else:
            returncode = run_command(f"python {test_script}")
            if returncode != 0:
                print("Error running unit tests.")
                if args.test_type == "unit":
                    return 1

    # Run the example script
    if args.test_type in ["example", "all"]:
        print("\nRunning example script...")
        example_script = current_dir / "backend/examples/financial_agents_example.py"
        if not example_script.exists():
            print(f"Warning: Example script not found: {example_script}")
        else:
            returncode = run_command(f"python {example_script} --api-key {api_key}")
            if returncode != 0:
                print("Error running example script.")
                if args.test_type == "example":
                    return 1

    # Run the agent tests
    if args.test_type in ["agent", "all"]:
        print("\nRunning agent tests...")

        # Test DocumentPreprocessorAgent
        if args.agent in ["document_preprocessor", "all"]:
            print("\nTesting DocumentPreprocessorAgent...")
            test_script = current_dir / "test_document_preprocessor.py"
            if not test_script.exists():
                print(f"Warning: Test script not found: {test_script}")
            else:
                returncode = run_command(f"python {test_script}")
                if returncode != 0:
                    print("Error testing DocumentPreprocessorAgent.")

        # Test HebrewOCRAgent
        if args.agent in ["hebrew_ocr", "all"]:
            print("\nTesting HebrewOCRAgent...")
            test_script = current_dir / "test_hebrew_ocr.py"
            if not test_script.exists():
                print(f"Warning: Test script not found: {test_script}")
            else:
                returncode = run_command(f"python {test_script}")
                if returncode != 0:
                    print("Error testing HebrewOCRAgent.")

        # Test ISINExtractorAgent
        if args.agent in ["isin_extractor", "all"]:
            print("\nTesting ISINExtractorAgent...")
            test_script = current_dir / "test_isin_extractor.py"
            if not test_script.exists():
                print(f"Warning: Test script not found: {test_script}")
            else:
                returncode = run_command(f"python {test_script}")
                if returncode != 0:
                    print("Error testing ISINExtractorAgent.")

        # Test FinancialTableDetectorAgent
        if args.agent in ["financial_table_detector", "all"]:
            print("\nTesting FinancialTableDetectorAgent...")
            test_script = current_dir / "test_financial_table_detector.py"
            if not test_script.exists():
                print(f"Warning: Test script not found: {test_script}")
            else:
                returncode = run_command(f"python {test_script} --api-key {api_key}")
                if returncode != 0:
                    print("Error testing FinancialTableDetectorAgent.")

        # Test DocumentMergeAgent
        if args.agent in ["document_merge", "all"]:
            print("\nTesting DocumentMergeAgent...")
            test_script = current_dir / "test_document_merge_evaluation_v2.py"
            if not test_script.exists():
                print(f"Warning: Test script not found: {test_script}")
            else:
                returncode = run_command(f"python {test_script}")
                if returncode != 0:
                    print("Error testing DocumentMergeAgent.")

    print("\nAll tests completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
