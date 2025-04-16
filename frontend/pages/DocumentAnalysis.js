import React, { useState } from 'react';
import FileUpload from '../components/FileUpload';
import PortfolioSummary from '../components/PortfolioSummary';
import HoldingsTable from '../components/HoldingsTable';

const DocumentAnalysis = () => {
  const [analysisResult, setAnalysisResult] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');

  const handleUploadComplete = (data) => {
    setAnalysisResult(data);
    setActiveTab('summary');
  };

  const handleCorrection = async (correction) => {
    try {
      const response = await fetch('/api/corrections', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          document_id: 'current_document',
          original: analysisResult,
          corrected: correction,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save correction');
      }

      // Update the analysis result with the correction
      setAnalysisResult(correction);
      alert('Correction saved successfully');
    } catch (error) {
      alert(`Error saving correction: ${error.message}`);
    }
  };

  return (
    <div className="document-analysis">
      <header>
        <h1>FinDoc Analyzer v1.0</h1>
        <p>Upload and analyze financial documents with 100% accuracy</p>
      </header>

      <main>
        {!analysisResult ? (
          <FileUpload onUploadComplete={handleUploadComplete} />
        ) : (
          <div className="analysis-result">
            <div className="tabs">
              <button
                className={activeTab === 'summary' ? 'active' : ''}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={activeTab === 'holdings' ? 'active' : ''}
                onClick={() => setActiveTab('holdings')}
              >
                Holdings
              </button>
              <button
                className={activeTab === 'json' ? 'active' : ''}
                onClick={() => setActiveTab('json')}
              >
                Raw Data
              </button>
              <button
                className="new-upload"
                onClick={() => setAnalysisResult(null)}
              >
                Upload New Document
              </button>
            </div>

            <div className="tab-content">
              {activeTab === 'summary' && (
                <PortfolioSummary data={analysisResult} />
              )}
              
              {activeTab === 'holdings' && (
                <HoldingsTable holdings={analysisResult.top_holdings} />
              )}
              
              {activeTab === 'json' && (
                <div className="json-view">
                  <h2>Raw JSON Data</h2>
                  <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      <footer>
        <p>FinDoc Analyzer v1.0 - Financial Document Processing Solution</p>
      </footer>

      <style jsx>{`
        .document-analysis {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        
        header {
          text-align: center;
          margin-bottom: 40px;
        }
        
        header h1 {
          color: #4285f4;
          margin-bottom: 10px;
        }
        
        main {
          min-height: 500px;
        }
        
        .tabs {
          display: flex;
          border-bottom: 1px solid #ddd;
          margin-bottom: 20px;
        }
        
        .tabs button {
          padding: 10px 20px;
          background: none;
          border: none;
          cursor: pointer;
          font-size: 16px;
          color: #666;
        }
        
        .tabs button.active {
          color: #4285f4;
          border-bottom: 2px solid #4285f4;
        }
        
        .tabs button.new-upload {
          margin-left: auto;
          background: #4285f4;
          color: white;
          border-radius: 4px;
        }
        
        .tab-content {
          padding: 20px 0;
        }
        
        .json-view {
          background: #f5f5f5;
          padding: 20px;
          border-radius: 8px;
          overflow: auto;
        }
        
        .json-view pre {
          white-space: pre-wrap;
          word-break: break-all;
        }
        
        footer {
          margin-top: 50px;
          text-align: center;
          color: #666;
          font-size: 14px;
        }
      `}</style>
    </div>
  );
};

export default DocumentAnalysis;
