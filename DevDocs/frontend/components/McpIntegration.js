import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import axios from 'axios';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:24125';

const McpIntegration = () => {
  const [buckets, setBuckets] = useState([]);
  const [selectedBucket, setSelectedBucket] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [url, setUrl] = useState('');
  const [fetchedContent, setFetchedContent] = useState('');

  // Fetch buckets on component mount
  useEffect(() => {
    fetchBuckets();
  }, []);

  // Fetch files when a bucket is selected
  useEffect(() => {
    if (selectedBucket) {
      fetchFiles(selectedBucket);
    }
  }, [selectedBucket]);

  // Fetch buckets from the MCP server
  const fetchBuckets = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mcp/buckets`);
      if (response.data.success) {
        setBuckets(response.data.result);
        if (response.data.result.length > 0) {
          setSelectedBucket(response.data.result[0]);
        }
      } else {
        setError(response.data.error || 'Failed to fetch buckets');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching buckets');
    } finally {
      setLoading(false);
    }
  };

  // Fetch files from a bucket
  const fetchFiles = async (bucketName) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mcp/files/${bucketName}`);
      if (response.data.success) {
        setFiles(response.data.result);
      } else {
        setError(response.data.error || 'Failed to fetch files');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching files');
    } finally {
      setLoading(false);
    }
  };

  // Upload a file to a bucket
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    try {
      // Read the file as base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Content = e.target.result.split(',')[1]; // Remove the data URL prefix

        // Upload the file
        const response = await axios.post(`${BACKEND_URL}/api/mcp/upload`, {
          bucketName: selectedBucket,
          fileName: file.name,
          fileContent: base64Content
        });

        if (response.data.success) {
          // Refresh the file list
          fetchFiles(selectedBucket);
        } else {
          setError(response.data.error || 'Failed to upload file');
        }
        setLoading(false);
      };

      reader.readAsDataURL(file);
    } catch (err) {
      setError(err.message || 'An error occurred while uploading the file');
      setLoading(false);
    }
  };

  // Process a document using Document AI
  const processDocument = async (fileName) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post(`${BACKEND_URL}/api/mcp/process-document`, {
        bucketName: selectedBucket,
        fileName
      });

      if (response.data.success) {
        alert(`Document processed successfully: ${fileName}`);
      } else {
        setError(response.data.error || 'Failed to process document');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while processing the document');
    } finally {
      setLoading(false);
    }
  };

  // Search the web
  const handleSearch = async () => {
    if (!searchQuery) return;

    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mcp/web-search?query=${encodeURIComponent(searchQuery)}`);
      if (response.data.success) {
        setSearchResults(response.data.result);
      } else {
        setError(response.data.error || 'Failed to search the web');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while searching the web');
    } finally {
      setLoading(false);
    }
  };

  // Fetch content from a URL
  const handleFetchContent = async () => {
    if (!url) return;

    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${BACKEND_URL}/api/mcp/web-fetch?url=${encodeURIComponent(url)}`);
      if (response.data.success) {
        setFetchedContent(response.data.result.content);
      } else {
        setError(response.data.error || 'Failed to fetch content');
      }
    } catch (err) {
      setError(err.message || 'An error occurred while fetching content');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="mcp-integration">
      <h1>Google Cloud Integration</h1>

      {error && <div className="error">{error}</div>}

      <section className="section">
        <h2>Storage Buckets</h2>
        {loading && <div className="loading">Loading...</div>}
        <div className="buckets">
          <select
            value={selectedBucket}
            onChange={(e) => setSelectedBucket(e.target.value)}
            disabled={loading}
          >
            <option value="">Select a bucket</option>
            {buckets.map((bucket) => (
              <option key={bucket} value={bucket}>
                {bucket}
              </option>
            ))}
          </select>
          <button onClick={fetchBuckets} disabled={loading}>
            Refresh Buckets
          </button>
        </div>
      </section>

      <section className="section">
        <h2>Files in {selectedBucket}</h2>
        {loading && <div className="loading">Loading...</div>}
        <div className="files">
          <ul>
            {files.map((file) => (
              <li key={file}>
                {file}
                <button onClick={() => processDocument(file)} disabled={loading}>
                  Process
                </button>
              </li>
            ))}
          </ul>
          <div className="upload">
            <input type="file" onChange={handleFileUpload} disabled={loading} />
          </div>
        </div>
      </section>

      <section className="section">
        <h2>Web Search</h2>
        <div className="search">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Enter search query"
            disabled={loading}
          />
          <button onClick={handleSearch} disabled={loading}>
            Search
          </button>
        </div>
        {loading && <div className="loading">Loading...</div>}
        <div className="search-results">
          <ul>
            {searchResults.map((result, index) => (
              <li key={index}>
                <a href={result.link} target="_blank" rel="noopener noreferrer">
                  {result.title}
                </a>
                <p>{result.snippet}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section">
        <h2>Web Fetch</h2>
        <div className="fetch">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter URL"
            disabled={loading}
          />
          <button onClick={handleFetchContent} disabled={loading}>
            Fetch
          </button>
        </div>
        {loading && <div className="loading">Loading...</div>}
        <div className="fetched-content">
          {fetchedContent && (
            <div>
              <h3>Fetched Content</h3>
              <div className="content" role="main">{fetchedContent}</div>
            </div>
          )}
        </div>
      </section>

      <style jsx>{`
        .mcp-integration {
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        .section {
          margin-bottom: 30px;
          padding: 20px;
          border: 1px solid #ddd;
          border-radius: 5px;
        }
        .error {
          color: red;
          margin-bottom: 20px;
          padding: 10px;
          background-color: #ffeeee;
          border: 1px solid #ffcccc;
          border-radius: 5px;
        }
        .loading {
          margin: 10px 0;
          color: #666;
        }
        .buckets, .files, .search, .fetch {
          margin-top: 10px;
        }
        select, input {
          padding: 8px;
          margin-right: 10px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
        button {
          padding: 8px 16px;
          background-color: #4285f4;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
        }
        ul {
          list-style-type: none;
          padding: 0;
        }
        li {
          padding: 10px;
          border-bottom: 1px solid #eee;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .content {
          margin-top: 10px;
          padding: 10px;
          background-color: #f9f9f9;
          border: 1px solid #ddd;
          border-radius: 4px;
          max-height: 300px;
          overflow-y: auto;
          white-space: pre-wrap;
        }
      `}</style>
    </div>
    </AccessibilityWrapper>
  );
};

export default McpIntegration;
