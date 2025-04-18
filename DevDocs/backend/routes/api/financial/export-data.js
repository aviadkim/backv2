/**
 * Financial Data Export API
 *
 * Handles exporting financial data in various formats.
 */

const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const logger = require('../../../utils/logger');

/**
 * @route POST /api/financial/export-data
 * @desc Export financial data in various formats
 * @access Public
 */
router.post('/', async (req, res) => {
  try {
    const { format, data, options } = req.body;

    if (!format) {
      return res.status(400).json({ error: 'Format is required' });
    }

    if (!data) {
      return res.status(400).json({ error: 'Data is required' });
    }

    // Process the data based on the format
    switch (format.toLowerCase()) {
      case 'json':
        return exportJson(res, data, options);
      case 'csv':
        return exportCsv(res, data, options);
      case 'excel':
        return exportExcel(res, data, options);
      case 'pdf':
        return exportPdf(res, data, options);
      default:
        return res.status(400).json({ error: `Unsupported format: ${format}` });
    }
  } catch (error) {
    logger.error(`Error exporting data: ${error.message}`, error);
    return res.status(500).json({ error: 'Error exporting data', detail: error.message });
  }
});

/**
 * Export data as JSON
 * @param {Object} res - Express response object
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 */
function exportJson(res, data, options) {
  // Set response headers
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Disposition', 'attachment; filename="financial-data.json"');

  // Send the data as JSON
  return res.json(data);
}

/**
 * Export data as CSV
 * @param {Object} res - Express response object
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 */
function exportCsv(res, data, options) {
  try {
    // Convert data to CSV format
    let csvData = '';

    // Handle different data structures
    if (Array.isArray(data)) {
      // Array of objects
      if (data.length > 0) {
        // Get headers from the first object
        const headers = Object.keys(data[0]);

        // Add headers to CSV
        csvData += headers.join(',') + '\n';

        // Add rows to CSV
        data.forEach(row => {
          const values = headers.map(header => {
            const value = row[header];
            if (value === null || value === undefined) {
              return '';
            } else if (typeof value === 'object') {
              return '"' + JSON.stringify(value).replace(/"/g, '""') + '"';
            } else if (typeof value === 'string') {
              return '"' + value.replace(/"/g, '""') + '"';
            } else {
              return value;
            }
          });
          csvData += values.join(',') + '\n';
        });
      }
    } else if (typeof data === 'object') {
      // Single object
      // Add headers to CSV
      csvData += 'Key,Value\n';

      // Add rows to CSV
      Object.entries(data).forEach(([key, value]) => {
        const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
        let formattedValue;

        if (value === null || value === undefined) {
          formattedValue = '';
        } else if (typeof value === 'object') {
          formattedValue = '"' + JSON.stringify(value).replace(/"/g, '""') + '"';
        } else if (typeof value === 'string') {
          formattedValue = '"' + value.replace(/"/g, '""') + '"';
        } else {
          formattedValue = value;
        }

        csvData += `"${formattedKey}",${formattedValue}\n`;
      });
    }

    // Set response headers
    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', 'attachment; filename="financial-data.csv"');

    // Send the CSV data
    return res.send(csvData);
  } catch (error) {
    logger.error(`Error exporting CSV: ${error.message}`, error);
    return res.status(500).json({ error: 'Error exporting CSV', detail: error.message });
  }
}

/**
 * Export data as Excel
 * @param {Object} res - Express response object
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 */
async function exportExcel(res, data, options) {
  try {
    // For now, we'll just export as CSV since we don't have ExcelJS
    // In a real implementation, we would use a library like ExcelJS
    return exportCsv(res, data, options);
  } catch (error) {
    logger.error(`Error exporting Excel: ${error.message}`, error);
    return res.status(500).json({ error: 'Error exporting Excel', detail: error.message });
  }
}

/**
 * Export data as PDF
 * @param {Object} res - Express response object
 * @param {Object} data - Data to export
 * @param {Object} options - Export options
 */
function exportPdf(res, data, options) {
  // For now, we'll just return a simple text representation
  // In a real implementation, we would use a PDF generation library

  // Convert data to text
  let textData = 'Financial Data Export\n\n';

  // Handle different data structures
  if (Array.isArray(data)) {
    // Array of objects
    if (data.length > 0) {
      // Get headers
      const headers = Object.keys(data[0]);

      // Add headers
      textData += headers.map(header =>
        header.charAt(0).toUpperCase() + header.slice(1).replace(/_/g, ' ')
      ).join('\t') + '\n';

      // Add separator
      textData += headers.map(() => '----------').join('\t') + '\n';

      // Add rows
      data.forEach(row => {
        textData += headers.map(header => {
          const value = row[header];
          return typeof value === 'object' ? JSON.stringify(value) : value;
        }).join('\t') + '\n';
      });
    }
  } else if (typeof data === 'object') {
    // Single object
    Object.entries(data).forEach(([key, value]) => {
      const formattedKey = key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ');
      const formattedValue = typeof value === 'object' ? JSON.stringify(value) : value;
      textData += `${formattedKey}: ${formattedValue}\n`;
    });
  }

  // Set response headers
  res.setHeader('Content-Type', 'text/plain');
  res.setHeader('Content-Disposition', 'attachment; filename="financial-data.txt"');

  // Send the text data
  return res.send(textData);
}

module.exports = router;
