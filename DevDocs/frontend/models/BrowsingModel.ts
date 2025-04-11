export interface WebPage {
  url: string;
  title: string;
  content: string;
  html?: string;
  loadedAt: string;
  metadata?: {
    description?: string;
    keywords?: string[];
    author?: string;
    favicon?: string;
    [key: string]: any;
  };
}

export interface SearchResult {
  url: string;
  title: string;
  snippet: string;
  position: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResult[];
  totalResults: number;
  searchTime: number;
  searchEngine: string;
  searchedAt: string;
}

export interface BrowsingHistory {
  url: string;
  title: string;
  visitedAt: string;
}

export interface BrowsingState {
  currentPage: WebPage | null;
  history: BrowsingHistory[];
  bookmarks: WebPage[];
  lastSearch: SearchResponse | null;
  loading: boolean;
  error: string | null;
}

export interface BrowsingOptions {
  headers?: Record<string, string>;
  timeout?: number;
  proxy?: string;
  userAgent?: string;
  followRedirects?: boolean;
  maxRedirects?: number;
}

export interface SearchOptions {
  engine?: 'google' | 'bing' | 'duckduckgo';
  numResults?: number;
  safeSearch?: boolean;
  region?: string;
  language?: string;
}

export default {
  createEmptyState(): BrowsingState {
    return {
      currentPage: null,
      history: [],
      bookmarks: [],
      lastSearch: null,
      loading: false,
      error: null
    };
  },
  
  createWebPage(url: string, title: string, content: string, html?: string): WebPage {
    return {
      url,
      title,
      content,
      html,
      loadedAt: new Date().toISOString(),
      metadata: {}
    };
  },
  
  createSearchResponse(query: string, results: SearchResult[], engine: string): SearchResponse {
    return {
      query,
      results,
      totalResults: results.length,
      searchTime: 0,
      searchEngine: engine,
      searchedAt: new Date().toISOString()
    };
  },
  
  createBrowsingHistory(url: string, title: string): BrowsingHistory {
    return {
      url,
      title,
      visitedAt: new Date().toISOString()
    };
  }
};
