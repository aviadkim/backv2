import React, { useState } from 'react';

const FileUpload = ({ onUploadComplete }) => {
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload');
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to upload file');
      }

      const data = await response.json();
      onUploadComplete(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="file-upload">
      <h2>Upload Financial Document</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="file">Select PDF file:</label>
          <input
            type="file"
            id="file"
            accept=".pdf,.txt"
            onChange={handleFileChange}
            disabled={isLoading}
          />
        </div>
        
        {error && <div className="error">{error}</div>}
        
        <button 
          type="submit" 
          disabled={!file || isLoading}
          className="upload-button"
        >
          {isLoading ? 'Processing...' : 'Upload and Analyze'}
        </button>
      </form>
      
      {isLoading && (
        <div className="loading">
          <p>Processing document... This may take a minute.</p>
          <div className="progress-bar"></div>
        </div>
      )}
      
      <style jsx>{`
        .file-upload {
          max-width: 500px;
          margin: 0 auto;
          padding: 20px;
          background: #f9f9f9;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .form-group {
          margin-bottom: 20px;
        }
        
        label {
          display: block;
          margin-bottom: 8px;
          font-weight: bold;
        }
        
        input[type="file"] {
          width: 100%;
          padding: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
        
        .upload-button {
          background: #4285f4;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 16px;
        }
        
        .upload-button:disabled {
          background: #ccc;
          cursor: not-allowed;
        }
        
        .error {
          color: #d32f2f;
          margin-bottom: 15px;
        }
        
        .loading {
          margin-top: 20px;
          text-align: center;
        }
        
        .progress-bar {
          height: 4px;
          background: #e0e0e0;
          border-radius: 2px;
          margin-top: 10px;
          position: relative;
          overflow: hidden;
        }
        
        .progress-bar:after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          width: 30%;
          background: #4285f4;
          animation: progress 1.5s infinite ease-in-out;
        }
        
        @keyframes progress {
          0% { left: -30%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
};

export default FileUpload;
