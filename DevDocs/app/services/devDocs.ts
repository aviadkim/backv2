import { googleCloudStorage, googleCloudDocumentAI } from './googleCloud';
import { v4 as uuidv4 } from 'uuid';

// Document types
export enum DocumentType {
  FINANCIAL_STATEMENT = 'financial_statement',
  PORTFOLIO_STATEMENT = 'portfolio_statement',
  ANNUAL_REPORT = 'annual_report',
  TAX_DOCUMENT = 'tax_document',
  INVOICE = 'invoice',
  RECEIPT = 'receipt',
  OTHER = 'other',
}

// Document metadata
export interface DocumentMetadata {
  id: string;
  name: string;
  type: DocumentType;
  uploadedAt: string;
  size: number;
  mimeType: string;
  url: string;
  tags?: string[];
  processingStatus: 'pending' | 'processing' | 'completed' | 'failed';
  processingResult?: any;
}

// DevDocs service
export class DevDocsService {
  private documentsDirectory = 'documents';
  
  // Upload a document to Google Cloud Storage and process it with Document AI
  async uploadDocument(
    file: Buffer,
    fileName: string,
    contentType: string,
    documentType: DocumentType
  ): Promise<DocumentMetadata> {
    try {
      // Generate a unique ID for the document
      const documentId = uuidv4();
      
      // Upload the file to Google Cloud Storage
      const url = await googleCloudStorage.uploadFile(
        file,
        `${this.documentsDirectory}/${documentId}/${fileName}`,
        contentType
      );
      
      // Create document metadata
      const metadata: DocumentMetadata = {
        id: documentId,
        name: fileName,
        type: documentType,
        uploadedAt: new Date().toISOString(),
        size: file.length,
        mimeType: contentType,
        url,
        processingStatus: 'pending',
      };
      
      // Store the metadata in Google Cloud Storage
      await this.saveDocumentMetadata(metadata);
      
      // Process the document with Document AI (asynchronously)
      this.processDocumentAsync(documentId, file, contentType);
      
      return metadata;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  }
  
  // Process a document with Document AI asynchronously
  private async processDocumentAsync(
    documentId: string,
    file: Buffer,
    contentType: string
  ): Promise<void> {
    try {
      // Update the processing status to 'processing'
      const metadata = await this.getDocumentMetadata(documentId);
      metadata.processingStatus = 'processing';
      await this.saveDocumentMetadata(metadata);
      
      // Process the document with Document AI
      const result = await googleCloudDocumentAI.processDocument(file, contentType);
      
      // Update the metadata with the processing result
      metadata.processingStatus = 'completed';
      metadata.processingResult = result;
      await this.saveDocumentMetadata(metadata);
    } catch (error) {
      console.error(`Error processing document ${documentId}:`, error);
      
      // Update the processing status to 'failed'
      const metadata = await this.getDocumentMetadata(documentId);
      metadata.processingStatus = 'failed';
      await this.saveDocumentMetadata(metadata);
    }
  }
  
  // Get document metadata
  async getDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
    try {
      // Download the metadata file from Google Cloud Storage
      const buffer = await googleCloudStorage.downloadFile(
        `${this.documentsDirectory}/${documentId}/metadata.json`
      );
      
      // Parse the metadata
      return JSON.parse(buffer.toString());
    } catch (error) {
      console.error(`Error getting document metadata for ${documentId}:`, error);
      throw error;
    }
  }
  
  // Save document metadata
  private async saveDocumentMetadata(metadata: DocumentMetadata): Promise<void> {
    try {
      // Convert the metadata to JSON
      const metadataJson = JSON.stringify(metadata, null, 2);
      
      // Upload the metadata file to Google Cloud Storage
      await googleCloudStorage.uploadFile(
        Buffer.from(metadataJson),
        `${this.documentsDirectory}/${metadata.id}/metadata.json`,
        'application/json'
      );
    } catch (error) {
      console.error(`Error saving document metadata for ${metadata.id}:`, error);
      throw error;
    }
  }
  
  // List all documents
  async listDocuments(): Promise<DocumentMetadata[]> {
    try {
      // List all files in the documents directory
      const files = await googleCloudStorage.listFiles(this.documentsDirectory);
      
      // Filter for metadata files
      const metadataFiles = files.filter((file) => file.endsWith('metadata.json'));
      
      // Get the metadata for each document
      const metadataPromises = metadataFiles.map(async (file) => {
        const buffer = await googleCloudStorage.downloadFile(file);
        return JSON.parse(buffer.toString());
      });
      
      // Wait for all metadata to be retrieved
      const metadataList = await Promise.all(metadataPromises);
      
      // Sort by upload date (newest first)
      return metadataList.sort((a, b) => {
        return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime();
      });
    } catch (error) {
      console.error('Error listing documents:', error);
      throw error;
    }
  }
  
  // Get a document by ID
  async getDocument(documentId: string): Promise<{ metadata: DocumentMetadata; content: Buffer }> {
    try {
      // Get the document metadata
      const metadata = await this.getDocumentMetadata(documentId);
      
      // Get the document content
      const files = await googleCloudStorage.listFiles(`${this.documentsDirectory}/${documentId}`);
      
      // Find the document file (not the metadata file)
      const documentFile = files.find((file) => !file.endsWith('metadata.json'));
      
      if (!documentFile) {
        throw new Error(`Document file not found for ${documentId}`);
      }
      
      // Download the document content
      const content = await googleCloudStorage.downloadFile(documentFile);
      
      return { metadata, content };
    } catch (error) {
      console.error(`Error getting document ${documentId}:`, error);
      throw error;
    }
  }
  
  // Delete a document
  async deleteDocument(documentId: string): Promise<void> {
    try {
      // List all files in the document directory
      const files = await googleCloudStorage.listFiles(`${this.documentsDirectory}/${documentId}`);
      
      // Delete each file
      for (const file of files) {
        await googleCloudStorage.deleteFile(file);
      }
    } catch (error) {
      console.error(`Error deleting document ${documentId}:`, error);
      throw error;
    }
  }
  
  // Update document metadata
  async updateDocumentMetadata(
    documentId: string,
    updates: Partial<DocumentMetadata>
  ): Promise<DocumentMetadata> {
    try {
      // Get the current metadata
      const metadata = await this.getDocumentMetadata(documentId);
      
      // Update the metadata
      const updatedMetadata = { ...metadata, ...updates };
      
      // Save the updated metadata
      await this.saveDocumentMetadata(updatedMetadata);
      
      return updatedMetadata;
    } catch (error) {
      console.error(`Error updating document metadata for ${documentId}:`, error);
      throw error;
    }
  }
}

// Export a singleton instance of the service
export const devDocsService = new DevDocsService();
