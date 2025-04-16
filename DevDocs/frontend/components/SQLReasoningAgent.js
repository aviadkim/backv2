import React, { useState, useEffect, useRef } from 'react';
import AccessibilityWrapper from './AccessibilityWrapper';
import { FiSend, FiDatabase, FiCode, FiSearch, FiInfo, FiCpu } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/cjs/styles/prism';

const SQLReasoningAgent = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeTab, setActiveTab] = useState('chat');
  const [schema, setSchema] = useState('');
  const [tables, setTables] = useState([]);
  const [customQuery, setCustomQuery] = useState('');
  const [queryResults, setQueryResults] = useState(null);
  const [queryError, setQueryError] = useState(null);
  const [knowledgeBase, setKnowledgeBase] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Fetch schema and tables on component mount
    fetchSchema();
    fetchTables();
    fetchKnowledgeBase();
  }, []);

  useEffect(() => {
    // Scroll to bottom of messages
    scrollToBottom();
  }, [conversations]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSchema = async () => {
    try {
      const response = await fetch('/api/sql-agent/schema');
      const data = await response.json();
      setSchema(data.schema);
    } catch (error) {
      console.error('Error fetching schema:', error);
    }
  };

  const fetchTables = async () => {
    try {
      const response = await fetch('/api/sql-agent/tables');
      const data = await response.json();
      setTables(data.tables);
    } catch (error) {
      console.error('Error fetching tables:', error);
    }
  };

  const fetchKnowledgeBase = async () => {
    try {
      const response = await fetch('/api/sql-agent/knowledge');
      const data = await response.json();
      setKnowledgeBase(data.knowledge_base);
    } catch (error) {
      console.error('Error fetching knowledge base:', error);
    }
  };

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) return;

    // Add user question to conversations
    setConversations(prev => [...prev, { role: 'user', content: question }]);

    // Clear input
    setQuestion('');

    // Set loading state
    setLoading(true);

    try {
      // Call API
      const response = await fetch('/api/sql-agent/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: question.trim() })
      });

      const data = await response.json();

      // Add agent response to conversations
      setConversations(prev => [...prev, {
        role: 'agent',
        content: data.explanation || 'I couldn\'t find an answer to your question.',
        sql_query: data.sql_query,
        results: data.results,
        reasoning: data.reasoning,
        error: data.error
      }]);
    } catch (error) {
      console.error('Error querying SQL agent:', error);

      // Add error message to conversations
      setConversations(prev => [...prev, {
        role: 'agent',
        content: 'Sorry, there was an error processing your question. Please try again.',
        error: error.message
      }]);
    } finally {
      // Clear loading state
      setLoading(false);
    }
  };

  const handleCustomQuerySubmit = async (e) => {
    e.preventDefault();

    if (!customQuery.trim()) return;

    setLoading(true);
    setQueryResults(null);
    setQueryError(null);

    try {
      // Call API to execute custom query
      const response = await fetch('/api/sql-agent/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: customQuery.trim() })
      });

      const data = await response.json();

      if (data.error) {
        setQueryError(data.error);
      } else {
        setQueryResults(data.results);
      }
    } catch (error) {
      console.error('Error executing custom query:', error);
      setQueryError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = async (e) => {
    e.preventDefault();

    if (!searchQuery.trim()) return;

    setLoading(true);
    setSearchResults([]);

    try {
      // Call API to search knowledge base
      const response = await fetch('/api/sql-agent/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: searchQuery.trim(), k: 5 })
      });

      const data = await response.json();
      setSearchResults(data.results || []);
    } catch (error) {
      console.error('Error searching knowledge base:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderChatTab = () => {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
              <FiDatabase className="h-12 w-12 mb-4" />
              <h3 className="text-xl font-medium">SQL Reasoning Agent</h3>
              <p className="mt-2 max-w-md">
                Ask questions about your financial data in natural language. I'll generate SQL queries and provide insights.
              </p>
              <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 max-w-lg">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Try asking:</p>
                  <p className="text-sm text-gray-500">"What is the total value of my portfolio?"</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Try asking:</p>
                  <p className="text-sm text-gray-500">"Show me my asset allocation"</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Try asking:</p>
                  <p className="text-sm text-gray-500">"What are my top performing holdings?"</p>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-gray-900">Try asking:</p>
                  <p className="text-sm text-gray-500">"How has my portfolio performed over time?"</p>
                </div>
              </div>
            </div>
          ) : (
            conversations.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-3xl rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.role === 'agent' && message.error ? (
                    <div className="text-red-500">
                      <p className="font-medium">Error:</p>
                      <p>{message.error}</p>
                    </div>
                  ) : (
                    <div>
                      <ReactMarkdown
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={tomorrow}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            );
                          }
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>

                      {message.sql_query && (
                        <div className="mt-2 p-2 bg-gray-800 rounded text-white">
                          <p className="text-xs text-gray-400 mb-1">SQL Query:</p>
                          <SyntaxHighlighter
                            language="sql"
                            style={tomorrow}
                            customStyle={{ margin: 0, padding: '0.5rem', fontSize: '0.8rem' }}
                          >
                            {message.sql_query}
                          </SyntaxHighlighter>
                        </div>
                      )}

                      {message.results && message.results.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500 mb-1">Results:</p>
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-300 text-sm">
                              <thead>
                                <tr>
                                  {Object.keys(message.results[0]).map((key) => (
                                    <th
                                      key={key}
                                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                                    >
                                      {key}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-gray-200">
                                {message.results.map((row, rowIndex) => (
                                  <tr key={rowIndex}>
                                    {Object.values(row).map((value, valueIndex) => (
                                      <td
                                        key={valueIndex}
                                        className="px-3 py-2 whitespace-nowrap"
                                      >
                                        {value !== null ? String(value) : 'null'}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 p-4">
          <form onSubmit={handleQuestionSubmit} className="flex space-x-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about your financial data..."
              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              disabled={loading}
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
              ) : (
                <FiSend className="h-4 w-4" />
              )}
            </button>
          </form>
        </div>
      </div>
    );
  };

  const renderSchemaTab = () => {
    return (
      <div className="p-4 h-full overflow-y-auto">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Database Schema</h3>

        <div className="bg-gray-50 p-4 rounded-lg">
          <pre className="whitespace-pre-wrap text-sm">{schema}</pre>
        </div>

        <div className="mt-6">
          <h4 className="text-md font-medium text-gray-900 mb-2">Tables</h4>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4">
            {tables.map((table) => (
              <div key={table} className="bg-white p-2 rounded border border-gray-200 text-sm">
                {table}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderQueryTab = () => {
    return (
      <div className="p-4 h-full flex flex-col">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Custom SQL Query</h3>

        <form onSubmit={handleCustomQuerySubmit} className="flex-1 flex flex-col">
          <div className="flex-1">
            <textarea
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="Enter your SQL query here..."
              className="w-full h-40 px-3 py-2 resize-none border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              disabled={loading}
            />
          </div>

          <div className="mt-4">
            <button
              type="submit"
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              disabled={loading}
            >
              {loading ? 'Executing...' : 'Execute Query'}
            </button>
          </div>
        </form>

        {queryError && (
          <div className="mt-4 p-4 bg-red-50 rounded-md">
            <h4 className="text-sm font-medium text-red-800 mb-1">Error:</h4>
            <p className="text-sm text-red-700">{queryError}</p>
          </div>
        )}

        {queryResults && queryResults.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Results:</h4>
            <div className="overflow-x-auto bg-white border border-gray-200 rounded-md">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {Object.keys(queryResults[0]).map((key) => (
                      <th
                        key={key}
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        {key}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {queryResults.map((row, rowIndex) => (
                    <tr key={rowIndex}>
                      {Object.values(row).map((value, valueIndex) => (
                        <td
                          key={valueIndex}
                          className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                        >
                          {value !== null ? String(value) : 'null'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderKnowledgeTab = () => {
    return (
      <div className="p-4 h-full overflow-y-auto">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Knowledge Base</h3>

        <form onSubmit={handleSearchSubmit} className="mb-6">
          <div className="flex space-x-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search knowledge base..."
              className="flex-1 min-w-0 block w-full px-3 py-2 rounded-md border border-gray-300 shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              disabled={loading}
            />
            <button
              type="submit"
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                loading ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              disabled={loading}
            >
              <FiSearch className="h-4 w-4" />
            </button>
          </div>
        </form>

        {searchResults.length > 0 && (
          <div className="mb-6">
            <h4 className="text-md font-medium text-gray-900 mb-2">Search Results</h4>
            <div className="space-y-4">
              {searchResults.map((result, index) => (
                <div key={index} className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="flex justify-between items-start">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {result.type}
                    </span>
                    <span className="text-xs text-gray-500">
                      Distance: {result.distance.toFixed(4)}
                    </span>
                  </div>
                  <div className="mt-2">
                    <pre className="whitespace-pre-wrap text-sm overflow-auto max-h-40">
                      {result.content}
                    </pre>
                  </div>
                  {result.metadata && (
                    <div className="mt-2 text-xs text-gray-500">
                      <span className="font-medium">Metadata: </span>
                      {JSON.stringify(result.metadata)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {knowledgeBase && (
          <div className="space-y-6">
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-2">Sample Queries</h4>
              <div className="space-y-2">
                {knowledgeBase.sample_queries.map((query, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                    <pre className="whitespace-pre-wrap text-sm overflow-auto max-h-40">
                      {query.content}
                    </pre>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-md font-medium text-gray-900 mb-2">Rules</h4>
              <div className="space-y-2">
                {knowledgeBase.rules.map((rule, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                    <div className="flex justify-between items-start">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {rule.metadata?.category || 'rule'}
                      </span>
                    </div>
                    <div className="mt-2">
                      <p className="text-sm">{rule.content}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-md font-medium text-gray-900 mb-2">Table Metadata</h4>
              <div className="space-y-2">
                {knowledgeBase.table_metadata.map((metadata, index) => (
                  <div key={index} className="bg-white p-3 rounded-lg border border-gray-200">
                    <div className="flex justify-between items-start">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        {metadata.metadata?.table_name || 'table'}
                      </span>
                    </div>
                    <div className="mt-2">
                      <pre className="whitespace-pre-wrap text-sm overflow-auto max-h-40">
                        {JSON.stringify(JSON.parse(metadata.content), null, 2)}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <AccessibilityWrapper>
      <div className="bg-white rounded-lg shadow-lg overflow-hidden h-[calc(100vh-12rem)]">
      <div className="border-b border-gray-200">
        <nav className="flex -mb-px">
          <button
            onClick={() => setActiveTab('chat')}
            className={`py-4 px-6 text-sm font-medium flex items-center ${
              activeTab === 'chat'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FiCpu className="mr-2 h-5 w-5" />
            Chat
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            className={`py-4 px-6 text-sm font-medium flex items-center ${
              activeTab === 'schema'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FiDatabase className="mr-2 h-5 w-5" />
            Schema
          </button>
          <button
            onClick={() => setActiveTab('query')}
            className={`py-4 px-6 text-sm font-medium flex items-center ${
              activeTab === 'query'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FiCode className="mr-2 h-5 w-5" />
            SQL Query
          </button>
          <button
            onClick={() => setActiveTab('knowledge')}
            className={`py-4 px-6 text-sm font-medium flex items-center ${
              activeTab === 'knowledge'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <FiInfo className="mr-2 h-5 w-5" />
            Knowledge Base
          </button>
        </nav>
      </div>

      <div className="h-full">
        {activeTab === 'chat' && renderChatTab()}
        {activeTab === 'schema' && renderSchemaTab()}
        {activeTab === 'query' && renderQueryTab()}
        {activeTab === 'knowledge' && renderKnowledgeTab()}
      </div>
    </div>
    </AccessibilityWrapper>
  );
};

export default SQLReasoningAgent;
