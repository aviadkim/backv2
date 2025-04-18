/**
 * ISIN Extractor
 * 
 * Extracts International Securities Identification Numbers (ISINs) from financial documents
 * and associates them with security names, quantities, and values.
 */

const logger = require('../../utils/logger');

/**
 * Extract ISINs from a document
 * @param {Object} options - ISIN extraction options
 * @param {string} options.extractedText - Extracted text from the document
 * @param {Array} options.tables - Extracted tables from the document
 * @param {Array} options.pages - Array of page objects with text content
 * @returns {Promise<Object>} - ISIN extraction results
 */
async function extractISINs(options) {
  const { extractedText, tables, pages } = options;
  
  // Create result object
  const result = {
    isins: [],
    count: 0
  };
  
  try {
    // Extract ISINs from text
    const textIsins = extractIsinsFromText(extractedText);
    
    // Extract ISINs from tables
    const tableIsins = extractIsinsFromTables(tables);
    
    // Merge and deduplicate ISINs
    const mergedIsins = mergeIsins([...textIsins, ...tableIsins]);
    
    // Enrich ISINs with additional information
    const enrichedIsins = await enrichIsins(mergedIsins, extractedText, tables);
    
    result.isins = enrichedIsins;
    result.count = enrichedIsins.length;
    
    logger.info(`Extracted ${result.count} ISINs from document`);
    return result;
  } catch (error) {
    logger.error(`Error extracting ISINs: ${error.message}`, error);
    throw error;
  }
}

/**
 * Extract ISINs from text using regex
 * @param {string} text - Text to extract ISINs from
 * @returns {Array} - Extracted ISINs
 */
function extractIsinsFromText(text) {
  logger.info(`Extracting ISINs from text`);
  
  const isins = [];
  
  // ISIN pattern: 2 letters followed by 10 alphanumeric characters
  // We look for patterns that are likely to be ISINs in financial documents
  const isinPattern = /\b([A-Z]{2}[A-Z0-9]{10})\b/g;
  
  let match;
  while ((match = isinPattern.exec(text)) !== null) {
    const isin = match[1];
    
    // Validate ISIN
    if (isValidIsin(isin)) {
      // Try to find the security name near the ISIN
      const contextBefore = text.substring(Math.max(0, match.index - 100), match.index);
      const contextAfter = text.substring(match.index + isin.length, Math.min(text.length, match.index + isin.length + 100));
      const context = contextBefore + contextAfter;
      
      const securityName = extractSecurityName(context, isin);
      
      isins.push({
        code: isin,
        name: securityName,
        source: 'text',
        context: context.trim()
      });
    }
  }
  
  logger.info(`Found ${isins.length} ISINs in text`);
  return isins;
}

/**
 * Extract ISINs from tables
 * @param {Array} tables - Tables to extract ISINs from
 * @returns {Array} - Extracted ISINs
 */
function extractIsinsFromTables(tables) {
  logger.info(`Extracting ISINs from ${tables.length} tables`);
  
  const isins = [];
  
  for (const table of tables) {
    // Find the ISIN column index
    const isinColumnIndex = findColumnIndex(table.headers, ['isin', 'security id', 'identifier', 'id']);
    
    if (isinColumnIndex === -1) {
      // No ISIN column found, try to find ISINs in any column
      for (const row of table.rows) {
        for (let i = 0; i < row.length; i++) {
          const cell = row[i];
          const isinMatch = cell.match(/\b([A-Z]{2}[A-Z0-9]{10})\b/);
          
          if (isinMatch && isValidIsin(isinMatch[1])) {
            // Try to find the security name in this row
            const nameColumnIndex = findColumnIndex(table.headers, ['name', 'security', 'description', 'asset']);
            const securityName = nameColumnIndex !== -1 ? row[nameColumnIndex] : '';
            
            // Try to find quantity and value
            const quantityColumnIndex = findColumnIndex(table.headers, ['quantity', 'amount', 'units', 'shares']);
            const valueColumnIndex = findColumnIndex(table.headers, ['value', 'market value', 'total', 'position']);
            
            const quantity = quantityColumnIndex !== -1 ? parseNumber(row[quantityColumnIndex]) : null;
            const value = valueColumnIndex !== -1 ? parseNumber(row[valueColumnIndex]) : null;
            
            isins.push({
              code: isinMatch[1],
              name: securityName,
              quantity: quantity,
              value: value,
              source: 'table',
              tableId: table.id,
              rowIndex: table.rows.indexOf(row)
            });
          }
        }
      }
    } else {
      // ISIN column found, extract ISINs from that column
      for (const row of table.rows) {
        if (isinColumnIndex < row.length) {
          const cell = row[isinColumnIndex];
          const isinMatch = cell.match(/\b([A-Z]{2}[A-Z0-9]{10})\b/);
          
          if (isinMatch && isValidIsin(isinMatch[1])) {
            // Try to find the security name in this row
            const nameColumnIndex = findColumnIndex(table.headers, ['name', 'security', 'description', 'asset']);
            const securityName = nameColumnIndex !== -1 && nameColumnIndex < row.length ? row[nameColumnIndex] : '';
            
            // Try to find quantity and value
            const quantityColumnIndex = findColumnIndex(table.headers, ['quantity', 'amount', 'units', 'shares']);
            const valueColumnIndex = findColumnIndex(table.headers, ['value', 'market value', 'total', 'position']);
            
            const quantity = quantityColumnIndex !== -1 && quantityColumnIndex < row.length ? parseNumber(row[quantityColumnIndex]) : null;
            const value = valueColumnIndex !== -1 && valueColumnIndex < row.length ? parseNumber(row[valueColumnIndex]) : null;
            
            isins.push({
              code: isinMatch[1],
              name: securityName,
              quantity: quantity,
              value: value,
              source: 'table',
              tableId: table.id,
              rowIndex: table.rows.indexOf(row)
            });
          }
        }
      }
    }
  }
  
  logger.info(`Found ${isins.length} ISINs in tables`);
  return isins;
}

/**
 * Find the index of a column in a table based on possible header names
 * @param {Array} headers - Table headers
 * @param {Array} possibleNames - Possible names for the column
 * @returns {number} - Column index or -1 if not found
 */
function findColumnIndex(headers, possibleNames) {
  for (let i = 0; i < headers.length; i++) {
    const header = headers[i].toLowerCase();
    
    for (const name of possibleNames) {
      if (header.includes(name.toLowerCase())) {
        return i;
      }
    }
  }
  
  return -1;
}

/**
 * Parse a number from a string
 * @param {string} str - String to parse
 * @returns {number|null} - Parsed number or null if invalid
 */
function parseNumber(str) {
  if (!str) return null;
  
  // Remove currency symbols, commas, and other non-numeric characters
  const cleanStr = str.replace(/[^\d.-]/g, '');
  
  // Parse as float
  const num = parseFloat(cleanStr);
  
  return isNaN(num) ? null : num;
}

/**
 * Extract security name from context around an ISIN
 * @param {string} context - Text context around the ISIN
 * @param {string} isin - ISIN code
 * @returns {string} - Extracted security name or empty string
 */
function extractSecurityName(context, isin) {
  // Try to find the security name before the ISIN
  // Look for patterns like "Security Name (ISIN)" or "Security Name ISIN"
  const beforePattern = /([A-Za-z0-9\s.,&'-]+)[\s(]*\b${isin}\b/;
  const beforeMatch = context.match(beforePattern);
  
  if (beforeMatch && beforeMatch[1].trim().length > 0) {
    return beforeMatch[1].trim();
  }
  
  // Try to find the security name after the ISIN
  // Look for patterns like "ISIN Security Name" or "ISIN: Security Name"
  const afterPattern = /\b${isin}\b[:\s)]*([A-Za-z0-9\s.,&'-]+)/;
  const afterMatch = context.match(afterPattern);
  
  if (afterMatch && afterMatch[1].trim().length > 0) {
    return afterMatch[1].trim();
  }
  
  return '';
}

/**
 * Merge and deduplicate ISINs
 * @param {Array} isins - Array of ISINs to merge
 * @returns {Array} - Merged and deduplicated ISINs
 */
function mergeIsins(isins) {
  const isinMap = new Map();
  
  for (const isin of isins) {
    const code = isin.code;
    
    if (!isinMap.has(code)) {
      isinMap.set(code, isin);
    } else {
      const existing = isinMap.get(code);
      
      // Merge information, preferring table source over text source
      if (isin.source === 'table' && existing.source === 'text') {
        isinMap.set(code, {
          ...existing,
          ...isin,
          name: isin.name || existing.name
        });
      } else if (isin.source === 'text' && existing.source === 'table') {
        isinMap.set(code, {
          ...existing,
          name: existing.name || isin.name
        });
      } else {
        // Both from same source, merge and take non-null values
        isinMap.set(code, {
          ...existing,
          name: existing.name || isin.name,
          quantity: existing.quantity || isin.quantity,
          value: existing.value || isin.value
        });
      }
    }
  }
  
  return Array.from(isinMap.values());
}

/**
 * Enrich ISINs with additional information
 * @param {Array} isins - ISINs to enrich
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {Promise<Array>} - Enriched ISINs
 */
async function enrichIsins(isins, text, tables) {
  logger.info(`Enriching ${isins.length} ISINs with additional information`);
  
  // For each ISIN, try to find additional information
  for (const isin of isins) {
    // If we don't have a name yet, try harder to find one
    if (!isin.name || isin.name.length === 0) {
      isin.name = findSecurityNameInDocument(isin.code, text, tables);
    }
    
    // If we don't have quantity or value, try to find them
    if (!isin.quantity || !isin.value) {
      const { quantity, value } = findQuantityAndValue(isin.code, text, tables);
      
      if (!isin.quantity) isin.quantity = quantity;
      if (!isin.value) isin.value = value;
    }
    
    // Try to determine the security type
    isin.securityType = determineSecurityType(isin.code, isin.name);
  }
  
  return isins;
}

/**
 * Find security name in the document
 * @param {string} isin - ISIN code
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {string} - Security name or empty string
 */
function findSecurityNameInDocument(isin, text, tables) {
  // Look for the ISIN in the text with more context
  const isinIndex = text.indexOf(isin);
  
  if (isinIndex !== -1) {
    const contextBefore = text.substring(Math.max(0, isinIndex - 200), isinIndex);
    const contextAfter = text.substring(isinIndex + isin.length, Math.min(text.length, isinIndex + isin.length + 200));
    const context = contextBefore + contextAfter;
    
    // Look for patterns that might indicate a security name
    const patterns = [
      // Name before ISIN
      new RegExp(`([A-Za-z0-9\\s.,&'-]{5,50})\\s*\\(\\s*${isin}\\s*\\)`, 'i'),
      new RegExp(`([A-Za-z0-9\\s.,&'-]{5,50})\\s*${isin}`, 'i'),
      // Name after ISIN
      new RegExp(`${isin}\\s*:\\s*([A-Za-z0-9\\s.,&'-]{5,50})`, 'i'),
      new RegExp(`${isin}\\s*([A-Za-z0-9\\s.,&'-]{5,50})`, 'i')
    ];
    
    for (const pattern of patterns) {
      const match = context.match(pattern);
      if (match && match[1].trim().length > 0) {
        return match[1].trim();
      }
    }
  }
  
  // Look in tables for rows that contain this ISIN
  for (const table of tables) {
    for (const row of table.rows) {
      const rowText = row.join(' ');
      
      if (rowText.includes(isin)) {
        // Try to find a cell that might contain a name
        // Usually it's one of the first few cells
        for (let i = 0; i < Math.min(3, row.length); i++) {
          const cell = row[i];
          
          // Check if this cell doesn't contain the ISIN and has a reasonable length
          if (!cell.includes(isin) && cell.length > 3 && cell.length < 100) {
            return cell.trim();
          }
        }
      }
    }
  }
  
  return '';
}

/**
 * Find quantity and value for an ISIN
 * @param {string} isin - ISIN code
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {Object} - Object with quantity and value
 */
function findQuantityAndValue(isin, text, tables) {
  let quantity = null;
  let value = null;
  
  // Look in tables for rows that contain this ISIN
  for (const table of tables) {
    for (const row of table.rows) {
      const rowText = row.join(' ');
      
      if (rowText.includes(isin)) {
        // Try to find quantity and value columns
        const quantityColumnIndex = findColumnIndex(table.headers, ['quantity', 'amount', 'units', 'shares']);
        const valueColumnIndex = findColumnIndex(table.headers, ['value', 'market value', 'total', 'position']);
        
        if (quantityColumnIndex !== -1 && quantityColumnIndex < row.length) {
          quantity = parseNumber(row[quantityColumnIndex]);
        }
        
        if (valueColumnIndex !== -1 && valueColumnIndex < row.length) {
          value = parseNumber(row[valueColumnIndex]);
        }
        
        if (quantity !== null && value !== null) {
          return { quantity, value };
        }
      }
    }
  }
  
  // If we couldn't find both in tables, try to find them in text
  if (quantity === null || value === null) {
    const isinIndex = text.indexOf(isin);
    
    if (isinIndex !== -1) {
      const contextAfter = text.substring(isinIndex + isin.length, Math.min(text.length, isinIndex + isin.length + 300));
      
      // Look for quantity pattern
      if (quantity === null) {
        const quantityPattern = /(?:quantity|amount|units|shares)[:\s]*([0-9,.]+)/i;
        const quantityMatch = contextAfter.match(quantityPattern);
        
        if (quantityMatch) {
          quantity = parseNumber(quantityMatch[1]);
        }
      }
      
      // Look for value pattern
      if (value === null) {
        const valuePattern = /(?:value|market value|total|position)[:\s]*([0-9,.]+)/i;
        const valueMatch = contextAfter.match(valuePattern);
        
        if (valueMatch) {
          value = parseNumber(valueMatch[1]);
        }
      }
    }
  }
  
  return { quantity, value };
}

/**
 * Determine the security type based on ISIN and name
 * @param {string} isin - ISIN code
 * @param {string} name - Security name
 * @returns {string} - Security type
 */
function determineSecurityType(isin, name) {
  // ISIN country code (first two letters)
  const countryCode = isin.substring(0, 2);
  
  // Check name for common security type indicators
  const nameLower = name.toLowerCase();
  
  if (nameLower.includes('bond') || nameLower.includes('note') || nameLower.includes('treasury') || 
      nameLower.includes('gilt') || nameLower.includes('debenture')) {
    return 'bond';
  } else if (nameLower.includes('share') || nameLower.includes('stock') || 
             nameLower.includes('common') || nameLower.includes('preferred')) {
    return 'equity';
  } else if (nameLower.includes('fund') || nameLower.includes('etf') || 
             nameLower.includes('trust') || nameLower.includes('index')) {
    return 'fund';
  } else if (nameLower.includes('warrant') || nameLower.includes('right') || 
             nameLower.includes('option')) {
    return 'derivative';
  } else if (nameLower.includes('structured') || nameLower.includes('certificate') || 
             nameLower.includes('note')) {
    return 'structured_product';
  }
  
  // Default to 'unknown'
  return 'unknown';
}

/**
 * Validate an ISIN code
 * @param {string} isin - ISIN code to validate
 * @returns {boolean} - Whether the ISIN is valid
 */
function isValidIsin(isin) {
  // Basic format check: 2 letters followed by 10 alphanumeric characters
  if (!/^[A-Z]{2}[A-Z0-9]{10}$/.test(isin)) {
    return false;
  }
  
  // Check digit validation
  const isinWithoutCheckDigit = isin.slice(0, -1);
  const checkDigit = parseInt(isin.slice(-1), 36);
  
  // Convert letters to numbers (A=10, B=11, ..., Z=35)
  let expandedIsin = '';
  for (let i = 0; i < isinWithoutCheckDigit.length; i++) {
    const char = isinWithoutCheckDigit[i];
    const code = char.charCodeAt(0);
    
    if (code >= 65 && code <= 90) {
      // Letter A-Z
      expandedIsin += (code - 55).toString();
    } else {
      // Digit 0-9
      expandedIsin += char;
    }
  }
  
  // Apply Luhn algorithm
  let sum = 0;
  for (let i = 0; i < expandedIsin.length; i++) {
    let digit = parseInt(expandedIsin[i], 10);
    
    if (i % 2 === 0) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
  }
  
  const calculatedCheckDigit = (10 - (sum % 10)) % 10;
  
  return checkDigit === calculatedCheckDigit;
}

module.exports = {
  extractISINs
};
