"""
Script to test Tesseract OCR installation and agent functionality.
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
    """Run the OCR installation tests."""
    parser = argparse.ArgumentParser(description="Test OCR Installation")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--test", choices=["tesseract", "hebrew", "table", "all"], default="all", help="Test to run")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key and (args.test == "table" or args.test == "all"):
        print("Warning: OpenRouter API key is not provided. FinancialTableDetectorAgent test may fail.")
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Test Tesseract OCR installation
    if args.test in ["tesseract", "all"]:
        print("\nTesting Tesseract OCR installation...")
        test_script = current_dir / "test_tesseract_installation.py"
        if not test_script.exists():
            print(f"Error: Test script not found: {test_script}")
            return 1
        
        returncode = run_command(f"python {test_script}")
        if returncode != 0:
            print("Error: Tesseract OCR installation test failed.")
            if args.test == "tesseract":
                return 1
    
    # Test HebrewOCRAgent
    if args.test in ["hebrew", "all"]:
        print("\nTesting HebrewOCRAgent...")
        test_script = current_dir / "test_hebrew_ocr_agent_installation.py"
        if not test_script.exists():
            print(f"Error: Test script not found: {test_script}")
            return 1
        
        returncode = run_command(f"python {test_script}")
        if returncode != 0:
            print("Error: HebrewOCRAgent test failed.")
            if args.test == "hebrew":
                return 1
    
    # Test FinancialTableDetectorAgent
    if args.test in ["table", "all"] and api_key:
        print("\nTesting FinancialTableDetectorAgent...")
        test_script = current_dir / "test_financial_table_detector_installation.py"
        if not test_script.exists():
            print(f"Error: Test script not found: {test_script}")
            return 1
        
        returncode = run_command(f"python {test_script} --api-key {api_key}")
        if returncode != 0:
            print("Error: FinancialTableDetectorAgent test failed.")
            if args.test == "table":
                return 1
    
    print("\nAll tests completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
