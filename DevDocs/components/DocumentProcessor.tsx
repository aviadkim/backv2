'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';

interface DocumentProcessorProps {
  documentId: string;
  documentName: string;
}

interface DocumentData {
  title: string;
  date: string;
  totalPages: number;
  author: string;
  financialData: {
    category: string;
    items: Array<{
      name: string;
      value: string;
      year: string;
    }>;
  }[];
  keyInsights: string[];
}

export default function DocumentProcessor({ documentId, documentName }: DocumentProcessorProps) {
  const [processing, setProcessing] = useState(false);
  const [processed, setProcessed] = useState(false);
  const [documentData, setDocumentData] = useState<DocumentData | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [question, setQuestion] = useState('');
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [customTable, setCustomTable] = useState<any[] | null>(null);
  const [customTablePrompt, setCustomTablePrompt] = useState('');
  const [generatingTable, setGeneratingTable] = useState(false);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  // Only render on client-side to avoid hydration issues
  useEffect(() => {
    setMounted(true);
  }, []);

  // Process the document when the component mounts
  useEffect(() => {
    processDocument();
  }, [documentId]);

  const processDocument = async () => {
    setProcessing(true);

    // In a real implementation, you would call your API to process the document
    // For now, we'll simulate processing with mock data
    setTimeout(() => {
      // Mock data for Messos financial document
      const mockData: DocumentData = {
        title: 'Messos Group Annual Financial Report',
        date: '2025-02-28',
        totalPages: 24,
        author: 'Messos Group Finance Department',
        financialData: [
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
        ],
        keyInsights: [
          'Revenue increased by 12.3% compared to previous year',
          'Gross margin improved from 41.2% to 43.4%',
          'Operating expenses were reduced by 2.1% through cost optimization initiatives',
          'Cash position strengthened with 14.5% increase in cash and equivalents',
          'Debt to equity ratio improved from 0.72 to 0.65',
          'Return on equity increased from 15.3% to 16.9%'
        ]
      };

      setDocumentData(mockData);
      setProcessed(true);
      setProcessing(false);
    }, 3000);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setAsking(true);
    setAnswer(null);

    // In a real implementation, you would call your API with the document ID and question
    // For now, we'll simulate a response based on the question
    setTimeout(() => {
      let response = '';

      // Simple pattern matching for demo purposes
      if (question.toLowerCase().includes('revenue')) {
        response = 'The total revenue for Messos Group in 2024 was €1,234,567,000, which represents a 12.3% increase compared to the previous year. This growth was primarily driven by expansion in European markets and the launch of new product lines.';
      } else if (question.toLowerCase().includes('profit margin') || question.toLowerCase().includes('profitability')) {
        response = 'Messos Group\'s net profit margin for 2024 was 15.2%, an improvement from 14.1% in the previous year. The gross margin was 43.4%, and the operating margin was 18.1%. These improvements were achieved through a combination of higher-margin product mix and operational efficiency initiatives.';
      } else if (question.toLowerCase().includes('debt') || question.toLowerCase().includes('liability')) {
        response = 'As of 2024, Messos Group has total liabilities of €1,234,567,000. The debt to equity ratio is 0.65, which improved from 0.72 in the previous year, indicating a strengthening financial position and reduced financial risk.';
      } else if (question.toLowerCase().includes('cash') || question.toLowerCase().includes('liquidity')) {
        response = 'Messos Group reported cash and equivalents of €456,789,000 in 2024, a 14.5% increase from the previous year. The company generated €234,567,000 in operating cash flow and has a current ratio of 2.3, indicating strong liquidity and ability to meet short-term obligations.';
      } else if (question.toLowerCase().includes('compare') || question.toLowerCase().includes('previous year')) {
        response = 'Compared to the previous year, Messos Group showed improvements across several key metrics in 2024:\n\n- Revenue: +12.3%\n- Gross Margin: +2.2 percentage points (from 41.2% to 43.4%)\n- Net Profit Margin: +1.1 percentage points (from 14.1% to 15.2%)\n- Return on Equity: +1.6 percentage points (from 15.3% to 16.9%)\n- Cash Position: +14.5%\n- Debt to Equity Ratio: Improved from 0.72 to 0.65';
      } else {
        response = 'Based on the Messos Group Annual Financial Report for 2024, the company demonstrated strong financial performance with revenue of €1,234,567,000 and net income of €187,654,000. The company maintains a solid balance sheet with total assets of €2,345,678,000 and a debt to equity ratio of 0.65. Key financial ratios indicate good profitability and financial stability.';
      }

      setAnswer(response);
      setAsking(false);
    }, 2000);
  };

  const generateCustomTable = async () => {
    if (!customTablePrompt.trim()) return;

    setGeneratingTable(true);
    setCustomTable(null);

    // In a real implementation, you would call your API with the document ID and prompt
    // For now, we'll simulate generating a table based on the prompt
    setTimeout(() => {
      let tableData = [];

      // Simple pattern matching for demo purposes
      if (customTablePrompt.toLowerCase().includes('quarterly') || customTablePrompt.toLowerCase().includes('quarter')) {
        tableData = [
          { quarter: 'Q1 2024', revenue: '€289,765,000', grossProfit: '€125,432,000', netIncome: '€42,345,000' },
          { quarter: 'Q2 2024', revenue: '€312,456,000', grossProfit: '€136,789,000', netIncome: '€46,789,000' },
          { quarter: 'Q3 2024', revenue: '€298,765,000', grossProfit: '€129,876,000', netIncome: '€43,987,000' },
          { quarter: 'Q4 2024', revenue: '€333,581,000', grossProfit: '€143,705,000', netIncome: '€54,533,000' },
          { quarter: 'Total 2024', revenue: '€1,234,567,000', grossProfit: '€535,802,000', netIncome: '€187,654,000' },
        ];
      } else if (customTablePrompt.toLowerCase().includes('year') || customTablePrompt.toLowerCase().includes('annual')) {
        tableData = [
          { year: '2020', revenue: '€876,543,000', grossProfit: '€350,617,000', netIncome: '€122,716,000' },
          { year: '2021', revenue: '€945,678,000', grossProfit: '€378,271,000', netIncome: '€132,395,000' },
          { year: '2022', revenue: '€1,023,456,000', grossProfit: '€409,382,000', netIncome: '€143,284,000' },
          { year: '2023', revenue: '€1,098,765,000', grossProfit: '€452,692,000', netIncome: '€153,827,000' },
          { year: '2024', revenue: '€1,234,567,000', grossProfit: '€535,802,000', netIncome: '€187,654,000' },
        ];
      } else if (customTablePrompt.toLowerCase().includes('ratio') || customTablePrompt.toLowerCase().includes('margin')) {
        tableData = [
          { year: '2020', grossMargin: '40.0%', operatingMargin: '16.2%', netMargin: '14.0%', roe: '14.1%', debtToEquity: '0.78' },
          { year: '2021', grossMargin: '40.0%', operatingMargin: '16.5%', netMargin: '14.0%', roe: '14.5%', debtToEquity: '0.76' },
          { year: '2022', grossMargin: '40.0%', operatingMargin: '16.8%', netMargin: '14.0%', roe: '14.8%', debtToEquity: '0.74' },
          { year: '2023', grossMargin: '41.2%', operatingMargin: '17.5%', netMargin: '14.0%', roe: '15.3%', debtToEquity: '0.72' },
          { year: '2024', grossMargin: '43.4%', operatingMargin: '18.1%', netMargin: '15.2%', roe: '16.9%', debtToEquity: '0.65' },
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

      setCustomTable(tableData);
      setGeneratingTable(false);
    }, 2500);
  };

  // Return a simplified UI during server-side rendering
  if (!mounted) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <h3 className="text-lg font-medium">Loading document processor...</h3>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!processed && processing) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <h3 className="text-lg font-medium">Processing document...</h3>
            <p className="text-gray-500 mt-2">Extracting data and insights from {documentName}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Document Analysis: {documentData?.title || documentName}</CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="financials">Financial Data</TabsTrigger>
              <TabsTrigger value="ask">Ask Questions</TabsTrigger>
              <TabsTrigger value="custom">Custom Tables</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="pt-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Document Information</h3>
                  <dl className="space-y-2">
                    <div className="flex justify-between">
                      <dt className="font-medium">Document Name:</dt>
                      <dd>{documentName}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">Document ID:</dt>
                      <dd>{documentId}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">Date:</dt>
                      <dd>{documentData?.date}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">Total Pages:</dt>
                      <dd>{documentData?.totalPages}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="font-medium">Author:</dt>
                      <dd>{documentData?.author}</dd>
                    </div>
                  </dl>
                </div>

                <div>
                  <h3 className="text-lg font-medium mb-4">Key Insights</h3>
                  <ul className="list-disc pl-5 space-y-2">
                    {documentData?.keyInsights.map((insight, index) => (
                      <li key={index}>{insight}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="financials" className="pt-4">
              <div className="space-y-6">
                {documentData?.financialData.map((category, index) => (
                  <div key={index}>
                    <h3 className="text-lg font-medium mb-4">{category.category}</h3>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Metric</TableHead>
                          <TableHead className="text-right">Value</TableHead>
                          <TableHead className="text-right">Year</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {category.items.map((item, itemIndex) => (
                          <TableRow key={itemIndex}>
                            <TableCell>{item.name}</TableCell>
                            <TableCell className="text-right">{item.value}</TableCell>
                            <TableCell className="text-right">{item.year}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="ask" className="pt-4">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Ask Questions About This Document</h3>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={question}
                      onChange={(e) => setQuestion(e.target.value)}
                      placeholder="e.g., What was the revenue in 2024?"
                      className="flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
                    />
                    <Button onClick={askQuestion} disabled={asking || !question.trim()}>
                      {asking ? 'Processing...' : 'Ask'}
                    </Button>
                  </div>
                </div>

                {(asking || answer) && (
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-2">Answer:</h4>
                    {asking ? (
                      <div className="flex items-center gap-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-blue-500"></div>
                        <span className="text-gray-500">Analyzing document...</span>
                      </div>
                    ) : (
                      <div className="whitespace-pre-line">{answer}</div>
                    )}
                  </div>
                )}

                <div>
                  <h4 className="font-medium mb-2">Suggested Questions:</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What was the total revenue in 2024?')}>
                      Revenue
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What are the profit margins?')}>
                      Profit Margins
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('How much debt does the company have?')}>
                      Debt
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What is the cash position?')}>
                      Cash Position
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('Compare performance to previous year')}>
                      YoY Comparison
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="custom" className="pt-4">
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Generate Custom Tables</h3>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={customTablePrompt}
                      onChange={(e) => setCustomTablePrompt(e.target.value)}
                      placeholder="e.g., Show quarterly revenue for 2024"
                      className="flex-grow px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      onKeyDown={(e) => e.key === 'Enter' && generateCustomTable()}
                    />
                    <Button onClick={generateCustomTable} disabled={generatingTable || !customTablePrompt.trim()}>
                      {generatingTable ? 'Generating...' : 'Generate'}
                    </Button>
                  </div>
                </div>

                {(generatingTable || customTable) && (
                  <div className="border rounded-lg p-4">
                    <h4 className="font-medium mb-4">Generated Table:</h4>
                    {generatingTable ? (
                      <div className="flex items-center justify-center py-8 gap-2">
                        <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-blue-500"></div>
                        <span className="text-gray-500">Generating table...</span>
                      </div>
                    ) : customTable && (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {Object.keys(customTable[0]).map((key) => (
                              <TableHead key={key} className={key !== Object.keys(customTable[0])[0] ? 'text-right' : ''}>
                                {key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}
                              </TableHead>
                            ))}
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {customTable.map((row, rowIndex) => (
                            <TableRow key={rowIndex}>
                              {Object.entries(row).map(([key, value], cellIndex) => (
                                <TableCell key={cellIndex} className={cellIndex !== 0 ? 'text-right' : ''}>
                                  {value as string}
                                </TableCell>
                              ))}
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    )}
                  </div>
                )}

                <div>
                  <h4 className="font-medium mb-2">Suggested Table Prompts:</h4>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" onClick={() => setCustomTablePrompt('Show quarterly financial data for 2024')}>
                      Quarterly Data
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setCustomTablePrompt('Show annual financial data for the last 5 years')}>
                      Annual Trends
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setCustomTablePrompt('Show financial ratios over time')}>
                      Financial Ratios
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setCustomTablePrompt('Compare 2023 vs 2024 performance')}>
                      Year Comparison
                    </Button>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
