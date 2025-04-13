/**
 * Financial Data Extraction Service
 * 
 * This service provides utilities for extracting financial data from documents:
 * - ISINs (International Securities Identification Numbers)
 * - Financial metrics and values
 * - Holdings and portfolio data
 */

/**
 * Extract ISINs from text
 * @param {string} text - The text to extract ISINs from
 * @returns {Array} - Array of extracted ISINs
 */
export function extractISINs(text) {
  // ISIN pattern: 2 letters followed by 10 alphanumeric characters
  // US ISINs start with "US" followed by 10 alphanumeric characters
  const isinPattern = /\b([A-Z]{2}[0-9A-Z]{10})\b/g;
  
  // Find all matches
  const matches = [...text.matchAll(isinPattern)];
  
  // Extract unique ISINs
  const isins = new Set(matches.map(match => match[1]));
  
  return [...isins];
}

/**
 * Extract financial data from text and tables
 * @param {string} text - The document text
 * @param {Array} tables - Optional tables extracted from the document
 * @returns {Object} - Extracted financial data
 */
export function extractFinancialData(text, tables = []) {
  // Extract holdings from tables first (more reliable)
  let holdings = extractHoldingsFromTables(tables);
  
  // If no holdings found in tables, try to extract from text
  if (holdings.length === 0) {
    holdings = extractHoldingsFromText(text);
  }
  
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
 * Extract holdings from tables
 * @param {Array} tables - Tables extracted from the document
 * @returns {Array} - Extracted holdings
 */
function extractHoldingsFromTables(tables) {
  const holdings = [];
  
  tables.forEach(table => {
    // Skip tables without data
    if (!table.data || table.data.length === 0) return;
    
    // Check if this looks like a holdings table
    const hasSecurityColumn = table.headers && (
      table.headers.includes('Security') ||
      table.headers.includes('Name') ||
      table.headers.includes('Asset')
    );
    
    const hasISINColumn = table.headers && (
      table.headers.includes('ISIN') ||
      table.headers.includes('Identifier')
    );
    
    const hasValueColumn = table.headers && (
      table.headers.includes('Value') ||
      table.headers.includes('Amount') ||
      table.headers.includes('Balance')
    );
    
    if (hasSecurityColumn && (hasISINColumn || hasValueColumn)) {
      // This looks like a holdings table
      table.data.forEach(row => {
        // Extract security name
        const securityName = row.Security || row.Name || row.Asset;
        
        // Extract ISIN
        const isin = row.ISIN || row.Identifier || '';
        
        // Extract value
        let value = 0;
        const valueStr = String(row.Value || row.Amount || row.Balance || '0');
        
        // Try to parse the value
        if (valueStr) {
          // Remove currency symbols and commas
          const cleanValue = valueStr.replace(/[^0-9.-]/g, '');
          value = parseFloat(cleanValue) || 0;
        }
        
        // Add to holdings if we have at least a name and value
        if (securityName && value > 0) {
          holdings.push({
            name: securityName,
            isin,
            value
          });
        }
      });
    }
  });
  
  return holdings;
}

/**
 * Extract holdings from text
 * @param {string} text - The document text
 * @returns {Array} - Extracted holdings
 */
function extractHoldingsFromText(text) {
  const holdings = [];
  
  // This is a simplified implementation
  // In a real application, you would use more sophisticated NLP techniques
  
  // Look for patterns like "Security Name (ISIN) $1,234.56"
  const holdingPattern = /([A-Za-z0-9\s.]+)\s+\(([A-Z]{2}[0-9A-Z]{10})\)\s+\$?([0-9,.]+)/g;
  
  let match;
  while ((match = holdingPattern.exec(text)) !== null) {
    const name = match[1].trim();
    const isin = match[2];
    const valueStr = match[3].replace(/,/g, '');
    const value = parseFloat(valueStr) || 0;
    
    if (name && value > 0) {
      holdings.push({ name, isin, value });
    }
  }
  
  // Look for patterns like "Security Name ... $1,234.56"
  if (holdings.length === 0) {
    const simplePattern = /([A-Za-z0-9\s.]+)\s+\$?([0-9,.]+)/g;
    
    while ((match = simplePattern.exec(text)) !== null) {
      const name = match[1].trim();
      const valueStr = match[2].replace(/,/g, '');
      const value = parseFloat(valueStr) || 0;
      
      // Only add if the name looks like a security (at least 2 words)
      if (name && name.split(' ').length >= 2 && value > 0) {
        holdings.push({ name, isin: '', value });
      }
    }
  }
  
  return holdings;
}

export default {
  extractISINs,
  extractFinancialData
};
