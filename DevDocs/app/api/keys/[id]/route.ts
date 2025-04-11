import { NextRequest, NextResponse } from 'next/server';

// Mock data for API keys
let apiKeys = [
  {
    id: '1',
    name: 'OpenRouter API Key',
    type: 'openrouter',
    key: 'sk-or-v1-xxxxxxxxxxxx', // In a real app, this would be encrypted
    createdAt: new Date().toISOString()
  },
  {
    id: '2',
    name: 'SERP API Key',
    type: 'serp',
    key: 'serpapi_xxxxxxxxxxxx', // In a real app, this would be encrypted
    createdAt: new Date().toISOString()
  }
];

// GET /api/keys/[id] - Get API key by ID
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const apiKey = apiKeys.find(k => k.id === params.id);
  
  if (!apiKey) {
    return NextResponse.json(
      { error: 'API key not found' },
      { status: 404 }
    );
  }
  
  // Mask the actual key value
  return NextResponse.json({
    ...apiKey,
    key: maskApiKey(apiKey.key)
  });
}

// PUT /api/keys/[id] - Update API key
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const keyIndex = apiKeys.findIndex(k => k.id === params.id);
    
    if (keyIndex === -1) {
      return NextResponse.json(
        { error: 'API key not found' },
        { status: 404 }
      );
    }
    
    // Update API key
    const updatedKey = {
      ...apiKeys[keyIndex],
      name: body.name || apiKeys[keyIndex].name,
      type: body.type || apiKeys[keyIndex].type,
      key: body.key || apiKeys[keyIndex].key // In a real app, this would be encrypted
    };
    
    apiKeys[keyIndex] = updatedKey;
    
    // Return the updated key with masked value
    return NextResponse.json({
      ...updatedKey,
      key: maskApiKey(updatedKey.key)
    });
  } catch (error) {
    console.error('Error updating API key:', error);
    return NextResponse.json(
      { error: 'Failed to update API key' },
      { status: 500 }
    );
  }
}

// DELETE /api/keys/[id] - Delete API key
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const keyIndex = apiKeys.findIndex(k => k.id === params.id);
  
  if (keyIndex === -1) {
    return NextResponse.json(
      { error: 'API key not found' },
      { status: 404 }
    );
  }
  
  // Remove API key
  apiKeys.splice(keyIndex, 1);
  
  return NextResponse.json({ success: true });
}

// Helper function to mask API key
function maskApiKey(key: string): string {
  if (!key) return '';
  
  // Keep first 4 and last 4 characters, mask the rest
  const firstFour = key.substring(0, 4);
  const lastFour = key.substring(key.length - 4);
  const maskedLength = Math.max(0, key.length - 8);
  const masked = '*'.repeat(maskedLength);
  
  return `${firstFour}${masked}${lastFour}`;
}
