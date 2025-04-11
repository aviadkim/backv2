import { NextApiRequest, NextApiResponse } from 'next';
import cheerio from 'cheerio';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { url, html, content } = req.body;

  if (!url || (!html && !content)) {
    return res.status(400).json({ error: 'URL and either HTML or content are required' });
  }

  try {
    // Extract financial data from HTML
    const financialData = extractFinancialData(url, html, content);
    
    return res.status(200).json(financialData);
  } catch (error) {
    console.error('Error extracting financial data:', error);
    
    return res.status(500).json({
      error: 'Failed to extract financial data',
      message: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}

/**
 * Extract financial data from HTML
 * @param {string} url The URL of the page
 * @param {string} html The HTML content
 * @param {string} content The text content
 * @returns {object} Extracted financial data
 */
function extractFinancialData(url, html, content) {
  const financialData = {
    url,
    extractedAt: new Date().toISOString(),
    securities: [],
    metrics: {},
    tables: [],
    charts: []
  };
  
  // Skip extraction if no HTML
  if (!html) {
    return financialData;
  }
  
  // Parse HTML with cheerio
  const $ = cheerio.load(html);
  
  // Extract ISINs
  const isinPattern = /\b[A-Z]{2}[A-Z0-9]{9}[0-9]\b/g;
  const isinMatches = html.match(isinPattern) || [];
  const isins = [...new Set(isinMatches)];
  
  // Extract ticker symbols
  const tickerPattern = /\b[A-Z]{1,5}(?:\.[A-Z]{1,3})?\b/g;
  const tickerMatches = html.match(tickerPattern) || [];
  const tickers = [...new Set(tickerMatches)];
  
  // Filter out common words that might match the ticker pattern
  const commonWords = ['A', 'I', 'IT', 'AT', 'BE', 'ME', 'MY', 'BY', 'TO', 'IN', 'IS', 'AM', 'PM', 'CEO', 'CFO', 'CTO', 'COO'];
  const filteredTickers = tickers.filter(ticker => !commonWords.includes(ticker));
  
  // Add securities
  isins.forEach(isin => {
    financialData.securities.push({
      type: 'ISIN',
      identifier: isin,
      name: findSecurityName($, isin)
    });
  });
  
  filteredTickers.forEach(ticker => {
    financialData.securities.push({
      type: 'Ticker',
      identifier: ticker,
      name: findSecurityName($, ticker)
    });
  });
  
  // Extract financial metrics
  financialData.metrics = extractFinancialMetrics($, content);
  
  // Extract tables
  financialData.tables = extractTables($);
  
  // Extract charts (just placeholders, as we can't actually extract chart data from HTML)
  financialData.charts = extractCharts($);
  
  return financialData;
}

/**
 * Find the name of a security based on its identifier
 * @param {CheerioStatic} $ Cheerio instance
 * @param {string} identifier Security identifier (ISIN or ticker)
 * @returns {string} Security name or empty string
 */
function findSecurityName($, identifier) {
  // Look for elements containing the identifier
  const elements = $(`*:contains("${identifier}")`).filter(function() {
    return $(this).text().includes(identifier);
  });
  
  // Try to find the security name in nearby elements
  for (let i = 0; i < elements.length; i++) {
    const element = elements[i];
    const text = $(element).text().trim();
    
    // Look for patterns like "Company Name (TICKER)" or "Company Name - ISIN: XX0000000000"
    const namePattern1 = new RegExp(`([^()]+)\\s*\\(${identifier}\\)`, 'i');
    const namePattern2 = new RegExp(`([^-]+)\\s*-\\s*(?:ISIN|Ticker):\\s*${identifier}`, 'i');
    
    const match1 = text.match(namePattern1);
    if (match1 && match1[1]) {
      return match1[1].trim();
    }
    
    const match2 = text.match(namePattern2);
    if (match2 && match2[1]) {
      return match2[1].trim();
    }
  }
  
  return '';
}

/**
 * Extract financial metrics from content
 * @param {CheerioStatic} $ Cheerio instance
 * @param {string} content Text content
 * @returns {object} Extracted financial metrics
 */
function extractFinancialMetrics($, content) {
  const metrics = {};
  
  // Define patterns for common financial metrics
  const metricPatterns = {
    marketCap: /market\s*cap(?:italization)?:?\s*([\$€£]?[\d,.]+\s*[bmtk]?)/i,
    revenue: /revenue:?\s*([\$€£]?[\d,.]+\s*[bmtk]?)/i,
    eps: /eps|earnings\s*per\s*share:?\s*([\$€£]?[\d,.]+)/i,
    pe: /p\/?e\s*ratio:?\s*([\d,.]+)/i,
    dividend: /dividend(?:\s*yield)?:?\s*([\$€£]?[\d,.]+%?)/i,
    beta: /beta:?\s*([\d,.]+)/i,
    fiftyTwoWeekHigh: /52(?:-|\s*)week\s*high:?\s*([\$€£]?[\d,.]+)/i,
    fiftyTwoWeekLow: /52(?:-|\s*)week\s*low:?\s*([\$€£]?[\d,.]+)/i
  };
  
  // Extract metrics using patterns
  for (const [metric, pattern] of Object.entries(metricPatterns)) {
    const match = content.match(pattern);
    if (match && match[1]) {
      metrics[metric] = match[1].trim();
    }
  }
  
  return metrics;
}

/**
 * Extract tables from HTML
 * @param {CheerioStatic} $ Cheerio instance
 * @returns {Array} Extracted tables
 */
function extractTables($) {
  const tables = [];
  
  // Find all tables
  $('table').each((i, tableElement) => {
    const table = {
      id: `table-${i + 1}`,
      headers: [],
      rows: []
    };
    
    // Extract headers
    $(tableElement).find('thead tr th, tr:first-child th').each((j, headerElement) => {
      table.headers.push($(headerElement).text().trim());
    });
    
    // If no headers found, try first row
    if (table.headers.length === 0) {
      $(tableElement).find('tr:first-child td').each((j, cellElement) => {
        table.headers.push($(cellElement).text().trim());
      });
    }
    
    // Extract rows
    $(tableElement).find('tbody tr, tr:not(:first-child)').each((j, rowElement) => {
      const row = [];
      
      $(rowElement).find('td').each((k, cellElement) => {
        row.push($(cellElement).text().trim());
      });
      
      if (row.length > 0) {
        table.rows.push(row);
      }
    });
    
    // Only add tables with data
    if (table.rows.length > 0) {
      tables.push(table);
    }
  });
  
  return tables;
}

/**
 * Extract charts from HTML (placeholder)
 * @param {CheerioStatic} $ Cheerio instance
 * @returns {Array} Extracted charts
 */
function extractCharts($) {
  const charts = [];
  
  // Look for chart elements
  $('div[id*="chart"], div[class*="chart"], canvas[id*="chart"], canvas[class*="chart"]').each((i, element) => {
    charts.push({
      id: `chart-${i + 1}`,
      type: 'unknown',
      title: $(element).attr('title') || $(element).attr('aria-label') || `Chart ${i + 1}`,
      data: null // We can't extract actual chart data from HTML
    });
  });
  
  return charts;
}
