import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Upload, FileText, Check, AlertCircle } from "lucide-react";
import { 
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface FinancialDocumentAnalysisProps {
  onAnalyze: (file: File) => Promise<any>;
}

export default function FinancialDocumentAnalysis({ onAnalyze }: FinancialDocumentAnalysisProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please select a file to analyze");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const results = await onAnalyze(file);
      setAnalysisResults(results);
    } catch (err) {
      setError(`Analysis failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Format currency values
  const formatCurrency = (value: string | number) => {
    const numValue = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.-]+/g, "")) : value;
    
    if (isNaN(numValue)) return value;
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(numValue);
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Financial Document Analysis</CardTitle>
          <CardDescription>
            Upload a financial document to extract key information and insights
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <Input
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt"
                onChange={handleFileChange}
                className="flex-1"
              />
              <Button 
                onClick={handleAnalyze} 
                disabled={!file || isAnalyzing}
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <FileText className="mr-2 h-4 w-4" />
                    Analyze Document
                  </>
                )}
              </Button>
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span>{error}</span>
                </div>
              </div>
            )}
            
            {file && !isAnalyzing && !error && !analysisResults && (
              <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded relative">
                <div className="flex">
                  <Upload className="h-5 w-5 mr-2" />
                  <span>Ready to analyze: {file.name}</span>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      {analysisResults && (
        <Tabs defaultValue="summary" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="financial">Financial Data</TabsTrigger>
            <TabsTrigger value="statements">Statements</TabsTrigger>
            <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
          </TabsList>
          
          {/* Summary Tab */}
          <TabsContent value="summary" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Document Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-medium">Document Type</h3>
                    <p>{analysisResults.document_type || "Financial Document"}</p>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-medium">Key Insights</h3>
                    <div className="mt-2 space-y-2">
                      {analysisResults.summary ? (
                        <p className="text-gray-700">{analysisResults.summary}</p>
                      ) : (
                        <p className="text-gray-500 italic">No summary available</p>
                      )}
                    </div>
                  </div>
                  
                  {analysisResults.insights && analysisResults.insights.length > 0 && (
                    <div>
                      <h3 className="text-lg font-medium">Detailed Insights</h3>
                      <ul className="mt-2 space-y-2 list-disc pl-5">
                        {analysisResults.insights.map((insight: any, index: number) => (
                          <li key={index} className="text-gray-700">
                            <span className="font-medium">{insight.topic}:</span> {insight.insight}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          {/* Financial Data Tab */}
          <TabsContent value="financial" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Financial Figures</CardTitle>
              </CardHeader>
              <CardContent>
                {analysisResults.financial_figures && analysisResults.financial_figures.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Value</TableHead>
                        <TableHead>Context</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {analysisResults.financial_figures.map((figure: any, index: number) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{figure.name}</TableCell>
                          <TableCell>{formatCurrency(figure.value)}</TableCell>
                          <TableCell className="text-sm text-gray-500">{figure.context}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-gray-500 italic">No financial figures extracted</p>
                )}
              </CardContent>
            </Card>
            
            {analysisResults.financial_metrics && Object.keys(analysisResults.financial_metrics).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Financial Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="profitability" className="w-full">
                    <TabsList className="grid w-full grid-cols-6">
                      <TabsTrigger value="profitability">Profitability</TabsTrigger>
                      <TabsTrigger value="liquidity">Liquidity</TabsTrigger>
                      <TabsTrigger value="solvency">Solvency</TabsTrigger>
                      <TabsTrigger value="valuation">Valuation</TabsTrigger>
                      <TabsTrigger value="growth">Growth</TabsTrigger>
                      <TabsTrigger value="efficiency">Efficiency</TabsTrigger>
                    </TabsList>
                    
                    {Object.entries(analysisResults.financial_metrics).map(([category, metrics]: [string, any]) => (
                      <TabsContent key={category} value={category} className="space-y-4">
                        {metrics.length > 0 ? (
                          <Table>
                            <TableHeader>
                              <TableRow>
                                <TableHead>Metric</TableHead>
                                <TableHead>Value</TableHead>
                                <TableHead>Context</TableHead>
                              </TableRow>
                            </TableHeader>
                            <TableBody>
                              {metrics.map((metric: any, index: number) => (
                                <TableRow key={index}>
                                  <TableCell className="font-medium">{metric.label}</TableCell>
                                  <TableCell>{metric.value}</TableCell>
                                  <TableCell className="text-sm text-gray-500">{metric.context}</TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        ) : (
                          <p className="text-gray-500 italic">No {category} metrics available</p>
                        )}
                      </TabsContent>
                    ))}
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </TabsContent>
          
          {/* Statements Tab */}
          <TabsContent value="statements" className="space-y-6">
            {analysisResults.financial_statements && (
              <Tabs defaultValue="income_statement" className="w-full">
                <TabsList className="grid w-full grid-cols-3">
                  <TabsTrigger value="income_statement">Income Statement</TabsTrigger>
                  <TabsTrigger value="balance_sheet">Balance Sheet</TabsTrigger>
                  <TabsTrigger value="cash_flow">Cash Flow</TabsTrigger>
                </TabsList>
                
                <TabsContent value="income_statement">
                  <Card>
                    <CardHeader>
                      <CardTitle>Income Statement</CardTitle>
                      {analysisResults.financial_statements.income_statement.period && (
                        <CardDescription>
                          Period: {analysisResults.financial_statements.income_statement.period}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      {analysisResults.financial_statements.income_statement.line_items && 
                       analysisResults.financial_statements.income_statement.line_items.length > 0 ? (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Item</TableHead>
                              <TableHead>Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {analysisResults.financial_statements.income_statement.line_items.map((item: any, index: number) => (
                              <TableRow key={index}>
                                <TableCell className="font-medium">{item.label}</TableCell>
                                <TableCell>{item.value}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      ) : (
                        <p className="text-gray-500 italic">No income statement data available</p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="balance_sheet">
                  <Card>
                    <CardHeader>
                      <CardTitle>Balance Sheet</CardTitle>
                      {analysisResults.financial_statements.balance_sheet.period && (
                        <CardDescription>
                          As of: {analysisResults.financial_statements.balance_sheet.period}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      {analysisResults.financial_statements.balance_sheet.line_items && 
                       analysisResults.financial_statements.balance_sheet.line_items.length > 0 ? (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Item</TableHead>
                              <TableHead>Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {analysisResults.financial_statements.balance_sheet.line_items.map((item: any, index: number) => (
                              <TableRow key={index}>
                                <TableCell className="font-medium">{item.label}</TableCell>
                                <TableCell>{item.value}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      ) : (
                        <p className="text-gray-500 italic">No balance sheet data available</p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="cash_flow">
                  <Card>
                    <CardHeader>
                      <CardTitle>Cash Flow Statement</CardTitle>
                      {analysisResults.financial_statements.cash_flow.period && (
                        <CardDescription>
                          Period: {analysisResults.financial_statements.cash_flow.period}
                        </CardDescription>
                      )}
                    </CardHeader>
                    <CardContent>
                      {analysisResults.financial_statements.cash_flow.line_items && 
                       analysisResults.financial_statements.cash_flow.line_items.length > 0 ? (
                        <Table>
                          <TableHeader>
                            <TableRow>
                              <TableHead>Item</TableHead>
                              <TableHead>Value</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {analysisResults.financial_statements.cash_flow.line_items.map((item: any, index: number) => (
                              <TableRow key={index}>
                                <TableCell className="font-medium">{item.label}</TableCell>
                                <TableCell>{item.value}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      ) : (
                        <p className="text-gray-500 italic">No cash flow data available</p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </TabsContent>
          
          {/* Portfolio Tab */}
          <TabsContent value="portfolio" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Portfolio Holdings</CardTitle>
              </CardHeader>
              <CardContent>
                {analysisResults.portfolio_data && analysisResults.portfolio_data.length > 0 ? (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Security</TableHead>
                        <TableHead>ISIN/Ticker</TableHead>
                        <TableHead>Quantity</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Value</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {analysisResults.portfolio_data.map((holding: any, index: number) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{holding.security}</TableCell>
                          <TableCell>{holding.isin || holding.ticker || '-'}</TableCell>
                          <TableCell>{holding.quantity || '-'}</TableCell>
                          <TableCell>{holding.price ? formatCurrency(holding.price) : '-'}</TableCell>
                          <TableCell>{holding.value ? formatCurrency(holding.value) : '-'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                ) : (
                  <p className="text-gray-500 italic">No portfolio data extracted</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
