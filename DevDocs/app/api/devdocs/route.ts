import { NextRequest, NextResponse } from 'next/server';
import { devDocsService, DocumentType } from '@/services/devDocs';

// Helper function to parse form data
async function parseFormData(request: NextRequest) {
  const formData = await request.formData();
  const file = formData.get('file') as File;
  const documentType = formData.get('documentType') as DocumentType || DocumentType.OTHER;
  
  if (!file) {
    return { error: 'No file provided' };
  }
  
  const buffer = Buffer.from(await file.arrayBuffer());
  const fileName = file.name;
  const contentType = file.type;
  
  return { buffer, fileName, contentType, documentType };
}

// Upload a document
export async function POST(request: NextRequest) {
  try {
    const { buffer, fileName, contentType, documentType, error } = await parseFormData(request);
    
    if (error) {
      return NextResponse.json({ error }, { status: 400 });
    }
    
    const metadata = await devDocsService.uploadDocument(
      buffer,
      fileName,
      contentType,
      documentType
    );
    
    return NextResponse.json({ metadata });
  } catch (error) {
    console.error('Error uploading document:', error);
    return NextResponse.json(
      { error: 'Failed to upload document' },
      { status: 500 }
    );
  }
}

// Get all documents
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const documentId = searchParams.get('id');
    
    if (documentId) {
      // Get a specific document
      const { metadata, content } = await devDocsService.getDocument(documentId);
      
      // If the request wants the document content, return it as a blob
      if (searchParams.get('content') === 'true') {
        return new NextResponse(content, {
          headers: {
            'Content-Type': metadata.mimeType,
            'Content-Disposition': `attachment; filename="${metadata.name}"`,
          },
        });
      }
      
      // Otherwise, return the metadata
      return NextResponse.json({ metadata });
    } else {
      // List all documents
      const documents = await devDocsService.listDocuments();
      return NextResponse.json({ documents });
    }
  } catch (error) {
    console.error('Error getting documents:', error);
    return NextResponse.json(
      { error: 'Failed to get documents' },
      { status: 500 }
    );
  }
}

// Delete a document
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const documentId = searchParams.get('id');
    
    if (!documentId) {
      return NextResponse.json(
        { error: 'Document ID is required' },
        { status: 400 }
      );
    }
    
    await devDocsService.deleteDocument(documentId);
    
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting document:', error);
    return NextResponse.json(
      { error: 'Failed to delete document' },
      { status: 500 }
    );
  }
}

// Update document metadata
export async function PATCH(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const documentId = searchParams.get('id');
    
    if (!documentId) {
      return NextResponse.json(
        { error: 'Document ID is required' },
        { status: 400 }
      );
    }
    
    const updates = await request.json();
    
    const metadata = await devDocsService.updateDocumentMetadata(documentId, updates);
    
    return NextResponse.json({ metadata });
  } catch (error) {
    console.error('Error updating document metadata:', error);
    return NextResponse.json(
      { error: 'Failed to update document metadata' },
      { status: 500 }
    );
  }
}
