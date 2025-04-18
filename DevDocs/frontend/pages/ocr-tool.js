import React, { useState, useEffect } from 'react';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import axios from 'axios';

const OCRTool = () => {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [ocrResults, setOcrResults] = useState(null);
  const [error, setError] = useState(null);
  const [apiKeyStatus, setApiKeyStatus] = useState(null);
  const [options, setOptions] = useState({
    enhanceText: true,
    detectOrientation: true,
    detectHandwriting: true,
    includeHOCR: false,
    confidenceThreshold: 70
  });
  const [textToEnhance, setTextToEnhance] = useState('');
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancedText, setEnhancedText] = useState(null);

  // Check API key status on component mount
  useEffect(() => {
    checkApiKey();
  }, []);

  const checkApiKey = async () => {
    try {
      const response = await axios.get('/api/config/api-key');
      setApiKeyStatus(response.data.isConfigured ? 'configured' : 'not-configured');
    } catch (error) {
      console.error('Error checking API key:', error);
      setApiKeyStatus('error');
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setOcrResults(null);
      setError(null);
    }
  };

  const handleOptionChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setOptions(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseInt(value) : value)
    }));
  };

  const handleProcessOCR = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to process');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setOcrResults(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('options', JSON.stringify(options));

      const response = await axios.post('/api/financial/ocr-document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setOcrResults(response.data);
    } catch (error) {
      console.error('Error processing OCR:', error);
      setError(error.response?.data?.detail || error.message || 'Error processing OCR');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextEnhance = async (e) => {
    e.preventDefault();
    
    if (!textToEnhance.trim()) {
      setError('Please enter text to enhance');
      return;
    }

    setIsEnhancing(true);
    setError(null);
    setEnhancedText(null);

    try {
      const response = await axios.post('/api/financial/ocr-document/enhance', {
        text: textToEnhance
      });

      setEnhancedText(response.data);
    } catch (error) {
      console.error('Error enhancing text:', error);
      setError(error.response?.data?.detail || error.message || 'Error enhancing text');
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleCopyText = (text) => {
    navigator.clipboard.writeText(text)
      .then(() => {
        alert('Text copied to clipboard');
      })
      .catch(err => {
        console.error('Error copying text:', err);
        alert('Failed to copy text');
      });
  };

  return (
    <SimpleFinDocUI>
      <div className="ocr-tool">
        <h1 className="page-title">Advanced OCR Tool</h1>

        {apiKeyStatus === 'not-configured' && (
          <div className="warning-message">
            <strong>API Key Not Configured</strong>
            <p>The OpenRouter API key is not configured. AI-enhanced OCR may not be available.</p>
            <p>Please configure the API key in the settings.</p>
          </div>
        )}

        <div className="ocr-container">
          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Document OCR</h2>
            </div>
            <div className="card-content">
              <form onSubmit={handleProcessOCR} className="ocr-form">
                <div className="file-upload">
                  <label className="file-label">Select Document</label>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg,.tif,.tiff"
                    onChange={handleFileChange}
                    className="file-input"
                  />
                  {file && (
                    <div className="file-info">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">({(file.size / 1024).toFixed(2)} KB)</span>
                    </div>
                  )}
                </div>

                <div className="options-container">
                  <h3 className="options-title">OCR Options</h3>
                  <div className="options-grid">
                    <div className="option-item">
                      <input
                        type="checkbox"
                        id="enhanceText"
                        name="enhanceText"
                        checked={options.enhanceText}
                        onChange={handleOptionChange}
                      />
                      <label htmlFor="enhanceText">Enhance Text with AI</label>
                    </div>
                    <div className="option-item">
                      <input
                        type="checkbox"
                        id="detectOrientation"
                        name="detectOrientation"
                        checked={options.detectOrientation}
                        onChange={handleOptionChange}
                      />
                      <label htmlFor="detectOrientation">Detect Orientation</label>
                    </div>
                    <div className="option-item">
                      <input
                        type="checkbox"
                        id="detectHandwriting"
                        name="detectHandwriting"
                        checked={options.detectHandwriting}
                        onChange={handleOptionChange}
                      />
                      <label htmlFor="detectHandwriting">Detect Handwriting</label>
                    </div>
                    <div className="option-item">
                      <input
                        type="checkbox"
                        id="includeHOCR"
                        name="includeHOCR"
                        checked={options.includeHOCR}
                        onChange={handleOptionChange}
                      />
                      <label htmlFor="includeHOCR">Include hOCR</label>
                    </div>
                    <div className="option-item confidence-threshold">
                      <label htmlFor="confidenceThreshold">Confidence Threshold:</label>
                      <input
                        type="number"
                        id="confidenceThreshold"
                        name="confidenceThreshold"
                        min="0"
                        max="100"
                        value={options.confidenceThreshold}
                        onChange={handleOptionChange}
                      />
                    </div>
                  </div>
                </div>

                <div className="action-buttons">
                  <button
                    type="submit"
                    className="btn primary"
                    disabled={!file || isProcessing}
                  >
                    {isProcessing ? 'Processing...' : 'Process OCR'}
                  </button>
                </div>
              </form>

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Text Enhancement</h2>
            </div>
            <div className="card-content">
              <form onSubmit={handleTextEnhance} className="enhance-form">
                <div className="text-input-container">
                  <label className="text-label">Enter OCR Text to Enhance</label>
                  <textarea
                    className="text-input"
                    value={textToEnhance}
                    onChange={(e) => setTextToEnhance(e.target.value)}
                    placeholder="Paste OCR text here to enhance with AI..."
                    rows={6}
                  ></textarea>
                </div>

                <div className="action-buttons">
                  <button
                    type="submit"
                    className="btn primary"
                    disabled={!textToEnhance.trim() || isEnhancing}
                  >
                    {isEnhancing ? 'Enhancing...' : 'Enhance Text'}
                  </button>
                </div>
              </form>

              {enhancedText && (
                <div className="enhanced-result">
                  <h3 className="result-title">Enhanced Text</h3>
                  <div className="text-comparison">
                    <div className="text-column">
                      <h4>Original Text</h4>
                      <div className="text-content">
                        <pre>{enhancedText.original_text}</pre>
                        <button
                          className="btn text-btn"
                          onClick={() => handleCopyText(enhancedText.original_text)}
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                    <div className="text-column">
                      <h4>Enhanced Text</h4>
                      <div className="text-content">
                        <pre>{enhancedText.enhanced_text}</pre>
                        <button
                          className="btn text-btn"
                          onClick={() => handleCopyText(enhancedText.enhanced_text)}
                        >
                          Copy
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {ocrResults && (
          <div className="card results-card">
            <div className="card-header">
              <h2 className="card-title">OCR Results</h2>
            </div>
            <div className="card-content">
              <div className="results-summary">
                <div className="summary-item">
                  <div className="summary-label">Filename:</div>
                  <div className="summary-value">{ocrResults.filename}</div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Processed At:</div>
                  <div className="summary-value">{new Date(ocrResults.processed_at).toLocaleString()}</div>
                </div>
                <div className="summary-item">
                  <div className="summary-label">Confidence:</div>
                  <div className="summary-value">
                    <div className="confidence-bar-container">
                      <div
                        className="confidence-bar"
                        style={{
                          width: `${ocrResults.confidence}%`,
                          backgroundColor: getConfidenceColor(ocrResults.confidence)
                        }}
                      ></div>
                      <div className="confidence-value">{ocrResults.confidence.toFixed(1)}%</div>
                    </div>
                  </div>
                </div>
                {ocrResults.orientation && (
                  <div className="summary-item">
                    <div className="summary-label">Orientation:</div>
                    <div className="summary-value">{ocrResults.orientation}</div>
                  </div>
                )}
                {ocrResults.contains_handwriting !== undefined && (
                  <div className="summary-item">
                    <div className="summary-label">Contains Handwriting:</div>
                    <div className="summary-value">{ocrResults.contains_handwriting ? 'Yes' : 'No'}</div>
                  </div>
                )}
                {ocrResults.language && (
                  <div className="summary-item">
                    <div className="summary-label">Language:</div>
                    <div className="summary-value">{ocrResults.language}</div>
                  </div>
                )}
              </div>

              <div className="results-content">
                <div className="text-result">
                  <h3 className="section-title">Extracted Text</h3>
                  <div className="text-content">
                    <pre>{ocrResults.text}</pre>
                    <button
                      className="btn text-btn"
                      onClick={() => handleCopyText(ocrResults.text)}
                    >
                      Copy Text
                    </button>
                  </div>
                </div>

                {ocrResults.original_text && ocrResults.original_text !== ocrResults.text && (
                  <div className="text-result">
                    <h3 className="section-title">Original OCR Text (Before Enhancement)</h3>
                    <div className="text-content">
                      <pre>{ocrResults.original_text}</pre>
                      <button
                        className="btn text-btn"
                        onClick={() => handleCopyText(ocrResults.original_text)}
                      >
                        Copy Text
                      </button>
                    </div>
                  </div>
                )}

                {ocrResults.blocks && ocrResults.blocks.length > 0 && (
                  <div className="blocks-result">
                    <h3 className="section-title">Text Blocks</h3>
                    <div className="blocks-list">
                      {ocrResults.blocks.map((block, index) => (
                        <div key={index} className={`block-item ${block.type}`}>
                          <div className="block-header">
                            <div className="block-id">{block.id}</div>
                            <div className="block-type">{block.type}</div>
                          </div>
                          <div className="block-text">{block.text}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {ocrResults.words && ocrResults.words.length > 0 && (
                  <div className="words-result">
                    <h3 className="section-title">Words</h3>
                    <div className="words-info">
                      <div className="words-count">Total Words: {ocrResults.words.length}</div>
                      <div className="words-note">Showing words with confidence above {options.confidenceThreshold}%</div>
                    </div>
                    <div className="words-list">
                      {ocrResults.words.slice(0, 100).map((word, index) => (
                        <div
                          key={index}
                          className="word-item"
                          style={{
                            opacity: word.confidence / 100
                          }}
                        >
                          <span className="word-text">{word.text}</span>
                          <span className="word-confidence">({word.confidence.toFixed(1)}%)</span>
                        </div>
                      ))}
                      {ocrResults.words.length > 100 && (
                        <div className="words-more">
                          +{ocrResults.words.length - 100} more words
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .ocr-tool {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .page-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .warning-message {
          padding: 15px;
          background-color: #fff3cd;
          color: #856404;
          border-radius: 4px;
          margin-bottom: 20px;
        }
        
        .warning-message strong {
          display: block;
          margin-bottom: 5px;
        }
        
        .warning-message p {
          margin: 5px 0;
        }
        
        .ocr-container {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
        }
        
        .card {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          overflow: hidden;
        }
        
        .card-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .card-title {
          font-size: 18px;
          font-weight: bold;
          margin: 0;
          color: #2c3e50;
        }
        
        .card-content {
          padding: 20px;
        }
        
        .ocr-form, .enhance-form {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        
        .file-upload {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .file-label {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .file-input {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 4px;
        }
        
        .file-info {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 14px;
          color: #6c757d;
        }
        
        .options-container {
          border: 1px solid #e9ecef;
          border-radius: 4px;
          padding: 15px;
        }
        
        .options-title {
          font-size: 16px;
          font-weight: 500;
          margin: 0 0 15px;
          color: #2c3e50;
        }
        
        .options-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 15px;
        }
        
        .option-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .confidence-threshold {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .confidence-threshold input {
          width: 60px;
          padding: 5px;
          border: 1px solid #ced4da;
          border-radius: 4px;
        }
        
        .action-buttons {
          display: flex;
          justify-content: flex-end;
        }
        
        .btn {
          padding: 10px 15px;
          border: none;
          border-radius: 4px;
          font-size: 16px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .btn.primary {
          background-color: #3498db;
          color: white;
        }
        
        .btn.primary:hover {
          background-color: #2980b9;
        }
        
        .btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        .btn.text-btn {
          background: none;
          color: #3498db;
          padding: 5px 10px;
          font-size: 14px;
        }
        
        .btn.text-btn:hover {
          text-decoration: underline;
        }
        
        .error-message {
          padding: 10px 15px;
          background-color: #f8d7da;
          color: #721c24;
          border-radius: 4px;
          margin-top: 15px;
        }
        
        .text-input-container {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .text-label {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .text-input {
          padding: 10px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-family: monospace;
          resize: vertical;
        }
        
        .enhanced-result {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e9ecef;
        }
        
        .result-title {
          font-size: 16px;
          font-weight: 500;
          margin: 0 0 15px;
          color: #2c3e50;
        }
        
        .text-comparison {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
        }
        
        .text-column {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .text-column h4 {
          font-size: 14px;
          font-weight: 500;
          margin: 0;
          color: #6c757d;
        }
        
        .text-content {
          position: relative;
          background-color: #f8f9fa;
          border-radius: 4px;
          padding: 15px;
          max-height: 300px;
          overflow-y: auto;
        }
        
        .text-content pre {
          margin: 0;
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: monospace;
          font-size: 14px;
          line-height: 1.5;
          color: #212529;
        }
        
        .text-content .btn {
          position: absolute;
          top: 10px;
          right: 10px;
          opacity: 0.7;
        }
        
        .text-content .btn:hover {
          opacity: 1;
        }
        
        .results-card {
          margin-top: 20px;
        }
        
        .results-summary {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
          gap: 15px;
          margin-bottom: 25px;
          padding-bottom: 15px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .summary-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        
        .summary-label {
          font-weight: 500;
          color: #6c757d;
        }
        
        .summary-value {
          font-size: 16px;
          color: #2c3e50;
        }
        
        .confidence-bar-container {
          height: 10px;
          background-color: #e9ecef;
          border-radius: 5px;
          position: relative;
          overflow: hidden;
          margin-top: 5px;
        }
        
        .confidence-bar {
          height: 100%;
          border-radius: 5px;
        }
        
        .confidence-value {
          position: absolute;
          right: 5px;
          top: -18px;
          font-size: 14px;
          font-weight: 500;
          color: #6c757d;
        }
        
        .results-content {
          display: flex;
          flex-direction: column;
          gap: 25px;
        }
        
        .section-title {
          font-size: 16px;
          font-weight: 500;
          margin: 0 0 15px;
          color: #2c3e50;
          padding-bottom: 10px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .blocks-list {
          display: flex;
          flex-direction: column;
          gap: 15px;
        }
        
        .block-item {
          background-color: #f8f9fa;
          border-radius: 4px;
          overflow: hidden;
        }
        
        .block-item.header {
          border-left: 4px solid #3498db;
        }
        
        .block-item.paragraph {
          border-left: 4px solid #2ecc71;
        }
        
        .block-item.table {
          border-left: 4px solid #e74c3c;
        }
        
        .block-item.list {
          border-left: 4px solid #f39c12;
        }
        
        .block-header {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          background-color: rgba(0, 0, 0, 0.05);
        }
        
        .block-id {
          font-weight: 500;
          color: #6c757d;
        }
        
        .block-type {
          font-size: 14px;
          color: #6c757d;
          text-transform: capitalize;
        }
        
        .block-text {
          padding: 12px;
          white-space: pre-wrap;
          word-wrap: break-word;
          font-family: monospace;
          font-size: 14px;
          line-height: 1.5;
          color: #212529;
        }
        
        .words-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 15px;
        }
        
        .words-count {
          font-weight: 500;
          color: #2c3e50;
        }
        
        .words-note {
          font-size: 14px;
          color: #6c757d;
        }
        
        .words-list {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          background-color: #f8f9fa;
          border-radius: 4px;
          padding: 15px;
        }
        
        .word-item {
          background-color: #e9ecef;
          border-radius: 4px;
          padding: 5px 10px;
          font-size: 14px;
          color: #212529;
        }
        
        .word-confidence {
          font-size: 12px;
          color: #6c757d;
          margin-left: 5px;
        }
        
        .words-more {
          width: 100%;
          text-align: center;
          padding: 10px;
          font-size: 14px;
          color: #6c757d;
        }
        
        @media (max-width: 768px) {
          .ocr-container {
            grid-template-columns: 1fr;
          }
          
          .text-comparison {
            grid-template-columns: 1fr;
          }
          
          .results-summary {
            grid-template-columns: 1fr;
          }
          
          .options-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </SimpleFinDocUI>
  );
};

// Helper function to get color based on confidence
function getConfidenceColor(confidence) {
  if (confidence >= 90) {
    return '#2ecc71'; // Green
  } else if (confidence >= 70) {
    return '#f39c12'; // Orange
  } else {
    return '#e74c3c'; // Red
  }
}

export default OCRTool;
