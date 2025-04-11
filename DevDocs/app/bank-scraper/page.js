'use client';

import { useState, useEffect } from 'react';
import { getBankTypes, startScraping, getUserResults } from '../../services/bankScraperClient';
import { v4 as uuidv4 } from 'uuid';

export default function BankScraperPage() {
  const [selectedBank, setSelectedBank] = useState('');
  const [credentials, setCredentials] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [bankTypes, setBankTypes] = useState({});
  const [userId, setUserId] = useState('');
  const [savedResults, setSavedResults] = useState([]);
  const [loadingSaved, setLoadingSaved] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  
  // Initialize on page load
  useEffect(() => {
    // Generate or retrieve user ID
    const storedUserId = localStorage.getItem('bankScraperUserId');
    if (storedUserId) {
      setUserId(storedUserId);
    } else {
      const newUserId = uuidv4();
      localStorage.setItem('bankScraperUserId', newUserId);
      setUserId(newUserId);
    }
    
    // Fetch available bank types
    async function fetchBankTypes() {
      try {
        const response = await getBankTypes();
        if (response.success) {
          setBankTypes(response.bankTypes);
        } else {
          console.error('Error fetching bank types:', response);
          setError('Failed to load bank information. Please try again later.');
        }
      } catch (error) {
        console.error('Failed to load bank information:', error);
        setError('Failed to load bank information. Please check if the Bank Scraper Service is running.');
      }
    }
    
    fetchBankTypes();
  }, []);
  
  const handleBankChange = (e) => {
    const bankKey = e.target.value;
    setSelectedBank(bankKey);
    
    // Reset credentials when bank changes
    if (bankTypes[bankKey]) {
      const emptyCredentials = {};
      bankTypes[bankKey].requiredCredentials.forEach(field => {
        emptyCredentials[field] = '';
      });
      setCredentials(emptyCredentials);
    }
  };

  const handleCredentialChange = (field, value) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    
    try {
      // Show warning about visible browser
      alert("The bank scraper will open a new browser window. Please don't close it until the process is complete.");
      
      const response = await startScraping(selectedBank, credentials, userId, {
        showBrowser: true, // Show browser for better user experience
        daysBack: 90 // Get last 90 days of transactions
      });
      
      setResult(response);
    } catch (error) {
      console.error('Error scraping bank data:', error);
      setError(error.message || 'An error occurred while scraping bank data');
    } finally {
      setLoading(false);
    }
  };
  
  const loadSavedResults = async () => {
    if (!userId) return;
    
    setLoadingSaved(true);
    setError(null);
    
    try {
      const response = await getUserResults(userId);
      if (response.success) {
        setSavedResults(response.results || []);
        setShowHistory(true);
      } else {
        setError('Failed to load saved results');
      }
    } catch (error) {
      console.error('Error loading saved results:', error);
      setError('Failed to load saved results: ' + error.message);
    } finally {
      setLoadingSaved(false);
    }
  };
  
  const viewSavedResult = (result) => {
    setResult(result.data);
    setShowHistory(false);
  };

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Israeli Bank Scraper</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
        <div className="md:col-span-4">
          <button 
            onClick={() => setShowHistory(false)}
            className={`px-4 py-2 mr-2 rounded ${!showHistory ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
          >
            New Scrape
          </button>
          <button 
            onClick={loadSavedResults}
            className={`px-4 py-2 rounded ${showHistory ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            disabled={loadingSaved}
          >
            {loadingSaved ? 'Loading...' : 'View History'}
          </button>
        </div>
      </div>
      
      {!showHistory ? (
        <div className="bg-white shadow-md rounded p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Select Bank and Enter Credentials</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-gray-700 mb-2">Select Bank:</label>
              <select 
                value={selectedBank}
                onChange={handleBankChange}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                disabled={loading}
                required
              >
                <option value="">-- Select a Bank --</option>
                {Object.keys(bankTypes).map(bankKey => (
                  <option key={bankKey} value={bankKey}>
                    {bankTypes[bankKey].description}
                  </option>
                ))}
              </select>
            </div>
            
            {selectedBank && bankTypes[selectedBank] && (
              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Enter Credentials:</h3>
                
                {bankTypes[selectedBank].requiredCredentials.map(field => (
                  <div key={field} className="mb-3">
                    <label className="block text-gray-700 mb-1 capitalize">
                      {field.replace(/([A-Z])/g, ' $1').trim()}:
                    </label>
                    <input
                      type="text"
                      value={credentials[field] || ''}
                      onChange={(e) => handleCredentialChange(field, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded"
                      disabled={loading}
                      required
                    />
                  </div>
                ))}
              </div>
            )}
            
            {selectedBank && (
              <button
                type="submit"
                className={`px-4 py-2 text-white rounded ${loading ? 'bg-gray-500' : 'bg-blue-600 hover:bg-blue-700'}`}
                disabled={loading}
              >
                {loading ? 'Scraping Data...' : 'Get Account Data'}
              </button>
            )}
          </form>
        </div>
      ) : (
        <div className="bg-white shadow-md rounded p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Previous Scraping Results</h2>
          
          {savedResults.length === 0 ? (
            <p>No saved results found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Date</th>
                    <th className="text-left p-2">Bank</th>
                    <th className="text-left p-2">Accounts</th>
                    <th className="text-left p-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {savedResults.map((result, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2">{new Date(result.timestamp).toLocaleString()}</td>
                      <td className="p-2">{result.filename.split('-')[1]}</td>
                      <td className="p-2">{result.data.accounts?.length || 0}</td>
                      <td className="p-2">
                        <button
                          onClick={() => viewSavedResult(result)}
                          className="px-3 py-1 bg-blue-100 text-blue-800 rounded hover:bg-blue-200"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
      
      {loading && (
        <div className="text-center p-6">
          <p className="text-lg">
            Scraping data from the bank... This may take up to a minute.
          </p>
          <p className="text-sm text-gray-600 mt-2">
            A browser window has been opened to access the bank's website securely. 
            Please don't close it until the process is complete.
          </p>
        </div>
      )}
      
      {result && (
        <div className="bg-white shadow-md rounded p-6">
          <h2 className="text-xl font-semibold mb-4">Results</h2>
          
          {result.success ? (
            <>
              <div className="mb-4 text-green-600 font-medium">
                Successfully scraped data from your account.
              </div>
              
              {result.accounts && result.accounts.map((account, idx) => (
                <div key={idx} className="mb-6 border-t pt-4">
                  <h3 className="text-lg font-medium mb-2">
                    Account: {account.accountNumber}
                    {account.balance !== undefined && (
                      <span className="ml-3">
                        Balance: {account.balance}
                      </span>
                    )}
                  </h3>
                  
                  {account.txns && account.txns.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left p-2">Date</th>
                            <th className="text-left p-2">Description</th>
                            <th className="text-left p-2">Amount</th>
                            <th className="text-left p-2">Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {account.txns.map((txn, txnIdx) => (
                            <tr key={txnIdx} className="border-b hover:bg-gray-50">
                              <td className="p-2">{txn.date.substring(0, 10)}</td>
                              <td className="p-2">{txn.description}</td>
                              <td className={`p-2 ${txn.chargedAmount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                {txn.chargedAmount}
                                {txn.originalCurrency !== 'ILS' && (
                                  <span className="text-sm ml-1">
                                    {txn.originalAmount} {txn.originalCurrency}
                                  </span>
                                )}
                              </td>
                              <td className="p-2">
                                <span className={`px-2 py-1 rounded text-xs ${
                                  txn.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                  {txn.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <p>No transactions found for this account.</p>
                  )}
                </div>
              ))}
            </>
          ) : (
            <div className="text-red-600">
              Failed to scrape data: {result.errorType} - {result.errorMessage}
            </div>
          )}
        </div>
      )}
      
      <div className="mt-8 text-sm text-gray-600 bg-gray-50 p-4 rounded">
        <h3 className="font-semibold mb-1">Important Notes:</h3>
        <ul className="list-disc pl-5 space-y-1">
          <li>Your credentials are only sent to the bank's website and are never stored.</li>
          <li>This tool uses the open-source Israeli Bank Scrapers library to securely access your data.</li>
          <li>A browser window will open during the scraping process - this is normal and allows you to see what's happening.</li>
          <li>Make sure the Bank Scraper Service is running before using this interface.</li>
        </ul>
      </div>
    </div>
  );
}