/**
 * Document Model
 *
 * Represents a document in the system.
 * Provides methods for document management.
 */

const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const supabase = require('../db/supabase');
const logger = require('../utils/logger');
const config = require('../config');
const { NotFoundError, BadRequestError } = require('../middleware/errorMiddleware');
const storageService = require('../services/storage/supabaseStorageService');

// Promisify fs functions
const mkdir = promisify(fs.mkdir);
const copyFile = promisify(fs.copyFile);
const unlink = promisify(fs.unlink);
const stat = promisify(fs.stat);
const readFile = promisify(fs.readFile);

/**
 * Document class
 */
class Document {
  /**
   * Create a new document
   * @param {Object} documentData - Document data
   * @param {Object} file - Uploaded file
   * @returns {Promise<Object>} Created document
   */
  static async create(documentData, file) {
    try {
      const { name, description, organizationId, userId } = documentData;

      // Validate required fields
      if (!name || !organizationId || !userId || !file) {
        throw new BadRequestError('Name, organization ID, user ID, and file are required');
      }

      // Generate unique ID
      const documentId = uuidv4();

      // Generate storage path
      const fileExtension = path.extname(file.originalname).toLowerCase();
      const storageFileName = `${organizationId}/${documentId}${fileExtension}`;

      // Upload file to Supabase Storage
      const uploadResult = await storageService.uploadFile(file.path, storageFileName);

      // Get file size
      const fileStats = await stat(file.path);

      // Create document in database
      const client = supabase.getClient();
      const { data: newDocument, error } = await client
        .from('documents')
        .insert({
          id: documentId,
          organization_id: organizationId,
          user_id: userId,
          name,
          description,
          file_path: uploadResult.path,
          file_type: fileExtension,
          file_size: fileStats.size,
          content_type: file.mimetype,
          status: 'uploaded',
          processing_status: 'pending',
          metadata: {
            storage: {
              bucket: uploadResult.bucket,
              path: uploadResult.path,
              url: uploadResult.fullPath
            }
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('id, name, description, file_path, file_type, file_size, content_type, status, processing_status, metadata, created_at')
        .single();

      if (error) {
        // Clean up file in storage if database insert fails
        await storageService.deleteFile(uploadResult.path);
        logger.error('Error creating document:', error);
        throw new Error('Error creating document');
      }

      // Clean up temporary file
      try {
        await unlink(file.path);
      } catch (unlinkError) {
        logger.warn(`Error deleting temporary file: ${unlinkError.message}`);
      }

      return {
        id: newDocument.id,
        name: newDocument.name,
        description: newDocument.description,
        filePath: newDocument.file_path,
        fileType: newDocument.file_type,
        fileSize: newDocument.file_size,
        contentType: newDocument.content_type,
        status: newDocument.status,
        processingStatus: newDocument.processing_status,
        metadata: newDocument.metadata,
        createdAt: newDocument.created_at
      };
    } catch (error) {
      logger.error('Error in Document.create:', error);
      throw error;
    }
  }

  /**
   * Find a document by ID
   * @param {string} id - Document ID
   * @returns {Promise<Object>} Document
   */
  static async findById(id) {
    try {
      const client = supabase.getClient();
      const { data: document, error } = await client
        .from('documents')
        .select(`
          id,
          name,
          description,
          file_path,
          file_type,
          file_size,
          content_type,
          status,
          processing_status,
          processing_error,
          metadata,
          created_at,
          updated_at,
          organization_id,
          user_id
        `)
        .eq('id', id)
        .single();

      if (error) {
        logger.error('Error finding document by ID:', error);
        throw new Error('Error finding document');
      }

      if (!document) {
        throw new NotFoundError('Document not found');
      }

      return {
        id: document.id,
        name: document.name,
        description: document.description,
        filePath: document.file_path,
        fileType: document.file_type,
        fileSize: document.file_size,
        contentType: document.content_type,
        status: document.status,
        processingStatus: document.processing_status,
        processingError: document.processing_error,
        metadata: document.metadata,
        createdAt: document.created_at,
        updatedAt: document.updated_at,
        organizationId: document.organization_id,
        userId: document.user_id
      };
    } catch (error) {
      logger.error('Error in Document.findById:', error);
      throw error;
    }
  }

  /**
   * Update a document
   * @param {string} id - Document ID
   * @param {Object} documentData - Document data to update
   * @returns {Promise<Object>} Updated document
   */
  static async update(id, documentData) {
    try {
      const { name, description, status, processingStatus, processingError, metadata } = documentData;

      // Prepare update data
      const updateData = {};

      if (name !== undefined) updateData.name = name;
      if (description !== undefined) updateData.description = description;
      if (status !== undefined) updateData.status = status;
      if (processingStatus !== undefined) updateData.processing_status = processingStatus;
      if (processingError !== undefined) updateData.processing_error = processingError;
      if (metadata !== undefined) updateData.metadata = metadata;

      updateData.updated_at = new Date().toISOString();

      // Update document
      const client = supabase.getClient();
      const { data: updatedDocument, error } = await client
        .from('documents')
        .update(updateData)
        .eq('id', id)
        .select(`
          id,
          name,
          description,
          file_path,
          file_type,
          file_size,
          content_type,
          status,
          processing_status,
          processing_error,
          metadata,
          created_at,
          updated_at,
          organization_id,
          user_id
        `)
        .single();

      if (error) {
        logger.error('Error updating document:', error);
        throw new Error('Error updating document');
      }

      if (!updatedDocument) {
        throw new NotFoundError('Document not found');
      }

      return {
        id: updatedDocument.id,
        name: updatedDocument.name,
        description: updatedDocument.description,
        filePath: updatedDocument.file_path,
        fileType: updatedDocument.file_type,
        fileSize: updatedDocument.file_size,
        contentType: updatedDocument.content_type,
        status: updatedDocument.status,
        processingStatus: updatedDocument.processing_status,
        processingError: updatedDocument.processing_error,
        metadata: updatedDocument.metadata,
        createdAt: updatedDocument.created_at,
        updatedAt: updatedDocument.updated_at,
        organizationId: updatedDocument.organization_id,
        userId: updatedDocument.user_id
      };
    } catch (error) {
      logger.error('Error in Document.update:', error);
      throw error;
    }
  }

  /**
   * Delete a document
   * @param {string} id - Document ID
   * @returns {Promise<boolean>} True if document was deleted
   */
  static async delete(id) {
    try {
      // Get document to get file path
      const document = await this.findById(id);

      // Delete document from database
      const client = supabase.getClient();
      const { error } = await client
        .from('documents')
        .delete()
        .eq('id', id);

      if (error) {
        logger.error('Error deleting document:', error);
        throw new Error('Error deleting document');
      }

      // Delete file from storage
      if (document.metadata && document.metadata.storage && document.metadata.storage.path) {
        try {
          await storageService.deleteFile(document.metadata.storage.path);
          logger.info(`Deleted document file from storage: ${document.metadata.storage.path}`);
        } catch (storageError) {
          logger.warn(`Error deleting document file from storage: ${storageError.message}`);
          // Continue even if storage deletion fails
        }
      }

      return true;
    } catch (error) {
      logger.error('Error in Document.delete:', error);
      throw error;
    }
  }

  /**
   * Get all documents for an organization
   * @param {string} organizationId - Organization ID
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Documents and count
   */
  static async getByOrganization(organizationId, options = {}) {
    try {
      const {
        page = 1,
        limit = 10,
        sortBy = 'created_at',
        sortOrder = 'desc',
        status = '',
        search = ''
      } = options;

      const offset = (page - 1) * limit;

      // Build query
      const client = supabase.getClient();
      let query = client
        .from('documents')
        .select(`
          id,
          name,
          description,
          file_type,
          file_size,
          status,
          processing_status,
          created_at,
          updated_at,
          user_id
        `, { count: 'exact' })
        .eq('organization_id', organizationId);

      // Apply filters
      if (status) {
        query = query.eq('status', status);
      }

      if (search) {
        query = query.or(`name.ilike.%${search}%,description.ilike.%${search}%`);
      }

      // Apply sorting and pagination
      query = query
        .order(sortBy, { ascending: sortOrder === 'asc' })
        .range(offset, offset + limit - 1);

      // Execute query
      const { data: documents, error, count } = await query;

      if (error) {
        logger.error('Error getting documents by organization:', error);
        throw new Error('Error getting documents');
      }

      return {
        documents: documents.map(doc => ({
          id: doc.id,
          name: doc.name,
          description: doc.description,
          fileType: doc.file_type,
          fileSize: doc.file_size,
          status: doc.status,
          processingStatus: doc.processing_status,
          createdAt: doc.created_at,
          updatedAt: doc.updated_at,
          userId: doc.user_id
        })),
        count,
        page,
        limit,
        totalPages: Math.ceil(count / limit)
      };
    } catch (error) {
      logger.error('Error in Document.getByOrganization:', error);
      throw error;
    }
  }

  /**
   * Get all documents for a user
   * @param {string} userId - User ID
   * @param {Object} options - Query options
   * @returns {Promise<Object>} Documents and count
   */
  static async getByUser(userId, options = {}) {
    try {
      const {
        page = 1,
        limit = 10,
        sortBy = 'created_at',
        sortOrder = 'desc',
        status = '',
        search = ''
      } = options;

      const offset = (page - 1) * limit;

      // Build query
      const client = supabase.getClient();
      let query = client
        .from('documents')
        .select(`
          id,
          name,
          description,
          file_type,
          file_size,
          status,
          processing_status,
          created_at,
          updated_at,
          organization_id
        `, { count: 'exact' })
        .eq('user_id', userId);

      // Apply filters
      if (status) {
        query = query.eq('status', status);
      }

      if (search) {
        query = query.or(`name.ilike.%${search}%,description.ilike.%${search}%`);
      }

      // Apply sorting and pagination
      query = query
        .order(sortBy, { ascending: sortOrder === 'asc' })
        .range(offset, offset + limit - 1);

      // Execute query
      const { data: documents, error, count } = await query;

      if (error) {
        logger.error('Error getting documents by user:', error);
        throw new Error('Error getting documents');
      }

      return {
        documents: documents.map(doc => ({
          id: doc.id,
          name: doc.name,
          description: doc.description,
          fileType: doc.file_type,
          fileSize: doc.file_size,
          status: doc.status,
          processingStatus: doc.processing_status,
          createdAt: doc.created_at,
          updatedAt: doc.updated_at,
          organizationId: doc.organization_id
        })),
        count,
        page,
        limit,
        totalPages: Math.ceil(count / limit)
      };
    } catch (error) {
      logger.error('Error in Document.getByUser:', error);
      throw error;
    }
  }

  /**
   * Add document data
   * @param {string} documentId - Document ID
   * @param {string} dataType - Data type
   * @param {Object} content - Data content
   * @returns {Promise<Object>} Document data
   */
  static async addData(documentId, dataType, content) {
    try {
      // Validate required fields
      if (!documentId || !dataType || !content) {
        throw new BadRequestError('Document ID, data type, and content are required');
      }

      // Create document data
      const client = supabase.getClient();
      const { data: documentData, error } = await client
        .from('document_data')
        .insert({
          id: uuidv4(),
          document_id: documentId,
          data_type: dataType,
          content,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        .select('id, document_id, data_type, created_at')
        .single();

      if (error) {
        logger.error('Error adding document data:', error);
        throw new Error('Error adding document data');
      }

      return {
        id: documentData.id,
        documentId: documentData.document_id,
        dataType: documentData.data_type,
        createdAt: documentData.created_at
      };
    } catch (error) {
      logger.error('Error in Document.addData:', error);
      throw error;
    }
  }

  /**
   * Get document data
   * @param {string} documentId - Document ID
   * @param {string} dataType - Data type (optional)
   * @returns {Promise<Array>} Document data
   */
  static async getData(documentId, dataType = null) {
    try {
      // Build query
      const client = supabase.getClient();
      let query = client
        .from('document_data')
        .select('id, document_id, data_type, content, created_at, updated_at')
        .eq('document_id', documentId);

      // Apply data type filter if provided
      if (dataType) {
        query = query.eq('data_type', dataType);
      }

      // Execute query
      const { data: documentData, error } = await query;

      if (error) {
        logger.error('Error getting document data:', error);
        throw new Error('Error getting document data');
      }

      return documentData.map(data => ({
        id: data.id,
        documentId: data.document_id,
        dataType: data.data_type,
        content: data.content,
        createdAt: data.created_at,
        updatedAt: data.updated_at
      }));
    } catch (error) {
      logger.error('Error in Document.getData:', error);
      throw error;
    }
  }
}

module.exports = Document;
