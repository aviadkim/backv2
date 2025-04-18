/**
 * Export Controller
 * 
 * Handles data export requests.
 */

const dataExportService = require('../services/export/dataExportService');
const Document = require('../models/Document');
const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorMiddleware');
const { BadRequestError, NotFoundError } = require('../middleware/errorMiddleware');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');

// Promisify fs functions
const unlink = promisify(fs.unlink);

/**
 * Export document data
 * @route POST /api/export/:id
 * @access Private
 */
const exportDocument = asyncHandler(async (req, res) => {
  const documentId = req.params.id;
  const { format } = req.body;
  const options = req.body.options || {};
  
  // Validate format
  if (!format) {
    throw new BadRequestError('Export format is required');
  }
  
  // Get document
  const document = await Document.findById(documentId);
  
  try {
    // Export data
    const filePath = await dataExportService.exportData(documentId, format, options);
    
    // Set content type based on format
    let contentType;
    let fileName = `export_${document.name}_${Date.now()}`;
    
    switch (format.toLowerCase()) {
      case 'excel':
      case 'xlsx':
        contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        fileName += '.xlsx';
        break;
      case 'csv':
        contentType = 'text/csv';
        fileName += '.csv';
        break;
      case 'pdf':
        contentType = 'application/pdf';
        fileName += '.pdf';
        break;
      case 'json':
        contentType = 'application/json';
        fileName += '.json';
        break;
      default:
        contentType = 'application/octet-stream';
    }
    
    // Set headers
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${fileName}"`);
    
    // Stream file to response
    const fileStream = fs.createReadStream(filePath);
    fileStream.pipe(res);
    
    // Clean up file after sending
    fileStream.on('end', async () => {
      try {
        await unlink(filePath);
        
        // Try to remove parent directory
        const dirPath = path.dirname(filePath);
        fs.rmdir(dirPath, { recursive: true }, (err) => {
          if (err) {
            logger.warn(`Error removing export directory: ${err.message}`);
          }
        });
      } catch (error) {
        logger.warn(`Error cleaning up export file: ${error.message}`);
      }
    });
  } catch (error) {
    logger.error(`Data export failed for document ${documentId}:`, error);
    
    throw new Error(`Data export failed: ${error.message}`);
  }
});

/**
 * Get export formats
 * @route GET /api/export/formats
 * @access Private
 */
const getExportFormats = asyncHandler(async (req, res) => {
  const formats = [
    {
      id: 'excel',
      name: 'Excel',
      extension: 'xlsx',
      contentType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      description: 'Export data to Microsoft Excel format'
    },
    {
      id: 'csv',
      name: 'CSV',
      extension: 'csv',
      contentType: 'text/csv',
      description: 'Export data to CSV (Comma Separated Values) format'
    },
    {
      id: 'pdf',
      name: 'PDF',
      extension: 'pdf',
      contentType: 'application/pdf',
      description: 'Export data to PDF format'
    },
    {
      id: 'json',
      name: 'JSON',
      extension: 'json',
      contentType: 'application/json',
      description: 'Export data to JSON format'
    }
  ];
  
  res.json({
    status: 'success',
    data: {
      formats
    }
  });
});

module.exports = {
  exportDocument,
  getExportFormats
};
