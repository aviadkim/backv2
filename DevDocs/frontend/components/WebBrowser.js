import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiSearch, FiBookmark, FiClock, FiExternalLink, FiDownload, FiRefreshCw, FiArrowLeft, FiArrowRight } from 'react-icons/fi';
import { useBrowsing } from '../providers/BrowsingProvider';

const WebBrowser = () => {
  const [url, setUrl] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('browser');
  const [showHistory, setShowHistory] = useState(false);
  const [showBookmarks, setShowBookmarks] = useState(false);
  const [extractedData, setExtractedData] = useState(null);

  const {
    currentPage,
    history,
    bookmarks,
    lastSearch,
    loading,
    error,
    fetchPage,
    search,
    extractFinancialData,
    addBookmark,
    removeBookmark,
    clearHistory
  } = useBrowsing();

  const handleUrlSubmit = async (e) => {
    e.preventDefault();

    if (!url) return;

    try {
      // Add protocol if missing
      let fullUrl = url;
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        fullUrl = `https://${url}`;
      }

      await fetchPage(fullUrl);
      setShowHistory(false);
      setShowBookmarks(false);
    } catch (error) {
      console.error('Error fetching page:', error);
    }
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();

    if (!searchQuery) return;

    try {
      await search(searchQuery);
      setActiveTab('search');
      setShowHistory(false);
      setShowBookmarks(false);
    } catch (error) {
      console.error('Error searching:', error);
    }
  };

  const handleExtractFinancialData = async () => {
    if (!currentPage) return;

    try {
      const data = await extractFinancialData(currentPage.url);
      setExtractedData(data);
      setActiveTab('data');
    } catch (error) {
      console.error('Error extracting financial data:', error);
    }
  };

  const handleBookmarkToggle = () => {
    if (!currentPage) return;

    const isBookmarked = bookmarks.some(b => b.url === currentPage.url);

    if (isBookmarked) {
      removeBookmark(currentPage.url);
    } else {
      addBookmark(currentPage);
    }
  };

  const handleHistoryClick = (historyItem) => {
    fetchPage(historyItem.url);
    setShowHistory(false);
  };

  const handleBookmarkClick = (bookmark) => {
    fetchPage(bookmark.url);
    setShowBookmarks(false);
  };

  const renderBrowserTab = () => {
    return (
      <div className="h-full flex flex-col">
        {currentPage ? (
          <div className="flex-1 overflow-auto p-4">
            <div className="bg-white rounded-lg shadow-md p-4 mb-4">
              <h2 className="text-xl font-semibold mb-2">{currentPage.title}</h2>
              <p className="text-sm text-gray-500 mb-4">{currentPage.url}</p>

              <div className="flex space-x-2 mb-4">
                <button
                  type="button"
                  onClick={handleBookmarkToggle}
                  className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                    bookmarks.some(b => b.url === currentPage.url)
                      ? 'bg-yellow-100 text-yellow-800 border-yellow-300'
                      : 'bg-white text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <FiBookmark className="mr-2 -ml-1 h-4 w-4" />
                  {bookmarks.some(b => b.url === currentPage.url) ? 'Bookmarked' : 'Bookmark'}
                </button>

                <button
                  type="button"
                  onClick={handleExtractFinancialData}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md bg-white text-gray-700 hover:bg-gray-50"
                >
                  <FiDownload className="mr-2 -ml-1 h-4 w-4" />
                  Extract Financial Data
                </button>

                <a
                  href={currentPage.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md bg-white text-gray-700 hover:bg-gray-50"
                >
                  <FiExternalLink className="mr-2 -ml-1 h-4 w-4" />
                  Open in New Tab
                </a>
              </div>

              {currentPage.metadata && Object.keys(currentPage.metadata).length > 0 && (
                <div className="mb-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-1">Metadata</h3>
                  <div className="bg-gray-50 p-2 rounded text-xs">
                    {currentPage.metadata.description && (
                      <p className="mb-1"><span className="font-medium">Description:</span> {currentPage.metadata.description}</p>
                    )}
                    {currentPage.metadata.author && (
                      <p className="mb-1"><span className="font-medium">Author:</span> {currentPage.metadata.author}</p>
                    )}
                    {currentPage.metadata.keywords && (
                      <p><span className="font-medium">Keywords:</span> {Array.isArray(currentPage.metadata.keywords) ? currentPage.metadata.keywords.join(', ') : currentPage.metadata.keywords}</p>
                    )}
                  </div>
                </div>
              )}

              <div className="prose max-w-none">
                <div className="whitespace-pre-wrap">{currentPage.content}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <FiSearch className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No page loaded</h3>
              <p className="mt-1 text-sm text-gray-500">Enter a URL or search for something to get started.</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderSearchTab = () => {
    return (
      <div className="h-full overflow-auto p-4">
        {lastSearch ? (
          <div>
            <div className="mb-4">
              <h2 className="text-lg font-medium text-gray-900">Search Results for "{lastSearch.query}"</h2>
              <p className="text-sm text-gray-500">
                {lastSearch.totalResults} results ({lastSearch.searchTime.toFixed(2)} seconds)
              </p>
            </div>

            <div className="space-y-4">
              {lastSearch.results.map((result, index) => (
                <div key={index} className="bg-white rounded-lg shadow-md p-4">
                  <h3 className="text-lg font-medium text-blue-600 mb-1">
                    <button
                      onClick={() => fetchPage(result.url)}
                      className="hover:underline text-left"
                    >
                      {result.title}
                    </button>
                  </h3>
                  <p className="text-sm text-green-700 mb-2">{result.url}</p>
                  <p className="text-sm text-gray-600">{result.snippet}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <FiSearch className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No search results</h3>
              <p className="mt-1 text-sm text-gray-500">Search for something to see results here.</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderDataTab = () => {
    return (
      <div className="h-full overflow-auto p-4">
        {extractedData ? (
          <div>
            <div className="mb-4">
              <h2 className="text-lg font-medium text-gray-900">Extracted Financial Data</h2>
              <p className="text-sm text-gray-500">
                From: <a href={extractedData.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{extractedData.url}</a>
              </p>
              <p className="text-sm text-gray-500">
                Extracted at: {new Date(extractedData.extractedAt).toLocaleString()}
              </p>
            </div>

            {extractedData.securities.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                <h3 className="text-md font-medium text-gray-900 mb-2">Securities</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Identifier</th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {extractedData.securities.map((security, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{security.type}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{security.identifier}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{security.name}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {Object.keys(extractedData.metrics).length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                <h3 className="text-md font-medium text-gray-900 mb-2">Financial Metrics</h3>
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
                  {Object.entries(extractedData.metrics).map(([key, value]) => (
                    <div key={key} className="bg-gray-50 p-3 rounded-lg">
                      <h4 className="text-xs font-medium text-gray-500 uppercase">{key.replace(/([A-Z])/g, ' $1').trim()}</h4>
                      <p className="mt-1 text-lg font-semibold text-gray-700">{value}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {extractedData.tables.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                <h3 className="text-md font-medium text-gray-900 mb-2">Tables</h3>
                <div className="space-y-4">
                  {extractedData.tables.map((table, tableIndex) => (
                    <div key={tableIndex} className="border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
                        <h4 className="text-sm font-medium text-gray-700">Table {tableIndex + 1}</h4>
                      </div>
                      <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              {table.headers.map((header, headerIndex) => (
                                <th key={headerIndex} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  {header}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="bg-white divide-y divide-gray-200">
                            {table.rows.map((row, rowIndex) => (
                              <tr key={rowIndex}>
                                {row.map((cell, cellIndex) => (
                                  <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {extractedData.charts.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-4 mb-4">
                <h3 className="text-md font-medium text-gray-900 mb-2">Charts</h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {extractedData.charts.map((chart, index) => (
                    <div key={index} className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">{chart.title}</h4>
                      <div className="h-40 flex items-center justify-center bg-gray-100 rounded border border-gray-200">
                        <p className="text-sm text-gray-500">Chart data not available</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <FiDownload className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No financial data</h3>
              <p className="mt-1 text-sm text-gray-500">
                Browse to a financial website and click "Extract Financial Data" to see results here.
              </p>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-lg overflow-hidden h-[calc(100vh-12rem)]">
      <div className="bg-gray-100 p-4 border-b border-gray-200">
        <div className="flex space-x-2 mb-2">
          <button
            type="button"
            onClick={() => window.history.back()}
            className="p-2 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
            title="Back"
          >
            <FiArrowLeft className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => window.history.forward()}
            className="p-2 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
            title="Forward"
          >
            <FiArrowRight className="h-5 w-5" />
          </button>
          <button
            type="button"
            onClick={() => currentPage && fetchPage(currentPage.url)}
            className="p-2 rounded-md text-gray-500 hover:bg-gray-200 hover:text-gray-700"
            title="Refresh"
          >
            <FiRefreshCw className="h-5 w-5" />
          </button>
        </div>

        <div className="flex space-x-2">
          <div className="flex-1">
            <form onSubmit={handleUrlSubmit} className="flex">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL..."
                className="flex-1 min-w-0 block w-full px-3 py-2 rounded-l-md border border-gray-300 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                disabled={loading}
              />
              <button
                type="submit"
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md shadow-sm text-white ${
                  loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                disabled={loading}
              >
                Go
              </button>
            </form>
          </div>

          <div className="flex-1">
            <form onSubmit={handleSearchSubmit} className="flex">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search..."
                className="flex-1 min-w-0 block w-full px-3 py-2 rounded-l-md border border-gray-300 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                disabled={loading}
              />
              <button
                type="submit"
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-r-md shadow-sm text-white ${
                  loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
                disabled={loading}
              >
                <FiSearch className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>

        <div className="flex mt-2">
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setShowHistory(!showHistory)}
              className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                showHistory ? 'bg-gray-200 text-gray-800' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FiClock className="mr-2 -ml-1 h-4 w-4" />
              History
            </button>

            <button
              type="button"
              onClick={() => setShowBookmarks(!showBookmarks)}
              className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                showBookmarks ? 'bg-gray-200 text-gray-800' : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FiBookmark className="mr-2 -ml-1 h-4 w-4" />
              Bookmarks
            </button>
          </div>

          <div className="ml-auto">
            <div className="flex space-x-2">
              <button
                type="button"
                onClick={() => setActiveTab('browser')}
                className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                  activeTab === 'browser' ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Browser
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('search')}
                className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                  activeTab === 'search' ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Search
              </button>

              <button
                type="button"
                onClick={() => setActiveTab('data')}
                className={`inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md ${
                  activeTab === 'data' ? 'bg-blue-100 text-blue-800 border-blue-300' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Financial Data
              </button>
            </div>
          </div>
        </div>

        {showHistory && (
          <div className="absolute z-10 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200">
            <div className="p-2 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-sm font-medium text-gray-700">History</h3>
              <button
                type="button"
                onClick={clearHistory}
                className="text-xs text-red-600 hover:text-red-800"
              >
                Clear All
              </button>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {history.length > 0 ? (
                <ul className="py-1">
                  {history.map((item, index) => (
                    <li key={index}>
                      <button
                        type="button"
                        onClick={() => handleHistoryClick(item)}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <div className="truncate font-medium">{item.title}</div>
                        <div className="truncate text-xs text-gray-500">{item.url}</div>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-4 text-sm text-gray-500 text-center">No history</div>
              )}
            </div>
          </div>
        )}

        {showBookmarks && (
          <div className="absolute z-10 mt-2 w-64 bg-white rounded-md shadow-lg border border-gray-200">
            <div className="p-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-700">Bookmarks</h3>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {bookmarks.length > 0 ? (
                <ul className="py-1">
                  {bookmarks.map((bookmark, index) => (
                    <li key={index}>
                      <button
                        type="button"
                        onClick={() => handleBookmarkClick(bookmark)}
                        className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        <div className="truncate font-medium">{bookmark.title}</div>
                        <div className="truncate text-xs text-gray-500">{bookmark.url}</div>
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="p-4 text-sm text-gray-500 text-center">No bookmarks</div>
              )}
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}

      {error && (
        <div className="bg-red-50 p-4 border-b border-red-200">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="h-full">
        {activeTab === 'browser' && renderBrowserTab()}
        {activeTab === 'search' && renderSearchTab()}
        {activeTab === 'data' && renderDataTab()}
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default WebBrowser;
