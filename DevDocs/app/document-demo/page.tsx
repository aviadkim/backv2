'use client';

import { useState } from 'react';

export default function DocumentDemo() {
  const [file, setFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessed, setIsProcessed] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const processDocument = () => {
    setIsProcessing(true);

    // Simulate processing with a timeout
    setTimeout(() => {
      setIsProcessing(false);
      setIsProcessed(true);
      // Mock analysis results
      setAnalysisResults({
        documentInfo: {
          fileName: file?.name || 'document.pdf',
          fileSize: `${(file?.size || 0) / 1024} KB`,
          uploadDate: new Date().toLocaleString(),
          documentType: 'Financial Statement',
        },
        financialMetrics: [
          { metric: 'Revenue', value: '$1,234,567', period: 'FY 2024' },
          { metric: 'Net Income', value: '$234,567', period: 'FY 2024' },
        ],
      });
    }, 2000);
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8 text-center">Document Understanding Demo</h1>

      {!isProcessed ? (
        <div className="border p-6 rounded-lg shadow-sm mb-8">
          <h2 className="text-xl font-semibold mb-4">Upload Financial Document</h2>

          <div className="border-dashed border-2 border-gray-300 rounded-lg p-8 text-center mb-4">
            {!file ? (
              <>
                <p className="mb-4">Drag and drop your file here, or browse</p>
                <button
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  onClick={() => document.getElementById('fileInput')?.click()}
                >
                  Select File
                </button>
                <input
                  id="fileInput"
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.xlsx,.csv"
                />
              </>
            ) : (
              <div>
                <p className="mb-2">Selected file:</p>
                <p className="font-semibold mb-4">{file.name}</p>
                {isProcessing ? (
                  <div>
                    <p className="mb-2">Processing document...</p>
                    <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                      <div className="bg-blue-600 h-2.5 rounded-full w-1/2"></div>
                    </div>
                  </div>
                ) : (
                  <button
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                    onClick={processDocument}
                  >
                    Process Document
                  </button>
                )}
              </div>
            )}
          </div>

          <div className="mt-6">
            <h3 className="font-semibold mb-2">Supported Document Types:</h3>
            <ul className="list-disc pl-5">
              <li>PDF Financial Statements</li>
              <li>Excel Spreadsheets with Financial Data</li>
              <li>CSV Files with Financial Data</li>
            </ul>
          </div>
        </div>
      ) : (
        <div>
          <div className="border p-6 rounded-lg shadow-sm mb-8">
            <h2 className="text-xl font-semibold mb-4">Document processed successfully!</h2>
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              onClick={() => {
                setFile(null);
                setIsProcessed(false);
                setAnalysisResults(null);
              }}
            >
              Upload Another Document
            </button>
          </div>

          <h2 className="text-2xl font-bold mb-4">Analysis Results</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border p-6 rounded-lg shadow-sm">
              <h3 className="text-xl font-semibold mb-4">Document Information</h3>
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="font-medium">File Name:</dt>
                  <dd>{analysisResults?.documentInfo.fileName}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">File Size:</dt>
                  <dd>{analysisResults?.documentInfo.fileSize}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Upload Date:</dt>
                  <dd>{analysisResults?.documentInfo.uploadDate}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="font-medium">Document Type:</dt>
                  <dd>{analysisResults?.documentInfo.documentType}</dd>
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
                  {analysisResults?.financialMetrics.map((metric: any, index: number) => (
                    <tr key={index}>
                      <td className="py-2">{metric.metric}</td>
                      <td className="text-right">{metric.value}</td>
                      <td className="text-right">{metric.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <div className="border p-6 rounded-lg shadow-sm mt-8">
        <h2 className="text-xl font-semibold mb-4">How It Works</h2>
        <p className="mb-4">
          Our document understanding system uses advanced AI to automatically extract and analyze information from financial documents.
          Simply upload your document, and our system will process it and provide you with a detailed analysis.
        </p>
        <ol className="list-decimal pl-5">
          <li className="mb-2">Upload your financial document</li>
          <li className="mb-2">Our AI analyzes the content</li>
          <li className="mb-2">View extracted financial metrics and ratios</li>
          <li className="mb-2">Download or share the analysis</li>
        </ol>
      </div>
    </div>
  );
}
