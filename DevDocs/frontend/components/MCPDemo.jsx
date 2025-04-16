import React, { useState } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import mcpClient from '../lib/mcpClient';

const MCPDemo = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Get context from MCP
      const contextResponse = await mcpClient.getContext(query, { webSearch: true });

      if (contextResponse && contextResponse.results) {
        setResults(contextResponse.results);
      } else {
        setResults([]);
      }
    } catch (err) {
      console.error('Error using MCP:', err);
      setError('Failed to get results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">MCP Demo</h2>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your query..."
            className="flex-1 p-2 border border-gray-300 rounded"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 mb-4 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      {results.length > 0 ? (
        <div>
          <h3 className="text-xl font-semibold mb-2">Results</h3>
          <div className="space-y-4">
            {results.map((result, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded">
                <h4 className="font-bold">{result.title}</h4>
                {result.link && (
                  <a
                    href={result.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-500 hover:underline"
                  >
                    {result.link}
                  </a>
                )}
                <p className="mt-2 text-gray-700">
                  {result.snippet || result.content || 'No content available'}
                </p>
                {result.source && (
                  <p className="mt-1 text-sm text-gray-500">
                    Source: {result.source}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : !loading && (
        <p className="text-gray-500">No results to display. Try searching for something!</p>
      )}
    </div>
    </AccessibilityWrapper>
  );
};

export default MCPDemo;
