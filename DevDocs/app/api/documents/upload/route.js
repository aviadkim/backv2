import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';
import supabaseService from '../../../../services/supabase_service';

export async function POST(req) {
  try {
    const formData = await req.formData();
    const file = formData.get('file');
    const title = formData.get('title') || file?.name || 'Untitled';
    const description = formData.get('description') || '';
    const tags = formData.get('tags') ? JSON.parse(formData.get('tags')) : [];
    const organizationId = formData.get('organizationId');
    const userId = formData.get('userId');

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
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

    // 1. Upload file to Supabase Storage
    const fileExt = file.name.split('.').pop();
    const fileName = `${uuidv4()}.${fileExt}`;
    const filePath = `${organizationId || 'public'}/${fileName}`;

    // Convert file to buffer
    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    const { data: uploadData, error: uploadError } = await supabase.storage
      .from('documents')
      .upload(filePath, buffer, {
        contentType: file.type,
        cacheControl: '3600'
      });

    if (uploadError) {
      console.error('Error uploading file to Supabase Storage:', uploadError);
      return NextResponse.json(
        { error: 'Failed to upload file to storage' },
        { status: 500 }
      );
    }

    // 2. Get public URL for the file
    const { data: urlData } = supabase.storage
      .from('documents')
      .getPublicUrl(filePath);

    // 3. Create document record in the database
    const { data: documentData, error: documentError } = await supabase
      .from('documents')
      .insert({
        organization_id: organizationId || null,
        title: title,
        description: description,
        file_path: filePath,
        file_name: file.name,
        file_type: file.type,
        file_size: file.size,
        tags: tags,
        created_by: userId || null,
      })
      .select()
      .single();

    if (documentError) {
      console.error('Error creating document record in Supabase:', documentError);
      return NextResponse.json(
        { error: 'Failed to create document record' },
        { status: 500 }
      );
    }

    // Return document info
    return NextResponse.json({
      id: documentData.id,
      title: documentData.title,
      description: documentData.description,
      file_name: documentData.file_name,
      file_type: documentData.file_type,
      file_size: documentData.file_size,
      file_url: urlData.publicUrl,
      created_at: documentData.created_at,
      message: 'File uploaded successfully'
    });
  } catch (error) {
    console.error('Error uploading file:', error);
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    );
  }
}
