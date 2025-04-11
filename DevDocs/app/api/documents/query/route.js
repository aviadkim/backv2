import { NextResponse } from 'next/server';
import supabaseService from '../../../../services/supabase_service';
import { OpenAI } from 'openai';

export async function POST(req) {
  try {
    const { documentId, question } = await req.json();

    if (!documentId || !question) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
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

    // 1. Get document from Supabase
    const { data: document, error: documentError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', documentId)
      .single();

    if (documentError) {
      console.error('Error fetching document from Supabase:', documentError);
      return NextResponse.json(
        { error: 'Document not found' },
        { status: 404 }
      );
    }

    // 2. Get document content from Supabase Storage
    const { data: fileData, error: fileError } = await supabase.storage
      .from('documents')
      .download(document.file_path);

    if (fileError) {
      console.error('Error downloading file from Supabase Storage:', fileError);
      return NextResponse.json(
        { error: 'Failed to download document content' },
        { status: 500 }
      );
    }

    // 3. Extract text content based on file type
    let textContent = '';

    if (document.file_type === 'application/pdf') {
      // For PDFs, we would use a PDF parsing library
      // This is a simplified example
      textContent = 'PDF content would be extracted here';
    } else if (document.file_type.startsWith('text/')) {
      // For text files, convert buffer to string
      textContent = await fileData.text();
    } else {
      // For other file types, return an error
      return NextResponse.json(
        { error: 'Unsupported file type for querying' },
        { status: 400 }
      );
    }

    // 4. Use OpenAI to answer the query based on document content
    const openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY || '',
    });

    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are a helpful assistant that answers questions based on document content.'
        },
        {
          role: 'user',
          content: `Document content: ${textContent}\n\nQuestion: ${question}`
        }
      ],
      temperature: 0.3,
      max_tokens: 500
    });

    // 5. Return the answer
    return NextResponse.json({
      content: response.choices[0].message.content,
      metadata: {
        model: 'gpt-4o',
        document_id: documentId
      }
    });
  } catch (error) {
    console.error('Error answering question:', error);
    return NextResponse.json(
      { error: 'Failed to answer question' },
      { status: 500 }
    );
  }
}
