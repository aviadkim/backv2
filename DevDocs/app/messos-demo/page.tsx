'use client';

import { useState } from 'react';

export default function MessosDemo() {
  const [isAnalyzed, setIsAnalyzed] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const analyzeDocument = () => {
    // Mock analysis results
    setAnalysisResults({
      documentInfo: {
        fileName: 'Messos 28.02.2025.pdf',
        fileSize: '2.4 MB',
        uploadDate: '2025-04-07',
        documentType: 'Annual Financial Report',
      },
      companyInfo: {
        name: 'Messos Group',
        fiscalYear: '2024',
        industry: 'Technology',
        reportType: 'Annual Report',
      },
      financialMetrics: [
        { metric: 'Revenue', value: '€1,234,567', period: 'FY 2024' },
        { metric: 'Net Income', value: '€234,567', period: 'FY 2024' },
        { metric: 'Total Assets', value: '€2,345,678', period: 'FY 2024' },
        { metric: 'Total Liabilities', value: '€1,234,567', period: 'FY 2024' },
      ],
      financialRatios: [
        { ratio: 'Gross Margin', value: '42.5%', period: 'FY 2024' },
        { ratio: 'Net Profit Margin', value: '19.0%', period: 'FY 2024' },
        { ratio: 'Return on Assets', value: '10.0%', period: 'FY 2024' },
        { ratio: 'Debt to Equity', value: '1.2', period: 'FY 2024' },
      ],
    });
    setIsAnalyzed(true);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Messos Financial Document Analysis</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="border p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Document Preview</h2>
          <div className="h-[300px] flex items-center justify-center bg-gray-100 rounded">
            <div className="text-center">
              <p className="text-gray-500 mb-4">PDF Viewer would appear here</p>
              <p className="text-sm text-gray-400">In a real implementation, this would display the actual PDF document</p>
            </div>
          </div>
        </div>

        <div className="border p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">About This Demo</h2>
          <p className="mb-4">
            This demo showcases our Document Understanding Engine analyzing a financial document from Messos Group.
          </p>
          <p className="mb-6">
            The system extracts key financial metrics, ratios, and company information automatically, saving hours of manual analysis.
          </p>
          <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-6">
            <h5 className="font-medium mb-1">Demo Mode Notice:</h5>
            <div className="text-sm">
              This is a demonstration with mock analysis results. In a production environment, the system would process the actual document.
            </div>
          </div>
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full"
            onClick={analyzeDocument}
          >
            Analyze Document
          </button>
        </div>
      </div>

      {isAnalyzed && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Document Information</h3>
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="font-medium">File Name:</dt>
                  <dd>{analysisResults.documentInfo.fileName}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">File Size:</dt>
                  <dd>{analysisResults.documentInfo.fileSize}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Upload Date:</dt>
                  <dd>{analysisResults.documentInfo.uploadDate}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Document Type:</dt>
                  <dd>{analysisResults.documentInfo.documentType}</dd>
                </div>
              </dl>
            </div>

            <div className="border p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Company Information</h3>
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="font-medium">Company Name:</dt>
                  <dd>{analysisResults.companyInfo.name}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Fiscal Year:</dt>
                  <dd>{analysisResults.companyInfo.fiscalYear}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Industry:</dt>
                  <dd>{analysisResults.companyInfo.industry}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Report Type:</dt>
                  <dd>{analysisResults.companyInfo.reportType}</dd>
                </div>
              </dl>
            </div>

            <div className="border p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Financial Metrics</h3>
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="text-left">Metric</th>
                    <th className="text-right">Value</th>
                    <th className="text-right">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.financialMetrics.map((metric: any, index: number) => (
                    <tr key={index}>
                      <td className="py-2">{metric.metric}</td>
                      <td className="text-right">{metric.value}</td>
                      <td className="text-right">{metric.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="border p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Financial Ratios</h3>
              <table className="w-full">
                <thead>
                  <tr>
                    <th className="text-left">Ratio</th>
                    <th className="text-right">Value</th>
                    <th className="text-right">Period</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.financialRatios.map((ratio: any, index: number) => (
                    <tr key={index}>
                      <td className="py-2">{ratio.ratio}</td>
                      <td className="text-right">{ratio.value}</td>
                      <td className="text-right">{ratio.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {!isAnalyzed && (
        <div className="border p-6 rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-4">Sample Analysis Results</h2>
          <p className="mb-6">
            Click the "Analyze Document" button above to see the analysis results for the Messos financial document.
          </p>
        </div>
      )}
    </div>
  );
}
