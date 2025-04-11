import React, { useState } from 'react';

export default function MessosDemo() {
  const [showAnalysis, setShowAnalysis] = useState(false);
  
  const handleAnalyze = () => {
    setShowAnalysis(true);
  };
  
  return (
    <div style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Messos Financial Document Analysis</h1>
      
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '10px' }}>About This Demo</h2>
        <p style={{ marginBottom: '15px' }}>
          This demo showcases our Document Understanding Engine's capabilities for analyzing the Messos financial document.
        </p>
        
        <div style={{ backgroundColor: '#FFFBEA', padding: '15px', borderRadius: '6px' }}>
          <h3 style={{ marginBottom: '5px', fontSize: '14px' }}>Demo Mode Notice:</h3>
          <p style={{ fontSize: '14px' }}>
            This is a demonstration with mock analysis results. In a real application, the analysis would be performed on the actual document.
          </p>
        </div>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '15px' }}>Messos Financial Document</h3>
          <div style={{ marginBottom: '15px' }}>
            <div style={{ border: '1px solid #ccc', borderRadius: '4px', height: '400px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <p>PDF Viewer would appear here</p>
            </div>
          </div>
          
          <button
            onClick={handleAnalyze}
            style={{
              backgroundColor: '#3B82F6',
              color: 'white',
              padding: '8px 16px',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Analyze Document
          </button>
        </div>
        
        {showAnalysis && (
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px' }}>
            <h3 style={{ marginBottom: '15px' }}>Analysis Results</h3>
            
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px' }}>Document Information</h4>
              <div style={{ backgroundColor: '#F9FAFB', padding: '15px', borderRadius: '6px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6B7280' }}>File Name</p>
                    <p style={{ fontSize: '14px', fontWeight: '500' }}>Messos 28.02.2025.pdf</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6B7280' }}>Document Type</p>
                    <p style={{ fontSize: '14px', fontWeight: '500' }}>Financial Statement</p>
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
                    <p style={{ fontSize: '14px', fontWeight: '500' }}>Messos Group</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '14px', color: '#6B7280' }}>Industry</p>
                    <p style={{ fontSize: '14px', fontWeight: '500' }}>Technology</p>
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
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Revenue</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>€1,234,567</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Net Income</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>€234,567</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Total Assets</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>€3,456,789</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Total Liabilities</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>€1,456,789</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
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
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Gross Margin</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>42.5%</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Net Margin</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>19.0%</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Return on Equity</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>15.8%</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>Debt to Equity</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>0.73</td>
                      <td style={{ padding: '10px', borderBottom: '1px solid #E5E7EB' }}>2025</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
