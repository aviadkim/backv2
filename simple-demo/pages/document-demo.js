import React, { useState } from 'react';

export default function DocumentDemo() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
  };
  
  const handleDragOver = (event) => {
    event.preventDefault();
  };
  
  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
  };
  
  const handleUpload = () => {
    if (!selectedFile) return;
    
    // Simulate processing
    setUploadStatus('processing');
    
    // Simulate a delay for processing
    setTimeout(() => {
      setUploadStatus('success');
      
      // Set mock analysis results
      setAnalysisResults({
        document_info: {
          file_name: selectedFile.name,
          title: "Financial Report"
        },
        company_info: {
          name: "Demo Company Inc.",
          ticker: "DEMO",
          industry: "Technology",
          sector: "Software"
        },
        financial_data: {
          financial_metrics: [
            {
              name: "revenue",
              display_name: "Revenue",
              value: 1000000,
              period: "2023"
            },
            {
              name: "net_income",
              display_name: "Net Income",
              value: 200000,
              period: "2023"
            }
          ]
        },
        financial_ratios: [
          {
            name: "gross_margin",
            display_name: "Gross Margin",
            value: 0.4,
            period: "2023"
          },
          {
            name: "net_margin",
            display_name: "Net Margin",
            value: 0.2,
            period: "2023"
          }
        ]
      });
    }, 2000);
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Document Understanding Demo</h1>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '10px' }}>About This Demo</h2>
        <p style={{ marginBottom: '15px' }}>
          This demo showcases our Document Understanding Engine's capabilities for analyzing financial documents.
          Upload a financial document (PDF, Excel, or CSV) to see how the system extracts and analyzes financial data.
        </p>
        
        <div style={{ backgroundColor: '#FFFBEA', padding: '15px', borderRadius: '6px' }}>
          <h3 style={{ marginBottom: '5px', fontSize: '14px' }}>Demo Mode Notice:</h3>
          <p style={{ fontSize: '14px' }}>
            This is a demonstration with mock data. In a real application, the analysis would be performed on your actual uploaded document.
          </p>
        </div>
      </div>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
        <h3 style={{ marginBottom: '15px' }}>Upload Financial Document</h3>
        
        <div 
          style={{ 
            border: '2px dashed #ccc', 
            borderRadius: '8px', 
            padding: '30px', 
            textAlign: 'center',
            cursor: 'pointer'
          }}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {!uploadStatus && (
            <>
              <div style={{ fontSize: '48px', marginBottom: '10px' }}>📄</div>
              <p style={{ marginBottom: '10px' }}>
                Drag and drop your file here, or{' '}
                <label style={{ color: 'blue', cursor: 'pointer' }}>
                  browse
                  <input
                    type="file"
                    style={{ display: 'none' }}
                    accept=".pdf,.xls,.xlsx,.csv"
                    onChange={handleFileChange}
                  />
                </label>
              </p>
              <p style={{ fontSize: '12px', color: '#666' }}>
                PDF, Excel, or CSV files up to 50MB
              </p>
            </>
          )}
          
          {selectedFile && !uploadStatus && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', marginRight: '10px' }}>📄</div>
                <span>{selectedFile.name}</span>
              </div>
              
              <button
                onClick={handleUpload}
                style={{
                  backgroundColor: '#3B82F6',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Process Document
              </button>
            </div>
          )}
          
          {uploadStatus === 'processing' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', marginRight: '10px' }}>⏳</div>
                <span>Processing document...</span>
              </div>
              
              <div style={{ 
                width: '100%', 
                height: '8px', 
                backgroundColor: '#E5E7EB',
                borderRadius: '4px',
                overflow: 'hidden',
                marginBottom: '10px'
              }}>
                <div style={{ 
                  width: '75%', 
                  height: '100%', 
                  backgroundColor: '#3B82F6',
                  animation: 'pulse 1.5s infinite'
                }}></div>
              </div>
              <p style={{ fontSize: '12px', color: '#666' }}>
                Analyzing document...
              </p>
            </div>
          )}
          
          {uploadStatus === 'success' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '24px', marginRight: '10px' }}>✅</div>
                <span>Document processed successfully!</span>
              </div>
              
              <button
                onClick={() => {
                  setSelectedFile(null);
                  setUploadStatus(null);
                }}
                style={{
                  backgroundColor: '#3B82F6',
                  color: 'white',
                  padding: '8px 16px',
                  borderRadius: '4px',
                  border: 'none',
                  cursor: 'pointer'
                }}
              >
                Upload Another Document
              </button>
            </div>
          )}
        </div>
      </div>
      
      {analysisResults && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginTop: '20px' }}>
          <h3 style={{ marginBottom: '15px' }}>Analysis Results</h3>
          
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ marginBottom: '10px' }}>Document Information</h4>
            <div style={{ backgroundColor: '#F9FAFB', padding: '15px', borderRadius: '6px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>File Name</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.document_info.file_name}</p>
                </div>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Title</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.document_info.title}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ marginBottom: '10px' }}>Company Information</h4>
            <div style={{ backgroundColor: '#F9FAFB', padding: '15px', borderRadius: '6px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Company Name</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.company_info.name}</p>
                </div>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Ticker Symbol</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.company_info.ticker}</p>
                </div>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Industry</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.company_info.industry}</p>
                </div>
                <div>
                  <p style={{ fontSize: '14px', color: '#6B7280' }}>Sector</p>
                  <p style={{ fontSize: '14px', fontWeight: '500' }}>{analysisResults.company_info.sector}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ marginBottom: '10px' }}>Financial Metrics</h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Metric</th>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Value</th>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Period</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.financial_data.financial_metrics.map((metric, index) => (
                    <tr key={index}>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>{metric.display_name}</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>${metric.value.toLocaleString()}</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>{metric.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          
          <div>
            <h4 style={{ marginBottom: '10px' }}>Financial Ratios</h4>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Ratio</th>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Value</th>
                    <th style={{ padding: '10px', textAlign: 'left', backgroundColor: '#F9FAFB', borderBottom: '1px solid #E5E7EB' }}>Period</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.financial_ratios.map((ratio, index) => (
                    <tr key={index}>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>{ratio.display_name}</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>{(ratio.value * 100).toFixed(1)}%</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>{ratio.period}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
