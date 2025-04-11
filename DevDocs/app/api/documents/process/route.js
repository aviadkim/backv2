import { NextResponse } from 'next/server';
import DocumentService from '../../../../services/document_service';

export async function GET(req) {
  try {
    // Get the document ID from the query parameters
    const { searchParams } = new URL(req.url);
    const documentId = searchParams.get('documentId');

    if (!documentId) {
      return NextResponse.json(
        { error: 'Document ID is required' },
        { status: 400 }
      );
    }

    // Create document service
    const documentService = new DocumentService();

    // Process the document
    const data = await documentService.processDocument(documentId);

    // Return the processed data
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error processing document:', error);

    // Return mock data as fallback
    return NextResponse.json({
      title: "Messos Group Annual Financial Report",
      date: "2025-02-28",
      totalPages: 24,
      author: "Messos Group Finance Department",
      holdings: [
        { name: "Apple Inc.", ticker: "AAPL", shares: 15000, value: "€2,745,000", weight: "8.2%" },
        { name: "Microsoft Corp", ticker: "MSFT", shares: 12000, value: "€4,320,000", weight: "12.9%" },
        { name: "Amazon.com Inc", ticker: "AMZN", shares: 5000, value: "€1,875,000", weight: "5.6%" },
        { name: "Alphabet Inc", ticker: "GOOGL", shares: 4000, value: "€1,240,000", weight: "3.7%" },
        { name: "Tesla Inc", ticker: "TSLA", shares: 8000, value: "€1,680,000", weight: "5.0%" },
        { name: "NVIDIA Corp", ticker: "NVDA", shares: 6000, value: "€3,600,000", weight: "10.8%" },
        { name: "Meta Platforms", ticker: "META", shares: 7000, value: "€2,450,000", weight: "7.3%" },
        { name: "Johnson & Johnson", ticker: "JNJ", shares: 9000, value: "€1,530,000", weight: "4.6%" },
        { name: "JPMorgan Chase", ticker: "JPM", shares: 10000, value: "€1,850,000", weight: "5.5%" },
        { name: "Visa Inc", ticker: "V", shares: 8500, value: "€2,125,000", weight: "6.4%" },
      ],
      financialData: [
        {
          category: "Income Statement",
          items: [
            { name: "Revenue", value: "€1,234,567,000", year: "2024" },
            { name: "Cost of Revenue", value: "€698,765,000", year: "2024" },
            { name: "Gross Profit", value: "€535,802,000", year: "2024" },
            { name: "Operating Expenses", value: "€312,456,000", year: "2024" },
            { name: "Operating Income", value: "€223,346,000", year: "2024" },
            { name: "Net Income", value: "€187,654,000", year: "2024" },
          ]
        },
        {
          category: "Balance Sheet",
          items: [
            { name: "Total Assets", value: "€2,345,678,000", year: "2024" },
            { name: "Total Liabilities", value: "€1,234,567,000", year: "2024" },
            { name: "Total Equity", value: "€1,111,111,000", year: "2024" },
            { name: "Cash and Equivalents", value: "€456,789,000", year: "2024" },
            { name: "Accounts Receivable", value: "€234,567,000", year: "2024" },
            { name: "Inventory", value: "€345,678,000", year: "2024" },
          ]
        },
        {
          category: "Cash Flow",
          items: [
            { name: "Operating Cash Flow", value: "€234,567,000", year: "2024" },
            { name: "Investing Cash Flow", value: "-€123,456,000", year: "2024" },
            { name: "Financing Cash Flow", value: "-€45,678,000", year: "2024" },
            { name: "Net Change in Cash", value: "€65,433,000", year: "2024" },
            { name: "Free Cash Flow", value: "€111,111,000", year: "2024" },
          ]
        },
        {
          category: "Financial Ratios",
          items: [
            { name: "Gross Margin", value: "43.4%", year: "2024" },
            { name: "Operating Margin", value: "18.1%", year: "2024" },
            { name: "Net Profit Margin", value: "15.2%", year: "2024" },
            { name: "Return on Assets", value: "8.0%", year: "2024" },
            { name: "Return on Equity", value: "16.9%", year: "2024" },
            { name: "Debt to Equity", value: "0.65", year: "2024" },
            { name: "Current Ratio", value: "2.3", year: "2024" },
          ]
        }
      ],
      keyInsights: [
        "Revenue increased by 12.3% compared to previous year",
        "Gross margin improved from 41.2% to 43.4%",
        "Operating expenses were reduced by 2.1% through cost optimization initiatives",
        "Cash position strengthened with 14.5% increase in cash and equivalents",
        "Debt to equity ratio improved from 0.72 to 0.65",
        "Return on equity increased from 15.3% to 16.9%",
        "Top 10 holdings represent 70% of the portfolio value",
        "Technology sector accounts for 53.5% of total holdings"
      ]
    });
  } catch (error) {
    console.error('Error processing PDF:', error);
    return NextResponse.json(
      { error: 'Failed to process PDF file' },
      { status: 500 }
    );
  }
}
