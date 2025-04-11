import { NextRequest, NextResponse } from 'next/server';

// Mock data for user agents
const userAgents = [
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

// Mock conversation history
const conversationHistory: Record<string, any[]> = {
  '1': [
    { role: 'system', content: 'You are a helpful AI assistant.' },
    { role: 'user', content: 'Hello, how are you?' },
    { role: 'assistant', content: 'I\'m doing well, thank you for asking! How can I help you today?' }
  ],
  '2': []
};

// POST /api/agents/[id]/chat - Send a message to the agent
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const agent = userAgents.find(a => a.id === params.id);
    
    if (!agent) {
      return NextResponse.json(
        { error: 'Agent not found' },
        { status: 404 }
      );
    }
    
    // Validate message
    if (!body.message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }
    
    // Initialize conversation history if it doesn't exist
    if (!conversationHistory[params.id]) {
      conversationHistory[params.id] = [];
    }
    
    // Add user message to history
    conversationHistory[params.id].push({
      role: 'user',
      content: body.message,
      timestamp: new Date().toISOString()
    });
    
    // In a real implementation, this would call the backend agent service
    // For now, we'll simulate a response based on the agent type
    let response;
    
    switch (agent.type) {
      case 'openrouter':
        response = await simulateOpenRouterResponse(body.message, agent);
        break;
      case 'document':
        response = await simulateDocumentResponse(body.message, agent, body.context);
        break;
      case 'sql':
        response = await simulateSqlResponse(body.message, agent);
        break;
      case 'web':
        response = await simulateWebResponse(body.message, agent);
        break;
      default:
        response = {
          content: 'I don\'t know how to respond to that.',
          metadata: {}
        };
    }
    
    // Add assistant response to history
    conversationHistory[params.id].push({
      role: 'assistant',
      content: response.content,
      metadata: response.metadata,
      timestamp: new Date().toISOString()
    });
    
    return NextResponse.json({
      response: response.content,
      metadata: response.metadata,
      conversationHistory: conversationHistory[params.id]
    });
  } catch (error) {
    console.error('Error processing chat message:', error);
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}

// GET /api/agents/[id]/chat - Get conversation history
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const agent = userAgents.find(a => a.id === params.id);
  
  if (!agent) {
    return NextResponse.json(
      { error: 'Agent not found' },
      { status: 404 }
    );
  }
  
  // Get conversation history
  const history = conversationHistory[params.id] || [];
  
  return NextResponse.json({
    conversationHistory: history
  });
}

// DELETE /api/agents/[id]/chat - Clear conversation history
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const agent = userAgents.find(a => a.id === params.id);
  
  if (!agent) {
    return NextResponse.json(
      { error: 'Agent not found' },
      { status: 404 }
    );
  }
  
  // Clear conversation history
  conversationHistory[params.id] = [];
  
  return NextResponse.json({ success: true });
}

// Helper functions to simulate agent responses

async function simulateOpenRouterResponse(message: string, agent: any) {
  // In a real implementation, this would call the OpenRouter API
  return {
    content: `This is a simulated response from the OpenRouter agent to your message: "${message}". In a real implementation, this would use the OpenRouter API with the ${agent.config.model} model.`,
    metadata: {
      model: agent.config.model,
      usage: {
        prompt_tokens: 100,
        completion_tokens: 50,
        total_tokens: 150
      }
    }
  };
}

async function simulateDocumentResponse(message: string, agent: any, context: any) {
  // In a real implementation, this would analyze a document
  const documentId = context?.documentId || 'unknown';
  return {
    content: `This is a simulated response from the Document agent to your question about document ${documentId}: "${message}". In a real implementation, this would analyze the document content.`,
    metadata: {
      document_id: documentId,
      model: agent.config.model
    }
  };
}

async function simulateSqlResponse(message: string, agent: any) {
  // In a real implementation, this would generate and execute a SQL query
  const sqlQuery = 'SELECT * FROM users LIMIT 10';
  return {
    content: `Based on your question "${message}", I would run the following SQL query:\n\n\`\`\`sql\n${sqlQuery}\n\`\`\`\n\nThis would return user data from the database.`,
    metadata: {
      sql_query: sqlQuery,
      executed: false
    }
  };
}

async function simulateWebResponse(message: string, agent: any) {
  // In a real implementation, this would search the web or analyze a webpage
  return {
    content: `I searched the web for information about "${message}" and found several relevant results. The most reliable source indicates that this is a complex topic with multiple perspectives.`,
    metadata: {
      search_query: message,
      search_results: [
        { title: 'Example Result 1', url: 'https://example.com/1' },
        { title: 'Example Result 2', url: 'https://example.com/2' }
      ]
    }
  };
}
