import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, FileDown, Check, AlertCircle } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { DatePicker } from "@/components/ui/date-picker";

interface FinancialReportGeneratorProps {
  onGenerateReport: (reportType: string, options: any) => Promise<any>;
  portfolios: Array<{ id: string; name: string }>;
}

export default function FinancialReportGenerator({ onGenerateReport, portfolios }: FinancialReportGeneratorProps) {
  const [reportType, setReportType] = useState("portfolio");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedReport, setGeneratedReport] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Portfolio report options
  const [selectedPortfolioId, setSelectedPortfolioId] = useState("");
  const [includePerformance, setIncludePerformance] = useState(true);
  const [includeRisk, setIncludeRisk] = useState(true);
  const [includeRecommendations, setIncludeRecommendations] = useState(true);
  
  // Financial statement report options
  const [statementType, setStatementType] = useState("income_statement");
  const [periodStart, setPeriodStart] = useState<Date | undefined>(undefined);
  const [periodEnd, setPeriodEnd] = useState<Date | undefined>(undefined);
  const [comparePreviousPeriod, setComparePreviousPeriod] = useState(false);
  
  const handleGenerateReport = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      let options = {};
      
      if (reportType === "portfolio") {
        if (!selectedPortfolioId) {
          setError("Please select a portfolio");
          setIsGenerating(false);
          return;
        }
        
        options = {
          portfolioId: selectedPortfolioId,
          includePerformance,
          includeRisk,
          includeRecommendations
        };
      } else if (reportType === "financial_statement") {
        if (!statementType) {
          setError("Please select a statement type");
          setIsGenerating(false);
          return;
        }
        
        if (!periodStart || !periodEnd) {
          setError("Please select start and end dates");
          setIsGenerating(false);
          return;
        }
        
        options = {
          statementType,
          periodStart: periodStart.toISOString(),
          periodEnd: periodEnd.toISOString(),
          comparePreviousPeriod
        };
      }
      
      const report = await onGenerateReport(reportType, options);
      setGeneratedReport(report);
    } catch (err) {
      setError(`Report generation failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleDownloadReport = () => {
    if (!generatedReport) return;
    
    // Create a blob from the report data
    const reportBlob = new Blob([JSON.stringify(generatedReport, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(reportBlob);
    
    // Create a link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportType}_report_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Financial Report Generator</CardTitle>
          <CardDescription>
            Generate comprehensive financial reports for analysis and decision-making
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="portfolio" className="w-full" onValueChange={setReportType}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="portfolio">Portfolio Report</TabsTrigger>
              <TabsTrigger value="financial_statement">Financial Statement</TabsTrigger>
              <TabsTrigger value="tax">Tax Report</TabsTrigger>
            </TabsList>
            
            {/* Portfolio Report Options */}
            <TabsContent value="portfolio" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="portfolio">Select Portfolio</Label>
                <Select value={selectedPortfolioId} onValueChange={setSelectedPortfolioId}>
                  <SelectTrigger id="portfolio">
                    <SelectValue placeholder="Select a portfolio" />
                  </SelectTrigger>
                  <SelectContent>
                    {portfolios.map((portfolio) => (
                      <SelectItem key={portfolio.id} value={portfolio.id}>
                        {portfolio.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Report Options</Label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="include-performance" 
                      checked={includePerformance} 
                      onCheckedChange={(checked) => setIncludePerformance(checked as boolean)}
                    />
                    <Label htmlFor="include-performance">Include Performance Analysis</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="include-risk" 
                      checked={includeRisk} 
                      onCheckedChange={(checked) => setIncludeRisk(checked as boolean)}
                    />
                    <Label htmlFor="include-risk">Include Risk Metrics</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="include-recommendations" 
                      checked={includeRecommendations} 
                      onCheckedChange={(checked) => setIncludeRecommendations(checked as boolean)}
                    />
                    <Label htmlFor="include-recommendations">Include Investment Recommendations</Label>
                  </div>
                </div>
              </div>
            </TabsContent>
            
            {/* Financial Statement Options */}
            <TabsContent value="financial_statement" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="statement-type">Statement Type</Label>
                <Select value={statementType} onValueChange={setStatementType}>
                  <SelectTrigger id="statement-type">
                    <SelectValue placeholder="Select statement type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="income_statement">Income Statement</SelectItem>
                    <SelectItem value="balance_sheet">Balance Sheet</SelectItem>
                    <SelectItem value="cash_flow">Cash Flow Statement</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="period-start">Period Start</Label>
                  <DatePicker 
                    date={periodStart} 
                    setDate={setPeriodStart} 
                    className="w-full"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="period-end">Period End</Label>
                  <DatePicker 
                    date={periodEnd} 
                    setDate={setPeriodEnd} 
                    className="w-full"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="compare-previous" 
                    checked={comparePreviousPeriod} 
                    onCheckedChange={(checked) => setComparePreviousPeriod(checked as boolean)}
                  />
                  <Label htmlFor="compare-previous">Compare with Previous Period</Label>
                </div>
              </div>
            </TabsContent>
            
            {/* Tax Report Options */}
            <TabsContent value="tax" className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tax-year">Tax Year</Label>
                <Select>
                  <SelectTrigger id="tax-year">
                    <SelectValue placeholder="Select tax year" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="2023">2023</SelectItem>
                    <SelectItem value="2022">2022</SelectItem>
                    <SelectItem value="2021">2021</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Report Options</Label>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox id="include-realized-gains" />
                    <Label htmlFor="include-realized-gains">Include Realized Gains/Losses</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox id="include-dividend-income" />
                    <Label htmlFor="include-dividend-income">Include Dividend Income</Label>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <Checkbox id="include-interest-income" />
                    <Label htmlFor="include-interest-income">Include Interest Income</Label>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
          
          <div className="mt-6 space-y-4">
            <Button 
              onClick={handleGenerateReport} 
              disabled={isGenerating}
              className="w-full"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Report...
                </>
              ) : (
                <>
                  Generate Report
                </>
              )}
            </Button>
            
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
                <div className="flex">
                  <AlertCircle className="h-5 w-5 mr-2" />
                  <span>{error}</span>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
      
      {generatedReport && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <div>
              <CardTitle>Generated Report</CardTitle>
              <CardDescription>
                {new Date(generatedReport.generated_at).toLocaleString()}
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={handleDownloadReport}>
              <FileDown className="mr-2 h-4 w-4" />
              Download
            </Button>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-sm overflow-auto max-h-96">
                {JSON.stringify(generatedReport, null, 2)}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
