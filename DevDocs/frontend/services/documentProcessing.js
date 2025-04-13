/**
 * Document Processing Service
 * 
 * This service handles the processing of various document types:
 * - PDF: Extracts text, tables, and financial identifiers
 * - Excel/CSV: Extracts structured data and financial information
 * - Word: Extracts text and financial identifiers
 * 
 * It uses client-side libraries to process documents directly in the browser
 * or server-side processing for larger files, avoiding external API calls
 * to minimize costs.
 */

import { extractISINs, extractFinancialData } from './financialDataExtraction';

/**
 * Process a document based on its file type
 * @param {File|Buffer} file - The file to process
 * @param {string} fileType - The MIME type of the file
 * @returns {Promise<Object>} - The processing result
 */
export async function processDocument(file, fileType) {
  try {
    // Convert File to ArrayBuffer if needed
    const buffer = file instanceof File 
      ? await file.arrayBuffer()
      : file;
    
    if (fileType.includes('pdf')) {
      return await processPdf(buffer);
    } else if (
      fileType.includes('excel') || 
      fileType.includes('spreadsheet') ||
      fileType.includes('xlsx') ||
      fileType.includes('xls')
    ) {
      return await processExcel(buffer);
    } else if (fileType.includes('csv')) {
      return await processCsv(buffer);
    } else if (
      fileType.includes('word') || 
      fileType.includes('docx') ||
      fileType.includes('doc')
    ) {
      return await processWord(buffer);
    } else {
      return await processText(buffer);
    }
  } catch (error) {
    console.error('Error processing document:', error);
    throw new Error(`Document processing failed: ${error.message}`);
  }
}

/**
 * Process a PDF document
 * @param {ArrayBuffer} buffer - The PDF file as an ArrayBuffer
 * @returns {Promise<Object>} - The processing result
 */
async function processPdf(buffer) {
  // Dynamically import pdf-parse to reduce initial bundle size
  const pdfParse = (await import('pdf-parse')).default;
  
  try {
    const data = await pdfParse(Buffer.from(buffer));
    
    // Extract text
    const text = data.text;
    
    // Extract financial identifiers (ISINs, etc.)
    const isins = extractISINs(text);
    
    // Extract tables (simplified implementation)
    // In a real implementation, you would use a library like tabula-js
    // or implement a more sophisticated table extraction algorithm
    const tables = extractTablesFromPdf(text);
    
    // Extract financial data
    const financialData = extractFinancialData(text, tables);
    
    return {
      type: 'pdf',
      pages: data.numpages || 1,
      text,
      isins,
      tables,
      financialData
    };
  } catch (error) {
    console.error('Error processing PDF:', error);
    throw new Error(`PDF processing failed: ${error.message}`);
  }
}

/**
 * Process an Excel document
 * @param {ArrayBuffer} buffer - The Excel file as an ArrayBuffer
 * @returns {Promise<Object>} - The processing result
 */
async function processExcel(buffer) {
  // Dynamically import xlsx to reduce initial bundle size
  const XLSX = (await import('xlsx')).default;
  
  try {
    // Parse the Excel file
    const workbook = XLSX.read(buffer, { type: 'array' });
    
    // Process each sheet
    const sheets = workbook.SheetNames.map(sheetName => {
      const worksheet = workbook.Sheets[sheetName];
      
      // Convert sheet to JSON
      const data = XLSX.utils.sheet_to_json(worksheet);
      
      // Get dimensions
      const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:A1');
      const rows = range.e.r - range.s.r + 1;
      const columns = range.e.c - range.s.c + 1;
      
      return {
        name: sheetName,
        rows,
        columns,
        data
      };
    });
    
    // Extract ISINs from all sheets
    const allData = sheets.flatMap(sheet => sheet.data);
    const isins = extractISINsFromStructuredData(allData);
    
    // Extract financial data
    const financialData = extractFinancialDataFromSheets(sheets);
    
    return {
      type: 'excel',
      sheets,
      isins,
      financialData
    };
  } catch (error) {
    console.error('Error processing Excel:', error);
    throw new Error(`Excel processing failed: ${error.message}`);
  }
}

/**
 * Process a CSV document
 * @param {ArrayBuffer} buffer - The CSV file as an ArrayBuffer
 * @returns {Promise<Object>} - The processing result
 */
async function processCsv(buffer) {
  // Dynamically import papaparse to reduce initial bundle size
  const Papa = (await import('papaparse')).default;
  
  try {
    // Convert ArrayBuffer to string
    const text = new TextDecoder().decode(buffer);
    
    // Parse CSV
    const result = Papa.parse(text, { header: true });
    
    // Extract data
    const data = result.data;
    const headers = result.meta.fields || [];
    
    // Create table structure
    const table = {
      headers,
      data
    };
    
    // Extract ISINs
    const isins = extractISINsFromStructuredData(data);
    
    // Extract financial data
    const financialData = extractFinancialDataFromTable(table);
    
    return {
      type: 'csv',
      rows: data.length,
      columns: headers.length,
      tables: [table],
      isins,
      financialData
    };
  } catch (error) {
    console.error('Error processing CSV:', error);
    throw new Error(`CSV processing failed: ${error.message}`);
  }
}

/**
 * Process a Word document
 * @param {ArrayBuffer} buffer - The Word file as an ArrayBuffer
 * @returns {Promise<Object>} - The processing result
 */
async function processWord(buffer) {
  // Dynamically import mammoth to reduce initial bundle size
  const mammoth = (await import('mammoth')).default;
  
  try {
    // Convert Word to HTML
    const result = await mammoth.convertToHtml({ arrayBuffer: buffer });
    const html = result.value;
    
    // Extract text (strip HTML tags)
    const text = html.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim();
    
    // Extract ISINs
    const isins = extractISINs(text);
    
    // Extract tables from HTML
    const tables = extractTablesFromHtml(html);
    
    // Extract financial data
    const financialData = extractFinancialData(text, tables);
    
    return {
      type: 'word',
      text,
      html,
      isins,
      tables,
      financialData
    };
  } catch (error) {
    console.error('Error processing Word:', error);
    throw new Error(`Word processing failed: ${error.message}`);
  }
}

/**
 * Process a plain text document
 * @param {ArrayBuffer} buffer - The text file as an ArrayBuffer
 * @returns {Promise<Object>} - The processing result
 */
async function processText(buffer) {
  try {
    // Convert ArrayBuffer to string
    const text = new TextDecoder().decode(buffer);
    
    // Extract ISINs
    const isins = extractISINs(text);
    
    // Extract financial data
    const financialData = extractFinancialData(text);
    
    return {
      type: 'text',
      text,
      isins,
      financialData
    };
  } catch (error) {
    console.error('Error processing text:', error);
    throw new Error(`Text processing failed: ${error.message}`);
  }
}

/**
 * Extract tables from PDF text (simplified implementation)
 * @param {string} text - The PDF text
 * @returns {Array} - Extracted tables
 */
function extractTablesFromPdf(text) {
  // This is a simplified implementation
  // In a real application, you would use a more sophisticated algorithm
  // or a library like tabula-js
  
  // Look for potential table patterns in the text
  const tableRegex = /([A-Za-z0-9\s]+)\s+(US[0-9A-Z]{10})\s+(\$?[0-9,.]+)/g;
  const matches = [...text.matchAll(tableRegex)];
  
  if (matches.length > 0) {
    // Create a table from the matches
    const tableData = matches.map(match => ({
      Security: match[1].trim(),
      ISIN: match[2],
      Value: match[3]
    }));
    
    return [{
      page: 1, // Assuming first page
      rows: tableData.length,
      columns: 3,
      headers: ['Security', 'ISIN', 'Value'],
      data: tableData
    }];
  }
  
  return [];
}

/**
 * Extract tables from HTML (for Word documents)
 * @param {string} html - The HTML content
 * @returns {Array} - Extracted tables
 */
function extractTablesFromHtml(html) {
  // This is a simplified implementation
  // In a real application, you would use a DOM parser
  
  const tables = [];
  const tableRegex = /<table[^>]*>([\s\S]*?)<\/table>/gi;
  const rowRegex = /<tr[^>]*>([\s\S]*?)<\/tr>/gi;
  const cellRegex = /<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi;
  
  let tableMatch;
  let tableIndex = 0;
  
  while ((tableMatch = tableRegex.exec(html)) !== null) {
    const tableHtml = tableMatch[1];
    const rows = [];
    let headers = [];
    
    let rowMatch;
    let rowIndex = 0;
    
    while ((rowMatch = rowRegex.exec(tableHtml)) !== null) {
      const rowHtml = rowMatch[1];
      const cells = [];
      
      let cellMatch;
      while ((cellMatch = cellRegex.exec(rowHtml)) !== null) {
        cells.push(cellMatch[1].replace(/<[^>]*>/g, '').trim());
      }
      
      if (rowIndex === 0) {
        // Assume first row is headers
        headers = cells;
      } else {
        // Create object with headers as keys
        const rowData = {};
        cells.forEach((cell, i) => {
          if (headers[i]) {
            rowData[headers[i]] = cell;
          }
        });
        rows.push(rowData);
      }
      
      rowIndex++;
    }
    
    tables.push({
      index: tableIndex,
      rows: rows.length,
      columns: headers.length,
      headers,
      data: rows
    });
    
    tableIndex++;
  }
  
  return tables;
}

/**
 * Extract ISINs from structured data (Excel, CSV)
 * @param {Array} data - The structured data
 * @returns {Array} - Extracted ISINs
 */
function extractISINsFromStructuredData(data) {
  const isins = new Set();
  
  // ISIN regex pattern
  const isinPattern = /US[0-9A-Z]{10}/;
  
  // Check each cell in the data
  data.forEach(row => {
    Object.values(row).forEach(value => {
      if (typeof value === 'string' && isinPattern.test(value)) {
        isins.add(value.match(isinPattern)[0]);
      }
    });
  });
  
  return [...isins];
}

/**
 * Extract financial data from Excel sheets
 * @param {Array} sheets - The Excel sheets
 * @returns {Object} - Extracted financial data
 */
function extractFinancialDataFromSheets(sheets) {
  // This is a simplified implementation
  // In a real application, you would implement more sophisticated
  // algorithms to identify and extract financial data
  
  const holdings = [];
  
  sheets.forEach(sheet => {
    sheet.data.forEach(row => {
      // Look for rows that might represent holdings
      if (
        (row.Security || row.Name || row.Asset) &&
        (row.ISIN || row.Identifier) &&
        (row.Value || row.Amount || row.Balance)
      ) {
        holdings.push({
          name: row.Security || row.Name || row.Asset,
          isin: row.ISIN || row.Identifier,
          value: parseFloat(String(row.Value || row.Amount || row.Balance).replace(/[^0-9.]/g, ''))
        });
      }
    });
  });
  
  // Calculate summary
  const totalValue = holdings.reduce((sum, holding) => sum + holding.value, 0);
  const topHolding = holdings.length > 0 
    ? holdings.reduce((max, holding) => holding.value > max.value ? holding : max, holdings[0]).name
    : '';
  
  return {
    holdings,
    summary: {
      totalValue: `$${totalValue.toFixed(2)}`,
      totalSecurities: holdings.length,
      topHolding,
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  };
}

/**
 * Extract financial data from a table
 * @param {Object} table - The table object
 * @returns {Object} - Extracted financial data
 */
function extractFinancialDataFromTable(table) {
  // Similar to extractFinancialDataFromSheets but for a single table
  const holdings = [];
  
  table.data.forEach(row => {
    // Look for rows that might represent holdings
    if (
      (row.Security || row.Name || row.Asset) &&
      (row.ISIN || row.Identifier) &&
      (row.Value || row.Amount || row.Balance)
    ) {
      holdings.push({
        name: row.Security || row.Name || row.Asset,
        isin: row.ISIN || row.Identifier,
        value: parseFloat(String(row.Value || row.Amount || row.Balance).replace(/[^0-9.]/g, ''))
      });
    }
  });
  
  // Calculate summary
  const totalValue = holdings.reduce((sum, holding) => sum + holding.value, 0);
  const topHolding = holdings.length > 0 
    ? holdings.reduce((max, holding) => holding.value > max.value ? holding : max, holdings[0]).name
    : '';
  
  return {
    holdings,
    summary: {
      totalValue: `$${totalValue.toFixed(2)}`,
      totalSecurities: holdings.length,
      topHolding,
      lastUpdated: new Date().toISOString().split('T')[0]
    }
  };
}

export default {
  processDocument
};
