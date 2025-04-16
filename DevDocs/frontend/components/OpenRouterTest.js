import React, { useState } from 'react';
import { FiSend, FiCheck, FiAlertCircle } from 'react-icons/fi';
import AccessibilityWrapper from './AccessibilityWrapper';

const OpenRouterTest = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess(false);
    setResponse('');
    
    try {
      const result = await fetch('/api/openrouter/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ prompt })
      });
      
      const data = await result.json();
      
      if (!result.ok) {
        throw new Error(data.message || 'Failed to get response from OpenRouter');
      }
      
      setResponse(data.data.response);
      setSuccess(true);
    } catch (error) {
      console.error('Error testing OpenRouter:', error);
      setError(error.message || 'An error occurred while testing OpenRouter');
    } finally {
      setLoading(false);
    }
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center mb-4">
          <h2 className="text-lg font-medium text-gray-900">Test OpenRouter API</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="mb-4">
          <div className="mb-4">
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-1">
              Enter a prompt for Optimus Alpha
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="What is the capital of France?"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              rows={3}
            />
          </div>
          
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
              }`}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <FiSend className="mr-2 -ml-1 h-5 w-5" />
                  Send
                </>
              )}
            </button>
          </div>
        </form>
        
        {error && (
          <div className="mb-4 p-3 bg-red-50 rounded-md">
            <p className="text-sm text-red-800 flex items-start">
              <FiAlertCircle className="h-5 w-5 mr-1 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </p>
          </div>
        )}
        
        {success && response && (
          <div className="mb-4">
            <div className="flex items-center mb-2">
              <FiCheck className="h-5 w-5 text-green-500 mr-1" />
              <h3 className="text-md font-medium text-gray-900">Response from Optimus Alpha</h3>
            </div>
            <div className="p-4 bg-gray-50 rounded-md">
              <p className="text-gray-800 whitespace-pre-wrap">{response}</p>
            </div>
          </div>
        )}
      </div>
    </AccessibilityWrapper>
  );
};

export default OpenRouterTest;
