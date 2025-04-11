import { Storage } from '@google-cloud/storage';
import { DocumentAI } from '@google-cloud/documentai';
import { v4 as uuidv4 } from 'uuid';

// Configuration for Google Cloud services
interface GoogleCloudConfig {
  projectId: string;
  keyFilename?: string;
  credentials?: {
    client_email: string;
    private_key: string;
  };
}

// Initialize Google Cloud configuration
const getGoogleCloudConfig = (): GoogleCloudConfig => {
  // Check if we have environment variables for credentials
  if (process.env.GOOGLE_CLOUD_CLIENT_EMAIL && process.env.GOOGLE_CLOUD_PRIVATE_KEY) {
    return {
      projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
      credentials: {
        client_email: process.env.GOOGLE_CLOUD_CLIENT_EMAIL,
        private_key: process.env.GOOGLE_CLOUD_PRIVATE_KEY.replace(/\\n/g, '\n'),
      },
    };
  }
  
  // Otherwise, use key file
  return {
    projectId: process.env.GOOGLE_CLOUD_PROJECT_ID || '',
    keyFilename: process.env.GOOGLE_CLOUD_KEY_FILENAME,
  };
};

// Google Cloud Storage service
export class GoogleCloudStorage {
  private storage: Storage;
  private bucketName: string;
  
  constructor() {
    const config = getGoogleCloudConfig();
    this.storage = new Storage(config);
    this.bucketName = process.env.GOOGLE_CLOUD_STORAGE_BUCKET || '';
  }
  
  // Upload a file to Google Cloud Storage
  async uploadFile(file: Buffer, fileName: string, contentType: string): Promise<string> {
    try {
      // Generate a unique filename to prevent collisions
      const uniqueFileName = `${uuidv4()}-${fileName}`;
      
      // Get a reference to the bucket
      const bucket = this.storage.bucket(this.bucketName);
      
      // Create a new blob in the bucket and upload the file
      const blob = bucket.file(uniqueFileName);
      
      // Create a write stream and specify the content type
      const blobStream = blob.createWriteStream({
        resumable: false,
        contentType,
      });
      
      // Return a promise that resolves with the public URL when the upload is complete
      return new Promise((resolve, reject) => {
        blobStream.on('error', (error) => {
          reject(`Error uploading file: ${error}`);
        });
        
        blobStream.on('finish', () => {
          // Make the file public
          blob.makePublic().then(() => {
            // Get the public URL
            const publicUrl = `https://storage.googleapis.com/${this.bucketName}/${uniqueFileName}`;
            resolve(publicUrl);
          }).catch(reject);
        });
        
        blobStream.end(file);
      });
    } catch (error) {
      console.error('Error uploading file to Google Cloud Storage:', error);
      throw error;
    }
  }
  
  // Download a file from Google Cloud Storage
  async downloadFile(fileName: string): Promise<Buffer> {
    try {
      // Get a reference to the file
      const file = this.storage.bucket(this.bucketName).file(fileName);
      
      // Download the file
      const [buffer] = await file.download();
      
      return buffer;
    } catch (error) {
      console.error('Error downloading file from Google Cloud Storage:', error);
      throw error;
    }
  }
  
  // List files in a directory
  async listFiles(directory: string): Promise<string[]> {
    try {
      // Get a reference to the bucket
      const bucket = this.storage.bucket(this.bucketName);
      
      // List files in the directory
      const [files] = await bucket.getFiles({ prefix: directory });
      
      // Return the file names
      return files.map((file) => file.name);
    } catch (error) {
      console.error('Error listing files in Google Cloud Storage:', error);
      throw error;
    }
  }
  
  // Delete a file from Google Cloud Storage
  async deleteFile(fileName: string): Promise<void> {
    try {
      // Get a reference to the file
      const file = this.storage.bucket(this.bucketName).file(fileName);
      
      // Delete the file
      await file.delete();
    } catch (error) {
      console.error('Error deleting file from Google Cloud Storage:', error);
      throw error;
    }
  }
}

// Google Cloud Document AI service
export class GoogleCloudDocumentAI {
  private client: DocumentAI;
  private processorId: string;
  private location: string;
  
  constructor() {
    const config = getGoogleCloudConfig();
    this.client = new DocumentAI(config);
    this.processorId = process.env.GOOGLE_CLOUD_DOCUMENT_AI_PROCESSOR_ID || '';
    this.location = process.env.GOOGLE_CLOUD_DOCUMENT_AI_LOCATION || 'us';
  }
  
  // Process a document with Document AI
  async processDocument(file: Buffer, mimeType: string): Promise<any> {
    try {
      // Get the full processor name
      const name = `projects/${getGoogleCloudConfig().projectId}/locations/${this.location}/processors/${this.processorId}`;
      
      // Convert the file to base64
      const encodedFile = file.toString('base64');
      
      // Process the document
      const [result] = await this.client.processDocument({
        name,
        rawDocument: {
          content: encodedFile,
          mimeType,
        },
      });
      
      return result;
    } catch (error) {
      console.error('Error processing document with Document AI:', error);
      throw error;
    }
  }
}

// Export a singleton instance of each service
export const googleCloudStorage = new GoogleCloudStorage();
export const googleCloudDocumentAI = new GoogleCloudDocumentAI();
