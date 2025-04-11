import { NextResponse } from 'next/server';
import { CompanyTypes, createScraper } from 'israeli-bank-scrapers';

// Extended timeout for this endpoint
export const maxDuration = 300; // Set to 5 minutes (300 seconds)

// This is a server-side API to handle bank scraping
export async function POST(request) {
  try {
    const body = await request.json();
    const { bankType, credentials } = body;
    
    console.log(`Starting bank scraping for ${bankType}`);
    
    // Validate required params
    if (!bankType || !credentials) {
      return NextResponse.json({ 
        success: false, 
        message: 'Missing required parameters' 
      }, { status: 400 });
    }

    // Get the correct CompanyType based on the bankType string
    const companyType = CompanyTypes[bankType];
    
    if (!companyType) {
      return NextResponse.json({ 
        success: false, 
        message: 'Invalid bank type' 
      }, { status: 400 });
    }

    // Create options for the scraper with more debug settings
    const options = {
      companyId: companyType,
      startDate: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000), // 90 days ago
      combineInstallments: false,
      showBrowser: true, // Enable browser visibility for debugging
      verbose: true, // Enable verbose logging
      timeout: 180000, // 3 minutes timeout
      defaultTimeout: 180000,
      // Puppeteer launch options for better compatibility
      puppeteer: {
        headless: 'new',
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-accelerated-2d-canvas',
          '--no-first-run',
          '--no-zygote',
          '--disable-gpu'
        ]
      }
    };
    
    console.log('Initializing scraper with options:', JSON.stringify(options));
    
    try {
      // Initialize the scraper
      const scraper = createScraper(options);
      
      console.log('Scraper created, starting scraping process...');
      
      // Start the scraping process
      const scrapeResult = await scraper.scrape(credentials);
      
      console.log('Scraping completed:', JSON.stringify({
        success: scrapeResult.success,
        errorType: scrapeResult.errorType,
        accountCount: scrapeResult.accounts?.length || 0
      }));

      return NextResponse.json(scrapeResult);
    } catch (scraperError) {
      console.error('Error in scraper execution:', scraperError);
      
      // Provide more detailed error information
      let errorDetails = 'Unknown error';
      
      if (scraperError.message) {
        errorDetails = scraperError.message;
      }
      
      if (scraperError.stack) {
        console.error('Error stack:', scraperError.stack);
      }
      
      return NextResponse.json({ 
        success: false, 
        errorType: 'SCRAPER_EXECUTION_ERROR',
        errorMessage: `Error executing scraper: ${errorDetails}`
      }, { status: 500 });
    }
  } catch (error) {
    console.error('Error in bank-scraper API:', error);
    return NextResponse.json({ 
      success: false, 
      errorType: 'API_ERROR',
      errorMessage: `API error: ${error.message}` 
    }, { status: 500 });
  }
}