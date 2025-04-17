import React, { useState, useEffect } from 'react';
import FinDocLayout from '../components/FinDocLayout';
import axios from 'axios';

const AgentStatus = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkAgents = async () => {
      try {
        setLoading(true);
        const response = await axios.get('/api/check-agents');
        setStatus(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error checking agents:', err);
        setError(err.message || 'Error checking agents');
        setLoading(false);
      }
    };

    checkAgents();
  }, []);

  return (
    <FinDocLayout>
      <div className="agent-status-container">
        <h1 className="page-title">Agent Status</h1>
        
        {loading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Checking agent status...</p>
          </div>
        )}
        
        {error && (
          <div className="error-container">
            <h2>Error</h2>
            <p>{error}</p>
          </div>
        )}
        
        {status && (
          <div className="status-container">
            <div className="api-key-status">
              <h2>OpenRouter API Key Status</h2>
              <div className={`status-indicator ${status.openRouterApiKeyAvailable ? 'success' : 'error'}`}>
                {status.openRouterApiKeyAvailable ? 'Available' : 'Not Available'}
              </div>
            </div>
            
            <div className="agents-status">
              <h2>Agent Status</h2>
              <table className="agents-table">
                <thead>
                  <tr>
                    <th>Agent</th>
                    <th>Connected</th>
                    <th>API Key Available</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(status.agents).map(([agent, agentStatus]) => (
                    <tr key={agent}>
                      <td>{agent}</td>
                      <td className={agentStatus.connected ? 'success' : 'error'}>
                        {agentStatus.connected ? 'Yes' : 'No'}
                      </td>
                      <td className={agentStatus.apiKeyAvailable ? 'success' : 'error'}>
                        {agentStatus.apiKeyAvailable ? 'Yes' : 'No'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
      
      <style jsx>{`
        .agent-status-container {
          padding: 30px;
        }
        
        .page-title {
          font-size: 24px;
          font-weight: 600;
          margin-bottom: 20px;
          color: #2c3e50;
        }
        
        .loading-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px;
        }
        
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid rgba(0, 0, 0, 0.1);
          border-radius: 50%;
          border-top-color: #3498db;
          animation: spin 1s ease-in-out infinite;
          margin-bottom: 20px;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        .error-container {
          background-color: #fee2e2;
          border: 1px solid #ef4444;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }
        
        .error-container h2 {
          color: #b91c1c;
          font-size: 18px;
          margin-bottom: 10px;
        }
        
        .status-container {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }
        
        .api-key-status, .agents-status {
          background-color: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 25px;
        }
        
        .api-key-status h2, .agents-status h2 {
          font-size: 18px;
          font-weight: 500;
          margin-bottom: 15px;
          color: #2c3e50;
        }
        
        .status-indicator {
          display: inline-block;
          padding: 8px 16px;
          border-radius: 4px;
          font-weight: 500;
        }
        
        .success {
          background-color: #dcfce7;
          color: #166534;
        }
        
        .error {
          background-color: #fee2e2;
          color: #b91c1c;
        }
        
        .agents-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .agents-table th, .agents-table td {
          padding: 12px 15px;
          text-align: left;
          border-bottom: 1px solid #e5e7eb;
        }
        
        .agents-table th {
          background-color: #f8fafc;
          font-weight: 500;
          color: #475569;
        }
        
        .agents-table tr:last-child td {
          border-bottom: none;
        }
      `}</style>
    </FinDocLayout>
  );
};

export default AgentStatus;
