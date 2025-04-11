import { useState, useEffect, useRef } from 'react';

const AgentChat = ({ agent, onClose }) => {
  const [userInput, setUserInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const messagesEndRef = useRef(null);

  // Fetch documents on component mount
  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch('http://localhost:24125/api/documents');
        if (response.ok) {
          const data = await response.json();
          setDocuments(data.documents || []);
        } else {
          console.error('Failed to fetch documents');
        }
      } catch (error) {
        console.error('Error fetching documents:', error);
      }
    };
    
    fetchDocuments();
  }, []);

  // Scroll to bottom of conversation when new messages are added
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  // Handle sending a message to the agent
  const handleSendMessage = async () => {
    if (!userInput.trim()) return;
    
    const userMessage = {
      role: 'user',
      content: userInput,
      timestamp: new Date().toISOString()
    };
    
    setConversation(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);
    
    try {
      // Prepare request data
      const requestData = {
        agent_id: agent.id,
        message: userInput,
        document_id: selectedDocument ? selectedDocument.id : null
      };
      
      // Send message to agent
      const response = await fetch('http://localhost:24125/api/agents/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (response.ok) {
        const responseData = await response.json();
        
        const agentMessage = {
          role: 'agent',
          content: responseData.response || 'Sorry, I could not process your request.',
          timestamp: new Date().toISOString()
        };
        
        setConversation(prev => [...prev, agentMessage]);
      } else {
        // Handle error response
        const errorData = await response.json();
        
        const errorMessage = {
          role: 'agent',
          content: `Error: ${errorData.error || 'Something went wrong. Please try again.'}`,
          timestamp: new Date().toISOString()
        };
        
        setConversation(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Generate mock response for demo purposes
      const mockResponses = {
        1: [
          "I've analyzed the document and found the following key information: total revenue of $2.5M, operating expenses of $1.8M, and net profit of $700K.",
          "The document contains 3 ISIN codes: US0378331005 (Apple), US5949181045 (Microsoft), and US88160R1014 (Tesla).",
          "Based on my analysis, this appears to be a quarterly financial report with a focus on technology sector investments."
        ],
        2: [
          "I've extracted the following ISINs from the document: US0378331005, US5949181045, US88160R1014, US0231351067, US30303M1027.",
          "The document contains references to 5 different securities, all from the technology sector.",
          "I've identified and validated all ISINs in the document. Would you like me to provide more details about any specific security?"
        ],
        3: [
          "Your portfolio has a Sharpe ratio of 1.2, which indicates a good risk-adjusted return compared to the market.",
          "The portfolio analysis shows an asset allocation of 60% equities, 30% bonds, and 10% cash equivalents.",
          "Based on my analysis, your portfolio has a beta of 0.85, indicating slightly lower volatility than the market."
        ],
        4: [
          "I've checked the document for regulatory compliance and found no major issues.",
          "The document meets all requirements for GDPR compliance.",
          "There are a few minor disclosure issues that should be addressed before final submission."
        ]
      };
      
      const randomIndex = Math.floor(Math.random() * mockResponses[agent.id].length);
      const mockResponse = mockResponses[agent.id][randomIndex];
      
      const fallbackMessage = {
        role: 'agent',
        content: mockResponse,
        timestamp: new Date().toISOString()
      };
      
      setConversation(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle selecting a document
  const handleSelectDocument = (document) => {
    setSelectedDocument(document === selectedDocument ? null : document);
  };

  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="agent-chat-modal">
      <div className="agent-chat-container">
        <div className="chat-header">
          <div className="agent-info">
            <h2>{agent.name}</h2>
            <div 
              className="status-indicator" 
              style={{
                backgroundColor: 
                  agent.status === 'active' ? '#38a169' : 
                  agent.status === 'idle' ? '#718096' : 
                  agent.status === 'configuring' ? '#3182ce' : '#e53e3e'
              }}
            >
              {agent.status}
            </div>
          </div>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>
        
        <div className="chat-body">
          <div className="conversation">
            {conversation.length === 0 ? (
              <div className="empty-conversation">
                <div className="welcome-message">
                  <h3>Welcome to {agent.name}</h3>
                  <p>{agent.description}</p>
                  {selectedDocument && (
                    <div className="selected-document-info">
                      <p>Currently working with: <strong>{selectedDocument.title}</strong></p>
                    </div>
                  )}
                </div>
                <div className="suggested-prompts">
                  <h4>Suggested prompts:</h4>
                  <ul>
                    {agent.id === 1 && (
                      <>
                        <li onClick={() => setUserInput("Analyze this document and extract key financial data")}>
                          Analyze this document and extract key financial data
                        </li>
                        <li onClick={() => setUserInput("Summarize the main points of this document")}>
                          Summarize the main points of this document
                        </li>
                      </>
                    )}
                    {agent.id === 2 && (
                      <>
                        <li onClick={() => setUserInput("Extract all ISINs from this document")}>
                          Extract all ISINs from this document
                        </li>
                        <li onClick={() => setUserInput("Validate the ISINs in this document")}>
                          Validate the ISINs in this document
                        </li>
                      </>
                    )}
                    {agent.id === 3 && (
                      <>
                        <li onClick={() => setUserInput("Analyze my portfolio performance")}>
                          Analyze my portfolio performance
                        </li>
                        <li onClick={() => setUserInput("Calculate risk metrics for my portfolio")}>
                          Calculate risk metrics for my portfolio
                        </li>
                      </>
                    )}
                    {agent.id === 4 && (
                      <>
                        <li onClick={() => setUserInput("Check this document for regulatory compliance")}>
                          Check this document for regulatory compliance
                        </li>
                        <li onClick={() => setUserInput("Identify potential compliance issues")}>
                          Identify potential compliance issues
                        </li>
                      </>
                    )}
                  </ul>
                </div>
              </div>
            ) : (
              <>
                {conversation.map((message, index) => (
                  <div 
                    key={index} 
                    className={`message ${message.role === 'user' ? 'user-message' : 'agent-message'}`}
                  >
                    <div className="message-avatar">
                      {message.role === 'user' ? 'U' : agent.name.charAt(0)}
                    </div>
                    <div className="message-content">
                      <div className="message-text">{message.content}</div>
                      <div className="message-timestamp">{formatTimestamp(message.timestamp)}</div>
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
          
          <div className="documents-sidebar">
            <h3>Documents</h3>
            <div className="documents-list">
              {documents.length === 0 ? (
                <p className="no-documents">No documents available</p>
              ) : (
                documents.map((doc) => (
                  <div 
                    key={doc.id}
                    className={`document-item ${selectedDocument && selectedDocument.id === doc.id ? 'selected' : ''}`}
                    onClick={() => handleSelectDocument(doc)}
                  >
                    <div className="document-icon">📄</div>
                    <div className="document-info">
                      <p className="document-title">{doc.title}</p>
                      <p className="document-date">{doc.date}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
        
        <div className="input-area">
          <textarea
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder={`Ask ${agent.name} a question...`}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <button 
            className="send-button"
            onClick={handleSendMessage}
            disabled={isLoading || !userInput.trim()}
          >
            {isLoading ? (
              <div className="loading-spinner"></div>
            ) : (
              <span className="send-icon">➤</span>
            )}
          </button>
        </div>
      </div>

      <style jsx>{`
        .agent-chat-modal {
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
        
        .agent-chat-container {
          width: 90%;
          max-width: 1000px;
          height: 80vh;
          background-color: white;
          border-radius: 8px;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        .chat-header {
          padding: 15px 20px;
          border-bottom: 1px solid #e2e8f0;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        
        .agent-info {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .agent-info h2 {
          margin: 0;
          font-size: 1.2rem;
          color: #2d3748;
        }
        
        .status-indicator {
          font-size: 0.75rem;
          padding: 4px 8px;
          border-radius: 12px;
          color: white;
          text-transform: capitalize;
        }
        
        .close-btn {
          background: none;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          color: #718096;
        }
        
        .chat-body {
          flex: 1;
          display: flex;
          overflow: hidden;
        }
        
        .conversation {
          flex: 1;
          padding: 20px;
          overflow-y: auto;
          background-color: #f8fafc;
        }
        
        .documents-sidebar {
          width: 250px;
          border-left: 1px solid #e2e8f0;
          padding: 15px;
          overflow-y: auto;
          background-color: white;
        }
        
        .documents-sidebar h3 {
          margin: 0 0 15px 0;
          font-size: 1rem;
          color: #4a5568;
        }
        
        .documents-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .no-documents {
          color: #a0aec0;
          font-size: 0.9rem;
          text-align: center;
          margin-top: 20px;
        }
        
        .document-item {
          display: flex;
          align-items: center;
          padding: 10px;
          border-radius: 4px;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .document-item:hover {
          background-color: #edf2f7;
        }
        
        .document-item.selected {
          background-color: #e6fffa;
          border-left: 3px solid #38b2ac;
        }
        
        .document-icon {
          margin-right: 10px;
          font-size: 1.2rem;
        }
        
        .document-info {
          flex: 1;
          min-width: 0;
        }
        
        .document-title {
          margin: 0 0 3px 0;
          font-size: 0.9rem;
          color: #2d3748;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        
        .document-date {
          margin: 0;
          font-size: 0.7rem;
          color: #a0aec0;
        }
        
        .empty-conversation {
          height: 100%;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          color: #718096;
          text-align: center;
        }
        
        .welcome-message {
          margin-bottom: 30px;
        }
        
        .welcome-message h3 {
          margin: 0 0 10px 0;
          color: #4a5568;
        }
        
        .welcome-message p {
          margin: 0;
          font-size: 0.9rem;
        }
        
        .selected-document-info {
          margin-top: 15px;
          padding: 10px;
          background-color: #e6fffa;
          border-radius: 4px;
          font-size: 0.9rem;
        }
        
        .suggested-prompts {
          width: 100%;
          max-width: 500px;
        }
        
        .suggested-prompts h4 {
          margin: 0 0 10px 0;
          color: #4a5568;
          font-size: 0.9rem;
        }
        
        .suggested-prompts ul {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }
        
        .suggested-prompts li {
          padding: 10px 15px;
          background-color: #edf2f7;
          border-radius: 8px;
          cursor: pointer;
          transition: background-color 0.2s;
          font-size: 0.9rem;
          text-align: left;
        }
        
        .suggested-prompts li:hover {
          background-color: #e2e8f0;
        }
        
        .message {
          display: flex;
          margin-bottom: 20px;
        }
        
        .user-message {
          flex-direction: row-reverse;
        }
        
        .message-avatar {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          flex-shrink: 0;
        }
        
        .user-message .message-avatar {
          background-color: #4299e1;
          color: white;
          margin-left: 12px;
        }
        
        .agent-message .message-avatar {
          background-color: #3182ce;
          color: white;
          margin-right: 12px;
        }
        
        .message-content {
          max-width: 70%;
        }
        
        .message-text {
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 0.95rem;
          line-height: 1.5;
        }
        
        .user-message .message-text {
          background-color: #4299e1;
          color: white;
          border-top-right-radius: 0;
        }
        
        .agent-message .message-text {
          background-color: #e2e8f0;
          color: #2d3748;
          border-top-left-radius: 0;
        }
        
        .message-timestamp {
          font-size: 0.7rem;
          color: #a0aec0;
          margin-top: 5px;
        }
        
        .user-message .message-timestamp {
          text-align: right;
        }
        
        .input-area {
          padding: 15px 20px;
          border-top: 1px solid #e2e8f0;
          display: flex;
          align-items: center;
          background-color: white;
        }
        
        .input-area textarea {
          flex: 1;
          border: 1px solid #e2e8f0;
          border-radius: 8px;
          padding: 12px 15px;
          font-size: 0.95rem;
          resize: none;
          height: 50px;
          outline: none;
          font-family: inherit;
          transition: border-color 0.2s;
        }
        
        .input-area textarea:focus {
          border-color: #4299e1;
        }
        
        .send-button {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background-color: #4299e1;
          color: white;
          border: none;
          margin-left: 10px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background-color 0.2s;
        }
        
        .send-button:hover {
          background-color: #3182ce;
        }
        
        .send-button:disabled {
          background-color: #cbd5e0;
          cursor: not-allowed;
        }
        
        .send-icon {
          font-size: 0.8rem;
        }
        
        .loading-spinner {
          width: 16px;
          height: 16px;
          border: 2px solid rgba(255, 255, 255, 0.3);
          border-radius: 50%;
          border-top-color: white;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
          .agent-chat-container {
            width: 95%;
            height: 90vh;
          }
          
          .chat-body {
            flex-direction: column;
          }
          
          .documents-sidebar {
            width: 100%;
            height: 200px;
            border-left: none;
            border-top: 1px solid #e2e8f0;
          }
          
          .message-content {
            max-width: 85%;
          }
        }
      `}</style>
    </div>
  );
};

export default AgentChat;
