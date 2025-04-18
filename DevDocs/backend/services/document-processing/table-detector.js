/**
 * Table Detector
 * 
 * Detects and extracts tables from financial documents using multiple approaches:
 * - Grid-based analysis
 * - Camelot for PDF tables
 * - Regular expression patterns for structured data
 * - AI-assisted table recognition
 */

const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);
const logger = require('../../utils/logger');

/**
 * Detect and extract tables from a document
 * @param {Object} options - Table detection options
 * @param {string} options.filePath - Path to the document file
 * @param {string} options.workDir - Working directory for temporary files
 * @param {string} options.extractedText - Extracted text from the document
 * @param {Array} options.pages - Array of page objects with text content
 * @param {string} options.documentType - Type of document
 * @returns {Promise<Object>} - Table detection results
 */
async function detectTables(options) {
  const { filePath, workDir, extractedText, pages, documentType } = options;
  
  // Get file extension
  const fileExt = path.extname(filePath).toLowerCase();
  
  // Create result object
  const result = {
    tables: [],
    tableCount: 0
  };
  
  try {
    // Use multiple approaches to detect tables
    let detectedTables = [];
    
    // 1. Use Camelot for PDF tables
    if (fileExt === '.pdf') {
      const camelotTables = await extractTablesWithCamelot(filePath, workDir);
      detectedTables = [...detectedTables, ...camelotTables];
    }
    
    // 2. Use grid-based analysis for text tables
    const gridTables = await extractTablesWithGridAnalysis(extractedText, pages);
    detectedTables = [...detectedTables, ...gridTables];
    
    // 3. Use regex patterns for structured data
    const regexTables = await extractTablesWithRegex(extractedText, documentType);
    detectedTables = [...detectedTables, ...regexTables];
    
    // Remove duplicate tables
    result.tables = removeDuplicateTables(detectedTables);
    result.tableCount = result.tables.length;
    
    logger.info(`Detected ${result.tableCount} tables in document`);
    return result;
  } catch (error) {
    logger.error(`Error detecting tables: ${error.message}`, error);
    throw error;
  }
}

/**
 * Extract tables from a PDF using Camelot
 * @param {string} filePath - Path to the PDF file
 * @param {string} workDir - Working directory
 * @returns {Promise<Array>} - Extracted tables
 */
async function extractTablesWithCamelot(filePath, workDir) {
  logger.info(`Extracting tables with Camelot from: ${filePath}`);
  
  try {
    // Create output directory for Camelot
    const camelotDir = path.join(workDir, 'camelot');
    fs.mkdirSync(camelotDir, { recursive: true });
    
    // Run Camelot to extract tables
    const outputPath = path.join(camelotDir, 'tables.json');
    await execPromise(`python -m camelot.cli --format json --output ${outputPath} lattice ${filePath}`);
    
    // Check if tables were extracted
    if (!fs.existsSync(outputPath)) {
      logger.warn(`No tables extracted by Camelot from ${filePath}`);
      return [];
    }
    
    // Read and parse the extracted tables
    const tablesJson = fs.readFileSync(outputPath, 'utf8');
    const camelotResult = JSON.parse(tablesJson);
    
    // Convert Camelot format to our table format
    const tables = camelotResult.map((table, index) => {
      return {
        id: `camelot-${index + 1}`,
        page: table.page,
        extraction_method: 'camelot',
        table_number: index + 1,
        accuracy: table.accuracy,
        headers: table.data[0] || [],
        rows: table.data.slice(1) || [],
        bbox: table.bbox || null
      };
    });
    
    logger.info(`Extracted ${tables.length} tables with Camelot`);
    return tables;
  } catch (error) {
    logger.error(`Error extracting tables with Camelot: ${error.message}`);
    // Return empty array if Camelot fails
    return [];
  }
}

/**
 * Extract tables using grid-based analysis of text
 * @param {string} extractedText - Extracted text from the document
 * @param {Array} pages - Array of page objects with text content
 * @returns {Promise<Array>} - Extracted tables
 */
async function extractTablesWithGridAnalysis(extractedText, pages) {
  logger.info(`Extracting tables with grid-based analysis`);
  
  const tables = [];
  
  try {
    // Process each page separately
    for (let i = 0; i < pages.length; i++) {
      const page = pages[i];
      const pageText = page.text;
      
      // Skip pages with very little text
      if (pageText.length < 100) continue;
      
      // Find potential table regions based on line patterns
      const tableRegions = findTableRegions(pageText);
      
      for (let j = 0; j < tableRegions.length; j++) {
        const region = tableRegions[j];
        
        // Extract and parse the table
        const parsedTable = parseTableFromText(region.text);
        
        if (parsedTable && parsedTable.headers.length > 0 && parsedTable.rows.length > 0) {
          tables.push({
            id: `grid-p${i+1}-${j+1}`,
            page: i + 1,
            extraction_method: 'grid-analysis',
            table_number: j + 1,
            accuracy: 0.8, // Estimated accuracy
            headers: parsedTable.headers,
            rows: parsedTable.rows,
            bbox: null
          });
        }
      }
    }
    
    logger.info(`Extracted ${tables.length} tables with grid-based analysis`);
    return tables;
  } catch (error) {
    logger.error(`Error extracting tables with grid analysis: ${error.message}`);
    return [];
  }
}

/**
 * Find potential table regions in text
 * @param {string} text - Text to analyze
 * @returns {Array} - Array of table regions
 */
function findTableRegions(text) {
  const regions = [];
  const lines = text.split('\n');
  
  let inTable = false;
  let tableStart = 0;
  let tableText = '';
  
  // Look for patterns that indicate tables:
  // 1. Lines with multiple delimiters (spaces, tabs)
  // 2. Consistent line lengths
  // 3. Numeric columns
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    // Skip empty lines
    if (line.length === 0) {
      if (inTable) {
        // Empty line might indicate end of table
        // But only if we have multiple empty lines
        if (i + 1 < lines.length && lines[i + 1].trim().length === 0) {
          regions.push({
            startLine: tableStart,
            endLine: i - 1,
            text: tableText
          });
          
          inTable = false;
          tableText = '';
        }
      }
      continue;
    }
    
    // Check if line looks like part of a table
    const isTableLine = (
      // Has multiple word separations
      line.split(/\s{2,}/).length > 3 ||
      // Has tab characters
      line.includes('\t') ||
      // Has consistent spacing that looks like columns
      /(\S+\s{2,}){3,}\S+/.test(line) ||
      // Has multiple numeric values
      (line.match(/\d+(\.\d+)?/g) || []).length >= 3
    );
    
    if (isTableLine) {
      if (!inTable) {
        inTable = true;
        tableStart = i;
        tableText = line + '\n';
      } else {
        tableText += line + '\n';
      }
    } else if (inTable) {
      // Check if this might still be part of the table
      // For example, it could be a continuation of a cell value
      const prevLine = lines[i - 1].trim();
      
      if (prevLine.length > 0 && 
          Math.abs(line.length - prevLine.length) < 10 &&
          (line.match(/\d+(\.\d+)?/g) || []).length > 0) {
        // Likely still part of the table
        tableText += line + '\n';
      } else {
        // End of table
        regions.push({
          startLine: tableStart,
          endLine: i - 1,
          text: tableText
        });
        
        inTable = false;
        tableText = '';
      }
    }
  }
  
  // Don't forget the last table if we're still in one
  if (inTable) {
    regions.push({
      startLine: tableStart,
      endLine: lines.length - 1,
      text: tableText
    });
  }
  
  return regions;
}

/**
 * Parse a table from text
 * @param {string} text - Table text
 * @returns {Object} - Parsed table with headers and rows
 */
function parseTableFromText(text) {
  const lines = text.split('\n').filter(line => line.trim().length > 0);
  
  if (lines.length < 2) {
    return null; // Need at least headers and one row
  }
  
  // Determine the delimiter
  let delimiter;
  if (text.includes('\t')) {
    delimiter = '\t';
  } else {
    // Use multiple spaces as delimiter
    delimiter = /\s{2,}/;
  }
  
  // Parse headers from the first line
  const headers = lines[0].split(delimiter).map(h => h.trim()).filter(h => h.length > 0);
  
  // Parse rows
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const row = lines[i].split(delimiter).map(cell => cell.trim());
    
    // Skip rows that don't have enough cells
    if (row.length < Math.max(2, headers.length / 2)) {
      continue;
    }
    
    // Pad or truncate row to match headers length
    while (row.length < headers.length) row.push('');
    if (row.length > headers.length) row.splice(headers.length);
    
    rows.push(row);
  }
  
  return { headers, rows };
}

/**
 * Extract tables using regex patterns for specific document types
 * @param {string} extractedText - Extracted text from the document
 * @param {string} documentType - Type of document
 * @returns {Promise<Array>} - Extracted tables
 */
async function extractTablesWithRegex(extractedText, documentType) {
  logger.info(`Extracting tables with regex patterns for ${documentType} documents`);
  
  const tables = [];
  
  try {
    // Different regex patterns based on document type
    if (documentType === 'financial' || documentType === 'portfolio') {
      // Look for portfolio holdings tables
      const holdingsPattern = /(?:holdings|securities|positions|portfolio composition).*?\n(.*?(?:\n.*?){3,}?)\n\s*(?:total|sum|subtotal|grand total)/is;
      const holdingsMatch = extractedText.match(holdingsPattern);
      
      if (holdingsMatch) {
        const tableText = holdingsMatch[1];
        const parsedTable = parseTableFromText(tableText);
        
        if (parsedTable && parsedTable.headers.length > 0 && parsedTable.rows.length > 0) {
          tables.push({
            id: `regex-holdings-1`,
            page: 1, // We don't know the exact page
            extraction_method: 'regex',
            table_number: 1,
            accuracy: 0.7, // Estimated accuracy
            headers: parsedTable.headers,
            rows: parsedTable.rows,
            bbox: null
          });
        }
      }
      
      // Look for asset allocation tables
      const allocationPattern = /(?:asset allocation|asset class|allocation by asset).*?\n(.*?(?:\n.*?){2,}?)\n\s*(?:total|sum|100%)/is;
      const allocationMatch = extractedText.match(allocationPattern);
      
      if (allocationMatch) {
        const tableText = allocationMatch[1];
        const parsedTable = parseTableFromText(tableText);
        
        if (parsedTable && parsedTable.headers.length > 0 && parsedTable.rows.length > 0) {
          tables.push({
            id: `regex-allocation-1`,
            page: 1, // We don't know the exact page
            extraction_method: 'regex',
            table_number: 2,
            accuracy: 0.7, // Estimated accuracy
            headers: parsedTable.headers,
            rows: parsedTable.rows,
            bbox: null
          });
        }
      }
    }
    
    logger.info(`Extracted ${tables.length} tables with regex patterns`);
    return tables;
  } catch (error) {
    logger.error(`Error extracting tables with regex: ${error.message}`);
    return [];
  }
}

/**
 * Remove duplicate tables from the results
 * @param {Array} tables - Array of detected tables
 * @returns {Array} - Deduplicated tables
 */
function removeDuplicateTables(tables) {
  // Sort tables by extraction method priority
  // Camelot > Grid Analysis > Regex
  const sortedTables = [...tables].sort((a, b) => {
    const methodPriority = {
      'camelot': 3,
      'grid-analysis': 2,
      'regex': 1
    };
    
    return methodPriority[b.extraction_method] - methodPriority[a.extraction_method];
  });
  
  const uniqueTables = [];
  const tableSignatures = new Set();
  
  for (const table of sortedTables) {
    // Create a signature for the table based on headers and first row
    const headerSignature = table.headers.join('|');
    const firstRowSignature = table.rows.length > 0 ? table.rows[0].join('|') : '';
    const signature = `${headerSignature}:${firstRowSignature}`;
    
    // Check if we've already seen this table
    if (!tableSignatures.has(signature)) {
      tableSignatures.add(signature);
      uniqueTables.push(table);
    }
  }
  
  return uniqueTables;
}

module.exports = {
  detectTables
};
