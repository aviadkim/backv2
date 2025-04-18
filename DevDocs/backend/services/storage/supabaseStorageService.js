/**
 * Supabase Storage Service
 * 
 * Provides methods for storing and retrieving files from Supabase Storage.
 */

const fs = require('fs');
const path = require('path');
const { promisify } = require('util');
const supabase = require('../../db/supabase');
const logger = require('../../utils/logger');
const config = require('../../config');

// Promisify fs functions
const readFile = promisify(fs.readFile);
const stat = promisify(fs.stat);

// Default bucket name
const DEFAULT_BUCKET = 'documents';

/**
 * Initialize storage service
 * @returns {Promise<boolean>} True if initialization was successful
 */
async function initStorage() {
  try {
    const client = supabase.getClient();
    
    // Check if default bucket exists
    const { data: buckets, error: listError } = await client
      .storage
      .listBuckets();
    
    if (listError) {
      logger.error('Error listing buckets:', listError);
      throw listError;
    }
    
    // Create default bucket if it doesn't exist
    if (!buckets.find(bucket => bucket.name === DEFAULT_BUCKET)) {
      logger.info(`Creating default bucket: ${DEFAULT_BUCKET}`);
      
      const { error: createError } = await client
        .storage
        .createBucket(DEFAULT_BUCKET, {
          public: false,
          fileSizeLimit: config.upload.maxFileSize
        });
      
      if (createError) {
        logger.error('Error creating default bucket:', createError);
        throw createError;
      }
    }
    
    logger.info('Storage service initialized successfully');
    return true;
  } catch (error) {
    logger.error('Error initializing storage service:', error);
    return false;
  }
}

/**
 * Upload a file to Supabase Storage
 * @param {string} filePath - Path to the file to upload
 * @param {string} fileName - Name to use for the uploaded file
 * @param {string} bucket - Bucket to upload to (optional)
 * @returns {Promise<Object>} Upload result
 */
async function uploadFile(filePath, fileName, bucket = DEFAULT_BUCKET) {
  try {
    const client = supabase.getClient();
    
    // Check if file exists
    await stat(filePath);
    
    // Read file
    const fileBuffer = await readFile(filePath);
    
    // Upload file
    const { data, error } = await client
      .storage
      .from(bucket)
      .upload(fileName, fileBuffer, {
        contentType: getContentType(filePath),
        upsert: false
      });
    
    if (error) {
      logger.error('Error uploading file:', error);
      throw error;
    }
    
    logger.info(`File uploaded: ${fileName}`);
    
    return {
      path: data.path,
      fullPath: getFileUrl(bucket, data.path),
      bucket
    };
  } catch (error) {
    logger.error('Error in uploadFile:', error);
    throw error;
  }
}

/**
 * Download a file from Supabase Storage
 * @param {string} filePath - Path to the file in storage
 * @param {string} bucket - Bucket to download from (optional)
 * @returns {Promise<Buffer>} File buffer
 */
async function downloadFile(filePath, bucket = DEFAULT_BUCKET) {
  try {
    const client = supabase.getClient();
    
    // Download file
    const { data, error } = await client
      .storage
      .from(bucket)
      .download(filePath);
    
    if (error) {
      logger.error('Error downloading file:', error);
      throw error;
    }
    
    logger.info(`File downloaded: ${filePath}`);
    
    return data;
  } catch (error) {
    logger.error('Error in downloadFile:', error);
    throw error;
  }
}

/**
 * Get a public URL for a file
 * @param {string} bucket - Bucket name
 * @param {string} filePath - Path to the file in storage
 * @returns {string} Public URL
 */
function getFileUrl(bucket, filePath) {
  try {
    const client = supabase.getClient();
    
    // Get public URL
    const { data } = client
      .storage
      .from(bucket)
      .getPublicUrl(filePath);
    
    return data.publicUrl;
  } catch (error) {
    logger.error('Error in getFileUrl:', error);
    throw error;
  }
}

/**
 * Delete a file from Supabase Storage
 * @param {string} filePath - Path to the file in storage
 * @param {string} bucket - Bucket to delete from (optional)
 * @returns {Promise<boolean>} True if deletion was successful
 */
async function deleteFile(filePath, bucket = DEFAULT_BUCKET) {
  try {
    const client = supabase.getClient();
    
    // Delete file
    const { error } = await client
      .storage
      .from(bucket)
      .remove([filePath]);
    
    if (error) {
      logger.error('Error deleting file:', error);
      throw error;
    }
    
    logger.info(`File deleted: ${filePath}`);
    
    return true;
  } catch (error) {
    logger.error('Error in deleteFile:', error);
    throw error;
  }
}

/**
 * List files in a bucket
 * @param {string} prefix - Prefix to filter files by (optional)
 * @param {string} bucket - Bucket to list files from (optional)
 * @returns {Promise<Array>} List of files
 */
async function listFiles(prefix = '', bucket = DEFAULT_BUCKET) {
  try {
    const client = supabase.getClient();
    
    // List files
    const { data, error } = await client
      .storage
      .from(bucket)
      .list(prefix);
    
    if (error) {
      logger.error('Error listing files:', error);
      throw error;
    }
    
    return data;
  } catch (error) {
    logger.error('Error in listFiles:', error);
    throw error;
  }
}

/**
 * Create a signed URL for a file
 * @param {string} filePath - Path to the file in storage
 * @param {number} expiresIn - Expiration time in seconds (optional)
 * @param {string} bucket - Bucket name (optional)
 * @returns {Promise<string>} Signed URL
 */
async function createSignedUrl(filePath, expiresIn = 60, bucket = DEFAULT_BUCKET) {
  try {
    const client = supabase.getClient();
    
    // Create signed URL
    const { data, error } = await client
      .storage
      .from(bucket)
      .createSignedUrl(filePath, expiresIn);
    
    if (error) {
      logger.error('Error creating signed URL:', error);
      throw error;
    }
    
    return data.signedUrl;
  } catch (error) {
    logger.error('Error in createSignedUrl:', error);
    throw error;
  }
}

/**
 * Get content type based on file extension
 * @param {string} filePath - Path to the file
 * @returns {string} Content type
 */
function getContentType(filePath) {
  const extension = path.extname(filePath).toLowerCase();
  
  const contentTypes = {
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.csv': 'text/csv',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.txt': 'text/plain',
    '.json': 'application/json'
  };
  
  return contentTypes[extension] || 'application/octet-stream';
}

module.exports = {
  initStorage,
  uploadFile,
  downloadFile,
  getFileUrl,
  deleteFile,
  listFiles,
  createSignedUrl
};
