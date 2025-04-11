"""
Script to process a PDF file and extract its content.
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from services.document_service import DocumentService
from agents.document_agent import DocumentAgent

async def process_pdf(pdf_path):
    """Process a PDF file and extract its content."""
    print(f"Processing PDF: {pdf_path}")
    
    # Create document service
    document_service = DocumentService()
    
    # Ensure data directory exists
    os.makedirs("data/documents", exist_ok=True)
    
    # For demonstration purposes, we'll use a simple text extraction
    # In a real implementation, you would use a PDF parsing library
    
    # Mock PDF content extraction (in a real implementation, use PyPDF2, pdfplumber, etc.)
    pdf_content = """
    Messos Group Annual Financial Report
    
    Financial Year 2024
    
    Executive Summary:
    The Messos Group has demonstrated strong financial performance in 2024, with revenue increasing by 12.3% compared to the previous year. Our gross margin improved from 41.2% to 43.4%, and our operating expenses were reduced by 2.1% through cost optimization initiatives.
    
    Income Statement:
    Revenue: €1,234,567,000
    Cost of Revenue: €698,765,000
    Gross Profit: €535,802,000
    Operating Expenses: €312,456,000
    Operating Income: €223,346,000
    Net Income: €187,654,000
    
    Balance Sheet:
    Total Assets: €2,345,678,000
    Total Liabilities: €1,234,567,000
    Total Equity: €1,111,111,000
    Cash and Equivalents: €456,789,000
    Accounts Receivable: €234,567,000
    Inventory: €345,678,000
    
    Cash Flow:
    Operating Cash Flow: €234,567,000
    Investing Cash Flow: -€123,456,000
    Financing Cash Flow: -€45,678,000
    Net Change in Cash: €65,433,000
    Free Cash Flow: €111,111,000
    
    Financial Ratios:
    Gross Margin: 43.4%
    Operating Margin: 18.1%
    Net Profit Margin: 15.2%
    Return on Assets: 8.0%
    Return on Equity: 16.9%
    Debt to Equity: 0.65
    Current Ratio: 2.3
    
    Portfolio Holdings:
    1. Apple Inc. (AAPL): 15,000 shares, €2,745,000, 8.2%
    2. Microsoft Corp (MSFT): 12,000 shares, €4,320,000, 12.9%
    3. Amazon.com Inc (AMZN): 5,000 shares, €1,875,000, 5.6%
    4. Alphabet Inc (GOOGL): 4,000 shares, €1,240,000, 3.7%
    5. Tesla Inc (TSLA): 8,000 shares, €1,680,000, 5.0%
    6. NVIDIA Corp (NVDA): 6,000 shares, €3,600,000, 10.8%
    7. Meta Platforms (META): 7,000 shares, €2,450,000, 7.3%
    8. Johnson & Johnson (JNJ): 9,000 shares, €1,530,000, 4.6%
    9. JPMorgan Chase (JPM): 10,000 shares, €1,850,000, 5.5%
    10. Visa Inc (V): 8,500 shares, €2,125,000, 6.4%
    
    Sector Allocation:
    Technology: €17,910,000, 53.5%, 5 holdings
    Healthcare: €3,280,000, 9.8%, 2 holdings
    Financial Services: €3,975,000, 11.9%, 2 holdings
    Consumer Discretionary: €4,555,000, 13.6%, 3 holdings
    Communication Services: €2,450,000, 7.3%, 1 holding
    Other: €1,305,000, 3.9%, 2 holdings
    
    Performance Metrics:
    Apple Inc.: 1Y Return: 32.4%, 3Y Return: 87.6%, 5Y Return: 345.2%
    Microsoft Corp: 1Y Return: 28.7%, 3Y Return: 112.3%, 5Y Return: 378.9%
    Amazon.com Inc: 1Y Return: 18.9%, 3Y Return: 45.6%, 5Y Return: 167.8%
    Alphabet Inc: 1Y Return: 22.3%, 3Y Return: 68.9%, 5Y Return: 201.4%
    Tesla Inc: 1Y Return: -15.6%, 3Y Return: 124.5%, 5Y Return: 987.6%
    NVIDIA Corp: 1Y Return: 187.5%, 3Y Return: 573.2%, 5Y Return: 1245.8%
    Meta Platforms: 1Y Return: 43.2%, 3Y Return: 28.7%, 5Y Return: 98.7%
    Johnson & Johnson: 1Y Return: 8.7%, 3Y Return: 21.4%, 5Y Return: 45.6%
    JPMorgan Chase: 1Y Return: 17.8%, 3Y Return: 42.3%, 5Y Return: 87.9%
    Visa Inc: 1Y Return: 15.6%, 3Y Return: 38.9%, 5Y Return: 112.3%
    
    Quarterly Results:
    Q1 2024: Revenue: €289,765,000, Gross Profit: €125,432,000, Net Income: €42,345,000
    Q2 2024: Revenue: €312,456,000, Gross Profit: €136,789,000, Net Income: €46,789,000
    Q3 2024: Revenue: €298,765,000, Gross Profit: €129,876,000, Net Income: €43,987,000
    Q4 2024: Revenue: €333,581,000, Gross Profit: €143,705,000, Net Income: €54,533,000
    """
    
    # Save the document
    filename = os.path.basename(pdf_path)
    metadata = {
        "mime_type": "application/pdf",
        "original_path": pdf_path,
        "file_size": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
    }
    
    document = await document_service.save_document(filename, pdf_content, metadata)
    document_id = document["id"]
    
    print(f"Document saved with ID: {document_id}")
    
    # Process the document
    analysis_results = await document_service.process_document(document_id)
    print(f"Document processed: {json.dumps(analysis_results, indent=2)}")
    
    # Create a document agent
    agent_config = {
        "api_key": os.environ.get("OPENROUTER_API_KEY", "demo_key"),
        "document_id": document_id
    }
    agent = DocumentAgent(
        agent_id="doc_agent_1",
        name="Document Analysis Agent",
        description="Agent that analyzes documents and answers questions about them",
        config=agent_config
    )
    
    # Ask some questions about the document
    questions = [
        "What was the revenue in 2024?",
        "What are the top holdings in the portfolio?",
        "What is the sector allocation?",
        "What are the financial ratios?",
        "How did the company perform quarterly in 2024?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        response = await agent.process(question)
        print(f"Answer: {response.content}")
    
    return document_id

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_pdf.py <pdf_path>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    asyncio.run(process_pdf(pdf_path))
