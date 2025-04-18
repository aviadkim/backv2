/**
 * Financial Data Analyzer
 * 
 * Analyzes financial data extracted from documents to identify:
 * - Portfolio value
 * - Asset allocation
 * - Security details
 * - Performance metrics
 * - Currency information
 */

const logger = require('../../utils/logger');

/**
 * Analyze financial data from a document
 * @param {Object} options - Analysis options
 * @param {string} options.extractedText - Extracted text from the document
 * @param {Array} options.tables - Extracted tables from the document
 * @param {Array} options.isins - Extracted ISINs from the document
 * @param {string} options.documentType - Type of document
 * @returns {Promise<Object>} - Analysis results
 */
async function analyzeFinancialData(options) {
  const { extractedText, tables, isins, documentType } = options;
  
  // Create result object
  const result = {
    portfolio_value: null,
    asset_allocation: {},
    securities: [],
    performance: {},
    currency: null
  };
  
  try {
    // Extract portfolio value
    result.portfolio_value = extractPortfolioValue(extractedText, tables);
    
    // Extract asset allocation
    result.asset_allocation = extractAssetAllocation(extractedText, tables);
    
    // Extract securities information
    result.securities = extractSecuritiesInfo(extractedText, tables, isins);
    
    // Extract performance metrics
    result.performance = extractPerformanceMetrics(extractedText, tables);
    
    // Extract currency information
    result.currency = extractCurrencyInfo(extractedText, tables);
    
    logger.info(`Analyzed financial data: found ${result.securities.length} securities`);
    return result;
  } catch (error) {
    logger.error(`Error analyzing financial data: ${error.message}`, error);
    throw error;
  }
}

/**
 * Extract portfolio value from document
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {number|null} - Portfolio value or null if not found
 */
function extractPortfolioValue(text, tables) {
  logger.info(`Extracting portfolio value`);
  
  // Look for portfolio value in text
  const patterns = [
    /(?:portfolio|account|total)\s+(?:value|worth|amount|balance)(?:\s*:|\s+is|\s+of)?\s*[$€£¥]?\s*([\d,]+(?:\.\d+)?)/i,
    /(?:total|net)\s+(?:assets|value|worth)(?:\s*:|\s+is|\s+of)?\s*[$€£¥]?\s*([\d,]+(?:\.\d+)?)/i,
    /(?:value|worth|amount|balance)(?:\s+of)?\s+(?:portfolio|account|assets)(?:\s*:|\s+is)?\s*[$€£¥]?\s*([\d,]+(?:\.\d+)?)/i
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      const value = parseNumber(match[1]);
      if (value && value > 1000) { // Assume portfolio values are reasonably large
        return value;
      }
    }
  }
  
  // Look for portfolio value in tables
  for (const table of tables) {
    // Look for tables with summary information
    const summaryTable = isSummaryTable(table);
    
    if (summaryTable) {
      // Look for rows with total/portfolio value
      for (const row of table.rows) {
        const rowText = row.join(' ').toLowerCase();
        
        if (rowText.includes('total') || 
            rowText.includes('portfolio value') || 
            rowText.includes('net assets') ||
            rowText.includes('account value')) {
          
          // Find the value in this row (usually the last cell)
          for (let i = row.length - 1; i >= 0; i--) {
            const value = parseNumber(row[i]);
            if (value && value > 1000) {
              return value;
            }
          }
        }
      }
    }
  }
  
  // If we still don't have a value, look for the largest value in summary tables
  // which is often the portfolio total
  let largestValue = null;
  
  for (const table of tables) {
    if (isSummaryTable(table)) {
      for (const row of table.rows) {
        for (const cell of row) {
          const value = parseNumber(cell);
          if (value && (largestValue === null || value > largestValue)) {
            largestValue = value;
          }
        }
      }
    }
  }
  
  if (largestValue && largestValue > 10000) {
    return largestValue;
  }
  
  // Default to null if we couldn't find a value
  return null;
}

/**
 * Check if a table is likely a summary table
 * @param {Object} table - Table to check
 * @returns {boolean} - Whether the table is likely a summary table
 */
function isSummaryTable(table) {
  // Summary tables usually have headers related to totals, assets, or allocation
  const headerText = table.headers.join(' ').toLowerCase();
  
  return headerText.includes('total') || 
         headerText.includes('asset') || 
         headerText.includes('allocation') ||
         headerText.includes('summary') ||
         headerText.includes('portfolio') ||
         headerText.includes('value');
}

/**
 * Extract asset allocation from document
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {Object} - Asset allocation
 */
function extractAssetAllocation(text, tables) {
  logger.info(`Extracting asset allocation`);
  
  const allocation = {};
  
  // Look for asset allocation tables
  for (const table of tables) {
    // Check if this table looks like an asset allocation table
    const headerText = table.headers.join(' ').toLowerCase();
    
    if (headerText.includes('asset') || 
        headerText.includes('allocation') || 
        headerText.includes('class') ||
        headerText.includes('type')) {
      
      // Find the asset class and percentage/value columns
      const assetClassIndex = findColumnIndex(table.headers, ['asset', 'class', 'type', 'category']);
      const percentageIndex = findColumnIndex(table.headers, ['%', 'percent', 'allocation', 'weight']);
      
      if (assetClassIndex !== -1) {
        for (const row of table.rows) {
          if (assetClassIndex < row.length) {
            const assetClass = row[assetClassIndex].trim();
            
            // Skip rows that don't look like asset classes
            if (assetClass.toLowerCase().includes('total') || 
                assetClass.length < 2 || 
                /^\d+$/.test(assetClass)) {
              continue;
            }
            
            let percentage = null;
            
            // Try to get percentage from the percentage column
            if (percentageIndex !== -1 && percentageIndex < row.length) {
              percentage = parsePercentage(row[percentageIndex]);
            }
            
            // If we couldn't get a percentage, try to find it in the row
            if (percentage === null) {
              for (const cell of row) {
                const parsedPercentage = parsePercentage(cell);
                if (parsedPercentage !== null) {
                  percentage = parsedPercentage;
                  break;
                }
              }
            }
            
            // Add to allocation if we found a percentage
            if (percentage !== null) {
              allocation[assetClass] = percentage;
            }
          }
        }
      }
    }
  }
  
  // If we couldn't find allocation in tables, try to extract from text
  if (Object.keys(allocation).length === 0) {
    // Look for patterns like "X% in Asset Class"
    const allocationPattern = /(\d+(?:\.\d+)?)%\s+(?:in|of|allocated to)\s+([A-Za-z\s&-]+)/gi;
    
    let match;
    while ((match = allocationPattern.exec(text)) !== null) {
      const percentage = parseFloat(match[1]) / 100;
      const assetClass = match[2].trim();
      
      allocation[assetClass] = percentage;
    }
  }
  
  return allocation;
}

/**
 * Parse a percentage value from a string
 * @param {string} str - String to parse
 * @returns {number|null} - Parsed percentage (as decimal) or null if invalid
 */
function parsePercentage(str) {
  if (!str) return null;
  
  // Check if the string contains a percentage sign
  const hasPercentSign = str.includes('%');
  
  // Remove non-numeric characters except decimal point
  const cleanStr = str.replace(/[^\d.-]/g, '');
  
  // Parse as float
  const num = parseFloat(cleanStr);
  
  if (isNaN(num)) return null;
  
  // If the string had a percentage sign, divide by 100
  return hasPercentSign ? num / 100 : (num > 1 ? num / 100 : num);
}

/**
 * Extract securities information from document
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @param {Array} isins - Extracted ISINs
 * @returns {Array} - Securities information
 */
function extractSecuritiesInfo(text, tables, isins) {
  logger.info(`Extracting securities information for ${isins.length} ISINs`);
  
  const securities = [];
  
  // Start with the ISINs we've already extracted
  for (const isin of isins) {
    const security = {
      isin: isin.code,
      name: isin.name || '',
      quantity: isin.quantity || null,
      value: isin.value || null,
      price: null,
      currency: null,
      securityType: isin.securityType || 'unknown'
    };
    
    // Try to find additional information for this security
    securities.push(security);
  }
  
  // Look for securities tables to extract more information
  for (const table of tables) {
    // Check if this table looks like a securities/holdings table
    const headerText = table.headers.join(' ').toLowerCase();
    
    if (headerText.includes('security') || 
        headerText.includes('holding') || 
        headerText.includes('position') ||
        headerText.includes('investment') ||
        headerText.includes('isin')) {
      
      // Find the relevant column indices
      const isinIndex = findColumnIndex(table.headers, ['isin', 'identifier', 'id']);
      const nameIndex = findColumnIndex(table.headers, ['name', 'security', 'description']);
      const quantityIndex = findColumnIndex(table.headers, ['quantity', 'amount', 'units', 'shares']);
      const priceIndex = findColumnIndex(table.headers, ['price', 'unit price', 'market price']);
      const valueIndex = findColumnIndex(table.headers, ['value', 'market value', 'position']);
      const currencyIndex = findColumnIndex(table.headers, ['currency', 'ccy']);
      const typeIndex = findColumnIndex(table.headers, ['type', 'asset class', 'category']);
      
      // Process each row
      for (const row of table.rows) {
        let isinCode = null;
        
        // Try to get ISIN from the ISIN column
        if (isinIndex !== -1 && isinIndex < row.length) {
          const isinMatch = row[isinIndex].match(/[A-Z]{2}[A-Z0-9]{10}/);
          if (isinMatch) {
            isinCode = isinMatch[0];
          }
        }
        
        // If we couldn't find an ISIN, look for it in any column
        if (!isinCode) {
          for (const cell of row) {
            const isinMatch = cell.match(/[A-Z]{2}[A-Z0-9]{10}/);
            if (isinMatch) {
              isinCode = isinMatch[0];
              break;
            }
          }
        }
        
        // If we found an ISIN, extract the security information
        if (isinCode) {
          // Check if we already have this security
          const existingSecurity = securities.find(s => s.isin === isinCode);
          
          if (existingSecurity) {
            // Update existing security with any new information
            if (nameIndex !== -1 && nameIndex < row.length && !existingSecurity.name) {
              existingSecurity.name = row[nameIndex].trim();
            }
            
            if (quantityIndex !== -1 && quantityIndex < row.length && !existingSecurity.quantity) {
              existingSecurity.quantity = parseNumber(row[quantityIndex]);
            }
            
            if (priceIndex !== -1 && priceIndex < row.length && !existingSecurity.price) {
              existingSecurity.price = parseNumber(row[priceIndex]);
            }
            
            if (valueIndex !== -1 && valueIndex < row.length && !existingSecurity.value) {
              existingSecurity.value = parseNumber(row[valueIndex]);
            }
            
            if (currencyIndex !== -1 && currencyIndex < row.length && !existingSecurity.currency) {
              existingSecurity.currency = extractCurrency(row[currencyIndex]);
            }
            
            if (typeIndex !== -1 && typeIndex < row.length && existingSecurity.securityType === 'unknown') {
              existingSecurity.securityType = row[typeIndex].trim().toLowerCase();
            }
          } else {
            // Create a new security
            const security = {
              isin: isinCode,
              name: nameIndex !== -1 && nameIndex < row.length ? row[nameIndex].trim() : '',
              quantity: quantityIndex !== -1 && quantityIndex < row.length ? parseNumber(row[quantityIndex]) : null,
              price: priceIndex !== -1 && priceIndex < row.length ? parseNumber(row[priceIndex]) : null,
              value: valueIndex !== -1 && valueIndex < row.length ? parseNumber(row[valueIndex]) : null,
              currency: currencyIndex !== -1 && currencyIndex < row.length ? extractCurrency(row[currencyIndex]) : null,
              securityType: typeIndex !== -1 && typeIndex < row.length ? row[typeIndex].trim().toLowerCase() : 'unknown'
            };
            
            securities.push(security);
          }
        }
      }
    }
  }
  
  // Calculate missing values where possible
  for (const security of securities) {
    // If we have quantity and value but no price, calculate price
    if (security.quantity && security.value && !security.price && security.quantity > 0) {
      security.price = security.value / security.quantity;
    }
    
    // If we have quantity and price but no value, calculate value
    if (security.quantity && security.price && !security.value) {
      security.value = security.quantity * security.price;
    }
  }
  
  return securities;
}

/**
 * Extract currency from a string
 * @param {string} str - String to extract currency from
 * @returns {string|null} - Currency code or null if not found
 */
function extractCurrency(str) {
  if (!str) return null;
  
  // Common currency codes
  const currencyCodes = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'HKD', 'SGD'];
  
  // Check if the string contains a currency code
  for (const code of currencyCodes) {
    if (str.includes(code)) {
      return code;
    }
  }
  
  // Check for currency symbols
  if (str.includes('$')) return 'USD';
  if (str.includes('€')) return 'EUR';
  if (str.includes('£')) return 'GBP';
  if (str.includes('¥')) return 'JPY';
  
  return null;
}

/**
 * Extract performance metrics from document
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {Object} - Performance metrics
 */
function extractPerformanceMetrics(text, tables) {
  logger.info(`Extracting performance metrics`);
  
  const performance = {
    ytd: null,
    one_year: null,
    three_year: null,
    five_year: null,
    since_inception: null
  };
  
  // Look for performance tables
  for (const table of tables) {
    // Check if this table looks like a performance table
    const headerText = table.headers.join(' ').toLowerCase();
    
    if (headerText.includes('performance') || 
        headerText.includes('return') || 
        headerText.includes('ytd') ||
        headerText.includes('year')) {
      
      // Look for performance periods in the headers
      const ytdIndex = findColumnIndexExact(table.headers, ['ytd', 'year to date']);
      const oneYearIndex = findColumnIndexExact(table.headers, ['1 year', '1 yr', '1-year', '1-yr', 'one year']);
      const threeYearIndex = findColumnIndexExact(table.headers, ['3 year', '3 yr', '3-year', '3-yr', 'three year']);
      const fiveYearIndex = findColumnIndexExact(table.headers, ['5 year', '5 yr', '5-year', '5-yr', 'five year']);
      const inceptionIndex = findColumnIndexExact(table.headers, ['inception', 'since inception']);
      
      // Look for the portfolio/total row
      for (const row of table.rows) {
        const rowText = row.join(' ').toLowerCase();
        
        if (rowText.includes('portfolio') || 
            rowText.includes('total') || 
            rowText.includes('fund')) {
          
          // Extract performance values
          if (ytdIndex !== -1 && ytdIndex < row.length) {
            performance.ytd = parsePercentage(row[ytdIndex]);
          }
          
          if (oneYearIndex !== -1 && oneYearIndex < row.length) {
            performance.one_year = parsePercentage(row[oneYearIndex]);
          }
          
          if (threeYearIndex !== -1 && threeYearIndex < row.length) {
            performance.three_year = parsePercentage(row[threeYearIndex]);
          }
          
          if (fiveYearIndex !== -1 && fiveYearIndex < row.length) {
            performance.five_year = parsePercentage(row[fiveYearIndex]);
          }
          
          if (inceptionIndex !== -1 && inceptionIndex < row.length) {
            performance.since_inception = parsePercentage(row[inceptionIndex]);
          }
          
          break;
        }
      }
    }
  }
  
  // If we couldn't find performance in tables, try to extract from text
  if (!performance.ytd && !performance.one_year) {
    // Look for patterns like "YTD return: X%"
    const ytdPattern = /ytd(?:\s+return|\s+performance)?(?:\s*:|\s+is|\s+of)?\s*(-?\d+(?:\.\d+)?)%/i;
    const ytdMatch = text.match(ytdPattern);
    if (ytdMatch) {
      performance.ytd = parseFloat(ytdMatch[1]) / 100;
    }
    
    // Look for patterns like "1-year return: X%"
    const oneYearPattern = /(?:1|one)(?:-|\s+)year(?:\s+return|\s+performance)?(?:\s*:|\s+is|\s+of)?\s*(-?\d+(?:\.\d+)?)%/i;
    const oneYearMatch = text.match(oneYearPattern);
    if (oneYearMatch) {
      performance.one_year = parseFloat(oneYearMatch[1]) / 100;
    }
    
    // Look for patterns like "3-year return: X%"
    const threeYearPattern = /(?:3|three)(?:-|\s+)year(?:\s+return|\s+performance)?(?:\s*:|\s+is|\s+of)?\s*(-?\d+(?:\.\d+)?)%/i;
    const threeYearMatch = text.match(threeYearPattern);
    if (threeYearMatch) {
      performance.three_year = parseFloat(threeYearMatch[1]) / 100;
    }
    
    // Look for patterns like "5-year return: X%"
    const fiveYearPattern = /(?:5|five)(?:-|\s+)year(?:\s+return|\s+performance)?(?:\s*:|\s+is|\s+of)?\s*(-?\d+(?:\.\d+)?)%/i;
    const fiveYearMatch = text.match(fiveYearPattern);
    if (fiveYearMatch) {
      performance.five_year = parseFloat(fiveYearMatch[1]) / 100;
    }
    
    // Look for patterns like "Since inception: X%"
    const inceptionPattern = /since\s+inception(?:\s+return|\s+performance)?(?:\s*:|\s+is|\s+of)?\s*(-?\d+(?:\.\d+)?)%/i;
    const inceptionMatch = text.match(inceptionPattern);
    if (inceptionMatch) {
      performance.since_inception = parseFloat(inceptionMatch[1]) / 100;
    }
  }
  
  return performance;
}

/**
 * Extract currency information from document
 * @param {string} text - Document text
 * @param {Array} tables - Document tables
 * @returns {string|null} - Currency code or null if not found
 */
function extractCurrencyInfo(text, tables) {
  logger.info(`Extracting currency information`);
  
  // Look for currency information in text
  const currencyPatterns = [
    /(?:currency|denominated in|valued in|reported in)(?:\s*:|\s+is)?\s*([A-Z]{3})/i,
    /(?:all|all amounts|values|prices)(?:\s+are|\s+in)?\s+([A-Z]{3})/i,
    /([A-Z]{3})(?:\s+denominated|\s+currency)/i
  ];
  
  for (const pattern of currencyPatterns) {
    const match = text.match(pattern);
    if (match) {
      const currency = match[1].toUpperCase();
      
      // Validate that this is a common currency code
      if (['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'HKD', 'SGD'].includes(currency)) {
        return currency;
      }
    }
  }
  
  // Look for currency symbols
  if (text.includes('$')) {
    // Try to determine if this is USD, CAD, AUD, etc.
    if (text.includes('USD') || text.includes('US dollar')) {
      return 'USD';
    } else if (text.includes('CAD') || text.includes('Canadian dollar')) {
      return 'CAD';
    } else if (text.includes('AUD') || text.includes('Australian dollar')) {
      return 'AUD';
    } else {
      return 'USD'; // Default to USD
    }
  } else if (text.includes('€')) {
    return 'EUR';
  } else if (text.includes('£')) {
    return 'GBP';
  } else if (text.includes('¥')) {
    // Try to determine if this is JPY or CNY
    if (text.includes('JPY') || text.includes('Japanese yen')) {
      return 'JPY';
    } else if (text.includes('CNY') || text.includes('Chinese yuan')) {
      return 'CNY';
    } else {
      return 'JPY'; // Default to JPY
    }
  }
  
  // Look for currency information in tables
  for (const table of tables) {
    // Check if any header contains 'currency'
    const currencyIndex = findColumnIndex(table.headers, ['currency', 'ccy']);
    
    if (currencyIndex !== -1) {
      // Get the most common currency in this column
      const currencies = {};
      
      for (const row of table.rows) {
        if (currencyIndex < row.length) {
          const cell = row[currencyIndex].trim();
          
          // Skip empty cells
          if (cell.length === 0) continue;
          
          // Try to extract a currency code
          const currency = extractCurrency(cell);
          
          if (currency) {
            currencies[currency] = (currencies[currency] || 0) + 1;
          }
        }
      }
      
      // Return the most common currency
      if (Object.keys(currencies).length > 0) {
        return Object.keys(currencies).reduce((a, b) => currencies[a] > currencies[b] ? a : b);
      }
    }
  }
  
  // Default to null if we couldn't find a currency
  return null;
}

/**
 * Find the index of a column in a table based on possible header names (exact match)
 * @param {Array} headers - Table headers
 * @param {Array} possibleNames - Possible names for the column
 * @returns {number} - Column index or -1 if not found
 */
function findColumnIndexExact(headers, possibleNames) {
  for (let i = 0; i < headers.length; i++) {
    const header = headers[i].toLowerCase();
    
    for (const name of possibleNames) {
      if (header === name.toLowerCase()) {
        return i;
      }
    }
  }
  
  return -1;
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

module.exports = {
  analyzeFinancialData
};
