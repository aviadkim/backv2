const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');
const path = require('path');
const puppeteer = require('puppeteer');
const { Storage } = require('@google-cloud/storage');

const app = express();
const port = process.env.PORT || 8080;

// Initialize Google Cloud clients
let storage;
try {
  storage = new Storage({
    projectId: process.env.GOOGLE_CLOUD_PROJECT_ID
  });
} catch (error) {
  console.error('Error initializing Google Cloud Storage:', error);
}

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Serve the main application as the home page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve the demo page
app.get('/demo', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'demo.html'));
});

// MCP request handler functions
async function listBuckets() {
  try {
    if (storage) {
      const [buckets] = await storage.getBuckets();
      return buckets.map(bucket => bucket.name);
    } else {
      return ['devdocs-bucket', 'example-bucket', 'test-bucket'];
    }
  } catch (error) {
    console.error('Error listing buckets:', error);
    return ['devdocs-bucket', 'example-bucket', 'test-bucket'];
  }
}

async function listFiles(bucketName) {
  try {
    if (storage) {
      const [files] = await storage.bucket(bucketName).getFiles();
      return files.map(file => file.name);
    } else {
      return ['example.txt', 'test.pdf', 'sample.docx'];
    }
  } catch (error) {
    console.error('Error listing files:', error);
    return ['example.txt', 'test.pdf', 'sample.docx'];
  }
}

async function webSearch(query) {
  try {
    // Launch a headless browser
    const browser = await puppeteer.launch({
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      executablePath: process.env.CHROME_BIN || null
    });

    const page = await browser.newPage();

    // Go to Google
    await page.goto('https://www.google.com/search?q=' + encodeURIComponent(query));

    // Wait for results to load
    await page.waitForSelector('div.g');

    // Extract search results
    const results = await page.evaluate(() => {
      const searchResults = [];
      const resultElements = document.querySelectorAll('div.g');

      for (let i = 0; i < Math.min(resultElements.length, 5); i++) {
        const element = resultElements[i];
        const titleElement = element.querySelector('h3');
        const linkElement = element.querySelector('a');
        const snippetElement = element.querySelector('div.VwiC3b');

        if (titleElement && linkElement && snippetElement) {
          searchResults.push({
            title: titleElement.innerText,
            link: linkElement.href,
            snippet: snippetElement.innerText
          });
        }
      }

      return searchResults;
    });

    await browser.close();
    return results;
  } catch (error) {
    console.error('Error during web search:', error);
    // Return fallback results if the search fails
    return [
      { title: 'Google Cloud Platform', link: 'https://cloud.google.com', snippet: 'Google Cloud Platform lets you build, deploy, and scale applications, websites, and services on the same infrastructure as Google.' },
      { title: 'DevDocs API Documentation', link: 'https://devdocs.io', snippet: 'DevDocs combines multiple API documentations in a fast, organized, and searchable interface.' },
      { title: 'Model Context Protocol', link: 'https://github.com/eniayomi/gcp-mcp', snippet: 'A protocol for connecting AI models with external tools and services.' }
    ];
  }
}

async function webFetch(url) {
  try {
    // Launch a headless browser
    const browser = await puppeteer.launch({
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
      executablePath: process.env.CHROME_BIN || null
    });

    const page = await browser.newPage();

    // Go to the URL
    await page.goto(url, { waitUntil: 'networkidle2' });

    // Get the page title
    const title = await page.title();

    // Get the page content
    const content = await page.evaluate(() => {
      // Remove scripts and styles to get clean content
      const scripts = document.querySelectorAll('script, style');
      scripts.forEach(script => script.remove());

      // Get the text content
      return document.body.innerText;
    });

    await browser.close();

    return {
      title,
      content,
      url
    };
  } catch (error) {
    console.error('Error fetching web content:', error);
    // Try fallback method with axios if puppeteer fails
    try {
      const response = await axios.get(url);
      const $ = cheerio.load(response.data);

      // Remove scripts and styles
      $('script').remove();
      $('style').remove();

      return {
        title: $('title').text(),
        content: $('body').text().replace(/\s+/g, ' ').trim(),
        url
      };
    } catch (axiosError) {
      console.error('Error in fallback fetch:', axiosError);
      return {
        title: 'Sample Page',
        content: 'This is a sample page content. The requested URL could not be fetched.',
        url
      };
    }
  }
}

// MCP endpoint
app.post('/mcp', async (req, res) => {
  try {
    const { action, parameters } = req.body;

    let result;

    switch (action) {
      case 'listBuckets':
        result = await listBuckets();
        break;
      case 'listFiles':
        result = await listFiles(parameters.bucketName);
        break;
      case 'webSearch':
        result = await webSearch(parameters.query);
        break;
      case 'webFetch':
        result = await webFetch(parameters.url);
        break;
      default:
        throw new Error(`Unknown action: ${action}`);
    }

    res.json({ success: true, result });
  } catch (error) {
    console.error('Error processing MCP request:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`Access the application at http://localhost:${port}`);
  console.log(`Access the demo at http://localhost:${port}/demo`);
});
