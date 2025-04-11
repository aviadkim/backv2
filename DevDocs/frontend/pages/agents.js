import { useState, useEffect } from 'react';
import Head from 'next/head';
import FinDocLayout from '../components/FinDocLayout';
import AgentChat from '../components/agents/AgentChat';

export default function AgentsPage() {
  const [agents, setAgents] = useState([
    {
      id: 1,
      name: 'Document Analyzer',
      description: 'Analyzes documents for financial data and extracts key information',
      status: 'active',
      lastRun: '2 hours ago',
      processedDocs: 152
    },
    {
      id: 2,
      name: 'ISIN Extractor',
      description: 'Identifies and extracts ISIN numbers from documents',
      status: 'active',
      lastRun: '3 hours ago',
      processedDocs: 126
    },
    {
      id: 3,
      name: 'Portfolio Analyzer',
      description: 'Analyzes investment portfolios for performance and risk assessment',
      status: 'idle',
      lastRun: '1 day ago',
      processedDocs: 58
    },
    {
      id: 4,
      name: 'Regulatory Compliance',
      description: 'Checks documents for regulatory compliance issues',
      status: 'configuring',
      lastRun: 'Never',
      processedDocs: 0
    },
  ]);

  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentDescription, setNewAgentDescription] = useState('');
  const [showNewAgentForm, setShowNewAgentForm] = useState(false);
  const [activeChat, setActiveChat] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [showApiKeyForm, setShowApiKeyForm] = useState(false);

  const handleCreateAgent = () => {
    if (newAgentName && newAgentDescription) {
      const newAgent = {
        id: agents.length + 1,
        name: newAgentName,
        description: newAgentDescription,
        status: 'configuring',
        lastRun: 'Never',
        processedDocs: 0
      };

      setAgents([...agents, newAgent]);
      setNewAgentName('');
      setNewAgentDescription('');
      setShowNewAgentForm(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#38a169';
      case 'idle': return '#718096';
      case 'configuring': return '#3182ce';
      case 'error': return '#e53e3e';
      default: return '#718096';
    }
  };

  return (
    <FinDocLayout>
      <Head>
        <title>AI Agents | FinDoc Analyzer</title>
      </Head>

      <div className="agents-page">
        <div className="page-header">
          <h1>AI Agents</h1>
          <button
            className="create-agent-btn"
            onClick={() => setShowNewAgentForm(!showNewAgentForm)}
          >
            {showNewAgentForm ? 'Cancel' : 'Create New Agent'}
          </button>
        </div>

        {showNewAgentForm && (
          <div className="new-agent-form">
            <h2>Create New Agent</h2>
            <div className="form-group">
              <label>Agent Name</label>
              <input
                type="text"
                value={newAgentName}
                onChange={(e) => setNewAgentName(e.target.value)}
                placeholder="Enter agent name"
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={newAgentDescription}
                onChange={(e) => setNewAgentDescription(e.target.value)}
                placeholder="Describe what this agent does"
              />
            </div>
            <div className="form-actions">
              <button
                className="cancel-btn"
                onClick={() => setShowNewAgentForm(false)}
              >
                Cancel
              </button>
              <button
                className="create-btn"
                onClick={handleCreateAgent}
                disabled={!newAgentName || !newAgentDescription}
              >
                Create Agent
              </button>
            </div>
          </div>
        )}

        <div className="agents-grid">
          {agents.map(agent => (
            <div key={agent.id} className="agent-card">
              <div className="agent-header">
                <h2>{agent.name}</h2>
                <div
                  className="status-indicator"
                  style={{backgroundColor: getStatusColor(agent.status)}}
                >
                  {agent.status}
                </div>
              </div>
              <p className="agent-description">{agent.description}</p>
              <div className="agent-stats">
                <div className="stat">
                  <span className="stat-label">Last Run:</span>
                  <span className="stat-value">{agent.lastRun}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Processed:</span>
                  <span className="stat-value">{agent.processedDocs} documents</span>
                </div>
              </div>
              <div className="agent-actions">
                <button className="action-btn" onClick={() => setShowApiKeyForm(true)}>Configure</button>
                <button className="action-btn" onClick={() => setActiveChat(agent)}>Chat</button>
                <button className="action-btn">View Logs</button>
              </div>
            </div>
          ))}
        </div>

        {activeChat && (
          <AgentChat agent={activeChat} onClose={() => setActiveChat(null)} />
        )}

        {showApiKeyForm && (
          <div className="api-key-modal">
            <div className="api-key-form">
              <h2>Configure API Key</h2>
              <p>Enter your OpenRouter API key to enable advanced AI capabilities.</p>

              <div className="form-group">
                <label>API Key</label>
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your OpenRouter API key"
                />
              </div>

              <div className="form-actions">
                <button
                  className="cancel-btn"
                  onClick={() => setShowApiKeyForm(false)}
                >
                  Cancel
                </button>
                <button
                  className="save-btn"
                  onClick={() => {
                    // Save API key logic would go here
                    alert('API key saved successfully!');
                    setShowApiKeyForm(false);
                  }}
                  disabled={!apiKey}
                >
                  Save API Key
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .api-key-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .api-key-form {
          background-color: white;
          border-radius: 8px;
          padding: 24px;
          width: 90%;
          max-width: 500px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .api-key-form h2 {
          margin-top: 0;
          margin-bottom: 8px;
          font-size: 1.2rem;
          color: #2d3748;
        }

        .api-key-form p {
          margin-bottom: 20px;
          color: #718096;
          font-size: 0.9rem;
        }

        .save-btn {
          background-color: #38a169;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 8px 16px;
          cursor: pointer;
        }

        .save-btn:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
        }
        .agents-page {
          max-width: 1200px;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        h1 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #2d3748;
          margin: 0;
        }

        .create-agent-btn {
          background-color: #3498db;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 8px 16px;
          font-size: 0.9rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .create-agent-btn:hover {
          background-color: #2980b9;
        }

        .new-agent-form {
          background-color: white;
          border-radius: 8px;
          padding: 24px;
          margin-bottom: 24px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        .new-agent-form h2 {
          font-size: 1.2rem;
          margin-top: 0;
          margin-bottom: 16px;
          color: #2d3748;
        }

        .form-group {
          margin-bottom: 16px;
        }

        .form-group label {
          display: block;
          font-weight: 500;
          margin-bottom: 8px;
          color: #4a5568;
        }

        .form-group input, .form-group textarea {
          width: 100%;
          padding: 10px;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .form-group textarea {
          height: 100px;
          resize: vertical;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 12px;
        }

        .cancel-btn {
          background-color: transparent;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          padding: 8px 16px;
          cursor: pointer;
        }

        .create-btn {
          background-color: #3498db;
          color: white;
          border: none;
          border-radius: 4px;
          padding: 8px 16px;
          cursor: pointer;
        }

        .create-btn:disabled {
          background-color: #a0aec0;
          cursor: not-allowed;
        }

        .agents-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .agent-card {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .agent-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 12px;
        }

        .agent-header h2 {
          font-size: 1.1rem;
          margin: 0;
          color: #2d3748;
        }

        .status-indicator {
          font-size: 0.75rem;
          padding: 4px 8px;
          border-radius: 12px;
          color: white;
          text-transform: capitalize;
        }

        .agent-description {
          color: #4a5568;
          font-size: 0.9rem;
          margin-bottom: 16px;
        }

        .agent-stats {
          display: flex;
          flex-direction: column;
          gap: 8px;
          margin-bottom: 16px;
          font-size: 0.85rem;
        }

        .stat {
          display: flex;
          justify-content: space-between;
        }

        .stat-label {
          color: #718096;
        }

        .stat-value {
          font-weight: 500;
        }

        .agent-actions {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          flex: 1;
          background-color: transparent;
          border: 1px solid #e2e8f0;
          border-radius: 4px;
          padding: 6px 8px;
          font-size: 0.8rem;
          cursor: pointer;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background-color: #f7fafc;
          border-color: #cbd5e0;
        }
      `}</style>
    </FinDocLayout>
  );
}
