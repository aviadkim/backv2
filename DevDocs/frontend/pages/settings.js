import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';
import SimpleFinDocUI from '../components/SimpleFinDocUI';
import UserPreferences from '../components/UserPreferences';
import axios from 'axios';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    general: {
      theme: 'light',
      language: 'en',
      dateFormat: 'MM/DD/YYYY',
      timezone: 'UTC'
    },
    notifications: {
      emailNotifications: true,
      documentProcessed: true,
      newAnalysisAvailable: true,
      securityAlerts: true
    },
    privacy: {
      shareAnalytics: true,
      storeDocuments: true,
      documentRetention: '90days'
    },
    display: {
      compactView: false,
      showTags: true,
      defaultView: 'grid'
    }
  });

  const [activeTab, setActiveTab] = useState('general');
  const [isLoading, setIsLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  const [apiKey, setApiKey] = useState('');
  const [apiKeyStatus, setApiKeyStatus] = useState(null);
  const [isTestingApiKey, setIsTestingApiKey] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [isSavingApiKey, setIsSavingApiKey] = useState(false);

  // Load saved settings on component mount
  useEffect(() => {
    const loadSavedSettings = () => {
      try {
        const savedSettingsJson = localStorage.getItem('findoc_settings');
        if (savedSettingsJson) {
          const savedSettings = JSON.parse(savedSettingsJson);
          setSettings(prevSettings => ({
            ...prevSettings,
            ...savedSettings
          }));
        }
      } catch (error) {
        console.error('Error loading saved settings:', error);
      }
    };

    loadSavedSettings();
    checkApiKey();
  }, []);

  // Check API key status
  const checkApiKey = async () => {
    try {
      const response = await axios.get('/api/config/api-key');
      setApiKeyStatus(response.data.isConfigured ? 'configured' : 'not-configured');
    } catch (error) {
      console.error('Error checking API key:', error);
      setApiKeyStatus('error');
    }
  };

  // Handle API key change
  const handleApiKeyChange = (e) => {
    setApiKey(e.target.value);
    setTestResult(null);
  };

  // Save API key
  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) {
      setTestResult({
        success: false,
        message: 'Please enter an API key'
      });
      return;
    }

    setIsSavingApiKey(true);
    setTestResult(null);

    try {
      await axios.post('/api/config/api-key', { apiKey });
      setApiKeyStatus('configured');
      setTestResult({
        success: true,
        message: 'API key saved successfully'
      });
    } catch (error) {
      console.error('Error saving API key:', error);
      setTestResult({
        success: false,
        message: error.response?.data?.detail || error.message || 'Error saving API key'
      });
    } finally {
      setIsSavingApiKey(false);
    }
  };

  // Test API key
  const handleTestApiKey = async () => {
    if (!apiKey.trim() && apiKeyStatus !== 'configured') {
      setTestResult({
        success: false,
        message: 'Please enter an API key first'
      });
      return;
    }

    setIsTestingApiKey(true);
    setTestResult(null);

    try {
      const response = await axios.post('/api/config/api-key/test', {
        apiKey: apiKey.trim() || undefined
      });

      setTestResult(response.data);
    } catch (error) {
      console.error('Error testing API key:', error);
      setTestResult({
        success: false,
        message: error.response?.data?.detail || error.message || 'Error testing API key'
      });
    } finally {
      setIsTestingApiKey(false);
    }
  };

  // Handle input change
  const handleInputChange = (section, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [setting]: value
      }
    }));
  };

  // Handle save settings
  const handleSaveSettings = () => {
    setIsLoading(true);
    setSaveStatus({ type: '', message: '' });

    try {
      // Save to localStorage
      localStorage.setItem('findoc_settings', JSON.stringify(settings));

      setSaveStatus({
        type: 'success',
        message: 'Settings saved successfully!'
      });
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveStatus({
        type: 'error',
        message: 'Failed to save settings. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Reset settings to defaults
  const handleResetSettings = () => {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
      setSettings({
        general: {
          theme: 'light',
          language: 'en',
          dateFormat: 'MM/DD/YYYY',
          timezone: 'UTC'
        },
        notifications: {
          emailNotifications: true,
          documentProcessed: true,
          newAnalysisAvailable: true,
          securityAlerts: true
        },
        privacy: {
          shareAnalytics: true,
          storeDocuments: true,
          documentRetention: '90days'
        },
        display: {
          compactView: false,
          showTags: true,
          defaultView: 'grid'
        }
      });

      setSaveStatus({
        type: 'warning',
        message: 'Settings reset to defaults. Click Save to apply changes.'
      });
    }
  };

  return (
    <FinDocLayout>
      <Head>
        <title>Settings | FinDoc Analyzer</title>
      </Head>

      <div className="settings-page">
        <h1 className="page-title">Settings</h1>

        {saveStatus.message && (
          <div className={`status-message ${saveStatus.type}`}>
            {saveStatus.message}
          </div>
        )}

        <div className="settings-container">
          <div className="settings-sidebar">
            <ul className="settings-tabs">
              <li
                className={activeTab === 'general' ? 'active' : ''}
                onClick={() => setActiveTab('general')}
              >
                <span className="tab-icon">⚙️</span>
                <span>General</span>
              </li>
              <li
                className={activeTab === 'notifications' ? 'active' : ''}
                onClick={() => setActiveTab('notifications')}
              >
                <span className="tab-icon">🔔</span>
                <span>Notifications</span>
              </li>
              <li
                className={activeTab === 'privacy' ? 'active' : ''}
                onClick={() => setActiveTab('privacy')}
              >
                <span className="tab-icon">🔒</span>
                <span>Privacy & Security</span>
              </li>
              <li
                className={activeTab === 'display' ? 'active' : ''}
                onClick={() => setActiveTab('display')}
              >
                <span className="tab-icon">📱</span>
                <span>Display</span>
              </li>
              <li
                className={activeTab === 'api-key' ? 'active' : ''}
                onClick={() => setActiveTab('api-key')}
              >
                <span className="tab-icon">🔑</span>
                <span>API Key</span>
              </li>
              <li
                className={activeTab === 'advanced' ? 'active' : ''}
                onClick={() => setActiveTab('advanced')}
              >
                <span className="tab-icon">🛠️</span>
                <span>Advanced</span>
              </li>
            </ul>
          </div>

          <div className="settings-content">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="settings-section">
                <h2>General Settings</h2>

                <div className="setting-group">
                  <label>Theme</label>
                  <select
                    value={settings.general.theme}
                    onChange={(e) => handleInputChange('general', 'theme', e.target.value)}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="system">System Default</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Language</label>
                  <select
                    value={settings.general.language}
                    onChange={(e) => handleInputChange('general', 'language', e.target.value)}
                  >
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="zh">Chinese</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Date Format</label>
                  <select
                    value={settings.general.dateFormat}
                    onChange={(e) => handleInputChange('general', 'dateFormat', e.target.value)}
                  >
                    <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                    <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                    <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                  </select>
                </div>

                <div className="setting-group">
                  <label>Timezone</label>
                  <select
                    value={settings.general.timezone}
                    onChange={(e) => handleInputChange('general', 'timezone', e.target.value)}
                  >
                    <option value="UTC">UTC</option>
                    <option value="EST">Eastern Time (EST)</option>
                    <option value="CST">Central Time (CST)</option>
                    <option value="MST">Mountain Time (MST)</option>
                    <option value="PST">Pacific Time (PST)</option>
                    <option value="GMT">Greenwich Mean Time (GMT)</option>
                    <option value="CET">Central European Time (CET)</option>
                  </select>
                </div>
              </div>
            )}

            {/* Notification Settings */}
            {activeTab === 'notifications' && (
              <div className="settings-section">
                <h2>Notification Settings</h2>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.notifications.emailNotifications}
                      onChange={(e) => handleInputChange('notifications', 'emailNotifications', e.target.checked)}
                    />
                    <span>Email Notifications</span>
                  </label>
                  <div className="setting-description">
                    Receive email notifications for important events
                  </div>
                </div>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.notifications.documentProcessed}
                      onChange={(e) => handleInputChange('notifications', 'documentProcessed', e.target.checked)}
                    />
                    <span>Document Processing</span>
                  </label>
                  <div className="setting-description">
                    Notify when document processing is complete
                  </div>
                </div>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.notifications.newAnalysisAvailable}
                      onChange={(e) => handleInputChange('notifications', 'newAnalysisAvailable', e.target.checked)}
                    />
                    <span>New Analysis Available</span>
                  </label>
                  <div className="setting-description">
                    Notify when new analysis results are available
                  </div>
                </div>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.notifications.securityAlerts}
                      onChange={(e) => handleInputChange('notifications', 'securityAlerts', e.target.checked)}
                    />
                    <span>Security Alerts</span>
                  </label>
                  <div className="setting-description">
                    Receive notifications about security-related events
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Settings */}
            {activeTab === 'privacy' && (
              <div className="settings-section">
                <h2>Privacy & Security Settings</h2>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.privacy.shareAnalytics}
                      onChange={(e) => handleInputChange('privacy', 'shareAnalytics', e.target.checked)}
                    />
                    <span>Share Usage Analytics</span>
                  </label>
                  <div className="setting-description">
                    Help improve FinDoc by sharing anonymous usage data
                  </div>
                </div>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.privacy.storeDocuments}
                      onChange={(e) => handleInputChange('privacy', 'storeDocuments', e.target.checked)}
                    />
                    <span>Store Documents</span>
                  </label>
                  <div className="setting-description">
                    Store uploaded documents for future reference
                  </div>
                </div>

                <div className="setting-group">
                  <label>Document Retention Period</label>
                  <select
                    value={settings.privacy.documentRetention}
                    onChange={(e) => handleInputChange('privacy', 'documentRetention', e.target.value)}
                  >
                    <option value="30days">30 Days</option>
                    <option value="90days">90 Days</option>
                    <option value="1year">1 Year</option>
                    <option value="forever">Forever</option>
                  </select>
                  <div className="setting-description">
                    How long to keep documents after processing
                  </div>
                </div>
              </div>
            )}

            {/* Display Settings */}
            {activeTab === 'display' && (
              <div className="settings-section">
                <h2>Display Settings</h2>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.display.compactView}
                      onChange={(e) => handleInputChange('display', 'compactView', e.target.checked)}
                    />
                    <span>Compact View</span>
                  </label>
                  <div className="setting-description">
                    Show more items per page with reduced spacing
                  </div>
                </div>

                <div className="setting-group checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.display.showTags}
                      onChange={(e) => handleInputChange('display', 'showTags', e.target.checked)}
                    />
                    <span>Show Tags</span>
                  </label>
                  <div className="setting-description">
                    Display document tags in list views
                  </div>
                </div>

                <div className="setting-group">
                  <label>Default View</label>
                  <select
                    value={settings.display.defaultView}
                    onChange={(e) => handleInputChange('display', 'defaultView', e.target.value)}
                  >
                    <option value="grid">Grid</option>
                    <option value="list">List</option>
                    <option value="compact">Compact</option>
                  </select>
                  <div className="setting-description">
                    Default view mode for document lists
                  </div>
                </div>
              </div>
            )}

            {/* API Key Settings */}
            {activeTab === 'api-key' && (
              <div className="settings-section">
                <h2>API Key Configuration</h2>

                <div className="api-key-status">
                  <div className="status-label">Status:</div>
                  <div className={`status-value ${apiKeyStatus}`}>
                    {apiKeyStatus === 'configured' && 'Configured'}
                    {apiKeyStatus === 'not-configured' && 'Not Configured'}
                    {apiKeyStatus === 'error' && 'Error Checking Status'}
                  </div>
                </div>

                <div className="setting-group">
                  <label>OpenRouter API Key</label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={handleApiKeyChange}
                    placeholder="Enter your OpenRouter API key"
                    className="api-key-input"
                  />
                  <div className="setting-description">
                    The OpenRouter API key is used for AI-enhanced features like document analysis and OCR.
                  </div>
                </div>

                <div className="api-key-actions">
                  <button
                    className="secondary-button"
                    onClick={handleTestApiKey}
                    disabled={isTestingApiKey || isSavingApiKey}
                  >
                    {isTestingApiKey ? 'Testing...' : 'Test API Key'}
                  </button>
                  <button
                    className="save-button"
                    onClick={handleSaveApiKey}
                    disabled={!apiKey.trim() || isTestingApiKey || isSavingApiKey}
                  >
                    {isSavingApiKey ? 'Saving...' : 'Save API Key'}
                  </button>
                </div>

                {testResult && (
                  <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
                    {testResult.message}
                  </div>
                )}

                <div className="api-key-info">
                  <h3>About the OpenRouter API Key</h3>
                  <p>
                    The OpenRouter API key is used to access advanced AI features in the application,
                    including document analysis, OCR enhancement, and financial insights.
                  </p>
                  <p>
                    You can get an API key by signing up at{' '}
                    <a href="https://openrouter.ai" target="_blank" rel="noopener noreferrer">
                      openrouter.ai
                    </a>
                  </p>
                  <p>
                    <strong>Note:</strong> Your API key is stored securely and is only used for
                    making requests to the OpenRouter API.
                  </p>
                </div>
              </div>
            )}

            {/* Advanced Settings */}
            {activeTab === 'advanced' && (
              <div className="settings-section">
                <h2>Advanced Settings</h2>

                <div className="setting-group">
                  <button
                    className="danger-button"
                    onClick={handleResetSettings}
                  >
                    Reset All Settings
                  </button>
                  <div className="setting-description">
                    Reset all settings to their default values
                  </div>
                </div>

                <div className="setting-group">
                  <button
                    className="danger-button"
                    onClick={() => {
                      if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
                        localStorage.clear();
                        alert('All data has been cleared. The page will now reload.');
                        window.location.reload();
                      }
                    }}
                  >
                    Clear All Data
                  </button>
                  <div className="setting-description">
                    Clear all stored data including settings, API keys, and cached documents
                  </div>
                </div>

                <div className="setting-group">
                  <h3>About FinDoc Analyzer</h3>
                  <div className="about-info">
                    <p><strong>Version:</strong> 1.0.0</p>
                    <p><strong>Build:</strong> 2025.04.09</p>
                    <p><strong>License:</strong> Commercial</p>
                  </div>
                </div>
              </div>
            )}

            <div className="settings-actions">
              <button
                className="save-button"
                onClick={handleSaveSettings}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Settings'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .settings-page {
          max-width: 1000px;
          margin: 0 auto;
        }

        .page-title {
          margin: 0 0 20px 0;
          font-size: 1.8rem;
          color: #2d3748;
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

        .settings-container {
          display: flex;
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
          overflow: hidden;
        }

        .settings-sidebar {
          width: 220px;
          background-color: #f8fafc;
          border-right: 1px solid #e2e8f0;
        }

        .settings-tabs {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .settings-tabs li {
          padding: 12px 16px;
          cursor: pointer;
          display: flex;
          align-items: center;
          color: #4a5568;
          border-left: 3px solid transparent;
          transition: all 0.2s;
        }

        .settings-tabs li:hover {
          background-color: #edf2f7;
          color: #2d3748;
        }

        .settings-tabs li.active {
          background-color: #ebf8ff;
          color: #3182ce;
          border-left-color: #3182ce;
        }

        .tab-icon {
          margin-right: 10px;
          font-size: 1.1rem;
        }

        .settings-content {
          flex: 1;
          padding: 24px;
        }

        .settings-section h2 {
          margin: 0 0 24px 0;
          font-size: 1.2rem;
          color: #2d3748;
          padding-bottom: 12px;
          border-bottom: 1px solid #e2e8f0;
        }

        .settings-section h3 {
          margin: 0 0 12px 0;
          font-size: 1.1rem;
          color: #2d3748;
        }

        .setting-group {
          margin-bottom: 20px;
        }

        .setting-group label {
          display: block;
          font-weight: 500;
          color: #4a5568;
          margin-bottom: 8px;
        }

        .setting-group.checkbox label {
          display: flex;
          align-items: center;
          font-weight: normal;
        }

        .setting-group.checkbox input {
          margin-right: 10px;
        }

        .setting-description {
          font-size: 0.85rem;
          color: #718096;
          margin-top: 4px;
        }

        .setting-group select,
        .setting-group input[type="text"],
        .setting-group input[type="number"] {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: border-color 0.2s;
        }

        .setting-group select:focus,
        .setting-group input[type="text"]:focus,
        .setting-group input[type="number"]:focus {
          outline: none;
          border-color: #4299e1;
          box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }

        .settings-actions {
          margin-top: 32px;
          display: flex;
          justify-content: flex-end;
          padding-top: 20px;
          border-top: 1px solid #e2e8f0;
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

        .danger-button {
          background-color: #fff5f5;
          color: #e53e3e;
          border: 1px solid #fed7d7;
          border-radius: 6px;
          padding: 8px 16px;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .danger-button:hover {
          background-color: #fed7d7;
        }

        .about-info {
          background-color: #f8fafc;
          border-radius: 6px;
          padding: 12px 16px;
        }

        .about-info p {
          margin: 8px 0;
          font-size: 0.9rem;
          color: #4a5568;
        }

        .api-key-status {
          display: flex;
          align-items: center;
          margin-bottom: 20px;
          padding: 10px 15px;
          background-color: #f8fafc;
          border-radius: 6px;
        }

        .status-label {
          font-weight: 500;
          margin-right: 10px;
          color: #4a5568;
        }

        .status-value {
          font-weight: 500;
        }

        .status-value.configured {
          color: #2f855a;
        }

        .status-value.not-configured {
          color: #c05621;
        }

        .status-value.error {
          color: #c53030;
        }

        .api-key-input {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          font-size: 0.95rem;
          transition: border-color 0.2s;
        }

        .api-key-input:focus {
          outline: none;
          border-color: #4299e1;
          box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.15);
        }

        .api-key-actions {
          display: flex;
          gap: 10px;
          margin-top: 15px;
        }

        .secondary-button {
          background-color: #edf2f7;
          color: #4a5568;
          border: 1px solid #e2e8f0;
          border-radius: 6px;
          padding: 8px 16px;
          font-size: 0.95rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .secondary-button:hover {
          background-color: #e2e8f0;
        }

        .secondary-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .test-result {
          margin-top: 15px;
          padding: 10px 15px;
          border-radius: 6px;
          font-size: 0.95rem;
        }

        .test-result.success {
          background-color: #f0fff4;
          border: 1px solid #c6f6d5;
          color: #2f855a;
        }

        .test-result.error {
          background-color: #fff5f5;
          border: 1px solid #fed7d7;
          color: #c53030;
        }

        .api-key-info {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #e2e8f0;
        }

        .api-key-info h3 {
          font-size: 1.1rem;
          margin: 0 0 15px 0;
          color: #2d3748;
        }

        .api-key-info p {
          margin: 0 0 10px 0;
          line-height: 1.5;
          color: #4a5568;
        }

        .api-key-info a {
          color: #4299e1;
          text-decoration: none;
        }

        .api-key-info a:hover {
          text-decoration: underline;
        }

        @media (max-width: 768px) {
          .settings-container {
            flex-direction: column;
          }

          .settings-sidebar {
            width: 100%;
            border-right: none;
            border-bottom: 1px solid #e2e8f0;
          }

          .settings-tabs {
            display: flex;
            overflow-x: auto;
          }

          .settings-tabs li {
            padding: 12px;
            border-left: none;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
          }

          .settings-tabs li.active {
            border-left-color: transparent;
            border-bottom-color: #3182ce;
          }
        }
      `}</style>
    </FinDocLayout>
  );
}
