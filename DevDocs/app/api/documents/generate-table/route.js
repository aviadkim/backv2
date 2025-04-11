import { NextResponse } from 'next/server';
import DocumentService from '../../../../services/document_service';

export async function POST(req) {
  try {
    const { documentId, prompt } = await req.json();

    if (!documentId || !prompt) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Create document service
    const documentService = new DocumentService();

    // Generate the table
    const tableData = await documentService.generateTable(documentId, prompt);

    return NextResponse.json({
      tableData,
      metadata: {
        model: 'gpt-4',
        document_id: documentId
      }
    });
  } catch (error) {
    console.error('Error generating table:', error);
    return NextResponse.json(
      { error: 'Failed to generate table' },
      { status: 500 }
    );
  }
}
