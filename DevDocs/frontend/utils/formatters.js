/**
 * Utility functions for formatting data
 */

/**
 * Format a number as currency
 * @param {number} amount - The amount to format
 * @param {string} currency - The currency code (default: USD)
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @returns {string} Formatted currency string
 */
export const formatCurrency = (amount, currency = 'USD', locale = 'en-US') => {
  // Handle null, undefined, or NaN
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '-';
  }
  
  try {
    // Use Intl.NumberFormat for proper currency formatting
    const formatter = new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
    
    return formatter.format(amount);
  } catch (error) {
    console.error('Error formatting currency:', error);
    // Fallback formatting
    return `${currency} ${amount.toFixed(2)}`;
  }
};

/**
 * Format a number with commas as thousands separators
 * @param {number} number - The number to format
 * @param {number} decimals - Number of decimal places (default: 2)
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @returns {string} Formatted number string
 */
export const formatNumber = (number, decimals = 2, locale = 'en-US') => {
  // Handle null, undefined, or NaN
  if (number === null || number === undefined || isNaN(number)) {
    return '-';
  }
  
  try {
    // Use Intl.NumberFormat for proper number formatting
    const formatter = new Intl.NumberFormat(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    
    return formatter.format(number);
  } catch (error) {
    console.error('Error formatting number:', error);
    // Fallback formatting
    return number.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
};

/**
 * Format a date
 * @param {Date|string} date - The date to format
 * @param {string} format - The format to use (default: 'medium')
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @returns {string} Formatted date string
 */
export const formatDate = (date, format = 'medium', locale = 'en-US') => {
  // Handle null or undefined
  if (date === null || date === undefined) {
    return '-';
  }
  
  try {
    // Convert string to Date if needed
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    // Check if date is valid
    if (isNaN(dateObj.getTime())) {
      return 'Invalid Date';
    }
    
    // Use Intl.DateTimeFormat for proper date formatting
    const options = getDateFormatOptions(format);
    const formatter = new Intl.DateTimeFormat(locale, options);
    
    return formatter.format(dateObj);
  } catch (error) {
    console.error('Error formatting date:', error);
    // Fallback formatting
    return date.toString();
  }
};

/**
 * Get date format options based on format string
 * @param {string} format - The format to use
 * @returns {object} Date format options
 */
const getDateFormatOptions = (format) => {
  switch (format) {
    case 'short':
      return { 
        year: 'numeric', 
        month: 'numeric', 
        day: 'numeric' 
      };
    case 'long':
      return { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
      };
    case 'time':
      return { 
        hour: 'numeric', 
        minute: 'numeric' 
      };
    case 'full':
      return { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long',
        hour: 'numeric', 
        minute: 'numeric',
        second: 'numeric'
      };
    case 'medium':
    default:
      return { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      };
  }
};

/**
 * Format a percentage
 * @param {number} value - The value to format as percentage
 * @param {number} decimals - Number of decimal places (default: 2)
 * @param {string} locale - The locale to use for formatting (default: en-US)
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value, decimals = 2, locale = 'en-US') => {
  // Handle null, undefined, or NaN
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }
  
  try {
    // Use Intl.NumberFormat for proper percentage formatting
    const formatter = new Intl.NumberFormat(locale, {
      style: 'percent',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
    
    // Convert to decimal if value is already a percentage
    const decimalValue = value > 1 ? value / 100 : value;
    
    return formatter.format(decimalValue);
  } catch (error) {
    console.error('Error formatting percentage:', error);
    // Fallback formatting
    const percentValue = value > 1 ? value : value * 100;
    return `${percentValue.toFixed(decimals)}%`;
  }
};

/**
 * Format file size
 * @param {number} bytes - The file size in bytes
 * @param {number} decimals - Number of decimal places (default: 2)
 * @returns {string} Formatted file size string
 */
export const formatFileSize = (bytes, decimals = 2) => {
  // Handle null, undefined, or NaN
  if (bytes === null || bytes === undefined || isNaN(bytes)) {
    return '-';
  }
  
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(decimals)) + ' ' + sizes[i];
};
