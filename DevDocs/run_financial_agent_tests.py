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
    print("Running unit tests...")
    test_script = current_dir / "backend/tests/test_financial_agents.py"
    if not test_script.exists():
        print(f"Error: Test script not found: {test_script}")
        return 1
    
    returncode = run_command(f"python {test_script}")
    if returncode != 0:
        print("Error running unit tests.")
        return 1
    
    # Run the example script
    print("\nRunning example script...")
    example_script = current_dir / "backend/examples/financial_agents_example.py"
    if not example_script.exists():
        print(f"Error: Example script not found: {example_script}")
        return 1
    
    returncode = run_command(f"python {example_script} --api-key {api_key}")
    if returncode != 0:
        print("Error running example script.")
        return 1
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
