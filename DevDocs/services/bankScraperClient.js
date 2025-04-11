/**
 * Client for the standalone Bank Scraper Service
 * This client communicates with the external bank scraper service
 * instead of running the scraper directly in Next.js
 */

// The API key must match the one set in start-bank-scraper-service.ps1
const API_KEY = process.env.BANK_SCRAPER_API_KEY || 'your-secure-api-key';
const SCRAPER_SERVICE_URL = process.env.BANK_SCRAPER_URL || 'http://localhost:4000';

/**
 * Get available bank types and their required credentials
 */
export async function getBankTypes() {
  try {
    const response = await fetch(`${SCRAPER_SERVICE_URL}/api/bank-types`);
    
    if (!response.ok) {
      throw new Error(`Error fetching bank types: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching bank types:', error);
    throw error;
  }
}

/**
 * Start a bank scraping operation
 * 
 * @param {string} bankType - The type of bank (e.g., 'leumi', 'hapoalim')
 * @param {object} credentials - The credentials for the bank
 * @param {string} userId - User identifier
 * @param {object} options - Additional options
 * @returns {Promise<object>} - The scraping result
 */
export async function startScraping(bankType, credentials, userId, options = {}) {
  try {
    const response = await fetch(`${SCRAPER_SERVICE_URL}/api/scrape`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': API_KEY
      },
      body: JSON.stringify({
        bankType,
        credentials,
        userId,
        options
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.errorMessage || `Server responded with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error starting bank scraping:', error);
    throw error;
  }
}

/**
 * Get previous scraping results for a user
 * 
 * @param {string} userId - User identifier
 * @returns {Promise<object>} - The user's scraping results
 */
export async function getUserResults(userId) {
  try {
    const response = await fetch(`${SCRAPER_SERVICE_URL}/api/results/${userId}`, {
      headers: {
        'X-API-Key': API_KEY
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.errorMessage || `Server responded with status ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching user results:', error);
    throw error;
  }
}