import { NextApiRequest, NextApiResponse } from 'next';
import axios from 'axios';
import cheerio from 'cheerio';

export default async function handler(req, res) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { url } = req.query;

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    // Validate URL
    const parsedUrl = new URL(url);
    
    // Block certain domains for security
    const blockedDomains = ['localhost', '127.0.0.1', '0.0.0.0', 'internal'];
    if (blockedDomains.some(domain => parsedUrl.hostname.includes(domain))) {
      return res.status(403).json({ error: 'Access to internal domains is not allowed' });
    }
    
    // Fetch the page
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
      },
      timeout: 10000,
      maxRedirects: 5
    });
    
    const html = response.data;
    
    // Parse HTML with cheerio
    const $ = cheerio.load(html);
    
    // Remove scripts and styles for security
    $('script, style').remove();
    
    // Extract title
    const title = $('title').text().trim();
    
    // Extract main content
    let content = '';
    
    // Try to find main content
    const mainSelectors = [
      'main',
      'article',
      '#content',
      '.content',
      '#main',
      '.main',
      '.post',
      '.article'
    ];
    
    for (const selector of mainSelectors) {
      const mainElement = $(selector);
      if (mainElement.length > 0) {
        content = mainElement.text().trim();
        break;
      }
    }
    
    // If no main content found, use body
    if (!content) {
      content = $('body').text().trim();
    }
    
    // Clean up content
    content = content
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
    
    // Return the processed data
    return res.status(200).json({
      url: response.request.res.responseUrl || url,
      title,
      content,
      html
    });
  } catch (error) {
    console.error('Error fetching URL:', error);
    
    return res.status(500).json({
      error: 'Failed to fetch URL',
      message: error.message,
      stack: process.env.NODE_ENV === 'development' ? error.stack : undefined
    });
  }
}
