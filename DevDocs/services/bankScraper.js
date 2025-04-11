// Israeli Bank Scrapers service
import { CompanyTypes, createScraper } from 'israeli-bank-scrapers';

/**
 * Function to scrape bank transactions from Israeli banks
 * @param {string} bankType - The bank to scrape (use CompanyTypes enum)
 * @param {Object} credentials - The credentials object for the specific bank
 * @param {Date} startDate - The start date for transaction fetching
 * @param {boolean} showBrowser - Whether to show the browser during scraping (useful for debugging)
 * @returns {Promise<Object>} - The scraping result
 */
export async function scrapeTransactions({
  bankType,
  credentials,
  startDate = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // Default to 90 days ago
  showBrowser = false
}) {
  try {
    const options = {
      companyId: bankType,
      startDate,
      combineInstallments: false,
      showBrowser
    };

    const scraper = createScraper(options);
    const scrapeResult = await scraper.scrape(credentials);

    return scrapeResult;
  } catch (error) {
    console.error(`Error scraping transactions: ${error.message}`);
    return {
      success: false,
      errorType: 'SCRAPING_ERROR',
      errorMessage: error.message
    };
  }
}

/**
 * Helper function to get available banks and their required credentials
 * @returns {Object} - Object containing bank types and their required credentials
 */
export function getAvailableBanks() {
  return {
    hapoalim: {
      type: CompanyTypes.hapoalim,
      requiredCredentials: ['userCode', 'password'],
      description: 'Bank Hapoalim'
    },
    leumi: {
      type: CompanyTypes.leumi,
      requiredCredentials: ['username', 'password'],
      description: 'Bank Leumi'
    },
    discount: {
      type: CompanyTypes.discount,
      requiredCredentials: ['id', 'password', 'num'],
      description: 'Discount Bank'
    },
    mizrahi: {
      type: CompanyTypes.mizrahi,
      requiredCredentials: ['username', 'password'],
      description: 'Mizrahi Bank'
    },
    otsarHahayal: {
      type: CompanyTypes.otsarHahayal,
      requiredCredentials: ['username', 'password'],
      description: 'Otsar Hahayal Bank'
    },
    visaCal: {
      type: CompanyTypes.visaCal,
      requiredCredentials: ['username', 'password'],
      description: 'Visa Cal'
    },
    max: {
      type: CompanyTypes.max,
      requiredCredentials: ['username', 'password'],
      description: 'Max (formerly Leumi Card)'
    },
    isracard: {
      type: CompanyTypes.isracard,
      requiredCredentials: ['id', 'card6Digits', 'password'],
      description: 'Isracard'
    },
    amex: {
      type: CompanyTypes.amex,
      requiredCredentials: ['username', 'card6Digits', 'password'],
      description: 'American Express'
    },
    yahav: {
      type: CompanyTypes.yahav,
      requiredCredentials: ['username', 'password', 'nationalID'],
      description: 'Yahav'
    }
  };
}

/**
 * Example usage for Bank Hapoalim
 */
export async function exampleHapoalimScrape() {
  const credentials = {
    userCode: 'your-user-code',
    password: 'your-password'
  };
  
  return await scrapeTransactions({
    bankType: CompanyTypes.hapoalim,
    credentials,
    showBrowser: true // Set to true to see the browser during scraping (helpful for debugging)
  });
}

/**
 * Example usage for Leumi Bank
 */
export async function exampleLeumiScrape() {
  const credentials = {
    username: 'your-username',
    password: 'your-password'
  };
  
  return await scrapeTransactions({
    bankType: CompanyTypes.leumi,
    credentials,
    showBrowser: true
  });
}

/**
 * Example usage for Isracard
 */
export async function exampleIsracardScrape() {
  const credentials = {
    id: 'your-id',
    card6Digits: 'last-6-digits',
    password: 'your-password'
  };
  
  return await scrapeTransactions({
    bankType: CompanyTypes.isracard,
    credentials,
    showBrowser: true
  });
}