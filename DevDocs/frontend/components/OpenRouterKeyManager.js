import React, { useState, useEffect } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiKey, FiEye, FiEyeOff, FiSave, FiCheck, FiAlertCircle } from 'react-icons/fi';

const OpenRouterKeyManager = () => {
  const [apiKey, setApiKey] = useState('');
  const [maskedKey, setMaskedKey] = useState('');
  const [isKeySet, setIsKeySet] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Fetch the current key status
  useEffect(() => {
    const fetchKeyStatus = async () => {
      setLoading(true);
      setError('');
      
      try {
        const response = await fetch('/api/config/get-openrouter-key-status');
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.message || 'Failed to fetch API key status');
        }
        
        setIsKeySet(data.data.isSet);
        setMaskedKey(data.data.maskedKey || '');
      } catch (error) {
        console.error('Error fetching OpenRouter API key status:', error);
        setError('Failed to fetch API key status');
      } finally {
        setLoading(false);
      }
    };
    
    fetchKeyStatus();
  }, []);

  // Handle saving the API key
  const handleSave = async (e) => {
    e.preventDefault();
    
    if (!apiKey) {
      setError('Please enter an API key');
      return;
    }
    
    // Validate the key format
    if (!apiKey.startsWith('sk-or-')) {
      setError('Invalid OpenRouter API key format. Keys should start with "sk-or-"');
      return;
    }
    
    setSaving(true);
    setError('');
    setSuccess(false);
    
    try {
      const response = await fetch('/api/config/set-openrouter-key', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Failed to save API key');
      }
      
      setSuccess(true);
      setIsKeySet(true);
      setMaskedKey(`${apiKey.substring(0, 8)}...${apiKey.substring(apiKey.length - 4)}`);
      setApiKey(''); // Clear the input for security
      setShowKey(false);
    } catch (error) {
      console.error('Error saving OpenRouter API key:', error);
      setError(error.message || 'Failed to save API key');
    } finally {
      setSaving(false);
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-4">
          <FiKey className="h-6 w-6 text-blue-500 mr-2" />
          <h2 className="text-lg font-medium text-gray-900">OpenRouter API Key</h2>
        </div>
        
        {loading ? (
          <div className="flex justify-center py-4">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <>
            {isKeySet && (
              <div className="mb-4 p-3 bg-blue-50 rounded-md">
                <p className="text-sm text-blue-800">
                  <FiCheck className="inline-block mr-1" /> OpenRouter API key is set: {maskedKey}
                </p>
              </div>
            )}
            
            <form onSubmit={handleSave}>
              <div className="mb-4">
                <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                  {isKeySet ? 'Update API Key' : 'Set API Key'}
                </label>
                <div className="relative">
                  <input
                    type={showKey ? 'text' : 'password'}
                    id="apiKey"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-or-v1-..."
                    className="block w-full pr-10 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-500"
                    onClick={() => setShowKey(!showKey)}
                  >
                    {showKey ? <FiEyeOff className="h-5 w-5" /> : <FiEye className="h-5 w-5" />}
                  </button>
                </div>
                <p className="mt-1 text-xs text-gray-500">
                  This key will be stored securely and used for all OpenRouter API calls.
                </p>
              </div>
              
              {error && (
                <div className="mb-4 p-3 bg-red-50 rounded-md">
                  <p className="text-sm text-red-800 flex items-start">
                    <FiAlertCircle className="h-5 w-5 mr-1 flex-shrink-0 mt-0.5" />
                    <span>{error}</span>
                  </p>
                </div>
              )}
              
              {success && (
                <div className="mb-4 p-3 bg-green-50 rounded-md">
                  <p className="text-sm text-green-800 flex items-start">
                    <FiCheck className="h-5 w-5 mr-1 flex-shrink-0 mt-0.5" />
                    <span>API key saved successfully!</span>
                  </p>
                </div>
              )}
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                    saving ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                  }`}
                >
                  {saving ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                      Saving...
                    </>
                  ) : (
                    <>
                      <FiSave className="mr-2 -ml-1 h-5 w-5" />
                      Save API Key
                    </>
                  )}
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </AccessibilityWrapper>
  );
};

export default OpenRouterKeyManager;
