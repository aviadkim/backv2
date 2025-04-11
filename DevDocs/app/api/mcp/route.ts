import { NextRequest, NextResponse } from 'next/server';
import { gcpMcpIntegration } from '@/services/gcpMcpIntegration';

// Start the GCP MCP server
export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json();
    
    if (action === 'start') {
      const success = await gcpMcpIntegration.startMcpServer();
      
      if (success) {
        return NextResponse.json({ status: 'success', message: 'GCP MCP server started successfully' });
      } else {
        return NextResponse.json(
          { status: 'error', message: 'Failed to start GCP MCP server' },
          { status: 500 }
        );
      }
    } else if (action === 'stop') {
      const success = gcpMcpIntegration.stopMcpServer();
      
      if (success) {
        return NextResponse.json({ status: 'success', message: 'GCP MCP server stopped successfully' });
      } else {
        return NextResponse.json(
          { status: 'error', message: 'Failed to stop GCP MCP server' },
          { status: 500 }
        );
      }
    } else {
      return NextResponse.json(
        { status: 'error', message: 'Invalid action. Use "start" or "stop".' },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Error managing GCP MCP server:', error);
    return NextResponse.json(
      { status: 'error', message: 'Failed to manage GCP MCP server' },
      { status: 500 }
    );
  }
}

// Get the status of the GCP MCP server
export async function GET() {
  try {
    const status = gcpMcpIntegration.getStatus();
    
    return NextResponse.json({
      status: 'success',
      data: status
    });
  } catch (error) {
    console.error('Error getting GCP MCP server status:', error);
    return NextResponse.json(
      { status: 'error', message: 'Failed to get GCP MCP server status' },
      { status: 500 }
    );
  }
}
