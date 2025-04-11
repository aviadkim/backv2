'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

// Simple SVG icon
interface IconProps {
  className?: string;
}

const ArrowLeftIcon = ({ className }: IconProps) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
    <line x1="19" y1="12" x2="5" y2="12"></line>
    <polyline points="12 19 5 12 12 5"></polyline>
  </svg>
);

export default function NewAgentPage() {
  const router = useRouter();
  const [agentTypes, setAgentTypes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: '',
    config: {}
  });
  const [selectedType, setSelectedType] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);

        // Fetch agent types
        const agentsResponse = await fetch('/api/agents');
        if (!agentsResponse.ok) {
          throw new Error('Failed to fetch agent types');
        }
        const agentsData = await agentsResponse.json();
        setAgentTypes(agentsData.availableAgentTypes || []);

        // Fetch API keys
        const keysResponse = await fetch('/api/keys');
        if (!keysResponse.ok) {
          throw new Error('Failed to fetch API keys');
        }
        const keysData = await keysResponse.json();
        setApiKeys(keysData || []);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  const handleTypeSelect = (type: any) => {
    setSelectedType(type);
    setFormData({
      ...formData,
      type: type.id,
      config: { ...type.defaultConfig }
    });
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleConfigChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      config: {
        ...formData.config,
        [name]: value
      }
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.type) {
      setError('Name and agent type are required');
      return;
    }

    try {
      setSubmitting(true);

      // Find the selected API key for this agent type
      const apiKeyField = document.getElementById('apiKey') as HTMLSelectElement;
      const selectedApiKey = apiKeyField?.value;

      // Add API key to config if selected
      const configWithApiKey = {
        ...formData.config,
        api_key: selectedApiKey || ''
      };

      const response = await fetch('/api/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          config: configWithApiKey
        })
      });

      if (!response.ok) {
        throw new Error('Failed to create agent');
      }

      const data = await response.json();
      router.push(`/agents/${data.id}`);
    } catch (err) {
      console.error('Error creating agent:', err);
      setError('Failed to create agent. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <Link href="/agents" className="flex items-center text-blue-600 hover:text-blue-800">
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Back to Agents
        </Link>
      </div>

      <h1 className="text-3xl font-bold mb-8">Create New Agent</h1>

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Agent Types */}
          <div className="md:col-span-1">
            <h2 className="text-xl font-semibold mb-4">Select Agent Type</h2>
            <div className="space-y-4">
              {agentTypes.map((type: any) => (
                <div
                  key={type.id}
                  className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                    selectedType?.id === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'hover:bg-gray-50'
                  }`}
                  onClick={() => handleTypeSelect(type)}
                >
                  <h3 className="font-semibold">{type.name}</h3>
                  <p className="text-sm text-gray-600">{type.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Agent Configuration */}
          <div className="md:col-span-2">
            <h2 className="text-xl font-semibold mb-4">Configure Your Agent</h2>

            {!selectedType ? (
              <div className="bg-gray-100 rounded-lg p-8 text-center">
                <p className="text-gray-600">
                  Please select an agent type from the left panel to configure your agent.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Agent Name *
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {selectedType.requiresApiKey && (
                  <div>
                    <label htmlFor="apiKey" className="block text-sm font-medium text-gray-700 mb-1">
                      API Key
                    </label>
                    <select
                      id="apiKey"
                      name="apiKey"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value="">Select an API key</option>
                      {apiKeys
                        .filter((key: any) => key.type === selectedType.id)
                        .map((key: any) => (
                          <option key={key.id} value={key.key}>
                            {key.name}
                          </option>
                        ))}
                    </select>
                    {apiKeys.filter((key: any) => key.type === selectedType.id).length === 0 && (
                      <p className="mt-2 text-sm text-red-600">
                        No API keys found for this agent type.{' '}
                        <Link href="/api-keys" className="text-blue-600 hover:text-blue-800">
                          Add an API key
                        </Link>
                      </p>
                    )}
                  </div>
                )}

                <div className="border-t pt-4">
                  <h3 className="font-semibold mb-4">Advanced Configuration</h3>

                  {selectedType.id === 'openrouter' && (
                    <>
                      <div className="mb-4">
                        <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
                          Model
                        </label>
                        <select
                          id="model"
                          name="model"
                          value={formData.config.model || 'openai/gpt-3.5-turbo'}
                          onChange={handleConfigChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="openai/gpt-3.5-turbo">GPT-3.5 Turbo</option>
                          <option value="openai/gpt-4">GPT-4</option>
                          <option value="anthropic/claude-3-opus">Claude 3 Opus</option>
                          <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet</option>
                          <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
                        </select>
                      </div>

                      <div className="mb-4">
                        <label htmlFor="system_prompt" className="block text-sm font-medium text-gray-700 mb-1">
                          System Prompt
                        </label>
                        <textarea
                          id="system_prompt"
                          name="system_prompt"
                          value={formData.config.system_prompt || 'You are a helpful AI assistant.'}
                          onChange={handleConfigChange}
                          rows={3}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 mb-1">
                            Temperature
                          </label>
                          <input
                            type="number"
                            id="temperature"
                            name="temperature"
                            min="0"
                            max="2"
                            step="0.1"
                            value={formData.config.temperature || 0.7}
                            onChange={handleConfigChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>

                        <div>
                          <label htmlFor="max_tokens" className="block text-sm font-medium text-gray-700 mb-1">
                            Max Tokens
                          </label>
                          <input
                            type="number"
                            id="max_tokens"
                            name="max_tokens"
                            min="100"
                            max="4000"
                            step="100"
                            value={formData.config.max_tokens || 1000}
                            onChange={handleConfigChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                          />
                        </div>
                      </div>
                    </>
                  )}

                  {selectedType.id === 'document' && (
                    <div className="mb-4">
                      <label htmlFor="model" className="block text-sm font-medium text-gray-700 mb-1">
                        Model
                      </label>
                      <select
                        id="model"
                        name="model"
                        value={formData.config.model || 'openai/gpt-4'}
                        onChange={handleConfigChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="openai/gpt-4">GPT-4</option>
                        <option value="anthropic/claude-3-opus">Claude 3 Opus</option>
                        <option value="anthropic/claude-3-sonnet">Claude 3 Sonnet</option>
                      </select>
                    </div>
                  )}

                  {selectedType.id === 'sql' && (
                    <div className="mb-4">
                      <label htmlFor="execute_queries" className="flex items-center">
                        <input
                          type="checkbox"
                          id="execute_queries"
                          name="execute_queries"
                          checked={formData.config.execute_queries !== false}
                          onChange={(e) => {
                            setFormData({
                              ...formData,
                              config: {
                                ...formData.config,
                                execute_queries: e.target.checked
                              }
                            });
                          }}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700">Execute SQL queries</span>
                      </label>
                      <p className="mt-1 text-xs text-gray-500">
                        If disabled, the agent will only generate SQL queries without executing them.
                      </p>
                    </div>
                  )}

                  {selectedType.id === 'web' && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label htmlFor="max_pages" className="block text-sm font-medium text-gray-700 mb-1">
                          Max Pages to Analyze
                        </label>
                        <input
                          type="number"
                          id="max_pages"
                          name="max_pages"
                          min="1"
                          max="10"
                          value={formData.config.max_pages || 3}
                          onChange={handleConfigChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>

                      <div>
                        <label htmlFor="search_results_count" className="block text-sm font-medium text-gray-700 mb-1">
                          Search Results Count
                        </label>
                        <input
                          type="number"
                          id="search_results_count"
                          name="search_results_count"
                          min="1"
                          max="20"
                          value={formData.config.search_results_count || 5}
                          onChange={handleConfigChange}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex justify-end">
                  <button
                    type="submit"
                    disabled={submitting}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-blue-300"
                  >
                    {submitting ? 'Creating...' : 'Create Agent'}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
