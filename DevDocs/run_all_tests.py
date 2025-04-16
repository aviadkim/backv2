"""
Script to run all tests in sequence.
"""
import os
import sys
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the output."""
    print(f"Running command: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
    
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"Error: {result.stderr}")
    else:
        print("Command completed successfully")
    
    return result

def main():
    """Main function to run all tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all tests")
    parser.add_argument("--pdf-file", default="messos.pdf", help="Path to the PDF file")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--output-dir", default="./test_results", help="Output directory")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Warning: No API key provided. Some tests may not work properly.")
        api_key_param = ""
    else:
        api_key_param = f"--api-key {api_key}"
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Step 1: Run enhanced PDF processor
    print("\n=== Step 1: Running Enhanced PDF Processor ===\n")
    pdf_processor_cmd = f"python enhanced_pdf_processor.py {args.pdf_file} {api_key_param}"
    run_command(pdf_processor_cmd)
    
    # Step 2: Run comprehensive ISIN analysis
    print("\n=== Step 2: Running Comprehensive ISIN Analysis ===\n")
    isin_analysis_cmd = f"python DevDocs/comprehensive_isin_analysis.py --text-file {args.pdf_file.replace('.pdf', '.txt')} --output-dir {output_dir}/isin_analysis"
    run_command(isin_analysis_cmd)
    
    # Step 3: Test all financial agents
    print("\n=== Step 3: Testing All Financial Agents ===\n")
    test_agents_cmd = f"python DevDocs/test_all_financial_agents.py --securities-file {output_dir}/isin_analysis/securities_table.csv {api_key_param} --output-dir {output_dir}/agent_tests"
    run_command(test_agents_cmd)
    
    # Step 4: Generate financial report
    print("\n=== Step 4: Generating Financial Report ===\n")
    report_cmd = f"python DevDocs/generate_financial_report.py --securities-file {output_dir}/isin_analysis/securities_table.csv --analysis-file {output_dir}/isin_analysis/portfolio_analysis.json --output-dir {output_dir}/financial_report"
    run_command(report_cmd)
    
    print("\n=== All Tests Completed ===\n")
    print(f"Results saved to {output_dir}")
    
    # Open the financial report in the browser
    report_path = Path(f"{output_dir}/financial_report/financial_report.html")
    if report_path.exists():
        print(f"\nFinancial report generated: {report_path}")
        print("You can open this file in your browser to view the report.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
