import fs from 'fs';
import path from 'path';
import pdfParse from 'pdf-parse';

class PdfService {
  /**
   * Extract text from a PDF file
   * @param {string} filePath - Path to the PDF file
   * @returns {Promise<{text: string, metadata: object}>} - Extracted text and metadata
   */
  async extractTextFromPdf(filePath) {
    try {
      // Read the PDF file
      const dataBuffer = fs.readFileSync(filePath);

      // Parse the PDF
      const data = await pdfParse(dataBuffer);

      // Return the extracted text and metadata
      return {
        text: data.text,
        metadata: {
          pageCount: data.numpages,
          info: data.info,
          version: data.version
        }
      };
    } catch (error) {
      console.error('Error extracting text from PDF:', error);
      throw error;
    }
  }

  /**
   * Process a PDF file and extract structured data
   * @param {string} filePath - Path to the PDF file
   * @returns {Promise<object>} - Structured data extracted from the PDF
   */
  async processPdf(filePath) {
    try {
      // Extract text from the PDF
      const { text, metadata } = await this.extractTextFromPdf(filePath);

      // For demonstration purposes, we'll use a simple rule-based approach to extract data
      // In a real implementation, you would use more sophisticated techniques like NLP or AI

      // Extract financial data
      const financialData = this.extractFinancialData(text);

      // Extract holdings data
      const holdings = this.extractHoldings(text);

      // Extract key insights
      const keyInsights = this.extractKeyInsights(text);

      // Return the structured data
      return {
        title: this.extractTitle(text),
        date: this.extractDate(text),
        totalPages: metadata.pageCount,
        author: metadata.info?.Author || 'Unknown',
        financialData,
        holdings,
        keyInsights
      };
    } catch (error) {
      console.error('Error processing PDF:', error);
      throw error;
    }
  }

  /**
   * Extract the title from the PDF text
   * @param {string} text - PDF text
   * @returns {string} - Extracted title
   */
  extractTitle(text) {
    // Simple approach: assume the title is in the first few lines
    const lines = text.split('\n').filter(line => line.trim());
    return lines[0] || 'Unknown Document';
  }

  /**
   * Extract the date from the PDF text
   * @param {string} text - PDF text
   * @returns {string} - Extracted date
   */
  extractDate(text) {
    // Simple approach: look for date patterns
    const datePattern = /\d{4}-\d{2}-\d{2}|\d{2}\/\d{2}\/\d{4}|\d{2}\.\d{2}\.\d{4}/;
    const match = text.match(datePattern);
    return match ? match[0] : new Date().toISOString().split('T')[0];
  }

  /**
   * Extract financial data from the PDF text
   * @param {string} text - PDF text
   * @returns {Array<object>} - Extracted financial data
   */
  extractFinancialData(text) {
    // For demonstration purposes, we'll return mock data
    // In a real implementation, you would use regex patterns or NLP to extract this data

    // Check if the text contains financial data
    if (text.includes('Revenue') || text.includes('Income') || text.includes('Balance Sheet')) {
      return [
        {
          category: 'Income Statement',
          items: [
            { name: 'Revenue', value: '€1,234,567,000', year: '2024' },
            { name: 'Cost of Revenue', value: '€698,765,000', year: '2024' },
            { name: 'Gross Profit', value: '€535,802,000', year: '2024' },
            { name: 'Operating Expenses', value: '€312,456,000', year: '2024' },
            { name: 'Operating Income', value: '€223,346,000', year: '2024' },
            { name: 'Net Income', value: '€187,654,000', year: '2024' },
          ]
        },
        {
          category: 'Balance Sheet',
          items: [
            { name: 'Total Assets', value: '€2,345,678,000', year: '2024' },
            { name: 'Total Liabilities', value: '€1,234,567,000', year: '2024' },
            { name: 'Total Equity', value: '€1,111,111,000', year: '2024' },
            { name: 'Cash and Equivalents', value: '€456,789,000', year: '2024' },
            { name: 'Accounts Receivable', value: '€234,567,000', year: '2024' },
            { name: 'Inventory', value: '€345,678,000', year: '2024' },
          ]
        },
        {
          category: 'Cash Flow',
          items: [
            { name: 'Operating Cash Flow', value: '€234,567,000', year: '2024' },
            { name: 'Investing Cash Flow', value: '-€123,456,000', year: '2024' },
            { name: 'Financing Cash Flow', value: '-€45,678,000', year: '2024' },
            { name: 'Net Change in Cash', value: '€65,433,000', year: '2024' },
            { name: 'Free Cash Flow', value: '€111,111,000', year: '2024' },
          ]
        },
        {
          category: 'Financial Ratios',
          items: [
            { name: 'Gross Margin', value: '43.4%', year: '2024' },
            { name: 'Operating Margin', value: '18.1%', year: '2024' },
            { name: 'Net Profit Margin', value: '15.2%', year: '2024' },
            { name: 'Return on Assets', value: '8.0%', year: '2024' },
            { name: 'Return on Equity', value: '16.9%', year: '2024' },
            { name: 'Debt to Equity', value: '0.65', year: '2024' },
            { name: 'Current Ratio', value: '2.3', year: '2024' },
          ]
        }
      ];
    }

    return [];
  }

  /**
   * Extract holdings data from the PDF text
   * @param {string} text - PDF text
   * @returns {Array<object>} - Extracted holdings data
   */
  extractHoldings(text) {
    // For demonstration purposes, we'll return mock data
    // In a real implementation, you would use regex patterns or NLP to extract this data

    // Check if the text contains holdings data
    if (text.includes('Holdings') || text.includes('Portfolio') || text.includes('Stocks')) {
      return [
        { name: 'Apple Inc.', ticker: 'AAPL', shares: 15000, value: '€2,745,000', weight: '8.2%' },
        { name: 'Microsoft Corp', ticker: 'MSFT', shares: 12000, value: '€4,320,000', weight: '12.9%' },
        { name: 'Amazon.com Inc', ticker: 'AMZN', shares: 5000, value: '€1,875,000', weight: '5.6%' },
        { name: 'Alphabet Inc', ticker: 'GOOGL', shares: 4000, value: '€1,240,000', weight: '3.7%' },
        { name: 'Tesla Inc', ticker: 'TSLA', shares: 8000, value: '€1,680,000', weight: '5.0%' },
        { name: 'NVIDIA Corp', ticker: 'NVDA', shares: 6000, value: '€3,600,000', weight: '10.8%' },
        { name: 'Meta Platforms', ticker: 'META', shares: 7000, value: '€2,450,000', weight: '7.3%' },
        { name: 'Johnson & Johnson', ticker: 'JNJ', shares: 9000, value: '€1,530,000', weight: '4.6%' },
        { name: 'JPMorgan Chase', ticker: 'JPM', shares: 10000, value: '€1,850,000', weight: '5.5%' },
        { name: 'Visa Inc', ticker: 'V', shares: 8500, value: '€2,125,000', weight: '6.4%' },
      ];
    }

    return [];
  }

  /**
   * Extract key insights from the PDF text
   * @param {string} text - PDF text
   * @returns {Array<string>} - Extracted key insights
   */
  extractKeyInsights(text) {
    // For demonstration purposes, we'll return mock data
    // In a real implementation, you would use NLP or AI to extract insights

    return [
      'Revenue increased by 12.3% compared to previous year',
      'Gross margin improved from 41.2% to 43.4%',
      'Operating expenses were reduced by 2.1% through cost optimization initiatives',
      'Cash position strengthened with 14.5% increase in cash and equivalents',
      'Debt to equity ratio improved from 0.72 to 0.65',
      'Return on equity increased from 15.3% to 16.9%',
      'Top 10 holdings represent 70% of the portfolio value',
      'Technology sector accounts for 53.5% of total holdings'
    ];
  }
}

export default PdfService;
