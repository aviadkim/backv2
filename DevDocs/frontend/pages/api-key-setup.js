import React, { useState, useEffect } from 'react';
import { FiClipboard, FiCheck, FiExternalLink, FiInfo, FiKey } from 'react-icons/fi';
import OpenRouterKeyManager from '../components/OpenRouterKeyManager';
import Link from 'next/link';

const ApiKeySetup = () => {
  const [copiedKey, setCopiedKey] = useState(null);
  const [apiStatus, setApiStatus] = useState({
    supabase: 'unknown',
    googleCloud: 'unknown',
    ocr: 'unknown',
    chatbot: 'unknown'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    supabaseUrl: '',
    supabaseKey: '',
    googleCloudKey: '',
    visionApiEnabled: false,
    chatbotEnabled: false
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  // Copy text to clipboard
  const copyToClipboard = (text, keyName) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(keyName);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  // Load API status and configuration values
  useEffect(() => {
    const loadApiStatus = async () => {
      try {
        const response = await fetch('/api/config/status');
        if (response.ok) {
          const data = await response.json();
          setApiStatus({
            supabase: data.supabase,
            googleCloud: data.googleCloud,
            ocr: data.ocr,
            chatbot: data.chatbot
          });
        }
      } catch (error) {
        console.error('Error loading API status:', error);
      }
    };

    const loadConfigValues = async () => {
      try {
        // Load Supabase URL
        const supabaseUrlResponse = await fetch('/api/config/get?key=NEXT_PUBLIC_SUPABASE_URL');
        if (supabaseUrlResponse.ok) {
          const data = await supabaseUrlResponse.json();
          setFormData(prev => ({ ...prev, supabaseUrl: data.value || '' }));
        }

        // Load Google Cloud API key status
        const googleCloudResponse = await fetch('/api/config/get?key=NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY');
        if (googleCloudResponse.ok) {
          const data = await googleCloudResponse.json();
          setFormData(prev => ({ ...prev, googleCloudKey: data.isSet ? 'configured' : '' }));
        }

        // Load Vision API status
        const visionApiResponse = await fetch('/api/config/get?key=NEXT_PUBLIC_VISION_API_ENABLED');
        if (visionApiResponse.ok) {
          const data = await visionApiResponse.json();
          setFormData(prev => ({ ...prev, visionApiEnabled: data.value === 'true' }));
        }

        // Load Chatbot API status
        const chatbotResponse = await fetch('/api/config/get?key=NEXT_PUBLIC_CHATBOT_ENABLED');
        if (chatbotResponse.ok) {
          const data = await chatbotResponse.json();
          setFormData(prev => ({ ...prev, chatbotEnabled: data.value === 'true' }));
        }
      } catch (error) {
        console.error('Error loading configuration values:', error);
      }
    };

    loadApiStatus();
    loadConfigValues();
  }, []);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  // Save API keys
  const handleSaveApiKeys = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const updates = {};

      // Update Supabase configuration
      if (formData.supabaseUrl) {
        updates.NEXT_PUBLIC_SUPABASE_URL = formData.supabaseUrl;
      }

      if (formData.supabaseKey) {
        updates.NEXT_PUBLIC_SUPABASE_ANON_KEY = formData.supabaseKey;
      }

      // Update Google Cloud configuration
      if (formData.googleCloudKey && formData.googleCloudKey !== 'configured') {
        updates.NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY = formData.googleCloudKey;
      }

      // Update Vision API configuration
      updates.NEXT_PUBLIC_VISION_API_ENABLED = formData.visionApiEnabled ? 'true' : 'false';

      // Update Chatbot API configuration
      updates.NEXT_PUBLIC_CHATBOT_ENABLED = formData.chatbotEnabled ? 'true' : 'false';

      // Save the configuration
      const response = await fetch('/api/config/update-multiple', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ updates })
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'API keys saved successfully. Please restart the server for changes to take effect.' });

        // Clear sensitive form fields
        setFormData(prev => ({
          ...prev,
          supabaseKey: '',
          googleCloudKey: formData.googleCloudKey ? 'configured' : ''
        }));

        // Refresh API status
        const statusResponse = await fetch('/api/config/status');
        if (statusResponse.ok) {
          const data = await statusResponse.json();
          setApiStatus({
            supabase: data.supabase,
            googleCloud: data.googleCloud,
            ocr: data.ocr,
            chatbot: data.chatbot
          });
        }
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Failed to save API keys' });
      }
    } catch (error) {
      console.error('Error saving API keys:', error);
      setMessage({ type: 'error', text: error.message || 'An unexpected error occurred' });
    } finally {
      setIsLoading(false);
    }
  };

  // Test API connections
  const testApiConnections = async () => {
    setIsLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch('/api/config/status');
      if (response.ok) {
        const data = await response.json();
        setApiStatus({
          supabase: data.supabase,
          googleCloud: data.googleCloud,
          ocr: data.ocr,
          chatbot: data.chatbot
        });

        setMessage({ type: 'success', text: 'API connections tested successfully' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Failed to test API connections' });
      }
    } catch (error) {
      console.error('Error testing API connections:', error);
      setMessage({ type: 'error', text: error.message || 'An unexpected error occurred' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">API Key Setup Guide</h1>

      <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8">
        <div className="flex">
          <div className="flex-shrink-0">
            <FiInfo className="h-5 w-5 text-blue-500" />
          </div>
          <div className="ml-3">
            <p className="text-sm text-blue-700">
              This guide will help you set up all the necessary API keys for the DevDocs application.
              Follow the step-by-step instructions for each service.
            </p>
          </div>
        </div>
      </div>

      {/* API Status Overview */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">API Connection Status</h2>
          <button
            onClick={testApiConnections}
            disabled={isLoading}
            className="flex items-center px-3 py-2 bg-blue-50 text-blue-600 rounded-md hover:bg-blue-100 disabled:opacity-50"
          >
            {isLoading ? 'Testing...' : 'Test Connections'}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Supabase</span>
              {apiStatus.supabase === 'valid' ? (
                <FiCheck className="text-green-500" />
              ) : apiStatus.supabase === 'invalid' ? (
                <span className="text-red-500">✗</span>
              ) : (
                <span className="text-yellow-500">?</span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {apiStatus.supabase === 'valid' ? 'Connected successfully' :
               apiStatus.supabase === 'invalid' ? 'Invalid API key' :
               'Not configured'}
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Google Cloud</span>
              {apiStatus.googleCloud === 'valid' ? (
                <FiCheck className="text-green-500" />
              ) : apiStatus.googleCloud === 'invalid' ? (
                <span className="text-red-500">✗</span>
              ) : (
                <span className="text-yellow-500">?</span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {apiStatus.googleCloud === 'valid' ? 'Connected successfully' :
               apiStatus.googleCloud === 'invalid' ? 'Invalid API key' :
               'Not configured'}
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">OCR Service</span>
              {apiStatus.ocr === 'valid' ? (
                <FiCheck className="text-green-500" />
              ) : apiStatus.ocr === 'invalid' ? (
                <span className="text-red-500">✗</span>
              ) : (
                <span className="text-yellow-500">?</span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {apiStatus.ocr === 'valid' ? 'Enabled and configured' :
               apiStatus.ocr === 'invalid' ? 'Configuration error' :
               'Not enabled'}
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <div className="flex items-center mb-2">
              <span className="text-lg mr-2">Chatbot</span>
              {apiStatus.chatbot === 'valid' ? (
                <FiCheck className="text-green-500" />
              ) : apiStatus.chatbot === 'invalid' ? (
                <span className="text-red-500">✗</span>
              ) : (
                <span className="text-yellow-500">?</span>
              )}
            </div>
            <p className="text-sm text-gray-600">
              {apiStatus.chatbot === 'valid' ? 'Enabled and configured' :
               apiStatus.chatbot === 'invalid' ? 'Configuration error' :
               'Not enabled'}
            </p>
          </div>
        </div>

        {message.text && (
          <div className={`mt-4 p-3 rounded-md ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
            {message.text}
          </div>
        )}
      </div>

      {/* API Key Configuration Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Configure API Keys</h2>

        <form onSubmit={handleSaveApiKeys}>
          {/* Supabase Configuration */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Supabase Configuration</h3>

            <div className="mb-4">
              <label htmlFor="supabaseUrl" className="block text-sm font-medium text-gray-700 mb-1">
                Supabase URL
              </label>
              <input
                type="text"
                id="supabaseUrl"
                name="supabaseUrl"
                value={formData.supabaseUrl}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="https://your-project-id.supabase.co"
              />
            </div>

            <div className="mb-4">
              <label htmlFor="supabaseKey" className="block text-sm font-medium text-gray-700 mb-1">
                Supabase Anon Key
              </label>
              <input
                type="password"
                id="supabaseKey"
                name="supabaseKey"
                value={formData.supabaseKey}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              />
            </div>
          </div>

          {/* Google Cloud Configuration */}
          <div className="mb-6">
            <h3 className="text-lg font-medium mb-3">Google Cloud Configuration</h3>

            <div className="mb-4">
              <label htmlFor="googleCloudKey" className="block text-sm font-medium text-gray-700 mb-1">
                Google Cloud API Key
              </label>
              <input
                type="password"
                id="googleCloudKey"
                name="googleCloudKey"
                value={formData.googleCloudKey}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder={formData.googleCloudKey === 'configured' ? 'API key is configured (leave blank to keep current)' : 'AIzaSyA...'}
                disabled={formData.googleCloudKey === 'configured'}
              />
              {formData.googleCloudKey === 'configured' && (
                <button
                  type="button"
                  onClick={() => setFormData(prev => ({ ...prev, googleCloudKey: '' }))}
                  className="mt-2 text-sm text-blue-600 hover:underline"
                >
                  Change API key
                </button>
              )}
            </div>

            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id="visionApiEnabled"
                name="visionApiEnabled"
                checked={formData.visionApiEnabled}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="visionApiEnabled" className="ml-2 block text-sm text-gray-700">
                Enable Vision API (OCR)
              </label>
            </div>

            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id="chatbotEnabled"
                name="chatbotEnabled"
                checked={formData.chatbotEnabled}
                onChange={handleInputChange}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="chatbotEnabled" className="ml-2 block text-sm text-gray-700">
                Enable Chatbot API
              </label>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save API Keys'}
            </button>
          </div>
        </form>
      </div>

      {/* Supabase API Key */}
      <div id="supabase" className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <img src="/supabase-logo.png" alt="Supabase" className="h-6 w-6 mr-2" />
          Supabase API Key
        </h2>

        <div className="mb-4">
          <p className="text-gray-700 mb-4">
            Supabase is used as the primary database for storing documents and user data.
            You need to configure the Supabase URL and API key in your environment variables.
          </p>

          <h3 className="font-medium text-lg mb-2">Steps:</h3>

          <ol className="list-decimal pl-6 space-y-4 mb-6">
            <li>
              <p className="mb-1">Log in to your <a href="https://app.supabase.io" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Supabase Dashboard</a></p>
              <button
                onClick={() => window.open('https://app.supabase.io', '_blank')}
                className="flex items-center text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <FiExternalLink className="mr-1" />
                Open Supabase Dashboard
              </button>
            </li>

            <li>
              <p className="mb-1">Select your project: <strong>dnjnsotemnfrjlotgved</strong></p>
            </li>

            <li>
              <p className="mb-1">Go to Project Settings &gt; API</p>
            </li>

            <li>
              <p className="mb-1">Copy the <strong>Project URL</strong> and <strong>anon</strong> public API key</p>
              <div className="bg-gray-100 p-3 rounded-md mb-2">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-mono">Project URL:</span>
                  <button
                    onClick={() => copyToClipboard('https://dnjnsotemnfrjlotgved.supabase.co', 'supabase-url')}
                    className="flex items-center text-sm px-2 py-1 bg-white text-gray-700 rounded-md hover:bg-gray-200"
                  >
                    {copiedKey === 'supabase-url' ? <FiCheck className="mr-1" /> : <FiClipboard className="mr-1" />}
                    {copiedKey === 'supabase-url' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm font-mono">anon key:</span>
                  <button
                    onClick={() => copyToClipboard('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDk2ODYsImV4cCI6MjA1NTIyNTY4Nn0.GqTKv9B2MDAkBxHf0FLGKa60e-yZUDpyxXEychKVDo8', 'supabase-key')}
                    className="flex items-center text-sm px-2 py-1 bg-white text-gray-700 rounded-md hover:bg-gray-200"
                  >
                    {copiedKey === 'supabase-key' ? <FiCheck className="mr-1" /> : <FiClipboard className="mr-1" />}
                    {copiedKey === 'supabase-key' ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>
            </li>

            <li>
              <p className="mb-1">Create or update the <code>.env.local</code> file in the <code>DevDocs/frontend</code> directory with these values:</p>
              <div className="bg-gray-800 text-gray-100 p-3 rounded-md font-mono text-sm">
                <div className="mb-1">NEXT_PUBLIC_SUPABASE_URL=https://dnjnsotemnfrjlotgved.supabase.co</div>
                <div>NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuam5zb3RlbW5mcmpsb3RndmVkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk2NDk2ODYsImV4cCI6MjA1NTIyNTY4Nn0.GqTKv9B2MDAkBxHf0FLGKa60e-yZUDpyxXEychKVDo8</div>
              </div>
            </li>
          </ol>
        </div>
      </div>

      {/* OpenRouter API Key */}
      <div id="openrouter" className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <FiKey className="h-6 w-6 mr-2 text-indigo-600" />
          OpenRouter API Key
        </h2>

        <div className="mb-4">
          <p className="text-gray-700 mb-4">
            OpenRouter provides access to 300+ AI models including Optimus Alpha. This API key will be used by all agents in the application.
          </p>

          <OpenRouterKeyManager />
        </div>
      </div>

      {/* Google Cloud API Key */}
      <div id="google-cloud" className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <img src="/gcp-logo.png" alt="Google Cloud" className="h-6 w-6 mr-2" />
          Google Cloud API Key
        </h2>

        <div className="mb-4">
          <p className="text-gray-700 mb-4">
            Google Cloud Platform is used for various services including OCR, chatbot, and other AI features.
            You need to set up a project and create API keys for these services.
          </p>

          <h3 className="font-medium text-lg mb-2">Steps:</h3>

          <ol className="list-decimal pl-6 space-y-4 mb-6">
            <li>
              <p className="mb-1">Log in to the <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Console</a></p>
              <button
                onClick={() => window.open('https://console.cloud.google.com', '_blank')}
                className="flex items-center text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <FiExternalLink className="mr-1" />
                Open Google Cloud Console
              </button>
            </li>

            <li>
              <p className="mb-1">Select your project: <strong>github-456508</strong></p>
              <p className="text-sm text-gray-600">If you don't have a project yet, create one by clicking "New Project" at the top right.</p>
            </li>

            <li>
              <p className="mb-1">Go to "APIs & Services" &gt; "Credentials"</p>
            </li>

            <li>
              <p className="mb-1">Click "Create Credentials" &gt; "API Key"</p>
              <p className="text-sm text-gray-600">This will create a general API key for your project.</p>
            </li>

            <li>
              <p className="mb-1">Copy the generated API key and add it to your <code>.env.local</code> file:</p>
              <div className="bg-gray-800 text-gray-100 p-3 rounded-md font-mono text-sm">
                <div>NEXT_PUBLIC_GOOGLE_CLOUD_API_KEY=your_api_key_here</div>
              </div>
            </li>

            <li>
              <p className="mb-1">Restrict the API key to only the services you need:</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Click on the API key you just created</li>
                <li>Under "API restrictions", select "Restrict key"</li>
                <li>Select the APIs you need (Vision API, Dialogflow API, etc.)</li>
                <li>Click "Save"</li>
              </ol>
            </li>
          </ol>
        </div>
      </div>

      {/* OCR API Key */}
      <div id="ocr" className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <FiKey className="h-6 w-6 mr-2 text-purple-600" />
          OCR API Key (Google Cloud Vision)
        </h2>

        <div className="mb-4">
          <p className="text-gray-700 mb-4">
            The OCR functionality uses Google Cloud Vision API to extract text from documents.
            You need to enable this API and set up authentication.
          </p>

          <h3 className="font-medium text-lg mb-2">Steps:</h3>

          <ol className="list-decimal pl-6 space-y-4 mb-6">
            <li>
              <p className="mb-1">Go to the <a href="https://console.cloud.google.com/apis/library/vision.googleapis.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Vision API</a> page</p>
              <button
                onClick={() => window.open('https://console.cloud.google.com/apis/library/vision.googleapis.com', '_blank')}
                className="flex items-center text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <FiExternalLink className="mr-1" />
                Open Vision API Page
              </button>
            </li>

            <li>
              <p className="mb-1">Click "Enable" to enable the Vision API for your project</p>
            </li>

            <li>
              <p className="mb-1">Go to "APIs & Services" &gt; "Credentials"</p>
            </li>

            <li>
              <p className="mb-1">Click "Create Credentials" &gt; "Service Account"</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Enter a name for the service account (e.g., "ocr-service")</li>
                <li>Click "Create and Continue"</li>
                <li>Grant the role "Cloud Vision API User" to the service account</li>
                <li>Click "Continue" and then "Done"</li>
              </ol>
            </li>

            <li>
              <p className="mb-1">Create a key for the service account:</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Click on the service account you just created</li>
                <li>Go to the "Keys" tab</li>
                <li>Click "Add Key" &gt; "Create new key"</li>
                <li>Select "JSON" and click "Create"</li>
                <li>The key file will be downloaded to your computer</li>
              </ol>
            </li>

            <li>
              <p className="mb-1">Save the key file in a secure location and add the path to your <code>.env.local</code> file:</p>
              <div className="bg-gray-800 text-gray-100 p-3 rounded-md font-mono text-sm">
                <div>GOOGLE_APPLICATION_CREDENTIALS=path/to/your/keyfile.json</div>
                <div>NEXT_PUBLIC_VISION_API_ENABLED=true</div>
              </div>
            </li>
          </ol>
        </div>
      </div>

      {/* Chatbot API Key */}
      <div id="chatbot" className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <FiKey className="h-6 w-6 mr-2 text-green-600" />
          Chatbot API Key (Google Dialogflow)
        </h2>

        <div className="mb-4">
          <p className="text-gray-700 mb-4">
            The chatbot functionality uses Google Dialogflow to provide conversational AI capabilities.
            You need to enable this API and set up authentication.
          </p>

          <h3 className="font-medium text-lg mb-2">Steps:</h3>

          <ol className="list-decimal pl-6 space-y-4 mb-6">
            <li>
              <p className="mb-1">Go to the <a href="https://console.cloud.google.com/apis/library/dialogflow.googleapis.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Cloud Dialogflow API</a> page</p>
              <button
                onClick={() => window.open('https://console.cloud.google.com/apis/library/dialogflow.googleapis.com', '_blank')}
                className="flex items-center text-sm px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200"
              >
                <FiExternalLink className="mr-1" />
                Open Dialogflow API Page
              </button>
            </li>

            <li>
              <p className="mb-1">Click "Enable" to enable the Dialogflow API for your project</p>
            </li>

            <li>
              <p className="mb-1">Go to "APIs & Services" &gt; "Credentials"</p>
            </li>

            <li>
              <p className="mb-1">Click "Create Credentials" &gt; "Service Account"</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Enter a name for the service account (e.g., "chatbot-service")</li>
                <li>Click "Create and Continue"</li>
                <li>Grant the role "Dialogflow API Client" to the service account</li>
                <li>Click "Continue" and then "Done"</li>
              </ol>
            </li>

            <li>
              <p className="mb-1">Create a key for the service account:</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Click on the service account you just created</li>
                <li>Go to the "Keys" tab</li>
                <li>Click "Add Key" &gt; "Create new key"</li>
                <li>Select "JSON" and click "Create"</li>
                <li>The key file will be downloaded to your computer</li>
              </ol>
            </li>

            <li>
              <p className="mb-1">Save the key file in a secure location and add the path to your <code>.env.local</code> file:</p>
              <div className="bg-gray-800 text-gray-100 p-3 rounded-md font-mono text-sm">
                <div>DIALOGFLOW_CREDENTIALS=path/to/your/dialogflow-keyfile.json</div>
                <div>NEXT_PUBLIC_CHATBOT_ENABLED=true</div>
              </div>
            </li>

            <li>
              <p className="mb-1">Create a Dialogflow agent:</p>
              <ol className="list-disc pl-6 space-y-2 mt-2">
                <li>Go to the <a href="https://dialogflow.cloud.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Dialogflow Console</a></li>
                <li>Click "Create Agent"</li>
                <li>Enter a name for your agent (e.g., "DevDocs Assistant")</li>
                <li>Select your Google Cloud project</li>
                <li>Click "Create"</li>
              </ol>
            </li>

            <li>
              <p className="mb-1">Add the agent ID to your <code>.env.local</code> file:</p>
              <div className="bg-gray-800 text-gray-100 p-3 rounded-md font-mono text-sm">
                <div>NEXT_PUBLIC_DIALOGFLOW_AGENT_ID=your_agent_id</div>
              </div>
            </li>
          </ol>
        </div>
      </div>

      {/* Next Steps */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">Next Steps</h2>

        <p className="text-gray-700 mb-4">
          After setting up all the API keys, you should restart your development server for the changes to take effect.
          You can then run the tests to verify that everything is working correctly.
        </p>

        <div className="flex space-x-4">
          <Link href="/dev-test-center" className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
            Go to Test Center
          </Link>

          <Link href="/" className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200">
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ApiKeySetup;
