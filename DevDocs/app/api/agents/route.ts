import { NextRequest, NextResponse } from 'next/server';

// Mock data for available agent types
const availableAgentTypes = [
  {
    id: 'openrouter',
    name: 'General AI Assistant',
    description: 'A general-purpose AI assistant that can answer a wide range of questions.',
    requiresApiKey: true,
    defaultConfig: {
      model: 'openai/gpt-3.5-turbo',
      system_prompt: 'You are a helpful AI assistant.',
      max_tokens: 1000,
      temperature: 0.7
    }
  },
  {
    id: 'document',
    name: 'Document Analysis',
    description: 'Analyzes documents and answers questions about their content.',
    requiresApiKey: true,
    defaultConfig: {
      model: 'openai/gpt-4',
      max_tokens: 1500,
      temperature: 0.3
    }
  },
  {
    id: 'sql',
    name: 'SQL Assistant',
    description: 'Converts natural language questions into SQL queries and executes them.',
    requiresApiKey: true,
    defaultConfig: {
      model: 'openai/gpt-4',
      max_tokens: 1000,
      temperature: 0.2,
      execute_queries: true,
      max_rows: 50
    }
  },
  {
    id: 'web',
    name: 'Web Browser',
    description: 'Browses the web to find information and answer questions.',
    requiresApiKey: true,
    defaultConfig: {
      model: 'openai/gpt-4',
      max_tokens: 1500,
      temperature: 0.3,
      max_pages: 3,
      search_results_count: 5
    }
  }
];

// Mock data for user agents
let userAgents = [
  {
    id: '1',
    name: 'My Assistant',
    description: 'My personal AI assistant',
    type: 'openrouter',
    config: {
      model: 'openai/gpt-3.5-turbo',
      system_prompt: 'You are a helpful AI assistant.',
      max_tokens: 1000,
      temperature: 0.7
    },
    createdAt: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Document Analyzer',
    description: 'Analyzes financial documents',
    type: 'document',
    config: {
      model: 'openai/gpt-4',
      max_tokens: 1500,
      temperature: 0.3
    },
    createdAt: new Date().toISOString()
  }
];

// GET /api/agents - Get all available agent types and user agents
export async function GET(request: NextRequest) {
  return NextResponse.json({
    availableAgentTypes,
    userAgents
  });
}

// POST /api/agents - Create a new agent
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Validate required fields
    if (!body.name || !body.type) {
      return NextResponse.json(
        { error: 'Name and type are required' },
        { status: 400 }
      );
    }
    
    // Check if agent type is valid
    const agentType = availableAgentTypes.find(type => type.id === body.type);
    if (!agentType) {
      return NextResponse.json(
        { error: 'Invalid agent type' },
        { status: 400 }
      );
    }
    
    // Create new agent
    const newAgent = {
      id: Math.random().toString(36).substring(2, 11), // Generate a random ID
      name: body.name,
      description: body.description || '',
      type: body.type,
      config: {
        ...agentType.defaultConfig,
        ...body.config
      },
      createdAt: new Date().toISOString()
    };
    
    // Add to user agents (in a real app, this would be stored in a database)
    userAgents.push(newAgent);
    
    return NextResponse.json(newAgent, { status: 201 });
  } catch (error) {
    console.error('Error creating agent:', error);
    return NextResponse.json(
      { error: 'Failed to create agent' },
      { status: 500 }
    );
  }
}
