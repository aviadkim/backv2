'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";

export default function DocumentAnalysisPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [isAsking, setIsAsking] = useState(false);
  const [tablePrompt, setTablePrompt] = useState('');
  const [customTable, setCustomTable] = useState<any[] | null>(null);
  const [isGeneratingTable, setIsGeneratingTable] = useState(false);
  const [mounted, setMounted] = useState(false);

  // State for document data
  const [documentData, setDocumentData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch document data from the API
  useEffect(() => {
    const fetchDocumentData = async () => {
      try {
        setLoading(true);

        // Get the document ID from the URL query parameters
        const urlParams = new URLSearchParams(window.location.search);
        const documentId = urlParams.get('documentId');

        if (!documentId) {
          // If no document ID is provided, use mock data
          setDocumentData({
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
          setLoading(false);
          return;
        }

        // Call the API to process the document
        const response = await fetch(`/api/documents/process?documentId=${documentId}`);

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        setDocumentData(data);
      } catch (error) {
        console.error('Error fetching document data:', error);
        setError('Failed to load document data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchDocumentData();
  }, []);

  // Only render on client-side to avoid hydration issues
  useEffect(() => {
    setMounted(true);
  }, []);

  const askQuestion = async () => {
    if (!question.trim()) return;

    setIsAsking(true);

    try {
      // Get the document ID from the URL query parameters
      const urlParams = new URLSearchParams(window.location.search);
      const documentId = urlParams.get('documentId') || 'doc_123';

      // Call the API to query the document
      const response = await fetch('/api/documents/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ documentId, question })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setAnswer(data.content);
    } catch (error) {
      console.error('Error querying document:', error);
      setAnswer('Error: Failed to process your question. Please try again.');
    } finally {
      setIsAsking(false);
    }
  };

  const generateTable = async () => {
    if (!tablePrompt.trim()) return;

    setIsGeneratingTable(true);
    setCustomTable(null);

    try {
      // Get the document ID from the URL query parameters
      const urlParams = new URLSearchParams(window.location.search);
      const documentId = urlParams.get('documentId') || 'doc_123';

      // Call the API to generate a table
      const response = await fetch('/api/documents/generate-table', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ documentId, prompt: tablePrompt })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setCustomTable(data.tableData);
    } catch (error) {
      console.error('Error generating table:', error);
      // Show an error message to the user
      alert('Failed to generate table. Please try again.');
    } finally {
      setIsGeneratingTable(false);
    }
  };

  // Return a simplified UI during server-side rendering or loading
  if (!mounted || loading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold mb-8">Document Analysis</h1>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="ml-4">Loading document analysis...</p>
        </div>
      </div>
    );
  }

  // Show error message if there was an error
  if (error || !documentData) {
    return (
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold mb-8">Document Analysis</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p className="font-medium">Error</p>
          <p>{error || 'Failed to load document data. Please try again.'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">Document Analysis</h1>

      <div className="mb-6">
        <Card>
          <CardHeader>
            <CardTitle>{documentData.title}</CardTitle>
            <CardDescription>Uploaded and processed successfully</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm font-medium text-gray-500">Date</p>
                <p>{documentData.date}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Pages</p>
                <p>{documentData.totalPages}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-500">Author</p>
                <p>{documentData.author}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="holdings">Holdings</TabsTrigger>
          <TabsTrigger value="financials">Financial Data</TabsTrigger>
          <TabsTrigger value="qa">Q&A</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Key Insights</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="list-disc pl-5 space-y-2">
                {documentData.keyInsights.map((insight, index) => (
                  <li key={index}>{insight}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="holdings" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Holdings</CardTitle>
              <CardDescription>Top 10 holdings as of {documentData.date}</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Company</TableHead>
                    <TableHead>Ticker</TableHead>
                    <TableHead className="text-right">Shares</TableHead>
                    <TableHead className="text-right">Value</TableHead>
                    <TableHead className="text-right">Weight</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documentData.holdings.map((holding, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-medium">{holding.name}</TableCell>
                      <TableCell>{holding.ticker}</TableCell>
                      <TableCell className="text-right">{holding.shares.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{holding.value}</TableCell>
                      <TableCell className="text-right">{holding.weight}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          <div className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle>Generate Custom Tables</CardTitle>
                <CardDescription>Create custom views of the portfolio data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={tablePrompt}
                      onChange={(e) => setTablePrompt(e.target.value)}
                      placeholder="e.g., Show sector allocation"
                      className="flex-grow px-3 py-2 border border-gray-300 rounded-md"
                      onKeyDown={(e) => e.key === 'Enter' && generateTable()}
                    />
                    <Button onClick={generateTable} disabled={isGeneratingTable || !tablePrompt.trim()}>
                      {isGeneratingTable ? 'Generating...' : 'Generate'}
                    </Button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" onClick={() => setTablePrompt('Show sector allocation')}>Sector Allocation</Button>
                    <Button variant="outline" size="sm" onClick={() => setTablePrompt('Show performance of holdings')}>Performance</Button>
                    <Button variant="outline" size="sm" onClick={() => setTablePrompt('Show quarterly results')}>Quarterly Results</Button>
                  </div>

                  {customTable && (
                    <div className="mt-4 border rounded-lg p-4">
                      <h3 className="text-lg font-medium mb-4">Custom Table</h3>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            {Object.keys(customTable[0]).map((key) => (
                              <TableHead key={key} className={key !== Object.keys(customTable[0])[0] ? 'text-right' : ''}>
                                {key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1').replace('_', ' ')}
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
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="financials" className="mt-6">
          <div className="space-y-6">
            {documentData.financialData.map((category, index) => (
              <Card key={index}>
                <CardHeader>
                  <CardTitle>{category.category}</CardTitle>
                </CardHeader>
                <CardContent>
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
                          <TableCell className="font-medium">{item.name}</TableCell>
                          <TableCell className="text-right">{item.value}</TableCell>
                          <TableCell className="text-right">{item.year}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="qa" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Ask Questions About This Document</CardTitle>
              <CardDescription>Get insights and information from the financial report</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., What was the revenue in 2024?"
                    className="flex-grow px-3 py-2 border border-gray-300 rounded-md"
                    onKeyDown={(e) => e.key === 'Enter' && askQuestion()}
                  />
                  <Button onClick={askQuestion} disabled={isAsking || !question.trim()}>
                    {isAsking ? 'Processing...' : 'Ask'}
                  </Button>
                </div>

                {answer && (
                  <div className="border rounded-lg p-4">
                    <h3 className="font-medium mb-2">Answer:</h3>
                    <p>{answer}</p>
                  </div>
                )}

                <div>
                  <h3 className="font-medium mb-2">Suggested Questions:</h3>
                  <div className="flex flex-wrap gap-2">
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What was the revenue in 2024?')}>Revenue</Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What are the profit margins?')}>Profit Margins</Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What are the top holdings in the portfolio?')}>Top Holdings</Button>
                    <Button variant="outline" size="sm" onClick={() => setQuestion('What is the cash position?')}>Cash Position</Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
