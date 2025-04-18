import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserPreferences = () => {
  const [preferences, setPreferences] = useState({
    theme: 'light',
    fontSize: 'medium',
    language: 'en',
    notifications: true,
    autoSave: true,
    highContrast: false,
    reducedMotion: false,
    keyboardShortcuts: true
  });
  
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null);
  
  // Load preferences from localStorage on component mount
  useEffect(() => {
    const savedPreferences = localStorage.getItem('userPreferences');
    if (savedPreferences) {
      try {
        setPreferences(JSON.parse(savedPreferences));
      } catch (error) {
        console.error('Error parsing saved preferences:', error);
      }
    }
    
    // Apply theme
    document.documentElement.setAttribute('data-theme', preferences.theme);
    
    // Apply font size
    document.documentElement.style.fontSize = getFontSizeValue(preferences.fontSize);
    
    // Apply high contrast
    if (preferences.highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
    
    // Apply reduced motion
    if (preferences.reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }
  }, []);
  
  // Update theme when preference changes
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', preferences.theme);
  }, [preferences.theme]);
  
  // Update font size when preference changes
  useEffect(() => {
    document.documentElement.style.fontSize = getFontSizeValue(preferences.fontSize);
  }, [preferences.fontSize]);
  
  // Update high contrast when preference changes
  useEffect(() => {
    if (preferences.highContrast) {
      document.documentElement.classList.add('high-contrast');
    } else {
      document.documentElement.classList.remove('high-contrast');
    }
  }, [preferences.highContrast]);
  
  // Update reduced motion when preference changes
  useEffect(() => {
    if (preferences.reducedMotion) {
      document.documentElement.classList.add('reduced-motion');
    } else {
      document.documentElement.classList.remove('reduced-motion');
    }
  }, [preferences.reducedMotion]);
  
  const handlePreferenceChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setPreferences(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    setSaveStatus(null);
  };
  
  const handleSavePreferences = async () => {
    setIsSaving(true);
    setSaveStatus(null);
    
    try {
      // Save to localStorage
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      
      // In a real implementation, we would also save to the server
      // await axios.post('/api/user/preferences', preferences);
      
      setSaveStatus('success');
    } catch (error) {
      console.error('Error saving preferences:', error);
      setSaveStatus('error');
    } finally {
      setIsSaving(false);
    }
  };
  
  const handleResetPreferences = () => {
    const defaultPreferences = {
      theme: 'light',
      fontSize: 'medium',
      language: 'en',
      notifications: true,
      autoSave: true,
      highContrast: false,
      reducedMotion: false,
      keyboardShortcuts: true
    };
    
    setPreferences(defaultPreferences);
    setSaveStatus(null);
  };
  
  return (
    <div className="preferences-container">
      <h2 className="preferences-title">User Preferences</h2>
      
      <div className="preferences-section">
        <h3 className="section-title">Appearance</h3>
        
        <div className="preference-item">
          <label htmlFor="theme">Theme</label>
          <select
            id="theme"
            name="theme"
            value={preferences.theme}
            onChange={handlePreferenceChange}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System Default</option>
          </select>
        </div>
        
        <div className="preference-item">
          <label htmlFor="fontSize">Font Size</label>
          <select
            id="fontSize"
            name="fontSize"
            value={preferences.fontSize}
            onChange={handlePreferenceChange}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
            <option value="x-large">Extra Large</option>
          </select>
        </div>
        
        <div className="preference-item">
          <label htmlFor="language">Language</label>
          <select
            id="language"
            name="language"
            value={preferences.language}
            onChange={handlePreferenceChange}
          >
            <option value="en">English</option>
            <option value="he">Hebrew</option>
          </select>
        </div>
      </div>
      
      <div className="preferences-section">
        <h3 className="section-title">Behavior</h3>
        
        <div className="preference-item checkbox">
          <input
            type="checkbox"
            id="notifications"
            name="notifications"
            checked={preferences.notifications}
            onChange={handlePreferenceChange}
          />
          <label htmlFor="notifications">Enable Notifications</label>
        </div>
        
        <div className="preference-item checkbox">
          <input
            type="checkbox"
            id="autoSave"
            name="autoSave"
            checked={preferences.autoSave}
            onChange={handlePreferenceChange}
          />
          <label htmlFor="autoSave">Auto-save Documents</label>
        </div>
        
        <div className="preference-item checkbox">
          <input
            type="checkbox"
            id="keyboardShortcuts"
            name="keyboardShortcuts"
            checked={preferences.keyboardShortcuts}
            onChange={handlePreferenceChange}
          />
          <label htmlFor="keyboardShortcuts">Enable Keyboard Shortcuts</label>
        </div>
      </div>
      
      <div className="preferences-section">
        <h3 className="section-title">Accessibility</h3>
        
        <div className="preference-item checkbox">
          <input
            type="checkbox"
            id="highContrast"
            name="highContrast"
            checked={preferences.highContrast}
            onChange={handlePreferenceChange}
          />
          <label htmlFor="highContrast">High Contrast Mode</label>
        </div>
        
        <div className="preference-item checkbox">
          <input
            type="checkbox"
            id="reducedMotion"
            name="reducedMotion"
            checked={preferences.reducedMotion}
            onChange={handlePreferenceChange}
          />
          <label htmlFor="reducedMotion">Reduced Motion</label>
        </div>
      </div>
      
      <div className="preferences-actions">
        <button
          className="btn secondary"
          onClick={handleResetPreferences}
        >
          Reset to Defaults
        </button>
        <button
          className="btn primary"
          onClick={handleSavePreferences}
          disabled={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Preferences'}
        </button>
      </div>
      
      {saveStatus === 'success' && (
        <div className="save-status success">
          Preferences saved successfully
        </div>
      )}
      
      {saveStatus === 'error' && (
        <div className="save-status error">
          Error saving preferences
        </div>
      )}
      
      <style jsx>{`
        .preferences-container {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
          padding: 20px;
        }
        
        .preferences-title {
          font-size: 20px;
          font-weight: bold;
          margin: 0 0 20px;
          color: #2c3e50;
          padding-bottom: 10px;
          border-bottom: 1px solid #e9ecef;
        }
        
        .preferences-section {
          margin-bottom: 25px;
        }
        
        .section-title {
          font-size: 16px;
          font-weight: 500;
          margin: 0 0 15px;
          color: #2c3e50;
        }
        
        .preference-item {
          display: flex;
          align-items: center;
          margin-bottom: 15px;
        }
        
        .preference-item label {
          flex: 0 0 150px;
          font-weight: 500;
          color: #495057;
        }
        
        .preference-item select {
          flex: 1;
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 14px;
          color: #495057;
        }
        
        .preference-item.checkbox {
          display: flex;
          align-items: center;
        }
        
        .preference-item.checkbox input {
          margin-right: 10px;
        }
        
        .preference-item.checkbox label {
          flex: 1;
        }
        
        .preferences-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid #e9ecef;
        }
        
        .btn {
          padding: 10px 15px;
          border: none;
          border-radius: 4px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s ease;
        }
        
        .btn.primary {
          background-color: #3498db;
          color: white;
        }
        
        .btn.primary:hover {
          background-color: #2980b9;
        }
        
        .btn.secondary {
          background-color: #e9ecef;
          color: #495057;
        }
        
        .btn.secondary:hover {
          background-color: #dee2e6;
        }
        
        .btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        
        .save-status {
          margin-top: 15px;
          padding: 10px;
          border-radius: 4px;
          text-align: center;
        }
        
        .save-status.success {
          background-color: #d4edda;
          color: #155724;
        }
        
        .save-status.error {
          background-color: #f8d7da;
          color: #721c24;
        }
        
        @media (max-width: 768px) {
          .preference-item {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .preference-item label {
            margin-bottom: 5px;
          }
          
          .preference-item select {
            width: 100%;
          }
          
          .preference-item.checkbox {
            flex-direction: row;
          }
        }
      `}</style>
    </div>
  );
};

// Helper function to get font size value
function getFontSizeValue(size) {
  switch (size) {
    case 'small':
      return '14px';
    case 'medium':
      return '16px';
    case 'large':
      return '18px';
    case 'x-large':
      return '20px';
    default:
      return '16px';
  }
}

export default UserPreferences;
