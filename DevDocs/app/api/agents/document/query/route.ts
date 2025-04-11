import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { documentId, question } = await req.json();
    
    if (!documentId || !question) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }
    
    // In a real implementation, this would call the document agent
    // For now, we'll return a mock response
    
    // Mock response based on the question
    let response = '';
    
    if (question.toLowerCase().includes('revenue')) {
      response = 'The total revenue for Messos Group in 2024 was €1,234,567,000, which represents a 12.3% increase compared to the previous year. This growth was primarily driven by expansion in European markets and the launch of new product lines.';
    } else if (question.toLowerCase().includes('profit margin') || question.toLowerCase().includes('profitability')) {
      response = 'Messos Group\'s net profit margin for 2024 was 15.2%, an improvement from 14.1% in the previous year. The gross margin was 43.4%, and the operating margin was 18.1%. These improvements were achieved through a combination of higher-margin product mix and operational efficiency initiatives.';
    } else if (question.toLowerCase().includes('holdings') || question.toLowerCase().includes('portfolio')) {
      response = 'The top holdings in the Messos Group portfolio include Microsoft (12.9%), NVIDIA (10.8%), Apple (8.2%), Meta Platforms (7.3%), and Visa (6.4%). The portfolio is heavily weighted towards technology stocks, which account for 53.5% of the total holdings. The top 10 holdings represent 70% of the total portfolio value.';
    } else if (question.toLowerCase().includes('cash') || question.toLowerCase().includes('liquidity')) {
      response = 'Messos Group reported cash and equivalents of €456,789,000 in 2024, a 14.5% increase from the previous year. The company generated €234,567,000 in operating cash flow and has a current ratio of 2.3, indicating strong liquidity and ability to meet short-term obligations.';
    } else {
      response = 'Based on the Messos Group Annual Financial Report for 2024, the company demonstrated strong financial performance with revenue of €1,234,567,000 and net income of €187,654,000. The company maintains a solid balance sheet with total assets of €2,345,678,000 and a debt to equity ratio of 0.65. The portfolio is diversified with significant holdings in technology companies like Microsoft, NVIDIA, and Apple.';
    }
    
    return NextResponse.json({
      content: response,
      metadata: {
        model: 'gpt-4',
        document_id: documentId,
        document_name: 'messos.pdf'
      }
    });
  } catch (error) {
    console.error('Error processing document query:', error);
    return NextResponse.json(
      { error: 'Failed to process document query' },
      { status: 500 }
    );
  }
}
