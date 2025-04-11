import { NextRequest, NextResponse } from 'next/server';
import supabaseService from '../../../services/supabase_service';
import { v4 as uuidv4 } from 'uuid';

// GET /api/keys - Get all API keys
export async function GET(request: NextRequest) {
  try {
    // Get Supabase client
    const supabase = supabaseService.getClient();
    if (!supabase) {
      return NextResponse.json(
        { error: 'Database connection error' },
        { status: 500 }
      );
    }

    // Get user ID from session
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get user profile to get organization ID
    const { data: profile } = await supabase
      .from('profiles')
      .select('organization_id')
      .eq('id', session.user.id)
      .single();

    // Get API keys for the user's organization
    const { data: apiKeys, error } = await supabase
      .from('api_keys')
      .select('*')
      .eq('organization_id', profile?.organization_id)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching API keys:', error);
      return NextResponse.json(
        { error: 'Failed to fetch API keys' },
        { status: 500 }
      );
    }

    // Mask the key values for security
    const maskedKeys = apiKeys.map(key => ({
      ...key,
      key_value: maskApiKey(key.key_value)
    }));

    return NextResponse.json(maskedKeys);
  } catch (error) {
    console.error('Error fetching API keys:', error);
    return NextResponse.json(
      { error: 'Failed to fetch API keys' },
      { status: 500 }
    );
  }
}

// POST /api/keys - Add a new API key
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate required fields
    if (!body.name || !body.key_type || !body.key_value) {
      return NextResponse.json(
        { error: 'Name, key type, and key value are required' },
        { status: 400 }
      );
    }

    // Get Supabase client
    const supabase = supabaseService.getClient();
    if (!supabase) {
      return NextResponse.json(
        { error: 'Database connection error' },
        { status: 500 }
      );
    }

    // Get user ID from session
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get user profile to get organization ID
    const { data: profile } = await supabase
      .from('profiles')
      .select('organization_id, role')
      .eq('id', session.user.id)
      .single();

    // Check if user has permission to add API keys
    if (!profile || !profile.organization_id || profile.role !== 'admin') {
      return NextResponse.json(
        { error: 'Unauthorized - Only admins can add API keys' },
        { status: 403 }
      );
    }

    // Create new API key in Supabase
    const { data: newKey, error } = await supabase
      .from('api_keys')
      .insert({
        organization_id: profile.organization_id,
        name: body.name,
        key_type: body.key_type,
        key_value: body.key_value, // In a production app, this should be encrypted
        created_by: session.user.id
      })
      .select()
      .single();

    if (error) {
      console.error('Error adding API key:', error);
      return NextResponse.json(
        { error: 'Failed to add API key' },
        { status: 500 }
      );
    }

    // Return the new key with masked value
    return NextResponse.json({
      ...newKey,
      key_value: maskApiKey(newKey.key_value)
    }, { status: 201 });
  } catch (error) {
    console.error('Error adding API key:', error);
    return NextResponse.json(
      { error: 'Failed to add API key' },
      { status: 500 }
    );
  }
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
