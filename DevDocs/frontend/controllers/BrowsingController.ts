import { WebPage, SearchResponse, BrowsingOptions, SearchOptions } from '../models/BrowsingModel';

class BrowsingController {
  /**
   * Fetch a web page and extract its content
   * @param url The URL to fetch
   * @param options Browsing options
   * @returns The web page content
   */
  async fetchPage(url: string, options?: BrowsingOptions): Promise<WebPage> {
    try {
      // Prepare request options
      const requestOptions: RequestInit = {
        headers: options?.headers || {
          'User-Agent': options?.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
        redirect: options?.followRedirects === false ? 'manual' : 'follow'
      };
      
      // Set timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), options?.timeout || 30000);
      requestOptions.signal = controller.signal;
      
      // Fetch the page
      const response = await fetch(`/api/web-proxy?url=${encodeURIComponent(url)}`, requestOptions);
      
      // Clear timeout
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch page: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Extract metadata
      const metadata = this._extractMetadata(data.html);
      
      // Create web page object
      const webPage: WebPage = {
        url: data.url || url,
        title: data.title || this._extractTitle(data.html) || url,
        content: data.content || this._extractText(data.html) || '',
        html: data.html,
        loadedAt: new Date().toISOString(),
        metadata
      };
      
      return webPage;
    } catch (error) {
      console.error('Error fetching page:', error);
      throw error;
    }
  }
  
  /**
   * Search the web
   * @param query The search query
   * @param options Search options
   * @returns Search results
   */
  async search(query: string, options?: SearchOptions): Promise<SearchResponse> {
    try {
      // Prepare request options
      const params = new URLSearchParams({
        query,
        engine: options?.engine || 'google',
        num_results: String(options?.numResults || 10),
        safe_search: String(options?.safeSearch !== false),
        region: options?.region || 'us',
        language: options?.language || 'en'
      });
      
      // Fetch search results
      const response = await fetch(`/api/web-search?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error(`Failed to search: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      // Create search response
      const searchResponse: SearchResponse = {
        query,
        results: data.results.map((result: any, index: number) => ({
          url: result.url,
          title: result.title,
          snippet: result.snippet,
          position: index + 1
        })),
        totalResults: data.total_results || data.results.length,
        searchTime: data.search_time || 0,
        searchEngine: options?.engine || 'google',
        searchedAt: new Date().toISOString()
      };
      
      return searchResponse;
    } catch (error) {
      console.error('Error searching:', error);
      throw error;
    }
  }
  
  /**
   * Extract financial data from a web page
   * @param url The URL to fetch
   * @returns Extracted financial data
   */
  async extractFinancialData(url: string): Promise<any> {
    try {
      // Fetch the page
      const webPage = await this.fetchPage(url);
      
      // Call the financial data extraction API
      const response = await fetch('/api/extract-financial-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: webPage.url,
          html: webPage.html,
          content: webPage.content
        })
      });
      
      if (!response.ok) {
        throw new Error(`Failed to extract financial data: ${response.statusText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error extracting financial data:', error);
      throw error;
    }
  }
  
  /**
   * Extract metadata from HTML
   * @private
   */
  private _extractMetadata(html?: string): WebPage['metadata'] {
    if (!html) return {};
    
    const metadata: WebPage['metadata'] = {};
    
    try {
      // Create a DOM parser
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Extract metadata from meta tags
      const metaTags = doc.querySelectorAll('meta');
      metaTags.forEach(tag => {
        const name = tag.getAttribute('name') || tag.getAttribute('property');
        const content = tag.getAttribute('content');
        
        if (name && content) {
          if (name === 'keywords') {
            metadata.keywords = content.split(',').map(k => k.trim());
          } else if (name === 'description') {
            metadata.description = content;
          } else if (name === 'author') {
            metadata.author = content;
          } else {
            metadata[name] = content;
          }
        }
      });
      
      // Extract favicon
      const faviconLink = doc.querySelector('link[rel="icon"], link[rel="shortcut icon"]');
      if (faviconLink) {
        metadata.favicon = faviconLink.getAttribute('href') || '';
      }
    } catch (error) {
      console.error('Error extracting metadata:', error);
    }
    
    return metadata;
  }
  
  /**
   * Extract title from HTML
   * @private
   */
  private _extractTitle(html?: string): string {
    if (!html) return '';
    
    try {
      const titleMatch = html.match(/<title[^>]*>(.*?)<\/title>/i);
      return titleMatch ? titleMatch[1].trim() : '';
    } catch (error) {
      console.error('Error extracting title:', error);
      return '';
    }
  }
  
  /**
   * Extract text content from HTML
   * @private
   */
  private _extractText(html?: string): string {
    if (!html) return '';
    
    try {
      // Create a DOM parser
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Remove script and style elements
      const scripts = doc.querySelectorAll('script, style');
      scripts.forEach(script => script.remove());
      
      // Get text content
      return doc.body.textContent || '';
    } catch (error) {
      console.error('Error extracting text:', error);
      return '';
    }
  }
}

const browsingController = new BrowsingController();
export default browsingController;
