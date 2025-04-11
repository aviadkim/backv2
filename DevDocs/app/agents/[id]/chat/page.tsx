'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

// Simple SVG icons
interface IconProps {
  className?: string;
}

const ArrowLeftIcon = ({ className }: IconProps) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="19" y1="12" x2="5" y2="12"></line>
    <polyline points="12 19 5 12 12 5"></polyline>
  </svg>
);

const PaperAirplaneIcon = ({ className }: IconProps) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="22" y1="2" x2="11" y2="13"></line>
    <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
  </svg>
);

const TrashIcon = ({ className }: IconProps) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  </svg>
);

export default function AgentChatPage() {
  const params = useParams();
  const router = useRouter();
  const [agent, setAgent] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function fetchAgent() {
      try {
        setLoading(true);
        const response = await fetch(`/api/agents/${params.id}`);

        if (!response.ok) {
          if (response.status === 404) {
            router.push('/agents');
            return;
          }
          throw new Error('Failed to fetch agent');
        }

        const data = await response.json();
        setAgent(data);

        // Fetch conversation history
        const historyResponse = await fetch(`/api/agents/${params.id}/chat`);

        if (historyResponse.ok) {
          const historyData = await historyResponse.json();
          setMessages(historyData.conversationHistory || []);
        }
      } catch (err) {
        console.error('Error fetching agent:', err);
        setError('Failed to load agent. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    if (params.id) {
      fetchAgent();
    }
  }, [params.id, router]);

  useEffect(() => {
    // Scroll to bottom when messages change
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim() || sending) return;

    try {
      setSending(true);

      // Add user message to UI immediately
      const userMessage = {
        role: 'user',
        content: input,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage]);
      setInput('');

      // Send message to API
      const response = await fetch(`/api/agents/${params.id}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: input,
          context: {} // Add any context needed for specific agent types
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      // Update messages with the full conversation history from the server
      setMessages(data.conversationHistory || []);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');

      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setSending(false);
    }
  };

  const handleClearChat = async () => {
    if (confirm('Are you sure you want to clear the conversation history?')) {
      try {
        const response = await fetch(`/api/agents/${params.id}/chat`, {
          method: 'DELETE'
        });

        if (!response.ok) {
          throw new Error('Failed to clear chat history');
        }

        setMessages([]);
      } catch (err) {
        console.error('Error clearing chat:', err);
        setError('Failed to clear chat history. Please try again.');
      }
    }
  };

  return (
    <div className="container mx-auto py-4 px-4 h-screen flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <Link href="/agents" className="mr-4 text-blue-600 hover:text-blue-800">
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          {agent && (
            <div>
              <h1 className="text-xl font-bold">{agent.name}</h1>
              <p className="text-sm text-gray-600">{agent.type} agent</p>
            </div>
          )}
        </div>

        <button
          onClick={handleClearChat}
          className="flex items-center text-gray-600 hover:text-red-600"
          title="Clear chat history"
        >
          <TrashIcon className="h-5 w-5" />
        </button>
      </div>

      {loading ? (
        <div className="flex-grow flex justify-center items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      ) : (
        <>
          {/* Chat Messages */}
          <div className="flex-grow overflow-y-auto mb-4 border rounded-lg p-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="h-full flex flex-col justify-center items-center text-center text-gray-500">
                <h2 className="text-xl font-semibold mb-2">Start a conversation</h2>
                <p className="max-w-md">
                  Send a message to start chatting with {agent?.name || 'the agent'}.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message: any, index: number) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-3/4 rounded-lg px-4 py-2 ${
                        message.role === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border text-gray-800'
                      }`}
                    >
                      {message.role === 'assistant' ? (
                        <ReactMarkdown className="prose prose-sm max-w-none">
                          {message.content}
                        </ReactMarkdown>
                      ) : (
                        <p>{message.content}</p>
                      )}

                      {message.timestamp && (
                        <div className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-blue-200' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              className="flex-grow px-4 py-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="bg-blue-600 text-white px-4 py-2 rounded-r-lg hover:bg-blue-700 disabled:bg-blue-300 flex items-center"
            >
              {sending ? (
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
              ) : (
                <PaperAirplaneIcon className="h-5 w-5" />
              )}
            </button>
          </form>
        </>
      )}
    </div>
  );
}
