// API routes for the MCP server
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const { Storage } = require('@google-cloud/storage');

const router = express.Router();

// Initialize Google Cloud Storage
const storage = new Storage();

// Web fetch endpoint
router.get('/webFetch', async (req, res) => {
  try {
    const url = req.query.url;
    if (!url) {
      return res.status(400).json({ error: 'URL parameter is required' });
    }

    console.log(`Fetching content from ${url}`);
    
    const response = await axios.get(url, {
      responseType: url.endsWith('.pdf') ? 'arraybuffer' : 'text'
    });

    if (url.endsWith('.pdf')) {
      // For PDFs, save to a temporary file and return the path
      const tempDir = path.join(__dirname, 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      const filename = `temp_${Date.now()}.pdf`;
      const filePath = path.join(tempDir, filename);
      
      fs.writeFileSync(filePath, response.data);
      
      res.json({
        success: true,
        message: 'PDF downloaded successfully',
        filePath: filePath,
        filename: filename
      });
    } else {
      // For HTML content, parse and return as text
      const $ = cheerio.load(response.data);
      const text = $('body').text().trim();
      
      res.json({
        success: true,
        content: text,
        url: url
      });
    }
  } catch (error) {
    console.error('Error fetching content:', error);
    res.status(500).json({ error: error.message });
  }
});

// Web search endpoint
router.get('/webSearch', async (req, res) => {
  try {
    const query = req.query.query;
    if (!query) {
      return res.status(400).json({ error: 'Query parameter is required' });
    }

    console.log(`Searching for ${query}`);
    
    // Use a search API or scrape search results
    // This is a simplified example
    const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    
    const response = await axios.get(searchUrl, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      }
    });
    
    const $ = cheerio.load(response.data);
    const results = [];
    
    // Extract search results
    $('.g').each((i, element) => {
      const titleElement = $(element).find('h3');
      const linkElement = $(element).find('a');
      const snippetElement = $(element).find('.VwiC3b');
      
      if (titleElement.length && linkElement.length) {
        results.push({
          title: titleElement.text(),
          link: linkElement.attr('href'),
          snippet: snippetElement.length ? snippetElement.text() : ''
        });
      }
    });
    
    res.json({
      success: true,
      results: results,
      query: query
    });
  } catch (error) {
    console.error('Error searching:', error);
    res.status(500).json({ error: error.message });
  }
});

// List buckets endpoint
router.get('/listBuckets', async (req, res) => {
  try {
    console.log('Listing buckets');
    
    const [buckets] = await storage.getBuckets();
    
    res.json({
      success: true,
      buckets: buckets.map(bucket => ({
        name: bucket.name,
        created: bucket.metadata.timeCreated
      }))
    });
  } catch (error) {
    console.error('Error listing buckets:', error);
    res.status(500).json({ error: error.message });
  }
});

// List files endpoint
router.get('/listFiles', async (req, res) => {
  try {
    const bucketName = req.query.bucket;
    if (!bucketName) {
      return res.status(400).json({ error: 'Bucket parameter is required' });
    }

    console.log(`Listing files in bucket ${bucketName}`);
    
    const [files] = await storage.bucket(bucketName).getFiles();
    
    res.json({
      success: true,
      files: files.map(file => ({
        name: file.name,
        size: file.metadata.size,
        updated: file.metadata.updated
      }))
    });
  } catch (error) {
    console.error('Error listing files:', error);
    res.status(500).json({ error: error.message });
  }
});

// Process PDF endpoint
router.post('/processPdf', async (req, res) => {
  try {
    const { url, filePath } = req.body;
    
    if (!url && !filePath) {
      return res.status(400).json({ error: 'Either URL or filePath parameter is required' });
    }

    let pdfPath;
    
    if (url) {
      // Download PDF from URL
      console.log(`Downloading PDF from ${url}`);
      
      const response = await axios.get(url, {
        responseType: 'arraybuffer'
      });
      
      const tempDir = path.join(__dirname, 'temp');
      if (!fs.existsSync(tempDir)) {
        fs.mkdirSync(tempDir, { recursive: true });
      }

      const filename = `temp_${Date.now()}.pdf`;
      pdfPath = path.join(tempDir, filename);
      
      fs.writeFileSync(pdfPath, response.data);
    } else {
      // Use provided file path
      pdfPath = filePath;
    }

    // Process the PDF using the Python script
    console.log(`Processing PDF at ${pdfPath}`);
    
    const outputDir = path.join(__dirname, 'results', path.basename(pdfPath, '.pdf'));
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Execute the Python script
    const command = `python3 ../test_findoc_analyzer.py --pdf ${pdfPath} --output-dir ${outputDir}`;
    
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error executing Python script: ${error.message}`);
        return res.status(500).json({ error: error.message });
      }
      
      if (stderr) {
        console.error(`Python script stderr: ${stderr}`);
      }
      
      console.log(`Python script stdout: ${stdout}`);
      
      // Read the results
      const resultsFile = path.join(outputDir, `${path.basename(pdfPath, '.pdf')}_extraction.json`);
      
      if (fs.existsSync(resultsFile)) {
        const results = JSON.parse(fs.readFileSync(resultsFile, 'utf8'));
        
        res.json({
          success: true,
          results: results,
          outputDir: outputDir
        });
      } else {
        res.status(500).json({ error: 'Failed to generate results file' });
      }
    });
  } catch (error) {
    console.error('Error processing PDF:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
