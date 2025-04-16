import React, { useState } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiUpload, FiFile, FiCheckCircle, FiAlertCircle, FiLoader } from 'react-icons/fi';
import axios from 'axios';

const DocumentUploader = ({ onDocumentProcessed }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
    setError(null);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    setSelectedFile(file);
    setUploadStatus(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setUploadProgress(0);
    setUploadStatus(null);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('/api/documents/process-and-analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });

      setUploadStatus('success');

      if (onDocumentProcessed) {
        onDocumentProcessed(response.data);
      }
    } catch (err) {
      console.error('Error uploading document:', err);
      setError(err.response?.data?.detail || 'Error uploading document');
      setUploadStatus('error');
    } finally {
      setUploading(false);
    }
  };

  const isValidFileType = (file) => {
    const validTypes = ['application/pdf', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'];
    return file && validTypes.includes(file.type);
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Upload Financial Document</h3>

      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center ${
          uploading ? 'border-gray-300 bg-gray-50' : 'border-gray-300 hover:border-blue-500'
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {!uploading && !uploadStatus && (
          <>
            <FiUpload className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-sm font-medium text-gray-900">
              Drag and drop your file here, or{' '}
              <label className="text-blue-600 hover:text-blue-500 cursor-pointer">
                browse
                <input
                  type="file"
                  className="hidden"
                  accept=".pdf,.xls,.xlsx,.csv"
                  onChange={handleFileChange}
                />
              </label>
            </p>
            <p className="mt-1 text-xs text-gray-500">
              PDF, Excel, or CSV files up to 50MB
            </p>
          </>
        )}

        {selectedFile && !uploading && !uploadStatus && (
          <div className="mt-4">
            <div className="flex items-center justify-center">
              <FiFile className="h-5 w-5 text-gray-400 mr-2" />
              <span className="text-sm font-medium text-gray-900">{selectedFile.name}</span>
            </div>

            {!isValidFileType(selectedFile) && (
              <p className="mt-2 text-xs text-red-500">
                Invalid file type. Please upload a PDF, Excel, or CSV file.
              </p>
            )}

            <button
              type="button"
              onClick={handleUpload}
              disabled={!isValidFileType(selectedFile)}
              className={`mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                isValidFileType(selectedFile) ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-400'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
            >
              Process Document
            </button>
          </div>
        )}

        {uploading && (
          <div className="mt-4">
            <div className="flex items-center justify-center">
              <FiLoader className="h-8 w-8 text-blue-500 animate-spin mr-2" />
              <span className="text-sm font-medium text-gray-900">Processing document...</span>
            </div>

            <div className="mt-4 w-full bg-gray-200 rounded-full h-2.5">
              <div
                className="bg-blue-600 h-2.5 rounded-full"
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <p className="mt-2 text-xs text-gray-500">
              {uploadProgress < 100 ? 'Uploading...' : 'Analyzing document...'}
            </p>
          </div>
        )}

        {uploadStatus === 'success' && (
          <div className="mt-4">
            <div className="flex items-center justify-center">
              <FiCheckCircle className="h-8 w-8 text-green-500 mr-2" />
              <span className="text-sm font-medium text-gray-900">Document processed successfully!</span>
            </div>

            <button
              type="button"
              onClick={() => {
                setSelectedFile(null);
                setUploadStatus(null);
              }}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Upload Another Document
            </button>
          </div>
        )}

        {uploadStatus === 'error' && (
          <div className="mt-4">
            <div className="flex items-center justify-center">
              <FiAlertCircle className="h-8 w-8 text-red-500 mr-2" />
              <span className="text-sm font-medium text-gray-900">Error processing document</span>
            </div>

            <p className="mt-2 text-xs text-red-500">
              {error || 'An error occurred while processing the document. Please try again.'}
            </p>

            <button
              type="button"
              onClick={() => {
                setUploadStatus(null);
                setError(null);
              }}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Try Again
            </button>
          </div>
        )}
      </div>

      <div className="mt-4">
        <h4 className="text-sm font-medium text-gray-900 mb-2">Supported Document Types:</h4>
        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
          <li>PDF Financial Statements</li>
          <li>Excel Spreadsheets with Financial Data</li>
          <li>CSV Files with Financial Data</li>
          <li>Bank Statements</li>
          <li>Investment Account Statements</li>
          <li>Credit Card Statements</li>
        </ul>
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default DocumentUploader;
