/**
 * Data Validator
 * 
 * Validates extracted financial data for consistency and accuracy:
 * - Checks for missing required data
 * - Validates numeric values are within expected ranges
 * - Ensures asset allocation percentages sum to approximately 100%
 * - Verifies security values sum to approximately the portfolio value
 * - Validates ISIN codes
 */

const logger = require('../../utils/logger');

/**
 * Validate extracted financial data
 * @param {Object} options - Validation options
 * @param {Object} options.portfolio_value - Portfolio value
 * @param {Object} options.asset_allocation - Asset allocation
 * @param {Array} options.securities - Securities information
 * @param {Object} options.performance - Performance metrics
 * @param {string} options.currency - Currency information
 * @param {string} options.documentType - Type of document
 * @returns {Promise<Object>} - Validation results
 */
async function validateData(options) {
  const { portfolio_value, asset_allocation, securities, performance, currency, documentType } = options;
  
  logger.info(`Validating financial data`);
  
  // Create result object
  const result = {
    isValid: true,
    errors: [],
    warnings: [],
    summary: {
      totalErrors: 0,
      totalWarnings: 0,
      validationStatus: 'valid'
    }
  };
  
  try {
    // Validate portfolio value
    validatePortfolioValue(portfolio_value, result);
    
    // Validate asset allocation
    validateAssetAllocation(asset_allocation, result);
    
    // Validate securities
    validateSecurities(securities, result);
    
    // Validate securities total against portfolio value
    validateSecuritiesTotalAgainstPortfolioValue(securities, portfolio_value, result);
    
    // Validate performance metrics
    validatePerformanceMetrics(performance, result);
    
    // Validate currency
    validateCurrency(currency, result);
    
    // Update summary
    result.summary.totalErrors = result.errors.length;
    result.summary.totalWarnings = result.warnings.length;
    result.summary.validationStatus = result.isValid ? 'valid' : 'invalid';
    
    logger.info(`Validation completed with ${result.summary.totalErrors} errors and ${result.summary.totalWarnings} warnings`);
    return result;
  } catch (error) {
    logger.error(`Error validating data: ${error.message}`, error);
    
    result.isValid = false;
    result.errors.push({
      code: 'VALIDATION_ERROR',
      message: `Validation process failed: ${error.message}`
    });
    
    result.summary.totalErrors = result.errors.length;
    result.summary.validationStatus = 'error';
    
    return result;
  }
}

/**
 * Validate portfolio value
 * @param {number} portfolioValue - Portfolio value
 * @param {Object} result - Validation result object
 */
function validatePortfolioValue(portfolioValue, result) {
  // Check if portfolio value is present
  if (portfolioValue === null || portfolioValue === undefined) {
    result.warnings.push({
      code: 'MISSING_PORTFOLIO_VALUE',
      message: 'Portfolio value is missing'
    });
    return;
  }
  
  // Check if portfolio value is a number
  if (typeof portfolioValue !== 'number') {
    result.errors.push({
      code: 'INVALID_PORTFOLIO_VALUE_TYPE',
      message: 'Portfolio value must be a number'
    });
    result.isValid = false;
    return;
  }
  
  // Check if portfolio value is positive
  if (portfolioValue <= 0) {
    result.errors.push({
      code: 'NEGATIVE_PORTFOLIO_VALUE',
      message: 'Portfolio value must be positive'
    });
    result.isValid = false;
    return;
  }
  
  // Check if portfolio value is within a reasonable range
  // This is a very broad check - adjust as needed
  if (portfolioValue < 100 || portfolioValue > 1000000000000) {
    result.warnings.push({
      code: 'UNUSUAL_PORTFOLIO_VALUE',
      message: `Portfolio value of ${portfolioValue} is outside the expected range`
    });
  }
}

/**
 * Validate asset allocation
 * @param {Object} assetAllocation - Asset allocation
 * @param {Object} result - Validation result object
 */
function validateAssetAllocation(assetAllocation, result) {
  // Check if asset allocation is present
  if (!assetAllocation || Object.keys(assetAllocation).length === 0) {
    result.warnings.push({
      code: 'MISSING_ASSET_ALLOCATION',
      message: 'Asset allocation is missing'
    });
    return;
  }
  
  // Check if asset allocation percentages are valid
  let totalPercentage = 0;
  
  for (const [assetClass, percentage] of Object.entries(assetAllocation)) {
    // Check if percentage is a number
    if (typeof percentage !== 'number') {
      result.errors.push({
        code: 'INVALID_ALLOCATION_PERCENTAGE_TYPE',
        message: `Asset allocation percentage for ${assetClass} must be a number`
      });
      result.isValid = false;
      continue;
    }
    
    // Check if percentage is between 0 and 1
    if (percentage < 0 || percentage > 1) {
      result.errors.push({
        code: 'INVALID_ALLOCATION_PERCENTAGE_RANGE',
        message: `Asset allocation percentage for ${assetClass} must be between 0 and 1`
      });
      result.isValid = false;
      continue;
    }
    
    totalPercentage += percentage;
  }
  
  // Check if total percentage is approximately 100%
  if (Math.abs(totalPercentage - 1) > 0.05) {
    result.warnings.push({
      code: 'ALLOCATION_PERCENTAGE_SUM',
      message: `Asset allocation percentages sum to ${(totalPercentage * 100).toFixed(2)}%, expected 100%`
    });
  }
}

/**
 * Validate securities
 * @param {Array} securities - Securities information
 * @param {Object} result - Validation result object
 */
function validateSecurities(securities, result) {
  // Check if securities are present
  if (!securities || securities.length === 0) {
    result.warnings.push({
      code: 'MISSING_SECURITIES',
      message: 'No securities found'
    });
    return;
  }
  
  // Validate each security
  for (let i = 0; i < securities.length; i++) {
    const security = securities[i];
    
    // Check if ISIN is present and valid
    if (!security.isin) {
      result.errors.push({
        code: 'MISSING_ISIN',
        message: `Security at index ${i} is missing ISIN`
      });
      result.isValid = false;
    } else if (!isValidIsin(security.isin)) {
      result.errors.push({
        code: 'INVALID_ISIN',
        message: `Security at index ${i} has invalid ISIN: ${security.isin}`
      });
      result.isValid = false;
    }
    
    // Check if name is present
    if (!security.name) {
      result.warnings.push({
        code: 'MISSING_SECURITY_NAME',
        message: `Security with ISIN ${security.isin} is missing name`
      });
    }
    
    // Check if quantity is present and valid
    if (security.quantity === null || security.quantity === undefined) {
      result.warnings.push({
        code: 'MISSING_SECURITY_QUANTITY',
        message: `Security with ISIN ${security.isin} is missing quantity`
      });
    } else if (typeof security.quantity !== 'number' || security.quantity < 0) {
      result.errors.push({
        code: 'INVALID_SECURITY_QUANTITY',
        message: `Security with ISIN ${security.isin} has invalid quantity: ${security.quantity}`
      });
      result.isValid = false;
    }
    
    // Check if value is present and valid
    if (security.value === null || security.value === undefined) {
      result.warnings.push({
        code: 'MISSING_SECURITY_VALUE',
        message: `Security with ISIN ${security.isin} is missing value`
      });
    } else if (typeof security.value !== 'number' || security.value < 0) {
      result.errors.push({
        code: 'INVALID_SECURITY_VALUE',
        message: `Security with ISIN ${security.isin} has invalid value: ${security.value}`
      });
      result.isValid = false;
    }
    
    // Check if price is present and valid
    if (security.price === null || security.price === undefined) {
      result.warnings.push({
        code: 'MISSING_SECURITY_PRICE',
        message: `Security with ISIN ${security.isin} is missing price`
      });
    } else if (typeof security.price !== 'number' || security.price < 0) {
      result.errors.push({
        code: 'INVALID_SECURITY_PRICE',
        message: `Security with ISIN ${security.isin} has invalid price: ${security.price}`
      });
      result.isValid = false;
    }
    
    // Check if quantity, price, and value are consistent
    if (security.quantity !== null && security.price !== null && security.value !== null) {
      const calculatedValue = security.quantity * security.price;
      const tolerance = Math.max(0.01 * security.value, 0.1); // 1% or $0.10, whichever is greater
      
      if (Math.abs(calculatedValue - security.value) > tolerance) {
        result.warnings.push({
          code: 'INCONSISTENT_SECURITY_VALUES',
          message: `Security with ISIN ${security.isin} has inconsistent quantity (${security.quantity}), price (${security.price}), and value (${security.value}). Expected value: ${calculatedValue}`
        });
      }
    }
  }
  
  // Check for duplicate ISINs
  const isinCounts = {};
  for (const security of securities) {
    if (security.isin) {
      isinCounts[security.isin] = (isinCounts[security.isin] || 0) + 1;
    }
  }
  
  for (const [isin, count] of Object.entries(isinCounts)) {
    if (count > 1) {
      result.warnings.push({
        code: 'DUPLICATE_ISIN',
        message: `ISIN ${isin} appears ${count} times`
      });
    }
  }
}

/**
 * Validate securities total against portfolio value
 * @param {Array} securities - Securities information
 * @param {number} portfolioValue - Portfolio value
 * @param {Object} result - Validation result object
 */
function validateSecuritiesTotalAgainstPortfolioValue(securities, portfolioValue, result) {
  // Skip if portfolio value is missing or invalid
  if (portfolioValue === null || portfolioValue === undefined || typeof portfolioValue !== 'number' || portfolioValue <= 0) {
    return;
  }
  
  // Skip if securities are missing
  if (!securities || securities.length === 0) {
    return;
  }
  
  // Calculate total value of securities
  let totalSecuritiesValue = 0;
  let securitiesWithValue = 0;
  
  for (const security of securities) {
    if (security.value !== null && security.value !== undefined && typeof security.value === 'number') {
      totalSecuritiesValue += security.value;
      securitiesWithValue++;
    }
  }
  
  // Skip if no securities have values
  if (securitiesWithValue === 0) {
    return;
  }
  
  // Check if total securities value is approximately equal to portfolio value
  // Allow for a 10% difference to account for cash, fees, etc.
  const tolerance = 0.1 * portfolioValue;
  
  if (Math.abs(totalSecuritiesValue - portfolioValue) > tolerance) {
    result.warnings.push({
      code: 'SECURITIES_TOTAL_MISMATCH',
      message: `Total securities value (${totalSecuritiesValue.toFixed(2)}) differs from portfolio value (${portfolioValue.toFixed(2)}) by more than 10%`
    });
  }
}

/**
 * Validate performance metrics
 * @param {Object} performance - Performance metrics
 * @param {Object} result - Validation result object
 */
function validatePerformanceMetrics(performance, result) {
  // Check if performance metrics are present
  if (!performance || Object.keys(performance).length === 0) {
    // This is not a critical error, just a warning
    result.warnings.push({
      code: 'MISSING_PERFORMANCE_METRICS',
      message: 'Performance metrics are missing'
    });
    return;
  }
  
  // Validate each performance metric
  for (const [period, value] of Object.entries(performance)) {
    // Skip null values
    if (value === null || value === undefined) {
      continue;
    }
    
    // Check if value is a number
    if (typeof value !== 'number') {
      result.errors.push({
        code: 'INVALID_PERFORMANCE_METRIC_TYPE',
        message: `Performance metric for ${period} must be a number`
      });
      result.isValid = false;
      continue;
    }
    
    // Check if value is within a reasonable range
    // Allow for a wide range of returns, but flag extreme values
    if (value < -0.9 || value > 2) {
      result.warnings.push({
        code: 'UNUSUAL_PERFORMANCE_METRIC',
        message: `Performance metric for ${period} (${(value * 100).toFixed(2)}%) is outside the expected range`
      });
    }
  }
}

/**
 * Validate currency
 * @param {string} currency - Currency information
 * @param {Object} result - Validation result object
 */
function validateCurrency(currency, result) {
  // Check if currency is present
  if (!currency) {
    // This is not a critical error, just a warning
    result.warnings.push({
      code: 'MISSING_CURRENCY',
      message: 'Currency information is missing'
    });
    return;
  }
  
  // Check if currency is a valid currency code
  const validCurrencies = ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'CAD', 'AUD', 'NZD', 'HKD', 'SGD', 'CNY'];
  
  if (!validCurrencies.includes(currency)) {
    result.warnings.push({
      code: 'UNKNOWN_CURRENCY',
      message: `Currency ${currency} is not a common currency code`
    });
  }
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
  validateData
};
