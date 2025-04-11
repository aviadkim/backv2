import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { documentId, prompt } = await req.json();
    
    if (!documentId || !prompt) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }
    
    // In a real implementation, this would call the document agent
    // For now, we'll return a mock response
    
    // Mock table data based on the prompt
    let tableData = [];
    
    if (prompt.toLowerCase().includes('sector') || prompt.toLowerCase().includes('industry')) {
      tableData = [
        { sector: 'Technology', value: '€17,910,000', weight: '53.5%', holdings: 5 },
        { sector: 'Healthcare', value: '€3,280,000', weight: '9.8%', holdings: 2 },
        { sector: 'Financial Services', value: '€3,975,000', weight: '11.9%', holdings: 2 },
        { sector: 'Consumer Discretionary', value: '€4,555,000', weight: '13.6%', holdings: 3 },
        { sector: 'Communication Services', value: '€2,450,000', weight: '7.3%', holdings: 1 },
        { sector: 'Other', value: '€1,305,000', weight: '3.9%', holdings: 2 },
      ];
    } else if (prompt.toLowerCase().includes('performance') || prompt.toLowerCase().includes('return')) {
      tableData = [
        { holding: 'Apple Inc.', '1y_return': '32.4%', '3y_return': '87.6%', '5y_return': '345.2%' },
        { holding: 'Microsoft Corp', '1y_return': '28.7%', '3y_return': '112.3%', '5y_return': '378.9%' },
        { holding: 'Amazon.com Inc', '1y_return': '18.9%', '3y_return': '45.6%', '5y_return': '167.8%' },
        { holding: 'Alphabet Inc', '1y_return': '22.3%', '3y_return': '68.9%', '5y_return': '201.4%' },
        { holding: 'Tesla Inc', '1y_return': '-15.6%', '3y_return': '124.5%', '5y_return': '987.6%' },
        { holding: 'NVIDIA Corp', '1y_return': '187.5%', '3y_return': '573.2%', '5y_return': '1245.8%' },
        { holding: 'Meta Platforms', '1y_return': '43.2%', '3y_return': '28.7%', '5y_return': '98.7%' },
        { holding: 'Johnson & Johnson', '1y_return': '8.7%', '3y_return': '21.4%', '5y_return': '45.6%' },
        { holding: 'JPMorgan Chase', '1y_return': '17.8%', '3y_return': '42.3%', '5y_return': '87.9%' },
        { holding: 'Visa Inc', '1y_return': '15.6%', '3y_return': '38.9%', '5y_return': '112.3%' },
      ];
    } else if (prompt.toLowerCase().includes('quarterly') || prompt.toLowerCase().includes('quarter')) {
      tableData = [
        { quarter: 'Q1 2024', revenue: '€289,765,000', grossProfit: '€125,432,000', netIncome: '€42,345,000' },
        { quarter: 'Q2 2024', revenue: '€312,456,000', grossProfit: '€136,789,000', netIncome: '€46,789,000' },
        { quarter: 'Q3 2024', revenue: '€298,765,000', grossProfit: '€129,876,000', netIncome: '€43,987,000' },
        { quarter: 'Q4 2024', revenue: '€333,581,000', grossProfit: '€143,705,000', netIncome: '€54,533,000' },
        { quarter: 'Total 2024', revenue: '€1,234,567,000', grossProfit: '€535,802,000', netIncome: '€187,654,000' },
      ];
    } else {
      tableData = [
        { metric: 'Revenue', value2023: '€1,098,765,000', value2024: '€1,234,567,000', change: '+12.3%' },
        { metric: 'Gross Profit', value2023: '€452,692,000', value2024: '€535,802,000', change: '+18.4%' },
        { metric: 'Operating Income', value2023: '€192,284,000', value2024: '€223,346,000', change: '+16.2%' },
        { metric: 'Net Income', value2023: '€153,827,000', value2024: '€187,654,000', change: '+22.0%' },
        { metric: 'Total Assets', value2023: '€2,123,456,000', value2024: '€2,345,678,000', change: '+10.5%' },
        { metric: 'Total Equity', value2023: '€987,654,000', value2024: '€1,111,111,000', change: '+12.5%' },
      ];
    }
    
    return NextResponse.json({
      tableData,
      metadata: {
        model: 'gpt-4',
        document_id: documentId,
        document_name: 'messos.pdf'
      }
    });
  } catch (error) {
    console.error('Error generating table:', error);
    return NextResponse.json(
      { error: 'Failed to generate table' },
      { status: 500 }
    );
  }
}
