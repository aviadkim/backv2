import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState({
    openRouter: '',
    supabase: '',
    aws: '',
    azure: ''
  });
  
  const [savedKeys, setSavedKeys] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  
  // Load saved API keys on component mount
  useEffect(() => {
    const loadSavedKeys = () => {
      try {
        const savedKeysJson = localStorage.getItem('findoc_api_keys');
        if (savedKeysJson) {
          const keys = JSON.parse(savedKeysJson);
          setSavedKeys(keys);
          
          // Show masked versions in the form
          const maskedKeys = {};
          Object.keys(keys).forEach(provider => {
            if (keys[provider]) {
              maskedKeys[provider] = '••••••••' + keys[provider].slice(-4);
            } else {
              maskedKeys[provider] = '';
            }
          });
          setApiKeys(maskedKeys);
        }
      } catch (error) {
        console.error('Error loading saved API keys:', error);
      }
    };
    
    loadSavedKeys();
  }, []);
  
  // Handle input change
  const handleInputChange = (provider, value) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }));
  };
  
  // Handle save API keys
  const handleSaveKeys = async () => {
    setIsLoading(true);
    setSaveStatus({ type: '', message: '' });
    
    try {
      // Prepare keys to save
      const keysToSave = { ...savedKeys };
      
      // Only update keys that have been changed (not masked)
      Object.keys(apiKeys).forEach(provider => {
        const value = apiKeys[provider];
        if (value && !value.startsWith('••••••••')) {
          keysToSave[provider] = value;
        }
      });
      
      // Save to localStorage
      localStorage.setItem('findoc_api_keys', JSON.stringify(keysToSave));
      
      // If OpenRouter key is provided, configure the agent
      if (keysToSave.openRouter && (!savedKeys.openRouter || keysToSave.openRouter !== savedKeys.openRouter)) {
        try {
          const response = await fetch('http://localhost:24125/api/agents/config', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              api_key: keysToSave.openRouter
            })
          });
          
          if (!response.ok) {
            throw new Error(`Failed to configure agent: ${response.statusText}`);
          }
        } catch (error) {
          console.error('Error configuring agent:', error);
          setSaveStatus({
            type: 'warning',
            message: 'API keys saved locally, but failed to configure backend agent.'
          });
          setIsLoading(false);
          return;
        }
      }
      
      setSavedKeys(keysToSave);
      
      // Show masked versions in the form
      const maskedKeys = {};
      Object.keys(keysToSave).forEach(provider => {
        if (keysToSave[provider]) {
          maskedKeys[provider] = '••••••••' + keysToSave[provider].slice(-4);
        } else {
          maskedKeys[provider] = '';
        }
      });
      setApiKeys(maskedKeys);
      
      setSaveStatus({
        type: 'success',
        message: 'API keys saved successfully!'
      });
    } catch (error) {
      console.error('Error saving API keys:', error);
      setSaveStatus({
        type: 'error',
        message: 'Failed to save API keys. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  // Clear a specific API key
  const handleClearKey = (provider) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: ''
    }));
  };
  
  return (
    <FinDocLayout>
      <Head>
        <title>API Keys | FinDoc Analyzer</title>
      </Head>
      
      <div className="api-keys-page">
        <h1 className="page-title">API Keys</h1>
        
        <div className="api-keys-description">
          <p>
            Configure your API keys to enable advanced features in FinDoc Analyzer. 
            Your keys are stored securely in your browser and are only sent to our backend when needed.
          </p>
        </div>
        
        {saveStatus.message && (
          <div className={`status-message ${saveStatus.type}`}>
            {saveStatus.message}
          </div>
        )}
        
        <div className="api-keys-form">
          <div className="api-key-section">
            <h2>AI Services</h2>
            
            <div className="api-key-item">
              <div className="key-header">
                <label htmlFor="openRouter">OpenRouter API Key</label>
                <div className="provider-badge ai">AI</div>
              </div>
              <div className="key-description">
                Required for advanced AI agent capabilities. Get your key at <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer">openrouter.ai</a>
              </div>
              <div className="input-group">
                <input
                  type="text"
                  id="openRouter"
                  value={apiKeys.openRouter}
                  onChange={(e) => handleInputChange('openRouter', e.target.value)}
                  placeholder="sk-or-..."
                />
                {apiKeys.openRouter && (
                  <button 
                    className="clear-button"
                    onClick={() => handleClearKey('openRouter')}
                    title="Clear"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
          </div>
          
          <div className="api-key-section">
            <h2>Storage Services</h2>
            
            <div className="api-key-item">
              <div className="key-header">
                <label htmlFor="supabase">Supabase API Key</label>
                <div className="provider-badge storage">DB</div>
              </div>
              <div className="key-description">
                For database storage and user authentication. Get your key at <a href="https://supabase.com" target="_blank" rel="noopener noreferrer">supabase.com</a>
              </div>
              <div className="input-group">
                <input
                  type="text"
                  id="supabase"
                  value={apiKeys.supabase}
                  onChange={(e) => handleInputChange('supabase', e.target.value)}
                  placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
                />
                {apiKeys.supabase && (
                  <button 
                    className="clear-button"
                    onClick={() => handleClearKey('supabase')}
                    title="Clear"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            
            <div className="api-key-item">
              <div className="key-header">
                <label htmlFor="aws">AWS Access Key</label>
                <div className="provider-badge storage">S3</div>
              </div>
              <div className="key-description">
                For S3 document storage. Get your key from AWS IAM console.
              </div>
              <div className="input-group">
                <input
                  type="text"
                  id="aws"
                  value={apiKeys.aws}
                  onChange={(e) => handleInputChange('aws', e.target.value)}
                  placeholder="AKIA..."
                />
                {apiKeys.aws && (
                  <button 
                    className="clear-button"
                    onClick={() => handleClearKey('aws')}
                    title="Clear"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
            
            <div className="api-key-item">
              <div className="key-header">
                <label htmlFor="azure">Azure Storage Key</label>
                <div className="provider-badge storage">Azure</div>
              </div>
              <div className="key-description">
                For Azure Blob Storage. Get your key from Azure Portal.
              </div>
              <div className="input-group">
                <input
                  type="text"
                  id="azure"
                  value={apiKeys.azure}
                  onChange={(e) => handleInputChange('azure', e.target.value)}
                  placeholder="DefaultEndpointsProtocol=https;AccountName=..."
                />
                {apiKeys.azure && (
                  <button 
                    className="clear-button"
                    onClick={() => handleClearKey('azure')}
                    title="Clear"
                  >
                    ×
                  </button>
                )}
              </div>
            </div>
          </div>
          
          <div className="form-actions">
            <button 
              className="save-button"
              onClick={handleSaveKeys}
              disabled={isLoading}
            >
              {isLoading ? 'Saving...' : 'Save API Keys'}
            </button>
          </div>
        </div>
        
        <div className="security-note">
          <h3>Security Note</h3>
          <p>
            Your API keys are stored securely in your browser's local storage and are only sent to our backend when needed.
            We never store your API keys on our servers. For maximum security, we recommend using restricted API keys with
            only the necessary permissions.
          </p>
        </div>
      </div>
      
      <style jsx>{`
        .api-keys-page {
          max-width: 800px;
          margin: 0 auto;
        }
        
        .page-title {
          margin: 0 0 20px 0;
          font-size: 1.8rem;
          color: #2d3748;
        }
        
        .api-keys-description {
          margin-bottom: 24px;
          color: #4a5568;
          font-size: 0.95rem;
          line-height: 1.5;
        }
        
        .status-message {
          padding: 12px 16px;
          border-radius: 6px;
          margin-bottom: 24px;
          font-size: 0.95rem;
        }
        
        .status-message.success {
          background-color: #f0fff4;
          border: 1px solid #c6f6d5;
          color: #2f855a;
        }
        
        .status-message.error {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          color: #c53030;
        }
        
        .status-message.warning {
          background-color: #fffaf0;
          border: 1px solid #feebc8;
          color: #c05621;
        }
        
        .api-keys-form {
          background-color: white;
          border-radius: 8px;
          padding: 24px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
          margin-bottom: 24px;
        }
        
        .api-key-section {
          margin-bottom: 32px;
        }
        
        .api-key-section h2 {
          font-size: 1.2rem;
          color: #2d3748;
          margin: 0 0 16px 0;
          padding-bottom: 8px;
          border-bottom: 1px solid #e2e8f0;
        }
        
        .api-key-item {
          margin-bottom: 24px;
        }
        
        .key-header {
          display: flex;
          align-items: center;
          margin-bottom: 8px;
        }
        
        .key-header label {
          font-weight: 500;
          color: #4a5568;
          font-size: 1rem;
          margin-right: 8px;
        }
        
        .provider-badge {
          font-size: 0.7rem;
          padding: 2px 6px;
          border-radius: 4px;
          font-weight: 600;
        }
        
        .provider-badge.ai {
          background-color: #ebf8ff;
          color: #3182ce;
        }
        
        .provider-badge.storage {
          background-color: #f0fff4;
          color: #38a169;
        }
        
        .key-description {
          font-size: 0.85rem;
          color: #718096;
          margin-bottom: 8px;
          line-height: 1.5;
        }
        
        .key-description a {
          color: #4299e1;
          text-decoration: none;
        }
        
        .key-description a:hover {
          text-decoration: underline;
        }
        
        .input-group {
          position: relative;
          display: flex;
        }
        
        .input-group input {
          flex: 1;
          padding: 10px 12px;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          font-size: 0.95rem;
          font-family: monospace;
          transition: border-color 0.2s;
        }
        
        .input-group input:focus {
          outline: none;
          border-color: #4299e1;
          box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }
        
        .clear-button {
          position: absolute;
          right: 10px;
          top: 50%;
          transform: translateY(-50%);
          background: none;
          border: none;
          color: #a0aec0;
          font-size: 1.2rem;
          cursor: pointer;
          padding: 0;
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
        }
        
        .clear-button:hover {
          color: #718096;
          background-color: #f7fafc;
        }
        
        .form-actions {
          display: flex;
          justify-content: flex-end;
          margin-top: 24px;
        }
        
        .save-button {
          background-color: #4299e1;
          color: white;
          border: none;
          border-radius: 6px;
          padding: 10px 20px;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .save-button:hover {
          background-color: #3182ce;
        }
        
        .save-button:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
        }
        
        .security-note {
          background-color: #f7fafc;
          border-radius: 8px;
          padding: 16px 20px;
          border-left: 4px solid #4299e1;
        }
        
        .security-note h3 {
          margin: 0 0 8px 0;
          font-size: 1rem;
          color: #2d3748;
        }
        
        .security-note p {
          margin: 0;
          font-size: 0.85rem;
          color: #4a5568;
          line-height: 1.5;
        }
      `}</style>
    </FinDocLayout>
  );
}
