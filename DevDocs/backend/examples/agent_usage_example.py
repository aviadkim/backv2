"""
Example of how to use the agents in a Python script.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the agents
sys.path.append(str(Path(__file__).parent.parent))

from agents.agent_manager import AgentManager
from agents.document_preprocessor_agent import DocumentPreprocessorAgent
from agents.hebrew_ocr_agent import HebrewOCRAgent
from agents.isin_extractor_agent import ISINExtractorAgent
from agents.financial_entity_extractor_agent import FinancialEntityExtractorAgent
from agents.table_extractor_agent import TableExtractorAgent
from agents.financial_report_generator_agent import FinancialReportGeneratorAgent
from agents.portfolio_analysis_agent import PortfolioAnalysisAgent

def main():
    """Example of how to use the agents."""
    parser = argparse.ArgumentParser(description="Agent Usage Example")
    parser.add_argument("--api-key", help="OpenRouter API key")
    parser.add_argument("--agent", choices=["preprocessor", "ocr", "isin", "entity", "table", "report", "portfolio", "all"], default="all", help="Agent to use")
    args = parser.parse_args()
    
    # Get API key from arguments or environment
    api_key = args.api_key or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OpenRouter API key is required. Provide it with --api-key or set OPENROUTER_API_KEY environment variable.")
        return 1
    
    # Create agent manager
    manager = AgentManager(api_key=api_key)
    
    # Create agents based on the selected agent
    if args.agent == "preprocessor" or args.agent == "all":
        manager.create_agent(
            "preprocessor",
            DocumentPreprocessorAgent,
            output_dir="./output/preprocessed"
        )
        print("Created DocumentPreprocessorAgent")
    
    if args.agent == "ocr" or args.agent == "all":
        manager.create_agent(
            "ocr",
            HebrewOCRAgent
        )
        print("Created HebrewOCRAgent")
    
    if args.agent == "isin" or args.agent == "all":
        manager.create_agent(
            "isin_extractor",
            ISINExtractorAgent
        )
        print("Created ISINExtractorAgent")
    
    if args.agent == "entity" or args.agent == "all":
        manager.create_agent(
            "entity_extractor",
            FinancialEntityExtractorAgent
        )
        print("Created FinancialEntityExtractorAgent")
    
    if args.agent == "table" or args.agent == "all":
        manager.create_agent(
            "table_extractor",
            TableExtractorAgent,
            output_dir="./output/tables"
        )
        print("Created TableExtractorAgent")
    
    if args.agent == "report" or args.agent == "all":
        manager.create_agent(
            "report_generator",
            FinancialReportGeneratorAgent,
            output_dir="./output/reports"
        )
        print("Created FinancialReportGeneratorAgent")
    
    if args.agent == "portfolio" or args.agent == "all":
        manager.create_agent(
            "portfolio_analyzer",
            PortfolioAnalysisAgent
        )
        print("Created PortfolioAnalysisAgent")
    
    # Example of using the agents
    if args.agent == "preprocessor":
        print("\nExample of using DocumentPreprocessorAgent:")
        print("manager.run_agent('preprocessor', 'path/to/document.pdf')")
    
    elif args.agent == "ocr":
        print("\nExample of using HebrewOCRAgent:")
        print("manager.run_agent('ocr', 'path/to/image.png', lang='heb+eng')")
    
    elif args.agent == "isin":
        print("\nExample of using ISINExtractorAgent:")
        print("manager.run_agent('isin_extractor', 'Text containing ISIN codes like US0378331005')")
    
    elif args.agent == "entity":
        print("\nExample of using FinancialEntityExtractorAgent:")
        print("manager.run_agent('entity_extractor', 'Text containing financial entities like $100 million and 5%')")
    
    elif args.agent == "table":
        print("\nExample of using TableExtractorAgent:")
        print("manager.run_agent('table_extractor', 'path/to/table_image.png')")
    
    elif args.agent == "report":
        print("\nExample of using FinancialReportGeneratorAgent:")
        print("manager.run_agent('report_generator', financial_data, report_type='summary')")
    
    elif args.agent == "portfolio":
        print("\nExample of using PortfolioAnalysisAgent:")
        print("manager.run_agent('portfolio_analyzer', portfolio_data, analysis_type='basic')")
    
    elif args.agent == "all":
        print("\nExample of using a pipeline:")
        print("""
pipeline = [
    {
        "agent_id": "preprocessor",
        "params": {"enhance_text": True},
        "output_key": "preprocessed"
    },
    {
        "agent_id": "ocr",
        "params": {"lang": "heb+eng"},
        "output_key": "ocr_results"
    },
    {
        "agent_id": "isin_extractor",
        "params": {"validate": True},
        "output_key": "isin_results"
    }
]

results = manager.run_pipeline(pipeline, "path/to/document.pdf")
        """)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
