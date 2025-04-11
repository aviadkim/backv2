import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import FinancialDashboard from '@/components/FinancialDashboard';
import FinancialDocumentAnalysis from '@/components/FinancialDocumentAnalysis';
import FinancialReportGenerator from '@/components/FinancialReportGenerator';

// This would normally come from an API call
const mockPortfolioData = [
  {
    security: "Apple Inc.",
    isin: "US0378331005",
    ticker: "AAPL",
    asset_class: "Equity",
    sector: "Technology",
    region: "North America",
    currency: "USD",
    quantity: 100,
    price: 175.25,
    value: 17525,
    weight: 15.2,
    cost: 15000,
    gain_loss: 2525,
    gain_loss_percent: 16.83
  },
  {
    security: "Microsoft Corporation",
    isin: "US5949181045",
    ticker: "MSFT",
    asset_class: "Equity",
    sector: "Technology",
    region: "North America",
    currency: "USD",
    quantity: 50,
    price: 325.75,
    value: 16287.5,
    weight: 14.1,
    cost: 14000,
    gain_loss: 2287.5,
    gain_loss_percent: 16.34
  },
  {
    security: "Amazon.com Inc.",
    isin: "US0231351067",
    ticker: "AMZN",
    asset_class: "Equity",
    sector: "Consumer Discretionary",
    region: "North America",
    currency: "USD",
    quantity: 40,
    price: 132.5,
    value: 5300,
    weight: 4.6,
    cost: 4800,
    gain_loss: 500,
    gain_loss_percent: 10.42
  },
  {
    security: "Vanguard Total Stock Market ETF",
    isin: "US9229087690",
    ticker: "VTI",
    asset_class: "ETF",
    sector: "Diversified",
    region: "North America",
    currency: "USD",
    quantity: 200,
    price: 220.35,
    value: 44070,
    weight: 38.2,
    cost: 40000,
    gain_loss: 4070,
    gain_loss_percent: 10.18
  },
  {
    security: "iShares Core MSCI EAFE ETF",
    isin: "US4642882736",
    ticker: "IEFA",
    asset_class: "ETF",
    sector: "Diversified",
    region: "International",
    currency: "USD",
    quantity: 300,
    price: 68.25,
    value: 20475,
    weight: 17.8,
    cost: 19500,
    gain_loss: 975,
    gain_loss_percent: 5.0
  },
  {
    security: "Vanguard Total Bond Market ETF",
    isin: "US9219378356",
    ticker: "BND",
    asset_class: "Bond",
    sector: "Fixed Income",
    region: "North America",
    currency: "USD",
    quantity: 150,
    price: 72.5,
    value: 10875,
    weight: 9.4,
    cost: 11250,
    gain_loss: -375,
    gain_loss_percent: -3.33
  }
];

// Mock analysis results
const mockAnalysisResults = {
  summary: {
    total_value: 115532.5,
    total_cost: 104550,
    total_gain_loss: 10982.5,
    total_gain_loss_percent: 10.5,
    securities_count: 6
  },
  allocation: {
    by_asset_class: {
      "Equity": {
        value: 39112.5,
        percent: 33.9
      },
      "ETF": {
        value: 64545,
        percent: 56.0
      },
      "Bond": {
        value: 10875,
        percent: 9.4
      }
    },
    by_sector: {
      "Technology": {
        value: 33812.5,
        percent: 29.3
      },
      "Consumer Discretionary": {
        value: 5300,
        percent: 4.6
      },
      "Diversified": {
        value: 64545,
        percent: 56.0
      },
      "Fixed Income": {
        value: 10875,
        percent: 9.4
      }
    },
    by_region: {
      "North America": {
        value: 94057.5,
        percent: 81.4
      },
      "International": {
        value: 20475,
        percent: 17.8
      }
    }
  },
  performance: {
    returns: {
      "1m": {
        value: 0.025,
        formatted: "2.50%"
      },
      "3m": {
        value: 0.048,
        formatted: "4.80%"
      },
      "6m": {
        value: 0.075,
        formatted: "7.50%"
      },
      "ytd": {
        value: 0.082,
        formatted: "8.20%"
      },
      "1y": {
        value: 0.105,
        formatted: "10.50%"
      }
    },
    annualized_returns: {
      "3y": {
        value: 0.092,
        formatted: "9.20%"
      },
      "5y": {
        value: 0.085,
        formatted: "8.50%"
      }
    }
  },
  risk: {
    volatility: 0.12,
    sharpe_ratio: 0.85,
    sortino_ratio: 1.2,
    max_drawdown: 0.18,
    beta: 0.95,
    alpha: 0.015,
    diversification_score: 78.5
  }
};

// Mock portfolios for the report generator
const mockPortfolios = [
  { id: "portfolio-1", name: "Main Investment Portfolio" },
  { id: "portfolio-2", name: "Retirement Account" },
  { id: "portfolio-3", name: "Children's Education Fund" }
];

export default function FinancialDashboardPage() {
  // These would be actual API calls in a real application
  const handleAnalyzeDocument = async (file: File) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Return mock data
    return {
      document_type: "Portfolio Statement",
      summary: "This portfolio statement shows a well-diversified portfolio with strong performance across equity holdings. Technology sector is overweight compared to benchmarks.",
      portfolio_data: mockPortfolioData,
      financial_figures: [
        { name: "Total Portfolio Value", value: "$115,532.50", context: "As of June 30, 2023" },
        { name: "Total Return YTD", value: "8.2%", context: "January 1 - June 30, 2023" },
        { name: "Dividend Yield", value: "1.8%", context: "Trailing 12 months" }
      ],
      insights: [
        { topic: "Asset Allocation", insight: "The portfolio is well-diversified across asset classes with a slight overweight to equities." },
        { topic: "Sector Exposure", insight: "Technology sector exposure is high at 29.3% of the portfolio, which may increase volatility." },
        { topic: "Performance", insight: "The portfolio has outperformed the benchmark by 1.2% year-to-date." }
      ]
    };
  };
  
  const handleGenerateReport = async (reportType: string, options: any) => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Return mock data based on report type
    if (reportType === "portfolio") {
      return {
        report_type: "portfolio",
        generated_at: new Date().toISOString(),
        title: "Portfolio Analysis Report",
        portfolio_name: options.portfolioId === "portfolio-1" ? "Main Investment Portfolio" : "Other Portfolio",
        summary: mockAnalysisResults.summary,
        allocation: mockAnalysisResults.allocation,
        performance: options.includePerformance ? mockAnalysisResults.performance : null,
        risk: options.includeRisk ? mockAnalysisResults.risk : null,
        holdings: mockPortfolioData,
        recommendations: options.includeRecommendations ? {
          summary: "Consider rebalancing to reduce technology exposure and increase international diversification.",
          actions: [
            { action: "Reduce technology exposure", rationale: "Currently overweight at 29.3% vs. target of 25%" },
            { action: "Increase international allocation", rationale: "Currently underweight at 17.8% vs. target of 25%" },
            { action: "Consider adding inflation protection", rationale: "Portfolio lacks TIPS or other inflation hedges" }
          ]
        } : null
      };
    } else if (reportType === "financial_statement") {
      return {
        report_type: "financial_statement",
        statement_type: options.statementType,
        generated_at: new Date().toISOString(),
        period_start: options.periodStart,
        period_end: options.periodEnd,
        data: {
          // Mock data would be returned here based on statement type
          line_items: [
            { name: "Revenue", value: "$1,250,000", previous_value: options.comparePreviousPeriod ? "$1,150,000" : null },
            { name: "Cost of Goods Sold", value: "$750,000", previous_value: options.comparePreviousPeriod ? "$700,000" : null },
            { name: "Gross Profit", value: "$500,000", previous_value: options.comparePreviousPeriod ? "$450,000" : null },
            { name: "Operating Expenses", value: "$300,000", previous_value: options.comparePreviousPeriod ? "$280,000" : null },
            { name: "Operating Income", value: "$200,000", previous_value: options.comparePreviousPeriod ? "$170,000" : null },
            { name: "Net Income", value: "$150,000", previous_value: options.comparePreviousPeriod ? "$125,000" : null }
          ]
        }
      };
    } else {
      return {
        report_type: reportType,
        generated_at: new Date().toISOString(),
        message: "Report type not fully implemented in this demo"
      };
    }
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Financial Dashboard</h1>
      
      <Tabs defaultValue="dashboard" className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="dashboard">Portfolio Dashboard</TabsTrigger>
          <TabsTrigger value="documents">Document Analysis</TabsTrigger>
          <TabsTrigger value="reports">Report Generator</TabsTrigger>
        </TabsList>
        
        <TabsContent value="dashboard">
          <FinancialDashboard 
            portfolioData={mockPortfolioData}
            analysisResults={mockAnalysisResults}
          />
        </TabsContent>
        
        <TabsContent value="documents">
          <FinancialDocumentAnalysis 
            onAnalyze={handleAnalyzeDocument}
          />
        </TabsContent>
        
        <TabsContent value="reports">
          <FinancialReportGenerator 
            onGenerateReport={handleGenerateReport}
            portfolios={mockPortfolios}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
}
