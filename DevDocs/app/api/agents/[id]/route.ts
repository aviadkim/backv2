import { NextRequest, NextResponse } from 'next/server';

// Mock data for user agents (this would be fetched from a database in a real app)
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

// Mock conversation history
const conversationHistory: Record<string, any[]> = {
  '1': [
    { role: 'system', content: 'You are a helpful AI assistant.' },
    { role: 'user', content: 'Hello, how are you?' },
    { role: 'assistant', content: 'I\'m doing well, thank you for asking! How can I help you today?' }
  ],
  '2': []
};

// GET /api/agents/[id] - Get agent by ID
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
    ...agent,
    conversationHistory: history
  });
}

// PUT /api/agents/[id] - Update agent
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const agentIndex = userAgents.findIndex(a => a.id === params.id);
    
    if (agentIndex === -1) {
      return NextResponse.json(
        { error: 'Agent not found' },
        { status: 404 }
      );
    }
    
    // Update agent
    const updatedAgent = {
      ...userAgents[agentIndex],
      name: body.name || userAgents[agentIndex].name,
      description: body.description || userAgents[agentIndex].description,
      config: {
        ...userAgents[agentIndex].config,
        ...(body.config || {})
      }
    };
    
    userAgents[agentIndex] = updatedAgent;
    
    return NextResponse.json(updatedAgent);
  } catch (error) {
    console.error('Error updating agent:', error);
    return NextResponse.json(
      { error: 'Failed to update agent' },
      { status: 500 }
    );
  }
}

// DELETE /api/agents/[id] - Delete agent
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const agentIndex = userAgents.findIndex(a => a.id === params.id);
  
  if (agentIndex === -1) {
    return NextResponse.json(
      { error: 'Agent not found' },
      { status: 404 }
    );
  }
  
  // Remove agent
  userAgents.splice(agentIndex, 1);
  
  // Remove conversation history
  delete conversationHistory[params.id];
  
  return NextResponse.json({ success: true });
}
